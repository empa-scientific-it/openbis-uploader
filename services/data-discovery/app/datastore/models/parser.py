from pydantic import BaseModel, fields
from typing import Dict, Optional, Tuple, List, Any
from uuid import UUID, uuid4
import enum
from instance_creator.views import OpenbisHierarcy


class FunctionParameters(BaseModel):
    pass

class ParserParameters(BaseModel):
    source: str
    identifier: str 
    type: OpenbisHierarcy
    parser: str
    dataset_type: str
    function_parameters: Dict[str, Any]


class ProcessState(enum.Enum):
    STOPPED = 0
    IN_PROGRESS = 1
    FINISHED = 2
    FAILED = -1

class ParserProcess(BaseModel):
    taskid: str
    status: ProcessState = ProcessState.IN_PROGRESS
    result: Any = None