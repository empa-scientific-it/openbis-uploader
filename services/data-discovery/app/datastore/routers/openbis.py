from fastapi import APIRouter, Depends
from datastore.routers.login import get_openbis, get_user
from datastore.services.openbis import OpenbisUser
import pytest
from pybis import Openbis

ob = Openbis("httpsasafs")
ob.login()

router = APIRouter(prefix="/openbis")

@router.get("/tree/")
async def get_tree(ob: Openbis = Depends(get_openbis)):
    pytest.set_trace()
    ob.get_spaces