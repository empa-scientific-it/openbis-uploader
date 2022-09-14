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