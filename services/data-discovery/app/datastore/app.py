
from fastapi import FastAPI, File, UploadFile, Depends
from datastore.routers import data, login, openbis
from datastore.utils import settings

import argparse as ap
import pathlib as pl
import aiofiles

import os
from datastore.services.ldap import session


"""
To configure the app, edit `.env` in the main directory
"""


def create_app():
    """
    Factory function to create a new fastapi app
    """
    
    #Create settings
    app = FastAPI()
    app.include_router(login.router)
    app.include_router(data.router)
    app.include_router(openbis.router)
    return app
