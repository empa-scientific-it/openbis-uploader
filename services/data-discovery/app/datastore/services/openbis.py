from dataclasses import dataclass
from typing import final
import pybis
from datastore.utils import settings
import contextlib
from fastapi import HTTPException, status
from typing import Tuple
from datastore.models import auth as auth_models

@dataclass
class OpenbisUser(auth_models.User):
    space: str
    permid: str

def get_openbis() -> pybis.Openbis:
    config = settings.get_settings()
    return pybis.Openbis(config.openbis_server, verify_certificates=False, use_cache=False)

@contextlib.contextmanager
def openbis_login(username: str, password: str) -> str:
    """
    Get an :obj:`pybis.Openbis` object given
    password and username.
    """
    config = settings.get_settings()
    breakpoint()
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
