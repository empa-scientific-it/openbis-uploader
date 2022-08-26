from abc import ABC, ABCMeta
from ast import Pass
from typing import Callable, Any, Dict, List, Literal, Type, TypeVar, Union
import pybis
from pybis.pybis import PropertyType, Space, SampleType, ExperimentType, Project, OpenBisObject
from pydantic.dataclasses import dataclass
from pydantic import BaseModel, Field, validator, root_validator
import pathlib as pl
from pydantic.typing import ForwardRef

import argparse as ap

"""
This module can be used to automatically populate an openBIS instance
from a configuration file
"""


def wrap_ob(fun: Callable) -> Callable:
    def run(*args, **kwargs) -> Any | None:
        try:
            return fun(*args, **kwargs)
        except ValueError:
            return None
    return run

def wipe_properties(ob: pybis.Openbis):
    """
    Wipes all object types from openbis
    """
    for sp in ob.get_sample_types():
        sp.delete("Ok")

def wipe_space(ob: pybis.Openbis, space: str):
    """
    Wipes all objects from an openbis space
    """
    sp:Space = ob.get_space(space)
    for project in sp.get_projects():
        for collection in project.get_collections():
            for sample in collection.get_objects():
                sample.delete("Wiping everything")
            collection.delete("Wiping everything")
        project.delete("Wiping everything")
    sp.delete("Wiping everything")




class OpenbisGenericObject(ABC, BaseModel):
    def create(self, ob: pybis.Openbis) -> None:
        pass
    
    def wipe(self, ob: pybis.Openbis) -> None:
        Pass


stack = []

class OpenbisTreeObject(OpenbisGenericObject):
    code: str = None
    parent_id: List[str] = None
    children: List['OpenbisTreeObject'] | None = None


    def path(self) -> str:
        els = [el for el in self.parent_id if el is not None] + [(self.code if self.code is not None else '')]
        return str(pl.PurePath(*els))
    
    def wipe(self, ob: pybis.Openbis):
        if self.children:
            for child in self.children:
                child.wipe(ob)


class OpenbisSample(OpenbisTreeObject):
    type: str
    properties: Dict | None = None
    def create(self, ob: pybis.Openbis, space: Type['OpenbisSpace'], project: Type['OpenbisProject'] | None = None, collection: Type['OpenbisCollection'] | None = None):
        breakpoint()
        sm = ob.new_sample(self.type, experiment=collection.path(), props = self.properties)
        try:
            sm.save()
        except:
            ob.get_sample()
        breakpoint()
        self.code = sm.permId
    
    def wipe(self, ob: pybis.Openbis):
        breakpoint()




class OpenbisCollection(OpenbisTreeObject):
    code: str
    type: str
    children: List[OpenbisSample] | None = Field(None, alias='samples')
    properties: Dict | None = None
    def create(self, ob: pybis.Openbis, space: 'OpenbisSpace', project: 'OpenbisProject'):
        col = ob.new_collection(self.type, code=f"{self.code}", project=project.code, props=self.properties)
        try:
            col.save()
        except ValueError as e:
            col = ob.get_collection(self.path())
        if self.children:
            for s in self.children:
                sp = s.create(ob, space, project, self)
                try:
                    sp.save()
                except:
                    pass

  
   

class OpenbisProject(OpenbisTreeObject):
    code: str
    description: str | None = None
    children: List[OpenbisCollection] | None = Field(None, alias='collections')
    def create(self, ob: pybis.Openbis, parent: 'OpenbisSpace'):
        pr = ob.new_project(parent.code, self.code, description=self.description)
        try:
            pr.save()
        except:
            pass
        for c in self.children:
            c.create(ob, parent, self)
    


class OpenbisSpace(OpenbisTreeObject):
    code: str
    children: List[OpenbisProject] | None = Field(None, alias='projects')
    def create(self, ob: pybis.Openbis):
        #Create space
        sp = ob.new_space(code=self.code)
        try:
            sp.save()
        except:
            pass
        #Create projects
        for p in self.children:
            p.create(ob, sp)
    


 

 
class OpenbisProperty(OpenbisGenericObject):
    code: str 
    label: str
    description: str = Field(..., min_length=1)
    data_type: Literal["INTEGER", "VARCHAR", "MULTILINE_VARCHAR", "REAL", "TIMESTAMP", "BOOLEAN", "HYPERLINK", "XML", "CONTROLLEDVOCABULARY", "MATERIAL"]

    def create(self, ob: pybis.Openbis):
        pt = ob.new_property_type(self.code, self.label, self.description, self.data_type)
        try:
            pt.save()
        except:
            pass


class OpenbisObjectType(OpenbisGenericObject):
    code: str
    prefix: str
    properties: Dict[str, List[str]] | None = {}
    extras: Dict[str, str] | None = None
    autogenerate_code: bool = True
    def create(self, ob: pybis.Openbis):
        ot:SampleType = ob.new_object_type(code = self.code, generatedCodePrefix = self.prefix, autoGeneratedCode=self.autogenerate_code)
        try:
            ot.save()
        except:
            ot = ob.get_sample_type(self.code)
        try:
            for section, props in self.properties.items():
                for prop in props:
                    ot.assign_property(prop, section=section)
                    try:
                        ot.save()
                    except:
                        pass
        except:
            pass

class OpenbisCollectionType(OpenbisGenericObject):
    code: str
    description: str
    properties: List[str] | None = {}
    def create(self, ob: pybis.Openbis):
        ot:ExperimentType = ob.new_collection_type(code = self.code, description= self.description)
        try:  
            ot.save()
            for prop in self.properties:
                    ot.assign_property(prop)
                    ot.save()
        except:
            pass


def children_validator(values, stack):
    if values.children:
        for child in values.children:
            if child.code:
                path = [*stack, child.code]
            else:
                path = stack
            child.parent_id = stack
            children_validator(child, path)
    else:
        values.parent_id = stack
            

class OpenbisInstance(OpenbisGenericObject):
    code: str = '/'
    children: List[OpenbisSpace] | None = Field(None, alias='spaces') 
    object_types: List[OpenbisObjectType] | None = None
    collection_types: List[OpenbisCollectionType] | None = None
    properties: List[OpenbisProperty] | None = None

    def create(self, ob: pybis.Openbis):
        for prop in self.properties:
            prop.create(ob)
        for ot in self.object_types:
            ot.create(ob)
        for ot in self.collection_types:
            ot.create(ob)
        for sp in self.children:
            sp.create(ob)
    
    def wipe(self, ob: pybis.Openbis):
        for prop in self.properties:
            prop.wipe(ob)
        for ot in self.object_types:
            ot.wipe(ob)
        for ot in self.collection_types:
            ot.wipe(ob)
        for sp in self.children:
            sp.wipe(ob)
        



    @root_validator(pre=False)
    def check_parent(cls, values):
        for c in values.get('children'):
            c.parent_id = values.get('code')
            children_validator(c, [values.get('code'), c.code])
            
        return values






parser = ap.ArgumentParser(usage="create_test_structure.py your_instance:port admin_user admin_password config_file.json")
parser.add_argument("url", type=str, help="Url to openbis instance")
parser.add_argument("username", type=str, help="Username")
parser.add_argument("password", type=str, help="password")
parser.add_argument("config", type=pl.Path, help="Path to json configuration file")
parser.add_argument('--wipe', action="store_true", help="If set, wipes the instance clean before creating")
args = parser.parse_args()



#Login
ob = pybis.Openbis(args.url,  verify_certificates=False, use_cache=False)
ob.logout()
ob.login(args.username, args.password)
oi = OpenbisInstance.parse_file(args.config)
oi.create(ob)
