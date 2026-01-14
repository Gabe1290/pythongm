#!/usr/bin/env python3
"""
Undo/Redo commands for Room Editor
Safe implementation that prevents segfaults during deletion
"""

from PySide6.QtCore import QTimer
from PySide6.QtGui import QUndoCommand

from core.logger import get_logger
logger = get_logger(__name__)


class AddInstanceCommand(QUndoCommand):
    """Command for adding an instance to the room"""

    def __init__(self, canvas, instance, description="Add Instance", already_added=False):
        super().__init__(description)
        self.canvas = canvas
        self.instance = instance
        self.instance_data = instance.to_dict()
        self.already_added = already_added

    def undo(self):
        """Remove the instance that was added"""
        try:
            if self.instance in self.canvas.instances:
                self.canvas.instances.remove(self.instance)
            if self.instance in self.canvas.selected_instances:
                self.canvas.selected_instances.remove(self.instance)

            # Safely update canvas after a delay
            QTimer.singleShot(0, self.canvas.update)
        except (RuntimeError, AttributeError) as e:
            logger.error(f"Error in AddInstanceCommand.undo: {e}")

    def redo(self):
        """Re-add the instance"""
        try:
            if not self.already_added:
                if self.instance not in self.canvas.instances:
                    self.canvas.instances.append(self.instance)
                    self.canvas.instance_added.emit(self.instance)

            # Safely update canvas after a delay
            QTimer.singleShot(0, self.canvas.update)
        except (RuntimeError, AttributeError) as e:
            logger.error(f"Error in AddInstanceCommand.redo: {e}")


class RemoveInstanceCommand(QUndoCommand):
    """Command for removing an instance from the room"""

    def __init__(self, canvas, instance, description="Delete Instance"):
        super().__init__(description)
        self.canvas = canvas
        self.instance = instance
        self.was_selected = (instance in canvas.selected_instances)

    def undo(self):
        """Re-add the instance that was removed"""
        try:
            if self.instance not in self.canvas.instances:
                self.canvas.instances.append(self.instance)

            if self.was_selected:
                if self.instance not in self.canvas.selected_instances:
                    self.canvas.selected_instances.append(self.instance)
                # Emit signal after a delay to prevent segfault
                QTimer.singleShot(0, lambda: self._safe_emit_selected(self.instance))

            # Update canvas after a delay
            QTimer.singleShot(0, self.canvas.update)
        except (RuntimeError, AttributeError) as e:
            logger.error(f"Error in RemoveInstanceCommand.undo: {e}")

    def redo(self):
        """Remove the instance again"""
        try:
            # Remove from instances list
            if self.instance in self.canvas.instances:
                self.canvas.instances.remove(self.instance)

            # Remove from selection
            if self.instance in self.canvas.selected_instances:
                self.canvas.selected_instances.remove(self.instance)

            # Emit selection change after a delay to prevent segfault
            new_selection = self.canvas.selected_instances[0] if self.canvas.selected_instances else None
            QTimer.singleShot(0, lambda: self._safe_emit_selected(new_selection))

            # Update canvas after a delay
            QTimer.singleShot(0, self.canvas.update)
        except (RuntimeError, AttributeError) as e:
            logger.error(f"Error in RemoveInstanceCommand.redo: {e}")

    def _safe_emit_selected(self, instance):
        """Safely emit instance_selected signal"""
        try:
            if hasattr(self.canvas, 'instance_selected'):
                self.canvas.instance_selected.emit(instance)
        except (RuntimeError, AttributeError):
            pass


class MoveInstanceCommand(QUndoCommand):
    """Command for moving an instance"""

    def __init__(self, canvas, instance, old_x, old_y, new_x, new_y, description="Move Instance"):
        super().__init__(description)
        self.canvas = canvas
        self.instance = instance
        self.old_x = old_x
        self.old_y = old_y
        self.new_x = new_x
        self.new_y = new_y

    def redo(self):
        """Move to new position"""
        try:
            self.instance.x = self.new_x
            self.instance.y = self.new_y
            QTimer.singleShot(0, self.canvas.update)
        except (RuntimeError, AttributeError) as e:
            logger.error(f"Error in MoveInstanceCommand.redo: {e}")

    def undo(self):
        """Move back to old position"""
        try:
            self.instance.x = self.old_x
            self.instance.y = self.old_y
            QTimer.singleShot(0, self.canvas.update)
        except (RuntimeError, AttributeError) as e:
            logger.error(f"Error in MoveInstanceCommand.undo: {e}")


class ChangeInstancePropertyCommand(QUndoCommand):
    """Command for changing instance property"""

    def __init__(self, canvas, instance, property_name, old_value, new_value):
        super().__init__(f"Change {property_name}")
        self.canvas = canvas
        self.instance = instance
        self.property_name = property_name
        self.old_value = old_value
        self.new_value = new_value

    def redo(self):
        """Apply new value"""
        try:
            setattr(self.instance, self.property_name, self.new_value)
            QTimer.singleShot(0, self.canvas.update)
        except (RuntimeError, AttributeError) as e:
            logger.error(f"Error in ChangeInstancePropertyCommand.redo: {e}")

    def undo(self):
        """Restore old value"""
        try:
            setattr(self.instance, self.property_name, self.old_value)
            QTimer.singleShot(0, self.canvas.update)
        except (RuntimeError, AttributeError) as e:
            logger.error(f"Error in ChangeInstancePropertyCommand.undo: {e}")


class BatchAddInstancesCommand(QUndoCommand):
    """Command for adding multiple instances at once (paint mode)"""

    def __init__(self, canvas, instances, description="Paint Instances", already_added=False):
        super().__init__(description)
        self.canvas = canvas
        self.instances = instances
        self.instances_data = [inst.to_dict() for inst in instances]
        self.already_added = already_added

    def undo(self):
        """Remove all instances that were added"""
        try:
            for instance in self.instances:
                if instance in self.canvas.instances:
                    self.canvas.instances.remove(instance)
                if instance in self.canvas.selected_instances:
                    self.canvas.selected_instances.remove(instance)

            QTimer.singleShot(0, self.canvas.update)
        except (RuntimeError, AttributeError) as e:
            logger.error(f"Error in BatchAddInstancesCommand.undo: {e}")

    def redo(self):
        """Re-add all instances"""
        try:
            for instance in self.instances:
                if not self.already_added and instance not in self.canvas.instances:
                    self.canvas.instances.append(instance)
                    self.canvas.instance_added.emit(instance)

            QTimer.singleShot(0, self.canvas.update)
        except (RuntimeError, AttributeError) as e:
            logger.error(f"Error in BatchAddInstancesCommand.redo: {e}")


class BatchRemoveInstancesCommand(QUndoCommand):
    """Command for removing multiple instances at once (erase mode)"""

    def __init__(self, canvas, instances, description="Delete Instances"):
        super().__init__(description)
        self.canvas = canvas
        self.instances = list(instances)  # Make a copy
        self.were_selected = [inst for inst in instances if inst in canvas.selected_instances]

    def undo(self):
        """Re-add all instances that were removed"""
        try:
            for instance in self.instances:
                if instance not in self.canvas.instances:
                    self.canvas.instances.append(instance)

            # Restore selection
            for instance in self.were_selected:
                if instance not in self.canvas.selected_instances:
                    self.canvas.selected_instances.append(instance)

            # Emit selection change after a delay
            new_selection = self.canvas.selected_instances[0] if self.canvas.selected_instances else None
            QTimer.singleShot(0, lambda: self._safe_emit_selected(new_selection))

            QTimer.singleShot(0, self.canvas.update)
        except (RuntimeError, AttributeError) as e:
            logger.error(f"Error in BatchRemoveInstancesCommand.undo: {e}")

    def redo(self):
        """Remove all instances again"""
        try:
            logger.debug(f"BatchRemoveInstancesCommand.redo() - removing {len(self.instances)} instances")

            for instance in self.instances:
                if instance in self.canvas.instances:
                    self.canvas.instances.remove(instance)
                    logger.debug(f"  Removed {instance.object_name}")
                if instance in self.canvas.selected_instances:
                    self.canvas.selected_instances.remove(instance)

            # Emit selection change after a delay to prevent segfault
            new_selection = self.canvas.selected_instances[0] if self.canvas.selected_instances else None
            QTimer.singleShot(0, lambda: self._safe_emit_selected(new_selection))

            # Update canvas after a delay
            QTimer.singleShot(0, self.canvas.update)
        except (RuntimeError, AttributeError) as e:
            logger.error(f"Error in BatchRemoveInstancesCommand.redo: {e}")

    def _safe_emit_selected(self, instance):
        """Safely emit instance_selected signal"""
        try:
            if hasattr(self.canvas, 'instance_selected'):
                self.canvas.instance_selected.emit(instance)
        except (RuntimeError, AttributeError):
            pass


class BatchMoveInstancesCommand(QUndoCommand):
    """Command for moving multiple instances at once"""

    def __init__(self, canvas, moved_instances_data, description="Move Instances"):
        super().__init__(description)
        self.canvas = canvas
        self.moved_data = moved_instances_data

    def undo(self):
        """Move all instances back to original positions"""
        try:
            for instance, old_x, old_y, new_x, new_y in self.moved_data:
                instance.x = old_x
                instance.y = old_y
            QTimer.singleShot(0, self.canvas.update)
        except (RuntimeError, AttributeError) as e:
            logger.error(f"Error in BatchMoveInstancesCommand.undo: {e}")

    def redo(self):
        """Move all instances to new positions"""
        try:
            for instance, old_x, old_y, new_x, new_y in self.moved_data:
                instance.x = new_x
                instance.y = new_y
            QTimer.singleShot(0, self.canvas.update)
        except (RuntimeError, AttributeError) as e:
            logger.error(f"Error in BatchMoveInstancesCommand.redo: {e}")
