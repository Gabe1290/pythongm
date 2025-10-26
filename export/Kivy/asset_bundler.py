#!/usr/bin/env python3
"""
Asset Bundler for PyGameMaker Kivy Export
Handles copying and optimizing game assets for mobile deployment
"""

import os
import json
import logging
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logging.warning("PIL/Pillow not available - image optimization will be skipped")

logger = logging.getLogger(__name__)


class AssetBundler:
    """
    Bundles game assets (sprites, sounds, backgrounds) for Kivy export.
    Handles copying, organizing, and optionally optimizing assets.
    """
    
    def __init__(self, project_path: Path, output_path: Path):
        """
        Initialize the asset bundler.
        
        Args:
            project_path: Path to the source project directory
            output_path: Path to the export output directory
        """
        self.project_path = project_path
        self.output_path = output_path
        
        # Asset directories
        self.assets_output = output_path / "assets"
        self.sprites_output = self.assets_output / "sprites"
        self.sounds_output = self.assets_output / "sounds"
        self.backgrounds_output = self.assets_output / "backgrounds"
        
        # Track bundled assets
        self.bundled_assets = {
            'sprites': [],
            'sounds': [],
            'backgrounds': []
        }
        
        logger.info("Asset bundler initialized")
    
    def bundle_assets(self, project_data: Dict[str, Any]) -> bool:
        """
        Bundle all project assets.
        
        Args:
            project_data: Complete project data dictionary
            
        Returns:
            bool: True if bundling successful (with or without warnings)
        """
        try:
            logger.info("="*60)
            logger.info("Starting asset bundling...")
            logger.info("="*60)
            
            # Extract asset data
            sprites = project_data.get("sprites", {})
            sounds = project_data.get("sounds", {})
            backgrounds = project_data.get("backgrounds", {})
            
            # Bundle each asset type
            success = True
            
            if sprites:
                logger.info(f"Bundling {len(sprites)} sprites...")
                if not self._copy_sprites(sprites):
                    logger.warning("Some sprites failed to bundle")
                    success = False
            else:
                logger.info("No sprites to bundle")
            
            if sounds:
                logger.info(f"Bundling {len(sounds)} sounds...")
                if not self._copy_sounds(sounds):
                    logger.warning("Some sounds failed to bundle")
                    success = False
            else:
                logger.info("No sounds to bundle")
            
            if backgrounds:
                logger.info(f"Bundling {len(backgrounds)} backgrounds...")
                if not self._copy_backgrounds(backgrounds):
                    logger.warning("Some backgrounds failed to bundle")
                    success = False
            else:
                logger.info("No backgrounds to bundle")
            
            # Create asset manifest
            self._create_asset_manifest()
            
            logger.info("="*60)
            logger.info("Asset bundling completed")
            logger.info(f"Total sprites: {len(self.bundled_assets['sprites'])}")
            logger.info(f"Total sounds: {len(self.bundled_assets['sounds'])}")
            logger.info(f"Total backgrounds: {len(self.bundled_assets['backgrounds'])}")
            logger.info("="*60)
            
            return success
            
        except Exception as e:
            logger.error(f"Asset bundling failed: {e}", exc_info=True)
            return False
    
    def _copy_sprites(self, sprites: Dict[str, Any]) -> bool:
        """
        Copy sprite assets to the output directory.
        
        Args:
            sprites: Dictionary of sprite data
            
        Returns:
            bool: True if all sprites copied successfully
        """
        all_success = True
        
        for sprite_name, sprite_data in sprites.items():
            try:
                logger.debug(f"Processing sprite: {sprite_name}")
                
                # Create sprite directory
                sprite_dir = self.sprites_output / sprite_name
                sprite_dir.mkdir(parents=True, exist_ok=True)
                
                # Get frames
                frames = sprite_data.get("frames", [])
                if not frames:
                    logger.warning(f"Sprite {sprite_name} has no frames")
                    continue
                
                # Copy each frame
                for frame_idx, frame in enumerate(frames):
                    frame_image = frame.get("image", "")
                    if not frame_image:
                        logger.warning(f"Frame {frame_idx} of sprite {sprite_name} has no image")
                        continue
                    
                    # Construct source path
                    source_path = self.project_path / frame_image
                    
                    if not source_path.exists():
                        logger.error(f"Source sprite file not found: {source_path}")
                        all_success = False
                        continue
                    
                    # Construct destination path
                    dest_filename = f"frame_{frame_idx}{source_path.suffix}"
                    dest_path = sprite_dir / dest_filename
                    
                    # Copy or optimize the image
                    if PIL_AVAILABLE and self._should_optimize_image(source_path):
                        if self._optimize_image(source_path, dest_path):
                            logger.debug(f"Optimized and copied: {dest_filename}")
                        else:
                            # Fall back to regular copy if optimization fails
                            shutil.copy2(source_path, dest_path)
                            logger.debug(f"Copied (optimization failed): {dest_filename}")
                    else:
                        shutil.copy2(source_path, dest_path)
                        logger.debug(f"Copied: {dest_filename}")
                    
                    # Track bundled asset
                    self.bundled_assets['sprites'].append({
                        'name': sprite_name,
                        'frame': frame_idx,
                        'path': str(dest_path.relative_to(self.output_path))
                    })
                
                logger.debug(f"Successfully bundled sprite: {sprite_name} ({len(frames)} frames)")
                
            except Exception as e:
                logger.error(f"Failed to bundle sprite {sprite_name}: {e}", exc_info=True)
                all_success = False
        
        return all_success
    
    def _copy_sounds(self, sounds: Dict[str, Any]) -> bool:
        """
        Copy sound assets to the output directory.
        
        Args:
            sounds: Dictionary of sound data
            
        Returns:
            bool: True if all sounds copied successfully
        """
        all_success = True
        
        for sound_name, sound_data in sounds.items():
            try:
                logger.debug(f"Processing sound: {sound_name}")
                
                # Get sound file path
                sound_file = sound_data.get("file", "")
                if not sound_file:
                    logger.warning(f"Sound {sound_name} has no file")
                    continue
                
                # Construct source path
                source_path = self.project_path / sound_file
                
                if not source_path.exists():
                    logger.error(f"Source sound file not found: {source_path}")
                    all_success = False
                    continue
                
                # Construct destination path
                dest_path = self.sounds_output / source_path.name
                
                # Copy the sound file
                shutil.copy2(source_path, dest_path)
                logger.debug(f"Copied sound: {sound_name}")
                
                # Track bundled asset
                self.bundled_assets['sounds'].append({
                    'name': sound_name,
                    'path': str(dest_path.relative_to(self.output_path)),
                    'format': source_path.suffix[1:].lower()
                })
                
            except Exception as e:
                logger.error(f"Failed to bundle sound {sound_name}: {e}", exc_info=True)
                all_success = False
        
        return all_success
    
    def _copy_backgrounds(self, backgrounds: Dict[str, Any]) -> bool:
        """
        Copy background assets to the output directory.
        
        Args:
            backgrounds: Dictionary of background data
            
        Returns:
            bool: True if all backgrounds copied successfully
        """
        all_success = True
        
        for bg_name, bg_data in backgrounds.items():
            try:
                logger.debug(f"Processing background: {bg_name}")
                
                # Get background image path
                bg_image = bg_data.get("image", "")
                if not bg_image:
                    logger.warning(f"Background {bg_name} has no image")
                    continue
                
                # Construct source path
                source_path = self.project_path / bg_image
                
                if not source_path.exists():
                    logger.error(f"Source background file not found: {source_path}")
                    all_success = False
                    continue
                
                # Construct destination path
                dest_path = self.backgrounds_output / source_path.name
                
                # Copy or optimize the image
                if PIL_AVAILABLE and self._should_optimize_image(source_path):
                    if self._optimize_image(source_path, dest_path):
                        logger.debug(f"Optimized and copied background: {bg_name}")
                    else:
                        # Fall back to regular copy if optimization fails
                        shutil.copy2(source_path, dest_path)
                        logger.debug(f"Copied background (optimization failed): {bg_name}")
                else:
                    shutil.copy2(source_path, dest_path)
                    logger.debug(f"Copied background: {bg_name}")
                
                # Track bundled asset
                self.bundled_assets['backgrounds'].append({
                    'name': bg_name,
                    'path': str(dest_path.relative_to(self.output_path))
                })
                
            except Exception as e:
                logger.error(f"Failed to bundle background {bg_name}: {e}", exc_info=True)
                all_success = False
        
        return all_success
    
    def _should_optimize_image(self, image_path: Path) -> bool:
        """
        Determine if an image should be optimized.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            bool: True if image should be optimized
        """
        # Only optimize images larger than 512KB
        try:
            file_size = image_path.stat().st_size
            return file_size > 512 * 1024  # 512KB threshold
        except Exception:
            return False
    
    def _optimize_image(self, source_path: Path, dest_path: Path) -> bool:
        """
        Optimize an image for mobile deployment.
        Reduces file size while maintaining acceptable quality.
        
        Args:
            source_path: Path to source image
            dest_path: Path to save optimized image
            
        Returns:
            bool: True if optimization successful
        """
        if not PIL_AVAILABLE:
            return False
        
        try:
            # Open image
            img = Image.open(source_path)
            
            # Convert RGBA to RGB if saving as JPEG
            if dest_path.suffix.lower() in ['.jpg', '.jpeg']:
                if img.mode == 'RGBA':
                    # Create white background
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[3])  # Use alpha channel as mask
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
            
            # Resize if image is very large (max 2048 pixels on longest side)
            max_size = 2048
            if max(img.size) > max_size:
                ratio = max_size / max(img.size)
                new_size = tuple(int(dim * ratio) for dim in img.size)
                img = img.resize(new_size, Image.Resampling.LANCZOS)
                logger.debug(f"Resized image from {source_path.stat().st_size} to fit {max_size}px")
            
            # Save with optimization
            save_kwargs = {}
            if dest_path.suffix.lower() in ['.jpg', '.jpeg']:
                save_kwargs['quality'] = 85
                save_kwargs['optimize'] = True
            elif dest_path.suffix.lower() == '.png':
                save_kwargs['optimize'] = True
            
            img.save(dest_path, **save_kwargs)
            
            # Log size reduction
            original_size = source_path.stat().st_size
            optimized_size = dest_path.stat().st_size
            reduction = ((original_size - optimized_size) / original_size) * 100
            
            if reduction > 5:  # Only log if significant reduction
                logger.debug(f"Optimized {source_path.name}: {original_size/1024:.1f}KB → {optimized_size/1024:.1f}KB ({reduction:.1f}% reduction)")
            
            return True
            
        except Exception as e:
            logger.warning(f"Failed to optimize image {source_path}: {e}")
            return False
    
    def _create_asset_manifest(self):
        """Create a JSON manifest of all bundled assets."""
        try:
            manifest_path = self.assets_output / "manifest.json"
            
            manifest_data = {
                'version': '1.0',
                'sprites': self.bundled_assets['sprites'],
                'sounds': self.bundled_assets['sounds'],
                'backgrounds': self.bundled_assets['backgrounds'],
                'counts': {
                    'sprites': len(self.bundled_assets['sprites']),
                    'sounds': len(self.bundled_assets['sounds']),
                    'backgrounds': len(self.bundled_assets['backgrounds'])
                }
            }
            
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest_data, f, indent=2)
            
            logger.info(f"Created asset manifest: {manifest_path}")
            
        except Exception as e:
            logger.error(f"Failed to create asset manifest: {e}", exc_info=True)


# Export the main class
__all__ = ['AssetBundler']
