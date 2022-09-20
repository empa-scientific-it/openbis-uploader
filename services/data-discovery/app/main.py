from fastapi import FastAPI, File, UploadFile, Depends

import uvicorn
import argparse as ap
from fastapi.logger import logger

from datastore.routers import login

from datastore.app import create_app

import pathlib as pl

def serve(app: FastAPI, host:str = '0.0.0.0', port: int = 8080, log_config: str = './uvicorn_log.yml'):
    """Serve the API using uvicorn."""
    uvicorn.run(app, host=host, port=port, log_config=log_config)

"""
To configure the app, edit `.env` in the main directory
"""


parser = ap.ArgumentParser(description="Run data discovery backedn servrice")
parser.add_argument("--host", type=str, help='Host to run the app on', default='0.0.0.0')
parser.add_argument("--port", type=int, help='Port to run the app on', default=8080)
parser.add_argument("--log-config", type=str, help='Port to run the app on', default='./uvicorn_log.yml')
args = parser.parse_args()


#Create app
app = create_app()



#Serve the app
serve(app, args.host, args.port, args.log_config)


