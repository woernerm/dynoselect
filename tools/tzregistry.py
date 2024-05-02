from zoneinfo import available_timezones, ZoneInfo
from collections import defaultdict
import re

from babel.dates import get_timezone_location, get_timezone_name
from babel.lists import format_list
from babel.core import Locale, get_global

from utils import request
from reflex_dynoselect.options import Option


class DeprecatedTimezones(dict):
    """Mapping of deprecated timezones to current timezones.
    
    The keys are the deprecated timezone names and the values are the current
    timezone names.
    """

    URL = "ftp://ftp.iana.org/tz/tzdata-latest.tar.gz"
    """URL to the latest timezone data."""

    TARMEMBER = "backward"
    """Name of the file in the tar archive that contains deprecated timezone names."""

    DELIMITER = "\t"

    def __init__(self) -> None:
        with request(self.URL) as tar:
            file = tar.extractfile(self.TARMEMBER).read().decode("utf-8")
        
        for line in file.splitlines():
            if not line.lower().startswith("link") or not line:
                continue
            # Some lines have erroneous tabs, so we need to filter them out.
            components = [e for e in line.split(self.DELIMITER) if e]
            _, target, oldname = components[:3]
            self[oldname.strip()] = target.strip()


class TimezoneCityRegistry(dict):
    """Mapping of timezones to the most populous cities within these zones.
    
    The dataset is from the GeoNames database at https://www.geonames.org/. For each
    timezone, cities over 500 inhabitants sorted by descending population, their
    population and alternative names in various languages are given.   
    """

    CATEGORY = "cities15000"

    URL = f"https://download.geonames.org/export/dump/{CATEGORY}.zip"

    ZIPMEMBER = f"{CATEGORY}.txt"

    DELIMITER = "\t"

    COL_NAME = 1
    COL_ALTNAMES = 3
    COL_POPULATION = 14
    COL_TIMEZONE = 17
    COL_FEATURE_CODE = 7
    COL_COUNTRY_CODE = 8

    KEY_NAME = "name"
    KEY_ALTNAMES = "altnames"
    KEY_POPULATION = "population"

    FEATURES = [
        "PPL", "PPLA", "PPLA2", "PPLA3", "PPLA4", "PPLC", "PPLCH", "PPLF", 
        "PPLG", "PPLR", "PPLS"
    ]

    def __init__(self, maxcities: int) -> None:
        with request(self.URL) as zip:
            with zip.open(self.ZIPMEMBER) as file:
                content = file.read().decode("utf-8")

        self._timezones = defaultdict(list)

        for line in content.splitlines():
            components = line.split(self.DELIMITER)
            name = components[self.COL_NAME]
            altnames = components[self.COL_ALTNAMES]
            population = int(components[self.COL_POPULATION])
            timezone = components[self.COL_TIMEZONE]
            feature = components[self.COL_FEATURE_CODE]

            if feature not in self.FEATURES:
                continue # Only allow cities, towns, etc.

            self._timezones[timezone].append({
                self.KEY_NAME: name, 
                self.KEY_ALTNAMES: altnames, 
                self.KEY_POPULATION: population
            })
        
        for timezone, data in self._timezones.items():
            # Sort by descending population
            entries = list(
                sorted(data, key=lambda x: x[self.KEY_POPULATION], reverse=True)
            )
            self[timezone] = entries[:maxcities]


class TimezoneRegistry(list):
    """ Mapping of canonical timezone names to localized names.
    
    The keys are canonical IANA timezone names and the values are localized, human 
    readable names optimized according to the recommendations given by 
    https://www.nngroup.com/articles/time-zone-selectors/    
    Deprecated timezone names and ETC/GMT+x timezones are excluded.
    """
    _REGEX_INVALID = re.compile(r"([A-Z]{3,}|\d+)")

    _DEPRECATED = None
    _CITIES = None

    def __init__(self, locale: str, maxcities: int = 0) -> None:
        self.locale = Locale.parse(locale, sep="-")

        if TimezoneRegistry._DEPRECATED is None:
            TimezoneRegistry._DEPRECATED = DeprecatedTimezones()

        if TimezoneRegistry._CITIES is None:
            TimezoneRegistry._CITIES = TimezoneCityRegistry(maxcities)

        # Use only non-deprecated IANA timezones, e.g. Europe/Paris.
        canonical = {
            self.canonical(name) for name in available_timezones() 
            if name not in self._DEPRECATED and "/" in name
        }
        zones = defaultdict(set)
        zones = dict([self.tzname(e) for e in canonical]) # Ensure uniqueness.
        zones = [(k, v,) for k, v in zones.items() if v is not None]
        zones = sorted(zones, key=lambda x: x[1])

        for canonical, label in zones:
            self.append(self.entry(canonical, label))

    def values(self) -> set[str]:
        return {e.value for e in self}

    def entry(self, canonical: str, label: str) -> dict:
        """Create a dictionary entry for a timezone."""
        cities = self._CITIES.get(canonical, [])
        
        # Add cities with the same timezone. However use only cities  that improve the 
        # search, i.e. those that would not be found in canonical name or label anyway.
        key = TimezoneCityRegistry.KEY_NAME
        keywords = [
            e[key] for e in cities if e[key] not in canonical and e[key] not in label
        ]
        data = {"value": canonical, "label": label}
        # Save space by only mentioning keywords if necessary.
        if keywords:
            data["keywords"] = keywords 
        return Option(**data)

    def canonical(self, dbname: str) -> str:
        """Determine the canonical timezone name."""
        return get_global('zone_aliases').get(dbname, dbname)

    def tzname(self, canonical: str) -> str:
        """Localized timezone name with representative city."""
        tz = ZoneInfo(canonical)

        # Get a representative city for the timezone.
        try:
            city = get_timezone_location(tz, locale=self.locale, return_city=True)        
            # Get the territory of the timezone and its translated name.
            territory = get_global('zone_territories').get(canonical, "")
            territory = self.locale.territories.get(territory, "")
        except KeyError:
            return None, None

        # Filter zones that are not associated with a territory.
        if not city or not territory:
            return None, None
        
        # Filter zones that contain numbers like GMT+1.
        if self._REGEX_INVALID.search(city) or self._REGEX_INVALID.search(territory):
            name = get_timezone_name(tz, locale=self.locale)
            if not self._REGEX_INVALID.search(name):
                return canonical, name
            return None, None
        
        pattern = self.locale.list_patterns.get("standard", {}).get("middle", "{}, {}")
        listed = pattern.format(city, territory)
        return canonical, listed

