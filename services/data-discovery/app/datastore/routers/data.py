from urllib.error import HTTPError
from xml.dom.minidom import Entity
from fastapi import APIRouter

from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, Body, BackgroundTasks, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datastore.utils.redis import get_redis
from datastore.utils import files, settings
from datastore.models import datasets
from datastore.services.ldap import auth, ldap, session
from pybis import Openbis
import argparse as ap
import pathlib as pl
import aiofiles

from typing import Dict, List

from datastore.services.ldap import session
from datastore.services import openbis as openbis_service
from datastore.services import auth as auth_service
from datastore.routers.login import get_user, oauth2_scheme, get_credential_context, get_resource_serves, get_credential_store
from datastore.routers.openbis import  get_openbis
from datastore.services.parsers.interfaces import OpenbisDatasetParser
from datastore.services.parsers import icp_ms

import datastore.services.parsers.helpers as parser_helper
from instance_creator.views import OpenbisHierarcy
from datastore.models.parser import ParserParameters, ParserProcess
from fastapi.concurrency import run_in_threadpool
from fastapi import WebSocket

import logging

from instance_creator.views import OpenbisHierarcy


from datastore.models import openbis as openbis_models

from datastore.utils import rq as rq_utils

from datastore.tasks import openbis as ob_tasks

import asyncio 


from redis import Redis

from rq import Queue
LOGGER = logging.getLogger(__name__)

router = APIRouter(prefix="/datasets")

async def get_ldap_user(token: str = Depends(oauth2_scheme), store: auth_service.CredentialsStore = Depends(get_credential_store), resource_server: Dict[str, auth_service.ResourceServer] = Depends(get_resource_serves)) -> ldap.LdapUser:
    """
    Given a token (as a dependence),
    return a LdapUser object containing the user information
    """
    return get_user("ldap", store, resource_server)(token)

async def get_user_instance(user: ldap.LdapUser = Depends(get_ldap_user)) -> files.InstanceDataStore:
    """
    Given an user info (as :obj:`ldap.User`) returns
    the instance data store for that particular user
    """
    set = settings.get_settings()
    group = ldap.decompose_dn(user.group[0])[set.ldap_group_attribute]
    ds = files.InstanceDataStore(set.base_path, group)
    #Attach parser
    ds.register_parser('icp_ms', icp_ms.ICPMsParser)
    return ds




@router.get("/find")
async def find_file(pattern: str, recent: float = float('inf'), inst: files.InstanceDataStore = Depends(get_user_instance)):
    """
    Find all datasets in instance `instance` with
    the pattern `pattern`
    :param instance: a DataStore instance
    :params pattern: a glob pattern
    :params recent: the last modified duration
    """
    fs = inst.list_files(pattern)
    if recent:
        fs_filt = [f for f in fs if files.get_modification_delay(f) < recent]
    else:
        fs_filt = fs
    info = [datasets.FileInfo.from_path(f).dict() for f in fs_filt]
    return {"files": info}

@router.get("/")
async def list_files(inst: files.InstanceDataStore = Depends(get_user_instance)):
    """
    Find all datasets in instance`
    :param user_info: user information
    """
    fs = inst.list_files("*")
    info = [datasets.FileInfo.from_path(f).dict() for f in fs]
    print(inst)
    print(info)
    return {"files": info}


@router.post("/")
async def upload_file(file: UploadFile, inst: files.InstanceDataStore = Depends(get_user_instance)) -> Dict:
    """
    Upload a new file to the instance
    """
    out_path = inst.path / pl.Path(file.filename).name
    try:
        contents = await file.read()
        async with aiofiles.open(out_path, 'wb') as f:
            await f.write(contents)
    except Exception:
        return {"message": "There was an error uploading the file"}
    finally:
        await file.close()
    return {"message": f"Successfuly uploaded {file.filename} to {out_path}"}

@router.delete("/")
async def delete_file(instance: str, name: str) -> Dict:
    """
    Delete a file by name
    """
    inst = ds.get_instance(instance)
    os_file = inst.path / name
    try:
        os_file.unlink(missing_ok=False)
    except FileNotFoundError as e:
        return {"message": f"File {os_file} does not exist"}

@router.get("/parsers")
async def get_registered_dataset_parsers(inst: files.InstanceDataStore = Depends(get_user_instance)) -> List[str]:
    """
    Gets the list of all registered dataset parsers
    """
    if len(inst.parsers) > 0:
        prs = [pr for pr in inst.parsers.keys()]
        return prs
    else:
        raise HTTPException(204)

@router.get("/parser_info", response_model=Dict)
async def get_parser_parameters(parser: str, inst: files.InstanceDataStore = Depends(get_user_instance)) -> Dict:
    """
    Gets the schema for the parameters for the choosen parser
    """
    if len(inst.parsers) > 0:
        parser_model = inst.parsers[parser]()._generate_basemodel()
        return parser_model.schema()
    else:
        raise HTTPException(204)



@router.put("/transfer", status_code=status.HTTP_202_ACCEPTED, response_model=ParserProcess)
def transfer_file(params: ParserParameters, background_tasks: BackgroundTasks, user: ldap.LdapUser = Depends(get_ldap_user), queue: Queue = Depends(rq_utils.get_queue), inst: files.InstanceDataStore = Depends(get_user_instance), ob: Openbis = Depends(get_openbis), jobs: parser_helper.ProcessingJobRegistry = Depends(parser_helper.get_registry)):
    """
    Transfers a file from the datastore
    to the openbis server by using one of
    the registed dataset extraction scripts.
    The processing happens on an external worker using rq. Returns a task
    id which can be used to moinitor the task
    """
    #Get files

    try:
        files_to_attach = inst.get_file(params.source)
    except FileNotFoundError:
        raise HTTPException(401, detail="The file {params.source} cannot be found")
    #Get the parser
    current_parser = inst.parsers[params.parser]()
    ob_m = openbis_models.OpenbisConnection.from_ob(ob)
    job = rq_utils.create_job(queue.connection, user, ob_tasks.process,[ob, files_to_attach, params.identifier, params.type.value,   current_parser, params.function_parameters], timeout=36000)
    enqueued_job = queue.enqueue_job(job)
    return {'taskid': job.id}
    # if ob.is_session_active():
    #     pass
    # else:
    #     raise HTTPException(401, detail="Openbis section not active")
    
    # match params.type:
    #     case OpenbisHierarcy.COLLECTION:
    #         loader = lambda files, type: ob.new_dataset(experiment = params.identifier, type = type, file = files)
    #     case OpenbisHierarcy.OBJECT:
    #         loader = lambda files, type: ob.new_dataset(sample = params.identifier, type = type, file = files)
    #     case _:
    #         raise HTTPException(401, detail='Specify a sample or a collection to attach an object to')
    # try:
    #     current_parser = inst.parsers[params.parser]()
    #     nd = loader(str(files_to_attach[0]), params.dataset_type)
    #     nd.kind = 'PHYSICAL'
    #     trans = ob.new_transaction()
    #     task_state = ParserProcess(status=parser_helper.ProcessState.IN_PROGRESS)
    #     jobs.append_job(task_state)
    #     background_tasks.add_task(current_parser.process, ob, trans, nd, **params.function_parameters)
    #     LOGGER.info('dfone')
    #     #trans = await run_in_threadpool(lambda: current_parser.process(ob, ))
    #     #trans.commit()
    #     return {"task_id": task_state.uid}
    # except Exception as e:
    #     LOGGER.error(str(e))
    #     raise HTTPException(401, detail=str(e))

