#!/usr/bin/env bash
#
# Cut a PyGameMaker release: bump every version location, add a CHANGELOG
# stub, commit, tag, and push. The Build workflow (.github/workflows/build.yml)
# fires on the pushed tag and recompiles + publishes the downloadable binaries.
#
# Usage (run from anywhere in the repo):
#   scripts/release.sh 1.0.1            # final release  -> tag v1.0.1 (Latest)
#   scripts/release.sh 1.0.1-rc.1       # pre-release    -> tag v1.0.1-rc.1
#   scripts/release.sh 1.0.1 --dry-run  # apply edits, show diff, then revert
#   scripts/release.sh 1.0.1 --no-push  # commit + tag locally, don't push
#   scripts/release.sh 1.0.1 -y         # skip the confirmation prompt
#
# Updates: __init__.py, pyproject.toml, version_info.txt, README.md badge,
# and CHANGELOG.md. (Flyers / test PDFs / wiki are separate — not release gates.)
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

# ---- parse args -----------------------------------------------------------
VER=""; DRY_RUN=0; NO_PUSH=0; ASSUME_YES=0
for a in "$@"; do
  case "$a" in
    --dry-run) DRY_RUN=1 ;;
    --no-push) NO_PUSH=1 ;;
    -y|--yes)  ASSUME_YES=1 ;;
    -*)        echo "unknown flag: $a" >&2; exit 2 ;;
    *)         VER="$a" ;;
  esac
done

if [[ -z "$VER" ]]; then
  echo "usage: scripts/release.sh <version> [--dry-run] [--no-push] [-y]" >&2
  exit 2
fi

# ---- validate + derive the version representations ------------------------
if [[ ! "$VER" =~ ^([0-9]+)\.([0-9]+)\.([0-9]+)(-(rc|alpha|beta|dev)\.([0-9]+))?$ ]]; then
  echo "error: version must look like 1.2.3 or 1.2.3-rc.1 (got '$VER')" >&2
  exit 1
fi
MAJOR="${BASH_REMATCH[1]}"; MINOR="${BASH_REMATCH[2]}"; PATCH="${BASH_REMATCH[3]}"
PRETYPE="${BASH_REMATCH[5]}"; PRENUM="${BASH_REMATCH[6]}"

BUILD=0; [[ -n "$PRETYPE" ]] && BUILD="$PRENUM"     # 4th field of the Windows version tuple
case "$PRETYPE" in
  "")    PEP440="$MAJOR.$MINOR.$PATCH" ;;            # pyproject.toml (PEP 440)
  rc)    PEP440="$MAJOR.$MINOR.${PATCH}rc${PRENUM}" ;;
  alpha) PEP440="$MAJOR.$MINOR.${PATCH}a${PRENUM}" ;;
  beta)  PEP440="$MAJOR.$MINOR.${PATCH}b${PRENUM}" ;;
  dev)   PEP440="$MAJOR.$MINOR.${PATCH}.dev${PRENUM}" ;;
esac
BADGE="${VER//-/--}"          # shields.io escapes '-' as '--'
TAG="v$VER"
DATE="$(date +%Y-%m-%d)"
FILES=(__init__.py utils/__init__.py core/__init__.py pyproject.toml version_info.txt README.md CHANGELOG.md)

echo "Releasing $VER"
echo "  tag           : $TAG"
echo "  __version__   : $VER"
echo "  pyproject     : $PEP440"
echo "  version tuple : ($MAJOR, $MINOR, $PATCH, $BUILD)"
echo "  README badge  : $BADGE"
echo

# ---- preconditions --------------------------------------------------------
if [[ -n "$(git status --porcelain)" ]]; then
  echo "error: working tree is not clean. Commit or stash your changes first" >&2
  echo "       (the release commit should contain only the version bump)." >&2
  exit 1
fi
if git rev-parse -q --verify "refs/tags/$TAG" >/dev/null; then
  echo "error: tag $TAG already exists." >&2
  exit 1
fi

# ---- apply edits ----------------------------------------------------------
sed_i() { sed "$1" "$2" > "$2.tmp" && mv "$2.tmp" "$2"; }

sed_i "s/^__version__ = \".*\"/__version__ = \"$VER\"/" __init__.py
# utils/core carry their own __version__ (the About dialog and Welcome tab
# read utils'); they went stale at "1.0.0-rc.13" when 1.0.0 shipped because
# this script didn't know about them.
sed_i "s/^__version__ = \".*\"/__version__ = \"$VER\"/" utils/__init__.py
sed_i "s/^__version__ = \".*\"/__version__ = \"$VER\"/" core/__init__.py
sed_i "s/^version = \".*\"/version = \"$PEP440\"/" pyproject.toml
sed_i "s/filevers=([0-9, ]*)/filevers=($MAJOR, $MINOR, $PATCH, $BUILD)/" version_info.txt
sed_i "s/prodvers=([0-9, ]*)/prodvers=($MAJOR, $MINOR, $PATCH, $BUILD)/" version_info.txt
sed_i "s/\\(u'FileVersion', u'\\)[^']*'/\\1$VER'/" version_info.txt
sed_i "s/\\(u'ProductVersion', u'\\)[^']*'/\\1$VER'/" version_info.txt
sed_i "s#badge/version-.*-blue#badge/version-$BADGE-blue#" README.md

awk -v ver="$VER" -v date="$DATE" '
  /^## \[[0-9]/ && !done {
    print "## [" ver "] - " date
    print ""
    print "### Fixed"
    print "- "
    print ""
    done = 1
  }
  { print }
' CHANGELOG.md > CHANGELOG.md.tmp && mv CHANGELOG.md.tmp CHANGELOG.md

# ---- verify every edit landed (guards against pattern drift) --------------
fail() { echo "error: expected change not found: $1" >&2; git checkout -- "${FILES[@]}"; exit 1; }
grep -q "^__version__ = \"$VER\"$"                     __init__.py      || fail "__init__.py __version__"
grep -q "^__version__ = \"$VER\"$"                     utils/__init__.py || fail "utils/__init__.py __version__"
grep -q "^__version__ = \"$VER\"$"                     core/__init__.py || fail "core/__init__.py __version__"
grep -q "^version = \"$PEP440\"$"                      pyproject.toml   || fail "pyproject version"
grep -q "filevers=($MAJOR, $MINOR, $PATCH, $BUILD)"    version_info.txt || fail "version_info filevers"
grep -q "u'FileVersion', u'$VER'"                      version_info.txt || fail "version_info FileVersion"
grep -q "badge/version-$BADGE-blue"                    README.md        || fail "README badge"
grep -q "^## \[$VER\] - $DATE$"                        CHANGELOG.md     || fail "CHANGELOG stub"

echo "=== proposed changes ==="
git --no-pager diff -- "${FILES[@]}"
echo

if [[ "$DRY_RUN" == 1 ]]; then
  git checkout -- "${FILES[@]}"
  echo "Dry run — changes reverted, no commit/tag/push."
  exit 0
fi

# ---- confirm, commit, tag, push -------------------------------------------
if [[ "$ASSUME_YES" != 1 ]]; then
  echo "Tip: edit CHANGELOG.md now to flesh out the $VER notes (the Build"
  echo "workflow uses that section as the GitHub Release body)."
  action="commit + tag $TAG"
  [[ "$NO_PUSH" != 1 ]] && action="$action + push (main + tag)"
  read -r -p "Proceed with $action? [y/N] " ans
  [[ "$ans" == y* || "$ans" == Y* ]] || { git checkout -- "${FILES[@]}"; echo "Aborted, changes reverted."; exit 1; }
fi

git add "${FILES[@]}"
git commit -q -m "release: $VER"
git tag -a "$TAG" -m "PyGameMaker $VER"
echo "Committed and tagged $TAG."

if [[ "$NO_PUSH" == 1 ]]; then
  echo "Not pushing (--no-push). When ready:  git push origin HEAD && git push origin $TAG"
  exit 0
fi

git push origin HEAD
git push origin "$TAG"
echo "Pushed. GitHub is now building binaries for $TAG — watch:"
echo "  https://github.com/Gabe1290/pythongm/actions"
