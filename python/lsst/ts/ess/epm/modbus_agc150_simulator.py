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


class ModbusAgc150Simulator:
    """Wrapper around the modbus server for an AGC150 controller.

    Parameters
    ----------
    port : `int`
        The modbus port.
    host : `str`
        The modbus host.
    """

    def __init__(self, http_port: int = 8080):
        self.host = "0.0.0.0"
        self.port = 502
        self.server = ModbusSimulatorServer(
            modbus_server="server",
            modbus_device="agc150_genset",
            http_host="localhost",
            http_port=http_port,
            json_file=os.path.dirname(__file__) + "/modbus_simulator_setup.json",
        )

    async def start(self) -> None:
        """Start the modbus server."""
        await self.server.run_forever(only_start=True)

    async def stop(self) -> None:
        """Stop the modbus server."""
        await self.server.stop()
