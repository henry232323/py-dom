# (c) 2020 Niklas Fiekas <niklas.fiekas@backscattering.de>
#
# Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
# https://www.apache.org/licenses/LICENSE-2.0> or the MIT license <LICENSE-MIT
# or https://opensource.org/licenses/MIT>, at your option. This file may not be
# copied, modified, or distributed except according to those terms.

"""A tiny library to safely render compact HTML5 from Python expressions."""

from __future__ import annotations

__version__ = "1.2.0"  # Remember to update setup.py
__author__ = "Niklas Fiekas"
__all__ = [
    "Frag", "SupportsRender", "Attribute",
    "render_into", "render",
    "h", "raw", "frag", "html",
]

import abc
from html import escape
from inspect import ismethod
from typing import Union, Dict, Iterable, List, Tuple

import cssutils

cssutils.ser.prefs.useMinified()


class Frag(abc.ABC):
    @abc.abstractmethod
    def render_into(self, builder: List[str]) -> None:
        ...

    def render(self) -> str:
        return render(self)

    _repr_html_ = __str__ = render

    def __repr__(self) -> str:
        return f"raw({self.render()!r})"


SupportsRender = Union[str, int, Frag, None, Iterable[Union[str, int, Frag, None]]]


def render_into(frag: SupportsRender, builder: List[str]) -> None:
    if callable(frag):
        frag = frag()
    if frag is None:
        return
    elif isinstance(frag, str):
        builder.append(escape(frag, quote=False))
    elif isinstance(frag, Frag):
        frag.render_into(builder)
    elif isinstance(frag, bytes):
        raise TypeError(f"cannot render bytes as html: {frag!r}")
    elif hasattr(frag, "__iter__"):
        for c in frag:  # type: ignore
            render_into(c, builder)
    else:
        builder.append(escape(str(frag), quote=False))


def render(frag: SupportsRender) -> str:
    builder: List[str] = []
    render_into(frag, builder)
    return "".join(builder)


Attribute = Union[str, int, bool, Iterable[Union[str, int, None]], Dict[str, bool], None]


class h(Frag):
    def __init__(self, __name: str, **attrs: Attribute) -> None:
        # See "Tag name" in
        # https://www.w3.org/TR/html52/syntax.html#writing-html-documents-elements.
        if not (__name and __name.isascii() and __name.isalnum()):
            raise ValueError(f"invalid html tag: {__name!r}")
        self.name = __name

        self.attrs = attrs

    def render_into(self, builder: List[str]) -> None:
        builder.append("<")
        builder.append(self.name)
        for attr, value in self.attrs.items():
            attr, value = _normalize_attr(attr, value)
            if value is False or value is None:
                # Falsy boolean attributes are omitted altogether:
                # https://www.w3.org/TR/html52/infrastructure.html#sec-boolean-attributes
                continue
            elif value is True:
                # Use the empty string as the value for truthy boolean
                # attributes:
                # https://www.w3.org/TR/html52/infrastructure.html#sec-boolean-attributes
                value = ""
            elif isinstance(value, str):
                pass
            elif isinstance(value, bytes):
                raise TypeError(f"cannot render bytes as html attribute: {value!r}")
            elif hasattr(value, "__iter__"):
                if isinstance(value, dict):
                    value = " ".join(key for key, val in value.items() if val)
                else:
                    value = " ".join(str(val) for val in value if val is not None)  # type: ignore
                if not value:
                    # Omit attributes with empty lists or dictionaries entirely.
                    continue
            else:
                value = str(value)

            # Attribute name is normalized/validated in constructor.
            builder.append(" ")
            builder.append(attr)

            # Attribute value syntax:
            # https://www.w3.org/TR/html52/syntax.html#elements-attributes
            if not value:
                # If the value is an empty string, use empty attribute syntax.
                continue
            else:
                # Double-quoted attribute value syntax. No need to escape
                # single quotes, as quote=True would do:
                # https://github.com/python/cpython/blob/v3.9.0/Lib/html/__init__.py#L12-L25
                builder.append("=\"")
                builder.append(escape(value, quote=False).replace("\"", "&quot;"))
                builder.append("\"")
        builder.append(">")

    def __call__(self, *children: SupportsRender) -> _h:
        return _h(self, children)


class _h(Frag):
    def __init__(self, tag: h, children: Tuple[SupportsRender, ...]) -> None:
        self.tag = tag
        self.children = children

    def render_into(self, builder: List[str]) -> None:
        if self.tag is not None:
            self.tag.render_into(builder)
        for child in self.children:
            render_into(child, builder)

        if self.tag is not None:
            builder.append("</")
            builder.append(self.tag.name)
            builder.append(">")


class raw(Frag):
    def __init__(self, html: str) -> None:
        self.html = html

    def render_into(self, builder: List[str]) -> None:
        builder.append(self.html)


class frag(Frag):
    def __init__(self, *children: SupportsRender):
        self.children = children

    def render_into(self, builder: List[str]) -> None:
        for child in self.children:
            render_into(child, builder)


class html(h):
    def __init__(self, **attrs: Attribute) -> None:
        super().__init__("html", **attrs)

    def render_into(self, builder: List[str]) -> None:
        builder.append("<!DOCTYPE html>")
        super().render_into(builder)


def convert_style(value: dict):
    rule = cssutils.css.CSSStyleDeclaration()
    for key, value in value.items():
        rule.setProperty(key, value)

    return rule.cssText


# callbacks = weakref.WeakValueDictionary()
callbacks = dict()


def convert_function(value: callable):
    target = id(value)
    callbacks[target] = value
    return f"gen_callback({target})()"


def gen_callback(ident):
    return callbacks.get(ident, "null")


def _normalize_attr(attr: str, value) -> (str, str):
    if callable(value):
        value = value()
    if attr in ("klass", "_class"):
        return "class", value

    if "_" in attr:
        attr = attr.rstrip("_").replace("_", "-")

    if attr == "style":
        value = convert_style(value)

    if callable(value):
        value = convert_function(value)


    # Slightly more restrictive than "Attribute names" in
    # https://www.w3.org/TR/html52/syntax.html#elements-attributes.
    if not (attr and attr.isascii() and all(ch.isalnum() or ch == "-" for ch in attr)):
        raise ValueError(f"invalid html attribute name: {attr!r}")

    return attr, value

class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

    def __getattribute__(self, item):
        attr = super().__getattribute__(item)
        if callable(attr) and not ismethod(attr):
            return attr()
        return attr

    def get(self, key):
        attr = super().get(key)
        if callable(attr) and not ismethod(attr):
            return attr()
        return attr