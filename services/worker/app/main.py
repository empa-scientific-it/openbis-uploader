import logging
from pickle import OBJ
from shutil import ExecError
from smtpd import DebuggingServer
from xml.dom import WrongDocumentErr
from celery import Celery, Task
import settings
import utils
#import argparse
from typing import Callable, List, Any
from celery.apps import worker
from celery.utils.log import get_logger
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent, FileModifiedEvent, FileCreatedEvent, FileClosedEvent
import pathlib as pl
from multiprocessing import Process
import datetime as dt
import time
from logging import getLogger
import importlib
logger = getLogger()
logger.setLevel(logging.INFO)
import inspect
class ModuleReloadHandler(FileSystemEventHandler):

    def __init__(self, worker: worker.Worker, app: Celery) -> None:
        self.worker = worker
        self.app = app
        self.last_modified = dt.datetime.now()

    def on_any_event(self, event: FileSystemEvent):
        logger.error(event)
        match event:
            case  FileCreatedEvent() | FileModifiedEvent():
                #self.process.terminate()
                full_path = pl.Path(event.src_path)
                module = f"{full_path.parent.parent.stem}.{full_path.parent.stem}.{full_path.stem}"
                logger.error(module)
                
                try:
                    m = importlib.import_module(module)
                    importlib.reload(m)
                    logger.error(f"Loaded {m}")
                    #self.app.autodiscover_tasks(packages=[m.__package__], force=True)
                    for r in dir(m):

                        try:
                            obj = m.__dict__[r]
                            logger.error(type(obj))
                            logger.error(inspect.signature(obj))
                            match obj:
                                case _:
                                    try:
                                        #tsk = self.app.register_task(obj())
                                        tsk = self.app.register_task(obj())
                                        logger.error(tsk)
                                        #self.worker.reload()
                                    except Exception as e:
                                        logger.error(str(e))
                        except Exception as e:
                            logger.error(str(e))
                    # self.app.close()
                    # app = create_app([])
                    # current_worker = worker.Worker(app)
                    # proc = Process(target=current_worker.start)
                    # proc.start()
                    # self.process = proc
                    # self.app = app
                    # logger.error(self.process)
                    # logger.error(m.__package__)
                    logger.error(self.app.tasks)
                    return 
                except Exception as e:
                    logger.error(str(e))
                # #try:
                # full_path = pl.Path(event.src_path)
                # module = f"{full_path.parent.parent.stem}"
                # modified = (dt.datetime.now() - self.last_modified)
                # logger.error(modified)
                # self.last_modified = dt.datetime.now()
                # if modified.total_seconds() < 2:
                #     return
                # else:                       
                #     logger.error(f'Reloading: {module}')
                #     tsk = self.app.autodiscover_tasks(packages=[module], force=True)
                #     importlib.import_module(module, full_path.parent.parent.stem)
                #     logger.error(self.app.tasks)
                # # except Exception as e:
                # #         logger.error(str(e))
                # #         logger.error("Module contains errors")
                # # try:
                # #     logger.error("closing process")
                # #     self.process.terminate()
                # #     self.app.close()
                # #     app = create_app([])
                # #     tsk = app.autodiscover_tasks(packages=[module], force=True)
                # #     logger.error("Closed process")
                # #     current_worker = worker.Worker(app)
                # #     proc = Process(target=current_worker.start)
                # #     proc.start()
                # #     self.process = proc
                # #     self.app = app
                # #     logger.error(app.tasks)
                # # except Exception as e:
                # #     logger.error(str(e))
            case _:
                pass



def get_task_package() -> pl.Path:
    return pl.Path(__file__).parent / 'tasks'

def create_app(args: List[Any]) -> Celery:
    config = settings.get_settings()
    url = utils.make_redis_url(config.redis_url, config.redis_port, config.redis_password)
    results = f"{url}/0"
    app = Celery('worker', broker=url, result_backend=results, task_serializer=config.task_serialiser, accept_content=config.accept_content)
    logger.error('Finding tasks')
    app.autodiscover_tasks(packages=['tasks.openbis'], force=True)
    return app


    

if __name__ == '__main__':

    logger.error('Finding tasks')
    app = create_app([])
    current_worker = worker.Worker(app)
    observer = Observer()
    # proc = Process(target=current_worker.start)
    #logger.error(f"Left {proc.ident}")
    #proc.start()
    handler = ModuleReloadHandler(current_worker, app)
    observer.schedule(handler, get_task_package(), recursive=True)
    observer.start()
    current_worker.start()
    #logger.error(f"Runing in {proc.ident}")
    logger.error(f"Staterd file watcher")
    logger.error(f"Staterd app")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    finally:
        current_worker.stop()
        observer.stop()
    observer.join()
    
    




    
