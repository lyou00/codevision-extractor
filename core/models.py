"""
Domain models for CodeVision Extractor.

Pure data classes with no external dependencies.
Follows the Single Responsibility Principle — each model represents
one distinct concept in the extraction pipeline.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path


@dataclass
class VideoFile:
    """Represents a single video file to be processed."""
    path: Path
    name: str = ""

    def __post_init__(self):
        if not self.name:
            self.name = self.path.stem


@dataclass
class ExtractedFrame:
    """Represents one frame image extracted from a video."""
    image_path: Path
    frame_index: int
    timestamp_sec: float = 0.0
    is_code_candidate: bool = False


@dataclass
class OcrResult:
    """Holds OCR output for a single frame."""
    frame: ExtractedFrame
    raw_text: str = ""
    cleaned_lines: List[str] = field(default_factory=list)
    is_code: bool = False


@dataclass
class CodeSnapshot:
    """A single point-in-time snapshot of the code being built."""
    index: int
    source_frame: str
    lines: List[str] = field(default_factory=list)


@dataclass
class ReconstructedScript:
    """The final reconstructed C# script with its build history."""
    class_name: str
    final_lines: List[str] = field(default_factory=list)
    history: List[CodeSnapshot] = field(default_factory=list)
    source_video: str = ""


@dataclass
class ExtractionReport:
    """Summary report for one video processing run."""
    video_name: str
    total_frames: int = 0
    candidate_frames: int = 0
    scripts_found: List[str] = field(default_factory=list)
    output_dir: str = ""
    errors: List[str] = field(default_factory=list)
