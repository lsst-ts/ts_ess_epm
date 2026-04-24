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

__all__ = ["ModbusAgc150Connector"]

import asyncio
import logging
import pathlib
import types
from typing import Union

from pymodbus.client import AsyncModbusTcpClient

from lsst.ts import salobj

from ..enums import (
    AGC150_DECIMAL_FACTOR,
    ARRAY_FIELDS_AGC150,
    DiscreteInputsAgc150,
    InputRegistersAgc150,
)
from .base_modbus_connector import BaseModbusConnector
from .modbus_simulator import ModbusSimulator

ModbusValueType = Union[int, float, bool, None]
FieldValueType = Union[ModbusValueType, list[ModbusValueType]]

# Wait time [s] for the telemetry task.
TELEMETRY_WAIT = 1.0

MODBUS_SETUP_FILE = pathlib.Path(__file__).resolve().parents[1] / "data" / "agc150_simulator_setup.json"


class ModbusAgc150Connector(BaseModbusConnector):
    """Class to connect to a modbus client for an AGC 150 controller.

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
        self.simulator = (
            ModbusSimulator(log=log, json_file=MODBUS_SETUP_FILE, modbus_device=config.device_type)
            if simulation_mode == 1
            else None
        )
        self.host = config.host if self.simulator is None else self.simulator.host
        self.port = config.port if self.simulator is None else self.simulator.port
        self.tel_agcGenset150 = getattr(self.topics, "tel_agcGenset150")

        # Populate the necessary Modbus address dicts.
        self.discrete_inputs_dict = {e.name: e.value for e in DiscreteInputsAgc150}
        self.input_registers_dict = {e.name: e.value for e in InputRegistersAgc150}

        # Populate the array fields dict.
        self.array_fields = ARRAY_FIELDS_AGC150

        # Populate the decimal factor dict.
        self.decimal_factor_dict = AGC150_DECIMAL_FACTOR

        self.log.debug("Modbus connector initialized.")

    async def connect(self) -> None:
        """Connect to the modbus client."""
        if not self.connected:
            if self.simulator is not None:
                await self.simulator.start()
            self.client = AsyncModbusTcpClient(
                self.host,
                port=self.port,
            )
            await self.client.connect()
            if self.client.connected:
                self.log.info("Client connected.")

    async def disconnect(self) -> None:
        """Disconnect from the modbus client."""
        if self.connected:
            try:
                self.client.close()
            except Exception:
                pass
            finally:
                self.client = None
            self.log.info("Modbus client is closed.")
            if self.simulator is not None:
                await self.simulator.stop()

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
            for array_field in self.array_fields:
                array_field_size = len(self.array_fields[array_field])
                self.telemetry_fields[array_field] = [None for _ in range(array_field_size)]
            await self.read_discrete_inputs()
            await self.read_input_registers()
            self.log.debug(f"{self.telemetry_fields=}")
            await self.tel_agcGenset150.set_write(**self.telemetry_fields)
            await asyncio.sleep(TELEMETRY_WAIT)
        else:
            raise RuntimeError("AGC150 connector is not connected.")
