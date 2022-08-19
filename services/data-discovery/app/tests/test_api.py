
import pathlib as pl
import tempfile as tf
import sys
from fastapi import FastAPI
from fastapi.testclient import TestClient
from datastore.routers import login, data
from datastore.utils import settings
from datastore.utils import files

from typing import Dict, Any
import pytest

import tempfile as tf

@pytest.fixture
def client() -> TestClient:
    app = FastAPI()
    app.include_router(login.router)
    app.include_router(data.router)
    client = TestClient(app)
    return client

@pytest.fixture
def login_data() -> Dict[str, str]:
    return dict(username = "basi", password="password")

@pytest.fixture
def token(client, login_data) -> Dict[Any, Any]:
    response = client.post("/login/", data=login_data)
    tok = response.json()
    token = tok['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    return headers

@pytest.fixture
def temp_files(client, token):
    app_settings = settings.get_settings()
    response = client.get("/login/me/", headers=token)
    print(response.json())
    ds = files.InstanceDataStore(app_settings.base_path, response.json()['group'])
    cf = tf.NamedTemporaryFile(dir = ds.path)
    yield cf
    cf.close()
 
def test_auth_fail(client):
    response = client.post("/login/")
    assert response.status_code == 422

def test_auth_success(client, login_data):
    response = client.post("/login/", data=login_data)
    tok = response.json()
    assert response.status_code == 200 

def test_token(client, login_data):
    token_req = client.post("/login/", data=login_data)
    token = token_req.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/login/me", headers=headers)
    assert (response.status_code == 200) & (response.json()['username'] == login_data['username'])

def test_fake_token(client):
    headers = {"Authorization": f"Bearer sadddsfwef"}
    response = client.get("/login/me", headers=headers)
    assert response.status_code == 401


def test_list_files(client, token, temp_files):
    resp = client.get("/datasets/", headers=token)
    files = resp.json()
    assert files['files'][0]['path'] == temp_files.name
