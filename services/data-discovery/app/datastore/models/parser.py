from pydantic import BaseModel, fields
from typing import Dict, Optional, Tuple, List, Any
from uuid import UUID, uuid4
import enum

class FunctionParameters(BaseModel):
    pass

class ParserParameters(BaseModel):
    source: str
    object: str | None
    collection: str | None
    parser: str
    dataset_type: str
    function_parameters: Dict[str, Any]


class ProcessState(enum.Enum):
    STOPPED = 0
    IN_PROGRESS = 1
    FINISHED = 2
    FAILED = -1

class ParserProcess(BaseModel):
    uid: UUID = fields.Field(default_factory=uuid4)
    status: ProcessState = ProcessState.STOPPED
    result: Any = None