#!/usr/bin/env python3
"""Round-trip every bundled sample object's events through the REAL Blockly page.

Loads editors/object_editor/blockly/blockly_workspace.html in a headless
QWebEngineView, registers the auto-generated custom_* blocks and pushes each
sample's asset lists exactly as BlocklyWidget does, then for every
samples/*/objects/*.json: loadEventsData(events) -> generatePythonCode() and
diffs the result against the original. A difference is what a student loses
the first time they edit that object in the Blockly tab (the object editor
replaces the object's events with Blockly's output).

Purely representational changes are normalised away ("4" vs 4, "sel" vs
"self", flat alarm_0 vs nested alarm/alarm_0 is reported but harmless).

Usage:
    QT_QPA_PLATFORM=offscreen python3 tools/audit_blockly_roundtrip.py [--details]

See docs/BLOCKLY_BLOCK_AUDIT_2026-10-08.md for the findings this produced.
"""
import collections
import glob
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from editors.object_editor.blockly_roundtrip import diff_events  # noqa: E402


def run_page(objs, assets):
    from PySide6.QtCore import QUrl, QTimer
    from PySide6.QtWidgets import QApplication
    from PySide6.QtWebEngineWidgets import QWebEngineView

    app = QApplication.instance() or QApplication(sys.argv)
    from events.plugin_loader import load_all_plugins
    load_all_plugins()
    from events.action_types import ACTION_TYPES

    defs = [{
        'name': n, 'display_name': a.display_name, 'description': a.description,
        'category': a.category, 'icon': a.icon or '',
        'parameters': [{'name': p.name, 'display_name': p.display_name,
                        'param_type': p.param_type, 'default_value': p.default_value,
                        **({'choices': p.choices} if getattr(p, 'choices', None) else {})}
                       for p in (a.parameters or [])]}
        for n, a in ACTION_TYPES.items()]

    # The IDE pushes the extension-event names (BlocklyWidget.
    # _push_extension_events) so their events load into the generic
    # event_extension block; do the same.
    from config.toolbox_visibility import extension_event_names
    ext_events = extension_event_names()

    js = """(function(objs, assets, extEvents){ var out = {};
      window.blocklyApi.setExtensionEvents(extEvents, []);
      for (var k in objs) {
        try { window.blocklyApi.setAssetLists(assets[k.split('/')[0]]);
              loadEventsData(objs[k]); out[k] = JSON.parse(generatePythonCode()); }
        catch (e) { out[k] = {__error__: String(e)}; }
      }
      return JSON.stringify(out); })(%s, %s, %s)""" % (json.dumps(objs), json.dumps(assets), json.dumps(ext_events))

    view = QWebEngineView()
    result = {}

    def loaded(ok):
        view.page().runJavaScript(
            "window.blocklyApi.registerCustomBlocks(JSON.parse(%s))" % json.dumps(json.dumps(defs)),
            lambda _n: view.page().runJavaScript(js, done))

    def done(r):
        result['after'] = json.loads(r)
        app.quit()

    view.loadFinished.connect(loaded)
    view.load(QUrl.fromLocalFile(str(REPO / 'editors/object_editor/blockly/blockly_workspace.html')))
    QTimer.singleShot(120000, app.quit)
    app.exec()
    if 'after' not in result:
        sys.exit("Blockly page did not finish (timeout)")
    return result['after']


def main():
    objs, assets = {}, {}
    for pj in sorted(glob.glob(str(REPO / 'samples/*/project.json'))):
        a = json.load(open(pj, encoding='utf-8')).get('assets', {})
        assets[Path(pj).parent.name] = {k: sorted((a.get(k) or {}).keys())
                                       for k in ('objects', 'sprites', 'sounds', 'rooms')}
    for f in sorted(glob.glob(str(REPO / 'samples/*/objects/*.json'))):
        ev = json.load(open(f, encoding='utf-8')).get('events') or {}
        if ev:
            objs[f"{Path(f).parent.parent.name}/{Path(f).name}"] = ev

    after = run_page(objs, assets)
    issues = []
    for obj, before in objs.items():
        aft = after.get(obj, {})
        if '__error__' in aft:
            issues.append((obj, 'load-error', aft['__error__'], ''))
            continue
        for where, kind, a, b in diff_events(before, aft):
            issues.append((f"{obj}:{where}", kind, a, b))

    groups = collections.defaultdict(set)
    for where, kind, a, b in issues:
        if kind == 'param-dropped':
            key = f"{a}.{b}"
        elif kind == 'param-changed':
            key = f"{a}.{str(b).split(':')[0]}"
        elif kind == 'event-dropped':
            key = b.split('/')[0] if '/' not in b else b
        else:
            key = f"{a} -> {b}"
        groups[(kind, key)].add(where.split('/')[0])
    print(f"objects: {len(objs)}  differences: {len(issues)}  "
          f"{dict(collections.Counter(i[1] for i in issues))}")
    for (kind, key), samples in sorted(groups.items(), key=lambda x: (x[0][0], -len(x[1]))):
        print(f"  {kind:15s} {key:45s} {', '.join(sorted(samples))}")
    if '--details' in sys.argv:
        for i in issues:
            print("   ", i)
    return 1 if issues else 0


if __name__ == '__main__':
    sys.exit(main())
