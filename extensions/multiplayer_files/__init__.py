#!/usr/bin/env python3
"""File Exchange Multiplayer -- 1990s-DOS-style turn-based multiplayer
over a shared folder (a mapped network drive, a synced Dropbox/OneDrive
folder, a school SMB share), for classroom LANs where a firewall blocks
the direct peer-to-peer connections extensions/multiplayer_lan/ needs.
See docs/MULTIPLAYER_FILE_EXCHANGE_PLAN.md for the full design and the
historical grounding (VGA Planets, Stars!, PBM/PBEM Diplomacy) this
pattern comes from.

Host-authoritative rounds, not a live connection: host_game_files /
join_game_files / leave_game_files, a join/welcome handshake, a
shared-variable blackboard staged per round and folded in by the host
(set_shared_var_files / get_shared_var_files / end_turn), custom messages
staged the same way (send_network_message_files), and the round/status
globals + lifecycle events below
(docs/MULTIPLAYER_FILE_EXCHANGE_PLAN.md "Proposed phases" Phases 1-2).

Hooks used: the generic per-frame hook (runtime/extension_hooks.py's
register_frame_update) -- the actual disk I/O inside it is gated to once
a second (state.POLL_INTERVAL), not every frame, since a real
network-drive round trip can cost 5-50ms and there is no live connection
to poll continuously. Also the room-change hook, migrating a live session
across change_room/restart_current_room the same way multiplayer_lan
does (M1, docs/FULL_AUDIT_2026-09-07.md). No room renderer -- this draws
nothing.
"""

PLUGIN_NAME = "File Exchange Multiplayer"

# Labels of its events in the generic Blockly "extension event" drop-down
_EVENT_LABELS = {          # language -> {event: label}; one entry per further language
    "fr": {
        "file_session_started": "Session par fichiers démarrée",
        "player_joined_files": "Joueur arrivé (fichiers)",
        "round_resolved": "Manche terminée",
        "player_skipped_round": "Joueur a passé la manche",
        "network_message_files": "Message réseau (échange de fichiers)",
        "file_session_lost": "Session par fichiers perdue",
    },
    "de": {
        "file_session_started": "Dateisitzung gestartet",
        "player_joined_files": "Spieler beigetreten (Dateien)",
        "round_resolved": "Runde abgeschlossen",
        "player_skipped_round": "Spieler hat die Runde ausgelassen",
        "network_message_files": "Netzwerknachricht (Dateiaustausch)",
        "file_session_lost": "Dateisitzung verloren",
    },
    "es": {
        "file_session_started": "Sesión por archivos iniciada",
        "player_joined_files": "Jugador unido (archivos)",
        "round_resolved": "Ronda terminada",
        "player_skipped_round": "Jugador omitió la ronda",
        "network_message_files": "Mensaje de red (intercambio de archivos)",
        "file_session_lost": "Sesión por archivos perdida",
    },
    "it": {
        "file_session_started": "Sessione a file avviata",
        "player_joined_files": "Giocatore entrato (file)",
        "round_resolved": "Turno concluso",
        "player_skipped_round": "Giocatore ha saltato il turno",
        "network_message_files": "Messaggio di rete (scambio di file)",
        "file_session_lost": "Sessione a file persa",
    },
    "pt": {
        "file_session_started": "Sessão por arquivos iniciada",
        "player_joined_files": "Jogador entrou (arquivos)",
        "round_resolved": "Rodada encerrada",
        "player_skipped_round": "Jogador pulou a rodada",
        "network_message_files": "Mensagem de rede (troca de arquivos)",
        "file_session_lost": "Sessão por arquivos perdida",
    },
    "ru": {
        "file_session_started": "Файловая сессия начата",
        "player_joined_files": "Игрок присоединился (файлы)",
        "round_resolved": "Раунд завершён",
        "player_skipped_round": "Игрок пропустил раунд",
        "network_message_files": "Сообщение по сети (обмен файлами)",
        "file_session_lost": "Файловая сессия потеряна",
    },
    "uk": {
        "file_session_started": "Файлову сесію розпочато",
        "player_joined_files": "Гравець приєднався (файли)",
        "round_resolved": "Раунд завершено",
        "player_skipped_round": "Гравець пропустив раунд",
        "network_message_files": "Повідомлення мережею (обмін файлами)",
        "file_session_lost": "Файлову сесію втрачено",
    },
    "sl": {
        "file_session_started": "Datotečna seja začeta",
        "player_joined_files": "Igralec se je pridružil (datoteke)",
        "round_resolved": "Krog končan",
        "player_skipped_round": "Igralec je izpustil krog",
        "network_message_files": "Omrežno sporočilo (izmenjava datotek)",
        "file_session_lost": "Datotečna seja izgubljena",
    },
    "ja": {
        "file_session_started": "ファイルセッション開始",
        "player_joined_files": "プレイヤーが参加（ファイル）",
        "round_resolved": "ラウンド終了",
        "player_skipped_round": "プレイヤーがラウンドをスキップ",
        "network_message_files": "ネットワークメッセージ（ファイル交換）",
        "file_session_lost": "ファイルセッションが切れた",
    },
}
PLUGIN_GENERATED_BLOCK_TRANSLATIONS = {"events": {
    name: {lang: labels[name] for lang, labels in _EVENT_LABELS.items() if name in labels}
    for name in _EVENT_LABELS["fr"]}}

# colour of its generated Blockly blocks and drawer (else grey)
PLUGIN_BLOCK_CATEGORY_COLORS = {"Network": "#2D93C8"}

from events.event_types import EventType

from .actions import PLUGIN_ACTIONS
from .handlers import (
    PluginExecutor, _frame_update_after_update, _frame_update_before_step,
    _on_room_change,
)

_CATEGORY = "Network"

PLUGIN_EVENTS = {
    "file_session_started": EventType(
        name="file_session_started", display_name="File Session Started",
        description="A client was welcomed by the host -- global.player_id "
                        "is now set. Client-only: the host already knows "
                        "synchronously, right after \"Host a Game (File "
                        "Exchange)\" returns, that hosting worked, so this "
                        "never fires on the host.",
        category=_CATEGORY, icon="🗂️", parameters=[]),
    "player_joined_files": EventType(
        name="player_joined_files", display_name="Player Joined (Files)",
        description="A player joined the game. global.network_sender "
                        "is their number, global.network_player_name "
                        "their name.",
        category=_CATEGORY, icon="➕", parameters=[]),
    "round_resolved": EventType(
        name="round_resolved", display_name="Round Resolved",
        description="A round finished: every joined player's move (or "
                        "the round deadline) was reached and the host "
                        "published new state. Fires on every machine "
                        "once it picks up the update. "
                        "global.round_number is the new round.",
        category=_CATEGORY, icon="🔄", parameters=[]),
    "player_skipped_round": EventType(
        name="player_skipped_round", display_name="Player Skipped Round",
        description="A player's round deadline lapsed without a move "
                        "this round. global.network_sender is their "
                        "number.",
        category=_CATEGORY, icon="⏭️", parameters=[]),
    "network_message_files": EventType(
        name="network_message_files", display_name="Network Message (File Exchange)",
        description="A custom message arrived (sent with \"Send a "
                        "Network Message (File Exchange)\"). "
                        "global.network_event is its label, "
                        "global.network_data its data, "
                        "global.network_sender the sender.",
        category=_CATEGORY, icon="✉️", parameters=[]),
    "file_session_lost": EventType(
        name="file_session_lost", display_name="File Session Lost",
        description="The shared folder became unreadable -- the drive "
                        "disconnected, a permission changed, and so on.",
        category=_CATEGORY, icon="⚠️", parameters=[]),
}

PLUGIN_FRAME_UPDATES = [
    (_frame_update_before_step, "before_step"),
    (_frame_update_after_update, "after_update"),
]

# Migrates a live session across a room change instead of it being
# silently orphaned on the room object being left -- same reasoning as
# multiplayer_lan's own M1 fix (docs/FULL_AUDIT_2026-09-07.md).
PLUGIN_ROOM_CHANGE_HOOKS = [_on_room_change]
