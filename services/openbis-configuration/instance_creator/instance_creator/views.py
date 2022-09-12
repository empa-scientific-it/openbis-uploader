
from ast import Str
from re import S
import pybis
from typing import List, Generator, Dict, Optional, Any

from pydantic import BaseModel, fields
from dataclasses import dataclass
import enum

class OpenbisHierarcy(enum.Enum):
    OBJECT = "OBJECT"
    COLLECTION = "COLLECTION"
    PROJECT = "PROJECT"
    SPACE = "SPACE"
    UNKNOWN = "UNKNOWN"
    INSTANCE = "INSTANCE"


class TreeElement(BaseModel):
    """
    A class to (recursively) represent a tree element
    """
    id: str
    code: str | None = None
    permid: str | None = None
    type: OpenbisHierarcy | None = None
    attributes: Dict[str, Any] | None = None
    children: List['TreeElement'] | List[None] = fields.Field([])
    openbis_type: str | None = None

    def children_ids(self) -> List[str]:
        return [el.id for el in self.children] 
    
    def get(self, id: str) -> Optional['TreeElement']:
        if id in self.children_ids():
            return self.children[self.children_ids().index(id)]
        else:
            pass

    def push(self, el: 'TreeElement'):
        if el.id not in self.children_ids():
            self.children.append(el)
        else:
            pass
    
    def find(self, id: str) -> Optional['TreeElement']:
        result = []
        def inner_search(start: TreeElement, id: Str):
            if start.id == id:
                return start
            else:
                els =  [x for x in [inner_search(child, id) for child in start.children] if x is not None]
                if len(els) > 0:
                    return els[0]
        return inner_search(self, id)


class TreeElementObject(TreeElement):
    """
    Class derived from tree element
    but which additionally stores the collection 
    this object is attached as well as the relationship
    of this object to others
    """
    collection: str
    ancestors: List[str] | None = []
    descendants: List[str] | None = []

@dataclass
class OpenbisSampleInfo:
    """
    Class to hold the sample information 
    from an openbis sample list
    """
    identifier: List[str] | None
    code: str
    permid: str
    type: str
    space: List[str] | None
    project: List[str] | None
    collection: List[str] | None


def split_identifier(id: str, sep='/') -> List[str] | None:
    return list(filter(None, id.split(sep)))

def get_samples_with_info(ob: pybis.Openbis) -> List[List[str]]:
    """
    Get a list of all samples in an openbis instance,
    returns the list of paths for all objects
    """
    objs = ob.get_objects(attrs=['space', 'experiment', 'project', 'code', 'type', "permId"])
    paths = [
        OpenbisSampleInfo(split_identifier(o.identifier), o.code, o.permId, o.type, split_identifier(o.space), split_identifier(o.project), split_identifier(o.experiment)) for o in objs.df.itertuples()
    ]
    return paths

def path_to_openbis_type(path: List[str]) -> OpenbisHierarcy:
    """
    Given the depth in the sample tree of a sample, return the corresponding
    type
    """
    match path:
        case str(x), str(y), str(z):
            res = OpenbisHierarcy.SPACE
        case str(x), str(y):
            res = OpenbisHierarcy.PROJECT
        case str(x), *rest if rest is None:
            res = OpenbisHierarcy.OBJECT
        case _:
            res = OpenbisHierarcy.UNKNOWN
    return res


def tree_builder(paths: List[OpenbisSampleInfo]) -> TreeElement:
    """
    Given a list of lists of `OpenbisSampleInfo` builds
    a tree representation (using `pydantic.BaseModel` as a base class)
    of the tree
    """
    def recurse_setdefault(array: List[str] | str, res: TreeElement):
        print(array)
        path_type = path_to_openbis_type(array)
        match array:
            #Leaf
            case str(x):
                if x in res.children_id():
                    return
                else:
                    res.push(TreeElement(id=x, children=[], type=path_type))
            case str(x), *rest:
                if x not in res.children_ids():
                    res.push(TreeElement(id=x, children=[],  type=path_type))
                recurse_setdefault(rest, res.get(x))
    tree = TreeElement(id='/', children = [], type=OpenbisHierarcy.INSTANCE)
    for p in paths:
        recurse_setdefault(p.identifier, tree)
    return tree


def build_sample_tree_from_list(ob: pybis.Openbis) -> TreeElement:
    base_tree = TreeElement(id='/', code='/', type=OpenbisHierarcy.INSTANCE)
    #Add spaces
    for space in ob.get_spaces().df.itertuples():
        base_tree.push(TreeElement(id=space.code, code=space.code, permid=space.code, type=OpenbisHierarcy.SPACE))
    #Add projects
    for proj in ob.get_projects():
        base_tree.get(id=proj.space.code).push(TreeElement(id=proj.identifier, code=proj.code, permid=proj.permId, type=OpenbisHierarcy.PROJECT))
    #Add collections
    for coll in ob.get_collections(attrs=['project', 'space', 'code', 'type']).df.itertuples():
        base_tree.get(coll.space).get(coll.project).push(TreeElement(id=coll.identifier, code=coll.code, permid=coll.permId, type=OpenbisHierarcy.COLLECTION, openbis_type=coll.type))
    #Add objects
    for samp in ob.get_objects(attrs=['project', 'space', 'code', 'experiment', 'type', "children", 'parents']).df.itertuples():
        proj = base_tree.find(samp.project)
        if proj:
            proj.push(TreeElementObject(id=samp.identifier, code=samp.code, permid=samp.permId, 
            collection=samp.experiment, type=OpenbisHierarcy.OBJECT, openbis_type=samp.type, ancestors=samp.parents, descendants=samp.children))
    return base_tree

def build_sample_tree(ob: pybis.Openbis) -> TreeElement:
    sample_info = get_samples_with_info(ob)

    return tree_builder(sample_info)

