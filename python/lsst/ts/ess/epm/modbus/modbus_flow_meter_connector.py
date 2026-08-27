# This file is part of ts_ess_m1m3.
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
# along with this program. If not, see <https://www.gnu.org/licenses/>.

import asyncio
import enum
import logging
import pathlib
import time
import types

from pymodbus.client import ModbusBaseClient
from pymodbus.exceptions import ModbusException

from lsst.ts import salobj

from .base_modbus_connector import BaseModbusConnector
from .custom_exceptions import NotConnectedError

MODBUS_SETUP_FILE = (
    pathlib.Path(__file__).resolve().parents[1] / "data" / "flowmeter_modbus_simulator_setup.json"
)


class InputRegistersFlowMeter(enum.IntEnum):
    """Addresses of the input holding registers used in Flow Meter
    communication."""

    flowRate = 1600
    velocity = 1604
    netTotalizer = 2800
    positiveTotalizer = 2804
    negativeTotalizer = 2808
    signalStrength = 5500
    meterTag = 7000
    serialNumber = 7128
    firmwareVersion = 7192
    calibrationDate = 7256
    dateCode = 7320


"""Telemetry loop cycle duration."""
TELEMETRY_WAIT = 2.0


def f64_to_value(regs: list[int]) -> float:
    """Convert registers to float64 value.

    Parameters
    ----------
    regs : `list[int]`
        Array of registers to convert to float64 value.

    Returns
    -------
        Converted float64 (float in Python) value.
    """
    return ModbusBaseClient.convert_from_registers(regs[:4], data_type=ModbusBaseClient.DATATYPE.FLOAT64)


def str_to_value(regs: list[int]) -> str:
    """Convert registers to string value.

    Parameters
    ----------
    regs : `list[int]`
        Array of registers to convert to string value.

    Returns
    -------
        Converted string value.
    """
    return "".join([chr(b & 0xFF) for b in regs[: regs.index(0)]])


class ModbusFlowMeterConnector(BaseModbusConnector):
    """Class to connect to a Flow Meter Modbus/TCP interface.

    Parameters
    ----------
    config : `types.SimpleNamespace`
        The configuration.
    topics : `types.SimpleNamespace`
        CSC topics.
    log : `logging.Logger`
        Logging instance.
    simulation_mode : `int`, optional
        Use the simulator if set to 1. Default to 0.
    """

    def __init__(
        self,
        config: types.SimpleNamespace,
        topics: salobj.Controller | types.SimpleNamespace,
        log: logging.Logger,
        simulation_mode: int = 0,
    ):
        super().__init__(config, topics, log, simulation_mode)

        self.simulator_config_file = MODBUS_SETUP_FILE
        self.tel_flowMeter = self.topics.tel_flowMeter
        self.evt_flowMeterIdentification = self.topics.evt_flowMeterIdentification

        self.__telemetry_ok = False

    async def read_registers(self, start: int, count: int, name: str) -> list[int]:
        """Read registers, report error.

        Parameters
        ----------
        start : `int`
            Starting register.
        count : `int`
            Number of registers to read out.
        name : `str`
            Name of the register group - for error message.

        Returns
        -------
        registers : `list[int]`
            Returned registers.

        Raises
        ------
        ModbusException
            When registers cannot be read.
        """

        ret = await self.client.read_holding_registers(start, count=count)
        if ret.isError():
            raise ModbusException(f"Cannot read {name} registers ({start}:{start + count} - {str(ret)}).")
        return ret.registers

    async def send_product_data(self) -> None:
        """Reads and send various flowmeter identification data."""

        meter_tag_registers = await self.read_registers(InputRegistersFlowMeter.meterTag, 21, "Tag")
        serial_number_registers = await self.read_registers(
            InputRegistersFlowMeter.serialNumber, 21, "Serial number"
        )
        firmware_version_registers = await self.read_registers(
            InputRegistersFlowMeter.firmwareVersion, 21, "Firmware version"
        )
        calibration_date_registers = await self.read_registers(
            InputRegistersFlowMeter.calibrationDate, 21, "Calibration date"
        )
        date_code_registers = await self.read_registers(InputRegistersFlowMeter.dateCode, 21, "Data code")

        await self.evt_flowMeterIdentification.set_write(
            meterTag=str_to_value(meter_tag_registers),
            serialNumber=str_to_value(serial_number_registers),
            firmwareVersion=str_to_value(firmware_version_registers),
            calibrationDate=str_to_value(calibration_date_registers),
            dateCode=str_to_value(date_code_registers),
        )

    async def process_telemetry(self) -> None:
        """Run a telemetry loop. Readouts values and send those over SAL."""
        start_time = time.monotonic_ns()

        self.__telemetry_ok = False

        if not self.connected:
            await self.topics.evt_sensorStatus.set_write(
                sensorName=self.config.host, sensorStatus=0, serverStatus=1
            )
            raise NotConnectedError("FlowMeter connector is not conected.")

        signal_strength_registers = await self.read_registers(
            InputRegistersFlowMeter.signalStrength, 1, "signal strength"
        )
        flow_registers = await self.read_registers(InputRegistersFlowMeter.flowRate, 8, "flow")
        totalizers_registers = await self.read_registers(
            InputRegistersFlowMeter.netTotalizer, 12, "totalizers"
        )

        if not self.__telemetry_ok:
            await self.send_product_data()
            self.__telemetry_ok = True

        await self.topics.tel_flowMeter.set_write(
            signalStrength=signal_strength_registers[0],
            flowRate=f64_to_value(flow_registers[0:4]),
            netTotalizer=f64_to_value(totalizers_registers[0:4]),
            positiveTotalizer=f64_to_value(totalizers_registers[4:8]),
            negativeTotalizer=f64_to_value(totalizers_registers[8:12]),
        )

        await asyncio.sleep(TELEMETRY_WAIT - (time.monotonic_ns() - start_time) / 1e9)
