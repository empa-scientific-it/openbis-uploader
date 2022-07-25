from inspect import ArgSpec
from typing import Callable
from fastapi import FastAPI
from datastore.utils import files, settings
import uvicorn
import argparse as ap
import pathlib as pl

def serve(app: FastAPI):
    """Serve the web application."""
    uvicorn.run(app)

#Create command line parser
parser = ap.ArgumentParser()

parser.add_argument("config", type=pl.Path, help='Path to configuration file')

args = parser.parse_args()

app = FastAPI()

#Create a datastore instance


ds = files.DataStore.from_yaml(args.config)
#Define the API methods

@app.get("/create/{instance}/")
async def create_instance():
    pass

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
    info = [files.FileHelper(f).to_dict() for f in fs_filt]
    return {"files": info}





serve(app)



