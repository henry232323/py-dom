import itertools
import sys

from lark import ast_utils, Transformer, Token

from .python_parser import chosen_parser

this_module = sys.modules[__name__]

#
#   Define AST
#

import ast

DEBUG = False


def debug(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)


def create_keywords(items):
    keywords = []
    for k, v in items:
        keywords.append(ast.keyword(k, v))

    return keywords


def gen_args(posonlyargs, args, vararg, kwonlyargs, kw_defaults, kwarg, defaults):
    try:
        return ast.arguments(posonlyargs, args, vararg, kwonlyargs, kw_defaults, kwarg, defaults)
    except:
        ast.arguments(args, vararg, kwonlyargs, kw_defaults, kwarg, defaults)


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
        s[0].s += s[1].s
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
            return ast.Assign([children[0]], children[1])

    def html_attr(self, s):
        debug("html_attr", s)
        if s[0] == "class":
            s[0] = "_class"

        item = s[1]
        if isinstance(item, str):
            item = ast.Name(item, ast.Load())
        if isinstance(item, ast.Call) and getattr(item, "is_htmltag", False):
            result = item
        elif isinstance(item, ast.Constant):
            result = item
        else:
            result = ast.Lambda(
                gen_args([], [], None, [], [], None, []),
                item
            )

        return s[0], result

    def singhtmltag(self, s):
        debug(4, s)
        result = None
        if len(s) == 1:
            result = ast.Call(ast.Name(s[0], ast.Load()), [], [])
        elif len(s) == 2:
            if (
                    s[1] and
                    not isinstance(s[1][0], list)
            ):
                s[1] = [s[1]]
            result = ast.Call(ast.Name(s[0], ast.Load()), [], create_keywords(s[1]))

        result.is_htmltag = True
        return result

    def inline_html_expr(self, s):
        debug('inline_html_expr', s)
        return ast.Lambda(gen_args([], [], None, [], [], None, []), s)

    def innerhtml_items(self, s):
        debug("innerhtml_items", s)
        return [ast.Name(item, ast.Load()) if isinstance(item, str) else item for item in s]

    def innerhtml(self, s):
        debug("innerhtml", s)
        return s

    def html_attrs(self, s):
        debug("html_attrs", s)
        return s

    @staticmethod
    def build_htmltag_body(items):
        result = []
        for item in items:
            if isinstance(item, str):
                item = ast.Name(item, ast.Load())
            if isinstance(item, ast.Call) and getattr(item, "is_htmltag", False):
                result.append(item)
            elif isinstance(item, ast.Constant):
                result.append(item)
            else:
                result.append(ast.Lambda(
                    gen_args([], [], None, [], [], None, []),
                    item
                ))
        return result

    def htmltag(self, s):
        debug(5, s)
        result = None
        if len(s) == 3:
            if s[0] != s[2]:
                raise SyntaxError(f"Unmatched tag <{s[0].id}>")
            result = ast.Call(
                ast.Call(ast.Name(s[0], ast.Load()), [], []),
                self.build_htmltag_body(s[1]),
                []
            )
        elif len(s) == 2:
            if s[0] != s[1]:
                raise SyntaxError(f"Unmatched tag <{s[0].id}>")
            result = ast.Call(ast.Call(ast.Name(s[0], ast.Load()), [], []), [], [])
        elif len(s) == 4:
            if s[0] != s[3]:
                raise SyntaxError(f"Unmatched tag <{s[0].id}>")
            if (s[1] and not isinstance(s[1], list)):
                s[1] = [s[1]]
            if not isinstance(s[2], list):
                s[2] = [s[2]]
            result = ast.Call(
                ast.Call(ast.Name(s[0], ast.Load()), [], create_keywords(s[1])),
                self.build_htmltag_body(s[2]),
                []
            )

        result.is_htmltag = True
        return result

    def expr_stmt(self, s):
        debug(3, s)
        return ast.Expr(s[0])

    def file_input(self, s):
        debug("module", s)
        return ast.Module(s)

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
        debug("arguments", s)
        return [ast.Name(arg, ast.Load()) if isinstance(arg, str) else arg for arg in s if arg]

    def suite(self, s):
        return s

    def argvalue(self, s):
        return ast.keyword(s[0], ast.Name(s[1], ast.Load()) if isinstance(s[1], str) else s[1])

    def return_stmt(self, s):
        return ast.Return(s[0])

    def funcdef(self, s):
        debug("funcdef", s)
        return ast.FunctionDef(s[0], s[1], s[3], s[2] or [], None)

    def starparams(self, s):
        debug("starparams", s)
        return [s[0]] + s[1]

    def starguard(self, s):
        return "*"

    def starparam(self, s):
        debug("starparam", s)
        return ('vararg', ast.arg(s[0]))

    def poststarparams(self, s):
        debug("poststarparams", s)
        return s

    def paramvalue(self, s):
        debug("paramvalue", s)
        return (ast.arg(s[0]), s[1])

    def parameters(self, s):
        debug("params 1", s)
        parts = [list(g) for k, g in itertools.groupby(s, type)]
        debug("params", parts)

        posonlyargs = []
        args = []
        vararg = None
        kwonlyargs = []
        kw_defaults = []
        kwarg = None
        defaults = []
        starred = False
        slashed = False
        while parts:
            part = parts.pop(0)
            if part == "*":
                starred = True
            if part and isinstance(part[0], list):
                parts = [list(g) for k, g in itertools.groupby(part[0], type)] + parts
                debug(parts)
            elif part and isinstance(part[0], Token):
                slashed = True
                posonlyargs.extend(args)
                args = []
            elif part and isinstance(part[0], str):
                if not starred:
                    args.extend(ast.arg(x) for x in part)
                else:
                    kwonlyargs.extend([ast.arg(c) for c in part])
                    kw_defaults.extend([None for c in part])
            elif part and isinstance(part[0], tuple):
                for key, val in part:
                    if isinstance(key, str):
                        if key == "vararg":
                            vararg = val
                        elif key == "kwarg":
                            kwarg = val
                        starred = True
                    else:
                        if starred:
                            kwonlyargs.append(key)
                            kw_defaults.append(val)
                        else:
                            args.append(key)
                            defaults.append(val)

        return gen_args(
            posonlyargs,
            args,
            vararg,  # todo: posonly
            kwonlyargs,
            kw_defaults,
            kwarg,
            defaults
        )

    def kwparams(self, s):
        debug('kwparams', s)
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
        return ast.Call(s[0], [x for x in s[1] if not isinstance(x, ast.keyword)],
                        [x for x in s[1] if isinstance(x, ast.keyword)])

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
    tree = parser.parse(text + "\n")
    transformed = transformer.transform(tree)
    ast.fix_missing_locations(transformed)
    return transformed


import autopep8
import astunparse


def transpile(source):
    tree = parse(source)
    ast.fix_missing_locations(tree)
    formatted = autopep8.fix_code(astunparse.unparse(tree))
    return formatted


def transpile_file(path, output_path):
    with open(path, 'r') as inputfile:
        with open(output_path, 'w') as outputfile:
            outputfile.write(transpile(inputfile.read()))
