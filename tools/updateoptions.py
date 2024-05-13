from pathlib import Path
from sys import path
path.append(str(Path(__file__).parent.parent / "custom_components" ))

from rich.console import Console
from localeregistry import LocaleRegistry
from tzregistry import TimezoneRegistry

from reflex_dynoselect.options import (
    LocalizedOptions, TIMEZONE_OPTION_PATH, LOCALE_OPTION_PATH, NONE_LOCALE
)

MIN_LANGUAGES = 0.9

def write_timezone_options(archive: Path):
    """ Write database file for timezone options. """
    out = Console()
    # Use the English locale as reference for what timezones should be available.
    with out.status("Determining reference timezones..."):
        ref_zones = TimezoneRegistry("en-US").values()
    out.print(f"Found {len(ref_zones)} reference timezones.")

    with LocalizedOptions(archive, "w") as file:
        for locale in LocaleRegistry().values():
            out.print(f"Writing timezone options for {locale}... ", end="")
            try:
                zones = TimezoneRegistry(locale)
                if bool(ref_zones - zones.values()):
                    raise Exception(f"Too few/different timezones ({len(zones)})")
                # Only store translations for reference timezones.
                zones = [e for e in zones if e.value in ref_zones]
                file.add(locale, zones)
                out.print("[green]Ok.")
            except Exception as e:
                out.print(f"[red]Failed: {e}")
        out.print("Stored ", file.language_count(), " languages.")

def write_locale_options(archive: Path):
    """ Write database file for locale options. """
    out = Console()
    # Only use locales which can be translated into all locales that have at least
    # MIN_LANGUAGES percent of all translations.
    with out.status(f"Determining {NONE_LOCALE}..."):
        autonyms = LocaleRegistry(None).values()
        lang_count = len(autonyms) * MIN_LANGUAGES

    with out.status("Determining reference locales that are widely translatable... "):
        registries = {e: LocaleRegistry(e) for e in autonyms.union({None})}
        valid_regs = [r for r in registries.values() if len(r) >= lang_count]
        refs = autonyms.intersection(*[e.values() for e in valid_regs]) 
    out.print(f"Found {len(refs)} locales that are widely translatable...")

    with LocalizedOptions(archive, "w") as file:
        for locale in refs.union({None}):
            out.print(f'Writing locale options for {locale or NONE_LOCALE}... ', end="")
            try:
                data = registries.get(locale, None)
                missing = refs - data.values()
                if missing: # Does the locale miss any values?
                    raise Exception(f"Missing {len(missing)} translations.")
                
                # Only store translations for reference locales.
                data = [e for e in data if e.value in refs]
                file.add((locale or NONE_LOCALE), data)
                out.print("[green]Ok.")
            except Exception as e:
                out.print(f"[red]Failed: {e}")
        out.print(f"Stored {len(refs)} locales in {file.language_count()} languages.")

write_locale_options(LOCALE_OPTION_PATH)
write_timezone_options(TIMEZONE_OPTION_PATH)