"""
Input path validator for CodeVision Extractor.

Validates user-provided paths (file or folder) and discovers
supported video files. Returns clear error messages for invalid inputs.
"""

import os
from pathlib import Path
from typing import List

from core.models import VideoFile
from core.exceptions import (
    InvalidPathError,
    VideoNotFoundError,
    NoVideosInFolderError,
)


# Supported video file extensions
SUPPORTED_EXTENSIONS = {'.mp4', '.mkv', '.avi', '.mov', '.webm', '.flv', '.wmv'}


class InputValidator:
    """Validates input paths and discovers video files."""

    def validate_file(self, file_path: str) -> VideoFile:
        """
        Validate a single video file path.

        Args:
            file_path: Absolute or relative path to a video file.

        Returns:
            VideoFile object if valid.

        Raises:
            InvalidPathError: If path does not exist.
            VideoNotFoundError: If file is not a supported video format.
        """
        path = Path(file_path).resolve()

        if not path.exists():
            raise InvalidPathError(str(path))

        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            raise VideoNotFoundError(str(path))

        return VideoFile(path=path)

    def validate_folder(self, folder_path: str) -> List[VideoFile]:
        """
        Validate a folder and discover all video files within it.

        Args:
            folder_path: Path to the video folder.

        Returns:
            List of VideoFile objects found in the folder.

        Raises:
            InvalidPathError: If path does not exist.
            NoVideosInFolderError: If no supported videos are found.
        """
        path = Path(folder_path).resolve()

        if not path.exists() or not path.is_dir():
            raise InvalidPathError(str(path))

        videos = []
        for f in sorted(path.rglob("*")):
            if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS:
                # Skip files inside output directories
                parts_lower = [p.lower() for p in f.parts]
                if any(skip in parts_lower for skip in
                       ['_extracted_csharp', '_extracted_csharp_v2',
                        'frames', 'candidateframes']):
                    continue
                videos.append(VideoFile(path=f))

        if not videos:
            raise NoVideosInFolderError(str(path))

        return videos
