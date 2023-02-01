import sys

import astpretty as astpretty
from lark import ast_utils, Transformer

from python_parser import chosen_parser

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
        return ast.parse(s[0].value, mode='eval').body
    def string(self, s):
        debug('string', s)
        return ast.parse(s[0].value, mode='eval').body
    def string_concat(self, s):
        debug('string', s)
        s[0].value += s[1].value
        return s[0]

    def name(self, s):
        debug(2.5, s)
        return s[0].value

    def assign_stmt(self, s):
        debug(1, s)
        tree = s[0]
        children = tree.children
        if isinstance(children[0], (ast.Attribute, ast.List, ast.Tuple)):
            children[0].ctx = ast.Store()
        if isinstance(children[0], str):
            children[0] = ast.Name(children[0], ast.Store())

        ops = {"+=": ast.Add, "-=": ast.Sub, "*=": ast.Mult, "/=": ast.Div, "//=": ast.FloorDiv, "**=": ast.Pow, }

        if len(children) == 3:
            return ast.AugAssign(children[0], ops[children[1][1]](), children[2])
        else:
            return ast.Assign([children[0]], children[1], None)

    def singhtmltag(self, s):
        debug(4, s)
        if len(s) == 1:
            return ast.Call(ast.Call(s[0], [], []), [], [])

    def htmltag(self, s):
        print(5, s)
        if len(s) == 3:
            if s[0] != s[2]:
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
        debug("class def", s)
        return ast.ClassDef(
            s[0],
            [x for x in s[1] if not isinstance(x, ast.keyword)],
            [x for x in s[1] if isinstance(x, ast.keyword)],
            s[2],
            []
        )

    def arguments(self, s):
        print("arguments", s)
        return [ast.Name(arg, ast.Load()) if isinstance(arg, str) else arg for arg in s if arg]

    def suite(self, s):
        return s

    def argvalue(self, s):
        return ast.keyword(s[0], ast.Name(s[1], ast.Load()) if isinstance(s[1], str) else s[1])

    def return_stmt(self, s):
        return ast.Return(s[0])
    def funcdef(self, s):
        debug("funcdef", s)
        return ast.FunctionDef(s[0], s[1], s[3], s[2], None, None)

    def starparams(self, s):
        debug("starparams", s)
        return ('starparams', s)

    def starparam(self, s):
        debug("starparam", s)
        return ('vararg', ast.arg(s[0]))

    def poststarparams(self, s):
        debug("poststarparams", s)
        return ('kwargs', s)

    def paramvalue(self, s):
        debug("paramvalue", s)
        return (ast.arg(s[0]), s[1])

    def parameters(self, s):
        debug("params", s)
        posonlyargs = []
        args = []
        vararg = None
        kwonlyargs = []
        kw_defaults = []
        kwarg = None
        defaults = []
        for item in s:
            if isinstance(item, str):
                args.append(ast.arg(item))
            elif isinstance(item, tuple):
                name, starparams = item
                assert name == 'starparams'
                for subname, value in starparams:
                    if subname == 'vararg':
                        vararg = value
                    elif subname == 'kwargs':
                        for kw in value:
                            if isinstance(kw, tuple):
                                if isinstance(kw[1], ast.arg):
                                    kwarg = kw[1]
                                else:
                                    kwonlyargs.append(kw[0])
                                    kw_defaults.append(kw[1])
                            elif isinstance(kw, str):
                                kwonlyargs.append(ast.arg(kw))
                                kw_defaults.append(None)
                    else:
                        raise SyntaxError(f"How did this happen {subname}")

        return ast.arguments(
            posonlyargs,
            args,
            vararg,  # todo: posonly
            kwonlyargs,
            kw_defaults,
            kwarg,
            defaults
        )

    def kwparams(self, s):
        return ('kwarg', ast.arg(s[0]))

    def decorated(self, s):
        debug("decorated", s)
        [decorators, cls] = s
        cls.decorator_list = decorators
        return cls

    def decorator(self, s):
        debug("decorator", s)
        return (ast.Name(s[0], ast.Load()) if isinstance(s[0], str) else s[0])

    def decorators(self, s):
        debug("decorators", s)
        return s

    def getattr(self, s):
        debug('getattr', s)
        if isinstance(s[0], str):
            s[0] = ast.Name(s[0], ast.Load())
        return ast.Attribute(s[0], s[1], ast.Load())

    def augassign_op(self, s):
        debug("augassign_op", s)
        return ('augassign_op', s[0].value)

    def funccall(self, s):
        debug("funccall", s)
        if isinstance(s[0], str):
            s[0] = ast.Name(s[0], ast.Load())
        if not s[1]:
            s[1] = []
        return ast.Call(s[0], [x for x in s[1] if not isinstance(x, ast.keyword)], [x for x in s[1] if isinstance(x, ast.keyword)])

    def list(self, s):
        return ast.List(s, ast.Load())
    def tuple(self, s):
        return ast.Tuple(s, ast.Load())
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
import autopep8

if __name__ == '__main__':
    source = '''
<a>
    <b/>
</a>
'''



    # print(astpretty.pprint(ast.parse(source)))
    tree = parse(source)
    ast.fix_missing_locations(tree)
    astpretty.pprint(tree)
    compile(tree, "<ast>", "exec")
    try:
        compile(tree, "<ast>", "exec")
    except Exception as e:
        print(e)
    print(autopep8.fix_code(astunparse.unparse(tree)))
