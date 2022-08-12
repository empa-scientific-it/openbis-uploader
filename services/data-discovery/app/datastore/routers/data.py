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


router = APIRouter()


@router.get("/datasets/find/")
async def find_file(pattern: str, recent: float = float('inf'), conn: str = Depends(auth.authenticate)):
    """
    Find all datasets in instance `instance` with
    the pattern `pattern`
    :param instance: a DataStore instance
    :params pattern: a glob pattern
    :params recent: the last modified duration
    """
    inst = files.InstanceDataStore.create(settings.base_path, instance)
    fs = inst.list_files(pattern)
    if recent:
        fs_filt = [f for f in fs if files.get_modification_delay(f) < recent]
    else:
        fs_filt = fs
    info = [datasets.FileInfo.from_path(f).dict() for f in fs_filt]
    return {"files": info}

@router.get("/{instance}/datasets/")
async def list_files(instance: str):
    """
    Find all datasets in instance`
    :param instance: the name of a DataStore instance
    """
    inst = ds.get_instance(instance)
    fs = inst.list_files("*")
    info = [datasets.FileInfo.from_path(f).dict() for f in fs]
    return {"files": info}


@router.post("/{instance}/datasets/")
async def upload_file(instance: str, name: str, file: UploadFile) -> None:
    """
    Upload a new file to the instance
    """
    inst = ds.get_instance(instance)
    out_path = inst.path / name
    try:
        contents = await file.read()
        async with aiofiles.open(out_path, 'wb') as f:
            await f.write(contents)
    except Exception:
        return {"message": "There was an error uploading the file"}
    finally:
        await file.close()

    return {"message": f"Successfuly uploaded {file.filename}"}

@router.delete("/{instance}/datasets/")
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

    