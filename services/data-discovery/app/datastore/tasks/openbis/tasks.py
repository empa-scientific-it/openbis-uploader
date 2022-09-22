from typing import Callable
import celery
from celery.utils.log import get_logger
logger = get_logger(__name__)
from celery import current_app

@current_app.task(name='re', serializer='pickle', bind=True)
def process(openbis_token: str, run: Callable):
    print(f'Processing with {openbis_token} done')
    print('vaadadsaddfsdddaddfddasaddcocdde')

@current_app.task(name='zulo.task', serializer='pickle', bind=True)
def trocess(args, openbis_token: str, run: Callable):
    logger.error(f'Processing with {openbis_token} asddsdfa')

print("Trickdf Dfddddfddfdsdeddddddeddfdffddcoddneddddo")