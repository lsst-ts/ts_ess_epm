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

__all__ = ["ModbusEaton9sxConnector"]

import asyncio
import logging
import pathlib
import types

from lsst.ts import salobj

from ..enums import (
    DiscreteInputsEaton9sx,
    InputRegistersEaton9sx,
)
from .base_modbus_connector import (
    BaseModbusConnector,
)
from .custom_exceptions import NotConnectedError

# Wait time [s] for the telemetry task.
TELEMETRY_WAIT = 1.0

MODBUS_SETUP_FILE = (
    pathlib.Path(__file__).resolve().parents[1] / "data" / "eaton9sx_modbus_simulator_setup.json"
)


class ModbusEaton9sxConnector(BaseModbusConnector):
    """Class to connect to a modbus client for an Eaton 9SX UPS.

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
        self.tel_e9sxups = getattr(self.topics, "tel_e9sxups")

        # Populate the necessary Modbus address dicts.
        self.discrete_inputs_dict = {e.name: e.value for e in DiscreteInputsEaton9sx}
        self.input_registers_dict = {e.name: e.value for e in InputRegistersEaton9sx}

        self.log.debug("Modbus connector initialized.")

    async def process_telemetry(self) -> None:
        """Read the different registers
        for the telemetries of the Eaton 9SX UPS
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
            await self.tel_e9sxups.set_write(**self.telemetry_fields)

            await self.topics.evt_sensorStatus.set_write(
                sensorName=self.config.host, sensorStatus=0, serverStatus=0
            )

            await asyncio.sleep(TELEMETRY_WAIT)
        else:
            await self.topics.evt_sensorStatus.set_write(
                sensorName=self.config.host, sensorStatus=0, serverStatus=0
            )
            raise NotConnectedError("Eaton 9SX connector is not connected.")
