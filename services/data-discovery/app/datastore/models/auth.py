from pydantic import BaseModel
from typing import Dict, Optional, Tuple, List
from passlib.context import CryptContext
from dataclasses import dataclass
import datetime as dt

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    sub: str | None = None
    aud: str | None | List[str] = None
    exp: int | None = None
    iat: int | None = dt.datetime.now().timestamp()


class TokenValidity(BaseModel):
    token: str
    valid: bool

@dataclass
class User:
    username: str