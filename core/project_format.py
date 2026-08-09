"""Project-file format-version guard.

Protects a 1.0-line PyGameMaker build from crashing or silently corrupting
a project saved by a newer format it doesn't understand — see
docs/extension_compat_2_0/PLAN.md, Task 1. A too-new project must be
refused before any code path could load it and later resave over it,
stripping fields this build doesn't recognize.
"""


class ProjectTooNewError(Exception):
    """Raised when a project's format_version exceeds SUPPORTED_FORMAT."""

    def __init__(self, fmt):
        self.fmt = fmt
        super().__init__(
            f"Project format {fmt[0]}.{fmt[1]} is newer than this build "
            f"supports (up to {SUPPORTED_FORMAT[0]}.{SUPPORTED_FORMAT[1]})"
        )


# This build understands any 1.x project format. Bump the minor number
# (never the app version) if a future field is added that a 1.x reader
# genuinely cannot tolerate; ordinary additive fields don't need a bump —
# readers are expected to stay tolerant of unknown keys (see
# ProjectManager._validate_project_data and _prepare_project_data_for_save,
# which already round-trip unrecognized top-level keys and action types).
SUPPORTED_FORMAT = (1, 9)


def check_project_format(project_dict):
    """Parse and validate a loaded project dict's ``format_version``.

    Absence of the key means a pre-format_version (1.0-era) project — the
    graceful default this whole guard exists to preserve. Returns the
    parsed ``(major, minor)`` tuple on success. Raises
    :class:`ProjectTooNewError` if the format exceeds what this build
    understands; the caller must abort the load without proceeding to any
    code path that could resave over the file.
    """
    raw = project_dict.get("format_version", "1.0")
    try:
        parts = [int(p) for p in str(raw).split(".")]
        fmt = (parts[0], parts[1] if len(parts) > 1 else 0)
    except (ValueError, IndexError):
        fmt = (1, 0)
    if fmt > SUPPORTED_FORMAT:
        raise ProjectTooNewError(fmt)
    return fmt
