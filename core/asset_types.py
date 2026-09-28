"""Registry of side-file asset types an extension can add to a project.

Core knows four asset kinds that keep their payload in ``<type>/<name>.json``
next to ``project.json``: rooms, objects, sprites (each with its own bespoke
loader in ``ProjectManager``) and, historically, playgrounds. A feature that
needs a *new kind of asset* — a robot arena, say — used to have to edit
``ProjectManager``/``AssetManager`` by hand. Now it registers one here
(``PLUGIN_ASSET_TYPES`` in an extension, see ``extensions/README.md``) and
the generic load/save/strip/side-file paths pick it up.

Deliberately Qt-free, like ``runtime/extension_hooks``: both the loader and
``ProjectManager`` import it with no cycle risk.
"""
from dataclasses import dataclass
from typing import Dict, List, Tuple

from core.logger import get_logger

logger = get_logger(__name__)

# The types ProjectManager loads/saves with its own hand-written code.
CORE_SIDE_FILE_TYPES: Tuple[str, ...] = ("rooms", "objects", "sprites")


@dataclass(frozen=True)
class SideFileAssetType:
    """One registered asset kind stored as ``<plural>/<name>.json``.

    ``file_keys`` are merged from the side file into the project.json entry
    on load; ``strip_keys`` are removed from the project.json entry on save
    (they live in the side file only). Keys outside ``strip_keys`` stay in
    project.json as the asset's summary.
    """
    plural: str
    singular: str
    description: str
    file_keys: Tuple[str, ...]
    strip_keys: Tuple[str, ...]

    @property
    def dir_name(self) -> str:
        return self.plural


_registered: Dict[str, SideFileAssetType] = {}


def register_side_file_asset_type(spec: SideFileAssetType) -> None:
    """Register (idempotently) an extension-owned side-file asset type."""
    if not isinstance(spec, SideFileAssetType):
        logger.error(f"Asset type is not a SideFileAssetType: {spec!r}")
        return
    if spec.plural in CORE_SIDE_FILE_TYPES:
        logger.error(f"Asset type {spec.plural!r} is a core type; not re-registered")
        return
    existing = _registered.get(spec.plural)
    if existing is not None and existing != spec:
        logger.error(f"Asset type {spec.plural!r} already registered differently; kept first")
        return
    _registered[spec.plural] = spec
    logger.debug(f"Registered side-file asset type: {spec.plural}")


def get_registered_asset_types() -> List[SideFileAssetType]:
    """Registered types, in registration order (a copy)."""
    return list(_registered.values())


def clear_registered_asset_types() -> None:
    """Drop every registered type. For tests and for reloading extensions."""
    _registered.clear()


def side_file_type_names() -> Tuple[str, ...]:
    """Every plural whose assets keep a ``<plural>/<name>.json`` side file:
    the core three plus whatever is registered. The single source for the
    delete/rename/duplicate side-file cleanup paths."""
    return CORE_SIDE_FILE_TYPES + tuple(_registered)


def plural_to_singular() -> Dict[str, str]:
    """``{plural: singular}`` for every registered type."""
    return {p: s.singular for p, s in _registered.items()}


# Playgrounds (the Thymio robot arena) register here for now so on-disk
# behaviour is unchanged; docs/THYMIO_EXTENSION_PLAN.md Stage C5 moves this
# call into extensions/thymio/ and core then carries no playground code.
register_side_file_asset_type(SideFileAssetType(
    plural="playgrounds",
    singular="playground",
    description="Aseba playground environments",
    file_keys=("arena", "colors", "walls", "robots"),
    strip_keys=("walls", "robots", "colors"),
))
