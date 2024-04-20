"""Reflex custom component Dynoselect."""

from typing import List, Dict, Literal, Optional

import reflex as rx

from reflex.components.radix.themes.typography.base import LiteralTextWeight
from reflex.components.radix.themes.base import LiteralRadius
from reflex.components.radix.themes.components.text_field import LiteralTextFieldSize
from reflex.event import EventHandler, EventSpec
from reflex.vars import BaseVar

from .options import TimezoneOptions

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

    hover: int
    """The index of the option currently hovered over."""

    search_phrase: str
    """The search phrase entered by the user."""

    selected: dict[str, str] = _DEFAULT
    """The currently selected option.
    
    The attribute contains the complete dictionary of the currently selected option. In 
    addition to the `value`, `label`, and `keywords` keys, one can add arbitrary keys to 
    the dictionary to store additional information about an option.
    """

    _OPT_LABEL = "label" # The key for the option's label.
    _OPT_VALUE = "value" # The key for the option's value.
    _OPT_KEYWORDS = "keywords" # Comma separated words to include in the search. 
    _SEARCH_DELIMITER = " " # The delimiter used to separate search words.

    _COLOR_PLACEHOLDER = "var(--gray-a10)"

    @classmethod
    def chevron_down(cls):
        """ Display the chevron down icon.
              
        The chevron down Lucide icon looks slightly different than the Radix one.
        Therefore, the Radix icon is used instead.        
        """
        
        return rx.html(
            '<svg width="9" height="9" viewBox="0 0 9 9" fill="currentColor" '
            'xmlns="http://www.w3.org/2000/svg" class="rt-SelectIcon" '
            'aria-hidden="true">'
            '<path d="M0.135232 3.15803C0.324102 2.95657 0.640521 2.94637 0.841971 '
            '3.13523L4.5 6.56464L8.158 3.13523C8.3595 2.94637 8.6759 2.95657 8.8648 '
            '3.15803C9.0536 3.35949 9.0434 3.67591 8.842 3.86477L4.84197 '
            '7.6148C4.64964 7.7951 4.35036 7.7951 4.15803 7.6148L0.158031 '
            '3.86477C-0.0434285 3.67591 -0.0536285 3.35949 0.135232 3.15803Z">'
            '</path></svg>'
        )
    
    @classmethod
    def _get_keywords(cls, opts: list[dict[str, str]] | dict[str, str]) -> rx.Var[str]:
        """ Return a searchable Reflex variable based on the given options."""
        if isinstance(opts, list):
            data = [cls.get_search_data(e) for e in opts]
            return cls._tovar(" ".join(data))
        else:
            return cls._tovar(cls.get_search_data(opts))
    
    @classmethod
    def _tovar(cls, string: str) -> rx.Var:
        """Convert a string to a reflex variable."""
        return rx.Var.create('"' + string + '"')
    
    @classmethod
    def search(cls, keywords: rx.Var[str]) -> rx.Var[bool]:
        """ Search for the search phrase in the given keywords.
        
        Returns:
            A Boolean reflex variable that is true if the search phrase is found.
        """
        return keywords.lower().contains(cls.search_phrase.lower())

    @classmethod
    def get_search_data(cls, option: dict[str, str]) -> str:
        """ Compute a searchable string based on the given option.
        
        This method is useful to implement a client-side search functionality.
        Basically, the string returned by this method is searched for occurrences of
        the user's search phrase. If the search phrase is found, the option is 
        displayed. Otherwise, it is hidden. The string returned by this method is never
        displayed to the user. Therefore, one does not have to worry about the format
        of the string.

        The default implementation returns the option's label and keywords.

        Args:
            option: A dictionary containing the option's values.
        """
        label = option.get(cls._OPT_LABEL, "")
        keywords = option.get(cls._OPT_KEYWORDS, "")
        if isinstance(keywords, (tuple,list,)):
            keywords = cls._SEARCH_DELIMITER.join(list(keywords))
        return label + cls._SEARCH_DELIMITER + keywords
    
    @classmethod
    def selected_text(cls, text: str, **props) -> rx.Component:
        return rx.text(
            text, 
            class_name="rt-SelectTriggerInner", weight=props.get("weight", "regular")
        )

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
        create_option: Optional[Dict[str, str]],
        modal: bool,
        on_select: Optional[callable] = None,
        ) -> rx.Component:
        """ Create the component. See dynoselect() function for more information."""
        # Select entries are either a text box or a solid button. They must have the
        # exact same height to avoid flicker effects when moving the mouse over the
        # entries. Therefore, this variable maps button height to text height.
        btn_2_text_height = {"1": "6", "2": "8", "3": "10", "4": "12"}
        indent_direction = {"center": "x", "left": "l", "right": "r"}
        style = dict(
            radius=radius,
            align="center", # This is always necessary to avoid flicker effects.
            padding="0", # Required for align="left" to align box and button texts. 
            class_name=f"h-{btn_2_text_height[size]} w-full",
        )

        def get_handler(option: dict[str, str]) -> EventHandler:
            """Return an event handler that sets the selected option."""
            if on_select is None:
                return lambda *x: [cls.set_selected(option)]
            return lambda *x: [cls.set_selected(option), on_select(option)] 
        
        def text(label: str):
            return rx.text(
                label, 
                trim="both", 
                align=align,
                size=size, 
                weight=weight, 
                class_name=f"p{indent_direction[align]}-{indent} w-full"
            )

        def item(child, **props):
            """ An item that is currently not hovered over. """
            return rx.flex(child, **props)

        def hitem(child, **props):
            """ An item that is currently hovered over."""
            bn = rx.button(child, display="inline", variant="solid", size=size, **props)
            return rx.popover.close(bn)

        def text_placeholder(label: rx.Component | str) -> rx.Component:
            if isinstance(label, str):
                return rx.text(label or "", color=cls._COLOR_PLACEHOLDER, weight=weight)
            return label
        
        def hoverable(child, index: int, **props) -> rx.Component:
            hv = dict(on_mouse_over=lambda *x: cls.set_hover(index), **props)
            return rx.cond(cls.hover==index, hitem(child, **hv), item(child, **hv)) 

        def create_entry(option: dict[str, str], index: int) -> rx.Component:
            label = option.get(cls._OPT_LABEL, "").format(cls.search_phrase)
            opt = dict(**option)
            opt[cls._OPT_LABEL] = cls.search_phrase
            entry = hoverable(
                text(label), 
                index, 
                **style, 
                on_click=get_handler(opt)
            )
            return rx.cond(
                # The last option is the one that gets created. So do not search it.
                cls.search(cls._get_keywords(options[:-1])),
                rx.fragment(),
                entry
            )
        
        def normal_entry(option: dict[str, str], index: int) -> rx.Component:
            txt = option.get(cls._OPT_LABEL, "")
            return hoverable(
                text(txt), 
                index, 
                **style, 
                on_click=get_handler(option)
            )
        
        entries = [
            rx.cond(
                # Condition to implement search functionality.
                cls.search(cls._get_keywords(opt)),
                normal_entry(opt, i), # Matches search phrase.
                rx.fragment(), # Does not match search phrase.
            )            
            for i, opt in enumerate(options)
        ]
        
        if create_option is not None:
            options.append(create_option)
            entries.append(create_entry(options[-1], len(options)-1))

        return rx.popover.root(
            rx.popover.trigger(
                rx.button(
                    rx.cond(
                        cls.selected[cls._OPT_LABEL] == "",
                        text_placeholder(placeholder),
                        cls.selected_text(
                            f"{cls.selected[cls._OPT_LABEL]}", weight=weight
                        ),
                    ),
                    
                    cls.chevron_down(),
                    _active={
                        "background-color": "transparent"
                    },
                    class_name="rt-reset rt-SelectTrigger rt-variant-surface",
                    size=size,
                    radius=radius,
                ),
            ),
            rx.popover.content(
                rx.box(
                    rx.box(
                        rx.input(
                            placeholder=(search_placeholder or ""),
                            on_change=cls.set_search_phrase,
                            size=size,
                            radius=radius,
                        ),
                        class_name=f"m-{padding}"
                    ),
                    rx.box(
                        rx.scroll_area(
                            rx.flex(
                                *entries,
                                direction="column",
                                class_name=f"w-full pr-{padding}",
                            ),
                            scrollbars="vertical",
                            class_name=f"pl-{padding} mb-{padding}",
                            radius=radius,
                            height=height
                        ),
                    ),
                ),
                overflow="hidden",
                padding="0"
            ),
            modal=modal,
            on_mount=cls.set_selected(default_option or cls._DEFAULT),
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
    _KEY_PLACEHOLDER = "placeholder"

    @classmethod
    def selected_text(cls, text: str, **props) -> rx.Component:
        return rx.flex(
            rx.icon("globe", size=cls._ICON_SIZE, color=cls._COLOR_PLACEHOLDER),
            rx.text(text, color=cls._COLOR_PLACEHOLDER),
            direction="row",
            spacing="2",
            align="center",
        )
    
    @classmethod
    def get_component(cls, locale: str, **props):
        options = TimezoneOptions(locale)
        props[cls._KEY_PLACEHOLDER] = cls.selected_text(
            props.get(cls._KEY_PLACEHOLDER, "")
        )
            
        return super().get_component(options, **props, create_option=None)
        

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