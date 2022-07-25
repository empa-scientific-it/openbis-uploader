from fastapi import FastAPI
from datastore.utils import files, settings


app = FastAPI()

#Create a datastore


@app.get("/create/{instance}/")
async def create_instance():
    pass

@app.get("/{instance}/datasets/")
async def root():
    return {"message": "Hello World"}