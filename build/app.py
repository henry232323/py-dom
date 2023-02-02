
from pydom import Element, div, a, span, p, main


class AwesomeCard(Element):
    buttonValue = 0

    def onclick(self):
        self.buttonValue += 1

    def _init(self, **props):
        self.children = [div(_class='col s6', style=(lambda: dict(padding=2)))(div(_class='card blue-grey darken-1')(div(_class='card-content white-text')(span(_class='card-title')((lambda: f'Card Title {self.buttonValue}')), p()(
            'I am a very simple card. I am good at containing small bits of information. I am convenient because I require little markup to use effectively.')), div(_class='card-action')(a(onclick=(lambda: self.onclick), _class='waves-effect waves-light btn')('Increment me!'))))]


class EpicElement(Element):

    def _init(self, **props):
        self.children = [main()(div(_class='container')(
            div(_class='row')(AwesomeCard(), AwesomeCard())))]


class App(Element):

    def _init(self, **props):
        self.children = [EpicElement()]
