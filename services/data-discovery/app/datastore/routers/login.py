from fastapi import APIRouter

from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datastore.utils import files, settings
from datastore.models import datasets, auth as auth_models
from datastore.services.ldap import auth, ldap, session

import argparse as ap
import pathlib as pl
import aiofiles
from datetime import datetime, timedelta
import os
from datastore.services.ldap import session as ldap_session, ldap
from datastore.utils import settings
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel

from datastore.services import auth as auth_service
from datastore.services import openbis as openbis_service
from dataclasses import asdict

from typing import Dict, Union

from pybis import Openbis

router = APIRouter(prefix='/authorize')


#Initialise credentials store
config = settings.get_settings()
cred_context = auth_service.CredentialsContext(config.jws_secret_key, config.jws_secret_key, config.jws_algorithm, config.jws_access_token_expire_minutes)
cred_store = auth_service.CredentialsStore(cred_context)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
#Bind LDAP principal
ldap_principal_conn = ldap_session.get_ldap_connection() 

#Initalise register of resource servers
resource_servers: Dict[str, auth_service.ResourceServer] = {
    'ldap': auth_service.ResourceServerLdap(cred_context, "ldap", ldap_principal_conn),
    'openbis': auth_service.ResourceServerOpenBis(cred_context, "openbis", openbis_service.get_openbis())
}


async def login_all(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Using a single login, create a JWT token with audiences for all services
    """
    rs = resource_servers["openbis"]
    services = list(resource_servers.keys())
    token, cred = rs.login(form_data.username, form_data.password)
    #Create a token for all audiences
    all_token = cred_context.create_access_token(auth_models.TokenData(sub=form_data.username, aud=services, exp=60))
    cred_store.store(all_token, services, cred)
    return  {"access_token": all_token, "token_type": "bearer"}

async def login_single(service: str, form_data: OAuth2PasswordRequestForm = Depends()):
    rs = resource_servers[service]
    token, cred = rs.login(form_data.username, form_data.password)
    cred_store.store(token, [service], cred)
    return  {"access_token": token, "token_type": "bearer"}


@router.post("/{service}/token/", response_model=auth_models.Token)
async def login(service: str, form_data: OAuth2PasswordRequestForm = Depends()):
    if service != 'all':
        return await login_single(service, form_data)
    else:
        return await login_all(form_data)




async def check_single_token(service: str, token: str =  Depends(oauth2_scheme)) -> bool:
    rs = resource_servers[service]
    if cred_store.is_valid(token):
       return rs.verify(token)

async def check_all_token(token: str =  Depends(oauth2_scheme))  -> bool:
    if cred_store.is_valid(token):
        import pytest; pytest.set_trace()
        valid = [rs.id for rs in resource_servers.values() if rs.verify(token)]
    return valid == list(resource_servers.keys())
        
@router.get("/{service}/check/")
async def check_token(service: str, token: str =  Depends(oauth2_scheme)) -> bool:
    if service != 'all':
        return await check_single_token(service, token)
    else:
        return await check_all_token(token)

@router.get("/{service}/logout/")
async def logout(service: str, token: str =  Depends(oauth2_scheme)):
    rs = resource_servers[service]
    rs.logout(token)
    cred_store.remove(token, [service])
    return  {"logged out": token}

def get_user(service: str):
    def _inner(token: str) -> openbis_service.OpenbisUser |  ldap.LdapUser:
        if cred_store.is_valid(token):
            try:
                return resource_servers[service].get_user_info(token)
            except JWTError as e:
                raise HTTPException(401)
        else:
            raise HTTPException(401)
    return _inner

def get_openbis(token: str =  Depends(oauth2_scheme)) -> Openbis:
    rs = resource_servers["openbis"]
    if rs.verify(token):
        ui = rs.get_user_info(token)
        return rs.openbis


@router.get("/{service}/me/", response_model= Union[openbis_service.OpenbisUser,  ldap.LdapUser])
async def read_users_me(service: str, current_user: auth_models.User = Depends(get_user), token: str = Depends(oauth2_scheme)):
    import pytest; pytest.set_trace()
    return current_user(token)


