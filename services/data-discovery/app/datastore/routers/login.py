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


@router.post("/{service}/token/", response_model=auth_models.Token)
async def login(service: str, form_data: OAuth2PasswordRequestForm = Depends()):
    rs = resource_servers[service]
    token, cred = rs.login(form_data.username, form_data.password)
    cred_store.store(token, service, cred)
    return  {"access_token": token, "token_type": "bearer"}

def get_user(service: str):
    def _inner(token: str) -> openbis_service.OpenbisUser |  ldap.LdapUser:
        return resource_servers[service].get_user_info(token)
    return _inner

@router.get("/{service}/me/", response_model= Union[openbis_service.OpenbisUser,  ldap.LdapUser])
async def read_users_me(service: str, current_user: auth_models.User = Depends(get_user), token: str = Depends(oauth2_scheme)):
    return current_user(token)


