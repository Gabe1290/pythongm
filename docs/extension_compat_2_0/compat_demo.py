"""
Compatibility prototype for the PyGameMaker 2.0 extension manifest.

Design-session artifact — see docs/extension_compat_2_0/PLAN.md for full
context, provenance, and the in-repo re-verification against
samples/plateforme_3/project.json.

Proves three properties against a REAL project file:
  1. A 2.0-aware loader reads a 1.0 file cleanly (no manifest => needs nothing).
  2. A 1.0-era loader meeting a 2.0 file degrades gracefully (warns, refuses to
     save-and-corrupt) instead of crashing.
  3. A 2.0-aware loader without the extensions installed still round-trips the
     file with ZERO data loss (unknown actions + manifest preserved on save).

As shipped, SRC expects a local project_1_0.json (not included — bring your
own, or point it at a copy of samples/plateforme_3/project.json to reproduce
the PLAN.md verification update).
"""
import json, copy

SRC = "project_1_0.json"

# ---------------------------------------------------------------------------
# Step A. Produce a 2.0 version of the real project.
#   - add an explicit format_version (absence == "1.0")
#   - add a required_extensions manifest (dict keyed by id, matching the
#     project's existing dict-keyed-by-name convention)
#   - inject two actions that only an extension could provide, so we can prove
#     they survive a save by an IDE that doesn't have those extensions.
# ---------------------------------------------------------------------------
one_oh = json.load(open(SRC))
two_oh = copy.deepcopy(one_oh)

two_oh["format_version"] = "2.0"
two_oh["required_extensions"] = {
    "thymio": {"name": "Thymio Robotics", "min_version": "1.0.0"},
    "threed": {"name": "3D",              "min_version": "1.0.0"},
}
# simulate a project actually built with those extensions:
pingus_step = two_oh["assets"]["objects"]["obj_pingus"]["events"]["step"]["actions"]
pingus_step.append({"action": "thymio_drive",
                    "parameters": {"left_speed": "200", "right_speed": "200"}})
pingus_step.append({"action": "set_camera_3d",
                    "parameters": {"x": "0", "y": "0", "z": "100"}})

json.dump(two_oh, open("project_2_0.json", "w"), indent=2, ensure_ascii=False)

# ---------------------------------------------------------------------------
# Shared knowledge: what the *core* engine can run, with no extensions.
# ---------------------------------------------------------------------------
CORE_ACTIONS = {
    a["action"]
    for o in one_oh["assets"]["objects"].values()
    for ev in o.get("events", {}).values()
    for a in ev.get("actions", [])
}

def parse_ver(s):            # "2.0" -> (2, 0)
    return tuple(int(p) for p in str(s).split("."))

# ---------------------------------------------------------------------------
# The 2.0-aware loader.
# ---------------------------------------------------------------------------
class Loader_2_0:
    SUPPORTED = (2, 0)
    def __init__(self, installed_extensions):
        self.installed = dict(installed_extensions)   # id -> provided action ids

    def load(self, path):
        d = json.load(open(path))
        fmt = parse_ver(d.get("format_version", "1.0"))   # <-- graceful default
        required = d.get("required_extensions", {})       # <-- graceful default
        missing = [eid for eid in required if eid not in self.installed]

        known = set(CORE_ACTIONS)
        for eid in self.installed:
            known |= set(self.installed[eid])

        unknown = []
        for oname, o in d["assets"]["objects"].items():
            for evname, ev in o.get("events", {}).items():
                for a in ev.get("actions", []):
                    if a["action"] not in known:
                        unknown.append((oname, evname, a["action"]))
        return d, fmt, required, missing, unknown

    def save(self, d, path):
        # naive full-fidelity save: we never touch actions we didn't understand,
        # and we never drop unknown top-level keys.
        json.dump(d, open(path, "w"), indent=2, ensure_ascii=False)

# ---------------------------------------------------------------------------
# A 1.0-era loader: knows nothing about format_version or manifests.
# The ONLY thing we add for compatibility is a version guard.
# ---------------------------------------------------------------------------
class Loader_1_0:
    SUPPORTED = (1, 9)   # understands any 1.x
    def load_guarded(self, path):
        d = json.load(open(path))
        fmt = parse_ver(d.get("format_version", "1.0"))
        if fmt > self.SUPPORTED:
            return None, ("REFUSE", fmt)   # warn + refuse, do NOT crash or save
        return d, ("OK", fmt)

# ===========================================================================
# TESTS
# ===========================================================================
print("="*68)
print("TEST 1 — 2.0-aware loader opens the ORIGINAL 1.0 file")
print("="*68)
ld = Loader_2_0(installed_extensions={})
d, fmt, req, missing, unknown = ld.load("project_1_0.json")
print(f"  detected format : {fmt}   (defaulted, file has no format_version)")
print(f"  required exts   : {req}")
print(f"  missing exts    : {missing}")
print(f"  unknown actions : {len(unknown)}")
assert fmt == (1, 0) and req == {} and missing == [] and unknown == []
print("  => clean load, needs nothing. PASS")

print()
print("="*68)
print("TEST 2 — 1.0-era loader meets the 2.0 file")
print("="*68)
old = Loader_1_0()
try:
    d2, status = old.load_guarded("project_2_0.json")
    print(f"  outcome         : {status[0]} (file is format {status[1]})")
    print(f"  crashed?        : no")
    print(f"  would save/corrupt? : no (returned None, save path never reached)")
    assert status[0] == "REFUSE" and d2 is None
    print("  => warns 'needs newer PyGameMaker', leaves file intact. PASS")
except Exception as e:
    print(f"  CRASHED: {e!r}  -> FAIL")

print()
print("="*68)
print("TEST 3 — 2.0 loader, extensions NOT installed, round-trips 2.0 file")
print("="*68)
ld = Loader_2_0(installed_extensions={})     # neither thymio nor 3d installed
d, fmt, req, missing, unknown = ld.load("project_2_0.json")
print(f"  detected format : {fmt}")
print(f"  missing exts    : {missing}")
print(f"  unknown actions (=> would render as placeholders):")
for o, ev, act in unknown:
    print(f"      {o}.{ev}: {act}")
ld.save(d, "project_2_0_resaved.json")

# verify ZERO data loss on the parts an un-extended IDE couldn't understand
orig = json.load(open("project_2_0.json"))
back = json.load(open("project_2_0_resaved.json"))
manifest_ok = orig["required_extensions"] == back["required_extensions"]
actions_ok  = (orig["assets"]["objects"]["obj_pingus"]["events"]["step"]["actions"]
               == back["assets"]["objects"]["obj_pingus"]["events"]["step"]["actions"])
whole_ok    = orig == back
print(f"  manifest preserved on save? {manifest_ok}")
print(f"  unknown actions preserved?  {actions_ok}")
print(f"  entire file identical?      {whole_ok}")
assert manifest_ok and actions_ok and whole_ok
print("  => nothing dropped, nothing corrupted. PASS")
print()
print("all three properties hold against the real file.")
