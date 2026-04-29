# This file is part of ts_ess_epm.
#
# Developed for the Vera C. Rubin Observatory Telescope and Site Systems.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

__all__ = ["ModbusTMAConnector"]

import asyncio
import logging
import math
import pathlib
import types

from lsst.ts import salobj, utils

from ..enums import TMA_SENSOR_DICT, TMASector
from .base_modbus_connector import BaseModbusConnector
from .custom_exceptions import NotConnectedError

# Wait time [s] for the telemetry task.
TELEMETRY_WAIT = 1.0

MODBUS_SETUP_FILE = pathlib.Path(__file__).resolve().parents[1] / "data" / "tma_modbus_simulator_config.json"


class ModbusTMAConnector(BaseModbusConnector):
    def __init__(
        self,
        config: types.SimpleNamespace,
        topics: salobj.Controller | types.SimpleNamespace,
        log: logging.Logger,
        simulation_mode: int = 0,
    ) -> None:
        super().__init__(config, topics, log, simulation_mode)
        self.simulator_config_file = MODBUS_SETUP_FILE

        # Populate the necessary dicts.
        for sector in TMASector:
            sensor_list = TMA_SENSOR_DICT[sector]
            self.coils_dict[sector.name] = sensor_list[0].coil
            self.holding_registers_dict[sector.name] = sensor_list[0].holding_register - 400000
        self.coil_values: dict[str, list[bool]] = {}
        self.holding_register_values: dict[str, list[float]] = {}

        # Set the number of addresses to read.
        self.num_coils = 100
        self.num_holding_registers = 100

        self.log.debug("Modbus connector initialized.")

    async def process_modbus_response_array(
        self,
        input_name: str,
        input_address: int,
        input_type: str,
        modbus_response_array: list[int | bool],
    ) -> None:
        """Process an array of values read from the modbus client.

        Parameters
        ----------
        input_name : `str`
            The name of the modbus input.
        input_address : `int`
            The address of the modbus input.
        input_type : `str`
            The type of the modbus input.
        modbus_response_array : `list[int | bool]`
            The array of values read from the modbus client.
        """
        if isinstance(modbus_response_array[0], bool):
            for read_value in modbus_response_array:
                assert isinstance(read_value, bool)
                self.coil_values[input_name].append(read_value)
        else:
            self.holding_register_values[input_name] = self.client.convert_from_registers(
                modbus_response_array, self.client.DATATYPE.FLOAT32, "big"
            )

    async def process_telemetry(self) -> None:
        """Read the different registers
        for the telemetries of the AGC150 Controller
        using the modbus client.

        Start with discrete inputs and then input registers.

        Raises
        ------
        `RuntimeError`
            Raised when the client is not connected to the modbus server.
        """
        if self.connected:
            for sector in TMASector:
                self.coil_values[sector.name] = []
                self.holding_register_values[sector.name] = []

            await self.read_coils()
            await self.read_holding_registers()
            self.log.debug(f"{self.coil_values=}")
            self.log.debug(f"{self.holding_register_values=}")
            for sector in TMASector:
                telemetry_values: list[float] = []
                locations: list[str] = []
                for index, tsi in enumerate(TMA_SENSOR_DICT[sector]):
                    telemetry_values.append(self.holding_register_values[sector.name][index])
                    locations.append(tsi.code)
                    if self.coil_values[sector.name][index * 2]:
                        telemetry_values[index] = math.nan
                self.log.debug(f"{sector.name}: {telemetry_values=}")
                self.log.debug(f"{sector.name}: {locations=}")
                await self.topics.tel_temperature.set_write(
                    sensorName=sector.name,
                    timestamp=utils.current_tai(),
                    temperatureItem=telemetry_values,
                    numChannels=len(telemetry_values),
                    location=locations,
                )

            # Only emit the sensorStatus once, since all sector telemetry is
            # read from the same server.
            await self.topics.evt_sensorStatus.set_write(
                sensorName=self.config.host, sensorStatus=0, serverStatus=0
            )

            await asyncio.sleep(TELEMETRY_WAIT)
        else:
            await self.topics.evt_sensorStatus.set_write(
                sensorName=self.config.host, sensorStatus=0, serverStatus=1
            )
            raise NotConnectedError("TMA connector is not connected.")
