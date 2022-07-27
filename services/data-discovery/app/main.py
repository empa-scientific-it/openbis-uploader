from inspect import ArgSpec
from typing import Callable
from fastapi import FastAPI, File, UploadFile
from datastore.utils import files, settings
from datastore.models import datasets
import uvicorn
import argparse as ap
import pathlib as pl
import aiofiles

import os

def serve(app: FastAPI, host:str = '127.0.0.0', port: int = '8080'):
    """Serve the API using uvicorn."""
    uvicorn.run(app, host=host, port=port)

#Create command line parser
parser = ap.ArgumentParser()

parser.add_argument("config", type=pl.Path, help='Path to configuration file')
parser.add_argument("--host", type=str, help='Optional host IP address', default="0.0.0.0")
parser.add_argument("--port", type=int, help='Optional host port address', default=8080)


args = parser.parse_args()

app = FastAPI()

#Create a datastore instance
ds = files.DataStore.from_yaml(args.config)
#Define the API methods

@app.get("/create/{instance}/")
async def create_instance(instance: str):
    """
    Creates a new instance given its name. This will create
    a new directory in the `base_path` of the Datastore
    :param instance: the name of the new instance to create
    """
    ds.add_instance(instance)

@app.get("/{instance}/datasets/find/")
async def find_file(instance: str, pattern: str, recent: float = float('inf')):
    """
    Find all datasets in instance `instance` with
    the pattern `pattern`
    :param instance: a DataStore instance
    :params pattern: a glob pattern
    :params recent: the last modified duration
    """
    inst = ds.get_instance(instance)
    fs = inst.list_files(pattern)
    if recent:
        fs_filt = [f for f in fs if files.get_modification_delay(f) < recent]
    else:
        fs_filt = fs
    info = [datasets.FileInfo.from_path(f).dict() for f in fs_filt]
    return {"files": info}

@app.get("/{instance}/datasets/")
async def list_files(instance: str):
    """
    Find all datasets in instance`
    :param instance: the name of a DataStore instance
    """
    inst = ds.get_instance(instance)
    fs = inst.list_files("*")
    info = [datasets.FileInfo.from_path(f).dict() for f in fs]
    return {"files": info}


@app.post("/{instance}/datasets/")
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

@app.delete("/{instance}/datasets/")
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

serve(app, port=args.port, host=args.host)



