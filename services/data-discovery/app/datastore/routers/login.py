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
from datastore.services.ldap import session, ldap
from datastore.utils import settings
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel

from datastore.services import auth as auth_service
from datastore.services import openbis as openbis_service
from dataclasses import asdict


router = APIRouter(prefix='/authorize')


resource_servers = {
    'LDAP': auth_service.ResourceServerLdap()
}

@router.post("/ldap/",response_model=auth_models.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    config = settings.get_settings()
    try:
        with auth.authenticate(form_data.username, form_data.password) as ldap_user:
            user_info = ldap.get_user_info(form_data.username)
            access_token_expires = timedelta(minutes=config.jws_access_token_expire_minutes)
            token_data = auth_models.TokenData(sub=form_data.username, dn=user_info.dn, group=user_info.group)
            access_token = auth_service.create_access_token(
                data=asdict(token_data), expires_delta=access_token_expires
            )
            
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/me/", response_model=ldap.User)
async def read_users_me(current_user: ldap.User = Depends(auth_service.get_current_user)):
    return current_user