from pydantic import BaseModel
from typing import Dict, Optional, Tuple, List, Any

class FunctionParameters(BaseModel):
    pass

class ParserParameters(BaseModel):
    source: str
    object: str | None
    collection: str | None
    parser: str
    dataset_type: str
    function_parameters: Dict[str, Any]

