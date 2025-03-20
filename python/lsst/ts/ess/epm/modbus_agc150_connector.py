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

from .enums import (
    ARRAY_FIELDS_AGC150,
    DiscreteInputsAgc150,
    InputRegistersAgc150,
    InputRegistersAgc150DecimalFactor,
)

ModbusValueType = Union[int, float, bool]
FieldValueType = Union[ModbusValueType, list[ModbusValueType]]

# Wait time [s] for the telemetry task.
TELEMETRY_WAIT = 1.0


class ModbusAgc150Connector:
    """Class to connect to a modbus client for an AGC150 controller.

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
        self.simulator = None
        self.host = config.host
        self.port = config.port
        if log is None:
            self.log: logging.Logger = logging.getLogger(type(self).__name__)
        else:
            self.log = log.getChild(type(self).__name__)
        self.client: AsyncModbusTcpClient = None
        self.tel_agcGenset150 = getattr(self.topics, "tel_agcGenset150")
        self.agc150_fields: dict[str, FieldValueType] = {}

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
        if not self.connected:
            if self.simulator is not None:
                # TODO: Implement simulation mode.
                pass
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
                # TODO: Implement simulation mode.
                pass

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
        for array_field in ARRAY_FIELDS_AGC150:
            if field_name in ARRAY_FIELDS_AGC150[array_field]:
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

    def _save_field(self, field_name: str, read_value: int | bool) -> None:
        """Process and store the value read from the modbus client.

        Parameters
        ----------
        field_name : `str`
            The field name.
        read_value : `int` | `bool`
            The value read from the modbus client.
        """
        processed_value = self._process_modbus_value(
            field_name,
            read_value,
        )
        field = self.agc150_fields.get(field_name)
        if field is not None and isinstance(field, list):
            field.append(processed_value)
        else:
            self.agc150_fields[field_name] = processed_value

    async def _read_discrete_input(self) -> None:
        """Read the discrete inputs from the modbus client.

        Raises
        ------
        `RuntimeError`
            Raised when the client is not connected to the modbus server.
        """
        if self.connected:
            for discrete_input in DiscreteInputsAgc150:
                field_name = self._get_xml_field_name(discrete_input.name)
                response = await self.client.read_discrete_inputs(
                    discrete_input.value, 1
                )
                read_value = response.bits[0]
                self._save_field(field_name, read_value)
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
                field_name = self._get_xml_field_name(input_register.name)
                response = await self.client.read_input_registers(
                    input_register.value, 1
                )
                read_value = response.registers[0]
                self._save_field(field_name, read_value)
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
                self.agc150_fields[array_field] = []
            await self._read_discrete_input()
            await self._read_input_registers()
            await self.tel_agcGenset150.set_write(**self.agc150_fields)
            await asyncio.sleep(TELEMETRY_WAIT)
        else:
            raise RuntimeError("AGC150 connector is not connected.")
