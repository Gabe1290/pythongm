#!/usr/bin/env python3
"""
Project Compression Utilities
Handles zipping and unzipping PyGameMaker projects
Supports working directly with zip files
"""

import zipfile
import json
from pathlib import Path
import shutil
import tempfile
from typing import Dict, Any, Optional


class ProjectCompressor:
    """Compress and decompress PyGameMaker projects"""
    
    @staticmethod
    def compress_project(project_path: Path, output_zip_path: Path) -> bool:
        """
        Compress a project folder into a .zip file
        
        Args:
            project_path: Path to project folder
            output_zip_path: Path to output .zip file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure output has .zip extension
            if not output_zip_path.suffix == '.zip':
                output_zip_path = output_zip_path.with_suffix('.zip')
            
            # Create zip file
            with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Walk through project directory
                for file_path in project_path.rglob('*'):
                    if file_path.is_file():
                        # Calculate relative path
                        arcname = file_path.relative_to(project_path)
                        
                        # Add file to zip
                        zipf.write(file_path, arcname)
                        print(f"  Added: {arcname}")
            
            print(f"✅ Project compressed to: {output_zip_path}")
            print(f"   Original size: {ProjectCompressor._get_folder_size(project_path) / 1024:.1f} KB")
            print(f"   Compressed size: {output_zip_path.stat().st_size / 1024:.1f} KB")
            
            return True
            
        except Exception as e:
            print(f"❌ Error compressing project: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    @staticmethod
    def decompress_project(zip_path: Path, output_folder: Path) -> bool:
        """
        Decompress a .zip project into a folder
        
        Args:
            zip_path: Path to .zip file
            output_folder: Path to extract to
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create output folder if it doesn't exist
            output_folder.mkdir(parents=True, exist_ok=True)
            
            # Extract zip file
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                zipf.extractall(output_folder)
                print(f"✅ Project extracted to: {output_folder}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error decompressing project: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    @staticmethod
    def is_project_zip(file_path: Path) -> bool:
        """
        Check if a file is a valid PyGameMaker project zip
        
        Args:
            file_path: Path to check
            
        Returns:
            True if valid project zip, False otherwise
        """
        try:
            if not file_path.suffix == '.zip':
                return False
            
            with zipfile.ZipFile(file_path, 'r') as zipf:
                # Check for project.json in root
                namelist = zipf.namelist()
                return 'project.json' in namelist or any(
                    name.endswith('project.json') for name in namelist
                )
        except Exception:
            return False
    
    @staticmethod
    def create_temporary_extraction(zip_path: Path) -> Path:
        """
        Extract project to a temporary directory
        
        Args:
            zip_path: Path to .zip file
            
        Returns:
            Path to temporary extraction directory
        """
        temp_dir = Path(tempfile.mkdtemp(prefix='pygamemaker_'))
        
        if ProjectCompressor.decompress_project(zip_path, temp_dir):
            return temp_dir
        else:
            shutil.rmtree(temp_dir, ignore_errors=True)
            return None
    
    @staticmethod
    def _get_folder_size(folder_path: Path) -> int:
        """Get total size of all files in folder"""
        total_size = 0
        for file_path in folder_path.rglob('*'):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        return total_size
    
    @staticmethod
    def get_project_name_from_zip(zip_path: Path) -> str:
        """
        Get project name from a zip file without extracting
        
        Args:
            zip_path: Path to .zip file
            
        Returns:
            Project name or None
        """
        try:
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                # Find project.json
                project_json_path = None
                for name in zipf.namelist():
                    if name.endswith('project.json'):
                        project_json_path = name
                        break
                
                if project_json_path:
                    # Read and parse project.json
                    with zipf.open(project_json_path) as f:
                        project_data = json.load(f)
                        return project_data.get('name', 'Unknown')
            
            return None
            
        except Exception as e:
            print(f"Error reading project name from zip: {e}")
            return None


class ZipProjectHandler:
    """
    Handle reading/writing directly to zip files without full extraction
    Allows working with projects in-place inside zip archives
    """
    
    def __init__(self, zip_path: Path):
        self.zip_path = zip_path
        self._cache = {}  # Cache for frequently accessed files
    
    def read_project_json(self) -> Optional[Dict[str, Any]]:
        """Read project.json directly from zip"""
        try:
            with zipfile.ZipFile(self.zip_path, 'r') as zipf:
                # Find project.json
                project_json_path = None
                for name in zipf.namelist():
                    if name == 'project.json' or name.endswith('/project.json'):
                        project_json_path = name
                        break
                
                if project_json_path:
                    with zipf.open(project_json_path) as f:
                        return json.load(f)
            
            return None
            
        except Exception as e:
            print(f"Error reading project.json from zip: {e}")
            return None
    
    def write_project_json(self, project_data: Dict[str, Any]) -> bool:
        """
        Update project.json in zip file
        This recreates the zip with the updated project.json
        """
        try:
            # Create temporary zip
            temp_zip = self.zip_path.with_suffix('.tmp')
            
            with zipfile.ZipFile(self.zip_path, 'r') as zip_read:
                with zipfile.ZipFile(temp_zip, 'w', zipfile.ZIP_DEFLATED) as zip_write:
                    # Copy all files except project.json
                    for item in zip_read.infolist():
                        if not (item.filename == 'project.json' or item.filename.endswith('/project.json')):
                            data = zip_read.read(item.filename)
                            zip_write.writestr(item, data)
                    
                    # Write updated project.json
                    project_json_str = json.dumps(project_data, indent=2)
                    zip_write.writestr('project.json', project_json_str)
            
            # Replace original with temp
            temp_zip.replace(self.zip_path)
            
            print(f"✅ Updated project.json in {self.zip_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error updating project.json in zip: {e}")
            import traceback
            traceback.print_exc()
            
            # Cleanup temp file
            if temp_zip.exists():
                temp_zip.unlink()
            
            return False
    
    def read_asset_file(self, asset_path: str) -> Optional[bytes]:
        """
        Read an asset file from the zip
        
        Args:
            asset_path: Relative path to asset (e.g., 'sprites/player.png')
            
        Returns:
            File contents as bytes, or None
        """
        try:
            with zipfile.ZipFile(self.zip_path, 'r') as zipf:
                return zipf.read(asset_path)
        except Exception as e:
            print(f"Error reading asset {asset_path} from zip: {e}")
            return None
    
    def list_assets(self, asset_type: str = None) -> list:
        """
        List all assets in the zip, optionally filtered by type
        
        Args:
            asset_type: Optional filter (e.g., 'sprites', 'sounds')
            
        Returns:
            List of asset paths
        """
        try:
            with zipfile.ZipFile(self.zip_path, 'r') as zipf:
                all_files = zipf.namelist()
                
                if asset_type:
                    # Filter by asset type folder
                    return [f for f in all_files if f.startswith(f'{asset_type}/')]
                else:
                    return all_files
                    
        except Exception as e:
            print(f"Error listing assets from zip: {e}")
            return []
    
    def extract_asset_to_temp(self, asset_path: str) -> Optional[Path]:
        """
        Extract a single asset to a temporary file
        Useful for opening assets in editors
        
        Args:
            asset_path: Relative path to asset
            
        Returns:
            Path to temporary file, or None
        """
        try:
            # Create temp directory if needed
            temp_dir = Path(tempfile.gettempdir()) / 'pygamemaker_assets'
            temp_dir.mkdir(exist_ok=True)
            
            # Extract to temp
            with zipfile.ZipFile(self.zip_path, 'r') as zipf:
                temp_file = temp_dir / Path(asset_path).name
                
                with zipf.open(asset_path) as source:
                    with open(temp_file, 'wb') as target:
                        shutil.copyfileobj(source, target)
                
                return temp_file
                
        except Exception as e:
            print(f"Error extracting asset {asset_path}: {e}")
            return None