from enum import Enum
from io import BufferedReader, FileIO
from typing_extensions import Self
from pydantic import BaseModel, HttpUrl, AnyHttpUrl, Json
from pydantic.generics import GenericModel
from pybis import Openbis
from typing import List, Any, Tuple, Generator
import pathlib as pl
from contextlib import contextmanager, ExitStack

class OpenbisConnection(BaseModel):
    openbis: AnyHttpUrl
    token: str

    @classmethod
    def from_ob(cls, ob: Openbis) -> 'OpenbisConnection':
        return cls(openbis = ob.url, token = ob.token)


class JRPCBase(BaseModel):
    id: str = "1"
    jsonrpc: str = "2.0"

class JRPCRequest(JRPCBase):
    method: str
    params: List[str | dict | int ]

class JRPCResponse(JRPCBase):
    result: str | int | List[str | int | dict] | dict


class OpenbisJRPCEndpoints(str, Enum):
    v3_api = "/openbis/openbis/rmi-application-server-v3.json"
    v1_api = "/openbis/openbis/rmi-general-information-v1.json"
    dss_appi = "/datastore_server/rmi-dss-api-v1.json"

class OpenbisElnUpload(BaseModel):
    type: str
    files: dict[str, pl.Path]
    sessionID: str

    @contextmanager
    def to_form(self) -> Generator[dict[str, int | str | tuple[str, BufferedReader]], 'OpenbisElnUpload', None]:
        try:
            with ExitStack() as stack:
                fs = {name: (str(file), open(file, 'rb')) for name, file in self.files.items()}
                rest = {"sessionKeysNumber": (None, 1) , "sessionID": (None, self.sessionID)}
                sk_mapping = {"sessionKey_0": (None, f) for f in self.files.keys()}
                yield rest | fs | sk_mapping
        finally:
            print('bye')