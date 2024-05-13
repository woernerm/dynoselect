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
    return rx.vstack(
        rx.theme_panel(),
        rx.vstack(
            rx.heading("Basic Component", size="4"),
            rx.vstack(
                rx.heading("Search", size="2"),
                dynoselect(
                    options,
                    placeholder="Select a color",
                    search_placeholder="Search for a color...",
                ),
                direction="column",
                align="center",
                spacing="3"
            ),
            rx.vstack(
                rx.heading("Create Missing Option", size="2"),
                dynoselect(
                    options,
                    placeholder="Select a color",
                    search_placeholder="Search for a color...",
                    create_option={"value": "custom", "label": 'Create "{}"'}
                ),
                direction="column",
                align="center",
                spacing="3"
            ),
            rx.vstack(
                rx.heading("With Icon", size="2"),
                dynoselect(
                    options,
                    placeholder="Select a color",
                    search_placeholder="Search for a color...",
                    icon="palette"
                ),
                direction="column",
                align="center",
                spacing="3"
            ),
            spacing="4",
            align="center",
        ),
        rx.vstack(
            rx.heading("Localized Components", size="4"),
            rx.vstack(
                rx.heading("Autonyms", size="2"),
                rx.flex(
                    dynolanguage(
                        placeholder="Language", 
                        search_placeholder="Search for a language..."
                    ),
                    direction="row",
                    align="center",
                    spacing="2"
                ),
                rx.heading("Locales filtered in advance", size="2"),
                rx.flex(
                    dynolanguage(
                        placeholder="Language", 
                        search_placeholder="Search for a language...",
                        only={"de", "en", "en-GB", "es", "fr", "fr-CH"},
                        height="10rem"
                    ),
                    direction="row",
                    align="center",
                    spacing="2"
                ),
                rx.heading("Locale en", size="2"),
                rx.flex(
                    dynotimezone(
                        "en",
                        placeholder="Timezone", 
                        search_placeholder="Search timezone..."
                    ),
                    dynolanguage(
                        "en",
                        placeholder="Language", 
                        search_placeholder="Search for a language..."
                    ),
                    direction="row",
                    align="center",
                    spacing="2"
                ),
                rx.heading("Locale de", size="2"),
                rx.flex(
                    dynotimezone(
                        "de",
                        placeholder="Zeitzone", 
                        search_placeholder="Zeitzone suchen..."
                    ),
                    dynolanguage(
                        "de",
                        placeholder="Sprache", 
                        search_placeholder="Sprache suchen..."
                    ),
                    direction="row",
                    align="center",
                    spacing="2"
                ),
                rx.heading("Locale fr", size="2"),
                rx.flex(
                    dynotimezone(
                        "fr",
                        placeholder="Fuseau horaire", 
                        search_placeholder="Rechercher un fuseau horaire..."
                    ),
                    dynolanguage(
                        "fr",
                        placeholder="Langue", 
                        search_placeholder="Rechercher une langue..."
                    ),
                    direction="row",
                    align="center",
                    spacing="2"
                ),
                rx.heading("Locale es", size="2"),
                rx.flex(
                    dynotimezone(
                        "es",
                        placeholder="Zona horaria", 
                        search_placeholder="Buscar una zona horaria..."
                    ),
                    dynolanguage(
                        "es",
                        placeholder="Idioma", 
                        search_placeholder="Buscar un idioma..."
                    ),
                    direction="row",
                    align="center",
                    spacing="2"
                ),
                align="center",
                spacing="3"
            ),
            align="center",
            spacing="4"
        ),
        spacing="9",
        align="center"
    )

def single() -> rx.Component:
    return rx.vstack(
        rx.spacer(),
        dynolanguage(
            placeholder="Language", 
            search_placeholder="Search for a language..."
        ),
        align="center",
        spacing="4"
    )

# Add state and page to the app.
app = rx.App(

)
app.add_page(index)
app.add_page(single)
