from abc import ABC, abstractmethod
from pybis import Openbis 
from pybis.openbis_object import Transaction
from pybis.dataset import DataSet
from pydantic import create_model, BaseModel
from pydantic.main import ModelMetaclass

import inspect
from typing import NewType

class ParserParameters(BaseModel):
    pass

class OpenbisDatasetParser(ABC):
    """
    Abstract Base class defining
    the interface for all methods used to 
    parse dataset and register them into openbis.

    To make this, the user only needs to implement the
    `process` method, which takes a :obj:`pybis.openbis_object.Transaction`  Transaction,
    a :obj:`pybis.openbis_object.DataSet` and returns another transaction.

    To define additional arguments to the method, the class derived from :obj:`OpenbisDatasetParser` 
    can define new fields in the :obj:`dataclasses` style. 
    These arguments will be passed to the `process` method at runtime. 

    Because this class is derived from :obj:`pydantic.BaseModel`., it can return a representation 
    of the parser parameters as a JSON schema, these are used to automatically fill a form or create an
    API response.
    """


    @abstractmethod
    def process(self, ob: Openbis, transaction: Transaction, dataset: DataSet, *args, **kwargs) -> Transaction:
        """
        Abstract method to extract metadata from file and 
        register additional samples  / datasets.
        The method takes an openbis transaction, an openbis connection, an openbis DataSet and returns another transaction
        Additional parameters can be defined, to provide to the function at runtime
        """
        pass

    def _generate_basemodel(self) -> ModelMetaclass:
        """
        Generates a :obj:`pydantic.BaseModel`
        from the annotation of the `process` function of
        the derived class.
        """
        excluded_names = ['transaction', 'dataset', 'ob']
        sig = inspect.signature(self.process)
        model = {par.name:(par.annotation, (... if par.default == inspect._empty else par.default)) for _, par in sig.parameters.items() if par.name not in excluded_names}
        model_name = f"{self.__class__.__name__}"
        full_model = {'arguments':model, 'description': self.process.__doc__}
        p1 = ParserParameters
        p1.__doc__ =\
        f"""
        Class: 
        {self.__doc__}
        Process Function:
        {self.process.__doc__}
        """
        pydantic_model = create_model(model_name, **model)
        return pydantic_model

Parent = NewType('Parser', OpenbisDatasetParser)

def process(obj: Parent, tran: Transaction):
    """
    Worker method to process
    the parser.
    """
    bm = obj._generate_basemodel()

