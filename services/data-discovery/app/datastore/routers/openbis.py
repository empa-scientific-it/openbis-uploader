from fastapi import APIRouter, Depends
from datastore.routers.login import get_openbis, get_user 
from datastore.services.openbis import OpenbisUser, get_user_instance
import pytest
from pybis import Openbis

from instance_creator import views

router = APIRouter(prefix="/openbis")

@router.get("/tree", response_model=views.TreeElement)
async def get_tree(ob: Openbis = Depends(get_openbis)):
    return views.build_sample_tree(ob)
    