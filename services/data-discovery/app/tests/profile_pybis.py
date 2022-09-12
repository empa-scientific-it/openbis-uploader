import cProfile, pstats, io
from pstats import SortKey
from pydoc import pathdirs
from unittest.mock import NonCallableMock
import xdrlib
import pybis
from typing import List, Generator, Dict, Optional, Any
import pathlib as pl

from pydantic import BaseModel, fields, dataclasses
import dataclasses
from collections import defaultdict
import tempfile as tf

from datastore.services.parsers.interfaces import OpenbisDatasetParser, process

from pybis.openbis_object import Transaction
from pybis.dataset import DataSet
from pybis import Openbis

from instance_creator import views
import os


ob = pybis.Openbis("https://localhost:8443", verify_certificates=False, token=None, use_cache=False)
ob.login('basi', 'password')


tree = views.build_sample_tree_from_list(ob)
tran = ob.new_transaction()  


class TestParser(OpenbisDatasetParser):
    a: int = 1
    b: str = 'bla'

    def process(tran: Transaction, dataset: DataSet, a: int, b:'str') -> Transaction:
        pybis.Openbis.new_object('ICP-MS-MEASUREMENT', '/MEASUREMENTS/TEST/ICPMS_MEAS1', {'GAS_FLOW':1.2, 'SAMPLE_ID':a})
    

parser = TestParser()

with  tf.NamedTemporaryFile() as temp_file:
    temp_file.write(os.urandom(1024))
    fn = temp_file.name
    ds = ob.new_dataset(type='RAW_DATA', experiment='/MEASUREMENTS/TEST/EXP1', files=fn)
    tran.add(ds)              
    process(parser, tran)

  

