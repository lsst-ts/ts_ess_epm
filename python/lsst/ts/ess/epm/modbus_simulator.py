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

import os

from pymodbus.server import ModbusSimulatorServer

MODBUS_SIMULATOR_SETUP = os.path.dirname(__file__) + "/modbus_simulator_setup.json"


class ModbusSimulator:
    """Modbus simulator server.

    All parameters must match values defined in
    the modbus_simulator_setup.json file.

    Parameters
    ----------
    host : `str`
        The modbus host.
    port : `int`
        The modbus port.
    modbus_server : `str`
        The modbus server name.
    modbus_device : `str`
        The modbus device name.
        Also needs to match the device_type in ts_config_ocs.
    """

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 502,
        modbus_server: str = "server",
        modbus_device: str = "device",
    ) -> None:
        self.host = host
        self.port = port
        self.server = ModbusSimulatorServer(
            modbus_server=modbus_server,
            modbus_device=modbus_device,
            json_file=MODBUS_SIMULATOR_SETUP,
        )

    async def start(self) -> None:
        """Start the modbus server."""
        await self.server.run_forever(only_start=True)

    async def stop(self) -> None:
        """Stop the modbus server."""
        await self.server.stop()
