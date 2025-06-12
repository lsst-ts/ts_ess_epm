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
import unittest

from lsst.ts import salobj
from lsst.ts.ess.epm import modbus_data_client


class ModbusDataClientTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_modbus_data_client(self) -> None:
        salobj.set_test_topic_subname()
        async with salobj.make_mock_write_topics(
            name="ESS",
            attr_names=["tel_agcGenset150"],
        ) as topics:
            config = types.SimpleNamespace(
                host="127.0.0.1",
                port=502,
                max_read_timeouts=5,
                connect_timeout=1,
                device_name="UnitTest",
                device_type="agc150genset",
            )
            log = logging.getLogger(type(self).__name__)
            self.modbus_data_client = modbus_data_client.ModbusDataClient(
                config=config, topics=topics, log=log, simulation_mode=1
            )
            assert self.modbus_data_client is not None
            assert self.modbus_data_client.modbus_connector is not None
            await self.modbus_data_client.connect()
            assert self.modbus_data_client.modbus_connector.connected
            await self.modbus_data_client.disconnect()
            assert not self.modbus_data_client.modbus_connector.connected
