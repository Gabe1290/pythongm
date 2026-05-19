#!/usr/bin/env python3
"""
Shared tutorials-path resolution for the tutorial dialog and panel.

`TutorialDialog` and `TutorialPanel` carried a byte-identical
`_get_localized_tutorials_path`. They are unrelated widgets (QDialog vs
QWidget) and the method only needs the base path, so the logic lives here as
a pure function; each widget keeps a thin `_get_localized_tutorials_path`
wrapper.

Note: the audit also listed `load_tutorial_list` as duplicated — it is not.
The two implementations diverge materially (panel reads `tutorial.json` in the
folder fallback and the dialog does not; the dialog disables placeholder list
items and resets a description label; different `folder` values), so folding
them would change behaviour, not preserve it. Left untouched by design.
"""


def localized_tutorials_path(base_tutorials_path):
    """Get the tutorials path for the current language, falling back to English"""
    if not base_tutorials_path:
        return None

    # Get current language
    try:
        from core.language_manager import get_language_manager
        language_manager = get_language_manager()
        current_lang = language_manager.get_current_language()
    except Exception:
        current_lang = 'en'

    # Check for language-specific folder
    if current_lang and current_lang != 'en':
        localized_path = base_tutorials_path / current_lang
        if localized_path.exists() and (localized_path / "index.json").exists():
            return localized_path

    # Fall back to base path (English)
    return base_tutorials_path
