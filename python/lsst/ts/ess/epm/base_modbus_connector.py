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

import logging
import types
from abc import ABC, abstractmethod

from lsst.ts import salobj
from pymodbus.client import AsyncModbusTcpClient


class BaseModbusConnector(ABC):
    """Abstract base class for Modbus connectors."""

    def __init__(
        self,
        config: types.SimpleNamespace,
        topics: salobj.Controller | types.SimpleNamespace,
        log: logging.Logger,
        simulation_mode: int = 0,
    ) -> None:
        """
        Parameters
        ----------
        config : `types.SimpleNamespace`
            The configuration.
        topics : `salobj.Controller` | `types.SimpleNamespace`
            The telemetry topics this connector can write.
        log : `logging.Logger`
            Logger instance for logging.
        """
        self.topics = topics
        self.config = config
        self.log = log
        self.simulation_mode = simulation_mode
        self.client: AsyncModbusTcpClient = None

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

    @abstractmethod
    async def _read_coils(self) -> None:
        """Read coils from the Modbus client."""
        pass

    @abstractmethod
    async def _read_discrete_inputs(self) -> None:
        """Read discrete inputs from the Modbus client."""
        pass

    @abstractmethod
    async def _read_holding_registers(self) -> None:
        """Read holding registers from the Modbus client."""
        pass

    @abstractmethod
    async def _read_input_registers(self) -> None:
        """Read input registers from the Modbus client."""
        pass

    @abstractmethod
    async def process_telemetry(self) -> None:
        """Process telemetry data."""
        pass
