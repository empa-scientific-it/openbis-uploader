
from dataclasses import dataclass
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datastore.utils import settings
from datastore.models import  auth as auth_models
from datastore.services.ldap import  ldap


from datetime import datetime, timedelta
from datastore.utils import settings
from passlib.context import CryptContext
from jose import JWTError, jwt

import pytest

from typing import Dict

from abc import ABC, abstractmethod

pwd_context = CryptContext(schemes=["sha1_crypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict) -> str:
    """
    Creates an access token 
    """
    config = settings.get_settings()
    to_encode = data.copy()
    access_token_expires = timedelta(minutes=config.jws_access_token_expire_minutes)
    to_encode.update({"exp": access_token_expires})
    encoded_jwt = jwt.encode(to_encode, config.jws_secret_key, algorithm=config.jws_algorithm)
    return encoded_jwt

def decode_access_token(token: str) -> auth_models.Token:
    """
    Given a JWT token, decodes it
    """
    config = settings.get_settings()
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, config.jws_secret_key, algorithms=[config.jws_algorithm])
        return auth_models.Token(**payload)
    except JWTError:
        raise credentials_exception


@dataclass
class ResourceServerPasswordBearer(ABC):
    """
    Represents a generic resource server
    (RS) for which we want to use OAUTH2 password flow for authentication.
    This is an abstract base class, every resource server
    should only implement two methods:
    - login
    - verify
    """
    id: str

    @abstractmethod
    def login(self, username:str, password:str) -> str:
        pass

    @abstractmethod
    def verify(self, token: str) -> bool:
        pass


class ResourceServerLdap(ResourceServerPasswordBearer):

    principal_connection: ldap.Connection

    def login(self, username: str, password:str) -> str:
        with ldap.auth.authenticate(username, password):
            token = create_access_token({"aud": self.id, "sub":username})
            return token

    def verify(self, token: str) -> bool:
        token_data = decode_access_token(token)
        user = ldap.get_user_info(token_data.username)
        return user is not None



async def get_current_user(token: str = Depends(oauth2_scheme)) -> ldap.User:
    config = settings.get_settings()
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, config.jws_secret_key, algorithms=[config.jws_algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = auth_models.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = ldap.get_user_info(token_data.username)
    if user is None:
        raise credentials_exception
    return user