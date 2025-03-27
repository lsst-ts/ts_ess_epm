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

from unittest.mock import AsyncMock, patch

import pytest
from lsst.ts.ess.epm.modbus_simulator import ModbusSimulator


@pytest.mark.asyncio
async def test_start() -> None:
    """Test the start method of ModbusSimulator."""
    with patch("lsst.ts.ess.epm.modbus_simulator.ModbusSimulatorServer") as MockServer:
        # Mock the ModbusSimulatorServer
        mock_server_instance = MockServer.return_value
        mock_server_instance.run_forever = AsyncMock()

        # Create an instance of ModbusSimulator
        simulator = ModbusSimulator(
            host="127.0.0.1",
            port=502,
            modbus_server="test_server",
            modbus_device="test_device",
        )

        # Call the start method
        await simulator.start()

        # Assert that run_forever was called with the correct arguments
        mock_server_instance.run_forever.assert_called_once_with(only_start=True)
