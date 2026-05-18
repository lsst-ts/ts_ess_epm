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

__all__ = ["ModbusAgc150MainsConnector"]

import asyncio
import logging
import pathlib
import types

from lsst.ts import salobj

from ..enums import (
    AGC150_BITMASK_ADDRESS,
    AGC150_DECIMAL_FACTOR,
    DiscreteInputsAgc150Mains,
    InputRegistersAgc150Mains,
)
from .base_modbus_connector import (
    BaseModbusConnector,
    ModbusValueType,
)
from .custom_exceptions import NotConnectedError

# Wait time [s] for the telemetry task.
TELEMETRY_WAIT = 1.0

MODBUS_SETUP_FILE = (
    pathlib.Path(__file__).resolve().parents[1] / "data" / "agc150mains_modbus_simulator_setup.json"
)


class ModbusAgc150MainsConnector(BaseModbusConnector):
    """Class to connect to a modbus client for an AGC 150 Mains controller.

    Parameters
    ----------
    config : `types.SimpleNamespace`
        The configuration.
    simulation_mode : `int`
        Use the simulator if 1.

    Attributes
    ----------
    port : `int`
        The modbus port.
    host : `str`
        The modbus host.
    client : `pymodbus.client.AsyncModbusTcpClient`
        The pymodbus async client.
    """

    def __init__(
        self,
        config: types.SimpleNamespace,
        topics: salobj.Controller | types.SimpleNamespace,
        log: logging.Logger,
        simulation_mode: int = 0,
    ) -> None:
        super().__init__(config, topics, log, simulation_mode)

        self.simulator_config_file = MODBUS_SETUP_FILE
        self.tel_agcMains150 = getattr(self.topics, "tel_agcMains150")

        # Populate the necessary Modbus address dicts.
        self.discrete_inputs_dict = {e.name: e.value for e in DiscreteInputsAgc150Mains}
        self.input_registers_dict = {e.name: e.value for e in InputRegistersAgc150Mains}

        # Populate the decimal factor dict.
        self.decimal_factor_dict = AGC150_DECIMAL_FACTOR

        # Populate the bitmask fields dict.
        self.bitmask_fields = AGC150_BITMASK_ADDRESS

        # Set the sensorName field
        self.telemetry_fields["sensorName"] = self.config.host

        self.log.debug("Modbus connector initialized.")

    async def save_field(self, input_name: str, read_value: ModbusValueType) -> None:
        """Process and store the value read from the modbus client.

        If the field is a bitmask field, the modbus read value is a bitmask
        where each bit corresponds to a different field. In this case,
        individual bits are processed and saved separately.
        Otherwise, the value is processed and saved directly.

        Parameters
        ----------
        input_name : `str`
            The modbus input name.
        read_value : `int` | `bool`
            The value read from the modbus client.
        """
        if input_name in self.bitmask_fields:
            if not isinstance(read_value, int):
                raise TypeError(
                    f"Expected int value for bitmask field {input_name}, got {type(read_value).__name__}."
                )
            bitmask_dict = self.bitmask_fields[input_name]
            for field_name, bitmask in bitmask_dict.items():
                bit_value = bool(read_value & bitmask)
                self.telemetry_fields[field_name] = bit_value
        else:
            await super().save_field(input_name, read_value)

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
            await self.read_discrete_inputs()
            await self.read_input_registers()
            self.log.debug(f"{self.telemetry_fields=}")
            await self.tel_agcMains150.set_write(**self.telemetry_fields)

            await self.topics.evt_sensorStatus.set_write(
                sensorName=self.config.host, sensorStatus=0, serverStatus=0
            )

            await asyncio.sleep(TELEMETRY_WAIT)
        else:
            await self.topics.evt_sensorStatus.set_write(
                sensorName=self.config.host, sensorStatus=0, serverStatus=1
            )
            raise NotConnectedError("AGC150 Mains connector is not connected.")
