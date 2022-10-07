from typing import List, NamedTuple, Dict, Tuple, TypeVar, Any
import pandas as pd
from pathlib import PurePath
import requests




def jrpc_request(url: str, method: str, params: List[Any]) -> Dict:
    """
    Creates a JRPC request
    """
    body = {
        "id": "1",
	    "jsonrpc": "2.0",
	    "method": method,
        "params": params
    }
    requests.post(url, json=body)

def get_token(url: str, username: str, password: str) -> str:
    """
    Gets the openbis
    """
    jrpc_request(url, 'login', [username, password])


def split_identifier(id: str, sep='/') -> List[str] | None:
    return list(filter(None, id.split(sep)))

def split_path(id: str) -> Tuple[str, ...] | None:
    return PurePath(id).parts

def prop_dict(row: Dict, props: List[str]):
    return dict(filter(lambda x: x[0] in props and not pd.isnull(x[1]), row._asdict().items()))

T = TypeVar('T')
def first_valid(lst: List[T]) -> T | None:
    return next(item for item in lst if item is not None)

T = TypeVar('T')
def none_if(val: T, check: T) -> T | None:
    if val == check:
        return None
    else:
        return val