"""
This module is used to manage datasets
for a specific instance of the data uploader
"""
from asyncore import file_dispatcher
from dataclasses import field
from functools import reduce
import inspect
import pathlib as pl
from pydantic.dataclasses import dataclass
from pydantic import BaseModel
from typing import Iterable, List, Optional, Dict, Union, TypeVar, Type
import datetime as dt

from re import Pattern
from venv import create

from . import settings

from ..services.ldap import ldap
from ..services.parsers.interfaces import OpenbisDatasetParser


import importlib
import importlib.util

import inspect

import sys

from collections import ChainMap

def get_modification_delay(f: pl.Path) -> float:
    """
    Get the time delay from the current time to the last modification
    of a given file
    :param f: the file to check
    :return the difference in minutes from the current time to the modification time
    """
    return (dt.datetime.now(dt.timezone.utc) - dt.datetime.fromtimestamp(f.stat().st_mtime, tz=dt.timezone.utc)).total_seconds() / 60


T = TypeVar('T')
def load_classes(loc: pl.Path, which: T) -> Dict[str, T] | None:
    """
    Load all classes that are a subclass of `which`
    """
    name = str(loc.stem)
    module_spec = importlib.util.spec_from_file_location(name, str(loc))
    module = None
    if module_spec:
        module = importlib.util.module_from_spec(module_spec)
        sys.modules[name] = module
    else:
        raise FileNotFoundError("Cannot load classes in {loc}")
    if module is not None and module_spec is not None:
        if module_spec.loader is not None:
            module_spec.loader.exec_module(module)
            classes = {name: obj for name, obj in inspect.getmembers(module, predicate=inspect.isclass) if (issubclass(obj, which) and obj != which)}
            return classes
        else:
            raise FileNotFoundError("Cannot load classes in {loc}")


@dataclass
class InstanceDataStore:
    """
    Class to represent the datastore
    for a specific instance. This is a directory in the path :obj:`path` that contains all the 
    datasets to be upload / attached to a given openBis instance.
    The `parsers` attribute contains a Dictionary of :class:`OpenbisDatasetParser` subclasses that are registered
    for this instance
    """
    path: pl.Path
    instance: str
    parsers: Dict[str, Type[OpenbisDatasetParser]] = field(default_factory=lambda: dict())

    def __init__(self,  base: pl.Path | str, instance: str) -> None:
        match base:
            case str(x):
                base_path = pl.Path(x)
            case pl.Path() as pt:
                base_path = pt
        instance_path = (base_path / pl.Path(instance)).expanduser().resolve()
        self.path = instance_path
        if not self.path.exists():
            self.path.mkdir()
        if not self.parser_path.exists():
            self.parser_path.mkdir()
        self.instance = instance
        self.parsers = dict() | p if (p:= self.find_parsers()) else dict()


    @property
    def parser_path(self) -> pl.Path:
        return self.path / 'parsers'

    def resolve_path(self) -> pl.Path:
        """
        Returns the full path to the instance datastore
        """
        return (self.path).expanduser().resolve()
        
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

    def get_file(self, name: str) -> List[pl.Path]:
        """
        Finds the file with the exact name if this exists
        """
        files = [f for f in self.path.iterdir() if f.name == name]
        if len(files) == 0:
            raise FileNotFoundError(f"Cannot find the file with path {self.path / name}")
        else:
            return files
    
    def register_parser(self, name:str, new_parser: Type[OpenbisDatasetParser]):
        """
        Given a class, registers it as a  dataset parser (as long as it is a subclass of the :obj:`OpenbisDatasetParser` ABC)
        """
        if issubclass(new_parser, OpenbisDatasetParser):
            self.parsers.update({name: new_parser})
        else:
            raise TypeError(f"Class {new_parser} is not  a subclass of {OpenbisDatasetParser}")

    def find_parsers(self) -> Dict[str, Type[OpenbisDatasetParser]] | None:
        """
        Find and load alll of the dataset parsers
        """
        py_files = self.parser_path.glob("*.py")
        res = [f for f in [load_classes(file, OpenbisDatasetParser) for file in py_files] if f is not None]
        if res:
            classes_per_file = reduce(lambda x,y: x | y, res)
            return classes_per_file
            



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
        instances = {i:InstanceDataStore(base_path, i) for i in instances}
        return cls(base_path, instances)

    @classmethod 
    def get_datastore(cls) -> "DataStore":
        """
        Create an instance of the DataStore from a BaseSettings object
        """
        config = settings.DataStoreSettings()
        instances = ldap.get_groups()
        return cls.initalise(config.base_path, instances)

    def add_instance(self, instance: str):
        """
        Add a new instance datastore to the current datastore
        :param instance: the id of the new datastore to add
        """
        ni = InstanceDataStore(self.base_path, instance)
        self.instances.update({instance: ni})

