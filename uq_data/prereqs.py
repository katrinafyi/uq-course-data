from dataclasses import dataclass, field
from typing import List

from parsimonious.grammar import Grammar
from parsimonious.exceptions import ParseError

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

# https://math.stackexchange.com/questions/140036/why-is-this-parsing-expression-grammar-left-recursive
_grammar = Grammar('''
    prereq = expr eof

    expr = (parens!(and/or)) / basic_comma_list / basic_and_list / basic_or_list
    parens = '(' expr ')'
    
    basic_comma_list = course!(and/or) more_commas
    more_commas = (',' space course more_commas) / ''
    comma = "," / ";"

    basic_and_list = course!or more_ands
    more_ands = (and course more_ands) / ''
    and = space ("and" / "&" / "+") space

    basic_or_list = course more_ors
    more_ors = (or course more_ors) / '' 
    or = space ("or" / "|") space

    course = code / parens
    code = ~r"[A-Z]{3,5}[0-9]{3,4}[A-Z]?"

    space = ~r"\\s+"

    eof = !~"."

''')
def parse_prereq(prereq_string: str):     
    return _grammar.parse(prereq_string)

if __name__ == "__main__":
    with open('_prereqs.txt') as f:
        failures = 0
        total = 0
        for l in f:
            total += 1
            l = l.strip()
            try:
                result = parse_prereq(l)
            except ParseError as e:
                failures += 1
                print('## failed', l)
                print(e)
            else:
                # print(failures, 'failed.')
                print(result)
            print()
            if total == 2:
                pass
                # break

        print()
        print('failed:', failures, '/', total)