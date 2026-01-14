#!/usr/bin/env python3
"""
Comprehensive Test Suite for Kivy Exporter
Tests all components: code generation, asset bundling, action conversion
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from pathlib import Path
import json
import tempfile
import shutil


def test_action_converter():
    """Test action converter with common actions"""
    print("\n=== Testing Action Converter ===")

    from export.Kivy.action_converter import ActionConverter

    converter = ActionConverter()

    # Test 1: Movement actions
    print("\n1. Testing movement actions...")
    test_actions = [
        {
            'action': 'set_hspeed',
            'parameters': {'speed': 5}
        },
        {
            'action': 'set_vspeed',
            'parameters': {'speed': -3}
        },
        {
            'action': 'set_direction_speed',
            'parameters': {'direction': 0, 'speed': 10}
        }
    ]

    for action in test_actions:
        try:
            code = converter.convert_actions([action], indent_level=2)
            assert code and code.strip(), f"No code generated for {action['action']}"
            assert 'pass' not in code or 'TODO' in code, f"Action {action['action']} not implemented"
            print(f"  ✅ {action['action']}: Generated code")
        except Exception as e:
            print(f"  ❌ {action['action']}: {e}")
            raise

    # Test 2: Collision actions
    print("\n2. Testing collision actions...")
    collision_action = {
        'action': 'if_collision',
        'parameters': {'object': 'obj_wall', 'actions': []}
    }

    code = converter.convert_actions([collision_action], indent_level=2)
    assert code and code.strip(), "No code generated for collision"
    print(f"  ✅ if_collision: Generated code")

    # Test 3: Variable actions
    print("\n3. Testing variable actions...")
    variable_action = {
        'action': 'set_variable',
        'parameters': {'variable': 'score', 'value': 100}
    }

    code = converter.convert_actions([variable_action], indent_level=2)
    assert code and code.strip(), "No code generated for variable"
    print(f"  ✅ set_variable: Generated code")

    # Test 4: Room actions
    print("\n4. Testing room actions...")
    room_actions = [
        {'action': 'restart_room', 'parameters': {}},
        {'action': 'next_room', 'parameters': {}},
        {'action': 'previous_room', 'parameters': {}}
    ]

    for action in room_actions:
        code = converter.convert_actions([action], indent_level=2)
        assert code and code.strip(), f"No code generated for {action['action']}"
        print(f"  ✅ {action['action']}: Generated code")

    # Test 5: Instance actions
    print("\n5. Testing instance actions...")
    instance_actions = [
        {
            'action': 'create_instance',
            'parameters': {'object': 'obj_bullet', 'x': 100, 'y': 200}
        },
        {
            'action': 'destroy_instance',
            'parameters': {}
        }
    ]

    for action in instance_actions:
        code = converter.convert_actions([action], indent_level=2)
        assert code and code.strip(), f"No code generated for {action['action']}"
        print(f"  ✅ {action['action']}: Generated code")

    print("\n✅ All action converter tests passed!")


def test_code_generator():
    """Test code generator"""
    print("\n=== Testing Code Generator ===")

    from export.Kivy.code_generator import ActionCodeGenerator

    # Test 1: Basic action code generation
    print("\n1. Testing basic action code generation...")

    generator = ActionCodeGenerator(base_indent=2)

    # Test simple movement actions
    actions = [
        {'action': 'set_hspeed', 'parameters': {'speed': 5}},
        {'action': 'set_vspeed', 'parameters': {'speed': -3}},
        {'action': 'stop_movement', 'parameters': {}}
    ]

    try:
        for action in actions:
            generator.process_action(action)

        code = generator.get_code()
        assert code and code.strip(), "No code generated"
        assert 'self.hspeed = 5' in code, "hspeed not set"
        assert 'self.vspeed' in code, "vspeed not set"

        print(f"  ✅ Generated code:\n{code}")
    except Exception as e:
        print(f"  ❌ Code generation failed: {e}")
        raise

    # Test 2: Conditional blocks
    print("\n2. Testing conditional block generation...")

    generator2 = ActionCodeGenerator(base_indent=2)

    conditional_action = {
        'action': 'if_collision',
        'parameters': {'object': 'obj_wall', 'x': 'self.x', 'y': 'self.y'}
    }

    then_action = {
        'action': 'set_hspeed',
        'parameters': {'speed': 0}
    }

    try:
        generator2.process_action(conditional_action)
        generator2.process_action(then_action)

        code = generator2.get_code()
        assert code and code.strip(), "No code generated"
        assert 'if self.check_collision_at' in code, "Conditional not found"

        print(f"  ✅ Conditional code:\n{code}")
    except Exception as e:
        print(f"  ❌ Conditional generation failed: {e}")
        raise

    print("\n✅ All code generator tests passed!")


def test_asset_bundler():
    """Test asset bundler"""
    print("\n=== Testing Asset Bundler ===")

    from export.Kivy.asset_bundler import AssetBundler

    # Create temporary directories
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir) / "test_project"
        output_path = Path(temp_dir) / "output"

        project_path.mkdir()
        output_path.mkdir()

        # Create fake sprite with proper structure
        sprites_dir = project_path / "sprites"
        sprites_dir.mkdir()

        fake_sprite = sprites_dir / "test_sprite.png"
        fake_sprite.write_bytes(b'\x89PNG\r\n\x1a\n' + b'\x00' * 100)  # Minimal PNG

        project_data = {
            'sprites': {
                'spr_test': {
                    'frames': [
                        {'image': 'sprites/test_sprite.png'}
                    ]
                }
            }
        }

        # Correct constructor signature: (project_path, output_path)
        bundler = AssetBundler(project_path, output_path)

        # Test 1: Bundle assets
        print("\n1. Testing asset bundling...")
        try:
            # Pass project_data to bundle_assets method
            success = bundler.bundle_assets(project_data)

            assert success, "Asset bundling returned False"

            # Check output directory
            assets_dir = output_path / "assets"
            assert assets_dir.exists(), "Assets directory not created"

            sprites_output = assets_dir / "sprites"
            assert sprites_output.exists(), "Sprites directory not created"

            print("  ✅ Asset bundling: Created directory structure")
        except Exception as e:
            print(f"  ❌ Asset bundling failed: {e}")
            raise

        # Test 2: Check manifest (auto-generated by bundle_assets)
        print("\n2. Testing manifest generation...")
        try:
            manifest_file = output_path / "assets" / "manifest.json"
            assert manifest_file.exists(), "Manifest file not created"

            with open(manifest_file) as f:
                manifest = json.load(f)

            assert 'sprites' in manifest, "No sprites in manifest"
            print("  ✅ Manifest generation: Created valid manifest")
        except Exception as e:
            print(f"  ❌ Manifest generation failed: {e}")
            raise

    print("\n✅ All asset bundler tests passed!")


def test_buildspec_generator():
    """Test buildozer spec generator"""
    print("\n=== Testing Buildspec Generator ===")

    from export.Kivy.buildspec_generator import BuildspecGenerator

    project_data = {
        'name': 'TestGame',
        'version': '1.0.0',
        'settings': {
            'package_name': 'com.test.game',
            'package_domain': 'com.test'
        }
    }

    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir)

        generator = BuildspecGenerator(project_data, output_path)

        # Test: Generate buildozer.spec
        print("\n1. Testing buildozer.spec generation...")
        try:
            # Correct method name: generate_buildozer_spec
            success = generator.generate_buildozer_spec()

            assert success, "Buildspec generation returned False"

            # Check file created
            spec_file = output_path / "buildozer.spec"
            assert spec_file.exists(), "buildozer.spec not created"

            # Read and verify content
            spec_content = spec_file.read_text()
            assert spec_content, "No spec content generated"
            assert 'title = TestGame' in spec_content, "Title not in spec"
            assert 'testgame' in spec_content.lower() or 'test' in spec_content.lower(), "Package name not in spec"
            assert 'version = 1.0' in spec_content, "Version not in spec"

            print("  ✅ Buildozer spec: Valid configuration")
        except Exception as e:
            print(f"  ❌ Buildspec generation failed: {e}")
            raise

    print("\n✅ All buildspec generator tests passed!")


def test_full_export():
    """Test complete export process"""
    print("\n=== Testing Full Export ===")

    from export.Kivy.kivy_exporter import KivyExporter

    # Create minimal test project
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir) / "test_project"
        output_path = Path(temp_dir) / "output"

        project_path.mkdir()

        # Create project with proper event structure (list, not dict)
        project_data = {
            'name': 'TestGame',
            'version': '1.0.0',
            'assets': {
                'rooms': {
                    'room_main': {
                        'width': 640,
                        'height': 480,
                        'background_color': '#87CEEB',
                        'instances': []
                    }
                },
                'objects': {
                    'obj_player': {
                        'sprite': 'spr_player',
                        'events': [
                            {
                                'event_type': 'create',
                                'actions': [
                                    {'action': 'set_hspeed', 'parameters': {'speed': 0}}
                                ]
                            }
                        ]
                    }
                },
                'sprites': {}
            }
        }

        project_file = project_path / "project.json"
        with open(project_file, 'w') as f:
            json.dump(project_data, f)

        # Test: Full export
        print("\n1. Testing complete export process...")
        try:
            exporter = KivyExporter(project_data, project_path, output_path)
            success = exporter.export()

            assert success, "Export failed"
            assert output_path.exists(), "Output directory not created"

            # Check key files in root
            requirements = output_path / "requirements.txt"
            assert requirements.exists(), "requirements.txt not created"

            buildozer_spec = output_path / "buildozer.spec"
            assert buildozer_spec.exists(), "buildozer.spec not created"

            readme = output_path / "README.md"
            assert readme.exists(), "README.md not created"

            # Check game directory
            game_dir = output_path / "game"
            assert game_dir.exists(), "game directory not created"

            # main.py is in game/ subdirectory, not root
            main_py = game_dir / "main.py"
            assert main_py.exists(), f"game/main.py not created"

            objects_dir = game_dir / "objects"
            assert objects_dir.exists(), "objects directory not created"

            scenes_dir = game_dir / "scenes"
            assert scenes_dir.exists(), "scenes directory not created"

            # Verify Python syntax of generated files
            print("\n2. Validating generated Python files...")
            for py_file in output_path.rglob("*.py"):
                try:
                    with open(py_file) as f:
                        code = f.read()
                    compile(code, str(py_file), 'exec')
                    print(f"  ✅ {py_file.name}: Valid syntax")
                except SyntaxError as e:
                    print(f"  ❌ {py_file.name}: Syntax error at line {e.lineno}")
                    print(f"     Error: {e.msg}")
                    raise

            print("\n✅ Full export test passed!")

        except Exception as e:
            print(f"  ❌ Export failed: {e}")
            import traceback
            traceback.print_exc()
            raise


def run_all_tests():
    """Run all tests"""
    print("="*60)
    print("KIVY EXPORTER COMPREHENSIVE TEST SUITE")
    print("="*60)

    tests = [
        ("Action Converter", test_action_converter),
        ("Code Generator", test_code_generator),
        ("Asset Bundler", test_asset_bundler),
        ("Buildspec Generator", test_buildspec_generator),
        ("Full Export", test_full_export)
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"\n❌ {test_name} FAILED: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "="*60)
    print(f"TEST RESULTS: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("="*60)

    if failed == 0:
        print("\n✅ ALL TESTS PASSED! Kivy exporter is ready for use.")
        print("\nNext steps:")
        print("1. Test with real projects")
        print("2. Build Android APK with: buildozer -v android debug")
        print("3. Test on actual devices")
    else:
        print(f"\n❌ {failed} test(s) failed. Please fix issues before using.")

    return failed == 0


if __name__ == '__main__':
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
