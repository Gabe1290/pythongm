"""Regression for docs/DEFERRED_GAPS_2026_PLAN.md Tier 2.3.

Investigated first (per the plan's own instruction): real Thymio hardware
is NOT tone-only for "Play System Sound" -- export/Aseba/aseba_exporter.py's
_translate_play_system_sound emits the real `sound.system(id)` Aseba
primitive, so an exported/uploaded program plays the robot's own authentic
melody for that sound. The gap is narrower than the plan assumed: only the
in-app SIMULATOR preview (runtime/thymio_action_handlers.py's
execute_thymio_play_system_sound_action) approximates it as a single tone,
which could mislead a student previewing in the simulator into thinking
that beep is what the real robot sounds like. Fixed by disclosing the
simulator/hardware difference in the action's user-facing description
(shown in the action config dialog via
editors/object_editor/gm80_action_dialog.py's QLabel), not by building real
sample playback (there's nothing to build -- hardware has no sampled-audio
capability at all, only sound.freq/sound.system tone primitives, and
thymio_play_tone's existing description was already accurate for both
targets)."""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from actions.thymio_actions import THYMIO_ACTIONS


def test_play_system_sound_description_discloses_the_simulator_approximation():
    action = THYMIO_ACTIONS["thymio_play_system_sound"]
    desc = action.description.lower()
    assert "simulator" in desc
    assert "tone" in desc
    assert "melody" in desc or "real" in desc


def test_play_tone_description_stays_accurate_for_both_targets():
    """thymio_play_tone genuinely works identically on the simulator and
    real hardware (both support arbitrary-frequency tones via sound.freq),
    so its description needs no disclosure -- confirm it wasn't touched."""
    action = THYMIO_ACTIONS["thymio_play_tone"]
    assert action.description == "Play a tone at specified frequency and duration"


def test_real_hardware_export_uses_the_authentic_system_sound_primitive():
    """The honesty fix is scoped to the simulator preview, not the feature
    itself -- confirm the Aseba export (real hardware path) still calls the
    real sound.system Aseba primitive, not an approximation."""
    src = (REPO_ROOT / "export" / "Aseba" / "aseba_exporter.py").read_text(encoding="utf-8")
    assert "call sound.system(" in src
