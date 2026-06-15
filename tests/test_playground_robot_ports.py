"""
Regression test: each robot placed with the Playground Robot tool gets a
distinct TCP port.

Audit M21 (docs/FULL_AUDIT_2026-06-11.md): add_robot() bumped self._next_port
only in its else (build-here) branch, but the only live placement path — the
Robot tool — pre-builds a PlaygroundRobot with port=_next_port and calls
add_robot(robot.to_dict()), which takes the robot_data branch where the bump
never ran. Every tool-placed robot therefore kept port 33333, so a multi-robot
playground exported colliding Aseba TCP ports.

Constructs a real (offscreen) QApplication rather than using pytest-qt, so it
runs anywhere PySide6 is installed.
"""

import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


@pytest.fixture(scope="module")
def _qapp():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


def _place_via_tool(canvas):
    """Mirror mousePressEvent's ROBOT branch: build with the current next-port,
    then hand the dict to add_robot (the data path)."""
    from editors.playground_editor.playground_elements import PlaygroundRobot
    robot = PlaygroundRobot(port=canvas._next_port, name=f"Thymio{len(canvas.robots)}")
    canvas.add_robot(robot.to_dict())


def test_tool_placed_robots_get_distinct_ports(_qapp):
    from editors.playground_editor.playground_canvas import PlaygroundCanvas
    canvas = PlaygroundCanvas()
    for _ in range(3):
        _place_via_tool(canvas)
    ports = [r.port for r in canvas.robots]
    assert ports == [33333, 33334, 33335], ports
    assert len(set(ports)) == len(ports)


def test_build_here_path_still_increments(_qapp):
    """add_robot(None) (no robot_data) must keep its original behaviour."""
    from editors.playground_editor.playground_canvas import PlaygroundCanvas
    canvas = PlaygroundCanvas()
    r1 = canvas.add_robot()
    r2 = canvas.add_robot()
    assert (r1.port, r2.port) == (33333, 33334)


def test_next_port_never_regresses_below_existing(_qapp):
    """A robot loaded with a high port must push _next_port past it so a later
    tool placement doesn't collide."""
    from editors.playground_editor.playground_canvas import PlaygroundCanvas
    from editors.playground_editor.playground_elements import PlaygroundRobot
    canvas = PlaygroundCanvas()
    canvas.add_robot(PlaygroundRobot(port=40000).to_dict())
    _place_via_tool(canvas)
    ports = [r.port for r in canvas.robots]
    assert len(set(ports)) == 2
    assert max(ports) >= 40001
