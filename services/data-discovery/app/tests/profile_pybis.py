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

from instance_creator import views

ob = pybis.Openbis("https://localhost:8443", verify_certificates=False, token=None, use_cache=False)
ob.login('basi', 'password')


tree = views.build_sample_tree(ob)

                    
breakpoint()

  