""""
Openbis instance configurator.
Copyright (C) 2022 Simone Baffelli

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from setuptools import find_packages, setup  # or find_namespace_packages
setup(name='instance-creator',
      version='1.0',
      py_modules=find_packages(where='.'),
      scripts=['instance_creator/make_instance.py'],
      requires=['pybis', 'pydantic']
      )