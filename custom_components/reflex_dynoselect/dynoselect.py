"""Reflex custom component Dynoselect."""

from typing import List, Dict, Literal, Optional, Union, Callable
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from itertools import chain
import reflex as rx

from reflex.components.radix.themes.typography.base import LiteralTextWeight
from reflex.components.radix.themes.base import LiteralRadius
from reflex.components.radix.themes.components.text_field import LiteralTextFieldSize

from .utils import chevron_down
from .options import TimezoneOptions

LiteralIndent = Literal[
    "0", "0.5", "1", "1.5", "2", "2.5", "3", "3.5", "4", "5", "6", "7", "8", "9", "10"
]

class Option(dict):
    KEYS = ["label", "value", "keywords"]

    _SEARCH_DELIMITER = " " # The delimiter used to separate search words.

    def __init__(self, label: str = "", value: str = "", keywords: List[str] = []):
        super().__init__(
            label=label, 
            value=value, 
            keywords=self._SEARCH_DELIMITER.join(keywords)
        )

    def _hasattr(self, key):
        if key not in self.KEYS:
            raise AttributeError(f'{self.__class__.__name__} has no attribute "{key}"')

    def __getattr__(self, attr):
        self._hasattr(attr)
        return self.get(attr, "")
    
    def __setattr__(self, attr, value):
        self._hasattr(attr)
        self[attr] = value

    def clone(self, **kwargs):
        tmp = Option(**self)
        for key, value in kwargs.items():
            setattr(tmp, key, value)
        return tmp

    def format(self, *args, **kwargs):
        value = self.value.format(*args, **kwargs)
        label = self.label.format(*args, **kwargs)
        keywords = self.keywords.format(*args, **kwargs)
        return Option(label=label, value=value, keywords=keywords)

         





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

    options: list[dict[str, str]]
    """ The options available to the user. """

    _KEY_LABEL = "label"
    _KEY_KEYWORDS = "keywords"
    _KEY_VALUE = "value"

    _COLOR_PLACEHOLDER = rx.color("gray", 10)
    
    @classmethod
    def client_search(cls, option) -> rx.Var[bool]:
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

    @rx.cached_var
    def chained_options(self) -> str:
        """ Summarize all search data in a single string.
        
        This is used to display a create option if not other results can be found.
        Although it would be better to count the number of search results and only
        show the create option if no results are found, it does not seem to be possible 
        with the current reflex implementation without asking the backend for help.
        """
        opts = self.cached_options
        result = Option._SEARCH_DELIMITER.join(
            chain(*[[e.get(self._KEY_LABEL, ""), e.get(self._KEY_KEYWORDS, "")] for e in opts])
        )
        return result

    @rx.cached_var
    def cached_options(self) -> list[dict[str, str]]:
        """ Modify options before display (e.g. to include recent information). 
        
        The default implementation will just use the options without modification.
        """
        return self.format_options()
    
    def format_options(self) -> list[dict[str, str]]:
        """ Format the options before display. """
        return self.options
    
    @classmethod
    def btntext(cls, child, **props) -> rx.Component:
        if child is None or isinstance(child, str):
            class_name = props.pop("class_name", "rt-SelectTriggerInner")
            return rx.text(child or "", class_name=class_name, **props)
        else:
            return child

    @classmethod
    def get_component(
        cls, 
        options: List[Dict[str, str]], 
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
        modal: bool = False,
        on_select: Optional[Callable] = None,
        ) -> rx.Component:
        """ Create the component. See dynoselect() function for more information.
        """
        size_radius = dict(size=size, radius=radius)
        opt_create = Option(**(create_option or {}))

        cls.__fields__["selected"].default = default_option or cls._DEFAULT
        cls.__fields__["options"].default = [Option(**opt) for opt in options]
        
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
        
        return rx.popover.root(
            rx.popover.trigger(
                rx.button(
                    # Show either placeholder or the selected option's label.
                    rx.cond(
                        cls.selected[cls._KEY_LABEL] == "",
                        cls.btntext(
                            placeholder, color=cls._COLOR_PLACEHOLDER, weight=weight
                        ),
                        cls.btntext(f"{cls.selected[cls._KEY_LABEL]}", weight=weight),
                    ),
                    chevron_down(),
                    class_name="rt-reset rt-SelectTrigger rt-variant-surface",
                    **size_radius
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
                            cls.cached_options, 
                            lambda opt, i: entry(cls.client_search(opt), opt, i)
                        ),
                        (
                            entry(
                                ~cls.chained_options.lower().contains(cls.search_phrase.lower()), 
                                opt_create.format(cls.search_phrase), 
                                cls.cached_options.length(), 
                                True
                            ) if create_option else rx.fragment()
                        ),
                        direction="column",
                        class_name=f"w-full pr-{padding}",
                    ),
                    scrollbars="vertical",
                    class_name=f"pl-{padding} mb-{padding}",
                    radius=radius,
                    height=height
                ),
                overflow="hidden",
                padding="0"
            ),
            modal=modal,
            on_open_change=cls.set_search_phrase(""),
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
        modal: bool = False,
        on_select: Optional[callable] = None,
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
        modal: Directly passed on to PopoverRoot. If true, interaction on screen 
            readers with other elements is disabled and only popover content 
            is visible.
        on_select: Event handler that is called when the user selects an option. Note
            that the event handler is called even if the user selects the same value
            as before.
    """

    return Dynoselect.create(
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
        create_option=create_option,
        modal=modal,
        on_select=on_select,
    )



class Dynotimezone(Dynoselect):

    _ICON_SIZE = 16

    locale: str

    def offset(self, canonical: str):
        """Return timezone names as UTC offset with represenative cities."""
        ref = datetime.now().astimezone(ZoneInfo(canonical))
        offset = ref.utcoffset().total_seconds()
        hours = int(offset // 3600)
        minutes = int(offset % 3600 // 60)
        return f"UTC{hours:+03}:{minutes:02d}" 
    
    def format_options(self) -> list[dict[str, str]]:
        """ Modify options before display (e.g. to include recent information). 
        
        The default implementation will just use the options without modification.
        """
        options = [Option(**opt) for opt in self.options]
        for opt in options:
            opt.label = f"{opt.label} ({self.offset(opt.value)})"    
        return options

    @classmethod
    def btntext(cls, child, **props) -> rx.Component:
        if isinstance(child, str):
            return rx.flex(
                rx.icon("globe", size=cls._ICON_SIZE, **props),
                rx.text(child, **props),
                direction="row",
                spacing="2",
                align="center",
            )
        return child
    
    @classmethod
    def get_component(cls, locale: str, **props):
        cls.__fields__["locale"].default = locale
        opts = TimezoneOptions(locale)
        
        return super().get_component(opts, **props)
        

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
        modal: bool = False,
        on_select: Optional[callable] = None,
)-> rx.Component:
    """Create a timezone select component. """

    return Dynotimezone.create(
        locale=locale,
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
        modal=modal,
        on_select=on_select,
    )