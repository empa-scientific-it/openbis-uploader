
from dataclasses import dataclass, asdict
import dataclasses
from multiprocessing.util import abstract_sockets_supported
from platform import python_revision
from venv import create
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

from typing import Dict, Tuple, Optional, List, Set

from abc import ABC, abstractmethod

from pybis import Openbis, person
import pybis

from redis import Redis

from pydantic import fields

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class Credentials(auth_models.BaseModel):
    sub: str
    secret: str  = fields.Field(repr=False)
    aud: str | List[str]


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

    def decode_access_token(self, token: str, audience: List[str]) -> auth_models.TokenData:
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

@dataclass
class AbstractCredentialStore(ABC):
    context: CredentialsContext
    

    @abstractmethod
    def store(self, key: str, audience: str, cred: Credentials) -> None:
        pass
    
    @abstractmethod
    def retreive(self, key: str, audience: str) -> Credentials:
        pass

    @abstractmethod
    def remove(self, key: str, audience: str) -> None:
        pass

    @abstractmethod
    def is_invalidated(self, key: str) -> bool:
        pass

    @classmethod
    @abstractmethod
    def create(cls, *args, **kwargs) -> 'AbstractCredentialStore':
        pass

    def decode_all(self, key: str, audiences: List[str]) -> List[str]:
        """
        Given a token and a list of audiences,
        check if all the claims are fullfilled
        """
        def handle(key: str, audience: str) -> str:
            try:
                jwt.decode(key, self.context.secret_key, self.context.algorithm, audience=audience)
                return audience
            except JWTError:
                return None
        return [aud  for aud in audiences if handle(key, aud)]

@dataclass
class RedisCredentialsStore(AbstractCredentialStore):
    redis: Redis

    @classmethod
    def create(cls, r: Redis, context: CredentialsContext):
        return cls(context = context, redis=r)
    
    def store_key(self, key: str, audience:str, extra:str|None=None):
        k = f"{key}:{audience}"
        if extra:
            fk = f"{k}:{extra}"
        else:
            fk = k
        return fk
    

    def is_invalidated(self, key: str) -> bool:
        val = self.redis.get(self.store_key(key,'invalidated'))
        if val:
            return True
        else: 
            return False
        
    def invalidate(self, key: str):
        self.redis.set(self.store_key(key,'invalidated'), True)
    
    def remove(self, key: str, audience: str):
        self.redis.delete(self.store_key(key, audience))
        self.invalidate(key)

    def store(self, key: str, audience: str, cred: Credentials) -> None:
        if not self.is_invalidated(key):
            valid = self.decode_all(key, audience)
            for v in valid:
                self.redis.set(self.store_key(key, v), cred.json(), ex = self.context.token_expires_minutes)
    
    def retreive(self, key: str, audience: str) -> Credentials | None:
        if not self.is_invalidated(key):
            valid = self.decode_all(key, [audience])
            return self.redis.get(self.store_key(key, valid[0]))
        else:
            raise JWTError("This token has been invalidated")

@dataclass
class CredentialsStore(AbstractCredentialStore):
    """
    A in-memory / redis credential store
    """
    context: CredentialsContext
    items: Dict[Tuple[str, str], Credentials] = dataclasses.field(default_factory=lambda: {})
    invalidated: Set[str] = dataclasses.field(default_factory=lambda: set())


    @classmethod
    def create(cls, context: CredentialsContext, items: Dict[Tuple[str, str], Credentials], invalidated: Set[str]):
        return cls(context, items, invalidated)

    def is_invalidated(self, key: str) -> bool:
        return key not in self.invalidated
    

    def store(self, key: str, audience: str, cred: Credentials) -> None:
        if not self.is_invalidated(key):
            try:
                valid = self.decode_all(key, audience)
                for v in valid:
                    self.items.update({(key, v): cred})
            except JWTError as e:
                raise KeyError(f"The JWT token {key} cannot be validated")
            except KeyError as e:
                raise KeyError(e)
        else:
            raise JWTError("This token has been invalidated")

    def retreive(self, key: str, audience: str) -> Credentials:
        if not self.is_invalidated(key):
            try:
                valid = self.decode_all(key, [audience])
                if audience in valid:
                    return self.items[(key, audience)]
                else:
                    raise KeyError(f"No such credentials ({key}, {audience}) are stored or they were invalidated")
            except JWTError as e:
                raise KeyError(f"The JWT token {key} cannot be validated")
            except KeyError as e:
                raise KeyError(f"No such credentials ({key}, {audience}) are stored or they were invalidated")
        else:
            raise JWTError("This token has been invalidated")
    
    def remove(self, key: str, audience: str) -> None:
        """
        Removes the token by moving it to the list of invalidated tokens
        """
        if (key, audience) in self.items.keys():
            self.items.pop((key, audience))
        self.invalidated.add(key)


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
    
    @abstractmethod
    def logout(self, token: str) -> None:
        pass


@dataclass
class ResourceServerLdap(ResourceServer):

    id: str
    principal_connection: ldap.Connection

    def login(self, username: str, password:str) -> Tuple[str, Credentials]:
        with self.principal_connection as pc:
            with ldap.auth.authenticate(pc, username, password) as con:
                token = self.context.create_access_token(auth_models.TokenData(aud=[self.id], sub=username))
                cd = Credentials(sub=username, aud=self.id, secret=password)
                return token, cd

    def logout(self, token: str) -> None:
        pass

    def verify(self, token: str) -> bool:
        try:
            token_data = self.context.decode_access_token(token, self.id)
            with self.principal_connection as pc:
                user = ldap.get_user_info(pc, token_data.sub)
            return user.username == token_data.sub and self.id in token_data.aud
        except Exception as e:
            return False

    
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
        openbis_token = self.openbis.login(username=username, password=password, save_token=False)
        token = self.context.create_access_token(auth_models.TokenData(aud= [self.id], sub=username))
        cd = Credentials(sub=username, aud=[self.id], secret=openbis_token)
        return token, cd

    def logout(self, token: str) -> None:
        if self.verify(token):
            self.openbis.logout()

    def verify(self, token: str) -> bool:
        try:
            token_data = self.context.decode_access_token(token, self.id)
            return  self.id in token_data.aud and self.openbis.is_session_active()
        except Exception as e:
            return False

    def get_user_info(self, token: str) -> Optional[openbis_service.OpenbisUser]:
        if self.verify(token):
            token_data = self.context.decode_access_token(token, self.id)
            user =  self.openbis.get_user(token_data.sub)
            match user:
                case pybis.person.Person():
                    sp = user.space.permID if user.space else None
                    return openbis_service.OpenbisUser(token_data.sub, sp, user.permId)
                case None:
                    raise ValueError(f"Openbis Person with UID {token_data.sub} not found")

        else:
            raise JWTError(f"Token {token} cannot be verified")


