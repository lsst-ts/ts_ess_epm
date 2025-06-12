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

__all__ = ["ModbusDataClient"]

import logging
import types
import typing
from typing import Type

import yaml
from lsst.ts import salobj
from lsst.ts.ess.common.data_client import BaseReadLoopDataClient

from .base_modbus_connector import BaseModbusConnector
from .enums import ModbusConnectors
from .utils import load_class


class ModbusDataClient(BaseReadLoopDataClient):
    """Class to read data using a modbus interface and publish it as ESS
    telemetry.

    Parameters
    ----------
    config : `types.SimpleNamespace`
        The configuration, after validation by the schema returned
        by `get_config_schema` and conversion to a types.SimpleNamespace.
    topics : `salobj.Controller`
        The telemetry topics this model can write, as a struct with attributes
        such as ``tel_temperature``.
    log : `logging.Logger`
        Logger.
    simulation_mode : `int`, optional
        Simulation mode; 0 for normal operation.
    auto_reconnect : `bool`
        Automatically disconnect and reconnect in case of a read error
        (default: False)?

    Notes
    -----
    The config is required to contain "max_read_timeouts". If it doesn't, a
    RuntimeError is raised at instantiation.
    """

    def __init__(
        self,
        config: types.SimpleNamespace,
        topics: salobj.Controller | types.SimpleNamespace,
        log: logging.Logger,
        simulation_mode: int = 0,
    ) -> None:
        super().__init__(
            config=config,
            topics=topics,
            log=log,
            simulation_mode=simulation_mode,
        )

        connector_class_path = ModbusConnectors[config.device_type].value
        ConnectorClass: Type[BaseModbusConnector] = load_class(connector_class_path)
        self.modbus_connector = ConnectorClass(
            config=config,
            topics=topics,
            log=log,
            simulation_mode=simulation_mode,
        )

    @classmethod
    def get_config_schema(cls) -> dict[str, typing.Any]:
        """Get the config schema as jsonschema dict."""
        return yaml.safe_load(
            """
$schema: http://json-schema.org/draft-07/schema#
description: Schema for ControllerDataClient
type: object
properties:
  host:
    description: IP address of the modbus interface.
    type: string
    format: hostname
  port:
    description: Port number of the modbus interface.
    type: integer
  max_read_timeouts:
    description: Maximum number of read timeouts before an exception is raised.
    type: integer
    default: 5
  connect_timeout:
    description: Timeout for connecting to the TCP/IP interface (sec).
    type: number
    default: 60.0
  device_name:
    description: The name of the device.
    type: string
  device_type:
    description: The type of the device.
    type: string
required:
  - host
  - port
  - max_read_timeouts
  - connect_timeout
  - device_name
  - device_type
additionalProperties: false
"""
        )

    def descr(self) -> str:
        """Return a brief description, without the class name.

        This should be just enough information to distinguish
        one instance of this client from another.
        """
        return (
            "["
            f"device_name={self.config.device_name}, "
            f"device_type={self.config.device_type}, "
            f"host={self.config.host}, "
            f"port={self.config.port}"
            "]"
        )

    async def connect(self) -> None:
        """Connect to the modbus interface.

        This will not be called if already connected.
        See the Raises section for exceptions subclasses should raise.

        Raises
        ------
        ConnectionError
            If the data server rejects the connection.
            This may happen if the data server is down
            or the configuration specified an invalid address.
        asyncio.TimeoutError
            If a connection cannot be made in reasonable time.
        Exception
            (or any subclass) if any other serious problem occurs.
        """
        await self.modbus_connector.connect()
        self._connected = True

    async def disconnect(self) -> None:
        """Disconnect from the modbus interface.

        This must always be safe to call, whether connected or not.
        """
        await self.modbus_connector.disconnect()
        self._connected = False

    async def read_data(self) -> None:
        """Read data."""
        await self.modbus_connector.process_telemetry()
