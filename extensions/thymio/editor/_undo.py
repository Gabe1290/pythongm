#!/usr/bin/env python3
"""Undo stack and obstacle/line clearing for :class:`ThymioPlaygroundWindow`.

Extracted verbatim from ``extensions/thymio/playground_window.py``
(``docs/PROJECT_STATUS.md``'s Thymio-extraction follow-up). A mixin --
``self`` / ``self.tr()`` / siblings resolve on the concrete window via MRO.
"""


class UndoMixin:
    """The undo stack and the actions that push to or consume it: adding/
    deleting an obstacle or line segment, and clearing obstacles/lines."""

    def _push_undo(self, action_type: str, data):
        """Push an action to the undo stack"""
        self.undo_stack.append((action_type, data))
        if len(self.undo_stack) > self.max_undo:
            self.undo_stack.pop(0)

    def undo(self):
        """Undo the last action"""
        if not self.undo_stack:
            self.statusbar.showMessage(self.tr("Nothing to undo"))
            return

        action_type, data = self.undo_stack.pop()

        if action_type == 'add_obstacle':
            if data in self.obstacles:
                self.obstacles.remove(data)
                self.statusbar.showMessage(self.tr("Undid obstacle addition"))
        elif action_type == 'add_line':
            if data in self.line_rects:
                self.line_rects.remove(data)
                self.statusbar.showMessage(self.tr("Undid line addition"))
        elif action_type == 'delete_obstacle':
            self.obstacles.append(data)
            self.statusbar.showMessage(self.tr("Undid obstacle deletion"))
        elif action_type == 'delete_line':
            self.line_rects.append(data)
            self.statusbar.showMessage(self.tr("Undid line deletion"))

    def delete_selected(self):
        """Delete the currently selected element"""
        if self.selected_obstacle:
            if self.selected_obstacle in self.obstacles:
                self.obstacles.remove(self.selected_obstacle)
                self._push_undo('delete_obstacle', self.selected_obstacle)
                self.statusbar.showMessage(self.tr("Obstacle deleted"))
            self.selected_obstacle = None
        elif self.selected_line:
            if self.selected_line in self.line_rects:
                self.line_rects.remove(self.selected_line)
                self._push_undo('delete_line', self.selected_line)
                self.statusbar.showMessage(self.tr("Line segment deleted"))
            self.selected_line = None

    def clear_obstacles(self):
        """Clear all interior obstacles (keep walls)"""
        # Store interior obstacles for undo
        interior_obstacles = self.obstacles[4:]
        if interior_obstacles:
            for obs in interior_obstacles:
                self._push_undo('delete_obstacle', obs)
            # Keep only the border walls (first 4)
            self.obstacles = self.obstacles[:4]
            self.selected_obstacle = None
            self.statusbar.showMessage(self.tr("Interior obstacles cleared"))
        else:
            self.statusbar.showMessage(self.tr("No interior obstacles to clear"))

    def clear_lines(self):
        """Clear all line segments"""
        if self.line_rects:
            # Store for potential undo
            for line in self.line_rects:
                self._push_undo('delete_line', line)
            self.line_rects = []
            self.selected_line = None
            self.statusbar.showMessage(self.tr("All line segments cleared"))
        else:
            self.statusbar.showMessage(self.tr("No line segments to clear"))
