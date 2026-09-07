"""M12, docs/FULL_AUDIT_2026-09-07.md: French text shown to students must
carry its real accents (a standing project rule -- this is educational
software for French-speaking students and teachers). Two spots had lost
theirs:

- extensions/multiplayer_lan/handlers.py's two host_game/join_game
  failure messages (shown in a blocking dialog when a port bind or a
  connection attempt fails) -- "heberger", "peut-etre deja utilise",
  "systeme", "reseau prive", "Verifiez", "l'hote", "lance", "meme
  reseau".
- events/action_editor.py's MessageTranslationsDialog._get_language_list
  ImportError fallback -- "Francais", "Espanol", "Portugues",
  "Slovenscina", plus "Russian"/"Ukrainian" used in English instead of
  the native "Русский"/"Українська".

Checked at the source-text level (not via a live QTranslator -- these are
plain Python strings, not self.tr() calls) since that's what actually
reaches the player/author. Byte/codepoint-level string containment,
following tests/test_extension_action_i18n.py's own reasoning: a cp1252
console can make correct UTF-8 look broken and vice versa, so the
assertions read the source file directly as UTF-8 rather than trusting
terminal rendering.
"""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _source(rel_path):
    return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


class TestMultiplayerNotifyMessagesAreAccented:
    def setup_method(self):
        self.source = _source("extensions/multiplayer_lan/handlers.py")

    def test_host_failure_message_is_accented(self):
        assert "Impossible d'héberger sur le port" in self.source
        assert "peut-être déjà utilisé" in self.source
        assert "système bloque" in self.source
        assert "réseau privé" in self.source
        # The old, unaccented forms must be gone, not just the accented
        # forms added alongside them.
        assert "Impossible d'heberger" not in self.source
        assert "peut-etre deja utilise" not in self.source
        assert "systeme bloque" not in self.source
        assert "reseau prive" not in self.source

    def test_join_failure_message_is_accented(self):
        assert "Impossible de se connecter à" in self.source
        assert "Vérifiez que l'hôte a bien lancé la partie" in self.source
        assert "même réseau filaire" in self.source
        assert "Impossible de se connecter a " not in self.source
        assert "Verifiez que l'hote a bien lance" not in self.source
        assert "meme reseau filaire" not in self.source


class TestActionEditorLanguageFallbackIsAccented:
    def setup_method(self):
        self.source = _source("events/action_editor.py")

    def test_fallback_language_names_match_language_manager(self):
        """Native names, matching LanguageManager.LANGUAGE_INFO exactly --
        this fallback exists so the dialog degrades gracefully if that
        import ever fails, not so it shows a DIFFERENT, wrong name."""
        from core.language_manager import LanguageManager

        for code in ("fr", "es", "pt", "sl", "ru", "uk"):
            native_name = LanguageManager.LANGUAGE_INFO[code][0]
            assert "('%s', '%s')" % (code, native_name) in self.source, (
                "fallback entry for %r must be %r" % (code, native_name))

    def test_old_unaccented_forms_are_gone(self):
        for bad in ("Francais", "Espanol", "Portugues", "Slovenscina"):
            assert bad not in self.source, (
                "%r is the unaccented form -- it must not appear anywhere "
                "in the fallback language list" % bad)

    def test_fallback_list_actually_returns_accented_names(self):
        """Behavioural check, not just a source grep: force the ImportError
        branch and read what the method really returns."""
        import importlib
        import sys

        import events.action_editor as mod

        real_import = __import__

        def _blocked_import(name, *args, **kwargs):
            if name == "core.language_manager":
                raise ImportError("simulated for this test")
            return real_import(name, *args, **kwargs)

        dialog = mod.MessageTranslationsDialog.__new__(mod.MessageTranslationsDialog)
        import builtins
        original = builtins.__import__
        builtins.__import__ = _blocked_import
        try:
            result = dialog._get_language_list()
        finally:
            builtins.__import__ = original

        by_code = dict(result)
        assert by_code["fr"] == "Français"
        assert by_code["es"] == "Español"
        assert by_code["pt"] == "Português"
        assert by_code["sl"] == "Slovenščina"
        assert by_code["ru"] == "Русский"
        assert by_code["uk"] == "Українська"
