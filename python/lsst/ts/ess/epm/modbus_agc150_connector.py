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
import types
from typing import Union

from lsst.ts import salobj
from pymodbus.client import AsyncModbusTcpClient

from .base_modbus_connector import BaseModbusConnector
from .enums import (
    ARRAY_FIELDS_AGC150,
    DiscreteInputsAgc150,
    InputRegistersAgc150,
    InputRegistersAgc150DecimalFactor,
)
from .modbus_simulator import ModbusSimulator

ModbusValueType = Union[int, float, bool, None]
FieldValueType = Union[ModbusValueType, list[ModbusValueType]]

# Wait time [s] for the telemetry task.
TELEMETRY_WAIT = 1.0


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
        self.topics = topics
        self.simulator = (
            ModbusSimulator(log=log, modbus_device=config.device_type)
            if simulation_mode == 1
            else None
        )
        self.host = config.host if self.simulator is None else self.simulator.host
        self.port = config.port if self.simulator is None else self.simulator.port
        self.log = log.getChild(type(self).__name__)
        self.client: AsyncModbusTcpClient = None
        self.tel_agcGenset150 = getattr(self.topics, "tel_agcGenset150")
        self.agc150_fields: dict[str, FieldValueType] = {}

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

    def _get_xml_field_name(self, field_name: str) -> str:
        """Get the XML name for AGC150 fields.

        For array fields, the number is removed.
        e.g. anyAlarmPMS1 -> anyAlarmPMS

        Parameters
        ----------
        field_name : `str`
            The field name.

        Returns
        -------
        `str`
            The XML field name.
        """
        xml_field_name = field_name
        for array_field, array in ARRAY_FIELDS_AGC150.items():
            if field_name in array:
                xml_field_name = array_field
                break
        return xml_field_name

    def _process_modbus_value(self, field: str, value: int | bool) -> ModbusValueType:
        """Process the value read from the modbus client.

        Convert unsigned ints to signed ints and apply the decimal factor.

        Parameters
        ----------
        field : `str`
            The field name.
        value : `int` | `bool`
            The value read from the modbus client.

        Returns
        -------
        `int` | `float` | `bool`
            The processed value.
        """
        if isinstance(value, bool):
            return value

        signed_value = value if value < 32768 else value - 65536
        decimal_factor = InputRegistersAgc150DecimalFactor[
            self._get_xml_field_name(field)
        ].value
        if decimal_factor == 0:
            return signed_value

        return signed_value / (10**decimal_factor)

    def _process_modbus_response_array(
        self,
        input: DiscreteInputsAgc150 | InputRegistersAgc150,
        modbus_response_array: list[int | bool],
    ) -> None:
        """Process an array of values read from the modbus client.

        Parameters
        ----------
        input : `DiscreteInputsAgc150` | `InputRegistersAgc150`
            The modbus input.
        modbus_response_array : `list[int | bool]`
            The array of values read from the modbus client.
        """
        if modbus_response_array and len(modbus_response_array) > 0:
            self._save_field(input.name, modbus_response_array[0])
        else:
            self.log.debug(
                f"Input register {input.name}({input.value}) returned no data."
            )

    def _save_field(self, input_name: str, read_value: int | bool) -> None:
        """Process and store the value read from the modbus client.

        Parameters
        ----------
        input_name : `str`
            The modbus input name.
        read_value : `int` | `bool`
            The value read from the modbus client.
        """
        field_name = self._get_xml_field_name(input_name)
        processed_value = self._process_modbus_value(
            field_name,
            read_value,
        )
        field = self.agc150_fields.get(field_name)
        if field is not None and isinstance(field, list):
            index = ARRAY_FIELDS_AGC150[field_name].index(input_name)
            field[index] = processed_value
        else:
            self.agc150_fields[field_name] = processed_value

    async def _read_coils(self) -> None:
        self.log.warning("Read coils not implemented for AGC 150.")

    async def _read_holding_registers(self) -> None:
        self.log.warning("Read holding registers not implemented for AGC 150.")

    async def _read_discrete_inputs(self) -> None:
        """Read the discrete inputs from the modbus client.

        Raises
        ------
        `RuntimeError`
            Raised when the client is not connected to the modbus server.
        """
        if self.connected:
            for discrete_input in DiscreteInputsAgc150:
                response = await self.client.read_discrete_inputs(
                    address=discrete_input.value, count=1
                )
                self._process_modbus_response_array(
                    discrete_input,
                    response.bits,
                )
        else:
            raise RuntimeError("AGC150 connector is not connected.")

    async def _read_input_registers(self) -> None:
        """Read the input registers from the modbus client.

        Raises
        ------
        `RuntimeError`
            Raised when the client is not connected to the modbus server.
        """
        if self.connected:
            for input_register in InputRegistersAgc150:
                response = await self.client.read_input_registers(
                    address=input_register.value, count=1
                )
                self._process_modbus_response_array(
                    input_register,
                    response.registers,
                )
        else:
            raise RuntimeError("AGC150 connector is not connected")

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
            for array_field in ARRAY_FIELDS_AGC150:
                array_field_size = len(ARRAY_FIELDS_AGC150[array_field])
                self.agc150_fields[array_field] = [
                    None for _ in range(array_field_size)
                ]
            await self._read_discrete_inputs()
            await self._read_input_registers()
            await self.tel_agcGenset150.set_write(**self.agc150_fields)
            await asyncio.sleep(TELEMETRY_WAIT)
        else:
            raise RuntimeError("AGC150 connector is not connected.")
