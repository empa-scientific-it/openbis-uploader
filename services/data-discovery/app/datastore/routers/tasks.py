from multiprocessing import connection
from fastapi import APIRouter, Depends, HTTPException, WebSocket
from datastore.utils.redis import get_redis
from datastore.routers.login import get_openbis, get_user, oauth2_scheme
from datastore.routers.data import get_user_instance
from datastore.services.openbis import OpenbisUser
from datastore.utils.rq import get_queue
import pytest
from pybis import Openbis
import async_timeout
from rq import Queue
from redis.asyncio import Redis

from typing import Dict

from instance_creator.models import OpenbisTreeObject, OpenbisProject, OpenbisSample, OpenbisCollection, OpenbisInstance, OpenbisSpace
import instance_creator.views as ic_views
from instance_creator.views import OpenbisHierarcy

import functools


import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tasks")


async def get_messages(redis: Redis, id: str):
    pubsub = redis.pubsub()
    await pubsub.subscribe(id)
    while True:
        async with async_timeout.timeout(1):
            m = await pubsub.get_message()
            if m is not None:
                yield m

@router.websocket("/tasks/log")
async def parser_status(websocket: WebSocket, id:str):
    logger.info("opened socket")
    redis = get_redis(sync=False)
    await websocket.accept()
    async for m in get_messages(redis, id):
        print(m)
        await websocket.send_text(str(m))
    await connection.close()
    await websocket.close()


@router.get("/task_list", response_model=Dict)
async def get_parser_parameters(inst: str = Depends(get_user_instance), user = Depends(get_user), queue:Queue = Depends(get_queue)) -> Dict:
    """
    Gets a list of tasks
    """