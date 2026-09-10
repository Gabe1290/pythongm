#!/usr/bin/env python3
"""The built-in connect / lobby screen for file-exchange multiplayer
(docs/MULTIPLAYER_FILE_EXCHANGE_PLAN.md Phase 4).

Shown when a game calls ``join_game_files`` with folder ``"auto"``
(client: type the shared folder's path) or ``host_game_files`` with
``show_lobby`` on (host: see who's joined, then Démarrer). Mirrors
`extensions/multiplayer_lan/connect_screen.py`'s own shape closely --
same modal-pygame-screen approach, same palette, same
``roster_fn``/``tick_fn`` decoupling from the session so this widget is
testable with plain pygame surfaces and synthetic events -- but there is
no server list here: file-exchange has no discovery (out of scope for
Phase 1, see the plan doc's "Explicitly out of scope"), so the client
side is a single validated text field for the folder path, not a
scannable server list. On a headless runner (no ``screen``) it degrades
to "just connect with whatever path was already given".
"""

import os
from pathlib import Path

try:
    import pygame
except ImportError:
    pygame = None

# palette -- identical to multiplayer_lan/connect_screen.py's, so the two
# extensions' modal screens read as siblings rather than looking like two
# different apps.
_BG = (18, 20, 28)
_PANEL = (30, 34, 46)
_TEXT = (232, 236, 244)
_DIM = (150, 158, 172)
_ACCENT = (90, 170, 250)
_OK = (80, 190, 120)
_ERR = (240, 120, 110)


class _Button:
    __slots__ = ("rect", "label", "enabled")

    def __init__(self, rect, label, enabled=True):
        self.rect = rect
        self.label = label
        self.enabled = enabled


class FileConnectScreen:
    def __init__(self, mode, screen, *, folder="", manual_default="",
                 roster_fn=None, tick_fn=None):
        self.mode = mode                       # "host" | "client"
        self.screen = screen
        self.folder = str(folder or "")        # host mode: shown, not editable
        self.roster_fn = roster_fn or (lambda: [(0, "Hôte")])
        self.tick_fn = tick_fn or (lambda: None)

        self.manual_path = str(manual_default or "")
        self.status = ""
        self.status_kind = "info"              # info | ok | error

        self._active = False
        self.result = None                    # "folder:<path>" | "start" | "cancel"
        self._buttons = {}
        self._font = None
        self._font_big = None

    # -- fonts ----------------------------------------------------------

    def _fonts(self):
        if self._font is None and pygame is not None:
            if not pygame.font.get_init():
                pygame.font.init()
            self._font = pygame.font.SysFont(None, 22)
            self._font_big = pygame.font.SysFont(None, 34)
        return self._font, self._font_big

    # -- event handling -----------------------------------------------

    def handle_event(self, event):
        """Process one pygame event. Sets ``self.result`` and returns it
        when the screen is done; otherwise returns None."""
        if pygame is None:
            return None
        if event.type == pygame.QUIT:
            return self._finish("cancel")
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return self._finish("cancel")
            if self.mode == "client":
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    return self._connect_now()
                if event.key == pygame.K_BACKSPACE:
                    self.manual_path = self.manual_path[:-1]
                else:
                    # getattr, not a bare event.unicode -- a synthetic or
                    # replayed KEYDOWN from elsewhere in a real pygame
                    # event queue (this screen only ever reads
                    # pygame.event.get(), the process-wide queue, not one
                    # scoped to this screen) is not guaranteed to carry a
                    # unicode attribute; found via the full suite, not
                    # this file's own tests, which always construct it.
                    ch = getattr(event, "unicode", "")
                    # A folder path is free-form (letters, digits, spaces,
                    # \\/:.-_ and more for a real UNC path) -- unlike the
                    # LAN screen's address field, this deliberately does
                    # NOT restrict which characters are accepted, only
                    # excludes control characters.
                    if ch and ch.isprintable():
                        self.manual_path += ch
            elif self.mode == "host" and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                return self._finish("start")
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            for name, btn in self._buttons.items():
                if btn.enabled and btn.rect.collidepoint(pos):
                    if name == "connect":
                        return self._connect_now()
                    if name == "start":
                        return self._finish("start")
                    if name == "cancel":
                        return self._finish("cancel")
        return None

    def _connect_now(self):
        path = self.manual_path.strip()
        if not path:
            self.set_status("Entrez le chemin du dossier partagé", "error")
            return None
        p = Path(path)
        if not p.is_dir():
            self.set_status("Ce dossier n'existe pas", "error")
            return None
        if not os.access(str(p), os.W_OK):
            self.set_status("Ce dossier n'est pas accessible en écriture", "error")
            return None
        return self._finish("folder:%s" % path)

    def _finish(self, result):
        self.result = result
        self._active = False
        return result

    def set_status(self, text, kind="info"):
        self.status = text
        self.status_kind = kind

    # -- drawing ----------------------------------------------------

    def draw(self):
        if pygame is None or self.screen is None:
            return
        font, big = self._fonts()
        w, h = self.screen.get_size()
        self.screen.fill(_BG)
        panel = pygame.Rect(int(w * 0.08), int(h * 0.08), int(w * 0.84), int(h * 0.84))
        pygame.draw.rect(self.screen, _PANEL, panel, border_radius=10)

        title = "Héberger une partie (fichiers)" if self.mode == "host" \
            else "Rejoindre une partie (fichiers)"
        self.screen.blit(big.render(title, True, _TEXT), (panel.x + 24, panel.y + 18))

        y = panel.y + 66
        self._buttons = {}

        if self.mode == "client":
            self.screen.blit(font.render("Chemin du dossier partagé :", True, _DIM),
                             (panel.x + 24, y))
            y += 26
            box = pygame.Rect(panel.x + 24, y, panel.width - 48, 30)
            pygame.draw.rect(self.screen, _BG, box, border_radius=4)
            pygame.draw.rect(self.screen, _ACCENT, box, width=1, border_radius=4)
            self.screen.blit(font.render(self.manual_path or " ", True, _TEXT),
                             (box.x + 8, box.y + 6))
            y += 42
            connect_btn = _Button(pygame.Rect(panel.x + 24, y, 160, 32), "Se connecter")
            self._buttons["connect"] = connect_btn
            self._draw_button(connect_btn)
            y += 46
        else:
            self.tick_fn()
            roster = self.roster_fn()
            self.screen.blit(font.render("Dossier : %s" % self.folder, True, _DIM),
                             (panel.x + 24, y))
            y += 28
            self.screen.blit(font.render("En attente de joueurs…", True, _DIM),
                             (panel.x + 24, y))
            y += 28
            for slot, name in roster:
                tag = "Hôte" if slot == 0 else "Joueur %d" % slot
                self.screen.blit(font.render("• %s — %s" % (tag, name), True, _TEXT),
                                 (panel.x + 40, y))
                y += 26
            y += 12
            start_btn = _Button(pygame.Rect(panel.x + 24, y, 200, 32), "Démarrer")
            self._buttons["start"] = start_btn
            self._draw_button(start_btn)
            y += 46

        # status line
        if self.status:
            col = {"ok": _OK, "error": _ERR}.get(self.status_kind, _DIM)
            self.screen.blit(font.render(self.status, True, col), (panel.x + 24, y))

        # footer: cancel only -- no "this machine" line, unlike the LAN
        # screen, since no address/port is involved here at all.
        foot = panel.bottom - 40
        cancel_btn = _Button(pygame.Rect(panel.right - 140, foot - 4, 116, 30), "Annuler")
        self._buttons["cancel"] = cancel_btn
        self._draw_button(cancel_btn)

    def _draw_button(self, btn):
        col = _ACCENT if btn.enabled else _DIM
        pygame.draw.rect(self.screen, col, btn.rect, border_radius=6)
        font, _ = self._fonts()
        surf = font.render(btn.label, True, _BG)
        self.screen.blit(surf, (btn.rect.centerx - surf.get_width() // 2,
                                btn.rect.centery - surf.get_height() // 2))

    # -- modal loop ------------------------------------------------

    def run(self, clock=None):
        """Block until the user picks an action (or the screen has no
        display, in which case connect straight away with whatever
        manual path was already given). Returns the result string."""
        if pygame is None or self.screen is None:
            if self.mode == "host":
                return "start"
            path = self.manual_path.strip()
            return ("folder:%s" % path) if path else "cancel"
        if clock is None:
            clock = pygame.time.Clock()
        self._active = True
        self.result = None
        while self._active:
            for event in pygame.event.get():
                self.handle_event(event)
            self.draw()
            try:
                pygame.display.flip()
            except pygame.error:
                break
            clock.tick(30)
        return self.result or "cancel"
