from difflib import restore
from datastore.services.parsers.interfaces import OpenbisDatasetParser
from abc import ABC, abstractmethod
from pybis import Openbis 
from pybis.openbis_object import Transaction
from pybis.dataset import DataSet
import pydantic
from pydantic import create_model, BaseModel
from pydantic.main import ModelMetaclass
import zipfile 
import tempfile
import pathlib as pl

from typing import List
import pandas as pd
        
def match_files(zf: zipfile.ZipFile, name: str) -> List[str]:
    return [f for f in zf.namelist() if pl.Path(f).name == name]



class ICPMsParser(OpenbisDatasetParser):
    encoding= 'iso-8859-1'

    def process(self, ob: Openbis, transaction: Transaction, dataset: DataSet, a: str) -> Transaction:
        #Load file
        with zipfile.ZipFile(dataset.file_list[0], 'r') as zf,  tempfile.TemporaryDirectory() as td:
            batch_log, *rest = match_files(zf, "BatchLog.csv")
            if batch_log:
                batch_log_path = zf.extract(batch_log, path=td)
                pd.read_csv(batch_log_path, encoding='iso-8859-1')

