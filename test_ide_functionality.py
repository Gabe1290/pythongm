#!/usr/bin/env python3
"""
Automated test script for PyGameMaker IDE
Tests basic functionality and reports any errors
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all core modules can be imported"""
    print("=" * 60)
    print("Testing Module Imports...")
    print("=" * 60)
    
    modules_to_test = [
        ('PySide6.QtWidgets', 'QApplication'),
        ('core.ide_window', 'PyGameMakerIDE'),
        ('core.project_manager', 'ProjectManager'),
        ('core.asset_manager', 'AssetManager'),
        ('editors.room_editor', 'RoomEditor'),
        ('editors.object_editor', 'ObjectEditor'),
        ('export.Kivy.kivy_exporter', 'KivyExporter'),
        ('export.HTML5.html5_exporter', 'HTML5Exporter'),
        ('events.event_types', 'EventType'),
        ('events.action_types', 'ActionType'),
    ]
    
    results = []
    for module_name, class_name in modules_to_test:
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            print(f"✅ {module_name}.{class_name}")
            results.append((module_name, class_name, True, None))
        except Exception as e:
            print(f"❌ {module_name}.{class_name}: {e}")
            results.append((module_name, class_name, False, str(e)))
    
    return results

def test_project_structure():
    """Test that required directories and files exist"""
    print("\n" + "=" * 60)
    print("Testing Project Structure...")
    print("=" * 60)
    
    required_paths = [
        'core/',
        'editors/',
        'export/',
        'events/',
        'widgets/',
        'utils/',
        'dialogs/',
        'runtime/',
        'translations/',
        'main.py',
        'requirements.txt',
    ]
    
    results = []
    for path in required_paths:
        full_path = Path(__file__).parent / path
        exists = full_path.exists()
        print(f"{'✅' if exists else '❌'} {path}")
        results.append((path, exists))
    
    return results

def test_event_action_definitions():
    """Test that event and action types are properly defined"""
    print("\n" + "=" * 60)
    print("Testing Event & Action Definitions...")
    print("=" * 60)
    
    try:
        from events.event_types import EventType
        from events.action_types import ActionType
        
        # Count events
        event_count = len([attr for attr in dir(EventType) if not attr.startswith('_')])
        print(f"✅ EventType defined with {event_count} events")
        
        # Count actions
        action_count = len([attr for attr in dir(ActionType) if not attr.startswith('_')])
        print(f"✅ ActionType defined with {action_count} actions")
        
        return True, event_count, action_count
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, 0, 0

def test_exporter_availability():
    """Test that exporters are available"""
    print("\n" + "=" * 60)
    print("Testing Exporters...")
    print("=" * 60)
    
    exporters = []
    
    # Test Kivy exporter
    try:
        from export.Kivy.kivy_exporter import KivyExporter
        print("✅ Kivy Exporter available")
        exporters.append(('Kivy', True))
    except Exception as e:
        print(f"❌ Kivy Exporter: {e}")
        exporters.append(('Kivy', False))
    
    # Test HTML5 exporter
    try:
        from export.HTML5.html5_exporter import HTML5Exporter
        print("✅ HTML5 Exporter available")
        exporters.append(('HTML5', True))
    except Exception as e:
        print(f"❌ HTML5 Exporter: {e}")
        exporters.append(('HTML5', False))
    
    # Test EXE exporter
    try:
        from export.exe.exe_exporter import ExeExporter
        print("✅ EXE Exporter available")
        exporters.append(('EXE', True))
    except Exception as e:
        print(f"❌ EXE Exporter: {e}")
        exporters.append(('EXE', False))
    
    return exporters

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("PyGameMaker IDE - Automated Functionality Test")
    print("=" * 60 + "\n")
    
    # Run tests
    import_results = test_imports()
    structure_results = test_project_structure()
    event_action_ok, event_count, action_count = test_event_action_definitions()
    exporter_results = test_exporter_availability()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    import_success = sum(1 for _, _, success, _ in import_results if success)
    import_total = len(import_results)
    print(f"Module Imports: {import_success}/{import_total} passed")
    
    structure_success = sum(1 for _, exists in structure_results if exists)
    structure_total = len(structure_results)
    print(f"Project Structure: {structure_success}/{structure_total} found")
    
    if event_action_ok:
        print(f"Events & Actions: ✅ ({event_count} events, {action_count} actions)")
    else:
        print("Events & Actions: ❌ Failed to load")
    
    exporter_success = sum(1 for _, success in exporter_results if success)
    exporter_total = len(exporter_results)
    print(f"Exporters: {exporter_success}/{exporter_total} available")
    
    # Overall result
    all_passed = (
        import_success == import_total and
        structure_success == structure_total and
        event_action_ok and
        exporter_success == exporter_total
    )
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED")
    else:
        print("⚠️  SOME TESTS FAILED - See details above")
    print("=" * 60 + "\n")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
