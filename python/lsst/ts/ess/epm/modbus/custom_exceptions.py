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

__all__ = [
    "NoCoilsDefinedError",
    "NoHoldingRegistersDefinedError",
    "NoDiscreteInputsDefinedError",
    "NoInputRegistersDefinedError",
    "NotConnectedError",
]


class NoCoilsDefinedError(Exception):
    """Exception raised when no coils are defined."""

    pass


class NoHoldingRegistersDefinedError(Exception):
    """Exception raised when no holding registers are defined."""

    pass


class NoDiscreteInputsDefinedError(Exception):
    """Exception raised when no discrete inputs are defined."""

    pass


class NoInputRegistersDefinedError(Exception):
    """Exception raised when no input registers are defined."""

    pass


class NotConnectedError(Exception):
    """Exception raised when not connected."""

    pass
