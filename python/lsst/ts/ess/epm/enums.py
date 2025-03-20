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

from enum import Enum, IntEnum

ARRAY_FIELDS_AGC150 = {
    "anyAlarmPMS": (
        "anyAlarmPMS1",
        "anyAlarmPMS2",
        "anyAlarmPMS3",
        "anyAlarmPMS4",
        "anyAlarmPMS5",
        "anyAlarmPMS6",
        "anyAlarmPMS7",
        "anyAlarmPMS8",
    ),
    "readyAutoStartDG": (
        "readyAutoStartDG1",
        "readyAutoStartDG2",
        "readyAutoStartDG3",
        "readyAutoStartDG4",
        "readyAutoStartDG5",
        "readyAutoStartDG6",
        "readyAutoStartDG7",
        "readyAutoStartDG8",
    ),
    "windingTemperature": (
        "windingTemperature1",
        "windingTemperature2",
        "windingTemperature3",
    ),
}


class InputRegistersAgc150DecimalFactor(Enum):
    applicationVersion = 0
    generatorVoltageL1L2 = 0
    generatorVoltageL2L3 = 0
    generatorVoltageL3L1 = 0
    generatorVoltageL1N = 0
    generatorVoltageL2N = 0
    generatorVoltageL3N = 0
    generatorFrequencyL1 = 2
    generatorFrequencyL2 = 2
    generatorFrequencyL3 = 2
    generatorVoltagePhaseAngleL1L2 = 1
    generatorVoltagePhaseAngleL2L3 = 1
    generatorVoltagePhaseAngleL3L1 = 1
    generatorCurrentL1 = 0
    generatorCurrentL2 = 0
    generatorCurrentL3 = 0
    generatorPowerL1 = 0
    generatorPowerL2 = 0
    generatorPowerL3 = 0
    generatorPower = 0
    generatorReactivePowerL1 = 0
    generatorReactivePowerL2 = 0
    generatorReactivePowerL3 = 0
    generatorReactivePower = 0
    generatorApparentPowerL1 = 0
    generatorApparentPowerL2 = 0
    generatorApparentPowerL3 = 0
    generatorApparentPower = 0
    generatorExportReactiveEnergyCounterTotal = 0
    generatorExportActiveEnergyCounterDay = 0
    generatorExportActiveEnergyCounterWeek = 0
    generatorExportActiveEnergyCounterMonth = 0
    generatorExportActiveEnergyCounterTotal = 0
    generatorPF = 2
    busBVoltageL1L2 = 0
    busBVoltageL2L3 = 0
    busBVoltageL3L1 = 0
    busBVoltageL1N = 0
    busBVoltageL2N = 0
    busBVoltageL3N = 0
    busBFrequencyL1 = 2
    busBFrequencyL2 = 2
    busBFrequencyL3 = 2
    busBVoltagePhaseAngleL1L2 = 1
    busBVoltagePhaseAngleL2L3 = 1
    busBVoltagePhaseAngleL3L1 = 1
    uBBL1uGENL1PhaseAngle = 0
    uBBL2uGENL2PhaseAngle = 0
    uBBL3uGENL3PhaseAngle = 0
    absoluteRunningHours = 0
    relativeRunningHours = 0
    numberAlarms = 0
    numberUnacknowledgedAlarms = 0
    numberActiveAcknowledgedAlarms = 0
    numberGBOperations = 0
    numberMBOperations = 0
    startAttempts = 0
    dcSupplyTerm12 = 1
    serviceTimer1RunningHours = 0
    serviceTimer1RunningDays = 0
    serviceTimer2RunningHours = 0
    serviceTimer2RunningDays = 0
    cosPhi = 2
    cosPhiType = 0
    rpm = 0
    runningHoursLoadProfile = 0
    multiInput20 = 0
    multiInput21 = 0
    multiInput22 = 0
    multiInput23 = 0
    mainsPower = 0
    engineSpeed = 0
    engineCoolantTemperature = 1
    engineOilPressure = 2
    numberActualFaults = 0
    engineOilTemperature = 1
    fuelTemperature = 0
    intakeManifold1Pressure = 2
    airInletTemperature = 0
    coolantLevel = 1
    fuelRate = 1
    chargeAirPressure = 0
    intakeManifold1Temperature = 0
    driversDemandEnginePercentTorque = 0
    actualEnginePercentTorque = 0
    acceleratorPedalPosition = 0
    percentLoadCurrentSpeed = 0
    airInletPressure = 2
    exhaustGasTemperature = 1
    engineHours = 0
    engineOilFilterDifferentialPressure = 2
    keyswitchBatteryPotential = 1
    fuelDeliveryPressure = 2
    engineOilLevel = 1
    crankcasePressure = 2
    coolantPressure = 2
    waterInFuel = 0
    blowbyFlow = 0
    fuelRailPressure = 0
    timingRailPressure = 0
    aftercoolerWaterInletTemperature = 0
    turboOilTemperature = 1
    particulateTrapInletPressure = 2
    airFilterDifferentialPressure = 3
    coolantFilterDifferentialPressure = 2
    atmosphericPressure = 2
    ambientAirTemperature = 1
    exhaustTemperatureRight = 1
    exhaustTemperatureLeft = 1
    windingTemperature = 0
    auxiliaryAnalogInfo = 0
    engineTurbocharger1CompressorOutletTemperature = 0
    engineIntercoolerTemperature = 0
    engineTripFuel = 0
    engineTotalFuel = 1
    tripFuelGasseous = 0
    totalFuelGasseous = 1


class DiscreteInputsAgc150(IntEnum):
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


class InputRegistersAgc150(IntEnum):
    applicationVersion = 500
    generatorVoltageL1L2 = 501
    generatorVoltageL2L3 = 502
    generatorVoltageL3L1 = 503
    generatorVoltageL1N = 504
    generatorVoltageL2N = 505
    generatorVoltageL3N = 506
    generatorFrequencyL1 = 507
    generatorFrequencyL2 = 508
    generatorFrequencyL3 = 509
    generatorVoltagePhaseAngleL1L2 = 510
    generatorVoltagePhaseAngleL2L3 = 511
    generatorVoltagePhaseAngleL3L1 = 512
    generatorCurrentL1 = 513
    generatorCurrentL2 = 514
    generatorCurrentL3 = 515
    generatorPowerL1 = 516
    generatorPowerL2 = 517
    generatorPowerL3 = 518
    generatorPower = 519
    generatorReactivePowerL1 = 520
    generatorReactivePowerL2 = 521
    generatorReactivePowerL3 = 522
    generatorReactivePower = 523
    generatorApparentPowerL1 = 524
    generatorApparentPowerL2 = 525
    generatorApparentPowerL3 = 526
    generatorApparentPower = 527
    generatorExportReactiveEnergyCounterTotal = 528
    generatorExportActiveEnergyCounterDay = 530
    generatorExportActiveEnergyCounterWeek = 532
    generatorExportActiveEnergyCounterMonth = 534
    generatorExportActiveEnergyCounterTotal = 536
    generatorPF = 538
    busBVoltageL1L2 = 539
    busBVoltageL2L3 = 540
    busBVoltageL3L1 = 541
    busBVoltageL1N = 542
    busBVoltageL2N = 543
    busBVoltageL3N = 544
    busBFrequencyL1 = 545
    busBFrequencyL2 = 546
    busBFrequencyL3 = 547
    busBVoltagePhaseAngleL1L2 = 548
    busBVoltagePhaseAngleL2L3 = 549
    busBVoltagePhaseAngleL3L1 = 550
    uBBL1uGENL1PhaseAngle = 551
    uBBL2uGENL2PhaseAngle = 552
    uBBL3uGENL3PhaseAngle = 553
    absoluteRunningHours = 554
    relativeRunningHours = 556
    numberAlarms = 558
    numberUnacknowledgedAlarms = 559
    numberActiveAcknowledgedAlarms = 560
    numberGBOperations = 563
    numberMBOperations = 564
    startAttempts = 566
    dcSupplyTerm12 = 567
    serviceTimer1RunningHours = 569
    serviceTimer1RunningDays = 570
    serviceTimer2RunningHours = 571
    serviceTimer2RunningDays = 572
    cosPhi = 573
    cosPhiType = 574
    rpm = 576
    runningHoursLoadProfile = 577
    multiInput20 = 583
    multiInput21 = 584
    multiInput22 = 585
    multiInput23 = 587
    mainsPower = 592
    engineSpeed = 593
    engineCoolantTemperature = 594
    engineOilPressure = 595
    numberActualFaults = 596
    engineOilTemperature = 597
    fuelTemperature = 598
    intakeManifold1Pressure = 599
    airInletTemperature = 600
    coolantLevel = 601
    fuelRate = 602
    chargeAirPressure = 603
    intakeManifold1Temperature = 604
    driversDemandEnginePercentTorque = 605
    actualEnginePercentTorque = 606
    acceleratorPedalPosition = 607
    percentLoadCurrentSpeed = 608
    airInletPressure = 609
    exhaustGasTemperature = 610
    engineHours = 611
    engineOilFilterDifferentialPressure = 612
    keyswitchBatteryPotential = 613
    fuelDeliveryPressure = 614
    engineOilLevel = 615
    crankcasePressure = 616
    coolantPressure = 617
    waterInFuel = 618
    blowbyFlow = 619
    fuelRailPressure = 620
    timingRailPressure = 621
    aftercoolerWaterInletTemperature = 622
    turboOilTemperature = 623
    particulateTrapInletPressure = 624
    airFilterDifferentialPressure = 625
    coolantFilterDifferentialPressure = 626
    atmosphericPressure = 627
    ambientAirTemperature = 628
    exhaustTemperatureRight = 629
    exhaustTemperatureLeft = 630
    windingTemperature1 = 631
    windingTemperature2 = 632
    windingTemperature3 = 633
    auxiliaryAnalogInfo = 634
    engineTurbocharger1CompressorOutletTemperature = 636
    engineIntercoolerTemperature = 637
    engineTripFuel = 638
    engineTotalFuel = 639
    tripFuelGasseous = 640
    totalFuelGasseous = 641
