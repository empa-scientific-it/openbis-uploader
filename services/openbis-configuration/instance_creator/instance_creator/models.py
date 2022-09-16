
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

from abc import ABC, abstractmethod
from ast import Pass
from dataclasses import field
from re import S
from select import select
from typing import Callable, Any, Dict, List, Literal, NamedTuple, Type, TypeVar, Union, Generator, Optional
from typing_extensions import Self
import pybis
from pybis.pybis import PropertyType, Space, SampleType, ExperimentType, Project, OpenBisObject, Experiment, Things, Sample, DataSetType, DataSet, Person, RoleAssignment
from pydantic.dataclasses import dataclass
from pydantic import BaseModel, Field, validator, root_validator
import pathlib as pl
from .validators import children_validator, TreeObject
from . import utils
import functools
import itertools


SACRED_SPACES = ['ELN_SETTINGS', 'STORAGE', 'METHODS', 'MATERIALS', 'STOCK_CATALOG', 'STOCK_ORDERS', 'PUBLICATIONS']
SACRED_USERS = ['etl', 'system']
SACRED_OBJECT_TYPES = ['UNKNOWN', 'GENERAL_ELN_SETTINGS', 'ENTRY', 'GENERAL_PROTOCOL', 'EXPERIMENTAL_STEP', 'STORAGE', 'STORAGE_POSITION', 'SUPPLIER', 'PRODUCT', 'REQUEST', 'ORDER', 'PUBLICATION', 'SEARCH_QUERY']
SACRED_COLLECTION_TYPES = ['DEFAULT_EXPERIMENT', 'UNKNOWN', 'COLLECTION']

class OpenbisGenericObject(ABC, BaseModel, TreeObject):
    """
    Abstract base class implementing
    the interface for a generic openbis object
    """
    perm_id: str | None = None
    code: str | None = None
    identifier: str | None = None
    registrator: str | None = None

    def create(self, ob: pybis.Openbis) -> None:
        pass

    def wipe(self, ob: pybis.Openbis) -> None:
        pass

    def get_ob_object(self, ob: pybis.Openbis) -> 'OpenBisObject':
        pass

    def reflect(self, ob: pybis.Openbis) -> 'OpenbisGenericObject':
        pass


    @classmethod
    def from_openbis(cls, ob: pybis.Openbis, code: str) -> 'OpenbisGenericObject':
        pass


class OpenbisRoleAssignment(OpenbisGenericObject):
    """
    Class to represent openbis role assignment for an unser
    """
    techid: int | None = None
    user: str | None = None
    role: Literal["OBSERVER", "POWER_USER", "ADMIN", "ETL_SERVER", "USER"] | None = None
    level: Literal["INSTANCE","SPACE","PROJECT"] | None  = None
    space: str | None = None
    group: str | None = None
    project: str | None = None
    children: None = None

    def get_ob_object(self, ob: pybis.Openbis) -> RoleAssignment | None:
        return ob.get_role_assignment(self.techid)

    def wipe(self, ob: pybis.Openbis) -> None:
        assign = self.get_ob_object(ob)
        if assign:
            assign.delete("Removed")

    @classmethod
    def from_openbis(cls, ob: pybis.Openbis, code: str) -> Optional['OpenbisRoleAssignment']:
        ob_obj = ob.get_role_assignment(code)
        if ob_obj:
            sp = ob_obj.space.code if ob_obj.space else None
            pr = ob_obj.project.code if ob_obj.project else None
            return cls(code=code, techid=int(code), user=ob_obj.user, level=ob_obj.roleLevel, space=sp, project=pr, group=ob_obj.group)

    def reflect(self, ob: pybis.Openbis) -> 'OpenbisRoleAssignment':
        ra = self.get_ob_object(ob)
        sp = ra.space.code if ra.space else None
        pr = ra.project.code if ra.project else None
        return OpenbisRoleAssignment(code=int(ra.id), techid=int(ra.id), user=ra.user, role=ra.role, level=ra.roleLevel, space=sp, project=pr)
    
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
    userid: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    space: str | None = None
    roles: List[OpenbisRoleAssignment] | None = None


    @classmethod
    def from_openbis(cls, ob: pybis.Openbis, code: str) -> 'OpenbisUser':
        us = ob.get_user(userId=code)
        roles = [OpenbisRoleAssignment.from_openbis(ob, role.techId) for role in us.get_roles()]
        return cls(userid=us.userId, first_name=us.firstName, last_name=us.lastName, space=us.space, roles=roles)

    def get_ob_object(self, ob: pybis.Openbis) -> Person:
        return ob.get_user(self.userid)
    
    def reflect(self, ob: pybis.Openbis) -> 'OpenbisUser':
        po = self.get_ob_object(ob)
        return OpenbisUser(userid = po.userId, first_name= po.firstName, last_name=po.lastName)


class OpenbisTreeObject(OpenbisGenericObject):
    """
    Class implementing a generic object in the openbis tree
    (Instance / Space / Project / Collection / Experiment),
    which can have parent, children and samples

    :param code: The openbis object code (NOT the full path identifier)
    :param perm_id: The openbis permid
    :param children: A list of children  
    :param samples: A list of children  

    """
    code: str | None = None
    perm_id: str | None = None
    parent_id: List[str] = Field(None, exclude=True)
    children: List['OpenbisTreeObject'] | List = []
    samples: List['OpenbisSample'] | List | None = []
    rel_in: List[str] | List = []
    rel_out: List[str] | List = []

    def path(self) -> str:
        els = [el for el in self.parent_id if el is not None] + [(self.code if self.code is not None else '')]

        return str(pl.PurePath(*els))
    
    def get_child(self, code: str) -> Optional['OpenbisTreeObject']:
        if self.children:
            found = [c for c in self.children if c.code == code]
            if found:
                return found[0]
    
    def find(self, identifier: str) -> Optional['OpenbisTreeObject']:
        if (self.code == identifier) or (self.identifier == identifier):
            return self
        else:
            if self.children:
                child = [p for c in self.children if (p:= c.find(identifier))]
                if len(child) > 0:
                    return child[0]

    
    def wipe(self, ob: pybis.Openbis):
        print("Deleting", self.code)
        if self.samples:
            for sample in self.samples:
                sample.wipe(ob)
        if self.children:
            for child in self.children:
                child.wipe(ob)
        obj = self.get_ob_object(ob)
        if obj.registrator != 'system':
            try:
                obj.delete(f"Deleted by {self.__class__}")
            except ValueError:
                pass




class OpenbisSample(OpenbisTreeObject):
    """
    Class representing an openBis sample
    """
    type: str
    properties: Dict | None = None
    collection: str | None = None
    space: str | None = None
    project: str | None = None
    samples: None | List['OpenbisSample'] = None

    def create(self, ob: pybis.Openbis, space: Type['OpenbisSpace'] | None, project: Type['OpenbisProject'] | None = None, collection: Type['OpenbisCollection'] | None = None):
        exp_path = (collection.path() if collection is not None else None)
        sp_path = (space.path() if space is not None else None)
        proj_path = (project.path() if project is not None else None)
        sm = ob.new_sample(self.type, code =(self.code if self.code else None), experiment=exp_path, space=sp_path, project=proj_path, props = self.properties)
        try:
            sm.save()
        except:
            ob.get_sample(self.code)
        self.code = sm.code
    
    def wipe(self, ob: pybis.Openbis):
        self.get_ob_object(ob).delete("Automatically deleted by {self.__class__}}")
    

    @classmethod
    def from_openbis(cls, ob: pybis.Openbis, code: str) -> 'OpenbisSample':
        """
        Creates a sample from openbis given its code (the full identifier in this case)
        """
        item = ob.get_object(code)
        obj = cls(code=item.code, 
            identifier=item.identifier, 
            perm_id=item.permId, 
            project=item.project.code if item.project else None, 
            collection=item.experiment.code if item.experiment else None, 
            space=item.space.code, 
            type=item.type.code,
            registrator=item.registrator,
            properties = item.props.all_nonempty()
            )
        return obj

    @classmethod
    def get_all_objects(cls, ob: pybis.Openbis, sample_type:str) -> List['OpenbisSample']:
        samples =  ob.get_samples(type=sample_type, props='*', attrs=['code','space', 'project', 'experiment'])
        prop_assigned = ob.get_object_type(sample_type).get_property_assignments()
        if not prop_assigned.df.empty:
            prop_names = prop_assigned.df.propertyType.to_list()
        else:
            prop_names = []
        objects = [
            cls(code=samp.code, 
            identifier=samp.identifier, 
            perm_id=samp.permId, 
            type=sample_type, 
            registrator=samp.registrator, 
            space=utils.none_if(samp.space, 'None'), 
            project=utils.none_if(samp.project, 'None'),
            collection=utils.none_if(samp.experiment, 'None'),
            parent_id = list(utils.split_path(samp.identifier))[:-1],
            properties=utils.prop_dict(samp, prop_names)) for samp in samples.df.itertuples()
            ]
        return objects

    def get_ob_object(self, ob: pybis.Openbis) -> Sample:
        return ob.get_object(self.path(), props='*')

    def reflect(self, ob: pybis.Openbis) -> 'OpenbisSample':
        obj = self.get_ob_object(ob)
        return OpenbisSample(code=obj.code, type=obj.type.code, perm_id=obj.permId, experiment=obj.collection.code, properties=obj.props.all_nonempty())



class OpenbisCollection(OpenbisTreeObject):
    """
    Class representing an openBis collection
    """
    code: str
    type: str
    #children: List[OpenbisSample] | None = Field(None, alias='samples')
    properties: Dict | None = None
    samples: List['OpenbisSample'] | None = None
    def create(self, ob: pybis.Openbis, space: 'OpenbisSpace', project: 'OpenbisProject'):
        col = ob.new_collection(self.type, code=f"{self.code}", project=project.path(), props=self.properties)
        try:
            col.save()
        except ValueError as e:
            col = ob.get_collection(self.path())
        # if self.children:
        #     for s in self.children:
        #         sp = s.create(ob, space, project, self)
        #         try:
        #             sp.save()
        #         except:
        #             pass
        if self.samples:
            for s in self.samples:
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

    @classmethod
    def from_openbis(cls, ob: pybis.Openbis, code: str) -> 'OpenbisCollection':
        coll = ob.get_collection(code)
        #children = [OpenbisSample.from_openbis(ob, ch.identifier) for ch in coll.get_objects().df.itertuples()]
        children = []
        return cls(code=coll.code, identifier=coll.identifier, perm_id=coll.permId, type=coll.type.code, samples=children, registrator=coll.registrator, properties=coll.props.all())
    
    def reflect(self, ob: pybis.Openbis) -> 'OpenbisCollection': 
        pass

class OpenbisProject(OpenbisTreeObject):
    """
    Class representing an openBis project
    """
    code: str
    description: str | None = None
    children: List[OpenbisCollection] | None = Field(None, alias='collections')
    space: str | None = None
    samples: List['OpenbisSample'] | None = None

    def create(self, ob: pybis.Openbis, parent: 'OpenbisSpace'):
        pr = ob.new_project(parent.code, self.code, description=self.description)
        try:
            pr.save()
        except:
            pass
        if self.children:
            for c in self.children:
                c.create(ob, parent, self)
        if self.samples:
            for c in self.samples:
                c.create(ob, parent, self)
    
    def get_ob_object(self, ob: pybis.Openbis) -> Project:
        return ob.get_project(self.path())

    @classmethod
    def from_openbis(cls, ob: pybis.Openbis, code: str):
        pr = ob.get_project(projectId=code)
        colls = [OpenbisCollection.from_openbis(ob, c.identifier) for c in  pr.get_collections().df.itertuples()]
        return cls(code=pr.code, perm_id=pr.permId, identifier=pr.identifier, space=pr.space.code, registrator=pr.registrator, collections=colls)

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
    samples: List['OpenbisSample'] | None = None

    def create(self, ob: pybis.Openbis):
        #Create space
        sp = ob.new_space(code=self.code)
        try:
            sp.save()
        except:
            sp = ob.get_space(code=self.code)
        #Create projects
        if self.children:
            for p in self.children:
                p.create(ob, self)
        #Create samples
        if self.samples:
            for c in self.samples:
                c.create(ob, self)

    def get_ob_object(self, ob: pybis.Openbis) -> Experiment:
        return ob.get_space(self.code)

    @classmethod
    def from_openbis(cls, ob: pybis.Openbis, code: str) -> 'OpenbisSpace':
        sp = ob.get_space(code)
        if sp:
            projects = sp.get_projects()
            if projects:
                projs = [OpenbisProject.from_openbis(ob, code = utils.split_identifier(pr.identifier)[-1]) for pr in projects.df.itertuples()]
            else:
                projs = None
            return cls(code=sp.code,perm_id=sp.permId, identifier=sp.permId, registrator=sp.registrator, projects=projs)

    def reflect(self, ob: pybis.Openbis) -> 'OpenbisSpace':
        sp = self.get_ob_object(ob)
        projects = sp.get_projects()
        projs = [OpenbisProject.from_openbis(ob, code = utils.split_identifier(pr.identifier)[-1]) for pr in projects.df.itertuples()]
        return OpenbisSpace(code=self.code, projects = [OpenbisProject(code = pr.code, perm_id=pr.permId, parent_id=self.parent_id + [self.code]).reflect(ob) for pr in projects.df.itertuples()], parent_id=self.parent_id)
 
class OpenbisProperty(OpenbisGenericObject):
    code: str
    perm_id: str | None = None
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
    
    def reflect(self, ob: pybis.Openbis) -> 'OpenbisProperty':
        pass
    def wipe(self, ob: pybis.Openbis):
        obj = self.get_ob_object(ob)
        obj.delete("Automatically deleted by {self.__class__}")

    @classmethod
    def from_openbis(cls, ob: pybis.Openbis, code: str) -> 'OpenbisProperty':
        pt:PropertyType = ob.get_property_type(code)
        return cls(code=code, perm_id=pt.permID, label=pt.label, data_type=pt.dataType, description=pt.description, children=[])


class OpenbisObjectType(OpenbisGenericObject):
    """
    An OpenBIS object type has codes, (optionally a prefix)
    """
    code: str
    perm_id: str | None = None
    prefix: str | None
    properties: Dict[str, List[str] | List[OpenbisProperty]] | None = {}
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
            if self.properties:
                for section, props in self.properties.items():
                    for prop in props:
                        match prop:
                            case OpenbisProperty(p):
                                prop.create(ob)
                                ot.assign_property(ob.get_property_type(prop.code), section=section)
                            case str(s):
                                ob.get_property_type(s)
                                ot.assign_property(prop, section=section)
                            case _:
                                pass
                        try:
                            ot.save()
                        except:
                            pass
        except:
            pass
    
    def get_ob_object(self, ob: pybis.Openbis) -> SampleType:
        return ob.get_object_type(self.code)
    
    def reflect(self, ob: pybis.Openbis) -> 'OpenbisObjectType':
        st = self.get_ob_object(ob)
        assignments = st.get_property_assignments()
        #Get assignment by section
        assignments_by_section = {k: [p.propertyType for p in v] for k,v in itertools.groupby(sorted(assignments.df.itertuples(),  key=lambda el: el.ordinal), lambda x: x.section)}
        #For each assignment, try to reflect the property if it does not yet exist
        return OpenbisObjectType(code = st.code, perm_id=st.permId, properties=assignments_by_section, autogenerate_code=st.autoGeneratedCode, prefix=st.generatedCodePrefix)
    
    @classmethod
    def from_openbis(cls, ob: pybis.Openbis, code:str):
        pass
    def wipe(self, ob: pybis.Openbis):
        obj = self.get_ob_object(ob)
        obj.delete(f"Automatically deleted by {self.__class__}")

class OpenbisCollectionType(OpenbisGenericObject):
    code: str
    description: str
    properties: List[str] | List[OpenbisProperty] | None = []

    def create(self, ob: pybis.Openbis):
        ot:ExperimentType = ob.new_collection_type(code = self.code, description= self.description)
        try:  
            ot.save()
        except ValueError:
            ot = ob.get_collection_type(self.code)
        breakpoint()
        try:
            match self.properties:
                case str(x), *rest:
                    for prop in self.properties:
                            ot.assign_property(prop)
                            ot.save()
                case OpenbisProperty(x), *rest:
                    for prop in self.properties:
                        breakpoint()
                        prop.create(ob)
                        ob_prop = prop.get_ob_object(ob)
                        ot.assign_property(ob_prop)
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

class OpenbisInstance(OpenbisTreeObject, OpenbisGenericObject):
    code: str = '/'
    children: List[OpenbisSpace] = Field([], alias='spaces') 
    object_types: List[OpenbisObjectType] | None = None
    collection_types: List[OpenbisCollectionType] | None = None
    properties: List[OpenbisProperty] | None = None
    dataset_types: List[OpenbisDatasetType] | None = None
    users: List[OpenbisUser] | None = None
    roles: List[OpenbisRoleAssignment] | None = None
    samples: List['OpenbisSample'] | None = Field([])

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
        for sp in self.samples:
            sp.wipe(ob)
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
        txt = self.json(indent=2, by_alias=True, exclude_unset=True)
        with open(path, 'w') as of:
            of.write(txt)
        
    @classmethod
    def reflect(cls, ob: pybis.Openbis) -> 'OpenbisInstance':
        """
        Given an openbis connection, try
        to reflect it as a object of type OpenbisInstance
        """
        #Get all property types
        property_types = [OpenbisProperty(code=p.code, label=p.label, data_type=p.dataType, description=p.description) for p in get_non_system_entities(ob, "property_types")]
        #Get all Object types
        object_types = [OpenbisObjectType(code=ot.code, prefix=ot.generatedCodePrefix).reflect(ob) for ot in get_non_system_entities(ob, "object_types")]

        #Get all collection types
        collection_types = [OpenbisCollectionType(code=p.code, description=p.description) for p in get_non_system_entities(ob, "collection_types")]
        #Get all the tree
        spaces = [OpenbisSpace.from_openbis(ob, code=sp.code)  for sp in ob.get_spaces().df.itertuples() if sp.code not in SACRED_SPACES]
        #Get all samples
        samples  = [*(OpenbisSample.get_all_objects(ob, st.code) for st in object_types)]
        #Reflect users
        users = [OpenbisUser(userid=ui.permId, first_name=ui.firstName, last_name=ui.lastName) for ui in ob.get_users().df.itertuples()]
        #Reflect role assignments
        roles = [OpenbisRoleAssignment(techid=ui.techId, role=ui.role, level=ui.roleLevel, user=ui.user, space=ui.space).reflect(ob) for ui in ob.get_role_assignments().df.itertuples()]
        #Create Instance
        inst = OpenbisInstance(spaces = spaces, object_types = object_types, collection_types = collection_types, properties = property_types, users=users, roles=roles)

        for samp in itertools.chain(*samples):
            key = utils.first_valid([samp.collection, samp.project, samp.space, '/'])
            sp = inst.find(key)
            if sp and key != '':
                sp.children.append(samp)
            elif  key == '':
                inst.samples.append(samp)
            else:
                pass

        return inst

    @root_validator(pre=False)
    def check_parent(cls, values):
        for el in ['children', 'samples']:
            if el in values.keys():
                if child:= values.get(el):
                    print(el)
                    for c in child:
                        print("IN", c.code)
                        c.parent_id = values.get('code')
                        children_validator(c, [values.get('code')])
        return values




def get_non_system_entities(ob: pybis.Openbis, type:str) -> List[SampleType | ExperimentType | PropertyType]:
    def df_selector(entities: Things, attribute: str, filter_registrator: bool, exclude_codes: List[str] | None = None) -> List[str]:
        if filter_registrator:
            df = entities.df[(entities.df.registrator != 'system')]
        else:
            df = entities.df
        return [e for e in df[attribute].unique() if e not in exclude_codes]
    def comp_selector(entities: Things, attribute: str, filter_registrator: bool, exclude_codes: List[str] | None = None) -> List[str]:
        return [e for e in list(set([getattr(e, attribute) for e in entities if (getattr(e, 'registrator') != 'system' if filter_registrator else True)])) if e not in exclude_codes]
    match type:
        case "object_types":
            selector = ob.get_object_types
            constructor = ob.get_object_type
            attribute = 'code'
            filter_registrator = False
            filter_fun = df_selector
            exclude_codes = SACRED_OBJECT_TYPES
        case "collection_types": 
            selector = ob.get_collection_types
            constructor = ob.get_collection_type
            attribute = 'code'
            filter_registrator = False
            filter_fun = df_selector
            exclude_codes = SACRED_COLLECTION_TYPES
        case "property_types":
            selector = ob.get_property_types
            constructor = ob.get_property_type
            attribute = 'code'
            filter_registrator = True
            filter_fun = df_selector
            exclude_codes = []
        case "spaces":
            selector = ob.get_spaces
            constructor = ob.get_space
            attribute = 'code'
            filter_registrator = True
            filter_fun = comp_selector
            exclude_codes = SACRED_SPACES
        case "roles":
            selector = ob.get_role_assignments
            constructor = ob.get_role_assignment
            attribute = 'techId'
            filter_registrator = False
        case _:
            raise ValueError(f"Not implemented for {type}")
    entities = selector()
    non_system_entities =  filter_fun(entities, attribute, filter_registrator, exclude_codes)
    return [constructor(e) for e in non_system_entities]

        