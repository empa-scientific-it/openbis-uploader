"""
This module is used to manage datasets
for a specific instance of the data uploader
"""
import pathlib as pl
from pydantic.dataclasses import dataclass
from pydantic import BaseModel
from typing import Iterable, List, Optional, Dict, Union
import datetime as dt

from re import Pattern
from venv import create

from . import settings

import yaml

def get_modification_delay(f: pl.Path) -> float:
    """
    Get the time delay from the current time to the last modification
    of a given file
    :param f: the file to check
    :return the difference in minutes from the current time to the modification time
    """
    return (dt.datetime.now(dt.timezone.utc) - dt.datetime.fromtimestamp(f.stat().st_mtime, tz=dt.timezone.utc)).total_seconds() / 60

@dataclass
class InstanceDataStore:
    """
    Class to represent the datastore
    for a specific instance. This is a directory in the path :obj:`path` that contains all the 
    datasets to be upload / attached to a given openBis instance
    """
    path: pl.Path
    instance: str

    def list_files(self, pattern: str | Pattern) -> Optional[Iterable[pl.Path]]:
        """
        List all files available for the current instance with the given pattern
        :param pattern: the pattern of the file to search for
        :return a list of files or none 
        """
        match pattern:
            case str(x) as pt:
                files = self.path.glob(x)
            case Pattern(p) as pt:
                files = (f for f in self.path.iterdir() if pt.search(str(p)))
        return files
    
    def list_recent_files(self, last_changed: int = 10) -> Optional[Iterable[pl.Path]]:
        """
        List all files that changed within a specified time
        :param last_changed, the time in minute where the change should be considered
        :return a list of recently changed files
        """
        return [f for f in self.path.iterdir() if get_modification_delay(f) < last_changed]

    @classmethod
    def create(cls, base: pl.Path | str, instance: str) -> "InstanceDataStore":
        """
        Class factory to create a new datastore instance given a base path. If the path already exists, just
        returns the instance, if the path doesn't exists, the directory is created first.
        """
        match base:
            case str(x):
                base_path = pl.Path(x)
            case pl.Path() as pt:
                base_path = pt
        instance_path = (base_path / pl.Path(instance)).expanduser().resolve()
        #Check if exists
        if instance_path.exists():
            return cls(instance_path, instance) 
        else:
            instance_path.mkdir(parents=True, exist_ok=True)
            return cls(instance_path, instance) 

@dataclass
class DataStore:
    """
    Class to represent the datastore
    """
    base_path: pl.Path
    instances: Dict[str, InstanceDataStore]

    def get_instance(self, instance: str) -> Optional[InstanceDataStore]:
        """
        Get the datastore for the instance :obj:`instance` if that exists
        :param instance: the instance to select
        :return an :obj:`InstanceDataStore` if it exists, None otherwise
        """
        return self.instances.get(instance)
    
    @classmethod
    def initalise(cls, base_path: pl.Path, instances: List[str]) -> "DataStore":
        """
        Create an instance of the DataStore given the base path, using
        the contained subfolders as instance stores
        """
        instances = {i:InstanceDataStore.create(base_path, i) for i in instances}
        return cls(base_path, instances)

    @classmethod 
    def from_yaml(cls, config: pl.Path) -> "DataStore":
        """
        Create an instance of the DataStore from a yaml file
        """
        with open(config, 'r') as cfg:
            cfg_dt = yaml.load(cfg, yaml.Loader)
        config = settings.DataStoreSettings().parse_obj(cfg_dt)
        return cls.initalise(config.base_path, config.instances)

    def add_instance(self, instance: str):
        """
        Add a new instance datastore to the current datastore
        :param instance: the id of the new datastore to add
        """
        ni = InstanceDataStore.create(self.base_path, instance)
        self.instances.update({instance: ni})

