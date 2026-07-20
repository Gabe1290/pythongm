#!/usr/bin/env python3
"""
Kivy Exporter for PyGameMaker IDE
Exports projects to Kivy format for mobile deployment
"""

import ast
import re
from typing import Dict

from core.logger import get_logger
logger = get_logger(__name__)


# Names the runtime's _eval_bool_expression resolves WITHOUT an instance
# prefix that we must NOT rewrite to self.<name>: the binding (self/other),
# Python constants, and the four callables the runtime exposes.
_EXPR_LEAVE_BARE = frozenset({
    'self', 'other', 'True', 'False', 'None',
    'abs', 'min', 'max', 'round',
})

# Game-global names the runtime resolves from the GameRunner / current room,
# mapped to their Kivy-export equivalents. score/lives/health go through the
# main module's getters, imported lazily via __import__('main') — the same
# circular-import-safe, call-time pattern the set_score/goto_room actions use
# (a plain `from main import` at object-module top can deadlock the import
# graph). room_width/height read the scene widget's size.
_EXPR_GLOBAL_MAP = {
    'score': "__import__('main').get_score()",
    'lives': "__import__('main').get_lives()",
    'health': "__import__('main').get_health()",
    'room_width': 'self.scene.width',
    'room_height': 'self.scene.height',
}


class _SelfNameResolver(ast.NodeTransformer):
    """Rewrite bare instance/custom variable names in an author expression to
    self.<name>, so exported conditions resolve them the way the IDE runtime's
    _eval_bool_expression does (it evaluates against a namespace seeded with
    the instance's attributes). Without this, a condition such as
    ``vspeed > 0 and y < other.y+8`` exports as a literal ``if`` whose bare
    ``vspeed`` / ``y`` raise NameError at runtime."""

    def visit_Name(self, node):
        if not isinstance(node.ctx, ast.Load) or node.id in _EXPR_LEAVE_BARE:
            return node
        if node.id in _EXPR_GLOBAL_MAP:
            new = ast.parse(_EXPR_GLOBAL_MAP[node.id], mode='eval').body
        elif node.id == 'vspeed':
            # The export stores vspeed in Kivy's (sign-flipped) Y space, so
            # compare the GameMaker-space value — same convention the
            # test_variable conditional uses (-(self.vspeed)).
            new = ast.parse('-(self.vspeed)', mode='eval').body
        else:
            new = ast.Attribute(
                value=ast.Name(id='self', ctx=ast.Load()),
                attr=node.id, ctx=ast.Load(),
            )
        return ast.copy_location(new, node)


def _resolve_instance_names(expr) -> str:
    """Bind bare instance/custom variable names in ``expr`` to self.<name>.

    Already-qualified names (self.x, other.y) are left untouched, as are the
    game-global names the export can't map. Malformed or non-string
    expressions are returned unchanged so codegen never crashes on bad input.
    """
    if not isinstance(expr, str) or not expr.strip():
        return expr
    try:
        tree = ast.parse(expr, mode='eval')
    except SyntaxError:
        return expr
    _SelfNameResolver().visit(tree)
    ast.fix_missing_locations(tree)
    try:
        return ast.unparse(tree)
    except Exception:
        return expr

# GM operation words -> Python comparison operators (mirrors the runtime's
# execute_test_variable_action / execute_test_instance_count_action).
_COMPARISON_OPS = {
    'equal': '==', 'not_equal': '!=',
    'less': '<', 'greater': '>',
    'less_equal': '<=', 'greater_equal': '>=',
}


def _literal(value):
    """Emit a parameter as a Python expression: numbers raw, the rest quoted."""
    if isinstance(value, (int, float)):
        return str(value)
    try:
        float(value)
        return str(value)
    except (TypeError, ValueError):
        return repr(value)


def _tofloat(value, default):
    """Parse a param value to float at codegen time; fall back to default."""
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return float(default)


def _num_code(value, default=0):
    """Emit a NUMERIC parameter that may be an expression ("direction+90").

    view_* variables become 0 (views unimplemented — matches the pygame
    runtime's unresolved-variable-defaults-to-0 fallback); plain numbers
    embed as literals; anything else resolves bare instance names to
    self.<name> and embeds as a parenthesized expression.
    """
    s = str(default if value is None or str(value).strip() == '' else value).strip()
    s = re.sub(r'view_[a-z]+', '0', s)
    try:
        f = float(s)
        return str(int(f)) if f.is_integer() else str(f)
    except ValueError:
        pass
    resolved = _resolve_instance_names(s)
    # Only emit the expression if it actually parses — a malformed field
    # ("10 pixels", "x >") would otherwise become uncompilable Python and
    # kill the whole exported object module. Fall back to the numeric
    # default (matching the runtime's silent no-op on a bad numeric field).
    try:
        ast.parse(resolved, mode='eval')
        return f"({resolved})"
    except SyntaxError:
        return str(default if isinstance(default, (int, float)) else 0)


class ActionCodeGenerator:
    """
    Handles proper code generation with indentation tracking for block-based actions.

    This class solves the critical problem where conditional actions like if_on_grid,
    start_block, and else_action need to properly indent subsequent actions.
    """

    def __init__(self, base_indent=2, sprite_paths=None, sound_paths=None, background_paths=None):
        """
        Initialize the code generator.

        Args:
            base_indent: Base indentation level (2 = inside a method definition)
            sprite_paths: Optional {sprite_name: 'assets/images/<file>'} map so
                the set_sprite action can resolve a sprite name to its exported
                asset path. Empty when not supplied (set_sprite then emits a
                no-op comment rather than a broken path).
            sound_paths: Optional {sound_name: 'assets/sounds/<file>'} map so the
                play_sound action can resolve a sound name to its exported path.
            background_paths: Optional {background_name: 'assets/images/<file>'}
                map so the draw_background action can resolve a background name
                to its exported path.
        """
        self.base_indent = base_indent
        self.sprite_paths = sprite_paths or {}
        self.sound_paths = sound_paths or {}
        self.background_paths = background_paths or {}
        self.indent_level = 0  # Additional indent beyond base
        self.lines = []
        self.block_stack = []  # Track open blocks for proper nesting
        # True right after a conditional's guarded unit closed: the next
        # action may be an else_action attaching to that conditional.
        self._await_else = False

    def add_line(self, code):
        """Add a line with current indentation"""
        if not code:
            return
        total_indent = self.base_indent + self.indent_level
        indent_str = "    " * total_indent

        # Handle multi-line code - indent each line properly
        if '\n' in code:
            for line in code.split('\n'):
                if line.strip():
                    self.lines.append(f"{indent_str}{line}")
        else:
            self.lines.append(f"{indent_str}{code}")

    def push_indent(self):
        """Increase indentation level (entering block)"""
        self.indent_level += 1

    def pop_indent(self):
        """Decrease indentation level (exiting block)"""
        self.indent_level = max(0, self.indent_level - 1)

    def get_code(self):
        """Get final generated code"""
        # Auto-close any remaining open blocks
        while self.block_stack:
            self._pop_block()
        return '\n'.join(self.lines)

    def _push_block(self, label):
        """Track an open suite together with the line count at open, so an
        empty suite can be padded with 'pass' when it closes."""
        self.block_stack.append((label, len(self.lines)))

    def _top_label(self):
        return self.block_stack[-1][0] if self.block_stack else None

    def _pop_block(self):
        label, opened_at = self.block_stack.pop()
        if len(self.lines) == opened_at:
            self.add_line("pass")  # empty suite — keep the code valid
        self.pop_indent()
        return label

    def _open_guard(self, condition_line):
        """Emit a conditional that guards exactly the next action or
        start_block..end_block group (GameMaker semantics — what the IDE
        runtime's skip-next dispatcher implements). The scope is closed by
        _complete_unit / end_block instead of staying open for the rest of
        the event (audit H6)."""
        self.add_line(condition_line)
        self.push_indent()
        self._push_block('guard_open')

    def _complete_unit(self):
        """A complete construct (simple action, self-contained conditional)
        was just emitted. If a conditional is waiting for its guarded unit,
        this was it — close the scope and allow a following else_action."""
        if self._top_label() == 'guard_open':
            self._pop_block()
            self._await_else = True

    def process_action(self, action: Dict, event_type: str = ''):
        """
        Process a single action and generate appropriate code.

        Handles both simple actions and complex block actions.
        Supports both 'action_type' and 'action' keys for compatibility.
        """
        # Support both 'action_type' and 'action' keys
        action_type = action.get('action_type', action.get('action', ''))
        params = action.get('parameters', {})

        # A conditional's guarded unit just closed: an else_action here
        # attaches to it; anything else means enclosing pending conditionals
        # (whose unit was that whole construct) close too (audit H6).
        if self._await_else:
            self._await_else = False
            if action_type in ('else_action', 'else_block'):
                self.add_line("else:")
                self.push_indent()
                self._push_block('guard_open')
                return
            while self._top_label() == 'guard_open':
                self._pop_block()

        # BLOCK CONTROL ACTIONS
        if action_type == 'start_block':
            if self._top_label() == 'guard_open':
                # This block is the conditional's guarded unit — same scope,
                # the conditional already pushed the indent.
                self.block_stack[-1] = ('guard_block', self.block_stack[-1][1])
            else:
                # Standalone grouping block: emit a no-op opener so the
                # deeper indentation stays syntactically valid.
                self.add_line("if True:  # action block")
                self.push_indent()
                self._push_block('block')
            return

        elif action_type == 'end_block':
            top = self._top_label()
            if top == 'guard_block':
                self._pop_block()
                self._await_else = True
            elif top in ('block', 'guard_open'):
                self._pop_block()
            else:
                self.pop_indent()
            return

        elif action_type == 'else_action' or action_type == 'else_block':
            if self._top_label() in ['if', 'if_on_grid', 'if_next_room_exists', 'if_previous_room_exists']:
                # Legacy nested shape: attach to the open if-block.
                self.pop_indent()
                self.add_line("else:")
                self.push_indent()
                self.block_stack[-1] = ('else', self.block_stack[-1][1])
            else:
                # ORPHANED else — no guard to attach to (GMK mis-imports
                # sometimes drop the question action, e.g. if_free_position
                # imported as set_score; see TODO.md maze_3 findings). The
                # IDE runtime skips the next action/block after such an
                # else; an "if False:" guard is the codegen equivalent.
                # The old pop/bare-else/push here emitted a SyntaxError
                # module (plateforme_4/5 Kivy exports never imported).
                self._open_guard("if False:  # orphaned else_action (runtime skips its unit)")
            return

        # CONDITIONAL ACTIONS (these start blocks)
        elif action_type == 'if_on_grid':
            then_actions = params.get('then_actions', [])
            if then_actions:
                self.add_line("if self.is_on_grid():")
                self.push_indent()
                # Snap to exact grid position when on grid
                self.add_line("self.snap_to_grid()")
                for nested_action in then_actions:
                    if isinstance(nested_action, dict):
                        self.process_action(nested_action, event_type)
                    elif isinstance(nested_action, str) and nested_action.strip():
                        self.add_line(nested_action)
                self.pop_indent()
                self._complete_unit()
            else:
                self._open_guard("if self.is_on_grid():")
                # Snap to exact grid position when on grid
                self.add_line("self.snap_to_grid()")
            return

        elif action_type == 'test_alignment':
            # GM "if aligned with grid" question (maze samples gate their
            # keyboard movement on it). Same guard shape as test_expression.
            try:
                hsnap = int(float(params.get('hsnap', 32) or 32))
                vsnap = int(float(params.get('vsnap', 32) or 32))
            except (TypeError, ValueError):
                hsnap, vsnap = 32, 32
            self._open_guard(
                f"if (self.x % {hsnap} == 0) and (self.y % {vsnap} == 0):")
            return

        elif action_type == 'test_expression':
            expr = _resolve_instance_names(params.get('expression', 'False'))
            self._open_guard(f"if {expr}:")
            return

        elif action_type == 'test_score':
            value = _num_code(params.get('value', 0))
            op = _COMPARISON_OPS.get(str(params.get('operation', 'equal')))
            if op is None:
                # Unknown operation (e.g. raw GM numeric codes in old
                # imports): the IDE runtime evaluates these to False.
                self._open_guard(
                    f"if False:  # test_score: unknown operation "
                    f"{params.get('operation')!r}")
            else:
                self.add_line("from main import get_game_app as _tsga")
                self._open_guard(
                    f"if (_tsga().score if _tsga() else 0) {op} {value}:")
            return

        elif action_type in ('test_health', 'test_lives'):
            # Same shape as test_score above, against the app's health/lives.
            # Missing until 2026-07-20, which made health and lives usable as
            # DISPLAY only on this target: set_health and draw_health_bar were
            # exported, but any conditional on them silently vanished, so a
            # "you died" branch never fired on Android.
            attr = 'health' if action_type == 'test_health' else 'lives'
            default = 100 if attr == 'health' else 3
            value = _num_code(params.get('value', 0))
            op = _COMPARISON_OPS.get(str(params.get('operation', 'equal')))
            if op is None:
                self._open_guard(
                    f"if False:  # {action_type}: unknown operation "
                    f"{params.get('operation')!r}")
            else:
                self.add_line("from main import get_game_app as _tsga")
                self._open_guard(
                    f"if (_tsga().{attr} if _tsga() else {default}) {op} {value}:")
            return

        elif action_type in ('if_collision', 'if_collision_at', 'check_collision'):
            obj_name = params.get('object', params.get('target', 'object'))
            # The pygame runtime treats x/y as OFFSETS from the instance
            # (check_x = instance.x + x_offset), defaulting to 0 — match that
            # here instead of passing them as absolute coordinates.
            x = _num_code(params.get('x', 0))
            y = _num_code(params.get('y', 0))
            cond = f"self.check_collision_at(self.x + ({x}), self.y + ({y}), {obj_name!r})"
            # GM stores the NOT checkbox as not_flag (older JSON: negate/not)
            if params.get('not_flag', params.get('negate', params.get('not', False))):
                cond = f"not {cond}"
            self._open_guard(f"if {cond}:")
            return

        elif action_type == 'check_empty':
            # Check if position is collision-free
            x = _num_code(params.get('x', 'self.x'))
            y = _num_code(params.get('y', 'self.y'))
            # relative parameter means offset from current position
            relative = params.get('relative', False)
            if relative:
                self._open_guard(f"if not self.check_collision_at(self.x + {x}, self.y + {y}):")
            else:
                self._open_guard(f"if not self.check_collision_at({x}, {y}):")
            return

        elif action_type == 'if_key_pressed':
            # Kivy keycodes. Arrows + common keys; letters/digits map to their
            # ASCII code (Kivy uses those). An unknown key maps to -1 so the
            # event simply never fires — the old fallback of '275' made EVERY
            # non-arrow key trigger on the RIGHT arrow.
            key = str(params.get('key', 'right')).lower()
            key_map = {'right': 275, 'left': 276, 'up': 273, 'down': 274,
                       'space': 32, 'enter': 13, 'return': 13, 'escape': 27,
                       'backspace': 8, 'tab': 9}
            if key in key_map:
                key_code = key_map[key]
            elif len(key) == 1 and (key.isalpha() or key.isdigit()):
                key_code = ord(key)
            else:
                key_code = -1
            self._open_guard(f"if self.scene.keys_pressed.get({key_code}, False):")
            return

        elif action_type == 'test_instance_count':
            # Conditional: compare the live count of an object type
            # (audit H7 — previously fell through to 'pass  # TODO', which
            # made the following block a SyntaxError and the guarded
            # actions unconditional).
            obj_name = params.get('object', '')
            target = params.get('number', params.get('count', 0))
            op = _COMPARISON_OPS.get(params.get('operation', 'equal'), '==')
            self._open_guard(
                f"if self.scene.count_instances('{obj_name}') {op} {_literal(target)}:")
            return

        elif action_type == 'test_variable':
            # Conditional: compare an instance variable (audit H7)
            var_name = params.get('variable') or params.get('variable_name') or 'temp'
            value = params.get('value', 0)
            op = _COMPARISON_OPS.get(params.get('operation', 'equal'), '==')
            if var_name == 'vspeed':
                # Kivy's Y axis is inverted relative to GameMaker, and
                # set_vspeed flips the sign on export — compare the
                # GameMaker-space value so thresholds keep their meaning.
                current = "-(self.vspeed)"
            else:
                current = f"getattr(self, '{var_name}', 0)"
            self._open_guard(f"if {current} {op} {_literal(value)}:")
            return

        elif action_type == 'if_condition':
            # Build condition from condition_type or direct expression
            condition_type = params.get('condition_type', '')
            if condition_type == 'instance_count':
                obj_name = params.get('object_name', '')
                operator = params.get('operator', '==')
                value = params.get('value', 0)
                condition = f"self.scene.count_instances('{obj_name}') {operator} {value}"
            else:
                condition = _resolve_instance_names(
                    params.get('condition', params.get('expression', 'True')))

            then_actions = params.get('then_actions', [])
            if then_actions:
                self.add_line(f"if {condition}:")
                self.push_indent()
                for nested_action in then_actions:
                    if isinstance(nested_action, dict):
                        self.process_action(nested_action, event_type)
                self.pop_indent()

                # Process else_actions if present
                else_actions = params.get('else_actions', [])
                if else_actions:
                    self.add_line("else:")
                    self.push_indent()
                    for nested_action in else_actions:
                        if isinstance(nested_action, dict):
                            self.process_action(nested_action, event_type)
                    self.pop_indent()
                self._complete_unit()
            else:
                # No nested actions: guard the next action / block (H6)
                self._open_guard(f"if {condition}:")
            return

        elif action_type == 'if_can_push':
            # Sokoban-specific: check if a box can be pushed in the current direction
            # Check if there's a collision with a box AND the space behind the box is free
            self.add_line("# Check if box can be pushed")
            self.add_line("_can_push = False")
            self.add_line("if self.hspeed != 0 or self.vspeed != 0:")
            self.push_indent()
            self.add_line("_gs = self.grid_size")
            self.add_line("_push_dx = _gs if self.hspeed > 0 else (-_gs if self.hspeed < 0 else 0)")
            self.add_line("_push_dy = _gs if self.vspeed > 0 else (-_gs if self.vspeed < 0 else 0)")
            self.add_line("# Check if space behind box is free (no wall, no other box)")
            self.add_line("if hasattr(other, 'x') and hasattr(other, 'y'):")
            self.push_indent()
            self.add_line("_behind_x = other.x + _push_dx")
            self.add_line("_behind_y = other.y + _push_dy")
            self.add_line("_can_push = not any(")
            self.push_indent()
            self.add_line("inst.check_collision(type('_TempBox', (), {'x': _behind_x, 'y': _behind_y, 'size': (_gs, _gs), 'has_sprite': True})())")
            self.add_line("for inst in self.scene.instances")
            self.add_line("if inst != self and inst != other and inst.solid")
            self.pop_indent()
            self.add_line(")")
            self.pop_indent()
            self.pop_indent()
            self.add_line("if _can_push:")
            self.push_indent()

            # Handle embedded then_action parameter
            then_action = params.get('then_action', '')
            if then_action == 'push_and_move':
                # Push the box and move the player
                self.add_line("# Push box in the direction of movement")
                self.add_line("other.x += _push_dx")
                self.add_line("other.y += _push_dy")
            elif then_action:
                # Process as a nested action
                self.process_action({'action': then_action, 'parameters': {}}, event_type)
            else:
                self.add_line("pass  # then_action placeholder")

            self.pop_indent()

            # Handle embedded else_action parameter
            else_action = params.get('else_action', '')
            if else_action:
                self.add_line("else:")
                self.push_indent()
                if else_action == 'stop_movement':
                    self.add_line("self.hspeed = 0; self.vspeed = 0; self.speed = 0")
                else:
                    self.process_action({'action': else_action, 'parameters': {}}, event_type)
                self.pop_indent()
            self._complete_unit()
            return

        elif action_type in ('if_next_room_exists', 'if_previous_room_exists'):
            direction = 'next' if action_type == 'if_next_room_exists' else 'previous'
            self.add_line(f"from main import {direction}_room_exists, _room_transition_pending")
            self.add_line("if _room_transition_pending:")
            self.push_indent()
            self.add_line("pass  # Room transition already in progress")
            self.pop_indent()

            then_actions = params.get('then_actions', [])
            if then_actions:
                self.add_line(f"elif {direction}_room_exists():")
                self.push_indent()
                for nested_action in then_actions:
                    if isinstance(nested_action, dict):
                        self.process_action(nested_action, event_type)
                self.pop_indent()

                # Process else_actions if present
                else_actions = params.get('else_actions', [])
                if else_actions:
                    self.add_line("else:")
                    self.push_indent()
                    for nested_action in else_actions:
                        if isinstance(nested_action, dict):
                            self.process_action(nested_action, event_type)
                    self.pop_indent()
                self._complete_unit()
            else:
                # No nested actions: guard the next action / block (H6)
                self._open_guard(f"elif {direction}_room_exists():")
            return

        # LOOP ACTIONS (GM repeat guards the next action / block, like a
        # conditional)
        elif action_type == 'repeat':
            count = params.get('count', 1)
            self._open_guard(f"for _i in range({count}):")
            return

        elif action_type == 'while':
            condition = _resolve_instance_names(params.get('condition', 'False'))
            self._open_guard(f"while {condition}:")
            return

        # SPECIAL CONDITIONAL ACTIONS
        elif action_type == 'stop_if_no_keys':
            # Grid-based movement: stop, snap to grid, then check keys to start new movement
            # This prevents wall-phasing and ensures proper grid alignment
            self.add_line("# Snap to exact grid position")
            self.add_line("self.snap_to_grid()")
            self.add_line("")
            self.add_line("# Always stop when on grid")
            self.add_line("self.hspeed = 0")
            self.add_line("self.vspeed = 0")
            self.add_line("")
            self.add_line("# Check if arrow keys are pressed to start moving to next grid")
            self.add_line("# Use wall collision check to prevent phasing")
            self.add_line("_gs = self.grid_size")
            self.add_line("_spd = max(1, _gs // 8)")
            self.add_line("if self.scene.keys_pressed.get(275, False):  # right")
            self.push_indent()
            self.add_line("if not self._check_wall_ahead(_gs, 0):")
            self.push_indent()
            self.add_line("self.hspeed = _spd")
            self.pop_indent()
            self.pop_indent()
            self.add_line("elif self.scene.keys_pressed.get(276, False):  # left")
            self.push_indent()
            self.add_line("if not self._check_wall_ahead(-_gs, 0):")
            self.push_indent()
            self.add_line("self.hspeed = -_spd")
            self.pop_indent()
            self.pop_indent()
            self.add_line("elif self.scene.keys_pressed.get(273, False):  # up")
            self.push_indent()
            self.add_line("if not self._check_wall_ahead(0, _gs):")
            self.push_indent()
            self.add_line("self.vspeed = _spd")
            self.pop_indent()
            self.pop_indent()
            self.add_line("elif self.scene.keys_pressed.get(274, False):  # down")
            self.push_indent()
            self.add_line("if not self._check_wall_ahead(0, -_gs):")
            self.push_indent()
            self.add_line("self.vspeed = -_spd")
            self.pop_indent()
            self.pop_indent()
            self._complete_unit()
            return

        elif action_type in ('execute_code', 'code'):
            # Inline Python authored in the IDE's code editor. Emitted verbatim
            # (NOT through _convert_simple_action, which strips each line and
            # would flatten any nested if/for indentation); add_line preserves
            # the block's own relative indentation. Like the runtime's
            # execute_code, the code is expected to use self.<attr> / other.<attr>;
            # we additionally make math/random importable so `math.`/`random.`
            # calls resolve the way they do in the IDE's exec namespace.
            user_code = params.get('code', '')
            if not isinstance(user_code, str) or not user_code.strip():
                # Empty body must still close a pending guard with valid syntax.
                self.add_line('pass')
                self._complete_unit()
                return
            # `\bmath\b` / `\brandom\b` heuristic — a spurious unused import is
            # harmless; a missing one would NameError.
            if 'math' in user_code:
                self.add_line('import math')
            if 'random' in user_code:
                self.add_line('import random')
            self.add_line(user_code)
            self._complete_unit()
            return

        elif action_type == 'move_to_contact':
            # Step pixel-by-pixel along `direction` (degrees) until colliding
            # with the target object type, or until max_distance. Mirrors the
            # runtime's execute_move_to_contact_action; Kivy Y is up so the
            # vertical step is +sin (the runtime negates it for screen coords).
            # direction / max_distance may be expressions that reference the
            # instance's own variables (e.g. the bare word "direction" meaning
            # the current heading) — the runtime resolves these against the
            # instance, so bind bare names to self.<name> the same way
            # conditions do, or they NameError in the export.
            direction = _resolve_instance_names(params.get('direction', 0))
            max_distance = _resolve_instance_names(params.get('max_distance', 1000))
            object_type = params.get('object', 'all')
            obj_arg = 'any' if object_type in ('all', '', None) else object_type
            self.add_line('import math')
            self.add_line(f'_ang = math.radians({direction})')
            self.add_line('_sx = math.cos(_ang); _sy = math.sin(_ang)')
            self.add_line(f'for _ in range(int({max_distance})):')
            self.push_indent()
            self.add_line(
                f"if self.check_collision_at(self.x + _sx, self.y + _sy, '{obj_arg}'):")
            self.push_indent()
            self.add_line('break')
            self.pop_indent()
            self.add_line('self.x += _sx; self.y += _sy')
            self.pop_indent()
            self._complete_unit()
            return

        # SIMPLE ACTIONS - generate code directly
        else:
            code = self._convert_simple_action(action_type, params, event_type)
            if code:
                # Handle multi-line code
                if '\n' in code:
                    for line in code.split('\n'):
                        if line.strip():
                            self.add_line(line.strip())
                else:
                    self.add_line(code)
                # A simple action is a complete unit: it closes a pending
                # conditional's guard scope (audit H6).
                self._complete_unit()

    def _convert_simple_action(self, action_type: str, params: Dict, event_type: str) -> str:
        """Convert a simple (non-block) action to Python code"""

        # MOVEMENT ACTIONS. Numeric params go through _num_code (empty field
        # -> default, bare instance names -> self.<name>, malformed -> default)
        # so a cleared or expression field can't emit uncompilable Python
        # the way a raw f-string embed did.
        if action_type == 'set_hspeed':
            return f"self.hspeed = {_num_code(params.get('speed', params.get('value', 0)))}"

        elif action_type == 'set_vspeed':
            # KIVY COORDINATE FIX: Flip vspeed sign
            # GameMaker: Y=0 at top, increases downward. UP = negative vspeed
            # Kivy: Y=0 at bottom, increases upward. UP = positive vspeed
            # So: kivy_vspeed = -gamemaker_vspeed. Fold the sign into a numeric
            # literal (so -3 -> 3, not "--3"); wrap an expression as -(expr).
            code = _num_code(params.get('speed', params.get('value', 0)))
            try:
                folded = -float(code)
                code = str(int(folded)) if folded.is_integer() else str(folded)
            except ValueError:
                code = f"-{code}"  # code is "(expr)" -> "-(expr)"
            return f"self.vspeed = {code}"

        elif action_type == 'set_speed':
            return f"self.speed = {_num_code(params.get('speed', params.get('value', 0)))}"

        elif action_type == 'set_direction':
            return f"self.direction = {_num_code(params.get('direction', params.get('value', 0)))}"

        elif action_type == 'set_direction_speed':
            # GM's Move Fixed-ish "direction + speed" setter (raycast_1's FPS
            # controls use direction="facing_angle"[+180]). _num_code resolves
            # the bare `facing_angle` to self.facing_angle.
            d = _num_code(params.get('direction', 0))
            s = _num_code(params.get('speed', 4))
            return f"self.direction = {d}; self.speed = {s}"

        elif action_type == 'set_facing_angle':
            angle = _num_code(params.get('angle', 0))
            rel = params.get('relative', False)
            if isinstance(rel, str):
                rel = rel.strip().lower() in ('true', '1', 'yes')
            if rel:
                return f"self.facing_angle = (self.facing_angle + {angle}) % 360"
            return f"self.facing_angle = ({angle}) % 360"

        elif action_type == 'enable_raycast_view':
            # Configure the scene's Doom-style first-person raycast camera
            # (rendered by the scene; see the raycast render methods). Mirrors
            # execute_enable_raycast_view_action's defaults.
            en = params.get('enable', True)
            if isinstance(en, str):
                en = en.strip().lower() not in ('false', '0', 'no')
            if not en:
                return "self.scene.raycast_camera = {'enabled': False}"
            def _q(v):
                return "''" if v is None else repr(str(v))
            cfg = {
                'enabled': True,
                'camera_object': str(params.get('camera_object') or ''),
                'fov': _tofloat(params.get('fov'), 66),
                'render_distance': int(_tofloat(params.get('render_distance'), 20)),
                'cell_size': int(_tofloat(params.get('cell_size'), 32)),
                'columns': int(_tofloat(params.get('columns'), 320)),
                'wall_color': str(params.get('wall_color') or '#993333'),
                'floor_color': str(params.get('floor_color') or '#464632'),
                'ceiling_color': str(params.get('ceiling_color') or '#87CEEB'),
                'wall_texture': str(params.get('wall_texture') or ''),
                'sky_texture': str(params.get('sky_texture') or ''),
                'floor_texture': str(params.get('floor_texture') or ''),
                'ceiling_texture': str(params.get('ceiling_texture') or ''),
                'wall_textured': not (str(params.get('wall_textured', 'true')).strip().lower()
                                      in ('false', '0', 'no')),
                'floor_cast_res': max(1, int(_tofloat(params.get('floor_cast_res'), 4))),
            }
            if not cfg['camera_object']:
                # No named camera object -> the acting instance IS the camera;
                # store it directly (the generated Kivy object has no
                # object_name attribute to look up by).
                return (f"self.scene.raycast_camera = {cfg!r}; "
                        f"self.scene.raycast_camera['camera_instance'] = self")
            return f"self.scene.raycast_camera = {cfg!r}"

        elif action_type in ('move_fixed', 'start_moving_direction'):
            # start_moving_direction shares move_fixed's semantics (a set of
            # named directions + a speed; one is chosen at random, 'stop'
            # halts). Numeric-angle / expression directions aren't covered
            # here — the named-direction case is what the events panel emits.
            directions = params.get('directions', ['right'])
            speed = params.get('speed', 4)
            dir_map = {
                'right': 0, 'up-right': 45, 'up': 90, 'up-left': 135,
                'left': 180, 'down-left': 225, 'down': 270, 'down-right': 315,
                'stop': -1
            }
            if 'stop' in directions:
                return "self.speed = 0"
            elif len(directions) == 1:
                deg = dir_map.get(directions[0], 0)
                return f"self.direction = {deg}; self.speed = {speed}"
            else:
                dirs = [str(dir_map.get(d, 0)) for d in directions if d != 'stop']
                return f"import random; self.direction = random.choice([{', '.join(dirs)}]); self.speed = {speed}"

        elif action_type == 'stop_movement':
            return "self.hspeed = 0; self.vspeed = 0; self.speed = 0"

        elif action_type == 'snap_to_grid':
            return "self.snap_to_grid()"

        elif action_type == 'stop_if_no_keys':
            # This is handled as a block action in process_action, not here
            return None

        elif action_type == 'move_grid':
            # Grid-based movement - move one grid cell in specified direction
            # Includes collision checking to prevent moving through walls
            # Also sets hspeed/vspeed to indicate direction for collision handlers
            direction = params.get('direction', 'right')
            grid_size = params.get('grid_size', 32)
            dir_map = {
                'right': (1, 0), 'left': (-1, 0),
                'up': (0, 1), 'down': (0, -1),  # Kivy Y is inverted
                'up-right': (1, 1), 'up-left': (-1, 1),
                'down-right': (1, -1), 'down-left': (-1, -1)
            }
            dx, dy = dir_map.get(direction, (0, 0))
            move_x = dx * grid_size
            move_y = dy * grid_size
            speed = max(1, grid_size // 8)
            # Set hspeed/vspeed to indicate direction (used by collision handlers)
            # Then check for collision before moving; only move if target cell is free
            return f"self.hspeed = {dx * speed}; self.vspeed = {dy * speed}; self._move_grid({move_x}, {move_y})"

        elif action_type == 'move_towards':
            # Move towards a specific point at given speed
            x = params.get('x', 0)
            y = params.get('y', 0)
            speed = params.get('speed', 4)
            return f"""import math
dx = {x} - self.x
dy = {y} - self.y
dist = math.sqrt(dx*dx + dy*dy)
if dist > 0:
    self.hspeed = (dx / dist) * {speed}
    self.vspeed = (dy / dist) * {speed}"""

        elif action_type == 'set_gravity':
            # Set gravity direction and strength
            direction = params.get('direction', 270)  # Default: down
            gravity = params.get('gravity', params.get('value', 0.5))
            return f"self.gravity = {gravity}; self.gravity_direction = {direction}"

        elif action_type == 'set_friction':
            # Set friction/deceleration
            friction = params.get('friction', params.get('value', 0.1))
            return f"self.friction = {friction}"

        elif action_type == 'reverse_horizontal':
            # Reverse horizontal direction
            return "self.hspeed = -self.hspeed"

        elif action_type == 'reverse_vertical':
            # Reverse vertical direction
            return "self.vspeed = -self.vspeed"

        elif action_type == 'exit_event':
            # Stop executing remaining actions in this event
            return "return"

        # INSTANCE ACTIONS
        elif action_type == 'create_instance':
            obj_name = params.get('object', '')
            x = _num_code(params.get('x', 0))
            y = _num_code(params.get('y', 0))
            relative = params.get('relative', False)
            if relative:
                return f"self.scene.create_instance({obj_name!r}, self.x + {x}, self.y + {y})"
            else:
                return f"self.scene.create_instance({obj_name!r}, {x}, {y})"

        elif action_type == 'destroy_instance':
            target = params.get('target', 'self')
            if target == 'other' and 'collision' in event_type:
                return "other.destroy()"
            else:
                return "self.destroy()"

        # ALARM ACTIONS
        elif action_type == 'set_alarm':
            try:
                alarm_num = int(params.get('alarm_number', 0) or 0)
            except (TypeError, ValueError):
                alarm_num = 0
            steps = _num_code(params.get('steps', 30), 30)
            return f"self.alarms[{alarm_num}] = {steps}"

        elif action_type == 'sleep':
            # Blocking pause (matches the desktop runtime); ms clamped to [0, 10000].
            ms = params.get('milliseconds', params.get('ms', params.get('duration', 1000)))
            try:
                ms = max(0, min(10000, int(ms)))
            except (ValueError, TypeError):
                ms = 1000
            return f"import time; time.sleep({ms / 1000.0})"

        # ROOM ACTIONS
        elif action_type == 'next_room' or action_type == 'room_goto_next':
            return "from main import goto_next_room; goto_next_room()"

        elif action_type == 'previous_room' or action_type == 'room_goto_previous':
            return "from main import goto_previous_room; goto_previous_room()"

        elif action_type == 'goto_room' or action_type == 'room_goto':
            room_name = params.get('room', params.get('room_name', ''))
            return f"from main import goto_room; goto_room('{room_name}')"

        elif action_type == 'restart_room' or action_type == 'room_restart':
            return "from main import get_game_app; app = get_game_app(); app._switch_to_room(app.current_room_index) if app else None"

        # VIEW / CAMERA ACTIONS — reconfigure the scene's views live. The
        # multi-view render needs the Fbo built at construction (baked
        # views_enabled), so these reconfigure an already-enabled camera; the
        # scene methods no-op safely otherwise. (Was previously "Unknown action
        # type".)
        elif action_type in ('enable_views', 'enable_view'):
            raw = params.get('enable', params.get('enabled', 'true'))
            if isinstance(raw, str):
                flag = raw.strip().lower() in ('true', '1', 'yes')
            else:
                flag = bool(raw)
            return f"self.scene.set_views_enabled({flag})"

        elif action_type in ('set_view', 'view_set'):
            try:
                idx = int(params.get('view', 0))
            except (ValueError, TypeError):
                idx = 0
            if idx < 0 or idx > 7:
                idx = 0
            updates = {}
            for k in ('view_x', 'view_y', 'view_w', 'view_h',
                      'port_x', 'port_y', 'port_w', 'port_h',
                      'hborder', 'vborder', 'hspeed', 'vspeed'):
                if k in params and params[k] not in (None, ''):
                    try:
                        updates[k] = int(float(params[k]))
                    except (ValueError, TypeError):
                        pass
            if 'visible' in params:
                vis = params['visible']
                if isinstance(vis, str):
                    updates['visible'] = vis.strip().lower() in ('true', '1', 'yes')
                else:
                    updates['visible'] = bool(vis)
            if 'follow' in params:
                f = params['follow']
                updates['follow'] = str(f) if f else None
            return f"self.scene.apply_set_view({idx}, {updates!r})"

        # GAME CONTROL ACTIONS
        elif action_type == 'game_end' or action_type == 'end_game':
            return "from kivy.app import App; App.get_running_app().stop()"

        # DELAY ACTION
        elif action_type == 'delay_action':
            frames = params.get('frames', 60)
            then_action = params.get('then_action', '')
            try:
                frames = int(frames)
            except (ValueError, TypeError):
                frames = 60
            delay_seconds = frames / 60.0
            # Room-changing actions need a guard to prevent firing after
            # the room has already changed (e.g., by a subsequent goto_next_room)
            is_room_action = then_action in ('next_room', 'room_goto_next', 'previous_room',
                                              'change_room', 'goto_room', 'restart_room',
                                              'game_end', 'end_game')
            # Generate the delayed action code (import + lambda-friendly call)
            if then_action == 'next_room' or then_action == 'room_goto_next':
                import_code = "from main import goto_next_room"
                call_code = "goto_next_room()"
            elif then_action == 'previous_room':
                import_code = "from main import goto_previous_room"
                call_code = "goto_previous_room()"
            elif then_action == 'game_end' or then_action == 'end_game':
                import_code = "from kivy.app import App"
                call_code = "App.get_running_app().stop()"
            elif then_action == 'restart_room':
                import_code = "from main import get_game_app"
                call_code = "get_game_app()._switch_to_room(get_game_app().current_room_index)"
            elif then_action == 'change_room' or then_action == 'goto_room':
                room_name = params.get('room_name', params.get('room', ''))
                import_code = "from main import goto_room"
                call_code = f"goto_room('{room_name}')"
            else:
                import_code = ""
                call_code = f"None  # delay_action: unknown then_action '{then_action}'"
                is_room_action = False
            if is_room_action:
                # Guard: only fire if still in the same room (prevents double transitions)
                return f"from main import get_game_app; {import_code}; from kivy.clock import Clock; _dr = get_game_app().current_room_index if get_game_app() else -1; Clock.schedule_once(lambda dt: {call_code} if get_game_app() and get_game_app().current_room_index == _dr else None, {delay_seconds})"
            elif import_code:
                return f"{import_code}; from kivy.clock import Clock; Clock.schedule_once(lambda dt: {call_code}, {delay_seconds})"
            else:
                return f"from kivy.clock import Clock; Clock.schedule_once(lambda dt: {call_code}, {delay_seconds})"

        # MESSAGE ACTIONS
        elif action_type == 'show_message' or action_type == 'display_message':
            message = params.get('message', '')
            # Embed via repr() so newlines, quotes and trailing backslashes
            # can't break the generated literal (L21); manual single-quote
            # escaping left those cases as a SyntaxError in the exported module.
            return f"from main import show_message; show_message({message!r})"

        # SCORE/LIVES/HEALTH ACTIONS (use lazy import to avoid circular imports)
        elif action_type == 'set_score':
            value = _num_code(params.get('value', 0))
            relative = bool(params.get('relative', False))
            return f"from main import set_score; set_score({value}, relative={relative})"

        elif action_type == 'set_lives':
            value = _num_code(params.get('value', 3), 3)
            relative = bool(params.get('relative', False))
            return f"from main import set_lives; set_lives({value}, relative={relative})"

        elif action_type == 'set_health':
            value = _num_code(params.get('value', 100), 100)
            relative = bool(params.get('relative', False))
            return f"from main import set_health; set_health({value}, relative={relative})"

        # DRAW ACTIONS — queue runtime-schema commands into
        # self._draw_queue; the scene renders it after on_draw runs
        # (base_object._render_draw_queue).
        elif action_type == 'draw_score':
            caption = str(params.get('caption', 'Score: '))
            x = _num_code(params.get('x', 0))
            y = _num_code(params.get('y', 0))
            return ("from main import get_game_app as _ga; "
                    f"self._draw_queue.append(dict(type='text', "
                    f"text={caption!r} + str(_ga().score if _ga() else 0), "
                    f"x={x}, y={y}, "
                    "color=getattr(self, 'draw_color', None) or (255, 255, 255)))")

        elif action_type == 'draw_text':
            text = str(params.get('text', ''))
            x = _num_code(params.get('x', 0))
            y = _num_code(params.get('y', 0))
            return (f"self._draw_queue.append(dict(type='text', text={text!r}, "
                    f"x={x}, y={y}, "
                    "color=getattr(self, 'draw_color', None) or (0, 0, 0)))")

        elif action_type == 'draw_lives':
            sprite = str(params.get('sprite', '') or '')
            path = self.sprite_paths.get(sprite, '')
            x = _num_code(params.get('x', 0))
            y = _num_code(params.get('y', 0))
            scale = _num_code(params.get('scale', 1.0), 1.0)
            return ("from main import get_game_app as _ga; "
                    f"self._draw_queue.append(dict(type='lives', "
                    f"count=int(_ga().lives if _ga() else 0), "
                    f"x={x}, y={y}, sprite_path={path!r}, scale={scale}))")

        elif action_type == 'draw_sprite':
            sprite = str(params.get('sprite', params.get('sprite_name', '')) or '')
            path = self.sprite_paths.get(sprite, '')
            if not path:
                return f"pass  # draw_sprite: sprite {sprite!r} not found in export"
            x = _num_code(params.get('x', 0))
            y = _num_code(params.get('y', 0))
            return (f"self._draw_queue.append(dict(type='sprite', "
                    f"sprite_path={path!r}, x={x}, y={y}))")

        elif action_type in ('draw_rectangle', 'draw_ellipse'):
            # Same shape for both — only the draw-queue 'type' differs,
            # mirroring runtime/action_executor.py's execute_draw_rectangle_
            # /ellipse_action (which are themselves near-identical).
            dq_type = 'rectangle' if action_type == 'draw_rectangle' else 'ellipse'
            x1 = _num_code(params.get('x1', 0))
            y1 = _num_code(params.get('y1', 0))
            x2 = _num_code(params.get('x2', 100))
            y2 = _num_code(params.get('y2', 100))
            filled = params.get('filled', True)
            filled = filled if isinstance(filled, bool) else str(filled).lower() in ('true', '1', 'yes')
            return (f"self._draw_queue.append(dict(type={dq_type!r}, "
                    f"x1={x1}, y1={y1}, x2={x2}, y2={y2}, filled={filled}, "
                    "color=getattr(self, 'draw_color', None) or (0, 0, 0)))")

        elif action_type == 'draw_circle':
            x = _num_code(params.get('x', 0))
            y = _num_code(params.get('y', 0))
            radius = _num_code(params.get('radius', 50))
            filled = params.get('filled', True)
            filled = filled if isinstance(filled, bool) else str(filled).lower() in ('true', '1', 'yes')
            return (f"self._draw_queue.append(dict(type='circle', "
                    f"x={x}, y={y}, radius={radius}, filled={filled}, "
                    "color=getattr(self, 'draw_color', None) or (0, 0, 0)))")

        elif action_type == 'draw_line':
            x1 = _num_code(params.get('x1', 0))
            y1 = _num_code(params.get('y1', 0))
            x2 = _num_code(params.get('x2', 100))
            y2 = _num_code(params.get('y2', 100))
            return (f"self._draw_queue.append(dict(type='line', "
                    f"x1={x1}, y1={y1}, x2={x2}, y2={y2}, "
                    "color=getattr(self, 'draw_color', None) or (0, 0, 0)))")

        elif action_type == 'draw_arrow':
            # tip1/tip2 are computed once at RUN time (positions may be
            # expressions), mirroring execute_draw_arrow_action's
            # atan2/cos/sin geometry exactly — the draw-queue renderer
            # (both the pygame runtime and _dq_render_cmd) just draws the
            # three pre-computed segments, it doesn't know about "arrows".
            x1 = _num_code(params.get('x1', 0))
            y1 = _num_code(params.get('y1', 0))
            x2 = _num_code(params.get('x2', 100))
            y2 = _num_code(params.get('y2', 100))
            tip_size = _num_code(params.get('tip_size', 10), 10)
            return (
                "import math as _m; "
                f"_ax1, _ay1, _ax2, _ay2, _ats = {x1}, {y1}, {x2}, {y2}, {tip_size}; "
                "_aang = _m.atan2(_ay2 - _ay1, _ax2 - _ax1); "
                "_at1x = _ax2 - _ats * _m.cos(_aang - _m.pi / 6); "
                "_at1y = _ay2 - _ats * _m.sin(_aang - _m.pi / 6); "
                "_at2x = _ax2 - _ats * _m.cos(_aang + _m.pi / 6); "
                "_at2y = _ay2 - _ats * _m.sin(_aang + _m.pi / 6); "
                "self._draw_queue.append(dict(type='arrow', x1=_ax1, y1=_ay1, "
                "x2=_ax2, y2=_ay2, tip1_x=_at1x, tip1_y=_at1y, tip2_x=_at2x, "
                "tip2_y=_at2y, color=getattr(self, 'draw_color', None) or (0, 0, 0)))"
            )

        elif action_type == 'draw_variable':
            x = _num_code(params.get('x', 0))
            y = _num_code(params.get('y', 0))
            var_name = str(params.get('variable', '') or '')
            expr = _resolve_instance_names(var_name) if var_name else "''"
            return (f"self._draw_queue.append(dict(type='text', text=str({expr}), "
                    f"x={x}, y={y}, "
                    "color=getattr(self, 'draw_color', None) or (0, 0, 0)))")

        elif action_type == 'draw_health_bar':
            x1 = _num_code(params.get('x1', 0))
            y1 = _num_code(params.get('y1', 0))
            x2 = _num_code(params.get('x2', 100))
            y2 = _num_code(params.get('y2', 20))
            back_color = str(params.get('back_color', '#FF0000'))
            bar_color = str(params.get('bar_color', '#00FF00'))
            return ("from main import get_game_app as _ga; "
                    f"self._draw_queue.append(dict(type='health_bar', "
                    f"x1={x1}, y1={y1}, x2={x2}, y2={y2}, "
                    f"health=(_ga().health if _ga() else 100), "
                    f"back_color={back_color!r}, bar_color={bar_color!r}))")

        elif action_type == 'draw_background':
            bg = str(params.get('background', params.get('background_name', '')) or '')
            path = self.background_paths.get(bg, '')
            if not path:
                return f"pass  # draw_background: background {bg!r} not found in export"
            x = _num_code(params.get('x', 0))
            y = _num_code(params.get('y', 0))
            tiled = params.get('tiled', False)
            tiled = tiled if isinstance(tiled, bool) else str(tiled).lower() in ('true', '1', 'yes')
            return (f"self._draw_queue.append(dict(type='background', "
                    f"background_path={path!r}, x={x}, y={y}, tiled={tiled}))")

        elif action_type == 'set_draw_color':
            color = str(params.get('color', '#000000'))
            try:
                hex_str = color.lstrip('#')
                rgb = (int(hex_str[0:2], 16), int(hex_str[2:4], 16),
                       int(hex_str[4:6], 16))
            except (ValueError, IndexError):
                rgb = (0, 0, 0)
            return f"self.draw_color = {rgb!r}"

        elif action_type == 'set_draw_font':
            # Stored for parity; the renderer uses one font, same as the
            # pygame runtime's _draw_text.
            return f"self.draw_font = {str(params.get('font', ''))!r}"

        # INSTANCE CREATION / DESTRUCTION CLUSTER
        elif action_type == 'create_moving_instance':
            obj_name = str(params.get('object', ''))
            if not obj_name:
                return "pass  # create_moving_instance: no object specified"
            x = _num_code(params.get('x', 0))
            y = _num_code(params.get('y', 0))
            direction = _num_code(params.get('direction', 0))
            speed = _num_code(params.get('speed', 0))
            return (f"_cmi = self.scene.create_instance({obj_name!r}, {x}, {y}); "
                    f"_cmi and setattr(_cmi, 'direction', {direction}); "
                    f"_cmi and setattr(_cmi, 'speed', {speed})")

        elif action_type == 'create_random_instance':
            choices = [str(params.get(f'object{i}'))
                       for i in range(1, 5) if params.get(f'object{i}')]
            if not choices:
                return "pass  # create_random_instance: no objects specified"
            x = _num_code(params.get('x', 0))
            y = _num_code(params.get('y', 0))
            return (f"import random as _rnd; "
                    f"self.scene.create_instance(_rnd.choice({choices!r}), {x}, {y})")

        elif action_type == 'jump_to_random':
            snap_h = _num_code(params.get('snap_h', 1), 1)
            snap_v = _num_code(params.get('snap_v', 1), 1)
            return f"self.jump_to_random({snap_h}, {snap_v})"

        elif action_type == 'destroy_at_position':
            x = _num_code(params.get('x', 0))
            y = _num_code(params.get('y', 0))
            radius = _num_code(params.get('radius', 32), 32)
            obj_filter = str(params.get('object', 'all') or 'all')
            relative = bool(params.get('relative', False))
            return (f"self.destroy_at_position({x}, {y}, {radius}, "
                    f"{obj_filter!r}, relative={relative})")

        elif action_type == 'set_direction_speed':
            direction = _num_code(params.get('direction', 0))
            speed = _num_code(params.get('speed', 4))
            return f"self.direction = {direction}; self.speed = {speed}"

        elif action_type == 'set_window_caption':
            # repr() the caption (free text) so an apostrophe/newline/backslash
            # can't break the literal — same fix as show_message. bool() the
            # flags so a non-bool stored value can't emit invalid Python.
            caption = params.get('caption', '')
            show_score = bool(params.get('show_score', True))
            show_lives = bool(params.get('show_lives', True))
            show_health = bool(params.get('show_health', False))
            return (f"from main import set_window_caption; set_window_caption("
                    f"caption={caption!r}, show_score={show_score}, "
                    f"show_lives={show_lives}, show_health={show_health})")

        elif action_type == 'jump_to_position':
            # Teleport to a specific position
            x = _num_code(params.get('x', 0))
            y = _num_code(params.get('y', 0))
            relative = params.get('relative', False)
            if relative:
                return f"self.x += {x}; self.y += {y}"
            else:
                return f"self.x = {x}; self.y = {y}"

        elif action_type == 'change_instance':
            # Change the object type (sprite) of this instance
            new_object = params.get('object', params.get('new_object', ''))
            perform_events = params.get('perform_events', True)
            if new_object:
                return f"self.change_to('{new_object}', perform_events={perform_events})"
            else:
                return "pass  # change_instance: no target object specified"

        elif action_type == 'if_object_exists':
            # Conditional: gate the nested then/else actions on object existence.
            # Returning a bare expression (the old behaviour) left the gated
            # actions running unconditionally. Mirror if_condition's block handling.
            object_name = params.get('object', '')
            # The runtime stores the negation flag as not_flag; accept the older
            # negate/not keys too so existing project JSON still exports correctly.
            negate = params.get('not_flag', params.get('negate', params.get('not', False)))
            cond = f"self.scene.object_exists('{object_name}')"
            condition = f"not {cond}" if negate else cond

            then_actions = params.get('then_actions', [])
            if then_actions:
                self.add_line(f"if {condition}:")
                self.push_indent()
                for nested_action in then_actions:
                    if isinstance(nested_action, dict):
                        self.process_action(nested_action, event_type)
                self.pop_indent()

                # Process else_actions if present
                else_actions = params.get('else_actions', [])
                if else_actions:
                    self.add_line("else:")
                    self.push_indent()
                    for nested_action in else_actions:
                        if isinstance(nested_action, dict):
                            self.process_action(nested_action, event_type)
                    self.pop_indent()
                self._complete_unit()
            else:
                # No nested actions: guard the next action / block (H6)
                self._open_guard(f"if {condition}:")
            return

        elif action_type == 'set_variable':
            # Set a variable to a value. Known-numeric attrs go through
            # _num_code (empty/expression safe); a custom var may hold a
            # number OR a string, so use _literal (number as-is, else a
            # repr'd string) — either way a cleared or quoted field can't
            # emit uncompilable Python.
            var_name = params.get('variable', params.get('name', 'temp'))
            raw = params.get('value', 0)
            relative = params.get('relative', False)
            numeric_attrs = ['x', 'y', 'hspeed', 'vspeed', 'speed', 'direction',
                             'visible', 'solid']
            if var_name in numeric_attrs:
                value = _num_code(raw)
                if relative:
                    return f"self.{var_name} += {value}"
                return f"self.{var_name} = {value}"
            value = _literal(raw)
            if relative:
                return f"self.{var_name} = getattr(self, {var_name!r}, 0) + {value}"
            return f"self.{var_name} = {value}"

        elif action_type == 'comment':
            # GM comments are real (no-op) actions: they can be the guarded
            # unit of a conditional, so emit a statement, not a bare comment.
            text = str(params.get('text', '')).replace('\n', ' ')
            return f"pass  # {text}" if text else "pass  # comment"

        elif action_type == 'set_sprite':
            # Swap the instance's sprite and/or set the current frame
            # (subimage) / animation speed. sprite='<self>' (or empty) keeps
            # the current sprite and only touches frame/speed, matching the
            # runtime's execute_set_sprite_action.
            sprite_name = params.get('sprite', '<self>')
            parts = []
            if sprite_name and sprite_name != '<self>':
                path = self.sprite_paths.get(sprite_name)
                if path:
                    parts.append(f"self.set_sprite('{path}')")
                else:
                    parts.append(f"pass  # set_sprite: '{sprite_name}' not found in export")
            # subimage / speed default to -1 ("don't change"); only emit when
            # the author set a real value. Non-numeric (expression) values are
            # skipped rather than emitted verbatim.
            try:
                subimage = int(params.get('subimage', -1))
                if subimage >= 0:
                    parts.append(f"self.image_index = {subimage}")
            except (ValueError, TypeError):
                pass
            try:
                anim_speed = float(params.get('speed', -1))
                if anim_speed >= 0:
                    parts.append(f"self.image_speed = {anim_speed}")
            except (ValueError, TypeError):
                pass
            return "; ".join(parts) if parts else "pass  # set_sprite: no change"

        elif action_type == 'restart_game':
            # Restart from the first room. Reuses the app's room-switch path
            # (index 0) rather than adding new infra — mirrors the runtime's
            # "recreate the room with fresh instances" restart.
            return ("from main import get_game_app; _app = get_game_app(); "
                    "(_app._switch_to_room(0) if _app else None)")

        elif action_type == 'play_sound':
            # Resolve the sound name to its exported path and call the
            # SoundLoader-backed play_sound() helper in the generated main.py.
            sound = params.get('sound', params.get('sound_name', ''))
            volume = params.get('volume', 1.0)
            try:
                volume = float(volume)
            except (ValueError, TypeError):
                volume = 1.0
            path = self.sound_paths.get(sound)
            if path:
                return (f"from main import play_sound; "
                        f"play_sound('{path}', {volume})")
            return f"pass  # play_sound: sound '{sound}' not found in export"

        elif action_type == 'show_highscore':
            # Show the high-score table (highscore.py module), prompting for a
            # name when the current score qualifies unless disabled.
            allow = params.get('allow_new_entry', True)
            return ("from highscore import show_highscore; "
                    f"show_highscore(allow_new_entry={bool(allow)})")

        elif action_type == 'clear_highscore':
            return "from highscore import clear_highscore; clear_highscore()"

        # DEFAULT
        else:
            logger.warning(f"Unknown action type '{action_type}'")
            return f"pass  # TODO: {action_type}"


