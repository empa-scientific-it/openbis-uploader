from dataclasses import dataclass
from typing import final
from urllib import request
import pybis
from datastore.utils import settings
import contextlib
from fastapi import HTTPException, status
from typing import Tuple
from datastore.models import auth as auth_models
from datastore.models import openbis as openbis_models
import pathlib as pl
from instance_creator import views as openbis_views
from fastapi import Form
from functools import cache
import requests

@dataclass
class OpenbisUser(auth_models.User):
    space: str | None
    permid: str | None 


#TODO use a better method to initialise only once
@cache
def get_openbis() -> pybis.Openbis:
    config = settings.get_settings()
    return pybis.Openbis(config.openbis_server, verify_certificates=False, token=False, allow_http_but_do_not_use_this_in_production_and_only_within_safe_networks=True, use_cache=True)



@contextlib.contextmanager
def openbis_login(username: str, password: str) -> str:
    """
    Get an :obj:`pybis.Openbis` object given
    password and username.
    """
    config = settings.get_settings()
    try:
        pb = get_openbis()
        token = pb.login(username, password)
        yield token
    except Exception as e:
        credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could login to openbis",
        headers={"WWW-Authenticate": "Bearer"})
        raise credentials_exception
    finally:
        pb.logout()



def delete_all(ob: pybis.Openbis, type:str):
    t = ob.new_transaction()
    for s in ob.get_object(type==type):
        t.add(s)



def upload_file_to_lims(ob: pybis.Openbis, file: pl.Path):
    """
    Upload a file to the ELN-LIMS file service. 
    This is used to add images or other attachments to the ELN.
    For more information, see https://unlimited.ethz.ch/display/openBISDoc2010/openBIS+Application+Server+Upload+Service
    """
    #https://localhost:8443/datastore_server/session_workspace_file_upload?filename=BatchLog.csv&id=1&startByte=0&endByte=13579&sessionID=admin-221007110617270xD31CE168E1158E7563DB86B78647A026
    path = f"{ob.url}/openbis/openbis/file-service/eln-lims?"
    params = {'type': 'Files', 'id':1, 'sessionID':ob.token, 'startByte':0, 'endByte':0}
    resp = requests.post(path, params=params, files={'upload': (file.name, open(file, 'rb'))}, verify=False)
    import pytest; pytest.set_trace()
    # with openbis_models.OpenbisElnUpload(type='file', files={'a': file}, sessionID=ob.token).to_form() as files:
        # resp = requests.post(path, files=files, verify=False)
        # import pytest; pytest.set_trace()
        
def get_file_from_lims(ob: pybis.Openbis, name: str):
    path = f"{ob.url}/openbis/openbis/upload"