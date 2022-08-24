from fastapi import APIRouter

from fastapi import FastAPI, File, UploadFile, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datastore.utils import files, settings
from datastore.models import datasets
from datastore.services.ldap import auth, ldap, session

import argparse as ap
import pathlib as pl
import aiofiles

import os
from datastore.services.ldap import session
from datastore.routers.login import get_user, oauth2_scheme, cred_store

router = APIRouter(prefix="/datasets")

async def get_ldap_user(token: str = Depends(oauth2_scheme)) -> ldap.LdapUser:
    return get_user("ldap")(token)

#user_getter: ldap.LdapUser = Depends(ldap_user_getter), token: str = Depends(oauth2_scheme)
async def get_user_instance(user: ldap.LdapUser = Depends(get_ldap_user)) -> files.InstanceDataStore:
    """
    Given an user info (as :obj:`ldap.User`) returns
    the instance data store for that particular user
    """
    set = settings.get_settings()
    return files.InstanceDataStore(set.base_path, user.group)


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
    return {"files": info}


@router.post("/")
async def upload_file(file: UploadFile, inst: files.InstanceDataStore = Depends(get_user_instance)) -> None:
    """
    Upload a new file to the instance
    """
    out_path = inst.path / pl.Path(file.filename).name
    import pytest; pytest.set_trace()
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
async def delete_file(instance: str, name: str) -> None:
    """
    Delete a file by name
    """
    inst = ds.get_instance(instance)
    os_file = inst.path / name
    try:
        os_file.unlink(missing_ok=False)
    except FileNotFoundError as e:
        return {"message": f"File {os_file} does not exist"}

    