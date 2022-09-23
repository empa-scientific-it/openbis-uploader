
import pathlib as pl
from platform import python_revision
import tempfile as tf
import sys
from fastapi import FastAPI
from fastapi.testclient import TestClient
from datastore.routers import login, data, openbis, tasks
from datastore.utils import settings, redis as redis_utils, rq as rq_utils
from datastore.utils import files
from datastore.services.ldap import ldap
from datastore.services.parsers.interfaces import OpenbisDatasetParser
import os
from typing import Callable, Dict, Any, Type, Generator
import pytest

from pybis import Openbis
from pybis.openbis_object import Transaction
from pybis.dataset import DataSet

import inspect

import tempfile as tf

import textwrap

from datastore.app import create_app

from rq import SimpleWorker, Queue, Worker
from multiprocessing import Process

@pytest.fixture
def client() -> TestClient:
    app = create_app()
    client = TestClient(app)
    return client


def temp_settings(base_path: pl.Path):
    class TempSettings(settings.DataStoreSettings):
        class Config:
            env_file = pl.Path(__file__) / pl.Path('.env')
    return TempSettings


@pytest.fixture
def temp_client() -> Callable:
    def _inner(path: pl.Path)  -> TestClient:
        app = FastAPI()
        app.include_router(login.router)
        app.include_router(data.router)
        app.include_router(openbis.router)
        app.include_router(tasks.router)
        app.dependency_overrides[settings.get_settings] = temp_settings(path)
        client = TestClient(app)
        return client
    return _inner


@pytest.fixture
def login_data() -> Dict[str, str]:
    def _inner(service:str, user:str = 'basi'):
        creds = {
            'ldap':[dict(username = "basi", password="password"), dict(username='baan', password="password")],
            'all':[dict(username = "basi", password="password"), dict(username='baan', password="password")],
            'openbis':[dict(username = "basi", password="password"), dict(username='baan', password="password"), dict(username='admin', password='changeit')]
        }
        return [c for c in creds[service] if c['username'] == user][0]
    return _inner

@pytest.fixture
def token(client, login_data) -> Dict[Any, Any]:
    def _inner(service:str, user: str = "basi"):
        response = client.post(f"/authorize/{service}/token", data=login_data(service, user))
        tok = response.json()
        token = tok['access_token']
        headers = {"Authorization": f"Bearer {token}"}
        return headers
    return _inner

@pytest.fixture
def temp_files(client, token):
    app_settings = settings.get_settings()
    response = client.get("/authorize/ldap/me", headers=token("ldap"))
    import pytest; pytest.set_trace()
    groups = ldap.decompose_dn(response.json()['group'][0])[app_settings.ldap_group_attribute]
    ds = files.InstanceDataStore(app_settings.base_path, groups)
    cf = tf.NamedTemporaryFile(dir = ds.path)
    yield cf
    cf.close()


@pytest.fixture
def temp_worker():
    con = redis_utils.get_redis()
    queue = Queue(connection=con)
    worker = Worker([queue], connection = con )
    proc = Process(target = worker.work, kwargs=dict(burst=True))
    proc.start()
    print('started')
    return proc

def test_auth_fail(client):
    response = client.post("/authorize/ldap/token")
    assert response.status_code == 422

def test_ldap_auth_success(client, login_data):
    response = client.post("/authorize/ldap/token", data=login_data("ldap"))
    tok = response.json()
    assert response.status_code == 200 

def test_openbis_auth_success(client, login_data):
    response = client.post("/authorize/openbis/token", data=login_data("openbis"))
    tok = response.json()
    assert response.status_code == 200

def test_multiple_auth(client, login_data):
    """
    Check if the different user get different tokens
    """
    def get_user(un: str):
        token_req = client.post("/authorize/openbis/token", data=login_data("openbis", un))
        token = token_req.json()['access_token']
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/authorize/openbis/me", headers=headers)
        return response
    resps = [get_user(u) for u in ['baan', 'basi']]
    assert (resps[0].json()['username'] != resps[1].json())


def test_invalidation(client:TestClient, login_data):
    token_req = client.post("/authorize/openbis/token", data=login_data("openbis"))
    token = token_req.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    invalid = client.get("/authorize/openbis/logout", headers=headers)
    should_fail = client.get("/authorize/openbis/me", headers=headers)
    assert should_fail.status_code == 401

   

def test_token(client:TestClient, login_data):
    token_req = client.post("/authorize/openbis/token", data=login_data("openbis"))
    token = token_req.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/authorize/openbis/me", headers=headers)
    assert (response.status_code == 200) & (response.json()['username'] == login_data("openbis")['username'])


def test_get_ldap_groups(client, token):
    resp = client.get("/authorize/ldap/me", headers=token("ldap"))
    assert resp.json()['group'][0] == 'cn=700,ou=users,dc=empa,dc=ch'



def test_login_all(client: TestClient, login_data):
    token_req = client.post("/authorize/all/token", data=login_data("all"))
    token_resp = token_req.json()['access_token']
    tok = {"Authorization": f"Bearer {token_resp}"}
    resp_ob = client.get("/authorize/openbis/me", headers=tok)
    resp_ldap = client.get("/authorize/ldap/me", headers=tok)
    assert (resp_ob.status_code == 200) & (resp_ldap.status_code == 200)


def test_logout_all(client: TestClient, token):
    resp_ob = client.get("/authorize/all/logout", headers=token('all', 'basi'))
    assert (resp_ob.status_code == 200)

def test_token_validation(client: TestClient, login_data):
    token_req = client.post("/authorize/all/token", data=login_data("all"))
    token_resp = token_req.json()['access_token']
    tok = {"Authorization": f"Bearer {token_resp}"}
    params = {'token': token_resp}
    resp_ob = client.get("/authorize/all/check", headers=tok, params=params)
    pytest.set_trace()
    assert (resp_ob.status_code == 200) &   (resp_ob.json()['valid'])


def test_token_invalidation(client: TestClient, login_data):
    tok = f"Bearer gibberish"
    resp_ob = client.get("/authorize/all/check", params={'token':tok})
    assert (resp_ob.status_code == 200) &  (not resp_ob.json()['valid'])

def test_list_files(client, token, temp_files):
    resp = client.get("/datasets/", headers=token("ldap"))
    files = resp.json()
    assert temp_files.name in [f['path'] for f in files['files']]


def test_post_file(client, token):
    with  tf.NamedTemporaryFile() as temp_file:
        temp_file.write(os.urandom(1024))
        resp = client.post(f"/datasets/", headers=token("ldap"), files={'file': (temp_file.name, temp_file, "application/octet-stream")})
        fn = pl.Path(temp_file.name)
    find_query = client.get(f"/datasets/find/?pattern={fn.name}", headers=token("ldap"))


def test_openbis_tree(client, token):
    resp = client.get(f"/openbis/tree/", headers=token("openbis", "basi"))
    assert resp.status_code == 200

def test_openbis_info(client, token):
    for identifier, level in [('/DEMO/TEST', 'PROJECT'), ('DEMO', 'SPACE'), ('/DEMO/TEST/SAMPLES', 'COLLECTION')]:
        resp = client.get(f"/openbis/?", headers=token("openbis", "basi"), params={'identifier':identifier, 'type':level})
        assert (resp.status_code == 200) & (resp.json()['identifier'] == identifier)


def test_openbis_delete(client, token):
    resp = client.delete(f"/openbis/?", headers=token("openbis", "basi"), params={'identifier':'/DEMO/TEST/SAMP1'})
    assert resp.status_code == 200

def test_transfer(client, token):
    with  tf.NamedTemporaryFile() as temp_file:
        temp_file.write(os.urandom(1024))
        resp = client.post(f"/datasets/", headers=token("ldap"), files={'file': (temp_file.name, temp_file, "application/octet-stream")})
        fn = pl.Path(temp_file.name)
    body = {'source':fn.name, 'collection': '/MEASUREMENTS/TEST/EXP1', 'parser':'icp_ms', 'dataset_type':'RAW_DATA', 'function_parameters': {'a':1}}
    transfer_query = client.put(f"/datasets/transfer", headers=token("all"), json=body)

def test_parser_parameters(client, token):
    params = {'parser': 'icp_ms'}
    resp = client.get(f"/datasets/parser_info?", headers=token("all", "basi"), params=params)
    pytest.set_trace()

def test_icp_ms_parser(client, token, temp_worker):
    body ={"identifier":"/DEMO/TEST/SAMP33", 'type':'OBJECT',"dataset_type":"RAW_DATA","parser":"icp_ms","source":"ICP-MS RAW.zip","function_parameters":{"loader_name":"das","description":"ad"}}
    transfer_query = client.put(f"/datasets/transfer", headers=token("all"), json=body)
    temp_worker.interrupt()
    assert transfer_query.status_code == 202

def test_icp_ms_parser_logger(client, token, temp_worker):
    body ={"identifier":"/DEMO/TEST/SAMP33", 'type':'OBJECT',"dataset_type":"RAW_DATA","parser":"icp_ms","source":"ICP-MS RAW.zip","function_parameters":{"loader_name":"das","description":"ad"}}
    transfer_query = client.put(f"/datasets/transfer", headers=token("all"), json=body)
    task_id = transfer_query.json()['taskid']
    print(task_id)
    temp_worker.join()
    # import pytest; pytest.set_trace()
    # with client.websocket_connect(f"/log") as websocket:
    #     while True:
    #         data = websocket.receive_text()
    #         print(data)
    # import pytest; pytest.set_trace()

    assert data == {"msg": "Hello WebSocket"}
    
    assert transfer_query.status_code == 202


@pytest.fixture
def test_parser_class() -> Type[OpenbisDatasetParser]:
    class TestParser(OpenbisDatasetParser):
        def process(self, transaction: Transaction, ob: Openbis, dataset: DataSet, a: int, b:str, c:str = 'gala') -> Transaction:
            ob.new_object('ICP-MS-MEASUREMENT', '/MEASUREMENTS/TEST/SAMP1', {'GAS_FLOW':1.2, 'SAMPLE_ID':a})
            return transaction 
    return TestParser 

@pytest.fixture
def test_parser_file() -> pl.Path:
    return pl.Path(__file__).parent / pl.Path('test_parser.py') 

@pytest.fixture
def test_instance() -> files.InstanceDataStore:
    with tf.TemporaryDirectory() as td:
        yield files.InstanceDataStore(base = td, instance='test')
    print("done")




def test_register_parser(test_parser_class :Type[OpenbisDatasetParser] , test_instance: files.InstanceDataStore):
    test_instance.register_parser('test', test_parser_class)
    assert test_instance.parsers['test'] == test_parser_class

def test_find_parsers(test_parser_file: pl.Path, test_instance: files.InstanceDataStore):
    file_path = test_instance.parser_path / 'test.py'
    with open(file_path, 'w+') as of, open(test_parser_file, 'r') as source:
        of.writelines(source.readlines())
    parsers = test_instance.find_parsers()
    if parsers:
        [test_instance.register_parser(name, parser) for name,parser in parsers.items()]
        [parser()._generate_basemodel() for name, parser in test_instance.parsers.items()]
    


def test_run_parser(temp_client, login_data):
    with tf.TemporaryDirectory() as td:
        tc = temp_client(td)
    response = tc.post("/authorize/openbis/token", data=login_data("all"))
    tok = response.json()
    pass