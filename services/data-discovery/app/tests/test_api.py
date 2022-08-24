
import pathlib as pl
import tempfile as tf
import sys
from fastapi import FastAPI
from fastapi.testclient import TestClient
from datastore.routers import login, data, openbis
from datastore.utils import settings
from datastore.utils import files
import os
from typing import Dict, Any
import pytest

import tempfile as tf

@pytest.fixture
def client() -> TestClient:
    app = FastAPI()
    app.include_router(login.router)
    app.include_router(data.router)
    app.include_router(openbis.router)
    client = TestClient(app)
    return client

@pytest.fixture
def login_data() -> Dict[str, str]:
    def _inner(service:str, user:str = 'basi'):
        creds = {'ldap':[dict(username = "basi", password="password"), dict(username='baan', password="password")],'openbis':[dict(username = "basi", password="password"), dict(username='baan', password="password")]}
        return [c for c in creds[service] if c['username'] == user][0]
    return _inner

@pytest.fixture
def token(client, login_data) -> Dict[Any, Any]:
    def _inner(service:str, user: str = "basi"):
        response = client.post(f"/authorize/{service}/token/", data=login_data(service, user))
        tok = response.json()
        token = tok['access_token']
        headers = {"Authorization": f"Bearer {token}"}
        return headers
    return _inner

@pytest.fixture
def temp_files(client, token):
    app_settings = settings.get_settings()
    response = client.get("/authorize/ldap/me/", headers=token("ldap"))
    print(response.json())
    ds = files.InstanceDataStore(app_settings.base_path, response.json()['group'])
    cf = tf.NamedTemporaryFile(dir = ds.path)
    yield cf
    cf.close()
 
def test_auth_fail(client):
    response = client.post("/authorize/ldap/token/")
    assert response.status_code == 422

def test_ldap_auth_success(client, login_data):
    response = client.post("/authorize/ldap/token/", data=login_data("ldap"))
    tok = response.json()
    assert response.status_code == 200 

def test_openbis_auth_success(client, login_data):
    response = client.post("/authorize/openbis/token/", data=login_data("openbis"))
    tok = response.json()
    assert response.status_code == 200

def test_multiple_auth(client, login_data):
    """
    Check if the different user get different tokens
    """
    def get_user(un: str):
        token_req = client.post("/authorize/openbis/token/", data=login_data("openbis", un))
        token = token_req.json()['access_token']
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/authorize/openbis/me/", headers=headers)
        return response
    resps = [get_user(u) for u in ['baan', 'basi']]
    assert (resps[0].json()['username'] != resps[1].json())

def test_token(client:TestClient, login_data):
    token_req = client.post("/authorize/openbis/token/", data=login_data("openbis"))
    token = token_req.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/authorize/openbis/me/", headers=headers)
    assert (response.status_code == 200) & (response.json()['username'] == login_data("openbis")['username'])

def test_list_files(client, token, temp_files):
    resp = client.get("/datasets/", headers=token("ldap"))
    files = resp.json()
    assert files['files'][0]['path'] == temp_files.name


def test_post_file(client, token):
    with  tf.NamedTemporaryFile() as temp_file:
        temp_file.write(os.urandom(1024))
        resp = client.post(f"/datasets/", headers=token("ldap"), files={'file': (temp_file.name, temp_file, "application/octet-stream")})
        fn = pl.Path(temp_file.name)
    find_query = client.get(f"/datasets/find/?pattern={fn.name}", headers=token("ldap"))
    pytest.set_trace()


def test_openbis(client, token):
    resp = client.get(f"/openbis/tree/", headers=token("openbis", "baan"))
    pytest.set_trace()