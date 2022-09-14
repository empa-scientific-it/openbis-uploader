from difflib import restore
from hmac import trans_36
from xml.sax.handler import DTDHandler
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

def clean_names(df: pd.DataFrame) -> pd.DataFrame:
    df_out = df.copy()
    return df_out.rename(lambda c: c.strip().replace(" ", "").lower().replace('-', '_').replace('.', '_'), axis="columns")  

class ICPMsParser(OpenbisDatasetParser):
    encoding= 'iso-8859-1'

    def process(self, ob: Openbis, transaction: Transaction, dataset: DataSet, a: str) -> Transaction:
        #Load file
        with zipfile.ZipFile(dataset.file_list[0], 'r') as zf,  tempfile.TemporaryDirectory() as td:
            batch_log, *rest = match_files(zf, "BatchLog.csv")
            if batch_log:
                batch_log_path = zf.extract(batch_log, path=td)
                batch_log_dt = clean_names(pd.read_csv(batch_log_path, encoding=self.encoding))
                for row in batch_log_dt.itertuples():
                    props = {'sample_id': 1, 
                    "sample_name": row.samplename, 
                    'acq_timestamp': row.acq_date_time, 
                    'sample_type': row.sampletype,
                    'acquistion_result': row.acquisitionresult,
                    'operator': row.operator}
                    sample = ob.new_object(type='ICP-MS-MEASUREMENT', code=None, project = dataset.project, props=props, experiment=dataset.experiment)
                    print("Adding sample")
                    transaction.add(sample)
        import pytest; pytest.set_trace()
        return transaction

