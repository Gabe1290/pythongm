#!/usr/bin/env python3
"""Export readable session notes from Claude Code transcripts.

Extracts the user prompts and Claude's explanation text (skipping tool-call
noise) from a session's .jsonl transcript into a Markdown file under
docs/session-notes/, one file per session, named <start-date>-<id8>.md.
Idempotent: re-running on the same transcript overwrites the same file, so
a session's notes stay current as it grows.

Two ways to run:

1. As a Claude Code Stop hook (no args). Reads the hook JSON from stdin
   (which carries transcript_path) and writes the current session's notes.
   Silent on stdout; always exits 0 so it never blocks the session.

2. Manually, for backfill:  python3 scripts/export_session_notes.py FILE...
   where FILE is one or more transcript .jsonl paths. On any machine:
       python3 scripts/export_session_notes.py ~/.claude/projects/*/*.jsonl
   Sessions with no substantive assistant text are skipped.

Stdlib only; works on Python 3.8+.
"""

import json
import os
import socket
import sys
from pathlib import Path

MIN_ASSISTANT_CHARS = 300  # skip trivial sessions below this

NOISE_PREFIXES = (
    "<system-reminder",
    "<command-name>",
    "<local-command",
    "<task-notification",
    "Caveat: The messages below",
    "[Request interrupted",
    "No response requested",
)


def repo_root():
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env:
        return Path(env)
    return Path(__file__).resolve().parent.parent


def extract(transcript):
    """Return (start_date, cwd, merged message list) or None if unusable."""
    entries = []
    start_ts = None
    cwd = None
    try:
        fh = open(transcript, encoding="utf-8")
    except OSError:
        return None
    with fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                o = json.loads(line)
            except json.JSONDecodeError:
                continue
            ts = o.get("timestamp", "")
            if start_ts is None and ts:
                start_ts = ts
            if cwd is None and o.get("cwd"):
                cwd = o["cwd"]
            if o.get("isSidechain"):
                continue  # subagent traffic
            t = o.get("type")
            msg = o.get("message") or {}
            content = msg.get("content")
            if t == "user":
                if isinstance(content, str):
                    text = content
                elif isinstance(content, list):
                    text = "\n".join(
                        c.get("text", "")
                        for c in content
                        if isinstance(c, dict) and c.get("type") == "text"
                    )
                else:
                    continue
                text = text.strip()
                if not text or text.startswith(NOISE_PREFIXES):
                    continue
                entries.append(("user", ts, text))
            elif t == "assistant":
                if not isinstance(content, list):
                    continue
                text = "\n\n".join(
                    c.get("text", "").strip()
                    for c in content
                    if isinstance(c, dict)
                    and c.get("type") == "text"
                    and c.get("text", "").strip()
                )
                if text:
                    entries.append(("assistant", ts, text))

    if start_ts is None:
        return None

    # merge consecutive same-role entries (assistant text between tool calls)
    merged = []
    for role, ts, text in entries:
        if merged and merged[-1][0] == role:
            merged[-1] = (role, merged[-1][1], merged[-1][2] + "\n\n" + text)
        else:
            merged.append((role, ts, text))
    return start_ts[:10], cwd or "?", merged


def write_notes(transcript, out_dir):
    """Extract one transcript; returns the output path or None if skipped."""
    result = extract(transcript)
    if result is None:
        return None
    start_date, cwd, merged = result
    total = sum(len(t) for r, _, t in merged if r == "assistant")
    if total < MIN_ASSISTANT_CHARS:
        return None

    sid = Path(transcript).stem
    out = out_dir / "{}-{}.md".format(start_date, sid[:8])
    out_dir.mkdir(parents=True, exist_ok=True)

    # never clobber a hand-curated file: put <!-- curated --> on a line of
    # its own near the top of a notes file and the extractor leaves it alone
    # (must be the whole line — the generated header merely *mentions* the
    # marker in backticks, which must not trip the guard)
    if out.exists():
        try:
            head = out.read_text(encoding="utf-8", errors="replace")[:500]
            if any(l.strip() == "<!-- curated -->" for l in head.splitlines()):
                return None
        except OSError:
            pass

    lines = [
        "# Session notes — {} (`{}`)".format(start_date, sid[:8]),
        "",
        "Auto-extracted from the Claude Code transcript. Machine: `{}`, "
        "project dir: `{}`.".format(socket.gethostname(), cwd),
        "User messages are quoted; the rest is Claude's explanation text",
        "(tool calls and results omitted). Curate freely, then add",
        "`<!-- curated -->` near the top so the extractor won't overwrite it.",
        "",
        "---",
        "",
    ]
    for role, ts, text in merged:
        day = ts[:10] if ts else "?"
        if role == "user":
            lines.append("## [{}] User".format(day))
            lines.append("")
            lines.extend("> " + l for l in text.splitlines())
        else:
            lines.append("### Claude")
            lines.append("")
            lines.append(text)
            lines.append("")
            lines.append("---")
        lines.append("")

    out.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return out


def main():
    out_dir = repo_root() / "docs" / "session-notes"

    if len(sys.argv) > 1:  # manual/backfill mode
        written = skipped = 0
        for arg in sys.argv[1:]:
            p = write_notes(Path(arg), out_dir)
            if p:
                written += 1
                print("wrote {}".format(p))
            else:
                skipped += 1
        print("{} written, {} skipped (trivial/unreadable)".format(written, skipped))
        return

    # hook mode: stdin carries the hook JSON
    try:
        payload = json.load(sys.stdin)
        transcript = payload.get("transcript_path")
        if transcript:
            write_notes(Path(transcript), out_dir)
    except Exception:
        pass  # a notes hook must never break the session


if __name__ == "__main__":
    main()
