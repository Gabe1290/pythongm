"""Real execution proof for engine.js's PythonBridge._initEmbedded (the
offline Pyodide bundle's browser-side loading logic) -- this repo has no
Node.js/browser in CI, so every other engine.js test is structural (regex/
substring assertions against the source). That's not strong enough proof
for THIS code: it does real base64/gzip decoding, dynamic <script>
injection, and a temporary window.fetch override that MUST restore
itself -- exactly the kind of logic where "the source looks right" and
"it actually works" can diverge.

Skipped cleanly (not failed) when `node` isn't on PATH, so it adds real
verification wherever Node happens to be available without becoming a
hard CI dependency this repo has deliberately avoided everywhere else.

The harness feeds PythonBridge._initEmbedded a small FAKE "pyodide" bundle
(not the real ~13 MB payload) through mocked browser globals
(document/window/fetch/atob/TextDecoder/Response are either Node builtins
or minimal stand-ins), using the REAL vendored pako.min.js to decompress —
so the gzip round-trip is genuinely exercised, not assumed.
"""
import gzip
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
ENGINE_JS = REPO_ROOT / "export" / "HTML5" / "templates" / "engine.js"
PAKO_JS = REPO_ROOT / "resources" / "vendor" / "pako.min.js"

pytestmark = pytest.mark.skipif(
    shutil.which("node") is None, reason="Node.js not available")


def _extract_pythonbridge_snippet() -> str:
    """The self-contained slice of engine.js this test needs: PYODIDE_URL/
    EMBEDDED_PYODIDE through the end of the PythonBridge class. Extracted
    by marker, not a hardcoded line range, so it tracks future edits."""
    lines = ENGINE_JS.read_text(encoding="utf-8").split("\n")
    start = next(i for i, l in enumerate(lines) if l.startswith("const PYODIDE_URL"))
    end = None
    in_class = False
    for i in range(start, len(lines)):
        if lines[i].startswith("class PythonBridge"):
            in_class = True
        if in_class and lines[i] == "}":
            end = i
            break
    assert end is not None, "Could not find the end of engine.js's PythonBridge class"
    return "\n".join(lines[start:end + 1])


_HARNESS_TEMPLATE = r"""
const fs = require('fs');
const zlib = require('zlib');

const pakoSrc = fs.readFileSync(process.argv[2], 'utf8');
const pakoModule = { exports: {} };
new Function('module', 'exports', pakoSrc)(pakoModule, pakoModule.exports);
global.pako = pakoModule.exports;

const snippet = fs.readFileSync(process.argv[3], 'utf8');
const fixture = JSON.parse(fs.readFileSync(process.argv[4], 'utf8'));

const createdScripts = [];
global.document = {
    head: {
        appendChild: (el) => {
            createdScripts.push(el);
            if (el.textContent) new Function(el.textContent)();
        },
    },
    createElement: (tag) => ({ tag, textContent: '' }),
};

let loadPyodideCalledWith = null;
global.loadPyodide = async (opts) => {
    loadPyodideCalledWith = opts;
    const resp = await global.fetch(opts.indexURL + 'pyodide.asm.wasm');
    const buf = new Uint8Array(await resp.arrayBuffer());
    globalThis._wasmBytesReceivedLength = buf.length;
    return { runPython: () => {}, globals: { get: (name) => `stub-${name}` } };
};
global.window = global;

const nativeFetchBefore = global.fetch;

const wrapped = snippet.replace(
    "const EMBEDDED_PYODIDE = null; // __PYGM_EMBEDDED_PYODIDE_MARKER__",
    "const EMBEDDED_PYODIDE = " + JSON.stringify(fixture) + ";"
) + "\nglobal.PythonBridge = PythonBridge;";
eval(wrapped);

(async () => {
    const bridge = new PythonBridge();
    await bridge._initEmbedded();
    console.log(JSON.stringify({
        loaderRan: globalThis._fakeLoaderRan === true,
        asmRan: globalThis._fakeAsmRan === true,
        wasmBytesReceivedLength: globalThis._wasmBytesReceivedLength,
        fetchRestored: global.fetch === nativeFetchBefore,
        lockFileURL: loadPyodideCalledWith.lockFileURL,
        stdLibURL: loadPyodideCalledWith.stdLibURL,
        indexURL: loadPyodideCalledWith.indexURL,
    }));
})().catch(e => { console.error('HARNESS_FAILED: ' + e.stack); process.exit(1); });
"""

# Separate harness for the branch-selection check: EMBEDDED_PYODIDE stays
# null here (no fixture substitution) -- init() must call _initFromCDN and
# NOT _initEmbedded. Spies replace both methods rather than actually
# running either (the real CDN path awaits a <script> onload that never
# fires against these mocks; the real embedded path would need the fixture
# this harness deliberately omits).
_BRANCH_HARNESS_TEMPLATE = r"""
const fs = require('fs');
global.document = { head: { appendChild: () => {} }, createElement: () => ({}) };
global.window = global;

const snippet = fs.readFileSync(process.argv[2], 'utf8');
eval(snippet + "\nglobal.PythonBridge = PythonBridge;");

(async () => {
    let cdnCalled = false, embeddedCalled = false;
    const bridge = new PythonBridge();
    bridge._initFromCDN = async () => { cdnCalled = true; bridge.pyodide = { runPython(){}, globals:{get:()=>null} }; };
    bridge._initEmbedded = async () => { embeddedCalled = true; bridge.pyodide = { runPython(){}, globals:{get:()=>null} }; };
    await bridge.init(() => {});
    console.log(JSON.stringify({ cdnCalled, embeddedCalled }));
})().catch(e => { console.error('HARNESS_FAILED: ' + e.stack); process.exit(1); });
"""


def _b64(data: bytes) -> str:
    import base64
    return base64.b64encode(data).decode("ascii")


def _gzip_b64(text: str) -> str:
    return _b64(gzip.compress(text.encode("utf-8"), compresslevel=9))


@pytest.fixture(scope="module")
def js_result(tmp_path_factory):
    """Runs the real Node harness once; every test below asserts on
    slices of its single JSON result (fast — one subprocess for the
    whole file, not one per assertion)."""
    tmp_path = tmp_path_factory.mktemp("pyodide_js_exec")
    snippet_path = tmp_path / "snippet.js"
    snippet_path.write_text(_extract_pythonbridge_snippet(), encoding="utf-8")

    fake_wasm = bytes([0x00, 0x61, 0x73, 0x6d, 1, 2, 3, 4, 5, 6, 7, 8])
    fixture = {
        "pyodide.js": _gzip_b64("globalThis._fakeLoaderRan = true;"),
        "pyodide.asm.js": _gzip_b64(
            "globalThis._createPyodideModule = function(){return{};};"
            "globalThis._fakeAsmRan = true;"),
        "pyodide.asm.wasm": _b64(fake_wasm),
        "pyodide-lock.json": _b64(json.dumps({"info": {}, "packages": {}}).encode()),
        "python_stdlib.zip": _b64(b"PK\x03\x04fake-zip-content"),
    }
    fixture_path = tmp_path / "fixture.json"
    fixture_path.write_text(json.dumps(fixture), encoding="utf-8")

    harness_path = tmp_path / "harness.js"
    harness_path.write_text(_HARNESS_TEMPLATE, encoding="utf-8")

    proc = subprocess.run(
        ["node", str(harness_path), str(PAKO_JS), str(snippet_path), str(fixture_path)],
        capture_output=True, text=True, timeout=30,
    )
    assert proc.returncode == 0, f"Node harness failed:\n{proc.stdout}\n{proc.stderr}"
    result = json.loads(proc.stdout)
    result["_fixture"] = fixture
    result["_fake_wasm_len"] = len(fake_wasm)
    return result


def test_embedded_pyodide_js_executes_via_inline_script(js_result):
    assert js_result["loaderRan"] is True


def test_embedded_pyodide_asm_js_executes_via_inline_script(js_result):
    assert js_result["asmRan"] is True


def test_wasm_fetch_intercept_serves_the_exact_embedded_bytes(js_result):
    assert js_result["wasmBytesReceivedLength"] == js_result["_fake_wasm_len"]


def test_fetch_is_restored_to_the_original_after_init(js_result):
    assert js_result["fetchRestored"] is True


def test_lockfile_and_stdlib_passed_as_correct_data_uris(js_result):
    fixture = js_result["_fixture"]
    assert js_result["lockFileURL"] == "data:application/json;base64," + fixture["pyodide-lock.json"]
    assert js_result["stdLibURL"] == "data:application/zip;base64," + fixture["python_stdlib.zip"]


def test_indexurl_is_set_to_something_non_empty(js_result):
    # Only used to compute the wasm fetch URL (intercepted regardless of
    # its exact value) — just needs to be a real, non-empty string.
    assert js_result["indexURL"]


def test_default_null_embedded_pyodide_takes_the_cdn_branch(tmp_path):
    snippet_path = tmp_path / "snippet.js"
    snippet_path.write_text(_extract_pythonbridge_snippet(), encoding="utf-8")
    harness_path = tmp_path / "branch_harness.js"
    harness_path.write_text(_BRANCH_HARNESS_TEMPLATE, encoding="utf-8")

    proc = subprocess.run(
        ["node", str(harness_path), str(snippet_path)],
        capture_output=True, text=True, timeout=15,
    )
    assert proc.returncode == 0, f"Node harness failed:\n{proc.stdout}\n{proc.stderr}"
    # init()'s own console.log('✅ Python runtime ready') lands on stdout
    # before our JSON line (the spies replace _initFromCDN/_initEmbedded,
    # not init() itself) — take the last line, not the whole output.
    result = json.loads(proc.stdout.strip().splitlines()[-1])
    assert result == {"cdnCalled": True, "embeddedCalled": False}
