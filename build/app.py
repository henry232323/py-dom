
from pydom import Element, div, a, span, p, main


class AwesomeCard(Element):
    button_value = 0

    def onclick(self):
        self.button_value += 1

    def build_children(self, **props):
        self.children = [div(_class='col s6', style=(lambda: dict(padding=2)))(div(_class='card blue-grey darken-1')(div(_class='card-content white-text')(span(_class='card-title')((lambda: f"{props.get('text')} {self.button_value}")), p()(
            'I am a very simple card. I am good at containing small bits of information. I am convenient because I require little markup to use effectively.')), div(_class='card-action')(a(onclick=(lambda: self.onclick), _class='waves-effect waves-light btn')('Increment me!'))))]


class EpicElement(Element):
    card_one_title = 'Prop Title'

    def change_card_title(self):
        self.card_one_title = 'Even More Epic Title'

    def build_children(self, **props):
        self.children = [main()(div(_class='container')(div(_class='row')(AwesomeCard(text=(lambda: self.card_one_title)), AwesomeCard(
            text='Epic Prop Title'))), div(_class='row')(a(onclick=(lambda: self.change_card_title), _class='waves-effect waves-light btn')('Change Card Text')))]


class App(Element):

    def build_children(self, **props):
        self.children = [EpicElement()]
