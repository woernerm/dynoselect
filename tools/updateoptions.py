from json import dump
from pathlib import Path

from locales import get_locale_table
from timezone import TimezoneOptions, TimezoneCities

DATA_DIR = Path.cwd() / "custom_components" / "reflex_dynoselect" / "options"
LOCALE_FILE = DATA_DIR / "locales.json"

TIMEZONE_FILE = DATA_DIR / "timezones_{}.json"

def write_data(filename: Path, data: any):
    with open(str(filename), 'w', encoding='utf-8') as file:
        dump(data, file, ensure_ascii=False)

def write_locale_options():
    write_data(LOCALE_FILE, get_locale_table())

def write_timezone_options(locale: str, maxcities: int):
    loc = locale.replace("-", "_")
    write_data(str(TIMEZONE_FILE).format(loc), TimezoneOptions(locale, maxcities))

write_timezone_options("en-US", 5)
