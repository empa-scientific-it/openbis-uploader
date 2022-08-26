
import argparse as ap
import pybis
import pathlib as pl
from instance_creator.models import OpenbisInstance

parser = ap.ArgumentParser(usage="create_test_structure.py your_instance:port admin_user admin_password config_file.json")
parser.add_argument("url", type=str, help="Url to openbis instance")
parser.add_argument("username", type=str, help="Username")
parser.add_argument("password", type=str, help="password")
parser.add_argument("config", type=pl.Path, help="Path to json configuration file")
parser.add_argument('--wipe', action="store_true", help="If set, wipes the instance clean before creating")
args = parser.parse_args()



#Login
ob = pybis.Openbis(args.url,  verify_certificates=False, use_cache=False)
ob.logout()
ob.login(args.username, args.password)
oi = OpenbisInstance.parse_file(args.config)
oi.create(ob)
