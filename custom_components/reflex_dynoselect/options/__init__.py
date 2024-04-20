import json
from pathlib import Path

class Options(list):
    def __init__(self, name: str) -> None:
        filename = Path(__file__).parent / f"{name}.json"
        with open(str(filename), "r", encoding="utf-8") as file:
            data = json.load(file)
        super().__init__(data)

class TimezoneOptions(Options):
    _PREFIX = "timezones_"

    def __init__(self, locale: str) -> None:
        super().__init__(self._PREFIX + locale.replace("-", "_"))