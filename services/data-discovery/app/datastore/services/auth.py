
from dataclasses import dataclass, asdict
import dataclasses
from platform import python_revision
from wsgiref import validate
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, OAuth2
from datastore.utils import settings
from datastore.models import  auth as auth_models
from datastore.services.ldap import  ldap
from datastore.services import openbis as openbis_service

from datetime import datetime, timedelta
from datastore.utils import settings
from jose import JWTError, jwt
import bcrypt

from typing import Dict, Tuple, Optional, List

from abc import ABC, abstractmethod

from pybis import Openbis, person
import pybis



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@dataclass
class Credentials:
    sub: str
    secret: str = dataclasses.field(repr=False)
    aud: str


@dataclass
class CredentialsContext:

    secret_key: str = dataclasses.field(repr=False)
    storage_key: str = dataclasses.field(repr=False)
    algorithm: str
    token_expires_minutes: int

    def create_access_token(self, data: auth_models.TokenData) -> str:
        """
        Creates an access token 
        """
        access_token_expires = datetime.now() + timedelta(minutes=self.token_expires_minutes)
        encoded_jwt = jwt.encode(data.dict() | {"exp": access_token_expires.timestamp()}, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def decode_access_token(self, token: str, audience: str) -> auth_models.TokenData:
        """
        Given a JWT token, decodes it
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm], audience=audience,)
            return auth_models.TokenData(**payload)
        except JWTError:
            raise credentials_exception

    def store(self, jwt_token: str, audience: str, secret: str):
        """
        Stores an entry (token/password) of (jwt token)
        """       
        payload = self.decode_access_token(jwt_token, audience)
        creds = Credentials(payload.sub, secret, payload.aud)
        self.items.update({jwt_token: creds})

    def retreive(self, jwt_token: str) -> Optional[Credentials]:
        """
        Given an url and the corresponding user, retreive
        the token, user tuple (if available)
        """
        self.items.get(jwt_token)

@dataclass
class CredentialsStore:
    context: CredentialsContext
    items: Dict[Tuple[str, str], Credentials] = dataclasses.field(default_factory=lambda: {})

    def store(self, key: str, audience: str, cred: Credentials) -> None:
        try:
            jwt.decode(key, self.context.secret_key, self.context.algorithm, audience=audience)
            self.items.update({(key, audience): cred})
        except JWTError as e:
            raise KeyError(f"The JWT token {key} cannot be validated")

    def retreive(self, key: str, audience: str) -> Credentials:
        try:
            jwt.decode(key, self.context.secret_key, self.context.algorithm, audience=audience)
            return self.items[(key, audience)]
        except JWTError as e:
            raise KeyError(f"The JWT token {key} cannot be validated")
        except KeyError as e:
            raise KeyError(f"No such credentials ({key}, {audience}) are stored")
    



@dataclass
class ResourceServer(ABC):
    """
    Represents a generic resource server
    (RS) for which we want to use OAUTH2 password flow for authentication.
    This is an abstract base class, every resource server
    should only implement two methods:
    - login
    - verify
    - get credentials
    - get_user_info
    """

    context: CredentialsContext
    id: str

    @abstractmethod
    def login(self, username:str, password:str) -> Tuple[str, Credentials]:
        pass

    @abstractmethod
    def verify(self, token: str) -> bool:
        pass

    # @abstractmethod
    # def get_credentials(self, token:str) -> Tuple[str, str]:
    #     pass

    @abstractmethod
    def get_user_info(self, token:str) -> auth_models.User:
        pass 

@dataclass
class ResourceServerLdap(ResourceServer):

    id: str
    principal_connection: ldap.Connection

    def login(self, username: str, password:str) -> Tuple[str, Credentials]:
        with self.principal_connection as pc:
            with ldap.auth.authenticate(pc, username, password) as con:
                token = self.context.create_access_token(auth_models.TokenData(aud=self.id, sub=username))
                cd = Credentials(sub=username, aud=self.id, secret=password)
                return token, cd

    def verify(self, token: str) -> bool:
        token_data = self.context.decode_access_token(token, self.id)
        with self.principal_connection as pc:
            user = ldap.get_user_info(pc, token_data.sub)
        return user.username == token_data.sub and self.id in token_data.aud
    

    
    def get_user_info(self, token: str) -> ldap.LdapUser:
        if self.verify(token):
            with self.principal_connection as pc:
                token_content = self.context.decode_access_token(token, self.id)
                return ldap.get_user_info(pc, token_content.sub)
        else:
            raise JWTError("Cannot verify token")

@dataclass
class ResourceServerOpenBis(ResourceServer):

    id: str
    openbis: Openbis

    def login(self, username: str, password: str) -> Tuple[str, Credentials]:
        openbis_token = self.openbis.login(username, password)
        token = self.context.create_access_token(auth_models.TokenData(aud= self.id, sub=username))
        cd = Credentials(sub=username, aud=self.id, secret=openbis_token)
        return token, cd

    def verify(self, token: str) -> bool:
        token_data = self.context.decode_access_token(token, self.id)
        return  self.id in token_data.aud and self.openbis.is_token_valid()

    def get_user_info(self, token: str) -> Optional[openbis_service.OpenbisUser]:
        if self.verify(token):
            token_data = self.context.decode_access_token(token, self.id)
            user =  self.openbis.get_user(token_data.sub)
            match user:
                case pybis.person.Person():
                    return openbis_service.OpenbisUser(token_data.sub, user.space.permId, user.permId)
                case None:
                    raise ValueError(f"Openbis Person with UID {token_data.sub} not found")
                case Any:
                    return user
        else:
            raise JWTError(f"Token {token} cannot be verified")

