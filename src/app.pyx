from pydom import Element, div, a, span, p, main


class AwesomeCard(Element):
    button_value = 0

    def onclick(self):
        self.button_value += 1

    def build_children(self, props):
        self.children = [
            (<div class={"col s6"} style={dict(padding=2)}>
                <div class={"card blue-grey darken-1"}>
                    <div class="card-content white-text">
                        <span class={"card-title"}>
                            {f"{props.get('text')} {self.button_value}"}
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
    card_one_title = "Prop Title"

    def change_card_title(self):
        self.card_one_title = "Even More Epic Title"

    def build_children(self, props):
        self.children = [
            <main>
                <div class={"container"}>
                    <div class={"row"}>
                        <AwesomeCard text={self.card_one_title}/>
                        <AwesomeCard text={"Epic Prop Title"}/>
                    </div>
                </div>
                <div class={"row"}>
                    <a onclick={self.change_card_title} class={"waves-effect waves-light btn"} >
                        {"Change Card Text"}
                    </a>
                </div>
            </main>
        ]


class App(Element):
    def build_children(self, props):
        self.children = [(<EpicElement/>)]
