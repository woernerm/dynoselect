import reflex as rx
from reflex_dynoselect import dynotimezone, dynoselect
from reflex_dynoselect.options import TimezoneOptions

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

tmp = dynotimezone(
    "de-DE",
    placeholder="Select a timezone",
    search_placeholder="Search for a timezone",
)

def index() -> rx.Component:
    return rx.center(
        rx.theme_panel(),
        tmp
        # dynoselect(
        #     TimezoneOptions("de-DE"), 
        #     placeholder="Select a color", 
        #     search_placeholder="Search for a color"
        # )
    )

# Add state and page to the app.
app = rx.App(

)
app.add_page(index)
