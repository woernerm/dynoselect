from pathlib import Path
from typing import Literal
import tarfile
import io
import json

TIMEZONE_OPTION_PATH = (Path(__file__).parent / "timezones.tar.gz").absolute()
"""Path to the timezone options archive."""

LOCALE_OPTION_PATH = (Path(__file__).parent / "locales.tar.gz").absolute()
"""Path to the locale options archive."""

class Option(dict):
    """ Represents a single selectable option."""
    KEYS = ["label", "value", "keywords"]

    _SEARCH_DELIMITER = " " # The delimiter used to separate search words.

    def __init__(self, label: str = "", value: str = "", keywords: list[str] = []):
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
    

class LocalizedOptions:
    """ A class to store localized options in a tar.gz archive.
    
    Deriving localized options can take some computing time. To avoid this, the 
    options are stored in a tar archive. The archive is a gzipped tar archive that
    contains JSON files for each locale. The filename is the locale, e.g. "de-DE.json".
    If the options are locale-independent, they are stored in a file called 
    "autonyms.json". For example, if language options are given in the respective
    language itself (e.g. "Deutsch" for "German"), they are stored in such a file.

    The class is meant to be used as a context manager using the "with" statement.
    """

    _AUTONYMS = "autonyms" 
    """ Option in their corresponding locale.
    
    For example, the language option "German" given in German, which would be "Deutsch".
    """

    _SEPARATOR = "-"
    _SUFFIX = ".json"

    def __init__(self, archive: Path | str, mode: Literal["w", "r"] = "w"):
        self._filename = Path(archive)
        self._mode = mode

    def _normalize(self, locale: str) -> str:
        """ Correct minor variations in the locale string.
        
        For example, a locale may be given as "de_DE" or "de-DE". If the given locale
        is None, the key for autonyms is returned.

        Args:
            locale: The locale to normalize.
        """
        if not locale:
            return self._AUTONYMS
        return locale.replace("_", self._SEPARATOR)

    def add(self, locale: str, data: any):
        """ Add json-serializable data for a given locale to the archive.
        
        Args:
            locale: The locale for which the data is stored.
            data: The data to store. Must be json-serializable.        
        """
        locale = self._normalize(locale)
        file = io.BytesIO()
        file.write(json.dumps(data, ensure_ascii=False).encode())  
        file.seek(0)
        info = tarfile.TarInfo(locale + self._SUFFIX)
        info.size = len(file.getvalue())
        self._tar.addfile(info, file)

    def find(self, locale: str) -> bool:
        """ Find the file for the given locale.
        
        If the locale is not found, it will try to find the parent locale, e.g. if
        "de-DE" is not found, "de" is tried. If the parent locale is not found, it will
        continue until the root locale is reached. If the root locale is not found, a
        KeyError is raised.

        Args:
            locale: The locale to find.
        """
        loc = self._normalize(locale)
        locales = self.get_locales()
        while loc not in locales and loc and self._SEPARATOR in loc:
            loc = self._SEPARATOR.join(loc.split(self._SEPARATOR)[:-1])
        if loc in locales:
            return loc + self._SUFFIX
        raise KeyError(f'Locale "{locale}" not found.')

    def get(self, locale: str) -> list[Option]:
        """ Return the options for the given locale.
        
        Args:
            locale: The locale for which to return the options.        
        """
        filename = self.find(locale)
        file = self._tar.extractfile(filename)
        data = json.loads(file.read().decode())
        return [Option(**e) for e in data]
    
    def language_count(self) -> int:
        """ Return the number of languages available (not number of locales!)."""
        members = self.get_locales()
        return len({e.split(self._SEPARATOR)[0] for e in members})
    
    def get_locales(self) -> list[str]:
        """ Return a list of all locales in the archive."""
        locales = [e.removesuffix(self._SUFFIX) for e in self.get_members()]
        return [None if e == self._AUTONYMS else e for e in locales]
    
    def get_members(self) -> list[str]:
        """ Return a list of all filenames in the archive."""
        return self._tar.getnames()
    
    @classmethod
    def load(cls, archive: Path | str, locale: str) -> list[Option]:
        """ Load options for a given locale from the archive.
        
        Args:
            archive: The archive to load the options from.
            locale: The locale for which to load the options.
        """
        with cls(archive, "r") as file:
            return file.get(locale)

    def __enter__(self):
        filename = str(self._filename)
        self._tar = tarfile.open(filename, f"{self._mode}:gz", encoding="utf-8") 
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._tar.close()