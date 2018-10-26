# Copyright (C) 2018 Krishna Moniz

# This package contains the code for the CA
# This __init__ file will receive method calls from run.py (see parent directory)
# and forward them to the right module (see other py files in this folder)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


def perform_action(message: str='NO MESSAGE'):
    print(message)
