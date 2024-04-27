from json import dump
from pathlib import Path

from locales import get_locale_table
from timezone import TimezoneRegistry, TimezoneCityRegistry

DATA_DIR = Path.cwd() / "custom_components" / "reflex_dynoselect" / "options"
LOCALE_FILE = DATA_DIR / "locales.json"

TIMEZONE_FILE = DATA_DIR / "timezones_{}.json"

def write_data(filename: Path, data: any):
    with open(str(filename), 'w', encoding='utf-8') as file:
        dump(data, file, ensure_ascii=False)

def write_locale_options(data):
    write_data(LOCALE_FILE, data)

def write_timezone_options(locale: str, maxcities: int):
    loc = locale.replace("-", "_")
    write_data(str(TIMEZONE_FILE).format(loc), TimezoneRegistry(locale, maxcities))

print("Writing locales...")
locales = get_locale_table()
write_locale_options(locales)

for option in locales:
    locale = option["value"]
    print(f"Writing timezones for {locale}... ", end="")
    try:
        write_timezone_options(locale, 5)
        print("Ok.")
    except Exception as e:
        print(f"Failed: {e}")
