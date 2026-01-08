#!/usr/bin/env python3
"""
Sync Coordinator for PyGameMaker Object Editor
Prevents infinite sync loops between Code Editor, Blockly, and Events Panel.
"""

from typing import Optional
from enum import Enum


class SyncSource(Enum):
    """Identifies the source of a sync operation"""
    CODE = "code"
    BLOCKLY = "blockly"
    EVENTS = "events"
    EXTERNAL = "external"  # Loading from file, etc.


class SyncCoordinator:
    """
    Coordinates synchronization between Code, Blockly, and Events views.

    Usage:
        coordinator = SyncCoordinator()

        # When starting a sync from code editor:
        if coordinator.begin_sync(SyncSource.CODE):
            try:
                # Perform sync operations...
                events_panel.load_events_data(events)
                blockly.load_events_data(events)
            finally:
                coordinator.end_sync()

        # In event handlers, check if we should skip:
        def on_events_modified(self):
            if self.coordinator.is_syncing():
                return  # Skip - this change is from another sync
    """

    def __init__(self):
        self._sync_source: Optional[SyncSource] = None
        self._sync_lock: bool = False
        self._sync_depth: int = 0

    def begin_sync(self, source: SyncSource) -> bool:
        """
        Start a sync operation.

        Args:
            source: Which view initiated this sync

        Returns:
            True if sync can proceed, False if already syncing
        """
        if self._sync_lock:
            return False

        self._sync_lock = True
        self._sync_source = source
        self._sync_depth += 1
        return True

    def end_sync(self):
        """Complete the current sync operation"""
        self._sync_depth -= 1
        if self._sync_depth <= 0:
            self._sync_lock = False
            self._sync_source = None
            self._sync_depth = 0

    def is_syncing(self) -> bool:
        """Check if currently in a sync operation"""
        return self._sync_lock

    def is_syncing_from(self, source: SyncSource) -> bool:
        """Check if currently syncing from a specific source"""
        return self._sync_lock and self._sync_source == source

    def get_sync_source(self) -> Optional[SyncSource]:
        """Get the current sync source, or None if not syncing"""
        return self._sync_source if self._sync_lock else None

    def should_skip_for(self, target: SyncSource) -> bool:
        """
        Check if an update to target should be skipped.

        Returns True if we're currently syncing FROM a different source,
        meaning target doesn't need to process this update.
        """
        if not self._sync_lock:
            return False
        # Skip if the sync source is different from the target
        # (the target is receiving, not initiating)
        return self._sync_source != target


class SyncContext:
    """
    Context manager for sync operations.

    Usage:
        with SyncContext(coordinator, SyncSource.CODE) as can_sync:
            if can_sync:
                # Perform sync operations
                pass
    """

    def __init__(self, coordinator: SyncCoordinator, source: SyncSource):
        self.coordinator = coordinator
        self.source = source
        self.can_sync = False

    def __enter__(self) -> bool:
        self.can_sync = self.coordinator.begin_sync(self.source)
        return self.can_sync

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.can_sync:
            self.coordinator.end_sync()
        return False  # Don't suppress exceptions
