from fastapi import APIRouter, Depends
from datastore.routers.login import get_openbis, get_user 
from datastore.services.openbis import OpenbisUser, get_user_instance
import pytest
from pybis import Openbis

from instance_creator import models

router = APIRouter(prefix="/openbis")

@router.get("/tree/")
async def get_tree(ob: Openbis = Depends(get_openbis)):
    i = models.OpenbisInstance.reflect(ob)
    return [s for s in i.children if s.code != 'ELN_SETTINGS']