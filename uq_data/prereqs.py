from dataclasses import dataclass, field
from typing import List

static_field = lambda name: field(default=name, init=False, repr=False, compare=False)

@dataclass
class PrereqNode:
    type_: str = static_field('node')
    pass

@dataclass 
class Relation(PrereqNode):
    type_: str = static_field('relation')
    children: list = field(default_factory=list, repr=False)

    def verify(self, courses):
        raise NotImplementedError

@dataclass 
class And(Relation):
    type_: str = static_field('and')

@dataclass 
class Or(Relation):
    type_: str = static_field('or')

@dataclass
class UnitsOf(Relation):
    type_: str = static_field('units')
    units: int = 0

@dataclass
class CourseNode(PrereqNode): 
    type_: str = static_field('course')
    course_code: str 
    units: float
    name: str

def pretty_string(node):
    return '\n'.join(_pretty_list(node))

def _pretty_list(node, depth=0):
    indent = '  '*depth
    if isinstance(node, Relation):
        s = []
        s.append(indent+str(node) + ':')
        for child in node.children:
            s.extend(x for x in _pretty_list(child, depth+1))
        return s
    else:
        return (indent+str(node), )
