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

__all__ = ["BaseModbusConnector", "ModbusValueType"]

import logging
import pathlib
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
from .modbus_simulator import ModbusSimulator

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
    simulator_config_file : `pathlib.Path` | None
        The path to the modbus simulator configuration file.
    simulator : `ModbusSimulator` | None
        The modbus simulator instance.
    host : `str`
        The host to connect to.
    port : `int`
        The port to connect to.
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
    num_coils : `int`
        The number of coils to read.
    num_holding_registers : `int`
        The number of holding_registers to read.
    num_discrete_inputs : `int`
        The number of discrete inputs to read.
    num_input_registers : `int`
        The number of input registers to read.
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
        self.simulator_config_file: pathlib.Path | None = None
        self.simulator: ModbusSimulator | None = None
        self.host = ""
        self.port = 0

        # Dicts that hold info for the various Modbus addresses.
        self.coils_dict: dict[str, int] = {}
        self.holding_registers_dict: dict[str, int] = {}
        self.discrete_inputs_dict: dict[str, int] = {}
        self.input_registers_dict: dict[str, int] = {}

        # Dicts to help save and send telemetry.
        self.telemetry_fields: dict[str, FieldValueType] = {}

        # Dict for converting ints to floats.
        self.decimal_factor_dict: dict[str, int] = {}

        # Numbers of registers to read.
        self.num_coils = 1
        self.num_holding_registers = 1
        self.num_discrete_inputs = 1
        self.num_input_registers = 1

    @property
    def connected(self) -> bool:
        """Is the modbus client connected?

        Returns
        -------
        `bool`
            Is the client connected?
        """
        return self.client is not None and self.client.connected

    async def connect(self) -> None:
        """Connect to the modbus client."""
        if self.simulation_mode == 1:
            assert self.simulator_config_file is not None
            self.log.debug(f"Using {self.simulator_config_file=}.")
            self.simulator = ModbusSimulator(
                log=self.log, json_file=self.simulator_config_file, modbus_device=self.config.device_type
            )
        self.host = self.config.host if self.simulator is None else self.simulator.host
        self.port = self.config.port if self.simulator is None else self.simulator.port

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

    def process_modbus_value(self, field: str, value: ModbusValueType) -> ModbusValueType:
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
        assert value is not None
        if isinstance(value, bool):
            return value

        signed_value = value if value < 32768 else value - 65536
        decimal_factor = self.decimal_factor_dict[field] if field in self.decimal_factor_dict else 0
        if decimal_factor == 0:
            return signed_value

        return signed_value / (10**decimal_factor)

    async def save_field(self, input_name: str, read_value: ModbusValueType) -> None:
        """Process and store the value read from the modbus client.

        Parameters
        ----------
        input_name : `str`
            The modbus input name.
        read_value : `int` | `bool`
            The value read from the modbus client.
        """
        processed_value = self.process_modbus_value(input_name, read_value)
        self.telemetry_fields[input_name] = processed_value

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
                self.log.debug(
                    f"Reading {self.num_coils} coils starting at {input_address} for {input_name}."
                )
                response = await self.client.read_coils(address=input_address, count=self.num_coils)
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
                self.log.debug(
                    f"Reading {self.num_discrete_inputs} discrete inputs "
                    f"starting at {input_address} for {input_name}."
                )
                response = await self.client.read_discrete_inputs(
                    address=input_address, count=self.num_discrete_inputs
                )
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
                self.log.debug(
                    f"Reading {self.num_holding_registers} holding registers "
                    f"starting at {input_address} for {input_name}."
                )
                response = await self.client.read_holding_registers(
                    address=input_address, count=self.num_holding_registers
                )
                await self.process_modbus_response_array(
                    input_name, input_address, "Holding register", response.registers
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
                self.log.debug(
                    f"Reading {self.num_input_registers} input registers "
                    f"starting at {input_address} for {input_name}."
                )
                response = await self.client.read_input_registers(
                    address=input_address, count=self.num_input_registers
                )
                await self.process_modbus_response_array(
                    input_name, input_address, "Input register", response.registers
                )
        else:
            raise NotConnectedError()

    @abstractmethod
    async def process_telemetry(self) -> None:
        """Process telemetry data."""
        pass
