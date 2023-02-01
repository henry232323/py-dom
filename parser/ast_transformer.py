import sys

import astpretty as astpretty
from lark import ast_utils, Transformer

from parser.python_parser import chosen_parser

this_module = sys.modules[__name__]

#
#   Define AST
#

import ast

DEBUG = False


def debug(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)


class ToAst(Transformer):
    # Define extra transformation functions, for rules that don't correspond to an AST class.
    def var(self, s):
        debug(2, s)
        return s[0]

    def number(self, s):
        debug('number', s)
        return ast.parse(s[0].value, mode='eval')

    def name(self, s):
        debug(2.5, s)
        return s[0].value

    def assign_stmt(self, s):
        debug(1, s)
        return ast.Assign([s[0].children[0]], s[0].children[1])

    def singhtmltag(self, s):
        debug(4, s)
        if len(s) == 1:
            return ast.Call(ast.Call(s[0], [], []), [], [])

    def htmltag(self, s):
        debug(5, s)
        if len(s) == 3:
            if s[0].id != s[2].id:
                raise SyntaxError(f"Unmatch tag <{s[0].id}>")
            return ast.Call(ast.Call(s[0], [], []), [s[1]], [])

    def expr_stmt(self, s):
        debug(3, s)
        return ast.Expr(s[0])

    def file_input(self, s):
        debug("module", s)
        return ast.Module(s, [])

    def import_from(self, s):
        debug("Import from", s)
        return ast.ImportFrom(s[0], s[1], 0)

    def import_stmt(self, s):
        debug("Import", s)
        if isinstance(s[0], ast.ImportFrom):
            return s[0]
        else:
            return ast.Import(s[0])

    def dotted_name(self, s):
        debug("dotted name", s)
        return s[0]

    def import_as_names(self, s):
        debug("as names", s)
        return s

    def import_as_name(self, s):
        debug("as name", s)
        alias = ast.alias(s[0], s[1])
        ast.fix_missing_locations(alias)
        return alias

    def stmt(self, s):
        ast.fix_missing_locations(s[0])
        return s[0]

    def dotted_as_name(self, s):
        debug("dotted as name", s)
        alias = ast.alias(s[0], s[1])
        ast.fix_missing_locations(alias)
        return alias

    def dotted_as_names(self, s):
        debug("dotted as names", s)
        return s

    def import_name(self, s):
        debug("import name", s)
        return s[0]

    def classdef(self, s):
        print("class def", s)
        return ast.ClassDef(
            s[0],
            [x for x in s[1] if not isinstance(x, ast.keyword)],
            [x for x in s[1] if isinstance(x, ast.keyword)],
            [],
            s[2]
        )

    def arguments(self, s):
        print("arguments", s)
        return s

    def suite(self, s):
        return s

    def argvalue(self, s):
        return ast.keyword(s[0], ast.Name(s[1], ast.Load))

    def funcdef(self, s):
        print("funcdef", s)
        return ast.FunctionDef(s[0], s[1], s[2])

    def starparams(self, s):
        print("starparams", s)
        return s

    def starparam(self, s):
        print("starparam", s)
        return ast.arg(s[0])

    def poststarparams(self, s):
        print("poststarparams", s)
        return s

    def paramvalue(self, s):
        return s[1]

    def parameters(self, s):
        print("params", s)
        posargs = [ast.arg(x) for x in s if isinstance(x, str)]
        keywords = [x for x in s if isinstance(x, ast.keyword)]
        return ast.arguments(
            [],
            posargs,
            [], # todo: all arg flavors
            [],
            [],
            [],
            keywords,
        )

#
#   Define Parser
#

parser = chosen_parser

transformer = ast_utils.create_transformer(this_module, ToAst())


def parse(text):
    tree = parser.parse(text)
    return transformer.transform(tree)


#
#   Test
#
import astunparse

if __name__ == '__main__':
    source = '''

@balls
class AwesomeCard(Element, Elemnt2, a=b):
    buttonValue = 0

    def onclick(self, *args, k=5, f, d=5, **kwargs,):
        self.buttonValue += 1
'''
    '''
    
    """
    <div class="col s6">asd</div>
    """
    @property
    def children(self):
        return div(_class="col s6")(
            div(_class="card blue-grey darken-1")(
                div(_class="card-content white-text")(
                    span(_class="card-title")(f"Card Title {self.buttonValue}"),
                    p()("I am a very simple card. I am good at containing small bits of information. "
                        "I am convenient because I require little markup to use effectively."),
                ),
                div(_class="card-action")(
                    a(onclick=self.onclick, _class="waves-effect waves-light btn")("Increment me!"),
                )
            ),
        )
        '''
    print(astpretty.pprint(ast.parse(source)))
    tree = parse(source)

    ast.fix_missing_locations(tree)
    astpretty.pprint(tree)
    print(astunparse.unparse(tree))
