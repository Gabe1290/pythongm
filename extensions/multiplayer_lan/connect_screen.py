#!/usr/bin/env python3
"""The built-in French connect / lobby screen (docs/MULTIPLAYER_LAN_V2_PLAN.md
Phase 6.2).

Shown when a game calls ``join_game`` with host ``"auto"`` (client: pick a
server or type an address) or ``host_game`` with ``show_lobby`` on (host:
wait for players, then Démarrer). It's a **modal** pygame screen -- the
game is frozen while it's up, which is the right UX for choosing a server,
and it sidesteps having to thread input events through the frame-update
hook. On a headless runner (no ``screen``) it degrades to "just connect
with the parameters given".

``ConnectScreen`` is deliberately decoupled from ``NetworkSession``: the
host lobby's roster and per-frame pump come in as callables
(``roster_fn`` / ``tick_fn``), so the widget is testable with plain
pygame surfaces and synthetic events.
"""

import socket

try:
    import pygame
except ImportError:
    pygame = None

from .state import DEFAULT_PORT

# palette
_BG = (18, 20, 28)
_PANEL = (30, 34, 46)
_TEXT = (232, 236, 244)
_DIM = (150, 158, 172)
_ACCENT = (90, 170, 250)
_SEL = (54, 88, 140)
_OK = (80, 190, 120)
_ERR = (240, 120, 110)


def local_ip() -> str:
    """This machine's primary LAN address (no packet is actually sent --
    UDP ``connect`` just picks the outbound interface). Falls back to
    loopback when there's no route."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def _split_addr(text, default_port=DEFAULT_PORT):
    """"1.2.3.4" or "1.2.3.4:45000" -> (ip, port)."""
    text = (text or "").strip()
    if ":" in text:
        ip, _, port = text.rpartition(":")
        try:
            return ip.strip() or "127.0.0.1", int(port)
        except ValueError:
            return ip.strip() or "127.0.0.1", default_port
    return text or "127.0.0.1", default_port


class _Button:
    __slots__ = ("rect", "label", "enabled")

    def __init__(self, rect, label, enabled=True):
        self.rect = rect
        self.label = label
        self.enabled = enabled


class ConnectScreen:
    def __init__(self, mode, screen, *, discovery_listener=None,
                 manual_default="", default_port=DEFAULT_PORT,
                 roster_fn=None, tick_fn=None, game_name=""):
        self.mode = mode                       # "host" | "client"
        self.screen = screen
        self.listener = discovery_listener
        self.default_port = int(default_port)
        self.roster_fn = roster_fn or (lambda: [(0, game_name or "Hôte")])
        self.tick_fn = tick_fn or (lambda: None)
        self.game_name = game_name
        self.local_ip = local_ip()

        self.manual_ip = str(manual_default or "")
        self.servers = []
        self.selected = -1
        self.status = ""
        self.status_kind = "info"              # info | ok | error

        self._active = False
        self.result = None                    # "connect:<ip>:<port>" | "start" | "cancel"
        self._buttons = {}
        self._server_rects = []
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
                    self.manual_ip = self.manual_ip[:-1]
                    self.selected = -1
                else:
                    ch = event.unicode
                    if ch and (ch.isdigit() or ch in ".:"):
                        self.manual_ip += ch
                        self.selected = -1
            elif self.mode == "host" and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                return self._finish("start")
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            for idx, rect in enumerate(self._server_rects):
                if rect.collidepoint(pos):
                    if self.selected == idx:        # second click = connect
                        return self._connect_now()
                    self.selected = idx
                    return None
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
        if 0 <= self.selected < len(self.servers):
            s = self.servers[self.selected]
            return self._finish("connect:%s:%d" % (s["ip"], s["port"]))
        if not self.manual_ip.strip():
            self.set_status("Entrez une adresse ou choisissez un serveur", "error")
            return None
        ip, port = _split_addr(self.manual_ip, self.default_port)
        return self._finish("connect:%s:%d" % (ip, port))

    def _finish(self, result):
        self.result = result
        self._active = False
        return result

    def set_status(self, text, kind="info"):
        self.status = text
        self.status_kind = kind

    # -- drawing ----------------------------------------------------

    def _refresh_servers(self):
        if self.mode == "client" and self.listener is not None:
            self.servers = self.listener.servers()
            if self.selected >= len(self.servers):
                self.selected = -1

    def draw(self):
        if pygame is None or self.screen is None:
            return
        self._refresh_servers()
        font, big = self._fonts()
        w, h = self.screen.get_size()
        self.screen.fill(_BG)
        panel = pygame.Rect(int(w * 0.08), int(h * 0.08), int(w * 0.84), int(h * 0.84))
        pygame.draw.rect(self.screen, _PANEL, panel, border_radius=10)

        title = "Héberger une partie" if self.mode == "host" else "Rejoindre une partie"
        self.screen.blit(big.render(title, True, _TEXT), (panel.x + 24, panel.y + 18))

        y = panel.y + 66
        self._server_rects = []
        self._buttons = {}

        if self.mode == "client":
            self.screen.blit(font.render("Serveurs détectés :", True, _DIM), (panel.x + 24, y))
            y += 26
            if not self.servers:
                self.screen.blit(font.render("(aucun — utilisez l'adresse ci-dessous)",
                                             True, _DIM), (panel.x + 40, y))
                y += 26
            for idx, s in enumerate(self.servers):
                row = pygame.Rect(panel.x + 24, y, panel.width - 48, 26)
                if idx == self.selected:
                    pygame.draw.rect(self.screen, _SEL, row, border_radius=4)
                label = "%s  —  %d/%d joueurs  —  %s:%d" % (
                    s["name"], s["players"], s["max"], s["ip"], s["port"])
                self.screen.blit(font.render(label, True, _TEXT), (row.x + 8, row.y + 4))
                self._server_rects.append(row)
                y += 30

            y += 12
            self.screen.blit(font.render("Adresse de l'hôte :", True, _DIM), (panel.x + 24, y))
            y += 26
            box = pygame.Rect(panel.x + 24, y, panel.width - 220, 30)
            pygame.draw.rect(self.screen, _BG, box, border_radius=4)
            pygame.draw.rect(self.screen, _ACCENT, box, width=1, border_radius=4)
            self.screen.blit(font.render(self.manual_ip or " ", True, _TEXT),
                             (box.x + 8, box.y + 6))
            connect_btn = _Button(pygame.Rect(box.right + 16, y, 160, 30), "Se connecter")
            self._buttons["connect"] = connect_btn
            self._draw_button(connect_btn)
            y += 46
        else:
            self.tick_fn()
            roster = self.roster_fn()
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

        # footer: this machine + cancel
        foot = panel.bottom - 40
        self.screen.blit(font.render("Cette machine : %s" % self.local_ip, True, _DIM),
                         (panel.x + 24, foot))
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
        display, in which case connect straight away with the manual
        address). Returns the result string."""
        if pygame is None or self.screen is None:
            if self.mode == "host":
                return "start"
            ip, port = _split_addr(self.manual_ip, self.default_port)
            return "connect:%s:%d" % (ip or "127.0.0.1", port)
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
