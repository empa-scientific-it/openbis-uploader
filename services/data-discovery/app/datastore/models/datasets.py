from pydantic.dataclasses import dataclass
from pydantic import BaseModel
from typing import Iterable, List, Optional, Dict, Union
import datetime as dt
import pathlib as pl

class FileInfo(BaseModel):
    """
    Helper class containing information on a file. This is based on pydantic
    models. 
    :ivar name: file name
    :ivar path: file path on the datastore
    :ivar modified: date of modification of the file
    :ivar created: date of file creation
    :ivar size: size of the file on disk
    """
    name: str
    path: pl.Path
    modified: dt.datetime
    created: dt.datetime
    size: float

    @classmethod
    def from_path(cls, p: pl.Path) -> "FileInfo":
        """
        Factory function to generate a :obj:`FileInfo` instance
        from a path
        :param p: path of the file to read in
        """
        st = p.stat()
        return FileInfo(name=p.name, path=p.expanduser().absolute(), modified=dt.datetime.fromtimestamp(st.st_mtime), created=dt.datetime.fromtimestamp(st.st_ctime), size=st.st_size)


class Response(BaseModel):
    """
    """
