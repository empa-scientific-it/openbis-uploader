from asyncio.log import logger
from ldap3 import Connection, Server, ALL, SAFE_SYNC
from ...utils import settings
import contextlib
from fastapi import logger

def get_server() -> Server:
    st = settings.get_settings()
    print(st)
    ldap_server = Server(st.ldap_server, st.ldap_port, get_info=ALL)
    return ldap_server

def get_ldap_connection() -> Connection:
    st = settings.get_settings()
    ldap_server = get_server()
    return Connection(ldap_server, st.ldap_principal_name, st.ldap_principal_password, client_strategy=SAFE_SYNC)
