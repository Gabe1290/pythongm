"""The compiled IDE's start-up profile.

The IDE built on GitHub (``PyGameMaker.spec``) bundles ``build_config/build_profile.json`` at the top
of the bundle. It sets how a fresh install STARTS:

* ``edition``: the edition used while the user has not chosen one -- also for the sample list, which
  otherwise shows every sample on an unset edition;
* ``extensions_enabled_by_default``: ``false`` makes every extension start switched off.

These are DEFAULTS: a choice the user saved in Preferences wins. Running from source has no profile
file, so nothing changes there, and neither does an exported game (its bundle does not carry the
file).

The Welcome tab's sample list always hides a sample whose extension is actually switched off
(config/editions.py's filter_samples_for_edition), source or compiled -- that one is unconditional,
not part of this profile, since a disabled extension's actions are genuinely unregistered either way.
"""

import json
import sys
from pathlib import Path

FILE_NAME = "build_profile.json"


def profile_path() -> Path:
    """Where the profile lives: the top of a PyInstaller bundle (the repo root when running from
    source, where there is no such file)."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / FILE_NAME
    return Path(__file__).resolve().parent.parent / FILE_NAME


def load_profile() -> dict:
    """The profile, or ``{}`` when there is none or it cannot be read."""
    try:
        data = json.loads(profile_path().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def edition(fallback=None):
    """The profile's edition key, else ``fallback``."""
    value = load_profile().get("edition")
    return value if isinstance(value, str) and value else fallback


def extension_default(manifest_default: bool) -> bool:
    """Whether an extension the user never switched should load."""
    if load_profile().get("extensions_enabled_by_default") is False:
        return False
    return manifest_default
