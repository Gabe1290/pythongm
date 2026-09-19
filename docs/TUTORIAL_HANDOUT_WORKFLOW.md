# Tutorial handout round-trip workflow

> **2026-09-19:** sources moved to `docs/handouts/<NN_slug>/{student,teacher,worksheet}.<lang>.md`
> (was `docs/TUTORIAL_01_*`). Older mentions of the old names below are historical.


How a human edit made directly in an .odt draft gets folded back into
the real source (the `.md` files under `docs/handouts/*/*.md`) instead
of living only in that one Writer document. Written 2026-09-17 after
doing this once by hand for `TUTORIAL_01_STUDENT_HANDOUT_FR` and finding
two real bugs in the generator along the way (see "Landmines" below) —
this doc exists so the next round doesn't re-derive any of it.

**The `.md` files stay the single source of truth.** `.odt` and `.pdf`
are *generated* from them (`scripts/generate_tutorial_handouts_odt.py` /
`_pdf.py`). A hand-edited `.odt` is a temporary fork that must get
folded back into its `.md`, not a new parallel source.

## The procedure

1. **Generate a fresh `.odt` draft** from the current `.md`:
   `python scripts/generate_tutorial_handouts_odt.py docs/handouts/01_getting_started/student.en.md`
   (or the no-argument form to regenerate every `TUTORIAL_01_*.md`
   sibling at once).
2. **Commit that draft before anyone edits it.** This is the checkpoint
   both the human's edits and Claude's later diff get measured against.
   Skipping this step is exactly how a hand-edited `.odt` got silently
   destroyed on 2026-09-17 (see "What went wrong once" below) — it must
   not happen again.
3. The user edits the `.odt` freely in LibreOffice/Word — wording,
   structure, even an inserted screenshot.
4. The user tells Claude "I've edited X.odt, sync it" (or similar).
5. **Before touching anything else, Claude backs up the user's edited
   file** — `git add` + a throwaway commit, or at minimum a copied
   file outside the repo's normal generate/overwrite path. Regenerating
   the `.odt` later in this same procedure overwrites it in place;
   without a backup taken *first*, the human's actual edit is gone the
   moment that happens, recoverable only from whatever Claude already
   extracted for the diff.
6. **Extract the edited `.odt` as clean text**:
   `python scripts/extract_odt_text.py docs/X.odt --images-out /tmp/x_images`
   — real ODF-DOM traversal (headings, paragraphs, list items, table
   rows, and any embedded picture's position + real bytes), not a raw
   tag-strip.
7. **Diff that extraction against the current source `.md`**, line by
   line. Catalogue every real change — added/removed sentences,
   reworded phrasing, reordered content, a formality shift (tu/vous in
   French), a new embedded image, a changed notes-line count. Don't
   assume a difference is a typo; only silently correct something that
   plainly isn't a real word (and say so afterward).
8. **A newly embedded image needs a decision, not a guess.** If the
   `.md` has no way to represent what was added (this repo's handout
   pipeline was text-only until 2026-09-17), ask the user how far to
   go — build real support (see "Image support," below, now built) vs.
   a text-only approximation vs. dropping it. Don't silently discard
   visual content someone deliberately added.
9. **Edit the source `.md`** to match every real change, preserving the
   author's exact wording/intent.
10. **Mirror the same substantive edits into every sibling-language
    `.md`** — translate appropriately, don't copy-paste. A formality
    choice specific to one language (French tu/vous) usually doesn't
    have a direct equivalent; a real content change (a removed
    sentence, an added clause) does and should land in every language.
11. **Regenerate every derived output** — every language's `.odt` *and*
    `.pdf` — from the now-corrected `.md` sources, so nothing is left
    stale or inconsistent with another language.
12. **Visually spot-check before declaring done.** Render each PDF page
    and ODT to PNG and actually look (see "How to preview," below) —
    this is what caught the linked-vs-embedded image bug the very run
    it was introduced, before it reached the user.
13. Commit everything (`.md` + regenerated `.odt`/`.pdf`) together,
    describing what changed and why.

## Tools involved

- `scripts/generate_tutorial_handouts_pdf.py` — `.md` → PDF (fpdf2).
- `scripts/generate_tutorial_handouts_odt.py` — `.md` → HTML →
  (headless LibreOffice) → ODT.
- `scripts/extract_odt_text.py` — `.odt` → diffable plain text, plus
  `--images-out DIR` to save every embedded picture's real bytes.
  Requires `odfpy` (`pip install odfpy` — a dev-tool-only dependency,
  same tier as `fpdf2`; neither is in `requirements.txt` /
  `requirements-dev.txt`, both are `scripts/` tooling only).
- LibreOffice (`soffice`) must be on `PATH` for the ODT generator and
  for rendering previews. On a Windows box it typically is **not** on
  `PATH` by default even when installed — add it per session:
  `export PATH="$PATH:/c/Program Files/LibreOffice/program"` (bash) or
  the equivalent in PowerShell.

## How to preview a generated file (no viewer needed)

- **PDF, one page at a time**, via `pymupdf` (`pip install pymupdf`,
  dev-tool-only, same tier as above):
  ```python
  import fitz
  doc = fitz.open("docs/X.pdf")
  for i, page in enumerate(doc):
      page.get_pixmap(dpi=110).save(f"/tmp/preview_p{i+1}.png")
  ```
- **ODT, first page only**, via LibreOffice itself:
  `soffice --headless --convert-to png --outdir /tmp/preview docs/X.odt`
  (Draw's PNG export filter only renders page 1; good enough for a
  first-page sanity check, not a full-document review).

Then read the resulting PNG(s) — actually look, don't just check the
generation command exited 0.

## Image support (added 2026-09-17)

Both generators now understand a markdown image line:

```
![alt text](relative/path.png)
```

Path is relative to the source `.md`'s own folder. The PDF generator
scales it to the full content width via fpdf2's `image()`, preserving
aspect ratio, and starts a fresh page first if it wouldn't fit on the
current one. The ODT generator inlines it as a base64 `data:` URI in
the generated HTML (see "Landmines" for why not a plain `file://` path).

## Landmines fixed 2026-09-17, don't rediscover

- **The LibreOffice profile URI was malformed.**
  `generate_tutorial_handouts_odt.py` built it as
  `"file://" + os.path.join(tmp, "loprofile")` — string-gluing a scheme
  onto a raw Windows backslash path, missing the third slash a real
  Windows `file://` URI needs (a correct one is
  `file:///C:/Users/.../loprofile`). This apparently worked for
  years on plain-text conversions, but the moment an `<img>` tag
  *also* needed real `file://` URI resolution in the same LibreOffice
  process, the whole `soffice` subprocess hung indefinitely (confirmed
  by isolating it: the identical conversion with a syntactically
  correct profile URI, built via `pathlib.Path(...).as_uri()`, ran in
  a few seconds). Fixed the profile URI's construction the same way for
  everyone, not just image-carrying documents, since the malformed form
  is never something to rely on continuing to work.
- **A `file://`-sourced `<img>` becomes a broken LINK, not an embedded
  picture.** Verified empirically: even with the profile-URI bug fixed,
  LibreOffice's HTML import filter turned `<img src="file:///abs/path">`
  into a `draw:frame` with a relative `xlink:href` computed from the
  *conversion's own throwaway temp directory* — something like
  `../../../../../pygm/docs/x.png` — which is already wrong the moment
  the `.odt` is moved to its real location (`docs/`, one level up), let
  alone opened on a different machine. The ODT looked fine in an
  automated "did it produce a file" check and was silently broken the
  first time a human actually opened it. Fixed by inlining the image as
  a `data:` URI instead (`_data_uri()` in
  `generate_tutorial_handouts_odt.py`) — LibreOffice's HTML import
  correctly embeds a data URI's bytes into the document's own picture
  store, confirmed by checking the resulting `.odt`'s `Pictures/` entry
  directly (`unzip -l`), not just that the conversion succeeded.
- **`odf.text.H` / `odf.table.Table` / etc. are element *factory
  functions*, not classes** — `isinstance(node, Table)` always raises
  `TypeError`, even though the same-named import looks exactly like a
  class you'd expect to work that way. `extract_odt_text.py` dispatches
  on each parsed node's real `.qname[1]` (the tag's local name string)
  instead.
- **odfpy's parsed elements have no `.itertext()`** (that's an
  `xml.etree.ElementTree` method; odfpy's own DOM-like `Element` class
  doesn't implement it) — use `odf.teletype.extractText(node)`.
- **`doc.Pictures` values are a 3-tuple** `(flag, data_bytes, mimetype)`,
  not the `(mimetype, data)` pair that would be the more obvious guess.

## What went wrong once (2026-09-17), so it's on record

The very first time through this procedure, the regeneration step
(current step 11) overwrote `docs/TUTORIAL_01_STUDENT_HANDOUT_FR.odt`
— the user's actual hand-edited file — with the freshly auto-generated
version, with **no backup taken first** (current step 5 did not exist
yet; it was added *because of* this). The edited `.odt` had never been
committed either, so it was gone the moment the overwrite happened,
recoverable only from what had already been extracted into
`/tmp` for the diff minutes earlier — itself session-scoped and not
durable. Every substantive change from that edit was still captured
correctly in the `.md` files (the diff had already been done carefully
before the overwrite), so no *content* was actually lost — but the
user's own file, as an artifact, was. Steps 2 and 5 above exist
specifically so this can't happen again: back up before generating,
and back up again before regenerating over a human's live edit.
