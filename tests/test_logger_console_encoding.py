"""A log message must reach the console even when the console is cp1252.

Log messages here carry emoji -- `logger.error(f"❌ IMPORT ERROR: {msg}")` in
core/asset_manager.py and many more. On Windows the console is cp1252, so
encoding one raises UnicodeEncodeError inside `StreamHandler.emit`, which
catches it and prints `--- Logging error ---` and a traceback INSTEAD of the
message.

That is user-facing at the default level (WARNING): the emoji are on error and
warning calls, not just debug ones. A teacher whose sprite import failed got a
logging traceback where the reason should have been.

Found while running a frozen build of the engine on a Windows console
(2026-08-17), where the same fault filled the output with
`UnicodeEncodeError: 'charmap' codec can't encode character '\\U0001f4e6'`.
"""
import io
import logging
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from core.logger import ConsoleSafeHandler, PyGMFormatter  # noqa: E402


class _Cp1252Stream(io.TextIOWrapper):
    """A stream that behaves like a real Windows console: strict cp1252."""

    def __init__(self):
        super().__init__(io.BytesIO(), encoding="cp1252", errors="strict",
                         newline="")

    def value(self):
        self.flush()
        return self.buffer.getvalue().decode("cp1252")


def _record(msg, level=logging.ERROR):
    return logging.LogRecord("pygm.test", level, __file__, 1, msg, None, None)


def _emit(msg, level=logging.ERROR):
    stream = _Cp1252Stream()
    handler = ConsoleSafeHandler(stream)
    handler.setFormatter(PyGMFormatter())
    # handleError would swallow the very failure under test, so make it loud.
    handler.handleError = lambda record: (_ for _ in ()).throw(
        AssertionError("handler failed to emit %r" % msg))
    handler.emit(_record(msg, level))
    return stream.value()


def test_emoji_message_still_reaches_a_cp1252_console():
    out = _emit("❌ IMPORT ERROR: sprite.png is not a valid image")
    # The words are what matter; the emoji may degrade to '?'.
    assert "IMPORT ERROR" in out
    assert "sprite.png is not a valid image" in out
    assert "ERROR" in out


def test_the_unencodable_character_is_replaced_not_dropped_silently():
    out = _emit("\U0001f4e6 Registered 75 modular action handlers")
    assert "Registered 75 modular action handlers" in out


def test_accented_text_is_preserved_exactly():
    """cp1252 CAN encode French accents, so they must survive untouched --
    the sanitizer must not flatten text it does not need to touch. This
    repo's French UI strings depend on that."""
    out = _emit("Impossible de charger la scène « niveau »")
    assert "scène" in out
    assert "« niveau »" in out


def test_plain_ascii_is_untouched():
    out = _emit("Loaded project: maze_1")
    assert "Loaded project: maze_1" in out


def test_a_utf8_console_keeps_the_emoji():
    """The fix must not degrade output on Linux/macOS, where the console
    handles emoji fine."""
    stream = io.TextIOWrapper(io.BytesIO(), encoding="utf-8", newline="")
    handler = ConsoleSafeHandler(stream)
    handler.setFormatter(PyGMFormatter())
    handler.emit(_record("❌ IMPORT ERROR"))
    stream.flush()
    assert "❌" in stream.buffer.getvalue().decode("utf-8")


def test_a_stream_with_no_encoding_attribute_does_not_crash():
    """io.StringIO has no `encoding`; so do several test doubles in this
    suite that pass a fake stream to configure_logging."""
    stream = io.StringIO()
    handler = ConsoleSafeHandler(stream)
    handler.setFormatter(PyGMFormatter())
    handler.emit(_record("❌ IMPORT ERROR"))
    assert "IMPORT ERROR" in stream.getvalue()


def test_configure_logging_installs_the_safe_handler():
    """The class existing is no use if configure_logging still builds a
    plain StreamHandler."""
    import core.logger as logger_module

    stream = _Cp1252Stream()
    logger_module.configure_logging(level=logging.WARNING, stream=stream)
    try:
        installed = logging.getLogger("pygm").handlers
        assert installed, "no handler installed"
        assert all(isinstance(h, ConsoleSafeHandler) for h in installed), (
            "configure_logging must install ConsoleSafeHandler, got %r"
            % [type(h).__name__ for h in installed])
        logging.getLogger("pygm.test").error("❌ REPLACE ERROR: boom")
        assert "REPLACE ERROR: boom" in stream.value()
    finally:
        # Leave logging as the rest of the suite expects it.
        logger_module._logging_configured = False
        logging.getLogger("pygm").handlers.clear()
        logger_module.configure_logging()
