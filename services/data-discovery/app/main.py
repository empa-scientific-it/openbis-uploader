from inspect import ArgSpec
from typing import Callable
from fastapi import FastAPI, File, UploadFile, Depends
from datastore.utils import files, settings
from datastore.models import datasets
from datastore.services.ldap import auth, ldap, session


import uvicorn
import argparse as ap
import pathlib as pl
import aiofiles

import os
from datastore.services.ldap import session

from datastore.routers import login

def serve(app: FastAPI, host:str = '0.0.0.0', port: int = 8080):
    """Serve the API using uvicorn."""
    uvicorn.run(app, host=host, port=port)

"""
To configure the app, edit `.env` in the main directory
"""

app = FastAPI()
app.include_router(login.router)



#Serve the app
serve(app)


