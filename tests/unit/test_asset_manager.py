#!/usr/bin/env python3
"""
Unit tests for AssetManager
Tests asset import, export, deletion, and management
"""

import pytest
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
from PIL import Image
from pythongm.core.asset_manager import AssetManager


class TestAssetManagerInitialization:
    """Test AssetManager initialization"""

    def test_asset_manager_creates_with_directory(self, project_dir):
        """Test that AssetManager can be created with a project directory"""
        am = AssetManager(project_directory=project_dir)

        assert am.project_directory == project_dir

    def test_asset_manager_creates_without_directory(self):
        """Test that AssetManager can be created without a project directory"""
        am = AssetManager(project_directory=None)

        assert am.project_directory is not None  # Should default to cwd

    def test_asset_manager_initializes_caches(self, asset_manager):
        """Test that AssetManager initializes cache dictionaries"""
        assert isinstance(asset_manager.assets_cache, dict)
        assert isinstance(asset_manager.thumbnails_cache, dict)

    def test_asset_manager_creates_directories(self, project_dir):
        """Test that AssetManager creates asset directories"""
        am = AssetManager(project_directory=project_dir)

        expected_dirs = ["sprites", "sounds", "backgrounds", "objects",
                        "rooms", "scripts", "fonts", "data", "thumbnails"]

        for dirname in expected_dirs:
            dir_path = project_dir / dirname
            assert dir_path.exists(), f"Directory {dirname} was not created"


class TestAssetImport:
    """Test asset import functionality"""

    def test_import_sprite_creates_copy(self, asset_manager, sample_sprite_file, project_dir):
        """Test that importing a sprite creates a copy in the project"""
        result = asset_manager.import_asset(
            sample_sprite_file, "sprites", "test_sprite"
        )

        assert result is not None
        sprite_path = project_dir / "sprites" / "test_sprite.png"
        assert sprite_path.exists()

    def test_import_sprite_returns_asset_data(self, asset_manager, sample_sprite_file):
        """Test that import_asset returns asset data dictionary"""
        result = asset_manager.import_asset(
            sample_sprite_file, "sprites", "test_sprite"
        )

        assert isinstance(result, dict)
        assert "name" in result
        assert "path" in result

    def test_import_sprite_emits_signal(self, asset_manager, sample_sprite_file, qtbot):
        """Test that import_asset emits asset_imported signal"""
        with qtbot.waitSignal(asset_manager.asset_imported, timeout=1000):
            asset_manager.import_asset(
                sample_sprite_file, "sprites", "test_sprite"
            )

    def test_import_sound_creates_copy(self, asset_manager, sample_sound_file, project_dir):
        """Test that importing a sound creates a copy in the project"""
        result = asset_manager.import_asset(
            sample_sound_file, "sounds", "test_sound"
        )

        assert result is not None
        sound_path = project_dir / "sounds" / "test_sound.wav"
        assert sound_path.exists()

    def test_import_unsupported_format_fails(self, asset_manager, temp_dir):
        """Test that importing an unsupported format fails gracefully"""
        # Create a .txt file and try to import as sprite
        txt_file = temp_dir / "test.txt"
        txt_file.write_text("not an image")

        result = asset_manager.import_asset(txt_file, "sprites", "test")

        assert result is None

    def test_import_nonexistent_file_fails(self, asset_manager, temp_dir):
        """Test that importing a nonexistent file fails gracefully"""
        nonexistent = temp_dir / "does_not_exist.png"

        result = asset_manager.import_asset(nonexistent, "sprites", "test")

        assert result is None

    def test_import_generates_name_if_not_provided(self, asset_manager, sample_sprite_file):
        """Test that import_asset generates a name if not provided"""
        result = asset_manager.import_asset(sample_sprite_file, "sprites")

        assert result is not None
        assert "name" in result
        assert result["name"] != ""

    def test_import_preserves_file_extension(self, asset_manager, sample_sprite_file, project_dir):
        """Test that import preserves the original file extension"""
        asset_manager.import_asset(sample_sprite_file, "sprites", "test_sprite")

        sprite_path = project_dir / "sprites" / "test_sprite.png"
        assert sprite_path.exists()
        assert sprite_path.suffix == ".png"


class TestAssetDeletion:
    """Test asset deletion functionality"""

    def test_delete_asset_removes_file(self, asset_manager, sample_sprite_file, project_dir):
        """Test that delete_asset removes the file from disk"""
        asset_manager.import_asset(sample_sprite_file, "sprites", "test_sprite")

        result = asset_manager.delete_asset("sprites", "test_sprite")

        assert result is True
        sprite_path = project_dir / "sprites" / "test_sprite.png"
        assert not sprite_path.exists()

    def test_delete_asset_emits_signal(self, asset_manager, sample_sprite_file, qtbot):
        """Test that delete_asset emits asset_deleted signal"""
        asset_manager.import_asset(sample_sprite_file, "sprites", "test_sprite")

        with qtbot.waitSignal(asset_manager.asset_deleted, timeout=1000):
            asset_manager.delete_asset("sprites", "test_sprite")

    def test_delete_nonexistent_asset_fails(self, asset_manager):
        """Test that deleting a nonexistent asset fails gracefully"""
        result = asset_manager.delete_asset("sprites", "does_not_exist")

        assert result is False

    def test_delete_asset_removes_thumbnail(self, asset_manager, sample_sprite_file, project_dir):
        """Test that delete_asset also removes the thumbnail"""
        asset_manager.import_asset(sample_sprite_file, "sprites", "test_sprite")

        # Generate thumbnail
        asset_manager.generate_thumbnail(
            project_dir / "sprites" / "test_sprite.png",
            "test_sprite"
        )

        asset_manager.delete_asset("sprites", "test_sprite")

        thumbnail_path = project_dir / "thumbnails" / "test_sprite.png"
        assert not thumbnail_path.exists()


class TestAssetRenaming:
    """Test asset renaming functionality"""

    def test_rename_asset_changes_filename(self, asset_manager, sample_sprite_file, project_dir):
        """Test that rename_asset changes the file name"""
        asset_manager.import_asset(sample_sprite_file, "sprites", "old_name")

        result = asset_manager.rename_asset("sprites", "old_name", "new_name")

        assert result is True
        old_path = project_dir / "sprites" / "old_name.png"
        new_path = project_dir / "sprites" / "new_name.png"
        assert not old_path.exists()
        assert new_path.exists()

    def test_rename_asset_updates_cache(self, asset_manager, sample_sprite_file):
        """Test that rename_asset updates the asset cache"""
        asset_manager.import_asset(sample_sprite_file, "sprites", "old_name")

        asset_manager.rename_asset("sprites", "old_name", "new_name")

        # Old name should not be in cache
        old_cache_key = "sprites/old_name"
        new_cache_key = "sprites/new_name"

        assert old_cache_key not in asset_manager.assets_cache
        assert new_cache_key in asset_manager.assets_cache

    def test_rename_nonexistent_asset_fails(self, asset_manager):
        """Test that renaming a nonexistent asset fails"""
        result = asset_manager.rename_asset("sprites", "does_not_exist", "new_name")

        assert result is False

    def test_rename_to_existing_name_fails(self, asset_manager, sample_sprite_file):
        """Test that renaming to an existing name fails"""
        # Import two assets
        asset_manager.import_asset(sample_sprite_file, "sprites", "sprite1")

        # Create a second sprite file
        sprite2_path = sample_sprite_file.parent / "sprite2.png"
        shutil.copy(sample_sprite_file, sprite2_path)
        asset_manager.import_asset(sprite2_path, "sprites", "sprite2")

        # Try to rename sprite1 to sprite2 (should fail)
        result = asset_manager.rename_asset("sprites", "sprite1", "sprite2")

        assert result is False


class TestAssetDuplication:
    """Test asset duplication functionality"""

    def test_duplicate_asset_creates_copy(self, asset_manager, sample_sprite_file, project_dir):
        """Test that duplicate_asset creates a copy of the asset"""
        asset_manager.import_asset(sample_sprite_file, "sprites", "original")

        result = asset_manager.duplicate_asset("sprites", "original")

        assert result is not None
        # Should create a file with a different name (e.g., original_copy or original_1)
        assert len(list((project_dir / "sprites").glob("*.png"))) == 2

    def test_duplicate_asset_returns_new_name(self, asset_manager, sample_sprite_file):
        """Test that duplicate_asset returns the new asset name"""
        asset_manager.import_asset(sample_sprite_file, "sprites", "original")

        result = asset_manager.duplicate_asset("sprites", "original")

        assert result is not None
        assert isinstance(result, (str, dict))

    def test_duplicate_nonexistent_asset_fails(self, asset_manager):
        """Test that duplicating a nonexistent asset fails"""
        result = asset_manager.duplicate_asset("sprites", "does_not_exist")

        assert result is None


class TestThumbnailGeneration:
    """Test thumbnail generation functionality"""

    def test_generate_thumbnail_creates_file(self, asset_manager, sample_sprite_file, project_dir):
        """Test that generate_thumbnail creates a thumbnail file"""
        asset_manager.import_asset(sample_sprite_file, "sprites", "test_sprite")

        sprite_path = project_dir / "sprites" / "test_sprite.png"
        result = asset_manager.generate_thumbnail(sprite_path, "test_sprite")

        assert result is not None
        thumbnail_path = project_dir / "thumbnails" / "test_sprite.png"
        assert thumbnail_path.exists()

    def test_thumbnail_is_correct_size(self, asset_manager, sample_sprite_file, project_dir):
        """Test that generated thumbnail is the correct size"""
        asset_manager.import_asset(sample_sprite_file, "sprites", "test_sprite")

        sprite_path = project_dir / "sprites" / "test_sprite.png"
        asset_manager.generate_thumbnail(sprite_path, "test_sprite")

        thumbnail_path = project_dir / "thumbnails" / "test_sprite.png"
        with Image.open(thumbnail_path) as img:
            # Should be <= THUMBNAIL_SIZE in both dimensions
            assert img.width <= AssetManager.THUMBNAIL_SIZE[0]
            assert img.height <= AssetManager.THUMBNAIL_SIZE[1]

    def test_generate_thumbnail_handles_large_images(self, asset_manager, temp_dir, project_dir):
        """Test that thumbnail generation handles large images"""
        # Create a large image
        large_image_path = temp_dir / "large.png"
        large_img = Image.new('RGB', (2000, 2000), color='blue')
        large_img.save(large_image_path)

        asset_manager.import_asset(large_image_path, "sprites", "large_sprite")

        sprite_path = project_dir / "sprites" / "large_sprite.png"
        result = asset_manager.generate_thumbnail(sprite_path, "large_sprite")

        assert result is not None

        thumbnail_path = project_dir / "thumbnails" / "large_sprite.png"
        with Image.open(thumbnail_path) as img:
            assert img.width <= AssetManager.THUMBNAIL_SIZE[0]
            assert img.height <= AssetManager.THUMBNAIL_SIZE[1]


class TestPathConversion:
    """Test path conversion utilities"""

    def test_get_absolute_path(self, asset_manager, project_dir):
        """Test converting relative path to absolute"""
        relative_path = "sprites/test.png"

        absolute_path = asset_manager.get_absolute_path(relative_path)

        expected = project_dir / "sprites" / "test.png"
        assert absolute_path == expected

    def test_get_relative_path(self, asset_manager, project_dir):
        """Test converting absolute path to relative"""
        absolute_path = project_dir / "sprites" / "test.png"

        relative_path = asset_manager.get_relative_path(absolute_path)

        expected = "sprites/test.png"
        # Normalize path separators for cross-platform compatibility
        assert Path(relative_path) == Path(expected)

    def test_get_relative_path_outside_project(self, asset_manager, temp_dir):
        """Test getting relative path for file outside project"""
        outside_path = temp_dir / "outside.png"

        relative_path = asset_manager.get_relative_path(outside_path)

        # Should return the path as-is if not relative to project
        assert relative_path is not None


class TestAssetValidation:
    """Test asset validation functionality"""

    def test_is_supported_format_for_sprites(self, asset_manager):
        """Test format validation for sprites"""
        assert asset_manager.is_supported_format(Path("test.png"), "sprites")
        assert asset_manager.is_supported_format(Path("test.jpg"), "sprites")
        assert not asset_manager.is_supported_format(Path("test.txt"), "sprites")

    def test_is_supported_format_for_sounds(self, asset_manager):
        """Test format validation for sounds"""
        assert asset_manager.is_supported_format(Path("test.wav"), "sounds")
        assert asset_manager.is_supported_format(Path("test.mp3"), "sounds")
        assert not asset_manager.is_supported_format(Path("test.png"), "sounds")

    def test_get_supported_formats(self, asset_manager):
        """Test getting list of supported formats"""
        sprite_formats = asset_manager.get_supported_formats("sprites")

        assert isinstance(sprite_formats, list)
        assert ".png" in sprite_formats
        assert ".jpg" in sprite_formats


class TestAssetCache:
    """Test asset caching functionality"""

    def test_import_adds_to_cache(self, asset_manager, sample_sprite_file):
        """Test that importing an asset adds it to the cache"""
        asset_manager.import_asset(sample_sprite_file, "sprites", "test_sprite")

        cache_key = "sprites/test_sprite"
        assert cache_key in asset_manager.assets_cache

    def test_delete_removes_from_cache(self, asset_manager, sample_sprite_file):
        """Test that deleting an asset removes it from the cache"""
        asset_manager.import_asset(sample_sprite_file, "sprites", "test_sprite")

        asset_manager.delete_asset("sprites", "test_sprite")

        cache_key = "sprites/test_sprite"
        assert cache_key not in asset_manager.assets_cache

    def test_set_project_directory_clears_cache(self, asset_manager, sample_sprite_file, temp_dir):
        """Test that changing project directory clears the cache"""
        asset_manager.import_asset(sample_sprite_file, "sprites", "test_sprite")

        assert len(asset_manager.assets_cache) > 0

        # Create a new project directory
        new_project_dir = temp_dir / "new_project"
        new_project_dir.mkdir()

        asset_manager.set_project_directory(new_project_dir)

        assert len(asset_manager.assets_cache) == 0
        assert len(asset_manager.thumbnails_cache) == 0


# ============================================================================
# Parametrized Tests
# ============================================================================

@pytest.mark.parametrize("asset_type,formats", [
    ("sprites", [".png", ".jpg", ".jpeg", ".bmp"]),
    ("sounds", [".wav", ".mp3", ".ogg"]),
    ("backgrounds", [".png", ".jpg", ".jpeg"]),
    ("fonts", [".ttf", ".otf"]),
    ("data", [".json", ".xml", ".txt", ".csv"])
])
def test_supported_formats_for_each_type(asset_manager, asset_type, formats):
    """Test that each asset type has the expected supported formats"""
    supported = asset_manager.get_supported_formats(asset_type)

    for fmt in formats:
        assert fmt in supported, f"Format {fmt} not supported for {asset_type}"


@pytest.mark.parametrize("image_format", ["png", "jpg", "bmp"])
def test_import_different_image_formats(asset_manager, temp_dir, project_dir, image_format):
    """Test importing images in different formats"""
    # Create test image in the specified format
    image_path = temp_dir / f"test.{image_format}"
    img = Image.new('RGB', (50, 50), color='green')

    if image_format == "jpg":
        img.save(image_path, "JPEG")
    else:
        img.save(image_path)

    result = asset_manager.import_asset(image_path, "sprites", f"test_{image_format}")

    assert result is not None
    imported_path = project_dir / "sprites" / f"test_{image_format}.{image_format}"
    assert imported_path.exists()
