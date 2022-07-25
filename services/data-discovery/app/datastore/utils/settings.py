import pydantic
from pydantic import BaseSettings
import pathlib as pl
from typing import List

class DataStoreSettings(BaseSettings):
    """
    Class to represent the settings of the datastore
    """
    base_path: pl.Path = pl.Path('/usr/stores/') 
    instances: List[str] | None = None
