#!/usr/bin/env python3

import json
from pathlib import Path
from typing import Dict, List, Any, Tuple, Union
from datetime import datetime
import hashlib
import mimetypes
from PIL import Image, ImageOps
import pygame


class AssetUtils:
    """Utility class for asset-related operations"""

    # Asset type mappings
    ASSET_EXTENSIONS = {
        "sprites": [".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tga", ".webp"],
        "sounds": [".wav", ".mp3", ".ogg", ".m4a", ".aac", ".flac"],
        "backgrounds": [".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tga", ".webp"],
        "fonts": [".ttf", ".otf", ".woff", ".woff2"],
        "data": [".json", ".xml", ".txt", ".csv", ".yaml", ".yml"]
    }

    # Default thumbnail sizes
    THUMBNAIL_SIZES = {
        "small": (32, 32),
        "medium": (64, 64),
        "large": (128, 128),
        "xlarge": (256, 256)
    }

    @staticmethod
    def validate_asset_file(file_path: Union[str, Path], asset_type: str) -> Dict[str, Any]:
        """Validate an asset file and return validation results"""
        file_path = Path(file_path)
        result = {
            "valid": False,
            "errors": [],
            "warnings": [],
            "info": {},
            "file_info": {}
        }

        try:
            # Check if file exists
            if not file_path.exists():
                result["errors"].append("File does not exist")
                return result

            # Check file extension
            extension = file_path.suffix.lower()
            valid_extensions = AssetUtils.ASSET_EXTENSIONS.get(asset_type, [])

            if extension not in valid_extensions:
                result["errors"].append(f"Invalid extension '{extension}' for {asset_type}")
                return result

            # Get basic file info
            file_stat = file_path.stat()
            result["file_info"] = {
                "size": file_stat.st_size,
                "modified": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                "extension": extension,
                "mime_type": mimetypes.guess_type(str(file_path))[0]
            }

            # Asset-specific validation
            if asset_type == "sprites" or asset_type == "backgrounds":
                AssetUtils._validate_image(file_path, result)
            elif asset_type == "sounds":
                AssetUtils._validate_audio(file_path, result)
            elif asset_type == "fonts":
                AssetUtils._validate_font(file_path, result)
            elif asset_type == "data":
                AssetUtils._validate_data(file_path, result)

            # If no errors, mark as valid
            result["valid"] = len(result["errors"]) == 0

        except Exception as e:
            result["errors"].append(f"Validation error: {str(e)}")

        return result

    @staticmethod
    def _validate_image(file_path: Path, result: Dict[str, Any]):
        """Validate image file"""
        try:
            with Image.open(file_path) as img:
                width, height = img.size

                result["info"].update({
                    "width": width,
                    "height": height,
                    "format": img.format,
                    "mode": img.mode,
                    "has_transparency": "transparency" in img.info or img.mode in ("RGBA", "LA")
                })

                # Check image size constraints
                if width > 4096 or height > 4096:
                    result["warnings"].append(f"Large image dimensions: {width}x{height}")

                if width < 1 or height < 1:
                    result["errors"].append("Invalid image dimensions")

                # Check file size
                file_size = result["file_info"]["size"]
                if file_size > 50 * 1024 * 1024:  # 50MB
                    result["warnings"].append(f"Large file size: {file_size / (1024*1024):.1f}MB")

        except Exception as e:
            result["errors"].append(f"Invalid image file: {str(e)}")

    @staticmethod
    def _validate_audio(file_path: Path, result: Dict[str, Any]):
        """Validate audio file"""
        try:
            pygame.mixer.init()
            sound = pygame.mixer.Sound(str(file_path))

            length = sound.get_length()
            result["info"].update({
                "duration": length,
                "format": file_path.suffix.upper()[1:]
            })

            # Check duration constraints
            if length > 300:  # 5 minutes
                result["warnings"].append(f"Long audio duration: {length:.1f} seconds")

            if length <= 0:
                result["errors"].append("Invalid audio duration")

        except Exception as e:
            result["errors"].append(f"Invalid audio file: {str(e)}")

    @staticmethod
    def _validate_font(file_path: Path, result: Dict[str, Any]):
        """Validate font file"""
        try:
            # Basic font validation - check if file can be opened
            with open(file_path, 'rb') as f:
                header = f.read(4)

                # Check for common font file signatures
                if header in [b'\x00\x01\x00\x00', b'OTTO', b'true', b'typ1']:
                    result["info"]["format"] = "TrueType/OpenType"
                elif header == b'wOFF':
                    result["info"]["format"] = "WOFF"
                elif header == b'wOF2':
                    result["info"]["format"] = "WOFF2"
                else:
                    result["warnings"].append("Unknown font format")

        except Exception as e:
            result["errors"].append(f"Invalid font file: {str(e)}")

    @staticmethod
    def _validate_data(file_path: Path, result: Dict[str, Any]):
        """Validate data file"""
        try:
            extension = file_path.suffix.lower()

            if extension == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    json.load(f)
                result["info"]["format"] = "JSON"

            elif extension == '.xml':
                # Basic XML validation
                import xml.etree.ElementTree as ET
                ET.parse(file_path)
                result["info"]["format"] = "XML"

            elif extension in ['.yaml', '.yml']:
                try:
                    import yaml
                    with open(file_path, 'r', encoding='utf-8') as f:
                        yaml.safe_load(f)
                    result["info"]["format"] = "YAML"
                except ImportError:
                    result["warnings"].append("YAML support not available")

            elif extension == '.csv':
                import csv
                with open(file_path, 'r', encoding='utf-8') as f:
                    csv.Sniffer().sniff(f.read(1024))
                result["info"]["format"] = "CSV"

        except Exception as e:
            result["errors"].append(f"Invalid data file: {str(e)}")

    @staticmethod
    def generate_thumbnail(image_path: Union[str, Path],
                          output_path: Union[str, Path],
                          size: Tuple[int, int] = (64, 64),
                          quality: int = 85) -> bool:
        """Generate thumbnail for image"""
        try:
            image_path = Path(image_path)
            output_path = Path(output_path)

            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with Image.open(image_path) as img:
                # Handle EXIF orientation
                img = ImageOps.exif_transpose(img)

                # Convert to RGB if necessary (for JPEG output)
                if img.mode in ('RGBA', 'P', 'LA'):
                    # Create white background for transparency
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')

                # Create thumbnail
                img.thumbnail(size, Image.Resampling.LANCZOS)

                # Center the image on a square canvas
                if size[0] == size[1]:  # Square thumbnail
                    canvas = Image.new('RGB', size, (255, 255, 255))
                    x = (size[0] - img.width) // 2
                    y = (size[1] - img.height) // 2
                    canvas.paste(img, (x, y))
                    img = canvas

                # Save thumbnail
                img.save(output_path, 'JPEG', quality=quality, optimize=True)

            return True

        except Exception as e:
            print(f"Error generating thumbnail: {e}")
            return False

    @staticmethod
    def get_image_info(image_path: Union[str, Path]) -> Dict[str, Any]:
        """Get detailed information about an image"""
        info = {}

        try:
            with Image.open(image_path) as img:
                info = {
                    "width": img.width,
                    "height": img.height,
                    "format": img.format,
                    "mode": img.mode,
                    "has_transparency": "transparency" in img.info or img.mode in ("RGBA", "LA"),
                    "is_animated": getattr(img, "is_animated", False),
                    "n_frames": getattr(img, "n_frames", 1)
                }

                # Get DPI if available
                if "dpi" in img.info:
                    info["dpi"] = img.info["dpi"]

                # Calculate aspect ratio
                if info["height"] != 0:
                    info["aspect_ratio"] = info["width"] / info["height"]

        except Exception as e:
            info["error"] = str(e)

        return info

    @staticmethod
    def get_audio_info(audio_path: Union[str, Path]) -> Dict[str, Any]:
        """Get detailed information about an audio file"""
        info = {}

        try:
            pygame.mixer.init()
            sound = pygame.mixer.Sound(str(audio_path))

            info = {
                "duration": sound.get_length(),
                "format": Path(audio_path).suffix.upper()[1:],
                "file_size": Path(audio_path).stat().st_size
            }

            # Try to get more detailed info using other libraries if available
            try:
                import mutagen
                file_info = mutagen.File(str(audio_path))
                if file_info is not None:
                    if hasattr(file_info, 'info'):
                        audio_info = file_info.info
                        if hasattr(audio_info, 'bitrate'):
                            info["bitrate"] = audio_info.bitrate
                        if hasattr(audio_info, 'sample_rate'):
                            info["sample_rate"] = audio_info.sample_rate
                        if hasattr(audio_info, 'channels'):
                            info["channels"] = audio_info.channels
            except ImportError:
                pass  # mutagen not available

        except Exception as e:
            info["error"] = str(e)

        return info

    @staticmethod
    def optimize_image(image_path: Union[str, Path],
                      output_path: Union[str, Path] = None,
                      max_width: int = None,
                      max_height: int = None,
                      quality: int = 85,
                      format: str = None) -> bool:
        """Optimize image file"""
        try:
            image_path = Path(image_path)
            if output_path is None:
                output_path = image_path
            else:
                output_path = Path(output_path)

            with Image.open(image_path) as img:
                # Handle EXIF orientation
                img = ImageOps.exif_transpose(img)

                # Resize if dimensions specified
                if max_width or max_height:
                    if max_width and max_height:
                        img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                    elif max_width:
                        if img.width > max_width:
                            ratio = max_width / img.width
                            new_height = int(img.height * ratio)
                            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
                    elif max_height:
                        if img.height > max_height:
                            ratio = max_height / img.height
                            new_width = int(img.width * ratio)
                            img = img.resize((new_width, max_height), Image.Resampling.LANCZOS)

                # Determine output format
                if format is None:
                    format = img.format or "PNG"

                # Save optimized image
                save_kwargs = {"optimize": True}

                if format.upper() == "JPEG":
                    if img.mode in ('RGBA', 'LA', 'P'):
                        # Convert to RGB for JPEG
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                        img = background
                    save_kwargs["quality"] = quality
                elif format.upper() == "PNG":
                    save_kwargs["compress_level"] = 6

                img.save(output_path, format, **save_kwargs)

            return True

        except Exception as e:
            print(f"Error optimizing image: {e}")
            return False

    @staticmethod
    def create_sprite_sheet(images: List[Union[str, Path]],
                           output_path: Union[str, Path],
                           columns: int = None,
                           padding: int = 0,
                           background_color: Tuple[int, int, int, int] = (0, 0, 0, 0)) -> Dict[str, Any]:
        """Create sprite sheet from multiple images"""
        try:
            if not images:
                return {"success": False, "error": "No images provided"}

            # Load all images
            loaded_images = []
            max_width = 0
            max_height = 0

            for image_path in images:
                try:
                    img = Image.open(image_path)
                    loaded_images.append(img)
                    max_width = max(max_width, img.width)
                    max_height = max(max_height, img.height)
                except Exception as e:
                    print(f"Error loading image {image_path}: {e}")
                    continue

            if not loaded_images:
                return {"success": False, "error": "No valid images loaded"}

            # Calculate grid dimensions
            total_images = len(loaded_images)
            if columns is None:
                columns = int(total_images ** 0.5) or 1

            rows = (total_images + columns - 1) // columns

            # Calculate sprite sheet dimensions
            sheet_width = columns * (max_width + padding) - padding
            sheet_height = rows * (max_height + padding) - padding

            # Create sprite sheet
            sprite_sheet = Image.new('RGBA', (sheet_width, sheet_height), background_color)

            # Place images on sprite sheet
            frame_info = []
            for i, img in enumerate(loaded_images):
                row = i // columns
                col = i % columns

                x = col * (max_width + padding)
                y = row * (max_height + padding)

                sprite_sheet.paste(img, (x, y))

                frame_info.append({
                    "index": i,
                    "x": x,
                    "y": y,
                    "width": img.width,
                    "height": img.height
                })

            # Save sprite sheet
            sprite_sheet.save(output_path, "PNG")

            # Clean up
            for img in loaded_images:
                img.close()

            return {
                "success": True,
                "width": sheet_width,
                "height": sheet_height,
                "columns": columns,
                "rows": rows,
                "frame_count": total_images,
                "frame_info": frame_info
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def extract_sprite_frames(sprite_sheet_path: Union[str, Path],
                             frame_width: int, frame_height: int,
                             output_dir: Union[str, Path],
                             columns: int = None, rows: int = None) -> List[Path]:
        """Extract individual frames from a sprite sheet"""
        try:
            sprite_sheet = Image.open(sprite_sheet_path)
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

            sheet_width, sheet_height = sprite_sheet.size

            # Calculate grid dimensions if not provided
            if columns is None:
                columns = sheet_width // frame_width
            if rows is None:
                rows = sheet_height // frame_height

            extracted_frames = []
            frame_index = 0

            for row in range(rows):
                for col in range(columns):
                    x = col * frame_width
                    y = row * frame_height

                    # Check if frame is within bounds
                    if x + frame_width <= sheet_width and y + frame_height <= sheet_height:
                        # Extract frame
                        frame = sprite_sheet.crop((x, y, x + frame_width, y + frame_height))

                        # Save frame
                        frame_path = output_dir / f"frame_{frame_index:03d}.png"
                        frame.save(frame_path, "PNG")

                        extracted_frames.append(frame_path)
                        frame_index += 1

            sprite_sheet.close()
            return extracted_frames

        except Exception as e:
            print(f"Error extracting sprite frames: {e}")
            return []

    @staticmethod
    def get_asset_dependencies(asset_data: Dict[str, Any]) -> List[str]:
        """Get list of asset dependencies"""
        dependencies = []

        asset_type = asset_data.get("asset_type", "")

        if asset_type == "objects":
            # Objects can depend on sprites
            if "sprite" in asset_data and asset_data["sprite"]:
                dependencies.append(asset_data["sprite"])

        elif asset_type == "rooms":
            # Rooms can depend on backgrounds and contain object instances
            if "background" in asset_data and asset_data["background"]:
                dependencies.append(asset_data["background"])

            # Check instances
            instances = asset_data.get("instances", [])
            for instance in instances:
                if "object" in instance:
                    dependencies.append(instance["object"])

        return dependencies

    @staticmethod
    def validate_asset_references(project_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate all asset references in project"""
        issues = []
        assets = project_data.get("assets", {})

        # Create set of all available assets
        available_assets = set()
        for asset_type, asset_list in assets.items():
            for asset_name in asset_list.keys():
                available_assets.add(asset_name)

        # Check each asset's dependencies
        for asset_type, asset_list in assets.items():
            for asset_name, asset_data in asset_list.items():
                dependencies = AssetUtils.get_asset_dependencies(asset_data)

                for dependency in dependencies:
                    if dependency and dependency not in available_assets:
                        issues.append({
                            "type": "missing_reference",
                            "asset": asset_name,
                            "asset_type": asset_type,
                            "missing_reference": dependency,
                            "message": f"Asset '{asset_name}' references missing asset '{dependency}'"
                        })

        return issues

    @staticmethod
    def calculate_asset_hash(file_path: Union[str, Path]) -> str:
        """Calculate hash of asset file for change detection"""
        try:
            hasher = hashlib.md5()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception:
            return ""

    @staticmethod
    def create_asset_metadata(file_path: Union[str, Path], asset_type: str) -> Dict[str, Any]:
        """Create complete metadata for an asset"""
        file_path = Path(file_path)

        metadata = {
            "name": file_path.stem,
            "asset_type": asset_type,
            "file_path": str(file_path),
            "file_size": file_path.stat().st_size if file_path.exists() else 0,
            "file_hash": AssetUtils.calculate_asset_hash(file_path),
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
            "imported": True
        }

        # Add type-specific metadata
        if asset_type in ["sprites", "backgrounds"]:
            image_info = AssetUtils.get_image_info(file_path)
            metadata.update(image_info)

            # Set default origin for sprites
            if asset_type == "sprites":
                metadata.update({
                    "origin_x": image_info.get("width", 32) // 2,
                    "origin_y": image_info.get("height", 32) // 2,
                    "frames": image_info.get("n_frames", 1),
                    "speed": 1.0
                })

        elif asset_type == "sounds":
            audio_info = AssetUtils.get_audio_info(file_path)
            metadata.update(audio_info)
            metadata.update({
                "volume": 1.0,
                "loop": False
            })

        elif asset_type == "fonts":
            metadata.update({
                "font_name": file_path.stem,
                "size": 12,
                "bold": False,
                "italic": False,
                "charset": "ascii"
            })

        return metadata

    @staticmethod
    def convert_audio_format(input_path: Union[str, Path],
                           output_path: Union[str, Path],
                           output_format: str = "wav",
                           quality: int = 44100) -> bool:
        """Convert audio file to different format"""
        try:
            # This would require additional audio libraries like pydub
            # For now, return False to indicate conversion not available
            print(f"Audio conversion not implemented: {input_path} -> {output_path}")
            return False
        except Exception as e:
            print(f"Error converting audio: {e}")
            return False

    @staticmethod
    def is_supported_asset(file_path: Union[str, Path], asset_type: str) -> bool:
        """Check if file is supported for the given asset type"""
        extension = Path(file_path).suffix.lower()
        supported_extensions = AssetUtils.ASSET_EXTENSIONS.get(asset_type, [])
        return extension in supported_extensions

    @staticmethod
    def get_supported_formats(asset_type: str) -> List[str]:
        """Get list of supported formats for asset type"""
        return AssetUtils.ASSET_EXTENSIONS.get(asset_type, []).copy()

    @staticmethod
    def clean_asset_cache(cache_dir: Union[str, Path], max_age_days: int = 30) -> int:
        """Clean old cached assets"""
        cache_dir = Path(cache_dir)
        if not cache_dir.exists():
            return 0

        removed_count = 0
        cutoff_time = datetime.now().timestamp() - (max_age_days * 24 * 60 * 60)

        try:
            for cache_file in cache_dir.rglob('*'):
                if cache_file.is_file():
                    if cache_file.stat().st_mtime < cutoff_time:
                        cache_file.unlink()
                        removed_count += 1
        except Exception as e:
            print(f"Error cleaning cache: {e}")

        return removed_count


# Convenience functions
def validate_asset(file_path: Union[str, Path], asset_type: str) -> Dict[str, Any]:
    """Validate an asset file"""
    return AssetUtils.validate_asset_file(file_path, asset_type)

def generate_thumbnail(image_path: Union[str, Path], output_path: Union[str, Path],
                      size: Tuple[int, int] = (64, 64)) -> bool:
    """Generate thumbnail for image"""
    return AssetUtils.generate_thumbnail(image_path, output_path, size)

def get_image_info(image_path: Union[str, Path]) -> Dict[str, Any]:
    """Get image information"""
    return AssetUtils.get_image_info(image_path)

def get_audio_info(audio_path: Union[str, Path]) -> Dict[str, Any]:
    """Get audio information"""
    return AssetUtils.get_audio_info(audio_path)

def create_asset_metadata(file_path: Union[str, Path], asset_type: str) -> Dict[str, Any]:
    """Create asset metadata"""
    return AssetUtils.create_asset_metadata(file_path, asset_type)

def is_supported_asset(file_path: Union[str, Path], asset_type: str) -> bool:
    """Check if asset is supported"""
    return AssetUtils.is_supported_asset(file_path, asset_type)
