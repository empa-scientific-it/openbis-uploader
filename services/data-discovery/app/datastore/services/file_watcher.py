from ast import arg
from asyncio import run, tasks
import asyncio
import pathlib as pl
from pydantic import BaseModel
from typing import Dict
import fnmatch
import random
from asyncinotify import Inotify, Mask
import tempfile as tf


class WatchingTask(BaseModel):
    path: pl.Path
    pattern: str
    function: str
    
    def match_path(self, path: pl.Path) -> bool:
        return fnmatch.fnmatch(str(path), str(self.path / self.pattern))
    
    def work(self, *args, **kwargs):
        globals()[self.function](*args, **kwargs)


class WatchersRegistry(BaseModel):

    tasks: dict[str, WatchingTask]

    def make_notify(self) -> Inotify:
        notify = Inotify()
        for name, task in self.tasks.items():
            notify.add_watch(task.path,  Mask.CLOSE_WRITE)
        return notify

    async def work(self):
        notifier = self.make_notify()
        async for event in notifier:
            current_task, *rest = [task for name, task in self.tasks.items() if event.path and task.match_path(event.path)]
            current_task.work(event.path)
            print(current_task)

    
    



async def write_temp(path: pl.Path, suffix:str, delay:bool=True):
    while True:
        with tf.NamedTemporaryFile(dir=path, suffix=suffix, mode='w+') as temp_file:
            temp_file.writelines(['a'])
        await asyncio.sleep(random.random()) 

def fun1(file: pl.Path):
    print(f'I am the first function and I received {file}')

def fun2(file: pl.Path):
    print(f'I am the second function and I received {file}')



# async def main():
#     write_tasks = [write_temp(watcher.path, '.txt') for name, watcher in watchers.tasks.items()]
#     asyncio.gather(watchers.work(), *write_tasks)

