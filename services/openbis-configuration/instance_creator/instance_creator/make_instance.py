
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

import argparse as ap
import pybis
import pathlib as pl
from instance_creator.models import OpenbisInstance

def main():
    parser = ap.ArgumentParser(usage="create_test_structure.py your_instance:port admin_user admin_password config_file.json")
    parser.add_argument("url", type=str, help="Url to openbis instance")
    parser.add_argument("username", type=str, help="Username")
    parser.add_argument("password", type=str, help="password")
    parser.add_argument('what', type=str, choices=['create', 'export'])
    parser.add_argument("config", type=pl.Path, help="Path to json configuration file")
    parser.add_argument('--wipe', action="store_true", help="If set, wipes the instance clean before creating")
    args = parser.parse_args()



    #Login
    ob = pybis.Openbis(args.url,  verify_certificates=False, use_cache=False)
    ob.logout()
    ob.login(args.username, args.password)
    match args.what:
        case 'create':
            if args.wipe:
                oi = OpenbisInstance.reflect(ob)
            oi = OpenbisInstance.parse_file(args.config)
        case 'export':
            instance_config = OpenbisInstance.reflect(ob).export(args.config)


