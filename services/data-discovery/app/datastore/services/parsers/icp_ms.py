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
    """
    This is the core part of the dataset metadata extractor. To implement another extra
    """
    encoding= 'iso-8859-1'

    def process(self, ob: Openbis, transaction: Transaction, dataset: DataSet, loader_name: str, description: str) -> Transaction:
        """
        This is the function which processes the incoming dataset and extracts the metadata for openbis.
        The function requires the additional parameters `loader_name` and `description`. These are shown automatically in the dataset extractor UI
        """
        #Load file
        with zipfile.ZipFile(dataset.file_list[0], 'r') as zf,  tempfile.TemporaryDirectory() as td:
            #Extract the batch log of all measurements
            batch_log, *rest = match_files(zf, "BatchLog.csv")
            if batch_log:
                #Iterate over the row of the log
                batch_log_path = zf.extract(batch_log, path=td)
                batch_log_dt = clean_names(pd.read_csv(batch_log_path, encoding=self.encoding))
                for row in batch_log_dt.itertuples():
                    #Create metadata for each sample in the measurement log
                    props = {
                    "icpms.sample_name": row.samplename, 
                    'icpms.acq_timestamp': row.acq_date_time, 
                    'icpms.sample_type': row.sampletype,
                    'icpms.acquistion_result': row.acquisitionresult,
                    'icpms.operator': row.operator}
                    if dataset.sample is not None:
                        ids = dataset.sample.experiment.identifier
                        proj = dataset.sample.project.identifier
                    elif dataset.experiment is not None:
                        ids = dataset.experiment.identifer

                        proj = dataset.experiment.project.identifier
                    new_exp = f"{proj}/ICP_MS_MEASUREMENTS"
                    sample = ob.new_object(type='ICPMS', code=None, props=props, experiment= new_exp)
                    if dataset.sample is not None:
                        sample.set_parents(dataset.sample.identifier)
                    print("Adding sample")
                    transaction.add(sample)
        #Return the transaction with the new openbis objects (samples / collections / etc)
        return transaction