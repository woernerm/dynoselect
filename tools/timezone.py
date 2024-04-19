from zoneinfo import available_timezones, ZoneInfo
from datetime import datetime
from collections import defaultdict
import re

from babel.dates import get_timezone_location, get_timezone_name
from babel.lists import format_list
from babel.core import Locale, get_global


class TimezoneTable:
    _REGEX_INVALID = re.compile(r"([A-Z]{3,}|\d+)")

    def __init__(self, locale: str) -> None:
        self.locale = Locale.parse(locale, sep="-")

    def canonical(self, dbname: str) -> str:
        """Determine the canonical timezone name."""
        return get_global('zone_aliases').get(dbname, dbname)

    def tzname(self, dbname: str) -> str:
        """Localized timezone name with representative city."""
        tz = ZoneInfo(dbname)
        canonical = self.canonical(dbname)

        # Get a representative city for the timezone.
        city = get_timezone_location(tz, locale=self.locale, return_city=True)        
        # Get the territory of the timezone and its translated name.
        territory = get_global('zone_territories').get(canonical, "")
        territory = self.locale.territories.get(territory, "")

        # Filter zones that are not associated with a territory.
        if not city or not territory:
            return tz, None
        
        # Filter zones that contain numbers like GMT+1.
        if self._REGEX_INVALID.search(city) or self._REGEX_INVALID.search(territory):
            return tz, None

        return tz, [city, territory]

    def default_offset_s(self, timezone: ZoneInfo) -> int:
        """UTC offset (without daylight saving time, see tzinfo docs) in seconds."""
        ref = datetime.now().astimezone(timezone)
        return int((ref.utcoffset() - ref.dst()).total_seconds())
    
    def humanize(self, tz: ZoneInfo, locations: list[str]):
        """Return timezone names as UTC offset with represenative cities."""
        offset_s = self.default_offset_s(tz)
        hours = int(offset_s // 3600)
        minutes = int(offset_s % 3600 // 60)
        locs = [locs] if isinstance(locations, str) else locations

        localized = format_list(locs, "unit-short", self.locale)
        return f"{localized} (UTC{hours:+03}:{minutes:02d})" 

    def asdict(self) -> dict[str, str]:
        """ Returns a dictionary of timezones.

        The keys are the IANA timezone names and the values are localized, human 
        readable names. The human readable names are generated using a standard,
        localized timezone name and the location of the timezone as city name.
        """

        zones = defaultdict(set)
        zones = dict([self.tzname(canonical) for canonical in available_timezones()])
        zones = {k: v for k, v in zones.items() if v is not None}

        nntest = defaultdict(list)
        for k, v in zones.items():
            nntest[",".join(v)].append(k)
        return zones
