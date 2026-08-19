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

from dataclasses import dataclass
from enum import Enum, IntEnum, StrEnum


class ModbusConnectors(StrEnum):
    """Modbus connectors."""

    agc150genset = "lsst.ts.ess.epm.modbus.ModbusAgc150GensetConnector"
    agc150mains = "lsst.ts.ess.epm.modbus.ModbusAgc150MainsConnector"
    eaton9sx = "lsst.ts.ess.epm.modbus.ModbusEaton9sxConnector"
    tma = "lsst.ts.ess.epm.modbus.ModbusTMAConnector"


AGC150_ARRAY_FIELDS = {
    "anyAlarmPMS": [
        "anyAlarmPMS1",
        "anyAlarmPMS2",
        "anyAlarmPMS3",
        "anyAlarmPMS4",
        "anyAlarmPMS5",
        "anyAlarmPMS6",
        "anyAlarmPMS7",
        "anyAlarmPMS8",
    ],
    "readyAutoStartDG": [
        "readyAutoStartDG1",
        "readyAutoStartDG2",
        "readyAutoStartDG3",
        "readyAutoStartDG4",
        "readyAutoStartDG5",
        "readyAutoStartDG6",
        "readyAutoStartDG7",
        "readyAutoStartDG8",
    ],
    "windingTemperature": [
        "windingTemperature1",
        "windingTemperature2",
        "windingTemperature3",
    ],
}

# Bit address mapping for AGC150 controller registers.
#
# This dictionary defines bit positions (as bit masks) for various input
# registers that share a single Modbus address but represent multiple boolean
# values. As modbus registers are typically 16 bits, each bit can represent
# a different boolean state or alarm condition. The keys of the dictionary
# correspond to the register names that define a single address,
# and the values are dictionaries mapping specific conditions to
# their respective bit masks.
#
# Usage:
#   if modbus_response & (
#       AGC150_BITMASK_ADDRESS["acAlarms1"]["reversePowerMains1"]
#   ):
#       # alarm is active
AGC150_BITMASK_ADDRESS = {
    "acAlarms1": {
        "reversePowerMains1": 1 << 0,
        "reversePowerMains2": 1 << 1,
        "reversePowerMains3": 1 << 2,
        "overcurrentMains1": 1 << 3,
        "overcurrentMains2": 1 << 4,
        "overcurrentMains3": 1 << 5,
        "overcurrentMains4": 1 << 6,
        "voltDepOvercurrentMains": 1 << 8,
        "shortCircuitMains1": 1 << 9,
        "shortCircuitMains2": 1 << 10,
        "overvoltageMains1": 1 << 11,
        "overvoltageMains2": 1 << 12,
        "undervoltageMains1": 1 << 13,
        "undervoltageMains2": 1 << 14,
        "undervoltageMains3": 1 << 15,
    },
    "acAlarms2": {
        "overfrequencyMains1": 1 << 0,
        "overfrequencyMains2": 1 << 1,
        "overfrequencyMains3": 1 << 2,
        "underfrequencyMains1": 1 << 3,
        "underfrequencyMains2": 1 << 4,
        "underfrequencyMains3": 1 << 5,
        "overvoltageBusbar1": 1 << 6,
        "overvoltageBusbar2": 1 << 7,
        "overvoltageBusbar3": 1 << 8,
        "undervoltageBusbar1": 1 << 9,
        "undervoltageBusbar2": 1 << 10,
        "undervoltageBusbar3": 1 << 11,
        "undervoltageBusbar4": 1 << 12,
        "overfrequencyBusbar1": 1 << 13,
        "overfrequencyBusbar2": 1 << 14,
        "overfrequencyBusbar3": 1 << 15,
    },
    "acAlarms3": {
        "underfrequencyBusbar1": 1 << 0,
        "underfrequencyBusbar2": 1 << 1,
        "underfrequencyBusbar3": 1 << 2,
        "underfrequencyBusbar4": 1 << 3,
        "unbalanceCurrent": 1 << 12,
        "unbalanceVoltage": 1 << 13,
    },
    "acAlarms4": {
        "directionalOvercurrent1": 1 << 4,
        "directionalOvercurrent2": 1 << 5,
        "busbarVoltageUnbalance": 1 << 6,
    },
    "acAlarms5": {
        "tieBreakerExternalTrip": 1 << 8,
        "mainsBreakerExternalTrip": 1 << 9,
    },
    "alarms1": {
        "synchronizingWindow": 1 << 0,
        "synchronizingWindowFailureTB": 1 << 1,
        "synchronizingWindowFailureMB": 1 << 2,
        "tieBreakerOpenFailure": 1 << 4,
        "tieBreakerCloseFailure": 1 << 5,
        "tieBreakerPositionFailure": 1 << 6,
        "mainsBreakerOpenFailure": 1 << 7,
        "mainsBreakerCloseFailure": 1 << 8,
        "mainsBreakerPositionFailure": 1 << 9,
    },
}


class DiscreteInputsAgc150Genset(IntEnum):
    gbPositionOn = 0
    mbPositionOn = 1
    running = 3
    generatorVoltageFrequencyOk = 4
    mainFailure = 5
    blockMode = 6
    manualMode = 7
    semiAutoMode = 8
    autoMode = 9
    testMode = 10
    gbPositionOff = 11
    mbPositionOff = 12
    island = 13
    automaticMainsFailure = 14
    peakShaving = 15
    fixedPower = 16
    mainsPowerExport = 17
    loadTakeover = 18
    powerManagement = 19
    anyAlarmPMS1 = 20
    anyAlarmPMS2 = 21
    anyAlarmPMS3 = 22
    anyAlarmPMS4 = 23
    anyAlarmPMS5 = 24
    anyAlarmPMS6 = 25
    anyAlarmPMS7 = 26
    anyAlarmPMS8 = 27
    anyAlarmMains = 28
    batteryTest = 29
    readyAutoStartDG1 = 31
    readyAutoStartDG2 = 32
    readyAutoStartDG3 = 33
    readyAutoStartDG4 = 34
    readyAutoStartDG5 = 35
    readyAutoStartDG6 = 36
    readyAutoStartDG7 = 37
    readyAutoStartDG8 = 38
    mainSyncInhibit = 53
    anyMainsSyncInhibit = 54


class AddressFactorEnum(Enum):
    def __init__(self, address: int, decimal_factor: int = 0):
        self.address = address
        self.decimal_factor = decimal_factor


class InputRegistersAgc150Genset(AddressFactorEnum):
    applicationVersion = (500,)
    generatorVoltageL1L2 = (501,)
    generatorVoltageL2L3 = (502,)
    generatorVoltageL3L1 = (503,)
    generatorVoltageL1N = (504,)
    generatorVoltageL2N = (505,)
    generatorVoltageL3N = (506,)
    generatorFrequencyL1 = (507, 2)
    generatorFrequencyL2 = (508, 2)
    generatorFrequencyL3 = (509, 2)
    generatorVoltagePhaseAngleL1L2 = (510, 1)
    generatorVoltagePhaseAngleL2L3 = (511, 1)
    generatorVoltagePhaseAngleL3L1 = (512, 1)
    generatorCurrentL1 = (513,)
    generatorCurrentL2 = (514,)
    generatorCurrentL3 = (515,)
    generatorPowerL1 = (516,)
    generatorPowerL2 = (517,)
    generatorPowerL3 = (518,)
    generatorPower = (519,)
    generatorReactivePowerL1 = (520,)
    generatorReactivePowerL2 = (521,)
    generatorReactivePowerL3 = (522,)
    generatorReactivePower = (523,)
    generatorApparentPowerL1 = (524,)
    generatorApparentPowerL2 = (525,)
    generatorApparentPowerL3 = (526,)
    generatorApparentPower = (527,)
    generatorExportReactiveEnergyCounterTotal = (528,)
    generatorExportActiveEnergyCounterDay = (530,)
    generatorExportActiveEnergyCounterWeek = (532,)
    generatorExportActiveEnergyCounterMonth = (534,)
    generatorExportActiveEnergyCounterTotal = (536,)
    generatorPF = (538, 2)
    busBVoltageL1L2 = (539,)
    busBVoltageL2L3 = (540,)
    busBVoltageL3L1 = (541,)
    busBVoltageL1N = (542,)
    busBVoltageL2N = (543,)
    busBVoltageL3N = (544,)
    busBFrequencyL1 = (545, 2)
    busBFrequencyL2 = (546, 2)
    busBFrequencyL3 = (547, 2)
    busBVoltagePhaseAngleL1L2 = (548, 1)
    busBVoltagePhaseAngleL2L3 = (549, 1)
    busBVoltagePhaseAngleL3L1 = (550, 1)
    uBBL1uGENL1PhaseAngle = (551,)
    uBBL2uGENL2PhaseAngle = (552,)
    uBBL3uGENL3PhaseAngle = (553,)
    absoluteRunningHours = (554,)
    relativeRunningHours = (556,)
    numberAlarms = (558,)
    numberUnacknowledgedAlarms = (559,)
    numberActiveAcknowledgedAlarms = (560,)
    numberGBOperations = (563,)
    numberMBOperations = (564,)
    startAttempts = (566,)
    dcSupplyTerm12 = (567, 1)
    serviceTimer1RunningHours = (569,)
    serviceTimer1RunningDays = (570,)
    serviceTimer2RunningHours = (571,)
    serviceTimer2RunningDays = (572,)
    cosPhi = (573, 2)
    cosPhiType = (574,)
    rpm = (576,)
    runningHoursLoadProfile = (577,)
    multiInput20 = (583,)
    multiInput21 = (584,)
    multiInput22 = (585,)
    multiInput23 = (587,)
    mainsPower = (592,)
    engineSpeed = (593,)
    engineCoolantTemperature = (594, 1)
    engineOilPressure = (595, 2)
    numberActualFaults = (596,)
    engineOilTemperature = (597, 1)
    fuelTemperature = (598,)
    intakeManifold1Pressure = (599, 2)
    airInletTemperature = (600,)
    coolantLevel = (601, 1)
    fuelRate = (602, 1)
    chargeAirPressure = (603,)
    intakeManifold1Temperature = (604,)
    driversDemandEnginePercentTorque = (605,)
    actualEnginePercentTorque = (606,)
    acceleratorPedalPosition = (607,)
    percentLoadCurrentSpeed = (608,)
    airInletPressure = (609, 2)
    exhaustGasTemperature = (610, 1)
    engineHours = (611,)
    engineOilFilterDifferentialPressure = (612, 2)
    keyswitchBatteryPotential = (613, 1)
    fuelDeliveryPressure = (614, 2)
    engineOilLevel = (615, 1)
    crankcasePressure = (616, 2)
    coolantPressure = (617, 2)
    waterInFuel = (618,)
    blowbyFlow = (619,)
    fuelRailPressure = (620,)
    timingRailPressure = (621,)
    aftercoolerWaterInletTemperature = (622,)
    turboOilTemperature = (623, 1)
    particulateTrapInletPressure = (624, 2)
    airFilterDifferentialPressure = (625, 3)
    coolantFilterDifferentialPressure = (626, 2)
    atmosphericPressure = (627, 2)
    ambientAirTemperature = (628, 1)
    exhaustTemperatureRight = (629, 1)
    exhaustTemperatureLeft = (630, 1)
    windingTemperature1 = (631,)
    windingTemperature2 = (632,)
    windingTemperature3 = (633,)
    auxiliaryAnalogInfo = (634,)
    engineTurbocharger1CompressorOutletTemperature = (636,)
    engineIntercoolerTemperature = (637,)
    engineTripFuel = (638,)
    engineTotalFuel = (639, 1)
    tripFuelGasseous = (640,)
    totalFuelGasseous = (641, 1)


class DiscreteInputsAgc150Mains(IntEnum):
    tbPositionOn = 0
    mbPositionOn = 1
    busBarVoltageFrequencyOk = 4
    mainsFailure = 5
    blockMode = 6
    semiAutoMode = 8
    autoMode = 9
    testMode = 10
    tbPositionOff = 11
    mbPositionOff = 12
    island = 13
    automaticMainsFailure = 14
    peakShaving = 15
    fixedPower = 16
    mainsPowerExport = 17
    loadTakeover = 18
    anyAlarmMains = 28


class InputRegistersAgc150Mains(AddressFactorEnum):
    mainsVoltageL1L2 = (501,)
    mainsVoltageL2L3 = (502,)
    mainsVoltageL3L1 = (503,)
    mainsVoltageL1N = (504,)
    mainsVoltageL2N = (505,)
    mainsVoltageL3N = (506,)
    mainsFrequencyL1 = (507, 2)
    mainsFrequencyL2 = (508, 2)
    mainsFrequencyL3 = (509, 2)
    mainsCurrentL1 = (513,)
    mainsCurrentL2 = (514,)
    mainsCurrentL3 = (515,)
    mainsPowerL1 = (516,)
    mainsPowerL2 = (517,)
    mainsPowerL3 = (518,)
    mainsPower = (519,)
    mainsReactivePowerL1 = (520,)
    mainsReactivePowerL2 = (521,)
    mainsReactivePowerL3 = (522,)
    mainsReactivePower = (523,)
    mainsApparentPowerL1 = (524,)
    mainsApparentPowerL2 = (525,)
    mainsApparentPowerL3 = (526,)
    mainsApparentPower = (527,)
    mainsExportReactiveEnergyCounterTotal = (528,)
    mainsExportActiveEnergyCounterDay = (530,)
    mainsExportActiveEnergyCounterWeek = (532,)
    mainsExportActiveEnergyCounterMonth = (534,)
    mainsExportActiveEnergyCounterTotal = (536,)
    mainsPF = (538, 2)
    busBVoltageL1L2 = (539,)
    busBVoltageL2L3 = (540,)
    busBVoltageL3L1 = (541,)
    busBVoltageL1N = (542,)
    busBVoltageL2N = (543,)
    busBVoltageL3N = (544,)
    busBFrequencyL1 = (545,)
    busBFrequencyL2 = (546,)
    busBFrequencyL3 = (547,)
    numberAlarms = (558,)
    numberUnacknowledgedAlarms = (559,)
    numberActiveAcknowledgedAlarms = (560,)
    numberMBOperations = (564,)
    multiInput20 = (583,)
    multiInput21 = (584,)
    multiInput22 = (585,)
    multiInput23 = (587,)
    acAlarms1 = (1000,)
    acAlarms2 = (1001,)
    acAlarms3 = (1002,)
    acAlarms4 = (1003,)
    acAlarms5 = (1004,)
    alarms1 = (1005,)


class TMASector(StrEnum):
    MMC = "M1M3 Cell"
    LPN = "Lower Pylons"
    CTS = "Central Section"
    MPN = "Main Pylons"
    TRS = "Truss"
    MBR = "Mid Baffle Ring"
    TER = "Top End Ring"
    SPD = "Spiders"
    TEA = "Top End Assembly"
    M2H = "M2 Hexapod"
    CHX = "Cam Hexapod"


@dataclass
class TMASensorInfo:
    code: str
    subsector: str
    coordinate: str
    coil: int
    holding_register: int


TMA_SENSOR_DICT: dict[TMASector, list[TMASensorInfo]] = {
    TMASector.MMC: [
        TMASensorInfo(code="AS00", subsector="CB", coordinate="XP", coil=32769, holding_register=432769),
        TMASensorInfo(code="AS01", subsector="CB", coordinate="XN", coil=32771, holding_register=432771),
        TMASensorInfo(code="AS02", subsector="CB", coordinate="YP", coil=32773, holding_register=432773),
        TMASensorInfo(code="AS03", subsector="CB", coordinate="YN", coil=32775, holding_register=432775),
        TMASensorInfo(code="AS04", subsector="DK", coordinate="XP", coil=32777, holding_register=432777),
        TMASensorInfo(code="AS05", subsector="DK", coordinate="XN", coil=32779, holding_register=432779),
        TMASensorInfo(code="AS06", subsector="DK", coordinate="YP", coil=32781, holding_register=432781),
        TMASensorInfo(code="AS07", subsector="DK", coordinate="YN", coil=32783, holding_register=432783),
        TMASensorInfo(code="AS08", subsector="DK", coordinate="XPYP", coil=32785, holding_register=432785),
        TMASensorInfo(code="AS09", subsector="DK", coordinate="XPYN", coil=32787, holding_register=432787),
        TMASensorInfo(code="AS10", subsector="DK", coordinate="XNYP", coil=32789, holding_register=432789),
        TMASensorInfo(code="AS11", subsector="DK", coordinate="XNYN", coil=32791, holding_register=432791),
    ],
    TMASector.LPN: [
        TMASensorInfo(code="BS00", subsector="MD", coordinate="XPYP", coil=32869, holding_register=432869),
        TMASensorInfo(code="BS01", subsector="MD", coordinate="XPYN", coil=32871, holding_register=432871),
        TMASensorInfo(code="BS02", subsector="MD", coordinate="XNYP", coil=32873, holding_register=432873),
        TMASensorInfo(code="BS03", subsector="MD", coordinate="XNYN", coil=32875, holding_register=432875),
    ],
    TMASector.CTS: [
        TMASensorInfo(code="BS04", subsector="CB", coordinate="XP", coil=32969, holding_register=432969),
        TMASensorInfo(code="BS05", subsector="CB", coordinate="XN", coil=32971, holding_register=432971),
        TMASensorInfo(code="BS06", subsector="CB", coordinate="YP", coil=32973, holding_register=432973),
        TMASensorInfo(code="BS07", subsector="CB", coordinate="YN", coil=32975, holding_register=432975),
    ],
    TMASector.MPN: [
        TMASensorInfo(code="BS08", subsector="LW", coordinate="XPYP", coil=33069, holding_register=433069),
        TMASensorInfo(code="BS09", subsector="LW", coordinate="XPYN", coil=33071, holding_register=433071),
        TMASensorInfo(code="CS00", subsector="LW", coordinate="XNYP", coil=33073, holding_register=433073),
        TMASensorInfo(code="CS01", subsector="LW", coordinate="XNYN", coil=33075, holding_register=433075),
        TMASensorInfo(code="BS10", subsector="UP", coordinate="XPYP", coil=33069, holding_register=433069),
        TMASensorInfo(code="BS11", subsector="UP", coordinate="XPYN", coil=33071, holding_register=433071),
        TMASensorInfo(code="CS02", subsector="UP", coordinate="XNYP", coil=33073, holding_register=433073),
        TMASensorInfo(code="CS03", subsector="UP", coordinate="XNYN", coil=33075, holding_register=433075),
    ],
    TMASector.TRS: [
        TMASensorInfo(code="BS12", subsector="LW", coordinate="XPYP", coil=33169, holding_register=433169),
        TMASensorInfo(code="BS13", subsector="LW", coordinate="XPYN", coil=33171, holding_register=433171),
        TMASensorInfo(code="CS04", subsector="LW", coordinate="XNYP", coil=33173, holding_register=433173),
        TMASensorInfo(code="CS05", subsector="LW", coordinate="XNYN", coil=33175, holding_register=433175),
        TMASensorInfo(code="BS14", subsector="LW", coordinate="YPXP", coil=33177, holding_register=433177),
        TMASensorInfo(code="CS06", subsector="LW", coordinate="YPXN", coil=33179, holding_register=433179),
        TMASensorInfo(code="BS15", subsector="LW", coordinate="YNXP", coil=33181, holding_register=433181),
        TMASensorInfo(code="CS07", subsector="LW", coordinate="YNXN", coil=33183, holding_register=433183),
        TMASensorInfo(code="BS16", subsector="UP", coordinate="XPYP", coil=33185, holding_register=433185),
        TMASensorInfo(code="BS17", subsector="UP", coordinate="XPYN", coil=33187, holding_register=433187),
        TMASensorInfo(code="CS08", subsector="UP", coordinate="XNYP", coil=33189, holding_register=433189),
        TMASensorInfo(code="CS09", subsector="UP", coordinate="YPXN", coil=33191, holding_register=433191),
        TMASensorInfo(code="BS18", subsector="UP", coordinate="YPXP", coil=33193, holding_register=433193),
        TMASensorInfo(code="CS10", subsector="UP", coordinate="YPXN", coil=33195, holding_register=433195),
        TMASensorInfo(code="BS19", subsector="UP", coordinate="YNXP", coil=33197, holding_register=433197),
        TMASensorInfo(code="CS11", subsector="UP", coordinate="YNXN", coil=33199, holding_register=433199),
    ],
    TMASector.MBR: [
        TMASensorInfo(code="BS20", subsector="XX", coordinate="XP", coil=33269, holding_register=433269),
        TMASensorInfo(code="CS12", subsector="XX", coordinate="XN", coil=33271, holding_register=433271),
        TMASensorInfo(code="BS21", subsector="XX", coordinate="YP", coil=33273, holding_register=433273),
        TMASensorInfo(code="CS13", subsector="XX", coordinate="YN", coil=33275, holding_register=433275),
    ],
    TMASector.TER: [
        TMASensorInfo(code="BS22", subsector="XX", coordinate="XP", coil=33369, holding_register=433369),
        TMASensorInfo(code="CS14", subsector="XX", coordinate="XN", coil=33371, holding_register=433371),
        TMASensorInfo(code="BS23", subsector="XX", coordinate="YP", coil=33373, holding_register=433373),
        TMASensorInfo(code="CS15", subsector="XX", coordinate="YN", coil=33375, holding_register=433375),
    ],
    TMASector.SPD: [
        TMASensorInfo(code="BS24", subsector="MD", coordinate="XPYP", coil=33469, holding_register=433469),
        TMASensorInfo(code="BS25", subsector="MD", coordinate="XPYN", coil=33471, holding_register=433471),
        TMASensorInfo(code="CS16", subsector="MD", coordinate="XNYP", coil=33473, holding_register=433473),
        TMASensorInfo(code="CS17", subsector="MD", coordinate="XNYN", coil=33475, holding_register=433475),
        TMASensorInfo(code="BS26", subsector="MD", coordinate="YPXP", coil=33469, holding_register=433469),
        TMASensorInfo(code="CS18", subsector="MD", coordinate="YPXN", coil=33471, holding_register=433471),
        TMASensorInfo(code="BS27", subsector="MD", coordinate="YNXP", coil=33473, holding_register=433473),
        TMASensorInfo(code="CS19", subsector="MD", coordinate="YNXN", coil=33475, holding_register=433475),
    ],
    TMASector.TEA: [
        TMASensorInfo(code="BS28", subsector="LW", coordinate="XP", coil=33569, holding_register=433569),
        TMASensorInfo(code="CS20", subsector="LW", coordinate="XN", coil=33571, holding_register=433571),
        TMASensorInfo(code="BS29", subsector="LW", coordinate="YP", coil=33573, holding_register=433573),
        TMASensorInfo(code="CS21", subsector="LW", coordinate="YN", coil=33575, holding_register=433575),
        TMASensorInfo(code="BS30", subsector="MD", coordinate="XP", coil=33577, holding_register=433577),
        TMASensorInfo(code="CS22", subsector="MD", coordinate="XN", coil=33579, holding_register=433579),
        TMASensorInfo(code="BS31", subsector="MD", coordinate="YP", coil=33581, holding_register=433581),
        TMASensorInfo(code="CS23", subsector="MD", coordinate="YN", coil=33583, holding_register=433583),
        TMASensorInfo(code="BS32", subsector="UP", coordinate="XP", coil=33585, holding_register=433585),
        TMASensorInfo(code="CS24", subsector="UP", coordinate="XN", coil=33587, holding_register=433587),
        TMASensorInfo(code="BS33", subsector="UP", coordinate="YP", coil=33589, holding_register=433589),
        TMASensorInfo(code="CS25", subsector="UP", coordinate="YN", coil=33591, holding_register=433591),
    ],
    TMASector.M2H: [
        TMASensorInfo(code="DS00", subsector="FX", coordinate="1", coil=33669, holding_register=433669),
        TMASensorInfo(code="DS01", subsector="FX", coordinate="2", coil=33671, holding_register=433671),
        TMASensorInfo(code="DS02", subsector="FX", coordinate="3", coil=33673, holding_register=433673),
        TMASensorInfo(code="DS03", subsector="FX", coordinate="4", coil=33675, holding_register=433675),
        TMASensorInfo(code="DS04", subsector="FX", coordinate="5", coil=33677, holding_register=433677),
        TMASensorInfo(code="DS05", subsector="FX", coordinate="6", coil=33679, holding_register=433679),
        TMASensorInfo(code="DS06", subsector="MT", coordinate="1", coil=33681, holding_register=433681),
        TMASensorInfo(code="DS07", subsector="MT", coordinate="2", coil=33683, holding_register=433683),
        TMASensorInfo(code="DS08", subsector="MT", coordinate="3", coil=33685, holding_register=433685),
        TMASensorInfo(code="DS09", subsector="MT", coordinate="4", coil=33687, holding_register=433687),
        TMASensorInfo(code="DS10", subsector="MT", coordinate="5", coil=33689, holding_register=433689),
        TMASensorInfo(code="DS11", subsector="MT", coordinate="6", coil=33691, holding_register=433691),
    ],
    TMASector.CHX: [
        TMASensorInfo(code="DS12", subsector="FX", coordinate="7", coil=33769, holding_register=433769),
        TMASensorInfo(code="DS13", subsector="FX", coordinate="8", coil=33771, holding_register=433771),
        TMASensorInfo(code="DS14", subsector="FX", coordinate="9", coil=33773, holding_register=433773),
        TMASensorInfo(code="DS15", subsector="FX", coordinate="10", coil=33775, holding_register=433775),
        TMASensorInfo(code="DS16", subsector="FX", coordinate="11", coil=33777, holding_register=433777),
        TMASensorInfo(code="DS17", subsector="FX", coordinate="12", coil=33779, holding_register=433779),
        TMASensorInfo(code="DS18", subsector="MT", coordinate="7", coil=33781, holding_register=433781),
        TMASensorInfo(code="DS19", subsector="MT", coordinate="8", coil=33783, holding_register=433783),
        TMASensorInfo(code="DS20", subsector="MT", coordinate="9", coil=33785, holding_register=433785),
        TMASensorInfo(code="DS21", subsector="MT", coordinate="10", coil=33787, holding_register=433787),
        TMASensorInfo(code="DS22", subsector="MT", coordinate="11", coil=33789, holding_register=433789),
        TMASensorInfo(code="DS23", subsector="MT", coordinate="12", coil=33791, holding_register=433791),
    ],
}


class DiscreteInputsEaton9sx(IntEnum):
    loadProtectedStatus = 1024
    upsCoupled = 1025
    unitGeneralAlarm = 1026
    configurationFirmwareFault = 1027
    upsInBackupStatus = 1028
    batteryLowWarning = 1029
    lowBattery = 1030
    communicationFault = 1033
    upsOverload = 1034
    emergencyStop = 1035
    batteryToBeChecked = 1037
    deviceVerificationFault = 1038
    upsClass = 1041
    manualBypassPresent = 1045
    modeEco = 1047
    batteryPresent = 1056
    batteryTestFault = 1058
    wiringFault = 1090
    main1VoltageOutOfTolerance = 1096
    main1FuseFault = 1097
    chargerOverTemperatureFault = 1098
    mainFrequencyTolerance = 1099
    redundancyLost = 1111
    maintenancePosition = 1121
    main2Overload = 1125
    outputOnBypass = 1127
    main2FrequencyOutOfTolerance = 1129
    phaseM2OutOfTolerance = 1131
    internalFault = 1136
    main2InternalFault = 1145
    chargerGeneralFault = 1168
    batteryCharge1 = 1169
    batteryCharge2 = 1171
    inverterMajorFault = 1217
    iverterOverload = 1218
    inverterOverTemperature = 1226
    shortCircuit = 1265
    electronicPowerSupplyFault = 1286
    bypassWiringFault = 1287


class InputRegistersEaton9sx(IntEnum):
    currentPhase1Output = 265
    currentPhase2Output = 266
    currentPhase3Output = 267
    voltagePhase1Main2 = 286
    voltagePhase2Main2 = 287
    voltagePhase3Main2 = 288
    outputVoltage1N = 292
    outputVoltage2N = 293
    outputVoltage3N = 294
    batteryVoltage = 301
    outputActivePowerPhase1 = 304
    outputActivePowerPhase2 = 305
    outputActivePowerPhase3 = 306
    outputApparentPowerPhase1 = 307
    outputApparentPowerPhase2 = 308
    outputApparentPowerPhase3 = 309
    outputTotalActivePower = 310
    outputTotalApparentPower = 311
    outputLoadLevel = 313
    powerFactory = 317
    main1Frequency = 318
    main2Frequency = 320
    outputFrequency = 321
    batteryBackupTime = 329
    batteryChargingLevel = 331
    voltageMain1Phase1 = 336
    voltageMain1Phase2 = 337
    voltageMain1Phase3 = 338
    manufacturerName = 416
    productName = 424
    upsModel = 432
    serialNumber = 440
    partNumber = 448
    nominalApparentPower = 521
    nominalActivePower = 529
    nominalBatteryVoltage = 531
