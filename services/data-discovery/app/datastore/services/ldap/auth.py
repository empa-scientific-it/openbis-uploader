
import contextlib
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import Depends, HTTPException, status
from . import session, ldap
from ldap3 import Connection
from ldap3.core.exceptions import LDAPException
from ...utils import settings
def make_username(base:str, user: str) -> str:
    """
    Given an username, forms a full LDAP dn to use
    for LDAP authentication
    """
    return f"{base},uid={user}"

security = HTTPBasic()

@contextlib.contextmanager
def authenticate(principal_con: Connection, username: str, password: str):
    server = session.get_server()
    set = settings.get_settings()
    user_info = ldap.get_user_info(principal_con, username)
    try:
        con = Connection(server, user=user_info.dn, password=password, auto_bind=True, authentication=set.ldap_authentication)
    except LDAPException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid authentication credentials {username}, {password}"
        )
    try:
        if con.bound:
            yield con
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Invalid authentication credentials {username}, {password}")
    finally:
        con.unbind()


