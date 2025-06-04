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
from lsst.ts.ess.epm.modbus_agc150_connector import ModbusAgc150Connector


class ModbusAgc150ConnectorTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_modbus_agc150_connector(self) -> None:
        salobj.set_test_topic_subname()
        async with salobj.make_mock_write_topics(
            name="ESS",
            attr_names=["tel_agcGenset150"],
        ) as topics:
            config = types.SimpleNamespace(
                host="127.0.0.1",
                port=502,
                max_read_timeouts=5,
                device_name="UnitTest",
                device_type="agc150genset",
            )
            log = logging.getLogger(type(self).__name__)
            self.modbus_agc150_connector = ModbusAgc150Connector(
                config=config,
                topics=topics,
                log=log,
                simulation_mode=1,
            )
            assert self.modbus_agc150_connector is not None
            await self.modbus_agc150_connector.connect()
            assert self.modbus_agc150_connector.connected
            await self.modbus_agc150_connector.disconnect()
            assert not self.modbus_agc150_connector.connected

    async def test_process_telemetry(self) -> None:
        salobj.set_test_topic_subname()
        async with salobj.make_mock_write_topics(
            name="ESS",
            attr_names=["tel_agcGenset150"],
        ) as topics:
            config = types.SimpleNamespace(
                host="127.0.0.1",
                port=502,
                max_read_timeouts=5,
                device_name="UnitTest",
                device_type="agc150genset",
            )
            log = logging.getLogger(type(self).__name__)
            self.modbus_agc150_connector = ModbusAgc150Connector(
                config=config,
                topics=topics,
                log=log,
                simulation_mode=1,
            )
            await self.modbus_agc150_connector.connect()
            assert self.modbus_agc150_connector.connected

            # Call process_telemetry and verify behavior
            await self.modbus_agc150_connector.process_telemetry()

            # Verify that the telemetry data was processed and written
            self.assertTrue(hasattr(topics, "tel_agcGenset150"))
            self.assertTrue(topics.tel_agcGenset150.has_data)

            await self.modbus_agc150_connector.disconnect()
            assert not self.modbus_agc150_connector.connected

    async def test_read_discrete_inputs_not_connected(self) -> None:
        salobj.set_test_topic_subname()
        async with salobj.make_mock_write_topics(
            name="ESS",
            attr_names=["tel_agcGenset150"],
        ) as topics:
            config = types.SimpleNamespace(
                host="127.0.0.1",
                port=502,
                max_read_timeouts=5,
                device_name="UnitTest",
                device_type="agc150genset",
            )
            log = logging.getLogger(type(self).__name__)
            self.modbus_agc150_connector = ModbusAgc150Connector(
                config=config, topics=topics, log=log
            )

            with self.assertRaises(RuntimeError):
                await self.modbus_agc150_connector._read_discrete_inputs()

    async def test_read_input_registers_not_connected(self) -> None:
        salobj.set_test_topic_subname()
        async with salobj.make_mock_write_topics(
            name="ESS",
            attr_names=["tel_agcGenset150"],
        ) as topics:
            config = types.SimpleNamespace(
                host="127.0.0.1",
                port=502,
                max_read_timeouts=5,
                device_name="UnitTest",
                device_type="agc150genset",
            )
            log = logging.getLogger(type(self).__name__)
            self.modbus_agc150_connector = ModbusAgc150Connector(
                config=config, topics=topics, log=log
            )

            with self.assertRaises(RuntimeError):
                await self.modbus_agc150_connector._read_input_registers()

    async def test_process_telemetry_not_connected(self) -> None:
        salobj.set_test_topic_subname()
        async with salobj.make_mock_write_topics(
            name="ESS",
            attr_names=["tel_agcGenset150"],
        ) as topics:
            config = types.SimpleNamespace(
                host="127.0.0.1",
                port=502,
                max_read_timeouts=5,
                device_name="UnitTest",
                device_type="agc150genset",
            )
            log = logging.getLogger(type(self).__name__)
            self.modbus_agc150_connector = ModbusAgc150Connector(
                config=config, topics=topics, log=log
            )

            with self.assertRaises(RuntimeError):
                await self.modbus_agc150_connector.process_telemetry()
