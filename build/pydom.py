import random
import string
from functools import partial
from typing import List

import js

from tinyhtml import h, _h


class BuiltinElement(h):
    def __new__(cls, __name: string, **attrs):
        return h(__name, **attrs)


button = partial(BuiltinElement, "button")
div = partial(BuiltinElement, "div")
h6 = partial(BuiltinElement, "h6")
h5 = partial(BuiltinElement, "h5")
h4 = partial(BuiltinElement, "h4")
h3 = partial(BuiltinElement, "h3")
h2 = partial(BuiltinElement, "h2")
h1 = partial(BuiltinElement, "h1")
a = partial(BuiltinElement, "a")
span = partial(BuiltinElement, "span")
p = partial(BuiltinElement, "p")
main = partial(BuiltinElement, "main")


class Element(_h):
    first_render = False

    def __init__(self, *, _class='div', **attrs):
        super().__init__(
            BuiltinElement(_class, **attrs, id=''.join(random.choices(string.ascii_lowercase, k=8))),
            tuple()
        )
        self.build_children(**attrs)

    def build_children(self, **attrs):
        self.children = [

        ]

    def __setattr__(self, key, value):
        if getattr(self, key, None) != value:
            fr = self.first_render
            super().__setattr__(key, value)
            if fr:
                self.render_tree()

    def render_root(self):
        if not self.first_render:
            self.first_render = True
        div = js.document.getElementById('root')
        html = self.render()
        div.innerHTML = html

    def render_tree(self):
        if not self.first_render:
            self.first_render = True
        ident = self.tag.attrs.get('id')
        div = js.document.getElementById(ident)
        html = self.render()
        div.innerHTML = html

    def render_into(self, builder: List[str]) -> None:
        super().render_into(builder)
        self.first_render = True
