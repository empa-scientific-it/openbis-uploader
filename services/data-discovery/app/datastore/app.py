
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


"""
To configure the app, edit `.env` in the main directory
"""



#Create settings
app = FastAPI()
settings = settings.get_settings()

#Define the API methods


@app.get("/")
def root(username: str = Depends(auth.authenticate)):
    """
    Root page
    """
    return {"message": f"Welcome {username}"}


