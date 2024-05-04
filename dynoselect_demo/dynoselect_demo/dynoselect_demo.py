import reflex as rx
from reflex_dynoselect import dynoselect, dynotimezone

options = [
    {"value": "ocean", "label": "Ocean", "keywords": ["blue", "water"]},
    {"value": "blue", "label": "Blue"},
    {"value": "purple", "label": "Purple"},
    {"value": "green", "label": "Green"},
    {"value": "red", "label": "Red"},
    {"value": "strange", "label": "Yellow"},
]

class State(rx.State):
    """The app state."""
    pass

def index() -> rx.Component:
    return rx.center(
        rx.theme_panel(),
        dynotimezone(
            "de",
            placeholder="Zeitzone", 
            search_placeholder="Zeitzone suchen..."
        )
    )

# Add state and page to the app.
app = rx.App(

)
app.add_page(index)
