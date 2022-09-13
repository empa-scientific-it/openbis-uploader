from pydantic import BaseModel
from typing import Dict, Optional, Tuple, List, Any

class ParserParameters(BaseModel):
    source: str
    object: str | None = None
    collection: str | None = None
    parser: str
    dataset_type: str
    function_parameters: Dict[str, Any] | None = None