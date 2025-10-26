#!/usr/bin/env python3

import os
import shutil
import hashlib
import tempfile
import mimetypes
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple, Union, Callable
from datetime import datetime
import json
import zipfile
import tarfile


class FileUtils:
    """Utility class for common file operations"""
    
    # Common file type mappings
    IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tga', '.webp', '.ico', '.svg'}
    AUDIO_EXTENSIONS = {'.wav', '.mp3', '.ogg', '.m4a', '.aac', '.flac', '.wma'}
    VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'}
    ARCHIVE_EXTENSIONS = {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz'}
    DOCUMENT_EXTENSIONS = {'.txt', '.md', '.pdf', '.doc', '.docx', '.rtf'}
    CODE_EXTENSIONS = {'.py', '.js', '.html', '.css', '.cpp', '.c', '.h', '.java', '.cs', '.gml'}
    DATA_EXTENSIONS = {'.json', '.xml', '.csv', '.yaml', '.yml', '.ini', '.cfg'}
    
    @staticmethod
    def ensure_directory(path: Union[str, Path]) -> Path:
        """Ensure directory exists, create if it doesn't"""
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @staticmethod
    def safe_copy(src: Union[str, Path], dst: Union[str, Path], 
                  backup: bool = True, overwrite: bool = False) -> bool:
        """Safely copy a file with optional backup"""
        try:
            src_path = Path(src)
            dst_path = Path(dst)
            
            if not src_path.exists():
                raise FileNotFoundError(f"Source file not found: {src_path}")
            
            if not src_path.is_file():
                raise ValueError(f"Source is not a file: {src_path}")
            
            # Ensure destination directory exists
            FileUtils.ensure_directory(dst_path.parent)
            
            # Handle existing destination file
            if dst_path.exists():
                if not overwrite:
                    raise FileExistsError(f"Destination file already exists: {dst_path}")
                
                if backup:
                    backup_path = FileUtils.create_backup_path(dst_path)
                    shutil.copy2(dst_path, backup_path)
            
            # Copy the file
            shutil.copy2(src_path, dst_path)
            return True
            
        except Exception as e:
            print(f"Error copying file {src} to {dst}: {e}")
            return False
    
    @staticmethod
    def safe_move(src: Union[str, Path], dst: Union[str, Path], 
                  backup: bool = True, overwrite: bool = False) -> bool:
        """Safely move a file with optional backup"""
        try:
            src_path = Path(src)
            dst_path = Path(dst)
            
            if not src_path.exists():
                raise FileNotFoundError(f"Source file not found: {src_path}")
            
            # Ensure destination directory exists
            FileUtils.ensure_directory(dst_path.parent)
            
            # Handle existing destination file
            if dst_path.exists():
                if not overwrite:
                    raise FileExistsError(f"Destination file already exists: {dst_path}")
                
                if backup:
                    backup_path = FileUtils.create_backup_path(dst_path)
                    shutil.copy2(dst_path, backup_path)
            
            # Move the file
            shutil.move(str(src_path), str(dst_path))
            return True
            
        except Exception as e:
            print(f"Error moving file {src} to {dst}: {e}")
            return False
    
    @staticmethod
    def safe_delete(path: Union[str, Path], backup: bool = False) -> bool:
        """Safely delete a file with optional backup"""
        try:
            file_path = Path(path)
            
            if not file_path.exists():
                return True  # Already deleted
            
            if backup:
                backup_path = FileUtils.create_backup_path(file_path)
                shutil.copy2(file_path, backup_path)
            
            file_path.unlink()
            return True
            
        except Exception as e:
            print(f"Error deleting file {path}: {e}")
            return False
    
    @staticmethod
    def create_backup_path(file_path: Path) -> Path:
        """Create a backup path for a file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.stem}_{timestamp}.bak{file_path.suffix}"
        return file_path.parent / backup_name
    
    @staticmethod
    def get_file_hash(file_path: Union[str, Path], algorithm: str = "md5") -> str:
        """Get file hash using specified algorithm"""
        try:
            hasher = hashlib.new(algorithm)
            
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            
            return hasher.hexdigest()
            
        except Exception as e:
            print(f"Error calculating hash for {file_path}: {e}")
            return ""
    
    @staticmethod
    def get_file_size(file_path: Union[str, Path]) -> int:
        """Get file size in bytes"""
        try:
            return Path(file_path).stat().st_size
        except Exception:
            return 0
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        size_index = 0
        
        while size_bytes >= 1024 and size_index < len(size_names) - 1:
            size_bytes /= 1024.0
            size_index += 1
        
        return f"{size_bytes:.1f} {size_names[size_index]}"
    
    @staticmethod
    def get_file_type(file_path: Union[str, Path]) -> str:
        """Get file type category based on extension"""
        suffix = Path(file_path).suffix.lower()
        
        if suffix in FileUtils.IMAGE_EXTENSIONS:
            return "image"
        elif suffix in FileUtils.AUDIO_EXTENSIONS:
            return "audio"
        elif suffix in FileUtils.VIDEO_EXTENSIONS:
            return "video"
        elif suffix in FileUtils.ARCHIVE_EXTENSIONS:
            return "archive"
        elif suffix in FileUtils.DOCUMENT_EXTENSIONS:
            return "document"
        elif suffix in FileUtils.CODE_EXTENSIONS:
            return "code"
        elif suffix in FileUtils.DATA_EXTENSIONS:
            return "data"
        else:
            return "unknown"
    
    @staticmethod
    def get_mime_type(file_path: Union[str, Path]) -> str:
        """Get MIME type of file"""
        mime_type, _ = mimetypes.guess_type(str(file_path))
        return mime_type or "application/octet-stream"
    
    @staticmethod
    def is_valid_filename(filename: str) -> bool:
        """Check if filename is valid for current OS"""
        if not filename:
            return False
        
        # Invalid characters for Windows (most restrictive)
        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        for char in invalid_chars:
            if char in filename:
                return False
        
        # Reserved names on Windows
        reserved_names = [
            'CON', 'PRN', 'AUX', 'NUL',
            'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
            'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
        ]
        
        base_name = filename.split('.')[0].upper()
        if base_name in reserved_names:
            return False
        
        # Check for trailing periods or spaces
        if filename.endswith('.') or filename.endswith(' '):
            return False
        
        return True
    
    @staticmethod
    def sanitize_filename(filename: str, replacement: str = "_") -> str:
        """Sanitize filename by replacing invalid characters"""
        if not filename:
            return "untitled"
        
        # Replace invalid characters
        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        sanitized = filename
        
        for char in invalid_chars:
            sanitized = sanitized.replace(char, replacement)
        
        # Remove trailing periods and spaces
        sanitized = sanitized.rstrip('. ')
        
        # Check reserved names
        reserved_names = [
            'CON', 'PRN', 'AUX', 'NUL',
            'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
            'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
        ]
        
        base_name = sanitized.split('.')[0].upper()
        if base_name in reserved_names:
            sanitized = f"{replacement}{sanitized}"
        
        return sanitized or "untitled"
    
    @staticmethod
    def find_unique_path(base_path: Union[str, Path]) -> Path:
        """Find a unique path by adding numbers if file exists"""
        path = Path(base_path)
        
        if not path.exists():
            return path
        
        counter = 1
        stem = path.stem
        suffix = path.suffix
        parent = path.parent
        
        while True:
            new_name = f"{stem} ({counter}){suffix}"
            new_path = parent / new_name
            
            if not new_path.exists():
                return new_path
            
            counter += 1
    
    @staticmethod
    def compare_files(file1: Union[str, Path], file2: Union[str, Path]) -> bool:
        """Compare two files for equality"""
        try:
            path1 = Path(file1)
            path2 = Path(file2)
            
            # Quick size check
            if path1.stat().st_size != path2.stat().st_size:
                return False
            
            # Compare content in chunks
            chunk_size = 8192
            with open(path1, 'rb') as f1, open(path2, 'rb') as f2:
                while True:
                    chunk1 = f1.read(chunk_size)
                    chunk2 = f2.read(chunk_size)
                    
                    if chunk1 != chunk2:
                        return False
                    
                    if not chunk1:  # End of file
                        break
            
            return True
            
        except Exception:
            return False
    
    @staticmethod
    def clean_directory(directory: Union[str, Path], 
                       patterns: List[str] = None,
                       older_than_days: int = None,
                       dry_run: bool = True) -> List[Path]:
        """Clean directory by removing files matching patterns or age"""
        directory = Path(directory)
        removed_files = []
        
        if not directory.exists():
            return removed_files
        
        # Default patterns for temporary files
        if patterns is None:
            patterns = ['*.tmp', '*.bak', '*.log', '*~', '*.temp']
        
        try:
            for pattern in patterns:
                for file_path in directory.glob(pattern):
                    if file_path.is_file():
                        should_remove = True
                        
                        # Check age if specified
                        if older_than_days is not None:
                            file_age = datetime.now() - datetime.fromtimestamp(file_path.stat().st_mtime)
                            if file_age.days < older_than_days:
                                should_remove = False
                        
                        if should_remove:
                            if not dry_run:
                                file_path.unlink()
                            removed_files.append(file_path)
            
        except Exception as e:
            print(f"Error cleaning directory {directory}: {e}")
        
        return removed_files
    
    @staticmethod
    def create_archive(source_dir: Union[str, Path], 
                      output_path: Union[str, Path],
                      archive_type: str = "zip",
                      exclude_patterns: List[str] = None) -> bool:
        """Create archive from directory"""
        try:
            source_dir = Path(source_dir)
            output_path = Path(output_path)
            
            if not source_dir.exists():
                raise FileNotFoundError(f"Source directory not found: {source_dir}")
            
            # Ensure output directory exists
            FileUtils.ensure_directory(output_path.parent)
            
            # Default exclusion patterns
            if exclude_patterns is None:
                exclude_patterns = ['*.tmp', '*.bak', '*.log', '__pycache__', '.git']
            
            if archive_type.lower() == "zip":
                with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as archive:
                    for file_path in source_dir.rglob('*'):
                        if file_path.is_file():
                            # Check exclusion patterns
                            should_exclude = False
                            for pattern in exclude_patterns:
                                if file_path.match(pattern):
                                    should_exclude = True
                                    break
                            
                            if not should_exclude:
                                arcname = file_path.relative_to(source_dir)
                                archive.write(file_path, arcname)
            
            elif archive_type.lower() in ["tar", "tar.gz", "tgz"]:
                mode = "w:gz" if archive_type.lower() in ["tar.gz", "tgz"] else "w"
                with tarfile.open(output_path, mode) as archive:
                    for file_path in source_dir.rglob('*'):
                        if file_path.is_file():
                            # Check exclusion patterns
                            should_exclude = False
                            for pattern in exclude_patterns:
                                if file_path.match(pattern):
                                    should_exclude = True
                                    break
                            
                            if not should_exclude:
                                arcname = str(file_path.relative_to(source_dir))
                                archive.add(file_path, arcname)
            
            else:
                raise ValueError(f"Unsupported archive type: {archive_type}")
            
            return True
            
        except Exception as e:
            print(f"Error creating archive: {e}")
            return False
    
    @staticmethod
    def extract_archive(archive_path: Union[str, Path], 
                       output_dir: Union[str, Path],
                       overwrite: bool = False) -> bool:
        """Extract archive to directory"""
        try:
            archive_path = Path(archive_path)
            output_dir = Path(output_dir)
            
            if not archive_path.exists():
                raise FileNotFoundError(f"Archive not found: {archive_path}")
            
            # Ensure output directory exists
            FileUtils.ensure_directory(output_dir)
            
            # Check if output directory is empty (unless overwrite is allowed)
            if not overwrite and any(output_dir.iterdir()):
                raise FileExistsError(f"Output directory is not empty: {output_dir}")
            
            suffix = archive_path.suffix.lower()
            
            if suffix == '.zip':
                with zipfile.ZipFile(archive_path, 'r') as archive:
                    archive.extractall(output_dir)
            
            elif suffix in ['.tar', '.gz', '.bz2', '.xz']:
                mode_map = {
                    '.tar': 'r',
                    '.gz': 'r:gz',
                    '.bz2': 'r:bz2',
                    '.xz': 'r:xz'
                }
                
                # Handle .tar.gz, .tar.bz2, etc.
                if archive_path.suffixes:
                    if len(archive_path.suffixes) >= 2 and archive_path.suffixes[-2] == '.tar':
                        mode = mode_map.get(suffix, 'r')
                    else:
                        mode = mode_map.get(suffix, 'r')
                else:
                    mode = 'r'
                
                with tarfile.open(archive_path, mode) as archive:
                    archive.extractall(output_dir)
            
            else:
                raise ValueError(f"Unsupported archive format: {suffix}")
            
            return True
            
        except Exception as e:
            print(f"Error extracting archive: {e}")
            return False
    
    @staticmethod
    def load_json(file_path: Union[str, Path], default: Any = None) -> Any:
        """Safely load JSON file with default fallback"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading JSON from {file_path}: {e}")
            return default
    
    @staticmethod
    def save_json(data: Any, file_path: Union[str, Path], 
                  indent: int = 2, backup: bool = True) -> bool:
        """Safely save data as JSON file"""
        try:
            file_path = Path(file_path)
            
            # Ensure directory exists
            FileUtils.ensure_directory(file_path.parent)
            
            # Create backup if file exists
            if backup and file_path.exists():
                backup_path = FileUtils.create_backup_path(file_path)
                shutil.copy2(file_path, backup_path)
            
            # Write to temporary file first
            temp_path = file_path.with_suffix(file_path.suffix + '.tmp')
            
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent, ensure_ascii=False)
            
            # Atomic rename
            temp_path.replace(file_path)
            
            return True
            
        except Exception as e:
            print(f"Error saving JSON to {file_path}: {e}")
            return False
    
    @staticmethod
    def read_text_file(file_path: Union[str, Path], encoding: str = 'utf-8') -> str:
        """Read text file with specified encoding"""
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except Exception as e:
            print(f"Error reading text file {file_path}: {e}")
            return ""
    
    @staticmethod
    def write_text_file(text: str, file_path: Union[str, Path], 
                       encoding: str = 'utf-8', backup: bool = True) -> bool:
        """Write text to file with specified encoding"""
        try:
            file_path = Path(file_path)
            
            # Ensure directory exists
            FileUtils.ensure_directory(file_path.parent)
            
            # Create backup if file exists
            if backup and file_path.exists():
                backup_path = FileUtils.create_backup_path(file_path)
                shutil.copy2(file_path, backup_path)
            
            # Write to temporary file first
            temp_path = file_path.with_suffix(file_path.suffix + '.tmp')
            
            with open(temp_path, 'w', encoding=encoding) as f:
                f.write(text)
            
            # Atomic rename
            temp_path.replace(file_path)
            
            return True
            
        except Exception as e:
            print(f"Error writing text file {file_path}: {e}")
            return False
    
    @staticmethod
    def get_directory_size(directory: Union[str, Path]) -> int:
        """Get total size of directory in bytes"""
        try:
            total_size = 0
            for path in Path(directory).rglob('*'):
                if path.is_file():
                    total_size += path.stat().st_size
            return total_size
        except Exception as e:
            print(f"Error calculating directory size: {e}")
            return 0
    
    @staticmethod
    def find_files(directory: Union[str, Path], 
                   pattern: str = "*",
                   recursive: bool = True,
                   include_dirs: bool = False) -> List[Path]:
        """Find files matching pattern in directory"""
        try:
            directory = Path(directory)
            
            if not directory.exists():
                return []
            
            if recursive:
                paths = directory.rglob(pattern)
            else:
                paths = directory.glob(pattern)
            
            if include_dirs:
                return list(paths)
            else:
                return [p for p in paths if p.is_file()]
                
        except Exception as e:
            print(f"Error finding files: {e}")
            return []
    
    @staticmethod
    def copy_directory(src: Union[str, Path], dst: Union[str, Path], 
                      overwrite: bool = False) -> bool:
        """Copy directory recursively"""
        try:
            src_path = Path(src)
            dst_path = Path(dst)
            
            if not src_path.exists():
                raise FileNotFoundError(f"Source directory not found: {src_path}")
            
            if dst_path.exists() and not overwrite:
                raise FileExistsError(f"Destination directory already exists: {dst_path}")
            
            if dst_path.exists() and overwrite:
                shutil.rmtree(dst_path)
            
            shutil.copytree(src_path, dst_path)
            return True
            
        except Exception as e:
            print(f"Error copying directory: {e}")
            return False
    
    @staticmethod
    def create_temp_file(suffix: str = "", prefix: str = "tmp", 
                        directory: Union[str, Path] = None) -> Path:
        """Create temporary file and return path"""
        fd, path = tempfile.mkstemp(suffix=suffix, prefix=prefix, dir=directory)
        os.close(fd)
        return Path(path)
    
    @staticmethod
    def create_temp_directory(prefix: str = "tmp", 
                             directory: Union[str, Path] = None) -> Path:
        """Create temporary directory and return path"""
        return Path(tempfile.mkdtemp(prefix=prefix, dir=directory))
    
    @staticmethod
    def is_hidden(file_path: Union[str, Path]) -> bool:
        """Check if file/directory is hidden"""
        path = Path(file_path)
        
        # Unix-style hidden files (starting with .)
        if path.name.startswith('.'):
            return True
        
        # Windows hidden files
        if os.name == 'nt':
            try:
                attrs = os.stat(path).st_file_attributes
                return attrs & 0x02  # FILE_ATTRIBUTE_HIDDEN
            except:
                return False
        
        return False


# Convenience functions that use the FileUtils class
def ensure_directory(path: Union[str, Path]) -> Path:
    """Ensure directory exists, create if it doesn't"""
    return FileUtils.ensure_directory(path)

def safe_copy(src: Union[str, Path], dst: Union[str, Path], 
              backup: bool = True, overwrite: bool = False) -> bool:
    """Safely copy a file with optional backup"""
    return FileUtils.safe_copy(src, dst, backup, overwrite)

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    return FileUtils.format_file_size(size_bytes)

def get_file_hash(file_path: Union[str, Path], algorithm: str = "md5") -> str:
    """Get file hash using specified algorithm"""
    return FileUtils.get_file_hash(file_path, algorithm)

def load_json(file_path: Union[str, Path], default: Any = None) -> Any:
    """Safely load JSON file with default fallback"""
    return FileUtils.load_json(file_path, default)

def save_json(data: Any, file_path: Union[str, Path], 
              indent: int = 2, backup: bool = True) -> bool:
    """Safely save data as JSON file"""
    return FileUtils.save_json(data, file_path, indent, backup)
