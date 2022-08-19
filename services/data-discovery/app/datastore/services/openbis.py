from typing import final
import pybis
from datastore.utils import settings
import contextlib
from fastapi import HTTPException, status
from typing import Tuple



@contextlib.contextmanager
def openbis_login(username: str, password: str) -> str:
    """
    Get an :obj:`pybis.Openbis` object given
    password and username.
    """
    config = settings.get_settings()
    breakpoint()
    try:
        pb = pybis.Openbis(config.openbis_server, verify_certificates=False)
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

