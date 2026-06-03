.. py:currentmodule:: lsst.ts.ess.epm

.. _lsst.ts.ess.version_history:

###############
Version History
###############

.. towncrier release notes start

v0.6.1 (2026-06-03)
===================

Performance Enhancement
-----------------------

- Made sure that all SNMP related telemetry topics always have the sensorName item equal to the configured host name of the SNMP server. (`OSW-2383 <https://rubinobs.atlassian.net//browse/OSW-2383>`_)


v0.6.0 (2026-05-18)
===================

New Features
------------

- Added a Modbus connector for the TMA temperature sensors. (`OSW-2226 <https://rubinobs.atlassian.net//browse/OSW-2226>`_)
- Added agc150mains modbus connector and enumerations. (`OSW-2250 <https://rubinobs.atlassian.net//browse/OSW-2250>`_)
- Added eaton9sx modbus connector and enumerations. (`OSW-2250 <https://rubinobs.atlassian.net//browse/OSW-2250>`_)


Performance Enhancement
-----------------------

- Made it possible to read multiple Modbus addresses at once. (`OSW-2226 <https://rubinobs.atlassian.net//browse/OSW-2226>`_)
- Refactored agc150genset modbus connector to simplify the BaseModbusConnector. (`OSW-2250 <https://rubinobs.atlassian.net//browse/OSW-2250>`_)
- Added the sensorName field for publishing the agcGenset150, agcMains150 and e9sxups telemetry. (`OSW-2250 <https://rubinobs.atlassian.net//browse/OSW-2250>`_)


v0.5.0 (2026-04-24)
===================

New Features
------------

- Extracted all common Modbus processing code into the BaseModbusConnector class. (`OSW-2221 <https://rubinobs.atlassian.net//browse/OSW-2221>`_)


Performance Enhancement
-----------------------

- Moved the SNMP code to the snmp sub module. (`OSW-2221 <https://rubinobs.atlassian.net//browse/OSW-2221>`_)
- Moved the Modbus code to the modbus sub module. (`OSW-2221 <https://rubinobs.atlassian.net//browse/OSW-2221>`_)
- Moved the ModBus simulator setup JSON file to the data dir. (`OSW-2221 <https://rubinobs.atlassian.net//browse/OSW-2221>`_)


v0.4.3 (2026-02-17)
===================

Bug Fixes
---------

- Fixed ModBus simulator telemetry values. (`OSW-1829 <https://rubinobs.atlassian.net//browse/OSW-1829>`_)


v0.4.2 (2026-02-09)
===================

Bug Fixes
---------

- Made simulation mode work for the SnmpDataClient. (`OSW-1799 <https://rubinobs.atlassian.net//browse/OSW-1799>`_)


v0.4.1 (2026-01-28)
===================

Performance Enhancement
-----------------------

- Set conda build string. (`OSW-982 <https://rubinobs.atlassian.net//browse/OSW-982>`_)
- Updated ts_conda_build dependency version. (`OSW-982 <https://rubinobs.atlassian.net//browse/OSW-982>`_)
- Made code compatible with python 3.13. (`OSW-1754 <https://rubinobs.atlassian.net//browse/OSW-1754>`_)


Other Changes and Additions
---------------------------

- Fixed the documentation build. (`OSW-1754 <https://rubinobs.atlassian.net//browse/OSW-1754>`_)


v0.4.0 (2025-06-12)
===================

Performance Enhancement
-----------------------

- Forced always to reconnect. (`DM-50895 <https://rubinobs.atlassian.net//browse/DM-50895>`_)


v0.3.1 (2025-06-04)
===================

Bug Fixes
---------

- Fix payload handling for modbus_agc150_connector. (`OSW-74 <https://rubinobs.atlassian.net//browse/OSW-74>`_)


Other Changes and Additions
---------------------------

- Avoid creation of an http server in simulation mode by properly configuring the pymodbus.server.ModbusSimulatorServer class. (`OSW-74 <https://rubinobs.atlassian.net//browse/OSW-74>`_)


v0.3.0 (2025-05-30)
===================

New Features
------------

- Switched to towncrier and ruff. (`DM-50632 <https://rubinobs.atlassian.net//browse/DM-50632>`_)


Bug Fixes
---------

- Made the code work with the latest version of pysnmp. (`DM-50632 <https://rubinobs.atlassian.net//browse/DM-50632>`_)
- Fixed importing of the version module. (`DM-50632 <https://rubinobs.atlassian.net//browse/DM-50632>`_)


v0.2.0
------

* Moved all SNMP code here from ts_ess_common.

v0.1.0
------

* Initial implementation of a modbus client for AGC 150 Genset controllers.
