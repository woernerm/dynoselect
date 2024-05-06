import reflex as rx
from reflex_dynoselect import dynoselect, dynotimezone, dynolanguage

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
        dynoselect(
            options,
            placeholder="Select a color",
            search_placeholder="Search for a color..."
        ),
        dynotimezone(
            "de",
            placeholder="Zeitzone", 
            search_placeholder="Zeitzone suchen..."
        ),
        dynolanguage(
            placeholder="Sprache", 
            search_placeholder="Sprache suchen..."
        )
    )

# Add state and page to the app.
app = rx.App(

)
app.add_page(index)
