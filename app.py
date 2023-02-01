from pydom import Element, div, a, span, p, main


class AwesomeCard(Element):
    buttonValue = 0

    def onclick(self):
        self.buttonValue += 1

    """
    <div class="col s6">asd</div>
    """

    @property
    def children(self):
        return div(_class="col s6")(
            div(_class="card blue-grey darken-1")(
                div(_class="card-content white-text")(
                    span(_class="card-title")("Card Title"),
                    p()("I am a very simple card. I am good at containing small bits of information. "
                        "I am convenient because I require little markup to use effectively."),
                ),
                div(_class="card-action")(
                    a(onclick=self.onclick, _class="waves-effect waves-light btn")("Increment me!"),
                )
            ),
        )


class EpicElement(Element):

    @property
    def children(self):
        return [
            main()(
                div(
                    _class="container"
                )(
                    div(_class="row")(
                        AwesomeCard(),
                        AwesomeCard(),
                    )
                ),
            )
        ]


class App(Element):
    @property
    def children(self):
        return [EpicElement()]
