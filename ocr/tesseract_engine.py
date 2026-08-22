"""
Tesseract OCR engine adapter.

Implements the IOcrEngine interface.
Handles Tesseract binary detection (system PATH or local portable install)
and per-frame OCR processing with C# code candidate scoring.
"""

import os
import subprocess
import shutil
from pathlib import Path
from typing import Optional, List

from core.interfaces import IOcrEngine
from core.models import ExtractedFrame, OcrResult
from core.exceptions import DependencyMissingError
from ocr.noise_filter import NoiseFilter

import re


class TesseractEngine(IOcrEngine):
    """Processes video frames using Tesseract OCR."""

    # C# code indicator patterns for candidate scoring
    _CODE_INDICATORS = [
        r'using\s+System',
        r'using\s+Unity',
        r'MonoBehaviour',
        r'public\s+class',
        r'private\s+class',
        r'void\s+Start',
        r'void\s+Update',
        r'void\s+Awake',
        r'\[Header\(',
        r'\[SerializeField\]',
        r'public\s+(int|float|bool|string|GameObject|Transform)',
        r'private\s+(int|float|bool|string|GameObject|Transform)',
        r'(public|private|protected|internal)\s+\w+',
        r'(if|else|for|foreach|while|switch)\s*\(',
        r'(Instantiate|Destroy|SetActive|GetComponent)\s*\(',
        r'(Input|Time|SceneManager|PlayerPrefs)\.',
        r'\b(return|break|continue)\b',
        r'\{|\}|;',
        r'GetComponent\b',
    ]

    def __init__(self, custom_path: Optional[str] = None,
                 tessdata_dir: Optional[str] = None):
        self._binary_path = self._resolve_binary(custom_path)
        self._tessdata_dir = tessdata_dir or ""
        self._noise_filter = NoiseFilter()

        # Set TESSDATA_PREFIX if a local tessdata was provided
        if self._tessdata_dir and os.path.isdir(self._tessdata_dir):
            os.environ["TESSDATA_PREFIX"] = self._tessdata_dir

    def _resolve_binary(self, custom_path: Optional[str] = None) -> str:
        """Locate the Tesseract binary."""
        if custom_path and os.path.isfile(custom_path):
            return custom_path

        system_tess = shutil.which("tesseract")
        if system_tess:
            return system_tess

        # Check common Windows install locations
        candidates = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        ]
        for c in candidates:
            if os.path.isfile(c):
                return c

        return ""

    def is_available(self) -> bool:
        """Check if Tesseract binary was found."""
        return bool(self._binary_path)

    def get_binary_path(self) -> str:
        return self._binary_path

    def _score_code_likelihood(self, text: str) -> int:
        """Score how likely the text contains C# code (0-100)."""
        score = 0
        for pattern in self._CODE_INDICATORS:
            if re.search(pattern, text, re.IGNORECASE):
                score += 10
        return min(score, 100)

    def process_frame(self, frame: ExtractedFrame,
                      output_dir: Path) -> OcrResult:
        """
        Run OCR on a single frame and return cleaned result.

        Args:
            frame: The extracted frame to process.
            output_dir: Directory to save raw OCR text output.

        Returns:
            OcrResult with raw and cleaned text, plus code candidate flag.
        """
        if not self.is_available():
            raise DependencyMissingError(
                "Tesseract OCR",
                "Install from https://github.com/UB-Mannheim/tesseract/wiki"
            )

        output_dir.mkdir(parents=True, exist_ok=True)
        txt_base = output_dir / frame.image_path.stem
        txt_file = Path(str(txt_base) + ".txt")

        cmd = [
            self._binary_path,
            str(frame.image_path),
            str(txt_base),
            "--psm", "6",
            "txt"
        ]

        try:
            subprocess.run(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
                timeout=30
            )
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            return OcrResult(frame=frame, raw_text="", cleaned_lines=[], is_code=False)

        # Read raw OCR output
        raw_text = ""
        if txt_file.exists():
            raw_text = txt_file.read_text(encoding="utf-8", errors="ignore")

        # Score code likelihood
        score = self._score_code_likelihood(raw_text)
        is_code = score >= 10

        # Clean lines using noise filter
        cleaned = self._noise_filter.clean_frame_text(raw_text) if is_code else []

        # Update frame candidate status
        frame.is_code_candidate = is_code

        return OcrResult(
            frame=frame,
            raw_text=raw_text,
            cleaned_lines=cleaned,
            is_code=is_code,
        )
