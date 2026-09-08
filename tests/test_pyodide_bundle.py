"""export/HTML5/pyodide_bundle.py — download/cache logic for the offline
Pyodide bundle (TODO.md's "Pyodide loads from the jsDelivr CDN" item).

Never touches the real network or downloads the real ~13 MB payload —
downloader is injected with small fake bytes standing in for each file,
matching this repo's established mocked-I/O test discipline for anything
that would otherwise be slow/network-dependent in CI.
"""
from pathlib import Path

import pytest

from export.HTML5.pyodide_bundle import (
    CORE_FILES, ensure_pyodide_files, is_cached, PYODIDE_VERSION,
)


def _fake_downloader(calls):
    def download(url):
        calls.append(url)
        filename = url.rsplit("/", 1)[-1]
        return f"fake-content-for-{filename}".encode("utf-8")
    return download


def test_downloads_every_core_file_on_a_cold_cache(tmp_path):
    calls = []
    result = ensure_pyodide_files(downloader=_fake_downloader(calls), cache_dir=tmp_path,
                                   expected_sha256={})

    assert set(result.keys()) == set(CORE_FILES)
    assert len(calls) == len(CORE_FILES)
    for filename in CORE_FILES:
        assert result[filename] == f"fake-content-for-{filename}".encode("utf-8")


def test_writes_downloaded_files_to_cache_dir(tmp_path):
    ensure_pyodide_files(downloader=_fake_downloader([]), cache_dir=tmp_path, expected_sha256={})

    for filename in CORE_FILES:
        cached = tmp_path / filename
        assert cached.exists()
        assert cached.read_bytes() == f"fake-content-for-{filename}".encode("utf-8")


def test_warm_cache_never_calls_the_downloader(tmp_path):
    for filename in CORE_FILES:
        (tmp_path / filename).write_bytes(f"cached-{filename}".encode("utf-8"))

    calls = []
    result = ensure_pyodide_files(downloader=_fake_downloader(calls), cache_dir=tmp_path,
                                   expected_sha256={})

    assert calls == []
    for filename in CORE_FILES:
        assert result[filename] == f"cached-{filename}".encode("utf-8")


def test_partial_cache_only_downloads_the_missing_files(tmp_path):
    already_cached = CORE_FILES[0]
    (tmp_path / already_cached).write_bytes(b"already-here")

    calls = []
    result = ensure_pyodide_files(downloader=_fake_downloader(calls), cache_dir=tmp_path,
                                   expected_sha256={})

    downloaded_filenames = {c.rsplit("/", 1)[-1] for c in calls}
    assert already_cached not in downloaded_filenames
    assert downloaded_filenames == set(CORE_FILES) - {already_cached}
    assert result[already_cached] == b"already-here"


def test_is_cached_false_on_empty_dir(tmp_path):
    assert is_cached(cache_dir=tmp_path) is False


def test_is_cached_true_once_all_files_present(tmp_path):
    for filename in CORE_FILES:
        (tmp_path / filename).write_bytes(b"x")
    assert is_cached(cache_dir=tmp_path) is True


def test_is_cached_false_if_even_one_file_missing(tmp_path):
    for filename in CORE_FILES[:-1]:
        (tmp_path / filename).write_bytes(b"x")
    assert is_cached(cache_dir=tmp_path) is False


def test_progress_callback_invoked_for_each_file_plus_completion(tmp_path):
    calls = []
    ensure_pyodide_files(
        downloader=_fake_downloader([]),
        cache_dir=tmp_path,
        progress_callback=lambda frac, msg: calls.append((frac, msg)),
        expected_sha256={},
    )
    # One call per file (progress before each) plus a final 1.0 completion.
    assert len(calls) == len(CORE_FILES) + 1
    assert calls[-1][0] == 1.0


def test_download_failure_raises_actionable_runtime_error(tmp_path):
    def failing_downloader(url):
        raise OSError("Name or service not known")

    with pytest.raises(RuntimeError) as exc_info:
        ensure_pyodide_files(downloader=failing_downloader, cache_dir=tmp_path, expected_sha256={})

    message = str(exc_info.value)
    assert "internet access" in message.lower()
    assert "Uncheck it" in message or "uncheck" in message.lower()


def test_files_downloaded_before_a_failure_stay_cached_for_the_retry(tmp_path):
    """A failure partway through must not throw away files already
    downloaded successfully this run -- a retry only re-fetches what's
    still missing (test_partial_cache_only_downloads_the_missing_files
    above proves that half)."""
    succeed_for = CORE_FILES[0]

    def downloader(url):
        filename = url.rsplit("/", 1)[-1]
        if filename == succeed_for:
            return b"ok"
        raise OSError("boom")

    with pytest.raises(RuntimeError):
        ensure_pyodide_files(downloader=downloader, cache_dir=tmp_path, expected_sha256={})

    assert (tmp_path / succeed_for).exists()
    assert (tmp_path / succeed_for).read_bytes() == b"ok"
    for filename in CORE_FILES[1:]:
        assert not (tmp_path / filename).exists()


def test_cache_dir_defaults_under_home_pygamemaker():
    from export.HTML5.pyodide_bundle import _cache_dir
    d = _cache_dir()
    assert str(d).endswith(f".pygamemaker/pyodide_cache/{PYODIDE_VERSION}") or \
        str(d).endswith(f".pygamemaker\\pyodide_cache\\{PYODIDE_VERSION}")
    assert d.is_relative_to(Path.home())


# ---------------------------------------------------------------------------
# L11, docs/FULL_AUDIT_2026-09-07.md: SHA-256 integrity pinning. The tests
# above all pass expected_sha256={} to exercise download/cache mechanics in
# isolation from the real CDN hashes; these exercise the verification code
# path itself, against hashes computed from the tests' own fake content
# (not the real EXPECTED_SHA256 table, which real Pyodide bytes -- outside
# the scope of a fast offline test -- are needed to satisfy).
# ---------------------------------------------------------------------------

def _hashes_for(content_by_filename):
    import hashlib
    return {name: hashlib.sha256(data).hexdigest()
            for name, data in content_by_filename.items()}


def test_fresh_download_matching_the_pinned_hash_is_accepted(tmp_path):
    content = {f: f"good-{f}".encode("utf-8") for f in CORE_FILES}

    def downloader(url):
        filename = url.rsplit("/", 1)[-1]
        return content[filename]

    result = ensure_pyodide_files(downloader=downloader, cache_dir=tmp_path,
                                   expected_sha256=_hashes_for(content))

    for filename in CORE_FILES:
        assert result[filename] == content[filename]
        assert (tmp_path / filename).read_bytes() == content[filename]


def test_fresh_download_not_matching_the_pinned_hash_is_rejected(tmp_path):
    """The exact bug: a tampered/compromised CDN response used to be
    embedded verbatim with no check at all."""
    good = {f: f"good-{f}".encode("utf-8") for f in CORE_FILES}
    hashes = _hashes_for(good)  # pin the GOOD content's hashes...

    tampered_file = CORE_FILES[0]

    def downloader(url):
        filename = url.rsplit("/", 1)[-1]
        if filename == tampered_file:
            return b"<script>alert('pwned')</script>"  # ...but serve this
        return good[filename]

    with pytest.raises(RuntimeError) as exc_info:
        ensure_pyodide_files(downloader=downloader, cache_dir=tmp_path, expected_sha256=hashes)

    message = str(exc_info.value)
    assert tampered_file in message
    assert "sha-256" in message.lower() or "sha256" in message.lower()
    # Never written to cache -- a rejected file must not persist and be
    # silently trusted on the next run.
    assert not (tmp_path / tampered_file).exists()


def test_a_tampered_cache_file_is_also_rejected(tmp_path):
    """The hash check runs on cache reads too, not just fresh downloads --
    a warm cache is exactly as trustable as its own last verification, not
    automatically trusted just for existing on disk."""
    tampered_file = CORE_FILES[0]
    for f in CORE_FILES:
        (tmp_path / f).write_bytes(f"good-{f}".encode("utf-8"))
    hashes = _hashes_for({f: f"good-{f}".encode("utf-8") for f in CORE_FILES})
    # Corrupt the file on disk after pinning the hash of the ORIGINAL content.
    (tmp_path / tampered_file).write_bytes(b"corrupted")

    def downloader(url):
        raise AssertionError("a cached file must not trigger a download")

    with pytest.raises(RuntimeError) as exc_info:
        ensure_pyodide_files(downloader=downloader, cache_dir=tmp_path, expected_sha256=hashes)

    assert tampered_file in str(exc_info.value)


def test_real_expected_sha256_table_covers_every_core_file():
    """Every filename in CORE_FILES must have a real pin -- a silently
    missing entry would make the check a no-op for that one file."""
    from export.HTML5.pyodide_bundle import EXPECTED_SHA256
    assert set(EXPECTED_SHA256) == set(CORE_FILES)
    for filename, digest in EXPECTED_SHA256.items():
        assert len(digest) == 64, f"{filename}'s pin is not a 64-char hex SHA-256"
        int(digest, 16)  # must be valid hex
