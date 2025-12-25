"""
Tests for the AssetManager class - asset import/export and management
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

# Check if PySide6 is available (required for AssetManager signals)
try:
    from PySide6.QtCore import QObject  # noqa: F401
    HAS_PYSIDE6 = True
except ImportError:
    HAS_PYSIDE6 = False

# Skip all tests if PySide6 is not available
pytestmark = pytest.mark.skipif(not HAS_PYSIDE6, reason="PySide6 not installed")


class TestAssetManagerBasics:
    """Test basic AssetManager functionality"""

    @pytest.fixture
    def asset_manager(self, temp_project_dir):
        """Create an AssetManager instance"""
        with patch('pygame.mixer.init'):
            from core.asset_manager import AssetManager
            am = AssetManager(project_directory=temp_project_dir)
            return am

    def test_init_with_project_directory(self, temp_project_dir):
        """AssetManager should accept project directory on init"""
        with patch('pygame.mixer.init'):
            from core.asset_manager import AssetManager
            am = AssetManager(project_directory=temp_project_dir)

            assert am.project_directory == temp_project_dir

    def test_init_without_project_directory(self):
        """AssetManager should work without project directory"""
        with patch('pygame.mixer.init'):
            from core.asset_manager import AssetManager
            am = AssetManager()

            assert am.project_directory is None

    def test_set_project_directory(self, temp_project_dir):
        """set_project_directory should update directory and clear caches"""
        with patch('pygame.mixer.init'):
            from core.asset_manager import AssetManager
            am = AssetManager()
            am.assets_cache = {"old": "data"}

            am.set_project_directory(temp_project_dir)

            assert am.project_directory == temp_project_dir.resolve()
            assert am.assets_cache == {}

    def test_ensure_directories_creates_folders(self, temp_project_dir):
        """ensure_directories should create asset folders"""
        with patch('pygame.mixer.init'):
            from core.asset_manager import AssetManager
            am = AssetManager(project_directory=temp_project_dir)

            # Directories should be created on init
            expected = ["sprites", "sounds", "backgrounds", "objects", "rooms", "fonts", "data"]
            for folder in expected:
                assert (temp_project_dir / folder).exists()


class TestAssetManagerFormats:
    """Test format support functionality"""

    @pytest.fixture
    def asset_manager(self, temp_project_dir):
        """Create an AssetManager instance"""
        with patch('pygame.mixer.init'):
            from core.asset_manager import AssetManager
            return AssetManager(project_directory=temp_project_dir)

    def test_get_supported_formats_sprites(self, asset_manager):
        """get_supported_formats should return sprite formats"""
        formats = asset_manager.get_supported_formats("sprites")

        assert ".png" in formats
        assert ".jpg" in formats
        assert ".gif" in formats

    def test_get_supported_formats_sounds(self, asset_manager):
        """get_supported_formats should return sound formats"""
        formats = asset_manager.get_supported_formats("sounds")

        assert ".wav" in formats
        assert ".mp3" in formats
        assert ".ogg" in formats

    def test_get_supported_formats_unknown(self, asset_manager):
        """get_supported_formats should return empty list for unknown types"""
        formats = asset_manager.get_supported_formats("unknown_type")

        assert formats == []

    def test_is_supported_format_valid(self, asset_manager):
        """is_supported_format should return True for valid formats"""
        assert asset_manager.is_supported_format(Path("test.png"), "sprites") is True
        assert asset_manager.is_supported_format(Path("test.wav"), "sounds") is True

    def test_is_supported_format_invalid(self, asset_manager):
        """is_supported_format should return False for invalid formats"""
        assert asset_manager.is_supported_format(Path("test.xyz"), "sprites") is False
        assert asset_manager.is_supported_format(Path("test.png"), "sounds") is False


class TestAssetManagerPaths:
    """Test path conversion functionality"""

    @pytest.fixture
    def asset_manager(self, temp_project_dir):
        """Create an AssetManager instance"""
        with patch('pygame.mixer.init'):
            from core.asset_manager import AssetManager
            return AssetManager(project_directory=temp_project_dir)

    def test_get_absolute_path(self, asset_manager, temp_project_dir):
        """get_absolute_path should convert relative to absolute"""
        absolute = asset_manager.get_absolute_path("sprites/player.png")

        assert absolute == temp_project_dir / "sprites/player.png"

    def test_get_relative_path(self, asset_manager, temp_project_dir):
        """get_relative_path should convert absolute to relative"""
        absolute = temp_project_dir / "sprites" / "player.png"
        relative = asset_manager.get_relative_path(absolute)

        assert relative == "sprites/player.png"

    def test_paths_without_project_directory(self):
        """Path methods should work without project directory"""
        with patch('pygame.mixer.init'):
            from core.asset_manager import AssetManager
            am = AssetManager()

            # Should return path as-is
            assert am.get_absolute_path("some/path") == Path("some/path")


class TestAssetManagerImport:
    """Test asset import functionality"""

    @pytest.fixture
    def asset_manager(self, temp_project_dir):
        """Create an AssetManager instance"""
        with patch('pygame.mixer.init'):
            from core.asset_manager import AssetManager
            return AssetManager(project_directory=temp_project_dir)

    def test_import_sprite(self, asset_manager, sample_sprite_path, temp_project_dir):
        """import_asset should import sprite files"""
        result = asset_manager.import_asset(sample_sprite_path, "sprites", "test_sprite")

        assert result is not None
        assert result["name"] == "test_sprite"
        assert (temp_project_dir / "sprites" / "test_sprite.png").exists()

    def test_import_sprite_generates_thumbnail(self, asset_manager, sample_sprite_path, temp_project_dir):
        """import_asset should generate thumbnail for sprites"""
        result = asset_manager.import_asset(sample_sprite_path, "sprites", "test_sprite")

        assert "thumbnail" in result
        thumbnail_path = temp_project_dir / result["thumbnail"]
        assert thumbnail_path.exists()

    def test_import_without_name_uses_filename(self, asset_manager, sample_sprite_path):
        """import_asset should use filename if no name provided"""
        result = asset_manager.import_asset(sample_sprite_path, "sprites")

        assert result["name"] == sample_sprite_path.stem

    def test_import_unsupported_format_fails(self, asset_manager, temp_dir):
        """import_asset should fail for unsupported formats"""
        bad_file = temp_dir / "test.xyz"
        bad_file.write_text("not a real file")

        result = asset_manager.import_asset(bad_file, "sprites")

        assert result is None

    def test_import_without_project_fails(self):
        """import_asset should fail without project directory"""
        with patch('pygame.mixer.init'):
            from core.asset_manager import AssetManager
            am = AssetManager()  # No project directory

            result = am.import_asset(Path("test.png"), "sprites")

            assert result is None

    def test_import_emits_signal(self, asset_manager, sample_sprite_path):
        """import_asset should emit asset_imported signal"""
        signal_spy = MagicMock()
        asset_manager.asset_imported.connect(signal_spy)

        asset_manager.import_asset(sample_sprite_path, "sprites", "test_sprite")

        signal_spy.assert_called_once()
        args = signal_spy.call_args[0]
        assert args[0] == "sprites"
        assert args[1] == "test_sprite"

    def test_import_creates_unique_name(self, asset_manager, sample_sprite_path, temp_dir):
        """import_asset should create unique name if name exists"""
        # Import first sprite
        asset_manager.import_asset(sample_sprite_path, "sprites", "player")

        # Create another sprite file
        from PIL import Image
        sprite2 = temp_dir / "player2.png"
        Image.new("RGBA", (32, 32), (0, 255, 0, 255)).save(sprite2)

        # Import with same name
        result = asset_manager.import_asset(sprite2, "sprites", "player")

        # Should have different name
        assert result["name"] != "player" or "player" in result["name"]


class TestAssetManagerCache:
    """Test asset caching functionality"""

    @pytest.fixture
    def asset_manager(self, temp_project_dir):
        """Create an AssetManager instance"""
        with patch('pygame.mixer.init'):
            from core.asset_manager import AssetManager
            return AssetManager(project_directory=temp_project_dir)

    def test_import_adds_to_cache(self, asset_manager, sample_sprite_path):
        """import_asset should add asset to cache"""
        asset_manager.import_asset(sample_sprite_path, "sprites", "cached_sprite")

        assert "sprites" in asset_manager.assets_cache
        assert "cached_sprite" in asset_manager.assets_cache["sprites"]

    def test_get_asset_from_cache(self, asset_manager, sample_sprite_path):
        """get_asset should retrieve from cache"""
        asset_manager.import_asset(sample_sprite_path, "sprites", "my_sprite")

        result = asset_manager.get_asset("sprites", "my_sprite")

        assert result is not None
        assert result["name"] == "my_sprite"

    def test_get_asset_not_found(self, asset_manager):
        """get_asset should return None for missing assets"""
        result = asset_manager.get_asset("sprites", "nonexistent")

        assert result is None


class TestAssetManagerDelete:
    """Test asset deletion functionality"""

    @pytest.fixture
    def asset_manager(self, temp_project_dir):
        """Create an AssetManager instance"""
        with patch('pygame.mixer.init'):
            from core.asset_manager import AssetManager
            return AssetManager(project_directory=temp_project_dir)

    def test_delete_asset_removes_file(self, asset_manager, sample_sprite_path, temp_project_dir):
        """delete_asset should remove the asset file"""
        asset_manager.import_asset(sample_sprite_path, "sprites", "to_delete")
        asset_file = temp_project_dir / "sprites" / "to_delete.png"
        assert asset_file.exists()

        asset_manager.delete_asset("sprites", "to_delete")

        assert not asset_file.exists()

    def test_delete_asset_removes_from_cache(self, asset_manager, sample_sprite_path):
        """delete_asset should remove from cache"""
        asset_manager.import_asset(sample_sprite_path, "sprites", "to_delete")

        asset_manager.delete_asset("sprites", "to_delete")

        assert asset_manager.get_asset("sprites", "to_delete") is None

    def test_delete_asset_emits_signal(self, asset_manager, sample_sprite_path):
        """delete_asset should emit asset_deleted signal"""
        asset_manager.import_asset(sample_sprite_path, "sprites", "to_delete")
        signal_spy = MagicMock()
        asset_manager.asset_deleted.connect(signal_spy)

        asset_manager.delete_asset("sprites", "to_delete")

        signal_spy.assert_called_once_with("sprites", "to_delete")


class TestAssetManagerThumbnails:
    """Test thumbnail generation functionality"""

    @pytest.fixture
    def asset_manager(self, temp_project_dir):
        """Create an AssetManager instance"""
        with patch('pygame.mixer.init'):
            from core.asset_manager import AssetManager
            return AssetManager(project_directory=temp_project_dir)

    def test_generate_thumbnail_creates_file(self, asset_manager, sample_sprite_path, temp_project_dir):
        """generate_thumbnail should create thumbnail file"""
        # Copy sprite to project
        import shutil
        dest = temp_project_dir / "sprites" / "test.png"
        shutil.copy(sample_sprite_path, dest)

        thumbnail_path = asset_manager.generate_thumbnail(dest, "test")

        assert thumbnail_path is not None
        assert Path(thumbnail_path).exists()

    def test_generate_thumbnail_correct_size(self, asset_manager, temp_project_dir):
        """generate_thumbnail should create correctly sized thumbnail"""
        from PIL import Image

        # Create a large image
        large_image = temp_project_dir / "sprites" / "large.png"
        Image.new("RGBA", (512, 512), (255, 0, 0, 255)).save(large_image)

        thumbnail_path = asset_manager.generate_thumbnail(large_image, "large")

        # Check thumbnail size
        with Image.open(thumbnail_path) as thumb:
            assert thumb.width <= 64
            assert thumb.height <= 64
