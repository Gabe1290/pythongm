"""GameMaker math functions available in expressions.

Shared by the action executor's expression evaluator and the condition
evaluator (runtime/action_flow.py). Lives in its own module because
action_executor imports action_flow, so action_flow cannot import back.
Mirrored by the HTML5 export (engine.js gmSafeMath) and the Kivy export
(GameObject.sqrt/ln/log10/exp) -- see docs/BLOCKLY_BLOCK_AUDIT_2026-10-08.md
B6b.
"""

import math


# GameMaker math functions for expressions (Blockly audit B6b). A domain
# error (sqrt of a negative, ln/log10 of <= 0, exp overflow) gives 0 for that
# call, matching the HTML5 and Kivy exports, rather than failing the whole
# expression.
def _gm_math(fn):
    def safe(x):
        try:
            result = fn(float(x))
        except (ValueError, OverflowError, TypeError):
            return 0
        return result if math.isfinite(result) else 0
    return safe


GM_MATH_FUNCTIONS = {
    'sqrt': _gm_math(math.sqrt),
    'ln': _gm_math(math.log),
    'log10': _gm_math(math.log10),
    'exp': _gm_math(math.exp),
}

