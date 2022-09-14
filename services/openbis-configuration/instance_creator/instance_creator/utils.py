from typing import List, NamedTuple, Dict, Tuple, TypeVar
import pandas as pd
from pathlib import PurePath
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