"""
C# class / script name detector.

Scans OCR text for class declarations, IDE breadcrumbs, and visible .cs file
names to determine which script is being edited.
"""

import re
from typing import List, Optional


class ClassDetector:
    """Detects C# class names from OCR text."""

    _CLASS_PATTERN = re.compile(
        r'\bclass\s+([A-Z_][A-Za-z0-9_]*)',
        re.IGNORECASE
    )

    _CS_FILE_PATTERN = re.compile(
        r'\b([A-Za-z_][A-Za-z0-9_]*)\.cs\b',
        re.IGNORECASE
    )

    _FALSE_POSITIVES = {
        "MonoBehaviour",
        "ScriptableObject",
        "Editor",
        "Program",
        "Script",
    }

    def detect_class_name(self, all_lines: List[str]) -> str:
        """
        Detect the primary C# class name from a collection of lines.

        Strategy:
        1. Prefer explicit class declarations.
        2. Fall back to visible .cs filenames from tabs or breadcrumbs.
        3. Default to ExtractedScript if nothing is found.
        """
        class_counts = {}
        for line in all_lines:
            match = self._CLASS_PATTERN.search(line)
            if match:
                name = match.group(1)
                if name not in self._FALSE_POSITIVES:
                    class_counts[name] = class_counts.get(name, 0) + 1

        if class_counts:
            return max(class_counts, key=class_counts.get)

        for line in all_lines:
            match = self._CS_FILE_PATTERN.search(line)
            if match:
                name = match.group(1)
                if name not in self._FALSE_POSITIVES:
                    return name

        return "ExtractedScript"

    def detect_frame_class(self, cleaned_lines: List[str],
                           raw_text: str = "") -> Optional[str]:
        """
        Detect the class/script currently visible in one frame.

        Per-frame detection lets the extractor keep project state across
        lessons when an instructor reopens an older script and edits it later.
        """
        lines = list(cleaned_lines)
        if raw_text:
            lines.extend(raw_text.splitlines())

        class_name = self.detect_class_name(lines)
        if class_name != "ExtractedScript":
            return class_name

        return None
