
from typing import List
from dataclasses import dataclass

@dataclass
class TreeObject:
    code: str
    children: List['TreeObject'] | None

def children_validator(values: TreeObject, stack: List[str]):
    """
    This recursive function visits the openbis object tree
    and pushes down the list of path component
    to the children object. In this way, every object receives
    the its full path at creation time
    """
    #breakpoint()
    print(values.code, stack)
    if values.children:  
        for child in values.children:
            # if child.code:
            #     path = [*stack, values.code]
            # else:
            #     path = stack
            path = [*stack, values.code]
            child.parent_id = path
            children_validator(child, path)
    else:
        values.parent_id = stack