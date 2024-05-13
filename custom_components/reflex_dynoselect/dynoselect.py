"""Reflex custom component Dynoselect."""

from typing import List, Dict, Literal, Optional, Callable, Iterable
from datetime import datetime
from zoneinfo import ZoneInfo
from itertools import chain
import reflex as rx

from reflex.components.radix.themes.typography.base import LiteralTextWeight
from reflex.components.radix.themes.base import LiteralRadius
from reflex.components.radix.themes.components.text_field import LiteralTextFieldSize

from .utils import chevron_down
from .options import (
    Option, LocalizedOptions, TIMEZONE_OPTION_PATH, LOCALE_OPTION_PATH, NONE_LOCALE
)

LiteralIndent = Literal[
    "0", "0.5", "1", "1.5", "2", "2.5", "3", "3.5", "4", "5", "6", "7", "8", "9", "10"
]


class Dynoselect(rx.ComponentState):
    """A select component with search functionality and ability to create new options.
    
    The component provides a text input to search all options. In addition, the user can 
    either select an existing option or create a new one by entering a custom label.
    
    Options are given as a list of dictionaries. Each dictionary must contain a label
    and a value key with strings as values. The label is displayed to the user while
    the value key can be used for internal identifiers. Optionally, one can provide a 
    keywords key to include alternative phrases that are included in the search but
    not displayed to the user.

    The `selected` attribute contains the complete dictionary of the currently selected 
    option. In addition to the `value`, `label`, and `keywords` keys, one can add
    arbitrary keys to the dictionary to store additional information about an option.

    Which keys in the option directory are considered for searching can be customized
    by overriding the get_search_data() method. The default implementation only
    includes the label and keywords keys.
    """

    _DEFAULT = {"label": "", "value": ""}
    """The default selected option."""

    search_phrase: str
    """The search phrase entered by the user."""

    selected: dict[str, str]
    """The currently selected option.
    
    The attribute contains the complete dictionary of the currently selected option. In 
    addition to the `value`, `label`, and `keywords` keys, one can add arbitrary keys to 
    the dictionary to store additional information about an option.
    """

    options: list[dict[str, str]] = []
    """ The formatted options available to the user. """

    chained_options: str
    """ A string that concatenates all options for search purposes."""

    _KEY_LABEL = "label"
    _KEY_KEYWORDS = "keywords"
    _KEY_VALUE = "value"

    _icon_size = 16
    """The size of the icon in pixels."""

    _COLOR_PLACEHOLDER = rx.color("gray", 10)
    
    @classmethod
    def client_search(cls, option: Option) -> rx.Var[bool]:
        """ Search for the search phrase in the given keywords and label.

        The option's value is not searched to avoid awkward results in case the value
        has nothing to do with what is displayed to the user. If the value shall be
        included in the search, it should be added to the option's keywords.
        
        Returns:
            A Boolean reflex variable that is true if the search phrase is found.
        """        
        return (
            option[cls._KEY_LABEL].lower().contains(cls.search_phrase.lower()) |
            option[cls._KEY_KEYWORDS].lower().contains(cls.search_phrase.lower())
        )
        
    @classmethod
    def btntext(cls, child, icon: str, **props) -> rx.Component:
        """Create a button text with a globe icon and placeholder text."""
        comps = [rx.text(child, **props)] if isinstance(child, str) else [child]
        comps = [rx.icon(icon, size=cls._icon_size, **props)] + comps if icon else comps
        return rx.flex(*comps, direction="row", spacing="2", align="center")

    @classmethod
    def get_component(
        cls, 
        default_option: Dict[str, str], 
        placeholder: str,
        search_placeholder: str,
        size: LiteralTextFieldSize,
        weight: LiteralTextWeight,
        radius: LiteralRadius,
        height: str,
        padding: str,
        indent: LiteralIndent,
        align: str,
        create_option: Optional[Dict[str, str]] = None,
        on_select: Optional[Callable] = None,
        icon: str = None,
        content_props: dict[str, str] = {},
        root_props: dict[str, str] = {},
        ) -> rx.Component:
        """ Create the component. See dynoselect() function for more information.
        """
        size_radius = dict(size=size, radius=radius)
        opt_create = Option(**(create_option or {}))

        cls.get_fields()["selected"].default = default_option or cls._DEFAULT
        
        def hoverable(child, idx: int, **props) -> rx.Component:
            btn = rx.button(
                child, display="inline", variant="solid", size=size,
                style={
                    ":not(:hover)":{"background": "transparent"},
                    f":not(:hover) > {child.as_}":{"color": rx.color("gray", 12)}
                },
                **props
            )
            return rx.popover.close(btn)
        
        def entry(cond, option: Option, idx: int, create: bool = False) -> rx.Component:
            # Entries are either a text box or a solid button. This mapping ensures they
            # have the same height to avoid flicker effects when hovering over them.
            btn_height = {"1": "6", "2": "8", "3": "10", "4": "12"}
            indent_direction = {"center": "x", "left": "l", "right": "r"}
            select = opt_create.clone(label=cls.search_phrase) if create else option

            handler = lambda: cls.set_selected(select)
            if on_select:
                handler = lambda: [cls.set_selected(select), on_select(select)]

            button = hoverable(
                rx.text(
                    option[cls._KEY_LABEL], 
                    trim="both", 
                    align=align,
                    size=size, 
                    weight=weight, 
                    class_name=f"p{indent_direction[align]}-{indent} w-full"
                ),
                idx, 
                radius=radius,
                align="center", # Avoid flicker effects.
                padding="0", # To align box and button texts for align="left".
                class_name=f"h-{btn_height[size]} w-full",
                on_click=handler
            )

            return rx.cond(cond, button, rx.fragment())
        
        on_open_auto_focus = content_props.pop(
            "on_open_auto_focus", lambda *a: [cls.set_search_phrase("")]
        )
        
        return rx.popover.root(
            rx.popover.trigger(
                rx.button(
                    # Show either placeholder or the selected option's label.
                    rx.cond(
                        cls.selected[cls._KEY_LABEL] == "",
                        cls.btntext(
                            placeholder, 
                            icon, 
                            color=cls._COLOR_PLACEHOLDER, 
                            weight=weight
                        ),
                        cls.btntext(
                            f"{cls.selected[cls._KEY_LABEL]}", icon, weight=weight
                        ),
                    ),
                    chevron_down(),
                    class_name="rt-reset rt-SelectTrigger rt-variant-surface",
                    **size_radius,
                ),
            ),
            rx.popover.content(
                rx.box(
                    rx.input(
                        placeholder=(search_placeholder or ""),
                        on_change=cls.set_search_phrase,
                        **size_radius
                    ),
                    class_name=f"m-{padding}"
                ),
                rx.scroll_area(
                    rx.flex(
                        rx.foreach(
                            cls.options, 
                            lambda opt, i: entry(cls.client_search(opt), opt, i)
                        ),
                        (
                            entry(
                                ~cls.chained_options.lower().contains(cls.search_phrase.lower()), 
                                opt_create.format(cls.search_phrase), 
                                cls.options.length(), 
                                True
                            ) if create_option else rx.fragment()
                        ),
                        direction="column",
                        class_name=f"w-full pr-{padding}",
                    ),
                    scrollbars="vertical",
                    class_name=f"pl-{padding} mb-{padding}",
                    radius=radius,
                    height=height,
                ),
                overflow="hidden",
                padding="0",
                on_open_auto_focus=on_open_auto_focus,
                **content_props,
            ),
            **root_props,
        )

def dynoselect(
        options: List[Dict[str, str]], 
        default_option: Dict[str, str] = None, 
        placeholder: str | None = None,
        search_placeholder: str | None = None,
        size: LiteralTextFieldSize = "2",
        weight: LiteralTextWeight = "regular",
        radius: LiteralRadius | None = None,
        height: str = "10rem",
        padding: str = "2",
        indent: LiteralIndent = "6",
        align: str = "left",
        create_option: dict[str, str] | None = None,
        on_select: Optional[Callable] = None,
        icon: str = None,
        content_props: dict[str, str] = {},
        root_props: dict[str, str] = {},
)-> rx.Component:
    """Create a the select component. 
        
    Args:
        options: A list of dictionaries containing the options. The dictionary
            must contain a label and a value key with strings as values. The label
            is displayed to the user while the value key can be used for internal
            identifiers. Optionally, one can provide a keywords key to include
            alternative phrases that are included in the search but not displayed
            to the user. This is intended to improve the search functionality so
            that the user can find an option even in case synonyms are used.
        default_option: The default option to select. By default, no option is
            selected.
        placeholder: The placeholder text for the select component that is shown
            when no option is selected.
        search_placeholder: The placeholder text for the search input field.
        size: Relative size of the component. Allowed values are "1", "2", and "3".
        weight: The weight of the text. Allowed values are "none", "light", 
            "regular", "medium", and "bold".
        radius: The radius of the select component. Allowed values are "none",
            "small", "medium", "large", and "full".
        height: The height of the select component. Can be given as a CSS value
            like "10rem" or "100%".
        padding: The padding around the border of the select component.
        indent: The indentation of the select component. If align is chosen to be
            "center", the indentation is applied horizontally to both sides and
            therefore acts as padding. Otherwise, it is applied to one side only
            and works as normal indentation.
        align: The alignment of each option. Allowed values are "left", "center", and 
            "right".
        create_option: The option to create a new entry. If this option is None,
            the user is not allowed to create new entries. If the option is a
            dictionary, it determines the value and label of the new entry. One
            can refer to the search phrase by using the "{}" placeholder in the
            label. For example, the label "Create new {}" would be displayed as
            "Create new apple" if the search phrase is "apple".    
        on_select: Event handler that is called when the user selects an option. Note
            that the event handler is called even if the user selects the same value
            as before.
        icon: The name of the lucide icon to display next to the selected option.
        content_props: Additional properties that are passed on to the 
            reflex.popover.content component used by Dynoselect.
        root_props: Additional properties that are passed on to the 
            reflex.popover.root component used by Dynoselect.
    """

    component = Dynoselect.create(
        default_option=default_option,
        placeholder=placeholder,
        search_placeholder=search_placeholder,
        size=size,
        weight=weight,
        radius=radius,
        height=height,
        padding=padding,
        indent=indent,
        align=align,
        create_option=create_option,
        on_select=on_select,
        icon=icon,
        content_props=content_props,
        root_props=root_props
    )
    component.State.get_fields()["options"].default = [Option(**opt) for opt in options]
    component.State.get_fields()["chained_options"].default = Option.chain(options)
    return component



class Dynotimezone(Dynoselect):
    """A select component for timezones.
    
    The component provides an extensive list of timezones that are translated into the
    selected locale. By default, the component tries to detect the user's timezone and
    select it. If the detection fails, the given default option is used or, if no
    default option is given, no timezone is selected. 

    Timezones are given as a representative city and country as well as the UTC offset.
    The offset is calculated ony the fly on page load in order to accomate for changes
    in offset due to daylight saving time. 

    Translations have been precomputed and stored in multiple JSON files that are
    themeselves stored in a tar.gz archive. This avoids negative performance impacts
    during app compilation.
    """

    _raw_options: list[dict[str, str]] = []
    """ The unformatted options as given during initialization. """

    def offset(self, canonical: str):
        """Return timezone names as UTC offset with represenative cities."""
        ref = datetime.now().astimezone(ZoneInfo(canonical))
        offset = ref.utcoffset().total_seconds()
        hours = int(offset // 3600)
        minutes = int(offset % 3600 // 60)
        return f"UTC{hours:+03}:{minutes:02d}" 
    
    def refresh(self):
        self.options = self.format_options()
        self.chained_options = Option.chain(self.options)
    
    def format_options(self) -> list[dict[str, str]]:
        """ Modify options before display (e.g. to include recent information). 
        
        The default implementation will just use the options without modification.
        """
        options = [Option(**opt) for opt in self._raw_options]
        for opt in options:
            opt.label = f"{opt.label} ({self.offset(opt.value)})"  
        return options 
    
    def initialize(self, value: str):
        """ Set the selected option by value. """
        default = self.get_fields()["selected"].default
        self.refresh()      
        self.selected = next((e for e in self.options if e.value == value), default)
    
    @classmethod
    def get_component(cls, **props):
        detect_timezone = rx.call_script(
            "Intl.DateTimeFormat().resolvedOptions().timeZone", 
            callback=cls.initialize
        )
        content_props = props.pop("content_props", {})

        return super().get_component(
            content_props={
                **content_props, 
                "on_mount": detect_timezone,
                "on_open_auto_focus": lambda *a: [cls.set_search_phrase(""), cls.refresh()]
            },
            **props, 
        )
        

def dynotimezone(
        locale: str,
        default_option: Dict[str, str] = None, 
        placeholder: str | None = None,
        search_placeholder: str | None = None,
        size: LiteralTextFieldSize = "2",
        weight: LiteralTextWeight = "regular",
        radius: LiteralRadius | None = None,
        height: str = "20rem",
        padding: str = "2",
        indent: LiteralIndent = "6",
        align: str = "left",
        on_select: Optional[callable] = None,
        icon: str = "globe",
        content_props: dict[str, str] = {},
        root_props: dict[str, str] = {},
)-> rx.Component:
    """Create a timezone select component. 
    
    Args:
        locale: The locale to use for the timezone names.
        default_option: The default option to select. By default, the component will
            try to detect the user's timezone and select it. If the detection fails,
            the default option is used.
        placeholder: The placeholder text for the select component that is shown
            when no option is selected.
        search_placeholder: The placeholder text for the search input field.
        size: Relative size of the component. Allowed values are "1", "2", and "3".
        weight: The weight of the text. Allowed values are "none", "light", 
            "regular", "medium", and "bold".
        radius: The radius of the select component. Allowed values are "none",
            "small", "medium", "large", and "full".
        height: The height of the select component. Can be given as a CSS value
            like "10rem" or "100%".
        padding: The padding around the border of the select component.
        indent: The indentation of the select component. If align is chosen to be
            "center", the indentation is applied horizontally to both sides and
            therefore acts as padding. Otherwise, it is applied to one side only
            and works as normal indentation.
        align: The alignment of each option. Allowed values are "left", "center", and 
            "right".
        on_select: Event handler that is called when the user selects an option. Note
            that the event handler is called even if the user selects the same value
            as before.
        icon: The lucide icon to display next to the selected option.
    """
    options = LocalizedOptions.load(TIMEZONE_OPTION_PATH, locale)

    component = Dynotimezone.create(
        default_option=default_option,
        placeholder=placeholder,
        search_placeholder=search_placeholder,
        size=size,
        weight=weight,
        radius=radius,
        height=height,
        padding=padding,
        indent=indent,
        align=align,
        on_select=on_select,
        icon=icon,
        content_props=content_props,
        root_props=root_props
    )
    component.State._raw_options = options
    return component
    

def dynolanguage(
        locale: str = None,
        default_option: Dict[str, str] = None, 
        placeholder: str | None = None,
        search_placeholder: str | None = None,
        size: LiteralTextFieldSize = "2",
        weight: LiteralTextWeight = "regular",
        radius: LiteralRadius | None = None,
        height: str = "20rem",
        padding: str = "2",
        indent: LiteralIndent = "6",
        align: str = "left",
        on_select: Optional[callable] = None,
        icon: str = "languages",
        content_props: dict[str, str] = {},
        root_props: dict[str, str] = {},
        only: Iterable[str] = None
)-> rx.Component:
    """Create a language select component.

    Args:
        locale: The locale to use for the language names. If None, each language
            is displayed in its own respective locale.
        default_option: The default option to select. By default, the component will
            try to detect the user's locale and select it. If the detection fails,
            the default option is used.
        placeholder: The placeholder text for the select component that is shown
            when no option is selected.
        search_placeholder: The placeholder text for the search input field.
        size: Relative size of the component. Allowed values are "1", "2", and "3".
        weight: The weight of the text. Allowed values are "none", "light", 
            "regular", "medium", and "bold".
        radius: The radius of the select component. Allowed values are "none",
            "small", "medium", "large", and "full".
        height: The height of the select component. Can be given as a CSS value
            like "10rem" or "100%".
        padding: The padding around the border of the select component.
        indent: The indentation of the select component. If align is chosen to be
            "center", the indentation is applied horizontally to both sides and
            therefore acts as padding. Otherwise, it is applied to one side only
            and works as normal indentation.
        align: The alignment of each option. Allowed values are "left", "center", and 
            "right".
        on_select: Event handler that is called when the user selects an option. Note
            that the event handler is called even if the user selects the same value
            as before.
        icon: The lucide icon to display next to the selected option.
        only: Optional iterable with languages to display. Default: Show all available
            language options. For example:
            ```py
            dynolanguage(
                placeholder="Language", 
                search_placeholder="Search for a language...",
                only={"de", "en-GB", "en", "fr", "es"},
            ),
            ```
            This will display options for German (as spoken in Germany), English (as
            spoken in the UK), English (as spoken in the United States), Spanish (as
            spoken in Spain).
    """
    options = LocalizedOptions.load(LOCALE_OPTION_PATH, locale or NONE_LOCALE)

    only = set(only) if only else set()
    missing = only - {e.value for e in options}
    if missing:
        raise LookupError(f"Locale(s) {', '.join(missing)} not available.")
    options = [e for e in options if not only or e.value in only]

    return dynoselect(
        options=options,
        default_option=default_option,
        placeholder=placeholder,
        search_placeholder=search_placeholder,
        size=size,
        weight=weight,
        radius=radius,
        height=height,
        padding=padding,
        indent=indent,
        align=align,
        on_select=on_select,
        icon=icon,
        content_props=content_props,
        root_props=root_props
    )




