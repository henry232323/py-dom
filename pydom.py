from functools import partial
import string
from functools import partial
import random
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


class Element(_h):
    first_render = False

    def __init__(self, _class='div', **attrs):
        self.tag = BuiltinElement(_class, **attrs, id=''.join(random.choices(string.ascii_lowercase, k=8)))
        self._init(**attrs)

    def _init(self, **attrs):
        pass

    @property
    def children(self):
        return []

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
