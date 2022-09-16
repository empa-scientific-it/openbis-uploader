from fastapi import APIRouter, Depends, HTTPException
from datastore.routers.login import get_openbis, get_user 
from datastore.services.openbis import OpenbisUser, get_user_instance
import pytest
from pybis import Openbis

from instance_creator.models import OpenbisTreeObject, OpenbisProject, OpenbisSample, OpenbisCollection
from instance_creator.views import OpenbisHierarcy, TreeElement

router = APIRouter(prefix="/openbis")
OpenbisTreeObject.update_forward_refs()

@router.get("/tree", response_model=TreeElement)
async def get_tree(ob: Openbis = Depends(get_openbis)):
    return views.build_sample_tree_from_list(ob)
    
@router.get('/dataset_types')
async def get_dataset_types(ob: Openbis = Depends(get_openbis)):
    return ob.get_dataset_types().df.permId.to_list()


@router.get('/info', response_model=OpenbisTreeObject)
async def get_object_info(identifier: str, type: OpenbisHierarcy, ob: Openbis = Depends(get_openbis)) -> OpenbisTreeObject:
    match type:
        case OpenbisHierarcy.PROJECT:
            return OpenbisProject.from_openbis(ob, identifier)
        case OpenbisHierarcy.COLLECTION:
            return OpenbisCollection.from_openbis(ob, identifier)
        case OpenbisHierarcy.SAMPLE:
            return OpenbisSample.from_openbis(ob, identifier)
        case _:
            raise HTTPException(401, detail="Not implemented yes")