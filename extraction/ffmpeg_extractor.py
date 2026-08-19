"""
FFmpeg-based video frame extraction adapter.

Implements IFrameExtractor interface.
Responsible for locating the FFmpeg binary and extracting frames
at configurable intervals. Follows Open/Closed Principle — can be
replaced with another extractor without modifying calling code.
"""

import os
import subprocess
import shutil
from pathlib import Path
from typing import List, Optional

from core.interfaces import IFrameExtractor
from core.models import ExtractedFrame
from core.exceptions import DependencyMissingError


class FFmpegExtractor(IFrameExtractor):
    """Extracts video frames using FFmpeg."""

    # Common locations to search for FFmpeg on Windows
    _SEARCH_PATHS = [
        r"C:\Program Files\FormatFactory\ffmpeg.exe",
        r"C:\Program Files\FFmpeg\bin\ffmpeg.exe",
        r"C:\ffmpeg\bin\ffmpeg.exe",
    ]

    def __init__(self, custom_path: Optional[str] = None):
        self._binary_path = self._resolve_binary(custom_path)

    def _resolve_binary(self, custom_path: Optional[str] = None) -> str:
        """Locate the FFmpeg binary on the system."""
        # 1. User-specified path
        if custom_path and os.path.isfile(custom_path):
            return custom_path

        # 2. System PATH
        system_ffmpeg = shutil.which("ffmpeg")
        if system_ffmpeg:
            return system_ffmpeg

        # 3. Known installation paths
        for candidate in self._SEARCH_PATHS:
            if os.path.isfile(candidate):
                return candidate

        return ""

    def is_available(self) -> bool:
        """Check if FFmpeg binary was found."""
        return bool(self._binary_path)

    def get_binary_path(self) -> str:
        """Return resolved FFmpeg binary path."""
        return self._binary_path

    def extract_frames(self, video_path: Path, output_dir: Path,
                       interval_sec: int = 3) -> List[ExtractedFrame]:
        """
        Extract frames from video at the given interval.

        Args:
            video_path: Path to the source video file.
            output_dir: Directory where frame images will be saved.
            interval_sec: Seconds between each extracted frame.

        Returns:
            List of ExtractedFrame objects for each generated image.

        Raises:
            DependencyMissingError: If FFmpeg is not available.
        """
        if not self.is_available():
            raise DependencyMissingError(
                "FFmpeg",
                "Install FFmpeg from https://ffmpeg.org/download.html and add to PATH."
            )

        output_dir.mkdir(parents=True, exist_ok=True)

        pattern = str(output_dir / "frame_%06d.jpg")
        fps_filter = f"fps=1/{interval_sec}"

        cmd = [
            self._binary_path,
            "-y",
            "-i", str(video_path),
            "-vf", fps_filter,
            "-q:v", "2",
            pattern
        ]

        try:
            subprocess.run(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
                timeout=600  # 10 min max per video
            )
        except subprocess.TimeoutExpired:
            pass  # Process best-effort frames
        except subprocess.CalledProcessError:
            pass  # Some frames may still have been extracted

        # Collect extracted frame files
        frames = []
        frame_files = sorted(output_dir.glob("frame_*.jpg"))
        for idx, fpath in enumerate(frame_files):
            frames.append(ExtractedFrame(
                image_path=fpath,
                frame_index=idx + 1,
                timestamp_sec=idx * interval_sec,
            ))

        return frames
