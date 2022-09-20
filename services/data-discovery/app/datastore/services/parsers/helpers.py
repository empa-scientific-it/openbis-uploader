from abc import ABC
from contextlib import contextmanager
from dataclasses import Field, dataclass, field
from pybis import Openbis
from typing import Protocol, Optional, Dict
from datastore.models.parser import ProcessState, ParserProcess
from uuid import UUID
import abc

from functools import cache
# class OpenbisMethodCapturer:

#     def __init__(self, ob: Openbis) -> None:
#         self.ob = ob


# def atomic_openbis_operations(ob: Openbis):


class ProcessingJobRegistry(Protocol):

    @abc.abstractmethod
    def append_job(self, job: ParserProcess) -> None:
        pass

    @abc.abstractmethod
    def get_job(self, uid: UUID) -> Optional[ParserProcess]:
        pass

@dataclass
class DictJobRegister(ProcessingJobRegistry):
    jobs: Dict[UUID, ParserProcess] = field(default_factory=lambda :{})

    def append_job(self, job: ParserProcess) -> None:
        self.jobs[job.uid] = job
        
    def get_job(self, uid: UUID) -> Optional[ParserProcess]:
        return self.jobs.get(uid)
    

@cache
def get_registry() -> ProcessingJobRegistry:
    return DictJobRegister({})