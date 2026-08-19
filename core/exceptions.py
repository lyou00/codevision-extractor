"""
Custom exceptions for CodeVision Extractor.

Provides clear, user-friendly error messages for common failure scenarios.
Follows the Single Responsibility Principle — each exception handles one
specific failure domain.
"""


class CodeVisionError(Exception):
    """Base exception for all CodeVision errors."""
    pass


class VideoNotFoundError(CodeVisionError):
    """Raised when a specified video file does not exist."""

    def __init__(self, path: str):
        self.path = path
        super().__init__(
            f"\n[ERROR] Video file not found: {path}\n"
            f"  -> Please check the file path and try again.\n"
            f"  -> Supported formats: .mp4, .mkv, .avi, .mov, .webm"
        )


class NoVideosInFolderError(CodeVisionError):
    """Raised when target folder contains no supported video files."""

    def __init__(self, folder: str):
        self.folder = folder
        super().__init__(
            f"\n[ERROR] No video files found in: {folder}\n"
            f"  -> Supported formats: .mp4, .mkv, .avi, .mov, .webm\n"
            f"  -> Make sure video files are placed directly in the folder."
        )


class DependencyMissingError(CodeVisionError):
    """Raised when a required external tool (FFmpeg/Tesseract) is not found."""

    def __init__(self, tool_name: str, install_hint: str = ""):
        self.tool_name = tool_name
        msg = f"\n[ERROR] Required dependency not found: {tool_name}"
        if install_hint:
            msg += f"\n  -> {install_hint}"
        super().__init__(msg)


class OcrProcessingError(CodeVisionError):
    """Raised when OCR processing fails for a frame."""

    def __init__(self, frame_path: str, reason: str = ""):
        self.frame_path = frame_path
        msg = f"\n[WARNING] OCR failed for frame: {frame_path}"
        if reason:
            msg += f"\n  -> Reason: {reason}"
        super().__init__(msg)


class InvalidPathError(CodeVisionError):
    """Raised when the provided path is invalid."""

    def __init__(self, path: str):
        self.path = path
        super().__init__(
            f"\n[ERROR] Invalid path: {path}\n"
            f"  -> The path does not exist. Please verify and try again."
        )
