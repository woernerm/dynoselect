from babel.core import Locale
from utils import request
from json import loads
from babel.core import UnknownLocaleError
from babel.core import Locale

from pyuca import Collator

collator = Collator()

class LocaleRegistry(list):
    """ Iterates over a real-world list of locales from the Unicode CLDR repository. """

    URL = (
        "https://raw.githubusercontent.com/unicode-org/cldr-json/main/cldr-json/"
        "cldr-core/availableLocales.json"
    )
    """ URL that lists all known locales in the CLDR repository. """

    _content = None
    _SEPARATOR = "-"

    def __init__(self, locale: str | None = None) -> None:
        """Return a list of options of existing locales and their localized names.
    
        This table can be used to display a list of available locales to the user. The
        names are given in the currently selected locale.
        Args:
            locale: The locale in which to display the names. If not given, the
                locale names are displayed in the locale itself (autonym).
        """
        from reflex_dynoselect.options import Option

        locale = Locale.parse(locale, sep=self._SEPARATOR) if locale else None

         # Download the list of files in the CLDR repository. Cache the results.
        if LocaleRegistry._content is None:
            data = loads(request(self.URL))
            LocaleRegistry._content = data.get("availableLocales", {}).get("full", [])

        def display_name(tag: str) -> str:
            try:
                taglocale = Locale.parse(tag, sep=self._SEPARATOR)
                return taglocale.get_display_name(locale or taglocale)
            except UnknownLocaleError:
                return None
    
        table = [Option(value=e.strip(), label=display_name(e)) for e in self._content]
        table = [e for e in table if e.label is not None and e.value is not None]
        super().__init__(sorted(table, key=lambda opt: collator.sort_key(opt.label)))

    def values(self) -> set[str]:
        return {e.value for e in self}