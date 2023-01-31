from pydom import Element, button, div


class EpicElement(Element):
    buttonValue = 0

    def onclick(self):
        self.buttonValue += 1

    @property
    def children(self):
        return [div(style={"background-color": "#38C", "height": "52px"})(
            button(style={'color': 'blue'}, onclick=self.onclick)(self.buttonValue))]


class App(Element):
    @property
    def children(self):
        return [EpicElement()]
