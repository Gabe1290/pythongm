"""Guard: code that goes into the frozen IDE never imports a module by a computed name.

PyInstaller (and Nuitka) bundle only the modules they can SEE being imported.
`importlib.import_module(f"config.blockly_block_i18n_{lang}")` looked fine from
source, and every test passed, but the 1.6.2 downloads died at startup on every
launch: "ModuleNotFoundError: No module named 'config.blockly_block_i18n_pl'"
(2026-11-23). Write plain imports instead (see config/ui_names/__init__.py).

Extensions and plugins are copied as DATA and loaded from files by
events/plugin_loader.py, so they are not part of this rule.
"""

import ast
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Not frozen into the IDE executable (tests, dev tools, data-loaded extensions,
# virtualenvs and build output).
EXCLUDED_TOP = {"tests", "tools", "scripts", "venv", ".venv", "build", "dist",
                "extensions", "plugins", "samples", "Tutorials", "wiki", "docs",
                ".git", "node_modules"}


def _frozen_sources():
    for path in REPO.rglob("*.py"):
        rel = path.relative_to(REPO)
        if rel.parts[0] in EXCLUDED_TOP or any(p.startswith(".") for p in rel.parts):
            continue
        yield path, rel


def _computed_imports(tree):
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not node.args:
            continue
        func = node.func
        name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "")
        if name in ("import_module", "__import__") and not isinstance(node.args[0], ast.Constant):
            yield node.lineno


def test_no_import_by_computed_name_in_frozen_code():
    offenders = []
    for path, rel in _frozen_sources():
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            continue
        offenders += [f"{rel}:{line}" for line in _computed_imports(tree)]
    assert not offenders, (
        "a frozen build cannot see these imports, so it leaves the modules out: "
        + ", ".join(offenders))


def test_every_blockly_language_module_is_listed_and_loads():
    from config import blockly_translations as bt
    on_disk = {p.stem.rsplit("_", 1)[1]
               for p in (REPO / "config").glob("blockly_block_i18n_*.py")}
    assert on_disk == set(bt.MODULE_LANGUAGES)
    for lang in bt.MODULE_LANGUAGES:
        assert bt.CATEGORY_TRANSLATIONS.get(lang), lang
