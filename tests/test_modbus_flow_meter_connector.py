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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

import logging
import types
import unittest

from lsst.ts import salobj
from lsst.ts.ess.epm.modbus import (
    ModbusFlowMeterConnector,
    NoCoilsDefinedError,
    NoDiscreteInputsDefinedError,
    NoHoldingRegistersDefinedError,
    NoInputRegistersDefinedError,
    NotConnectedError,
)
from lsst.ts.ess.epm.modbus.modbus_flow_meter_connector import f64_to_value, str_to_value

ATTR_NAMES = ["tel_flowMeter", "evt_sensorStatus", "evt_flowMeterIdentification"]


class ModbusFlowMeterConnectorTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_modbus_flow_meter_connector(self) -> None:
        salobj.set_test_topic_subname()
        async with salobj.make_mock_write_topics(
            name="ESS",
            attr_names=ATTR_NAMES,
        ) as topics:
            config = types.SimpleNamespace(
                host="127.0.0.1",
                port=502,
                max_read_timeouts=5,
                device_name="UnitTest",
                device_type="flowmeter",
            )
            log = logging.getLogger(type(self).__name__)
            self.modbus_flow_meter_connector = ModbusFlowMeterConnector(
                config=config,
                topics=topics,
                log=log,
                simulation_mode=1,
            )
            assert self.modbus_flow_meter_connector is not None
            await self.modbus_flow_meter_connector.connect()
            assert self.modbus_flow_meter_connector.connected
            await self.modbus_flow_meter_connector.disconnect()
            assert not self.modbus_flow_meter_connector.connected

    async def test_process_telemetry(self) -> None:
        salobj.set_test_topic_subname()
        async with salobj.make_mock_write_topics(
            name="ESS",
            attr_names=ATTR_NAMES,
        ) as topics:
            config = types.SimpleNamespace(
                host="127.0.0.1",
                port=502,
                max_read_timeouts=5,
                device_name="UnitTest",
                device_type="flowmeter",
            )
            log = logging.getLogger(type(self).__name__)
            self.modbus_flow_meter_connector = ModbusFlowMeterConnector(
                config=config,
                topics=topics,
                log=log,
                simulation_mode=1,
            )
            await self.modbus_flow_meter_connector.connect()
            assert self.modbus_flow_meter_connector.connected

            # Call process_telemetry and verify behavior
            await self.modbus_flow_meter_connector.process_telemetry()

            # Verify that the telemetry data was processed and written
            self.assertTrue(hasattr(topics, "tel_flowMeter"))
            self.assertTrue(topics.tel_flowMeter.has_data)

            await self.modbus_flow_meter_connector.disconnect()
            assert not self.modbus_flow_meter_connector.connected

    async def test_read_coils(self) -> None:
        salobj.set_test_topic_subname()
        async with salobj.make_mock_write_topics(
            name="ESS",
            attr_names=ATTR_NAMES,
        ) as topics:
            config = types.SimpleNamespace(
                host="127.0.0.1",
                port=502,
                max_read_timeouts=5,
                device_name="UnitTest",
                device_type="flowmeter",
            )
            log = logging.getLogger(type(self).__name__)
            self.modbus_flow_meter_connector = ModbusFlowMeterConnector(config=config, topics=topics, log=log)

            with self.assertRaises(NoCoilsDefinedError):
                await self.modbus_flow_meter_connector.read_coils()

    async def test_read_holding_registers(self) -> None:
        salobj.set_test_topic_subname()
        async with salobj.make_mock_write_topics(
            name="ESS",
            attr_names=ATTR_NAMES,
        ) as topics:
            config = types.SimpleNamespace(
                host="127.0.0.1",
                port=502,
                max_read_timeouts=5,
                device_name="UnitTest",
                device_type="flowmeter",
            )
            log = logging.getLogger(type(self).__name__)
            self.modbus_flow_meter_connector = ModbusFlowMeterConnector(config=config, topics=topics, log=log)

            with self.assertRaises(NoHoldingRegistersDefinedError):
                await self.modbus_flow_meter_connector.read_holding_registers()

    async def test_read_discrete_inputs_not_connected(self) -> None:
        salobj.set_test_topic_subname()
        async with salobj.make_mock_write_topics(
            name="ESS",
            attr_names=ATTR_NAMES,
        ) as topics:
            config = types.SimpleNamespace(
                host="127.0.0.1",
                port=502,
                max_read_timeouts=5,
                device_name="UnitTest",
                device_type="flowmeter",
            )
            log = logging.getLogger(type(self).__name__)
            self.modbus_flow_meter_connector = ModbusFlowMeterConnector(config=config, topics=topics, log=log)

            with self.assertRaises(NoDiscreteInputsDefinedError):
                await self.modbus_flow_meter_connector.read_discrete_inputs()

    async def test_read_input_registers_not_connected(self) -> None:
        salobj.set_test_topic_subname()
        async with salobj.make_mock_write_topics(
            name="ESS",
            attr_names=ATTR_NAMES,
        ) as topics:
            config = types.SimpleNamespace(
                host="127.0.0.1",
                port=502,
                max_read_timeouts=5,
                device_name="UnitTest",
                device_type="flowmeter",
            )
            log = logging.getLogger(type(self).__name__)
            self.modbus_flow_meter_connector = ModbusFlowMeterConnector(config=config, topics=topics, log=log)

            with self.assertRaises(NoInputRegistersDefinedError):
                await self.modbus_flow_meter_connector.read_input_registers()

    async def test_process_telemetry_not_connected(self) -> None:
        salobj.set_test_topic_subname()
        async with salobj.make_mock_write_topics(
            name="ESS",
            attr_names=ATTR_NAMES,
        ) as topics:
            config = types.SimpleNamespace(
                host="127.0.0.1",
                port=502,
                max_read_timeouts=5,
                device_name="UnitTest",
                device_type="flowmeter",
            )
            log = logging.getLogger(type(self).__name__)
            self.modbus_flow_meter_connector = ModbusFlowMeterConnector(config=config, topics=topics, log=log)

            with self.assertRaises(NotConnectedError):
                await self.modbus_flow_meter_connector.process_telemetry()

    def f64_to_value(self) -> None:
        assert f64_to_value([49221, 13762, 36700, 10486]) == -42.42

    def test_str_to_value(self) -> None:
        assert (
            str_to_value(
                [0x54, 0x68, 0x69, 0x73, 0x20, 0x69, 0x73, 0x20, 0x74, 0x65, 0x73, 0x74, 0x21, 0x00, 0x00]
            )
            == "This is test!"
        )
