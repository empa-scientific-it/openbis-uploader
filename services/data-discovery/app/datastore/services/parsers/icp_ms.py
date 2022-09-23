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
import logging

LOGGER = logging.getLogger(__name__)

from typing import List, Callable
import pandas as pd
        
def match_files(zf: pl.Path, predicate: Callable[[pl.Path], bool]) -> List[pl.PurePath]:
    return [pl.PurePath(f) for f in zf.iterdir() if predicate(f)]

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
        #Create names
        if dataset.sample is not None:
            ids = dataset.sample.experiment.identifier
            proj = dataset.sample.project.identifier
            is_sample = True
        elif dataset.experiment is not None:
            ids = dataset.experiment.identifer
            proj = dataset.experiment.project.identifier
            is_sample = False
        else:
            raise ValueError()
        #Extract file temporarily
        with  tempfile.TemporaryDirectory() as td:
            with zipfile.ZipFile(dataset.file_list[0], 'r') as zf:
                zf.extractall(path=td)
            LOGGER.info("Extracting all contents")
            td_path = pl.Path(td)
            #Extract the batch log of all measurements
            batch_log, *rest = td_path.glob("**/BatchLog.csv")
            if batch_log:
                #Iterate over the row of the log
                batch_log_dt = clean_names(pd.read_csv(batch_log, encoding=self.encoding))
                for row in batch_log_dt.itertuples():
                    LOGGER.info('Adding properties')
                    #Create metadata for each sample in the measurement log
                    props = {
                    "icpms.sample_name": row.samplename, 
                    'icpms.acq_timestamp': row.acq_date_time, 
                    'icpms.sample_type': row.sampletype,
                    'icpms.acquistion_result': row.acquisitionresult,
                    'icpms.operator': row.operator}
                    if row.acquisitionresult != 'Skip':
                        new_exp = f"{proj}/ICP_MS_MEASUREMENTS"
                        LOGGER.info('Creating sample')
                        sample = ob.new_object(type='ICPMS', props=props, experiment= new_exp)
                        LOGGER.info(f"saved sample {sample.identifier}")
                        # if is_sample:
                        #     sample.set_parents(ids)
                        transaction.add(sample)
                        
                        #Add a dataset for each sample
                        #Because the transaction is not finished, generate sample code here
                        #import pytest; pytest.set_trace()
                                            #Find the dataset for the sample
                        # subdataset_name = pl.PureWindowsPath(row.filename).name
                        # mts = td_path.glob("**/{subdataset_name}")
                        # if mts:
                        #     zf_iter = zipfile.Path(zf, at=str(mts[0]) + '/' )
                        #     subdataset_extract = [zf.extract(f.at, path=td)  for f in zf_iter.iterdir()]
                        #     if len(subdataset_extract) > 0:
                        #         LOGGER.info(subdataset_extract)
                        #         subdataset = ob.new_dataset(type='RAW_DATA', code=sample.code, sample=sample.identifier, files=subdataset_extract)
                        #         LOGGER.info(f"Attaching dataset to {sample.identifier}")
                        #         transaction.add(subdataset)
                                #subdataset.save()
                    #print(a)
        #Comit the transaction with the new openbis objects (samples / collections / etc)
        return transaction