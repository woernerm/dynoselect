from json import dump
from pathlib import Path

from locales import get_locale_table
from timezone import TimezoneTable

DATA_DIR = Path.cwd() / "custom_components" / "reflex_dynoselect" / "options"
LOCALE_FILE = DATA_DIR / "locales.json"

def write_data(filename: Path, data: any):
    with open(str(filename), 'w', encoding='utf-8') as file:
        dump(data, file, ensure_ascii=False)

def write_locale_options():
    write_data(LOCALE_FILE, get_locale_table())

table = TimezoneTable("de-DE")
data = table.asdict()
a = 1