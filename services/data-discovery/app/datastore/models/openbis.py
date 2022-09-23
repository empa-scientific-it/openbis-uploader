from pydantic import BaseModel, HttpUrl, AnyHttpUrl
from pybis import Openbis

class OpenbisConnection(BaseModel):
    openbis: AnyHttpUrl
    token: str

    @classmethod
    def from_ob(cls, ob: Openbis) -> 'OpenbisConnection':
        return cls(openbis = ob.url, token = ob.token)