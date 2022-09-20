from fastapi import APIRouter, Depends, HTTPException
from datastore.routers.login import get_openbis, get_user 
from datastore.services.openbis import OpenbisUser
import pytest
from pybis import Openbis

from instance_creator.models import OpenbisTreeObject, OpenbisProject, OpenbisSample, OpenbisCollection, OpenbisInstance, OpenbisSpace
import instance_creator.views as ic_views
from instance_creator.views import OpenbisHierarcy

import functools

router = APIRouter(prefix="/openbis")
OpenbisTreeObject.update_forward_refs()

@router.get("/tree", response_model=ic_views.TreeElement)
async def get_tree(ob: Openbis = Depends(get_openbis)):
    return ic_views.build_sample_tree_from_list(ob)
    
@router.get('/dataset_types')
async def get_dataset_types(ob: Openbis = Depends(get_openbis)):
    return ob.get_dataset_types().df.permId.to_list()


@router.get('/', response_model=OpenbisTreeObject)
async def get_object_info(identifier: str, type: OpenbisHierarcy, ob: Openbis = Depends(get_openbis)) -> OpenbisTreeObject:
    match type:
        case OpenbisHierarcy.PROJECT:
            return OpenbisProject.from_openbis(ob, identifier)
        case OpenbisHierarcy.COLLECTION:
            return OpenbisCollection.from_openbis(ob, identifier)
        case OpenbisHierarcy.SAMPLE:
            return OpenbisSample.from_openbis(ob, identifier)
        case OpenbisHierarcy.SPACE:
            return OpenbisSpace.from_openbis(ob, identifier)
        case OpenbisHierarcy.INSTANCE:
            return OpenbisInstance.from_openbis(ob, identifier)

@functools.lru_cache
def get_tree(ob: Openbis) -> ic_views.TreeElement:
    return ic_views.build_sample_tree_from_list(ob)

@router.delete('/')
async def delete(identifier: str, ob: Openbis = Depends(get_openbis)):
    obj = get_tree(ob).find(identifier)
    getters = {
        'SPACE': ob.get_space,
        'OBJECT': ob.get_object,
        'PROJECT': ob.get_project
    }
    if obj:
        try:
            ob_obj = getters[obj.type.value](identifier)
            ob_obj.delete("User requested")
        except Exception as e:
            raise HTTPException(401, detail=e)
    else:
        raise HTTPException(401, detail=f'No object with identifier {identifier}')