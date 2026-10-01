#!/usr/bin/env python3
"""The Standard object-editor panel's post-load events-data transform for
Thymio (docs/THYMIO_EXTENSION_PLAN.md, Stage G5b.4).

Moved verbatim out of ``editors/object_editor/events/_panel.py``'s
``_parse_execute_code_actions``, ``self`` -> ``panel``. Registered as a
``PLUGIN_EVENTS_DATA_TRANSFORMS`` entry (``core/ide_extension_points``), run
by ``ObjectEventsPanel.load_events_data`` right after a project loads, so an
object edited on a build without the Thymio tab still gets its
``execute_code`` actions parsed back into real ``thymio_*`` actions.

``PythonToActionsParser``/``ActionsToPythonGenerator`` (``editors/
object_editor/python_code_parser.py``) are the already-generic parsing
engine this calls into -- untouched by this move. Whether THAT engine's own
Thymio-specific method table (``THYMIO_METHOD_TO_ACTION`` etc.) should also
move behind a seam is a separate, larger, deliberately deferred design
question (see the plan doc's G5b.4 notes); this module is only the one
caller that decides WHEN to invoke it.
"""
from core.logger import get_logger

logger = get_logger(__name__)


def parse_execute_code_actions(panel) -> None:
    """Parse execute_code actions to extract proper action types (especially Thymio)"""
    from editors.object_editor.python_code_parser import PythonToActionsParser, ActionsToPythonGenerator

    parser = PythonToActionsParser()
    generator = ActionsToPythonGenerator()

    for event_name, event_info in panel.current_events_data.items():
        if not isinstance(event_info, dict):
            continue

        actions = event_info.get('actions', [])
        if not actions:
            continue

        # Build new actions list, parsing execute_code actions
        new_actions = []
        for action in actions:
            action_name = action.get('action') or action.get('type', '')
            if action_name == 'execute_code':
                code = action.get('parameters', {}).get('code', '')
                if code and 'thymio.' in code:
                    # This execute_code contains Thymio code - parse it
                    try:
                        result = parser.parse_event_code(code, event_name)
                        parsed_actions = result.get('actions', [])
                        if parsed_actions:
                            # Check if we got meaningful actions (not just execute_code)
                            has_thymio_actions = any(
                                (a.get('action', '') or a.get('type', '')).startswith('thymio_')
                                for a in parsed_actions
                            )
                            if has_thymio_actions:
                                # Only accept the rewrite if it's LOSSLESS -- the
                                # parse is idempotent under regeneration (L14,
                                # docs/FULL_AUDIT_2026-09-07.md). This is what
                                # guards against the real failure mode: a
                                # `'thymio' in code` substring match against the
                                # RAW text (comments included) gates a heuristic
                                # that reclassifies plain assignments as
                                # thymio_set_variable, so code that merely
                                # MENTIONS "thymio." in a comment could get an
                                # unrelated statement silently reinterpreted.
                                # Regenerating code from parsed_actions and
                                # re-parsing it fresh re-derives whether "thymio"
                                # genuinely appears in the REAL (comment-free)
                                # code; if that disagrees with the first parse,
                                # the rewrite isn't safe to persist.
                                regenerated = generator.generate_event_code(
                                    event_name, {"actions": parsed_actions})
                                reparsed_actions = parser.parse_event_code(
                                    regenerated, event_name).get('actions', [])
                                if reparsed_actions == parsed_actions:
                                    logger.debug(f"Parsed execute_code in {event_name}: {len(parsed_actions)} actions")
                                    new_actions.extend(parsed_actions)
                                    continue
                                logger.debug(
                                    f"Skipping lossy thymio rewrite in {event_name}: "
                                    "parse did not round-trip, keeping original execute_code")
                    except Exception as e:
                        logger.warning(f"Failed to parse execute_code in {event_name}: {e}")
                # Keep original execute_code if not Thymio code or parsing failed
                new_actions.append(action)
            else:
                # Keep non-execute_code actions as-is
                new_actions.append(action)

        # Update the event's actions
        event_info['actions'] = new_actions
