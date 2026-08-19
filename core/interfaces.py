"""
Abstract interfaces for CodeVision Extractor.

Defines contracts that infrastructure adapters must implement.
Follows the Dependency Inversion Principle — high-level modules
depend on abstractions, not concrete implementations.

This allows swapping FFmpeg for another extractor, or Tesseract
for a cloud OCR API, or adding AI-based reconstruction later.
"""

from abc import ABC, abstractmethod
from typing import List
from pathlib import Path

from core.models import ExtractedFrame, OcrResult, ReconstructedScript


class IFrameExtractor(ABC):
    """Contract for video frame extraction engines."""

    @abstractmethod
    def extract_frames(self, video_path: Path, output_dir: Path,
                       interval_sec: int = 3) -> List[ExtractedFrame]:
        """Extract frames from a video at the given interval."""
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the extraction engine binary is available."""
        ...


class IOcrEngine(ABC):
    """Contract for OCR processing engines."""

    @abstractmethod
    def process_frame(self, frame: ExtractedFrame,
                      output_dir: Path) -> OcrResult:
        """Run OCR on a single frame image."""
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the OCR engine binary is available."""
        ...


class ICodeReconstructor(ABC):
    """Contract for code reconstruction engines."""

    @abstractmethod
    def reconstruct(self, ocr_results: List[OcrResult]) -> ReconstructedScript:
        """Reconstruct a clean C# script from chronological OCR results."""
        ...
