"""Diffing logic shared between the Blockly round-trip audit tool
(tools/audit_blockly_roundtrip.py) and the live safety net in
blockly_widget.py (docs/BLOCKLY_BLOCK_AUDIT_2026-10-08.md, U0).

A single source for "what did Blockly lose": the audit tool uses it to find
every bundled sample object's losses in bulk; the widget uses it at runtime,
right after syncing an object's real events into Blockly, to decide whether
editing here would be safe. Kept dependency-free (no Qt, no project imports)
so both call sites — one headless/offline, one inside the running app — can
import it the same way.
"""
from typing import Any, Dict, List, Tuple

Issue = Tuple[str, str, Any, Any]  # (where, kind, a, b)

NESTED = ('then_actions', 'else_actions', 'sub_actions', 'actions')

# Equivalent spellings that are not losses (each pinned against its source by
# tests/test_blockly_round_trip_safety.py, since this module stays
# dependency-free):
# - action-name aliases the runtime resolves (ActionExecutor.ACTION_ALIASES)
ACTION_NAME_ALIASES = {
    'room_goto_next': 'next_room', 'goto_next_room': 'next_room',
    'room_goto_previous': 'previous_room', 'goto_previous_room': 'previous_room',
    'room_restart': 'restart_room', 'room_goto': 'goto_room',
}
# - GameMaker numeric comparison codes (importers/gmk_mappings.GM_COMPARISON_OPS),
#   which every engine now translates (audit B18)
GM_OPERATION_CODES = {'0': 'equal', '1': 'less', '2': 'greater',
                      '3': 'less_equal', '4': 'greater_equal', '5': 'not_equal'}


def norm(v):
    """Normalize a parameter value so representational differences (the
    string "4" vs the number 4, "self" vs "sel") don't count as real losses."""
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        s = v.strip()
        # "true" equals True: every engine reads it as true. Deliberately NOT
        # "false" -> False: some parameters (change_instance perform_events,
        # audit B17) use plain truthiness, where the text "false" is TRUE.
        if s.lower() == 'true':
            return True
        try:
            return float(s)
        except ValueError:
            return {'self': 'sel', 'instance': 'sel'}.get(s, s)
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, list):
        return [norm(x) for x in v]
    if isinstance(v, dict):
        return {k: norm(x) for k, x in v.items()}
    return v


def flat_events(ev: Dict[str, Any]) -> Dict[str, List[dict]]:
    """Flatten an events dict into {event_key: [actions]}, with nested
    sub-events (keyboard/alarm) as "event/subtype" keys. A flat alarm_N key
    is treated the same as nested alarm/alarm_N -- the runtime accepts both
    (game_runner's alarm lookup checks both forms), so that shape alone isn't
    a real loss."""
    out = {}
    for name, data in ev.items():
        if not isinstance(data, dict):
            continue
        if isinstance(data.get('actions'), list):
            out[name] = data['actions']
        for k, sub in data.items():
            if k != 'actions' and isinstance(sub, dict) and isinstance(sub.get('actions'), list):
                out[f"{name}/{k.lower()}"] = sub['actions']
    return {(k.replace('alarm_', 'alarm/alarm_', 1) if k.startswith('alarm_') else k): v
            for k, v in out.items()}


def walk(a_list, b_list, where: str, issues: List[Issue]):
    """Compare two action lists (before vs. after) action-by-action,
    recursing into nested action lists (then/else/sub_actions)."""
    a_list = [x for x in (a_list if isinstance(a_list, list) else []) if isinstance(x, dict)]
    b_list = [x for x in (b_list if isinstance(b_list, list) else []) if isinstance(x, dict)]
    for i in range(max(len(a_list), len(b_list))):
        a = a_list[i] if i < len(a_list) else None
        b = b_list[i] if i < len(b_list) else None
        an = a and (a.get('action') or a.get('type'))
        bn = b and (b.get('action') or b.get('type'))
        an = ACTION_NAME_ALIASES.get(an, an)
        bn = ACTION_NAME_ALIASES.get(bn, bn)
        if an != bn:
            issues.append((where, 'action-lost' if bn is None else 'action-changed', an, bn))
            return
        # The engine dispatches on the "action" key only; an action re-saved
        # under "type" silently stops running (audit B9: the Thymio Blockly
        # generators did exactly this, and comparing names alone missed it).
        if ('action' in a) != ('action' in b):
            issues.append((where, 'action-key-changed', an,
                           'type' if 'action' in a else 'action'))
        ap, bp = a.get('parameters') or {}, b.get('parameters') or {}
        for k in sorted(set(ap) | set(bp)):
            if k in NESTED:
                walk(ap.get(k), bp.get(k), f"{where}>{an}.{k}", issues)
            elif k not in bp:
                issues.append((where, 'param-dropped', an, k))
            elif k == 'operation' and (
                    GM_OPERATION_CODES.get(str(ap[k]).strip(), ap[k])
                    == GM_OPERATION_CODES.get(str(bp[k]).strip(), bp[k])):
                continue
            elif k in ap and norm(ap[k]) != norm(bp[k]):
                issues.append((where, 'param-changed', an, f"{k}: {ap[k]!r} -> {bp[k]!r}"))


def diff_events(before: Dict[str, Any], after: Dict[str, Any]) -> List[Issue]:
    """Every way `after` (Blockly's reconstruction) differs from `before`
    (the real events). An empty list means Blockly can reproduce `before`
    exactly -- it's safe to let a block edit save over it."""
    issues: List[Issue] = []
    fb, fa = flat_events(before or {}), flat_events(after or {})
    for ev in sorted(set(fb) | set(fa)):
        if ev not in fa:
            issues.append((ev, 'event-dropped', ev.split('/')[0], ev))
        elif ev in fb:
            walk(fb[ev], fa[ev], ev, issues)
    return issues


_LABELS = {
    'action-lost': "the {a} action (and anything nested inside it)",
    'action-changed': "{a} being replaced with {b}",
    'event-dropped': "the whole {b} event",
    'param-dropped': "{a}'s {b} setting",
    'param-changed': "{a}'s {b}",
}


def summarize_issues(issues: List[Issue], limit: int = 3) -> List[str]:
    """Up to `limit` short, deduplicated human-readable descriptions of what
    would be lost -- for a UI message, not a developer log. Dynamic (action/
    parameter names from the project), so callers interpolate this into a
    translated template rather than translating these strings themselves."""
    seen: List[str] = []
    for where, kind, a, b in issues:
        label = _LABELS.get(kind, "{a}/{b}").format(a=a, b=b)
        if label not in seen:
            seen.append(label)
        if len(seen) >= limit:
            break
    return seen
