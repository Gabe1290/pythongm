"""
Tests for the export module - HTML5, Kivy, EXE, and Linux exporters
"""

import pytest
import json
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))


# ============================================================================
# Helper to mock PySide6 for tests that need it
# ============================================================================

def mock_pyside6():
    """Create mock PySide6 module for tests"""
    mock_qobject = MagicMock()
    mock_qobject.__class__ = type

    mock_signal = MagicMock()
    mock_signal.connect = MagicMock()
    mock_signal.emit = MagicMock()

    mock_qtcore = MagicMock()
    mock_qtcore.QObject = mock_qobject
    mock_qtcore.Signal = MagicMock(return_value=mock_signal)
    mock_qtcore.QTimer = MagicMock()

    return {
        'PySide6': MagicMock(),
        'PySide6.QtCore': mock_qtcore,
        'PySide6.QtWidgets': MagicMock(),
    }


# ============================================================================
# HTML5 Exporter Tests
# ============================================================================

class TestHTML5ExporterBasics:
    """Test basic HTML5Exporter functionality"""

    @pytest.fixture
    def html5_exporter(self):
        """Create an HTML5Exporter instance with mocked templates"""
        with patch('builtins.open', create=True):
            with patch.object(Path, 'read_text') as mock_read:
                mock_read.return_value = "template content"
                from export.HTML5.html5_exporter import HTML5Exporter
                exporter = HTML5Exporter()
                exporter.template_html = "{game_name} {width} {height} {game_data} {sprites_data} {engine_code}"
                exporter.engine_code = "engine code"
                return exporter

    def test_init_loads_templates(self):
        """HTML5Exporter should load templates on init"""
        with patch.object(Path, 'read_text') as mock_read:
            mock_read.return_value = "template"
            from export.HTML5.html5_exporter import HTML5Exporter
            exporter = HTML5Exporter()

            assert mock_read.call_count == 2  # template_html and engine_code

    def test_encode_sprites_returns_dict(self, html5_exporter, temp_project_dir):
        """encode_sprites should return a dictionary"""
        project_data = {
            'assets': {
                'sprites': {},
                'backgrounds': {}
            }
        }
        result = html5_exporter.encode_sprites(temp_project_dir, project_data)

        assert isinstance(result, dict)

    def test_encode_sprites_handles_missing_files(self, html5_exporter, temp_project_dir):
        """encode_sprites should handle missing sprite files gracefully"""
        project_data = {
            'assets': {
                'sprites': {
                    'missing_sprite': {
                        'file_path': 'sprites/nonexistent.png'
                    }
                },
                'backgrounds': {}
            }
        }
        result = html5_exporter.encode_sprites(temp_project_dir, project_data)

        # Should return empty dict since file doesn't exist
        assert 'missing_sprite' not in result

    def test_encode_sprites_encodes_existing_files(self, html5_exporter, temp_project_dir):
        """encode_sprites should encode existing sprite files as base64"""
        from PIL import Image

        # Create a test sprite
        sprite_path = temp_project_dir / "sprites" / "test.png"
        Image.new("RGBA", (32, 32), (255, 0, 0, 255)).save(sprite_path)

        project_data = {
            'assets': {
                'sprites': {
                    'test_sprite': {
                        'file_path': 'sprites/test.png'
                    }
                },
                'backgrounds': {}
            }
        }
        result = html5_exporter.encode_sprites(temp_project_dir, project_data)

        assert 'test_sprite' in result
        assert result['test_sprite'].startswith('data:image/png;base64,')

    def test_export_creates_html_file(self, html5_exporter, temp_project_dir, temp_dir):
        """export should create an HTML file"""
        # Create project.json
        project_data = {
            'name': 'TestGame',
            'settings': {'window_width': 800, 'window_height': 600},
            'assets': {
                'sprites': {},
                'backgrounds': {},
                'rooms': {}
            }
        }
        with open(temp_project_dir / "project.json", 'w') as f:
            json.dump(project_data, f)

        output_dir = temp_dir / "output"
        output_dir.mkdir()

        result = html5_exporter.export(temp_project_dir, output_dir)

        assert result is True
        assert (output_dir / "TestGame.html").exists()

    def test_export_fails_on_invalid_project(self, html5_exporter, temp_dir):
        """export should fail gracefully for invalid projects"""
        output_dir = temp_dir / "output"
        output_dir.mkdir()

        result = html5_exporter.export(temp_dir, output_dir)

        assert result is False


class TestHTML5ExporterMimeTypes:
    """Test MIME type detection for sprites"""

    @pytest.fixture
    def html5_exporter(self):
        """Create an HTML5Exporter instance"""
        with patch.object(Path, 'read_text') as mock_read:
            mock_read.return_value = "template"
            from export.HTML5.html5_exporter import HTML5Exporter
            return HTML5Exporter()

    def test_encode_jpg_sprite(self, html5_exporter, temp_project_dir):
        """encode_sprites should use correct MIME type for JPG"""
        from PIL import Image

        sprite_path = temp_project_dir / "sprites" / "test.jpg"
        Image.new("RGB", (32, 32), (255, 0, 0)).save(sprite_path)

        project_data = {
            'assets': {
                'sprites': {
                    'test': {'file_path': 'sprites/test.jpg'}
                },
                'backgrounds': {}
            }
        }
        result = html5_exporter.encode_sprites(temp_project_dir, project_data)

        assert result['test'].startswith('data:image/jpeg;base64,')

    def test_encode_gif_sprite(self, html5_exporter, temp_project_dir):
        """encode_sprites should use correct MIME type for GIF"""
        from PIL import Image

        sprite_path = temp_project_dir / "sprites" / "test.gif"
        Image.new("P", (32, 32)).save(sprite_path)

        project_data = {
            'assets': {
                'sprites': {
                    'test': {'file_path': 'sprites/test.gif'}
                },
                'backgrounds': {}
            }
        }
        result = html5_exporter.encode_sprites(temp_project_dir, project_data)

        assert result['test'].startswith('data:image/gif;base64,')


# ============================================================================
# Kivy Exporter Tests
# ============================================================================

class TestKivyExporterBasics:
    """Test basic KivyExporter functionality"""

    @pytest.fixture
    def kivy_exporter(self, temp_project_dir, temp_dir):
        """Create a KivyExporter instance"""
        from export.Kivy.kivy_exporter import KivyExporter

        project_data = {
            'name': 'TestGame',
            'settings': {'window_width': 800, 'window_height': 600},
            'assets': {
                'sprites': {},
                'sounds': {},
                'backgrounds': {},
                'objects': {},
                'rooms': {}
            }
        }
        output_path = temp_dir / "kivy_output"
        output_path.mkdir()

        return KivyExporter(project_data, temp_project_dir, output_path)

    def test_init_stores_paths(self, temp_project_dir, temp_dir):
        """KivyExporter should store project and output paths"""
        from export.Kivy.kivy_exporter import KivyExporter

        project_data = {'name': 'Test', 'assets': {}}
        output_path = temp_dir / "output"
        output_path.mkdir()

        exporter = KivyExporter(project_data, temp_project_dir, output_path)

        assert exporter.project_path == temp_project_dir
        assert exporter.output_path == output_path

    def test_create_directory_structure(self, kivy_exporter):
        """_create_directory_structure should create required directories"""
        kivy_exporter._create_directory_structure()

        expected_dirs = [
            kivy_exporter.output_path / "game",
            kivy_exporter.output_path / "game" / "assets",
            kivy_exporter.output_path / "game" / "assets" / "images",
            kivy_exporter.output_path / "game" / "assets" / "sounds",
            kivy_exporter.output_path / "game" / "objects",
            kivy_exporter.output_path / "game" / "scenes",
        ]

        for dir_path in expected_dirs:
            assert dir_path.exists(), f"Missing directory: {dir_path}"

    def test_count_assets_empty(self, kivy_exporter):
        """_count_assets should return 0 for empty project"""
        count = kivy_exporter._count_assets()
        assert count == 0

    def test_count_assets_with_sprites(self, temp_project_dir, temp_dir):
        """_count_assets should count sprites correctly"""
        from export.Kivy.kivy_exporter import KivyExporter

        project_data = {
            'name': 'Test',
            'assets': {
                'sprites': {'spr1': {}, 'spr2': {}},
                'sounds': {'snd1': {}},
                'backgrounds': {}
            }
        }
        output_path = temp_dir / "output"
        output_path.mkdir()

        exporter = KivyExporter(project_data, temp_project_dir, output_path)
        count = exporter._count_assets()

        assert count == 3  # 2 sprites + 1 sound

    def test_get_room_class_name(self, kivy_exporter):
        """_get_room_class_name should convert snake_case to PascalCase"""
        assert kivy_exporter._get_room_class_name("room_start") == "RoomStart"
        assert kivy_exporter._get_room_class_name("room_game_over") == "RoomGameOver"
        assert kivy_exporter._get_room_class_name("room1") == "Room1"

    def test_get_object_class_name(self, kivy_exporter):
        """_get_object_class_name should convert snake_case to PascalCase"""
        assert kivy_exporter._get_object_class_name("obj_player") == "ObjPlayer"
        assert kivy_exporter._get_object_class_name("obj_wall") == "ObjWall"


class TestKivyExporterAssetExport:
    """Test Kivy asset export functionality"""

    @pytest.fixture
    def kivy_exporter(self, temp_project_dir, temp_dir):
        """Create a KivyExporter instance"""
        from export.Kivy.kivy_exporter import KivyExporter

        project_data = {
            'name': 'TestGame',
            'assets': {
                'sprites': {},
                'sounds': {},
                'backgrounds': {},
                'objects': {},
                'rooms': {}
            }
        }
        output_path = temp_dir / "kivy_output"
        output_path.mkdir()

        return KivyExporter(project_data, temp_project_dir, output_path)

    def test_export_sprite_copies_file(self, kivy_exporter, temp_project_dir):
        """_export_sprite should copy sprite file to output"""
        from PIL import Image

        # Create directory structure first
        kivy_exporter._create_directory_structure()

        # Create a test sprite
        sprite_path = temp_project_dir / "sprites" / "player.png"
        Image.new("RGBA", (32, 32), (255, 0, 0, 255)).save(sprite_path)

        # Export the sprite
        kivy_exporter._export_sprite("player", {'file_path': 'sprites/player.png'})

        # Check it was copied
        output_sprite = kivy_exporter.output_path / "game" / "assets" / "images" / "player.png"
        assert output_sprite.exists()

    def test_export_sprite_handles_missing_file(self, kivy_exporter):
        """_export_sprite should handle missing files gracefully"""
        kivy_exporter._create_directory_structure()

        # This should not raise an exception
        kivy_exporter._export_sprite("missing", {'file_path': 'sprites/nonexistent.png'})


class TestKivyExporterCodeGeneration:
    """Test Kivy code generation functionality"""

    @pytest.fixture
    def kivy_exporter(self, temp_project_dir, temp_dir):
        """Create a KivyExporter instance with rooms and objects"""
        from export.Kivy.kivy_exporter import KivyExporter

        project_data = {
            'name': 'TestGame',
            'settings': {'window_width': 800, 'window_height': 600},
            'assets': {
                'sprites': {
                    'spr_player': {'file_path': 'sprites/player.png'}
                },
                'sounds': {},
                'backgrounds': {},
                'objects': {
                    'obj_player': {
                        'sprite': 'spr_player',
                        'solid': False,
                        'visible': True,
                        'events': []
                    }
                },
                'rooms': {
                    'room_start': {
                        'width': 800,
                        'height': 600,
                        'instances': [
                            {'object_type': 'obj_player', 'x': 100, 'y': 100}
                        ]
                    }
                }
            }
        }
        output_path = temp_dir / "kivy_output"
        output_path.mkdir()

        return KivyExporter(project_data, temp_project_dir, output_path)

    def test_generate_main_app_creates_file(self, kivy_exporter):
        """_generate_main_app should create main.py"""
        kivy_exporter._create_directory_structure()
        kivy_exporter._generate_main_app()

        main_file = kivy_exporter.output_path / "game" / "main.py"
        assert main_file.exists()

        content = main_file.read_text()
        assert "class GameApp" in content
        assert "TestGame" in content

    def test_generate_utils_creates_file(self, kivy_exporter):
        """_generate_utils should create utils.py"""
        kivy_exporter._create_directory_structure()
        kivy_exporter._generate_utils()

        utils_file = kivy_exporter.output_path / "game" / "utils.py"
        assert utils_file.exists()

        content = utils_file.read_text()
        assert "def load_image" in content

    def test_generate_base_object_creates_file(self, kivy_exporter):
        """_generate_base_object should create base_object.py"""
        kivy_exporter._create_directory_structure()
        kivy_exporter._generate_base_object()

        base_file = kivy_exporter.output_path / "game" / "objects" / "base_object.py"
        assert base_file.exists()

        content = base_file.read_text()
        assert "class GameObject" in content
        assert "def check_collision" in content

    def test_generate_buildozer_spec_creates_file(self, kivy_exporter):
        """_generate_buildozer_spec should create buildozer.spec"""
        kivy_exporter._create_directory_structure()
        kivy_exporter._generate_buildozer_spec()

        spec_file = kivy_exporter.output_path / "buildozer.spec"
        assert spec_file.exists()

        content = spec_file.read_text()
        assert "testgame" in content.lower()

    def test_generate_requirements_creates_file(self, kivy_exporter):
        """_generate_requirements should create requirements.txt"""
        kivy_exporter._create_directory_structure()
        kivy_exporter._generate_requirements()

        req_file = kivy_exporter.output_path / "requirements.txt"
        assert req_file.exists()

        content = req_file.read_text()
        assert "kivy" in content

    def test_full_export_creates_all_files(self, kivy_exporter, temp_project_dir):
        """export should create all necessary files"""
        from PIL import Image

        # Create a test sprite
        sprite_path = temp_project_dir / "sprites" / "player.png"
        Image.new("RGBA", (32, 32), (255, 0, 0, 255)).save(sprite_path)

        result = kivy_exporter.export()

        assert result is True

        # Check all expected files exist
        expected_files = [
            "game/main.py",
            "game/utils.py",
            "game/objects/base_object.py",
            "game/objects/obj_player.py",
            "game/scenes/room_start.py",
            "buildozer.spec",
            "requirements.txt",
            "README.md",
        ]

        for file_path in expected_files:
            full_path = kivy_exporter.output_path / file_path
            assert full_path.exists(), f"Missing file: {file_path}"


class TestKivyExporterEvents:
    """Test Kivy event code generation"""

    @pytest.fixture
    def kivy_exporter(self, temp_project_dir, temp_dir):
        """Create a KivyExporter instance"""
        from export.Kivy.kivy_exporter import KivyExporter

        project_data = {
            'name': 'TestGame',
            'assets': {
                'sprites': {},
                'sounds': {},
                'backgrounds': {},
                'objects': {},
                'rooms': {}
            }
        }
        output_path = temp_dir / "kivy_output"
        output_path.mkdir()

        return KivyExporter(project_data, temp_project_dir, output_path)

    def test_get_event_method_name_create(self, kivy_exporter):
        """_get_event_method_name should return on_create for create event"""
        event = {'event_type': 'create'}
        assert kivy_exporter._get_event_method_name(event) == 'on_create'

    def test_get_event_method_name_step(self, kivy_exporter):
        """_get_event_method_name should return on_update for step event"""
        event = {'event_type': 'step'}
        assert kivy_exporter._get_event_method_name(event) == 'on_update'

    def test_get_event_method_name_collision(self, kivy_exporter):
        """_get_event_method_name should handle collision events"""
        event = {'event_type': 'collision_with_obj_wall'}
        assert kivy_exporter._get_event_method_name(event) == 'on_collision_obj_wall'

    def test_get_event_method_name_alarm(self, kivy_exporter):
        """_get_event_method_name should handle alarm events"""
        event = {'event_type': 'alarm_0'}
        assert kivy_exporter._get_event_method_name(event) == 'on_alarm_0'


# ============================================================================
# EXE Exporter Tests
# ============================================================================

# Skip EXE exporter tests if PySide6 is not available
# These tests require Qt for signals
try:
    HAS_PYSIDE6 = True
except ImportError:
    HAS_PYSIDE6 = False


@pytest.mark.skipif(not HAS_PYSIDE6, reason="PySide6 not available")
class TestExeExporterBasics:
    """Test basic ExeExporter functionality"""

    @pytest.fixture
    def exe_exporter(self):
        """Create an ExeExporter instance"""
        from export.exe.exe_exporter import ExeExporter
        return ExeExporter()

    def test_init_creates_instance(self, exe_exporter):
        """ExeExporter should initialize correctly"""
        assert exe_exporter.project_path is None
        assert exe_exporter.output_path is None
        assert exe_exporter.export_settings == {}

    def test_has_signals(self, exe_exporter):
        """ExeExporter should have progress and completion signals"""
        assert hasattr(exe_exporter, 'progress_update')
        assert hasattr(exe_exporter, 'export_complete')

    def test_check_pyinstaller_returns_bool(self, exe_exporter):
        """_check_pyinstaller should return boolean"""
        result = exe_exporter._check_pyinstaller()
        assert isinstance(result, bool)

    def test_check_kivy_returns_bool(self, exe_exporter):
        """_check_kivy should return boolean"""
        result = exe_exporter._check_kivy()
        assert isinstance(result, bool)

    def test_check_pillow_returns_bool(self, exe_exporter):
        """_check_pillow should return boolean"""
        result = exe_exporter._check_pillow()
        assert isinstance(result, bool)


@pytest.mark.skipif(not HAS_PYSIDE6, reason="PySide6 not available")
class TestExeExporterDependencyChecks:
    """Test EXE exporter dependency checking"""

    @pytest.fixture
    def exe_exporter(self):
        """Create an ExeExporter instance"""
        from export.exe.exe_exporter import ExeExporter
        return ExeExporter()

    def test_export_fails_without_pyinstaller(self, exe_exporter, temp_project_dir, temp_dir):
        """export_project should fail if PyInstaller is not installed"""
        # Create project file
        project_file = temp_project_dir / "project.json"
        with open(project_file, 'w') as f:
            json.dump({'name': 'Test'}, f)

        # Mock PyInstaller not installed
        with patch.object(exe_exporter, '_check_pyinstaller', return_value=False):
            signal_spy = MagicMock()
            exe_exporter.export_complete.connect(signal_spy)

            result = exe_exporter.export_project(
                str(temp_project_dir),
                str(temp_dir / "output"),
                {}
            )

            assert result is False
            signal_spy.assert_called_once()
            args = signal_spy.call_args[0]
            assert args[0] is False
            assert "PyInstaller" in args[1]

    def test_export_fails_without_kivy(self, exe_exporter, temp_project_dir, temp_dir):
        """export_project should fail if Kivy is not installed"""
        project_file = temp_project_dir / "project.json"
        with open(project_file, 'w') as f:
            json.dump({'name': 'Test'}, f)

        with patch.object(exe_exporter, '_check_pyinstaller', return_value=True):
            with patch.object(exe_exporter, '_check_kivy', return_value=False):
                signal_spy = MagicMock()
                exe_exporter.export_complete.connect(signal_spy)

                result = exe_exporter.export_project(
                    str(temp_project_dir),
                    str(temp_dir / "output"),
                    {}
                )

                assert result is False
                signal_spy.assert_called_once()
                args = signal_spy.call_args[0]
                assert "Kivy" in args[1]


@pytest.mark.skipif(not HAS_PYSIDE6, reason="PySide6 not available")
class TestExeExporterBuildDirectory:
    """Test EXE exporter build directory handling"""

    @pytest.fixture
    def exe_exporter(self, temp_project_dir):
        """Create an ExeExporter instance with project path set"""
        from export.exe.exe_exporter import ExeExporter
        exporter = ExeExporter()
        exporter.project_path = temp_project_dir / "project.json"
        return exporter

    def test_create_build_directory_creates_dir(self, exe_exporter, temp_project_dir):
        """_create_build_directory should create build directory"""
        build_dir = exe_exporter._create_build_directory()

        assert build_dir.exists()
        assert build_dir.is_dir()
        assert "build_temp_exe" in str(build_dir)

        # Cleanup
        shutil.rmtree(build_dir)

    def test_create_build_directory_cleans_existing(self, exe_exporter, temp_project_dir):
        """_create_build_directory should clean existing build directory"""
        # Create an existing build directory with content
        existing_build = temp_project_dir / "build_temp_exe"
        existing_build.mkdir()
        (existing_build / "old_file.txt").write_text("old content")

        build_dir = exe_exporter._create_build_directory()

        assert build_dir.exists()
        assert not (build_dir / "old_file.txt").exists()

        # Cleanup
        shutil.rmtree(build_dir)


# ============================================================================
# Linux Exporter Tests
# ============================================================================

@pytest.mark.skipif(not HAS_PYSIDE6, reason="PySide6 not available")
class TestLinuxExporterBasics:
    """Test basic LinuxExporter functionality"""

    @pytest.fixture
    def linux_exporter(self):
        """Create a LinuxExporter instance"""
        from export.linux.linux_exporter import LinuxExporter
        return LinuxExporter()

    def test_init_creates_instance(self, linux_exporter):
        """LinuxExporter should initialize correctly"""
        assert linux_exporter.project_path is None
        assert linux_exporter.output_path is None
        assert linux_exporter.export_settings == {}

    def test_has_signals(self, linux_exporter):
        """LinuxExporter should have progress and completion signals"""
        assert hasattr(linux_exporter, 'progress_update')
        assert hasattr(linux_exporter, 'export_complete')

    def test_check_pyinstaller_returns_bool(self, linux_exporter):
        """_check_pyinstaller should return boolean"""
        result = linux_exporter._check_pyinstaller()
        assert isinstance(result, bool)

    def test_check_kivy_returns_bool(self, linux_exporter):
        """_check_kivy should return boolean"""
        result = linux_exporter._check_kivy()
        assert isinstance(result, bool)


@pytest.mark.skipif(not HAS_PYSIDE6, reason="PySide6 not available")
class TestLinuxExporterPlatformCheck:
    """Test Linux exporter platform checking"""

    @pytest.fixture
    def linux_exporter(self):
        """Create a LinuxExporter instance"""
        from export.linux.linux_exporter import LinuxExporter
        return LinuxExporter()

    def test_export_fails_on_non_linux(self, linux_exporter, temp_project_dir, temp_dir):
        """export_project should fail on non-Linux platforms"""
        project_file = temp_project_dir / "project.json"
        with open(project_file, 'w') as f:
            json.dump({'name': 'Test'}, f)

        with patch('platform.system', return_value='Windows'):
            signal_spy = MagicMock()
            linux_exporter.export_complete.connect(signal_spy)

            result = linux_exporter.export_project(
                str(temp_project_dir),
                str(temp_dir / "output"),
                {}
            )

            assert result is False
            signal_spy.assert_called_once()
            args = signal_spy.call_args[0]
            assert args[0] is False
            assert "Linux" in args[1]


# ============================================================================
# Export Function Tests
# ============================================================================

class TestExportFunction:
    """Test the export_to_kivy convenience function"""

    def test_export_to_kivy_function(self, temp_project_dir, temp_dir):
        """export_to_kivy should work as a convenience function"""
        from export.Kivy.kivy_exporter import export_to_kivy

        project_data = {
            'name': 'TestGame',
            'assets': {
                'sprites': {},
                'sounds': {},
                'backgrounds': {},
                'objects': {},
                'rooms': {
                    'room_test': {
                        'width': 640,
                        'height': 480,
                        'instances': []
                    }
                }
            }
        }
        output_path = temp_dir / "export_output"
        output_path.mkdir()

        result = export_to_kivy(project_data, temp_project_dir, output_path)

        assert result is True
        assert (output_path / "game" / "main.py").exists()


# ============================================================================
# Action Code Generation Tests
# ============================================================================

class TestActionCodeGeneration:
    """Test action to code conversion"""

    @pytest.fixture
    def kivy_exporter(self, temp_project_dir, temp_dir):
        """Create a KivyExporter instance"""
        from export.Kivy.kivy_exporter import KivyExporter

        project_data = {
            'name': 'TestGame',
            'assets': {
                'sprites': {},
                'sounds': {},
                'backgrounds': {},
                'objects': {},
                'rooms': {}
            }
        }
        output_path = temp_dir / "kivy_output"
        output_path.mkdir()

        return KivyExporter(project_data, temp_project_dir, output_path)

    def test_convert_set_hspeed(self, kivy_exporter):
        """_convert_action_to_code should handle set_hspeed"""
        code = kivy_exporter._convert_action_to_code(
            'set_hspeed', {'value': 5}, 'step'
        )
        assert 'self.hspeed = 5' in code

    def test_convert_set_vspeed(self, kivy_exporter):
        """_convert_action_to_code should handle set_vspeed"""
        code = kivy_exporter._convert_action_to_code(
            'set_vspeed', {'value': -3}, 'step'
        )
        assert 'self.vspeed = -3' in code

    def test_convert_destroy_instance(self, kivy_exporter):
        """_convert_action_to_code should handle destroy_instance"""
        code = kivy_exporter._convert_action_to_code(
            'destroy_instance', {'target': 'self'}, 'step'
        )
        assert 'self.destroy()' in code

    def test_convert_destroy_other_in_collision(self, kivy_exporter):
        """_convert_action_to_code should destroy other in collision events"""
        code = kivy_exporter._convert_action_to_code(
            'destroy_instance', {'target': 'other'}, 'collision'
        )
        assert 'other.destroy()' in code

    def test_convert_show_message(self, kivy_exporter):
        """_convert_action_to_code should handle show_message"""
        code = kivy_exporter._convert_action_to_code(
            'show_message', {'message': 'Hello World'}, 'step'
        )
        assert "show_message" in code
        assert "Hello World" in code

    def test_convert_set_alarm(self, kivy_exporter):
        """_convert_action_to_code should handle set_alarm"""
        code = kivy_exporter._convert_action_to_code(
            'set_alarm', {'alarm_number': 0, 'steps': 60}, 'step'
        )
        assert 'self.alarms[0] = 60' in code

    def test_convert_set_score(self, kivy_exporter):
        """_convert_action_to_code should handle set_score"""
        code = kivy_exporter._convert_action_to_code(
            'set_score', {'value': 100, 'relative': False}, 'step'
        )
        assert 'set_score' in code
        assert '100' in code

    def test_convert_stop_movement(self, kivy_exporter):
        """_convert_action_to_code should handle stop_movement"""
        code = kivy_exporter._convert_action_to_code(
            'stop_movement', {}, 'step'
        )
        assert 'self.hspeed = 0' in code
        assert 'self.vspeed = 0' in code

    def test_convert_unknown_action(self, kivy_exporter):
        """_convert_action_to_code should return TODO for unknown actions"""
        code = kivy_exporter._convert_action_to_code(
            'unknown_action_type', {}, 'step'
        )
        assert '# TODO' in code
        assert 'unknown_action_type' in code

    # New action tests for the 10 previously unimplemented actions

    def test_convert_move_grid(self, kivy_exporter):
        """_convert_action_to_code should handle move_grid"""
        code = kivy_exporter._convert_action_to_code(
            'move_grid', {'direction': 'right', 'grid_size': 32}, 'step'
        )
        assert 'self.x +=' in code
        assert '32' in code

    def test_convert_move_grid_up(self, kivy_exporter):
        """_convert_action_to_code should handle move_grid up direction"""
        code = kivy_exporter._convert_action_to_code(
            'move_grid', {'direction': 'up', 'grid_size': 16}, 'step'
        )
        assert 'self.y +=' in code
        assert '16' in code

    def test_convert_move_towards(self, kivy_exporter):
        """_convert_action_to_code should handle move_towards"""
        code = kivy_exporter._convert_action_to_code(
            'move_towards', {'x': 100, 'y': 200, 'speed': 5}, 'step'
        )
        assert 'math' in code
        assert '100' in code
        assert '200' in code
        assert 'self.direction' in code
        assert 'self.speed' in code

    def test_convert_set_gravity(self, kivy_exporter):
        """_convert_action_to_code should handle set_gravity"""
        code = kivy_exporter._convert_action_to_code(
            'set_gravity', {'direction': 270, 'gravity': 0.5}, 'step'
        )
        assert 'self.gravity = 0.5' in code
        assert 'self.gravity_direction = 270' in code

    def test_convert_set_friction(self, kivy_exporter):
        """_convert_action_to_code should handle set_friction"""
        code = kivy_exporter._convert_action_to_code(
            'set_friction', {'friction': 0.2}, 'step'
        )
        assert 'self.friction = 0.2' in code

    def test_convert_reverse_horizontal(self, kivy_exporter):
        """_convert_action_to_code should handle reverse_horizontal"""
        code = kivy_exporter._convert_action_to_code(
            'reverse_horizontal', {}, 'step'
        )
        assert 'self.hspeed = -self.hspeed' in code

    def test_convert_reverse_vertical(self, kivy_exporter):
        """_convert_action_to_code should handle reverse_vertical"""
        code = kivy_exporter._convert_action_to_code(
            'reverse_vertical', {}, 'step'
        )
        assert 'self.vspeed = -self.vspeed' in code

    def test_convert_exit_event(self, kivy_exporter):
        """_convert_action_to_code should handle exit_event"""
        code = kivy_exporter._convert_action_to_code(
            'exit_event', {}, 'step'
        )
        assert 'return' in code


class TestActionCodeGeneratorBlocks:
    """Test block-based action code generation using ActionCodeGenerator directly"""

    @pytest.fixture
    def code_generator(self):
        """Create an ActionCodeGenerator instance"""
        from export.Kivy.code_generator import ActionCodeGenerator
        return ActionCodeGenerator(base_indent=2)

    def test_check_empty_generates_if(self, code_generator):
        """check_empty should generate if not collision check"""
        code_generator.process_action({
            'action_type': 'check_empty',
            'parameters': {'x': 100, 'y': 200}
        }, 'step')
        code = code_generator.get_code()
        assert 'if not self.check_collision_at(100, 200)' in code

    def test_check_empty_relative(self, code_generator):
        """check_empty with relative should offset from current position"""
        code_generator.process_action({
            'action_type': 'check_empty',
            'parameters': {'x': 32, 'y': 0, 'relative': True}
        }, 'step')
        code = code_generator.get_code()
        assert 'self.x + 32' in code

    def test_check_collision_generates_if(self, code_generator):
        """check_collision should generate if collision check"""
        code_generator.process_action({
            'action_type': 'check_collision',
            'parameters': {'object': 'obj_wall', 'x': 'self.x', 'y': 'self.y'}
        }, 'step')
        code = code_generator.get_code()
        assert "if self.check_collision_at(self.x, self.y, 'obj_wall')" in code

    def test_if_collision_at_generates_if(self, code_generator):
        """if_collision_at should generate if collision check"""
        code_generator.process_action({
            'action_type': 'if_collision_at',
            'parameters': {'target': 'obj_enemy', 'x': 50, 'y': 50}
        }, 'step')
        code = code_generator.get_code()
        assert "if self.check_collision_at(50, 50, 'obj_enemy')" in code

    def test_block_action_indentation(self, code_generator):
        """Block actions should properly handle indentation"""
        code_generator.process_action({
            'action_type': 'check_collision',
            'parameters': {'object': 'obj_wall'}
        }, 'step')
        code_generator.process_action({
            'action_type': 'destroy_instance',
            'parameters': {'target': 'self'}
        }, 'step')
        code_generator.process_action({'action_type': 'end_block', 'parameters': {}}, 'step')

        code = code_generator.get_code()
        lines = code.split('\n')

        # Find the destroy line and check it's indented more than the if
        if_line = next((l for l in lines if 'if self.check_collision' in l), None)
        destroy_line = next((l for l in lines if 'self.destroy()' in l), None)

        assert if_line is not None
        assert destroy_line is not None
        # Destroy should be indented more than if
        assert len(destroy_line) - len(destroy_line.lstrip()) > len(if_line) - len(if_line.lstrip())
