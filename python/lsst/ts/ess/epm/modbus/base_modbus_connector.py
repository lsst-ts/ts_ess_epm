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

__all__ = ["BaseModbusConnector"]

import logging
import types
from abc import ABC, abstractmethod

from pymodbus.client import AsyncModbusTcpClient

from lsst.ts import salobj

from .custom_exceptions import (
    NoCoilsDefinedError,
    NoDiscreteInputsDefinedError,
    NoHoldingRegistersDefinedError,
    NoInputRegistersDefinedError,
    NotConnectedError,
)

ModbusValueType = int | float | bool | None
FieldValueType = ModbusValueType | list[ModbusValueType]


class BaseModbusConnector(ABC):
    """Abstract base class for Modbus connectors.

    Parameters
    ----------
    config : `types.SimpleNamespace`
        The configuration.
    topics : `salobj.Controller` | `types.SimpleNamespace`
        The telemetry topics this connector can write.
    log : `logging.Logger`
        Logger instance for logging.
    simulation_mode : `int`
        Simulation mode.

    Attributes
    ----------
    client : `AsyncModbusTcpClient`
        Client to connect to the Modbus server.
    coils_dict : `dict[str, int]`
        Dict of coil (name, address) pairs.
    holding_registers_dict : `dict[str, int]`
        Dict of holding register (name, address) pairs.
    discrete_inputs_dict : `dict[str, int]`
        Dict of direct input (name, address) pairs.
    input_registers_dict : `dict[str, int]`
        Dict of input register (name, address) pairs.
    telemetry_fields : `dict[str, FieldValueType]`
        Dict of telemetry fields (name, value) pairs. This is used to populate
        the values for the salobj telemetry message.
    array_fields : `dict[str, list[str]]`
        Lookup dict for array fields. This is used to populate array fields in
        the salobj telemetry message.
    decimal_factor_dict : `dict[str, int]`
        Lookup dict for decimal factors. This is used to convert Modbus int
        values to telemetry decimal values.
    """

    def __init__(
        self,
        config: types.SimpleNamespace,
        topics: salobj.Controller | types.SimpleNamespace,
        log: logging.Logger,
        simulation_mode: int = 0,
    ) -> None:
        self.topics = topics
        self.config = config
        self.log = log.getChild(type(self).__name__)
        self.simulation_mode = simulation_mode
        self.client: AsyncModbusTcpClient = None

        # Dicts that hold info for the various Modbus addresses.
        self.coils_dict: dict[str, int] = {}
        self.holding_registers_dict: dict[str, int] = {}
        self.discrete_inputs_dict: dict[str, int] = {}
        self.input_registers_dict: dict[str, int] = {}

        # Dicts to help save and send telemetry.
        self.telemetry_fields: dict[str, FieldValueType] = {}
        self.array_fields: dict[str, list[str]] = {}

        # Dict for converting ints to floats.
        self.decimal_factor_dict: dict[str, int] = {}

    @property
    def connected(self) -> bool:
        """Is the modbus client connected?

        Returns
        -------
        `bool`
            Is the client connected?
        """
        return self.client is not None and self.client.connected

    @abstractmethod
    async def connect(self) -> None:
        """Establish a connection to the Modbus client."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the Modbus client."""
        pass

    def get_xml_field_name(self, field_name: str) -> str:
        """Get the XML name for a Modbus field name.

        For array fields, the number is removed.
        e.g. anyAlarmPMS1 -> anyAlarmPMS

        Parameters
        ----------
        field_name : `str`
            The field name.

        Returns
        -------
        str
            The XML field name.
        """

        xml_field_name = field_name
        for array_field, array in self.array_fields.items():
            if field_name in array:
                xml_field_name = array_field
                break
        return xml_field_name

    def process_modbus_value(self, field: str, value: int | bool) -> ModbusValueType:
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
        decimal_factor = self.decimal_factor_dict[self.get_xml_field_name(field)]
        if decimal_factor == 0:
            return signed_value

        return signed_value / (10**decimal_factor)

    async def save_field(self, input_name: str, read_value: int | bool) -> None:
        """Process and store the value read from the modbus client.

        Parameters
        ----------
        input_name : `str`
            The modbus input name.
        read_value : `int` | `bool`
            The value read from the modbus client.
        """
        """Process and store the value read from the modbus client.

        Parameters
        ----------
        input_name : `str`
            The modbus input name.
        read_value : `int` | `bool`
            The value read from the modbus client.
        """
        field_name = self.get_xml_field_name(input_name)
        processed_value = self.process_modbus_value(field_name, read_value)
        field = self.telemetry_fields.get(field_name)
        if isinstance(field, list):
            index = self.array_fields[field_name].index(input_name)
            field[index] = processed_value
        else:
            field = processed_value

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
        if modbus_response_array and len(modbus_response_array) > 0:
            await self.save_field(input_name, modbus_response_array[0])
        else:
            self.log.debug(f"{input_type} {input_name}({input_address}) returned no data.")

    async def read_coils(self) -> None:
        """Read coils from the Modbus client.

        Raises
        ------
        NoCoilsDefinedException
            If no coils are defined.
        NotConnectedException
            If not connected.
        """
        if len(self.coils_dict) == 0:
            raise NoCoilsDefinedError()

        if self.connected:
            for input_name, input_address in self.coils_dict.items():
                response = await self.client.read_coils(address=input_address, count=1)
                await self.process_modbus_response_array(input_name, input_address, "Coil", response.bits)
        else:
            raise NotConnectedError()

    async def read_discrete_inputs(self) -> None:
        """Read discrete inputs from the Modbus client.

        Raises
        ------
        NoDiscreteInputsDefinedException
            If no discrete inputs are defined.
        NotConnectedException
            If not connected.
        """
        if len(self.discrete_inputs_dict) == 0:
            raise NoDiscreteInputsDefinedError()

        if self.connected:
            for input_name, input_address in self.discrete_inputs_dict.items():
                response = await self.client.read_discrete_inputs(address=input_address, count=1)
                await self.process_modbus_response_array(
                    input_name, input_address, "Discrete input", response.bits
                )
        else:
            raise NotConnectedError()

    async def read_holding_registers(self) -> None:
        """Read holding registers from the Modbus client.

        Raises
        ------
        NoHoldingRegistersDefinedException
            If no holding registers are defined.
        NotConnectedException
            If not connected.
        """
        if len(self.holding_registers_dict) == 0:
            raise NoHoldingRegistersDefinedError()

        if self.connected:
            for input_name, input_address in self.holding_registers_dict.items():
                response = await self.client.read_holding_registers(address=input_address, count=1)
                await self.process_modbus_response_array(
                    input_name, input_address, "Holding register", response.bits
                )
        else:
            raise NotConnectedError()

    async def read_input_registers(self) -> None:
        """Read input registers from the Modbus client.

        Raises
        ------
        NoInputRegistersDefinedException
            If no input registers are defined.
        NotConnectedException
            If not connected.
        """
        if len(self.input_registers_dict) == 0:
            raise NoInputRegistersDefinedError()

        if self.connected:
            for input_name, input_address in self.input_registers_dict.items():
                response = await self.client.read_input_registers(address=input_address, count=1)
                await self.process_modbus_response_array(
                    input_name, input_address, "Input register", response.registers
                )
        else:
            raise NotConnectedError()

    @abstractmethod
    async def process_telemetry(self) -> None:
        """Process telemetry data."""
        pass
