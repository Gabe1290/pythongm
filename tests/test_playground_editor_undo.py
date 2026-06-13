"""Regression tests for Playground Editor robot ports and undo/redo.

Audit M21 (docs/FULL_AUDIT_2026-06-11.md): the live ROBOT-tool path builds a
PlaygroundRobot with port=_next_port then calls add_robot(robot.to_dict()),
which took the robot_data branch where _next_port never incremented — so every
robot placed in a session got port 33333.

Audit M22: AddElementCommand.already_added was set True at push time and never
reset, so after Undo of an Add Wall/Add Robot, Redo was a permanent no-op and
the element was lost.
"""

import pytest

from editors.playground_editor.playground_canvas import PlaygroundCanvas
from editors.playground_editor.playground_elements import PlaygroundRobot


@pytest.fixture
def canvas(qapp):
    c = PlaygroundCanvas()
    yield c
    c.deleteLater()


def _place_robot_via_tool(canvas):
    """Mirror the mousePressEvent ROBOT branch without a real event."""
    robot = PlaygroundRobot(x=0, y=0, port=canvas._next_port,
                            name=f"Thymio{len(canvas.robots)}")
    return canvas.add_robot(robot.to_dict())


class TestRobotPortIncrement:
    def test_placed_robots_get_distinct_ports(self, canvas):
        _place_robot_via_tool(canvas)
        _place_robot_via_tool(canvas)
        _place_robot_via_tool(canvas)
        ports = [r.port for r in canvas.robots]
        assert ports == [33333, 33334, 33335], ports
        assert len(set(ports)) == 3

    def test_next_port_advances_past_loaded_robots(self, canvas):
        # A loaded robot with a high port must not let _next_port regress.
        canvas.add_robot({'x': 0, 'y': 0, 'port': 40000, 'name': 'A'})
        new = _place_robot_via_tool(canvas)
        assert new.port == 40001


class TestAddElementRedo:
    def test_redo_after_undo_restores_robot(self, canvas):
        robot = canvas.add_robot()
        assert robot in canvas.robots
        canvas.undo_stack.undo()
        assert robot not in canvas.robots
        canvas.undo_stack.redo()
        assert robot in canvas.robots, "Redo must re-add the element"

    def test_redo_after_undo_restores_wall(self, canvas):
        wall = canvas.add_wall()
        assert wall in canvas.walls
        canvas.undo_stack.undo()
        assert wall not in canvas.walls
        canvas.undo_stack.redo()
        assert wall in canvas.walls

    def test_initial_push_does_not_double_add(self, canvas):
        canvas.add_robot()
        assert len(canvas.robots) == 1
