from fastapi import APIRouter, logger

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
from redis import Redis
from datastore.utils.redis import get_redis

from typing import Dict, Union

from pybis import Openbis

router = APIRouter(prefix='/authorize')



def get_credential_context() -> auth_service.CredentialsContext:
    #Initialise credentials store
    config = settings.get_settings()
    cred_context = auth_service.CredentialsContext(config.jws_secret_key, config.jws_secret_key, config.jws_algorithm, config.jws_access_token_expire_minutes)
    return cred_context



items = dict()
invalidated = set()
def get_credential_store(cred_context: auth_service.CredentialsContext = Depends(get_credential_context), redis: Redis = Depends(get_redis)) -> auth_service.CredentialsStore:
    cs = auth_service.RedisCredentialsStore.create(redis, cred_context)
    return cs
    

def get_resource_serves(cred_context: auth_service.CredentialsContext = Depends(get_credential_context)) -> Dict[str, auth_service.ResourceServer]:        
    #Bind LDAP principal
    ldap_principal_conn = ldap_session.get_ldap_connection() 
    #Initalise register of resource servers
    resource_servers: Dict[str, auth_service.ResourceServer] = {
        'ldap': auth_service.ResourceServerLdap(cred_context, "ldap", ldap_principal_conn),
        'openbis': auth_service.ResourceServerOpenBis(cred_context, "openbis", openbis_service.get_openbis())
    }
    return resource_servers

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def login_all(form_data: OAuth2PasswordRequestForm, cred_store:auth_service.CredentialsStore, cred_context: auth_service.CredentialsContext, resource_servers: Dict[str, auth_service.ResourceServer]):
    """
    Using a single login, create a JWT token with audiences for all services
    """
    rs = resource_servers["openbis"]
    services = list(resource_servers.keys())
    token, cred = rs.login(form_data.username, form_data.password)
    #Create a token for all audiences
    if token:
        all_token = cred_context.create_access_token(auth_models.TokenData(sub=form_data.username, aud=services, exp=60))
        cred_store.store(all_token, services, cred)
        return  {"access_token": all_token, "token_type": "bearer"}
    else:
        raise HTTPException(401)


async def login_single(form_data: OAuth2PasswordRequestForm, service: str, cred_store:auth_service.CredentialsStore, resource_servers: Dict[str, auth_service.ResourceServer]):
    rs = resource_servers[service]
    token, cred = rs.login(form_data.username, form_data.password)
    cred_store.store(token, service, cred)
    return  {"access_token": token, "token_type": "bearer"}


@router.post("/{service}/token", response_model=auth_models.Token)
async def login(service: str, form_data: OAuth2PasswordRequestForm = Depends(), cred_context: auth_service.CredentialsContext = Depends(get_credential_context), cred_store:auth_service.CredentialsStore = Depends(get_credential_store),  resource_servers: Dict[str, auth_service.ResourceServer] = Depends(get_resource_serves) ):
    logger.logger.info(form_data)
    if service != 'all':
        return await login_single(form_data, service, cred_store, resource_servers)
    else:
        return await login_all(form_data, cred_store, cred_context, resource_servers)




async def check_single_token(service: str, token, cred_store:auth_service.CredentialsStore,  resource_servers: Dict[str, auth_service.ResourceServer]) -> bool:
    rs = resource_servers[service]
    if not cred_store.is_invalidated(token):
       return rs.verify(token)
    else:
        return False

async def check_all_token(token: str, cred_store:auth_service.CredentialsStore, resource_servers: Dict[str, auth_service.ResourceServer])  -> bool:
    if not cred_store.is_invalidated(token):
        valid = [rs.id for rs in resource_servers.values() if rs.verify(token)]
        return valid == list(resource_servers.keys())
    else:
        return False
   

@router.get("/{service}/check", response_model=auth_models.TokenValidity)
async def check_token(service: str, token: str, cred_store:auth_service.CredentialsStore = Depends(get_credential_store), resource_servers: Dict[str, auth_service.ResourceServer] = Depends(get_resource_serves)) -> Dict:
    import pytest; pytest.set_trace()
    if service != 'all':
        val = await check_single_token(service, token, cred_store, resource_servers)
    else:
        val = await check_all_token(token, cred_store, resource_servers)
    return {'token': token, 'valid': val}


@router.get("/all/logout")
async def logout_all(token: str =  Depends(oauth2_scheme),  resource_servers: Dict[str, auth_service.ResourceServer] = Depends(get_resource_serves)):
    for serv in resource_servers.keys():
        await logout_single(serv, token)
    return  {"logged out": token}

@router.get("/{service}/logout")
async def logout_single(service: str, token: str =  Depends(oauth2_scheme), cred_store:auth_service.CredentialsStore = Depends(get_credential_store), resource_servers: Dict[str, auth_service.ResourceServer] = Depends(get_resource_serves)):
    print(service)
    rs = resource_servers[service]
    rs.logout(token)
    cred_store.remove(token, service)
    return  {"logged out": token}


def get_user(service: str, cred_store:auth_service.CredentialsStore, resource_servers: Dict[str, auth_service.ResourceServer]):
    def _inner(token: str) -> openbis_service.OpenbisUser |  ldap.LdapUser:
        if not cred_store.is_invalidated(token):
            try:
                return resource_servers[service].get_user_info(token)
            except JWTError as e:
                raise HTTPException(401)
        else:
            raise HTTPException(401)
    return _inner

def get_openbis(token: str =  Depends(oauth2_scheme), resource_servers: Dict[str, auth_service.ResourceServer] = Depends(get_resource_serves)) -> Openbis:
    rs = resource_servers["openbis"]
    if rs.verify(token):
        ui = rs.get_user_info(token)
        return rs.openbis


@router.get("/{service}/me", response_model= Union[openbis_service.OpenbisUser,  ldap.LdapUser])
async def read_users_me(service: str, token: str = Depends(oauth2_scheme), cred_store:auth_service.CredentialsStore = Depends(get_credential_store), resource_servers: Dict[str, auth_service.ResourceServer] = Depends(get_resource_serves)):
    return get_user(service, cred_store, resource_servers)(token)


