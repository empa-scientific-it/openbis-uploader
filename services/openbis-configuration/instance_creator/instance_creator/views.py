
import pybis
from typing import List, Generator, Dict, Optional, Any

from pydantic import BaseModel, fields
from dataclasses import dataclass


class TreeElement(BaseModel):
    id: str
    attributes: Dict[str, Any] | None = None
    children: List['TreeElement'] | List[None] = fields.Field([])

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



def get_samples_with_info(ob: pybis.Openbis) -> List[List[str]]:
    objs = ob.get_objects(attrs=['space', 'experiment', 'project', 'code', 'type'])
    paths = [o.split('/') for o in objs.df.identifier.to_list()]
    return paths


def tree_builder(paths: List[List[str]]) -> TreeElement:
    """
    Given a list of lists of sample paths [/a/b/c,[/c/d/e] builds
    a tree representation (using `pydantic.BaseModel` as a base class)
    of the tree
    """
    def recurse_setdefault(array: List[str] | str, res: TreeElement):

        match array:
            #Leaf
            case str(x) if x != '':
                res.push(TreeElement(id=x, children=[]))
            case str(x), *rest:
                if x not in res.children_ids():
                    res.push(TreeElement(id=x, children=[]))
                recurse_setdefault(rest, res.get(x))
    tree = TreeElement(id='', children = [])
    for p in paths:
        recurse_setdefault(p, tree)
    return tree


def build_sample_tree(ob: pybis.Openbis) -> TreeElement:
    return tree_builder(get_samples_with_info(ob))