
""""
Openbis instance configurator.
Copyright (C) 2022 Simone Baffelli

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from abc import ABC
from ast import Pass
from dataclasses import field
from re import S
from typing import Callable, Any, Dict, List, Literal, Type, TypeVar, Union, Generator
import pybis
from pybis.pybis import PropertyType, Space, SampleType, ExperimentType, Project, OpenBisObject, Experiment, Things, Sample, DataSetType, DataSet, Person
from pydantic.dataclasses import dataclass
from pydantic import BaseModel, Field, validator, root_validator
import pathlib as pl
from .validators import children_validator, TreeObject

import functools

class OpenbisGenericObject(ABC, BaseModel, TreeObject):
    """
    Abstract base class implementing
    the interface for a generic openbis object
    """
    def create(self, ob: pybis.Openbis) -> None:
        pass
    
    def wipe(self, ob: pybis.Openbis) -> None:
        pass

    def get_ob_object(self, ob: pybis.Openbis) -> 'OpenBisObject':
        pass
    
    def reflect(self, ob: pybis.Openbis) -> 'OpenbisGenericObject':
        pass

class OpenbisRoleAssignment(OpenbisGenericObject):
    """
    Class to represent openbis role assignment for an unser
    """
    techid: int = None
    user: str | None = None
    role: Literal["OBSERVER", "POWER_USER", "ADMIN", "ETL_SERVER", "USER"]  = None
    level: Literal["INSTANCE","SPACE","PROJECT"]  = None
    space: str | None = None
    group: str | None = None
    project: str | None = None

    def get_ob_object(self, ob: pybis.Openbis) -> 'OpenBisObject':
        return ob.get_role_assignment(self.techid)

    def reflect(self, ob: pybis.Openbis) -> 'OpenbisRoleAssignment':
        ra = self.get_ob_object(ob)
        sp = ra.space.code if ra.space else None
        pr = ra.project.code if ra.project else None
        return OpenbisRoleAssignment(techid=int(ra.id), user=ra.user, role=ra.role, level=ra.roleLevel, space=sp, project=pr)
    
    def create(self, ob: pybis.Openbis):
        user = ob.get_user(self.user)
        match self.level, user:
            case _, None:
                raise ValueError(f"Could not find user with id {self.user}")
            case "INSTANCE", _:
                match self.role:
                    case "ADMIN" | "OBSERVER":
                        user.assign_role(self.role)
                        user.save()
                    case _:
                        raise ValueError(f"Cannot assign role {self.role} to instance")
            case "SPACE", _:
                    match self.role:
                        case "POWER_USER" | "USER" | "OBSERVER" | "ADMIN":
                            u = user.assign_role(self.role, space=self.space)
                            user.save()
                        case _:
                            raise ValueError(f"Cannot assign role {self.role} to space")
    
            case _, _:
                raise NotImplementedError("Project-level assignment not implemented")

class OpenbisUser(OpenbisGenericObject):
    userid: str = None
    first_name: str = None
    last_name: str = None
    space: str = None
    roles: List[OpenbisRoleAssignment] | None = None

    def get_ob_object(self, ob: pybis.Openbis) -> Person:
        return ob.get_user(self.userid)
    
    def reflect(self, ob: pybis.Openbis) -> 'OpenbisUser':
        po = self.get_ob_object(ob)
        return OpenbisUser(userid = po.userId, first_name= po.firstName, last_name=po.lastName)


class OpenbisTreeObject(OpenbisGenericObject):
    """
    Class implementing a generic object in the openbis tree
    (Instance / Space / Project / Collection / Experiment)
    """
    code: str = None
    parent_id: List[str] = Field(None, exclude=True)
    children: List['OpenbisTreeObject'] | None = None


    def path(self) -> str:
        els = [el for el in self.parent_id if el is not None] + [(self.code if self.code is not None else '')]
        return str(pl.PurePath(*els))
    
    def wipe(self, ob: pybis.Openbis):
        
        if self.children:
            for child in self.children:
                child.wipe(ob)
        obj = self.get_ob_object(ob)
        if obj.registrator != 'system':
            obj.delete(f"Deleted by {self.__class__}")


class OpenbisObjectTree(OpenbisTreeObject):
    """
    Class implementing the tree of samples 
    in openbis (/SPACE/PROJECT/COLLECTION/Experiment)
    """

    code: str | None = None
    children: List['OpenbisObjectTree'] = None

    @classmethod
    def create(ob: pybis.Openbis) -> 'OpenbisObjectTree':
        #Get the objects
        init_struct = OpenbisTreeObject('/')
        objs:Things = ob.get_objects(attrs=['space', 'experiment', 'project', 'code', 'type'])
        #Extract the identifiers
        paths:List[str] = objs.df.identifier.to_list()
        #Iterate over paths
        for p in paths:
            components = p.split('/')
            functools.reduce(lambda tree, element:  tree['children'].append({'id': 'element'}) ,components, {'children': ''} )


def tree_builder(path: List[str], current: str) -> Generator:
    if path:
        for p in path:
            children = yield from tree_builder(p, current)
            yield {'id': current, 'children': [children]}
    else:
        yield {'id': current, 'children': []}


class OpenbisSample(OpenbisTreeObject):
    """
    Class representing an openBis sample
    """
    type: str
    properties: Dict | None = None
    def create(self, ob: pybis.Openbis, space: Type['OpenbisSpace'], project: Type['OpenbisProject'] | None = None, collection: Type['OpenbisCollection'] | None = None):
        sm = ob.new_sample(self.type, experiment=collection.path(), props = self.properties)
        try:
            sm.save()
        except:
            ob.get_sample()
        self.code = sm.permId
    
    def wipe(self, ob: pybis.Openbis):
        self.get_ob_object(ob).delete("Automatically deleted by {self.__class__}}")
    
    def get_ob_object(self, ob: pybis.Openbis) -> Sample:
        return ob.get_object(self.path())

    def reflect(self, ob: pybis.Openbis) -> 'OpenbisSample':
            return self.copy()   



class OpenbisCollection(OpenbisTreeObject):
    """
    Class representing an openBis collection
    """
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
    
    def get_ob_object(self, ob: pybis.Openbis) -> Experiment:
        return ob.get_collection(self.path())

    def get_children(self, ob: pybis.Openbis) -> List[OpenbisSample]:
        """
        Retreives all children of this collection
        """
        col:Experiment = self.get_ob_object(ob)
        children = col.get_objects()
    
    def reflect(self, ob: pybis.Openbis) -> 'OpenbisCollection': 
        coll = self.get_ob_object(ob)
        children = [OpenbisSample(code=ch.code, type=ch.type.code, parent_id=self.parent_id + [self.code]).reflect(ob) for ch in coll.get_objects()]
        objs = OpenbisCollection(code=self.code, type=coll.type.code, parent_id=self.parent_id, samples=children)
        return objs

class OpenbisProject(OpenbisTreeObject):
    """
    Class representing an openBis project
    """
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
    
    def get_ob_object(self, ob: pybis.Openbis) -> Project:
        return ob.get_project(self.path())

    def reflect(self, ob: pybis.Openbis) -> 'OpenbisProject':
        sp = self.get_ob_object(ob)
        collections = sp.get_collections()
        return OpenbisProject(code=self.code, parent_id=self.parent_id, collections = [OpenbisCollection(code = pr.code, parent_id=self.parent_id + [self.code], type = pr.type.code).reflect(ob) for pr in collections])

class OpenbisSpace(OpenbisTreeObject):
    """
    Class representing an openBis space
    """
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

    def get_ob_object(self, ob: pybis.Openbis) -> Experiment:
        return ob.get_space(self.code)

    def reflect(self, ob: pybis.Openbis) -> 'OpenbisSpace':
        sp = self.get_ob_object(ob)
        projects = sp.get_projects()
        return OpenbisSpace(code=self.code, projects = [OpenbisProject(code = pr.code, parent_id=self.parent_id + [self.code]).reflect(ob) for pr in projects], parent_id=self.parent_id)
 
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
    
    def get_ob_object(self, ob: pybis.Openbis) -> PropertyType:
        return ob.get_property_type(self.code)
    
    def wipe(self, ob: pybis.Openbis):
        obj = self.get_ob_object(ob)
        obj.delete("Automatically deleted by {self.__class__}")


class OpenbisObjectType(OpenbisGenericObject):
    code: str
    prefix: str
    properties: Dict[str, List[str]] | None = {}
    extras: Dict[str, str] | None = None
    autogenerate_code: bool = True
    children  : None = None

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
    
    def get_ob_object(self, ob: pybis.Openbis) -> SampleType:
        return ob.get_object_type(self.code)
    
    def wipe(self, ob: pybis.Openbis):
        obj = self.get_ob_object()
        obj.delete(f"Automatically deleted by {self.__class__}")

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
    
    def get_ob_object(self, ob: pybis.Openbis) -> ExperimentType:
        return ob.get_collection_type(self.code)
    
    def wipe(self, ob: pybis.Openbis) -> None:
        obj = self.get_ob_object(ob)
        obj.delete(f"Automatically deleted by {self.__class__}")



class OpenbisDatasetType(OpenbisGenericObject):
    code: str
    description: str 
    pattern: str | None = None
    path: str | None = None
    properties: List[str] | None = {}

    def get_ob_object(self, ob: pybis.Openbis) -> DataSetType:
        return ob.get_collection_type(self.code)
    
    def create(self, ob: pybis.Openbis) -> None:
        dt: DataSetType = ob.new_dataset_type(code=self.code, 
        description=self.description, mainDataSetPath=self.path, mainDataSetPattern=self.pattern)
        try:  
            dt.save()
            for prop in self.properties:
                    dt.assign_property(prop)
                    dt.save()
        except:
            pass

class OpenbisInstance(OpenbisGenericObject):
    code: str = '/'
    children: List[OpenbisSpace] | None = Field(None, alias='spaces') 
    object_types: List[OpenbisObjectType] | None = None
    collection_types: List[OpenbisCollectionType] | None = None
    properties: List[OpenbisProperty] | None = None
    dataset_types: List[OpenbisDatasetType] | None = None
    users: List[OpenbisUser] | None = None
    roles: List[OpenbisRoleAssignment] | None = None
    def create(self, ob: pybis.Openbis):
        if self.properties:
            for prop in self.properties:
                prop.create(ob)
        if self.object_types:
            for ot in self.object_types:
                ot.create(ob)
        if self.collection_types:
            for ot in self.collection_types:
                ot.create(ob)
        if self.children:
            for sp in self.children:
                sp.create(ob)
        if self.users:
            for sp in self.users:
                sp.create(ob)
        if self.roles:
            for sp in self.roles:
                sp.create(ob)
    
    def wipe(self, ob: pybis.Openbis):
        for sp in self.children:
            sp.wipe(ob)
        for ot in self.collection_types:
            ot.wipe(ob)
        for ot in self.object_types:
            ot.wipe(ob)
        for prop in self.properties:
            prop.wipe(ob)

    def export(self, path: pl.Path):
        """
        Export this object to a JSON file
        """
        txt = self.json(indent=2, by_alias=True)
        with open(path, 'w') as of:
            of.write(txt)
        
    @classmethod
    def reflect(cls, ob: pybis.Openbis) -> 'OpenbisInstance':
        """
        Given an openbis connection, try
        to reflect it as a object of type OpenbisInstance
        """
        #Get all Object types
        object_types = [OpenbisObjectType(code=ot.code, prefix=ot.generatedCodePrefix) for ot in get_non_system_entities(ob, "object_types")]
        #Get all property types
        property_types = [OpenbisProperty(code=p.code, label=p.label, data_type=p.dataType, description=p.description) for p in get_non_system_entities(ob, "property_types")]
        #Get all collection types
        collection_types = [OpenbisCollectionType(code=p.code, description=p.description) for p in get_non_system_entities(ob, "collection_types")]
        #Get all the tree
        dont_touch = ['ELN_SETTINGS', 'STORAGE', 'METHODS', 'MATERIALS', 'STOCK_CATALOG', 'STOCK_ORDERS', 'PUBLICATIONS']
        children = [OpenbisSpace(code=sp.code, parent_id=['/']).reflect(ob)  for sp in ob.get_spaces() if sp.code not in dont_touch]
        #Reflect users
        users = [OpenbisUser(userid=ui).reflect(ob) for ui in ob.get_users().df.userId]
        #Reflect role assignments
        roles = [OpenbisRoleAssignment(techid=ui).reflect(ob) for ui in ob.get_role_assignments().df.techId.astype(int)]
        return cls(object_types = object_types, collection_types = collection_types, properties = property_types, spaces=children, users=users, roles=roles)

    @root_validator(pre=False)
    def check_parent(cls, values):
        if 'children' in values.keys():
            if child:= values.get('children'):
                for c in child:
                    c.parent_id = values.get('code')
                    children_validator(c, [values.get('code')])
        return values


def get_non_system_entities(ob: pybis.Openbis, type:str) -> List[SampleType | ExperimentType | PropertyType]:
    def df_selector(entities: Things, attribute: str) -> List[str]:
        return [e for e in entities.df[entities.df.registrator != 'system'][attribute].unique()]
    def comp_selector(entities: Things, attribute: str) -> List[str]:
        return list(set([getattr(e, attribute) for e in entities if getattr(e, 'registrator') != 'system']))
    match type:
        case "object_types":
            selector = ob.get_objects
            constructor = ob.get_object_type
            attribute = 'type'
            filter_fun = df_selector
        case "collection_types": 
            selector = ob.get_collections
            constructor = ob.get_collection_type
            attribute = 'type'
            filter_fun = df_selector
        case "property_types":
            selector = ob.get_property_types
            constructor = ob.get_property_type
            attribute = 'code'
            filter_fun = df_selector
        case "spaces":
            selector = ob.get_spaces
            constructor = ob.get_space
            attribute = 'code'
            filter_fun = comp_selector
        case _:
            raise ValueError(f"Not implemented for {type}")
    entities = selector()
    non_system_entities =  filter_fun(entities, attribute)
    return [constructor(e) for e in non_system_entities]

        