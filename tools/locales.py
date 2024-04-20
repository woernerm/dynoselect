from babel.core import Locale
from utils import request
from json import loads

class LocaleRegistry:
    """ Iterates over a real-world list of locales from the Unicode CLDR repository. """

    URL = (
        "https://raw.githubusercontent.com/unicode-org/cldr-json/main/cldr-json/"
        "cldr-core/availableLocales.json"
    )
    """ URL that lists all known locales in the CLDR repository. """

    def __init__(self) -> None:
         # Download the list of files in the CLDR repository.
        self._content = loads(request(self.URL))
        self._content = self._content.get("availableLocales", {}).get("full", [])

    @property
    def category_count(self):
        return 1
    
    def __iter__(self):
        return iter(self._content)


def get_locale_table(locale: "Locale" = None) -> dict[str, str]:
    """Return a dictionary of existing locales and their localized names.
    
    This table can be used to display a list of available locales to the user. The
    names are given in the currently selected locale.
    Args:
        locale: The locale in which to display the names. If not given, the
            locale names are displayed in the locale itself (autonym).
    """
    from babel.core import UnknownLocaleError
    from babel.core import Locale
    
    def display_name(tag: str) -> str:
        try:
            return Locale.parse(tag, sep="-").get_display_name(locale)
        except UnknownLocaleError:
            return None
    
    table = {e.strip(): display_name(e) for e in LocaleRegistry()}
    table = {k: v for k, v in table.items() if v is not None}
    return [{"value": k, "label": v} for k, v in table.items()]