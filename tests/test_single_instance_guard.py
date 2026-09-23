"""Regression tests for core/single_instance.py.

The guard exists to stop a student ending up with many PyGameMaker IDE
processes pointed at the same project folder -- each instance's independent
saves silently accumulate rather than overwrite (folder save writes one file
per asset), so Test Game from any of them ends up loading the union of
everything every instance ever saved. A real classroom incident (2026-09-23)
had 10+ instances open this way.

Uses a hand-rolled offscreen QApplication (no qapp fixture) so this runs
without pytest-qt, matching this repo's audit-regression-test convention.
A unique per-test server name avoids colliding with a real IDE instance
that might be running on the machine executing the suite.
"""

import os
import time
import uuid

import pytest

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


@pytest.fixture
def offscreen_app():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture
def guard_module(monkeypatch):
    """core.single_instance with SERVER_NAME swapped to a unique per-test
    name, so tests never collide with each other or with a real running
    IDE instance on the machine."""
    import core.single_instance as single_instance
    unique = f"pygm2-test-single-instance-{uuid.uuid4().hex}"
    monkeypatch.setattr(single_instance, "SERVER_NAME", unique)
    return single_instance


def _pump_until(predicate, timeout=2.0):
    from PySide6.QtCore import QCoreApplication
    deadline = time.time() + timeout
    while not predicate() and time.time() < deadline:
        QCoreApplication.processEvents()
    return predicate()


class TestSingleInstanceGuard:

    def test_first_guard_becomes_primary(self, offscreen_app, guard_module):
        guard = guard_module.SingleInstanceGuard()
        try:
            assert guard.is_primary is True
        finally:
            guard.close()

    def test_second_guard_is_not_primary_and_notifies_the_first(self, offscreen_app, guard_module):
        primary = guard_module.SingleInstanceGuard()
        try:
            assert primary.is_primary

            notified = []
            primary.raise_requested.connect(lambda: notified.append(True))

            second = guard_module.SingleInstanceGuard()
            try:
                assert second.is_primary is False

                assert _pump_until(lambda: len(notified) == 1), (
                    "primary never received the second instance's connection"
                )
            finally:
                second.close()
        finally:
            primary.close()

    def test_a_third_instance_also_gets_turned_away(self, offscreen_app, guard_module):
        primary = guard_module.SingleInstanceGuard()
        try:
            notified = []
            primary.raise_requested.connect(lambda: notified.append(True))

            second = guard_module.SingleInstanceGuard()
            third = guard_module.SingleInstanceGuard()
            try:
                assert second.is_primary is False
                assert third.is_primary is False
                assert _pump_until(lambda: len(notified) == 2)
            finally:
                second.close()
                third.close()
        finally:
            primary.close()

    def test_closing_the_primary_frees_the_name_for_a_new_one(self, offscreen_app, guard_module):
        first = guard_module.SingleInstanceGuard()
        assert first.is_primary
        first.close()

        second = guard_module.SingleInstanceGuard()
        try:
            assert second.is_primary is True
        finally:
            second.close()

    def test_close_is_safe_to_call_when_never_primary(self, offscreen_app, guard_module):
        primary = guard_module.SingleInstanceGuard()
        try:
            second = guard_module.SingleInstanceGuard()
            assert second.is_primary is False
            second.close()  # must not raise
            second.close()  # idempotent
        finally:
            primary.close()
