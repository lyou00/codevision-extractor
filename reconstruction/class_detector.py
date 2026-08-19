"""
C# class / script name detector.

Scans OCR text for class declarations and IDE breadcrumb paths
to determine the filename of the script being edited in the video.
"""

import re
from typing import List, Optional


class ClassDetector:
    """Detects C# class names from OCR text."""

    # Pattern: public class ClassName : MonoBehaviour
    _CLASS_PATTERN = re.compile(
        r'\bclass\s+([A-Z][A-Za-z0-9_]+)',
        re.IGNORECASE
    )

    # Pattern: breadcrumb like "Assets > Scripts > ... > ClassName.cs"
    _BREADCRUMB_PATTERN = re.compile(
        r'>\s*©?\s*(\w+)\.cs',
        re.IGNORECASE
    )

    def detect_class_name(self, all_lines: List[str]) -> str:
        """
        Detect the primary C# class name from a collection of cleaned code lines.

        Strategy:
        1. Look for explicit class declarations.
        2. Fall back to breadcrumb filename detection.
        3. Default to "ExtractedScript" if nothing found.

        Args:
            all_lines: All cleaned code lines across all frames.

        Returns:
            The detected class name string.
        """
        # Strategy 1: Class declaration
        class_counts: dict = {}
        for line in all_lines:
            match = self._CLASS_PATTERN.search(line)
            if match:
                name = match.group(1)
                # Filter out common false positives
                if name not in ("MonoBehaviour", "ScriptableObject", "Editor"):
                    class_counts[name] = class_counts.get(name, 0) + 1

        if class_counts:
            # Return the most frequently detected class name
            return max(class_counts, key=class_counts.get)

        # Strategy 2: Breadcrumb path
        for line in all_lines:
            match = self._BREADCRUMB_PATTERN.search(line)
            if match:
                return match.group(1)

        return "ExtractedScript"
