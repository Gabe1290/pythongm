#!/usr/bin/env python3
"""
Undo/Redo commands for Playground Editor
"""

from PySide6.QtCore import QTimer
from PySide6.QtGui import QUndoCommand

from core.logger import get_logger
logger = get_logger(__name__)


class AddElementCommand(QUndoCommand):
    """Command for adding a wall or robot to the playground"""

    def __init__(self, canvas, element, description="Add Element", already_added=False):
        super().__init__(description)
        self.canvas = canvas
        self.element = element
        self.already_added = already_added
        self._list_name = self._get_list_name()

    def _get_list_name(self):
        from editors.playground_editor.playground_elements import PlaygroundWall
        return 'walls' if isinstance(self.element, PlaygroundWall) else 'robots'

    def _get_list(self):
        return getattr(self.canvas, self._list_name)

    def undo(self):
        try:
            elements = self._get_list()
            if self.element in elements:
                elements.remove(self.element)
            if self.element in self.canvas.selected_elements:
                self.canvas.selected_elements.remove(self.element)
            QTimer.singleShot(0, self.canvas.update)
        except (RuntimeError, AttributeError) as e:
            logger.error(f"Error in AddElementCommand.undo: {e}")

    def redo(self):
        try:
            if not self.already_added:
                elements = self._get_list()
                if self.element not in elements:
                    elements.append(self.element)
                    self.canvas.element_added.emit(self.element)
            QTimer.singleShot(0, self.canvas.update)
        except (RuntimeError, AttributeError) as e:
            logger.error(f"Error in AddElementCommand.redo: {e}")


class RemoveElementCommand(QUndoCommand):
    """Command for removing a wall or robot from the playground"""

    def __init__(self, canvas, element, description="Delete Element"):
        super().__init__(description)
        self.canvas = canvas
        self.element = element
        self.was_selected = (element in canvas.selected_elements)
        self._list_name = self._get_list_name()

    def _get_list_name(self):
        from editors.playground_editor.playground_elements import PlaygroundWall
        return 'walls' if isinstance(self.element, PlaygroundWall) else 'robots'

    def _get_list(self):
        return getattr(self.canvas, self._list_name)

    def undo(self):
        try:
            elements = self._get_list()
            if self.element not in elements:
                elements.append(self.element)
            if self.was_selected:
                if self.element not in self.canvas.selected_elements:
                    self.canvas.selected_elements.append(self.element)
                QTimer.singleShot(0, lambda: self._safe_emit(self.element))
            QTimer.singleShot(0, self.canvas.update)
        except (RuntimeError, AttributeError) as e:
            logger.error(f"Error in RemoveElementCommand.undo: {e}")

    def redo(self):
        try:
            elements = self._get_list()
            if self.element in elements:
                elements.remove(self.element)
            if self.element in self.canvas.selected_elements:
                self.canvas.selected_elements.remove(self.element)
            new_sel = self.canvas.selected_elements[0] if self.canvas.selected_elements else None
            QTimer.singleShot(0, lambda: self._safe_emit(new_sel))
            QTimer.singleShot(0, self.canvas.update)
        except (RuntimeError, AttributeError) as e:
            logger.error(f"Error in RemoveElementCommand.redo: {e}")

    def _safe_emit(self, element):
        try:
            self.canvas.element_selected.emit(element)
        except (RuntimeError, AttributeError):
            pass


class MoveElementCommand(QUndoCommand):
    """Command for moving a wall or robot"""

    def __init__(self, canvas, element, old_x, old_y, new_x, new_y,
                 description="Move Element"):
        super().__init__(description)
        self.canvas = canvas
        self.element = element
        self.old_x = old_x
        self.old_y = old_y
        self.new_x = new_x
        self.new_y = new_y

    def undo(self):
        try:
            self.element.x = self.old_x
            self.element.y = self.old_y
            QTimer.singleShot(0, self.canvas.update)
        except (RuntimeError, AttributeError) as e:
            logger.error(f"Error in MoveElementCommand.undo: {e}")

    def redo(self):
        try:
            self.element.x = self.new_x
            self.element.y = self.new_y
            QTimer.singleShot(0, self.canvas.update)
        except (RuntimeError, AttributeError) as e:
            logger.error(f"Error in MoveElementCommand.redo: {e}")


class ModifyElementCommand(QUndoCommand):
    """Command for changing a property on a wall or robot"""

    def __init__(self, canvas, element, prop_name, old_value, new_value,
                 description="Modify Element"):
        super().__init__(description)
        self.canvas = canvas
        self.element = element
        self.prop_name = prop_name
        self.old_value = old_value
        self.new_value = new_value

    def undo(self):
        try:
            setattr(self.element, self.prop_name, self.old_value)
            QTimer.singleShot(0, self.canvas.update)
        except (RuntimeError, AttributeError) as e:
            logger.error(f"Error in ModifyElementCommand.undo: {e}")

    def redo(self):
        try:
            setattr(self.element, self.prop_name, self.new_value)
            QTimer.singleShot(0, self.canvas.update)
        except (RuntimeError, AttributeError) as e:
            logger.error(f"Error in ModifyElementCommand.redo: {e}")
