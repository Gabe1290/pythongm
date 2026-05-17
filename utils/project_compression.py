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


