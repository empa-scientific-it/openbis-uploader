from datastore.utils.redis import get_redis
from datastore.models import openbis as openbis_models
import pathlib as pl
from typing import Any, List, Dict
from pybis import Openbis
from datastore.services.parsers import interfaces as parser_interfaces
from rq import get_current_job
from logging import getLogger
import time
logger = getLogger(__name__)


def process(ob: Openbis, data: pl.Path | List[pl.Path], identifier: str, type: str, parser: parser_interfaces.OpenbisDatasetParser, parser_args: List[Any] | None = [], parser_kwargs: Dict[str, Any] | None = {}):
    match type:
        case "COLLECTION" | "EXPERIMENT":
            nd = ob.new_dataset(type='RAW_DATA', experiment=identifier, files=data)
        case "OBJECT" | "SAMPLE":
            nd = ob.new_dataset(type='RAW_DATA', sample=identifier, files=data)
        case _:
            raise ValueError("Can only process object or collection")
    #Get the back channel
    redis = get_redis()
    logger.info(redis)
    job_id = get_current_job(connection=redis).id
    for i in range(1000):
        #logger.info('Working')
        redis.publish(job_id, 'started')
        time.sleep(2)
        redis.publish(job_id, 'finished')
    #parser.run(ob, nd, *parser_args, **parser_kwargs)

    return

