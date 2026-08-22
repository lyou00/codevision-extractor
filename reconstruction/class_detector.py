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

    _NAME_CORRECTIONS = [
        (r'^Gam[a-z]*anager$', 'GameManager'),
        (r'^Gan[a-z]*anager$', 'GameManager'),
        (r'^GaneManager$', 'GameManager'),
        (r'^Cam[a-z]*anager$', 'CameraManager'),
        (r'^Input[a-z]*anager$', 'InputManager'),
        (r'^Imput[a-z]*ager$', 'InputManager'),
        (r'^mputManager$', 'InputManager'),
        (r'^PlayerMover[a-z]*$', 'PlayerMovement'),
        (r'^CarC[a-z]*mera[a-z]*Contro[a-z]*$', 'CarCameraController'),
        (r'^CarCa[a-z]*era[a-z]*Contro[a-z]*$', 'CarCameraController'),
        (r'^CarContro[a-z]*$', 'CarController'),
        (r'^ShootingContro[a-z0-9]*$', 'ShootingController'),
        (r'^PoliceO[a-z]*ficer$', 'PoliceOfficer'),
        (r'^PoliceO[a-z]*ficer2$', 'PoliceOfficer2'),
        (r'^Wantedtevel$', 'WantedLevel'),
        (r'^WaypointE[a-z]*ditor$', 'WaypointEditor'),
        (r'^Waypoint[a-z]*anager[a-z]*indow$', 'WaypointManagerWindow'),
        (r'^Main[a-z]*enu[a-z]*anager$', 'MainMenuManager'),
        (r'^Pause[a-z]*enu$', 'PauseMenu'),
        (r'^AlSpawner$', 'AISpawner'),
        (r'^ATSpawner$', 'AISpawner'),
        (r'^ArSpawner$', 'AISpawner'),
    ]

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
                name = self.normalize_class_name(match.group(1))
                if self.is_valid_class_name(name):
                    class_counts[name] = class_counts.get(name, 0) + 1

        if class_counts:
            return max(class_counts, key=class_counts.get)

        for line in all_lines:
            match = self._CS_FILE_PATTERN.search(line)
            if match:
                name = self.normalize_class_name(match.group(1))
                if self.is_valid_class_name(name):
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

    def normalize_class_name(self, name: str) -> str:
        """Normalize common OCR mistakes in Unity C# script names."""
        cleaned = re.sub(r'[^A-Za-z0-9_]', '', name or "")
        if not cleaned:
            return ""

        if cleaned[:1].islower():
            cleaned = cleaned[:1].upper() + cleaned[1:]

        replacements = {
            "Hanager": "Manager",
            "hanager": "Manager",
            "tanager": "Manager",
            "Tanager": "Manager",
            "Canera": "Camera",
            "canera": "Camera",
            "Controtter": "Controller",
            "Controtler": "Controller",
            "Controtier": "Controller",
            "Controlter": "Controller",
            "Controlier": "Controller",
            "Controle": "Controller",
            "Control1e": "Controller",
            "Movernent": "Movement",
            "Moverent": "Movement",
            "Movenent": "Movement",
            "Oftficer": "Officer",
            "Ofticer": "Officer",
            "Otficer": "Officer",
            "Ottficer": "Officer",
            "Otticer": "Officer",
            "ficer": "Officer",
            "Wlaypoint": "Waypoint",
            "baypoint": "Waypoint",
            "Nalligator": "Navigator",
            "Wiaypoint": "Waypoint",
            "Eiditor": "Editor",
            "Eiitor": "Editor",
            "Esditor": "Editor",
            "Esitor": "Editor",
        }
        for bad, good in replacements.items():
            cleaned = cleaned.replace(bad, good)

        for pattern, replacement in self._NAME_CORRECTIONS:
            if re.match(pattern, cleaned, re.IGNORECASE):
                return replacement

        return cleaned

    def is_valid_class_name(self, name: str) -> bool:
        """Reject obvious OCR gibberish before it becomes a project file."""
        if not name or name in self._FALSE_POSITIVES:
            return False
        if len(name) < 3 or len(name) > 48:
            return False
        if not re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', name):
            return False

        letters = re.findall(r'[A-Za-z]', name)
        if letters:
            upper_ratio = sum(1 for c in letters if c.isupper()) / len(letters)
            if len(letters) > 10 and upper_ratio > 0.75:
                return False

        return True
