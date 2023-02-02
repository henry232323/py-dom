from pydom import Element, div, a, span, p, main


class AwesomeCard(Element):
    buttonValue = 0

    def onclick(self):
        self.buttonValue += 1

    @property
    def children(self):
        return [
            (<div class={"col s6"} style={dict(padding=2)}>
                <div class={"card blue-grey darken-1"}>
                    <div class="card-content white-text">
                        <span class={"card-title"}>
                            {f"Card Title {self.buttonValue}"}
                        </span>
                        <p>
                            {"I am a very simple card. I am good at containing small bits of information. "
                            "I am convenient because I require little markup to use effectively."}
                        </p>
                    </div>
                    <div class={"card-action"}>
                        <a onclick={self.onclick} class={"waves-effect waves-light btn"}>
                            {"Increment me!"}
                        </a>
                    </div>
                </div>
            </div>)
        ]


class EpicElement(Element):

    @property
    def children(self):
        return [
            (<main>
                <div class={"container"}>
                    <div class={"row"}>
                        <AwesomeCard/>
                        <AwesomeCard/>
                    </div>
                </div>
            </main>)
        ]


class App(Element):
    @property
    def children(self):
        return [(<EpicElement/>)]
