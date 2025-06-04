.. py:currentmodule:: lsst.ts.ess.epm

.. _lsst.ts.ess.version_history:

###############
Version History
###############

.. towncrier release notes start

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
