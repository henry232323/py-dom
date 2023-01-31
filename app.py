from pydom import Element, div, a, span, p


class EpicElement(Element):
    buttonValue = 0

    def onclick(self):
        self.buttonValue += 1

    @property
    def children(self):
        return [
            div(
                style={
                    "background-color": "#888",
                    "padding-top": "12px",
                    "padding-bottom": "12px",
                    "padding-left": "12px",
                    "padding-right": "12px",
                    "width": "100%",
                    "display": "flex",
                    "justifyContent": "center",
                    "alignItems": "center"
                })(
                div(_class="card blue-grey darken-1")(
                    div(_class="card-content white-text")(
                        span(_class="card-title")("Card Title"),
                        p()("I am a very simple card. I am good at containing small bits of information. "
                            "I am convenient because I require little markup to use effectively."),
                    ),
                    div(_class="card-action")(
                        a(href="#", onclick=self.onclick)(self.buttonValue),
                        a(href="#")("This is a link"),
                    )
                ),
            ),
        ]


class App(Element):
    @property
    def children(self):
        return [EpicElement()]
