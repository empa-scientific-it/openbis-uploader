from dataclasses import dataclass
from . import session, auth
from typing import List, Dict, Optional, Any
from ...utils import settings
from fastapi import Depends
from ldap3 import Connection
from pydantic import BaseModel
from ldap3.utils import dn
import re 

from ...models import auth as auth_models

@dataclass
class LdapResponse:
    """
    Simple dataclass to represent
    a response of a LDAP search
    """
    dn: str
    raw_dn: str
    attributes: Dict[str, str]
    raw_attributes: Dict[str, str]
    type: str



@dataclass 
class LdapUser(auth_models.User):
    """
    Class to hold the user authentication details
    """
    group: List[str]  | None
    dn: str 
    hashed_password: str

 

def decompose_dn(in_dn: str) -> Dict[str, str] | None :
    """
    Given a LDAP dn, decompose
    it into its element and return
    a dictionary
    """
    parsed_dn = dn.parse_dn(in_dn)
    return {k:v for k,v,*rest in parsed_dn}

def ldap_search(con: Connection, query: str, **kwargs) -> Optional[List[LdapResponse]]:
    """
    Given a ldap Connection and a query string, returns
    the response (if any) or none.
    """
    status: bool
    result: Dict[Any, Any]
    response: Optional[List[LdapResponse]] 
    config = settings.get_settings()
    status, result, response, *rest = con.search(config.ldap_base, query, **kwargs)
    if status:
        return [LdapResponse(**r) for r in response]
 
def get_groups(con: Connection, uid: str) -> Optional[List[str]]:
    """
    Get a list of groups from the given ldap connection
    """
    import pytest; pytest.set_trace()
    response = ldap_search(con, f'(uid={uid})', attributes='memberOf')
    if response:
        responses = [at['ou'] for dt in response if (at := dt.get('attributes'))]
        return [el for sl in responses for el in sl]

def get_user_dn(con: Connection, username: str) -> Optional[str]:
    """
    Given an username, get the full distinguished name
    """
    response = ldap_search(con, f"(&(objectclass=inetOrgPerson)(uid={username}))", attributes="+")
    if response:
        return response[0].dn

def get_user_info(con: Connection, uid: str) -> LdapUser | None:
    """
    Given a ldap connection and an user id,
    returns the user info as an :obj:User object
    """
    response = ldap_search(con, f"(&(objectclass=inetOrgPerson)(uid={uid}))", attributes=["+","*"])
    if response:
        resp = response[0]
        dn_dict = decompose_dn(resp.dn)
        pw = extract_password_hash((resp.attributes['userPassword'][0]).decode("utf-8"))
        return LdapUser(username=uid, dn=resp.dn, group=resp.attributes.get('memberOf'), hashed_password=pw)

def extract_password_hash(hash: str) -> str:
    """
    Given a password hash in the ldap form "{SHA}passwordhas"
    extract the hash only
    """
    pat = re.compile(r"(\{\w+\})(\S+)")
    match pat.search(hash).groups():
        case str(method), str(hash):
            ret = hash
        case str(pwd):
            ret = pwd
    return ret