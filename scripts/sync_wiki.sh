#!/usr/bin/env bash
#
# Keep the repo's wiki/ source folder in sync with the live GitHub wiki.
#
# The GitHub wiki is a SEPARATE git repo (…/pythongm.wiki.git). Editing the
# repo's wiki/ folder does NOT update the published wiki, and vice-versa — so
# the two drift apart unless someone syncs them. This script does that.
#
# Usage (run from anywhere in the repo):
#   scripts/sync_wiki.sh check   # default: report drift, exit 1 if out of sync
#   scripts/sync_wiki.sh pull    # live wiki  -> repo wiki/   (then commit wiki/)
#   scripts/sync_wiki.sh push    # repo wiki/ -> live wiki    (commits + pushes the wiki repo)
#
# Note: copy is additive/overwrite — page *deletions* or *renames* are not
# propagated automatically; handle those by hand on both sides.
set -euo pipefail

WIKI_REMOTE="https://github.com/Gabe1290/pythongm.wiki.git"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REPO_WIKI="$REPO_ROOT/wiki"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
git clone --quiet --depth 1 "$WIKI_REMOTE" "$TMP/live"
LIVE="$TMP/live"

case "${1:-check}" in
  check)
    if diff -rq "$LIVE" "$REPO_WIKI" --exclude=.git >/dev/null 2>&1; then
      echo "OK: wiki/ is in sync with the live wiki."
    else
      echo "DRIFT: wiki/ differs from the live wiki —"
      diff -rq "$LIVE" "$REPO_WIKI" --exclude=.git || true
      exit 1
    fi
    ;;
  pull)
    cp "$LIVE"/*.md "$REPO_WIKI"/
    echo "Pulled live wiki -> wiki/. Review, then commit:"
    echo "    git add wiki/ && git commit -m 'docs(wiki): sync from live wiki'"
    ;;
  push)
    cp "$REPO_WIKI"/*.md "$LIVE"/
    git -C "$LIVE" add -A
    if git -C "$LIVE" diff --cached --quiet; then
      echo "Nothing to push — live wiki already matches wiki/."
    else
      # Inherit the committer identity from the main repo (fresh clone has none).
      name="$(git -C "$REPO_ROOT" config user.name  || echo 'wiki-sync')"
      email="$(git -C "$REPO_ROOT" config user.email || echo 'wiki-sync@local')"
      git -C "$LIVE" -c user.name="$name" -c user.email="$email" \
        commit -q -m "Sync wiki from repo source"
      git -C "$LIVE" push origin master
      echo "OK: pushed wiki/ -> live wiki."
    fi
    ;;
  *)
    echo "usage: $0 {check|pull|push}" >&2
    exit 2
    ;;
esac
