"""
IDE / Visual Studio noise filter and OCR typo corrector.

Responsible for:
1. Removing IDE UI elements (menus, status bars, breadcrumbs, autocomplete).
2. Stripping OCR-injected line numbers and cursor artifacts.
3. Correcting common OCR misreadings of C# / Unity keywords.

Follows Single Responsibility Principle — only handles text cleaning.
"""

import re
from typing import Optional, List, Tuple


class NoiseFilter:
    """Filters IDE noise and corrects OCR typos from extracted text."""

    # ─── OCR Typo Correction Rules ─────────────────────────────────
    # Format: (regex_pattern, replacement_string)
    OCR_CORRECTIONS: List[Tuple[str, str]] = [
        # Unity / C# keywords
        (r'Unityéngine',                'UnityEngine'),
        (r'Unityengine',                'UnityEngine'),
        (r'MonoBchaviour',              'MonoBehaviour'),
        (r'Monofehaviour',              'MonoBehaviour'),
        (r'NonoBehaviour',              'MonoBehaviour'),
        (r'Honodchaviour',              'MonoBehaviour'),
        (r'Honotehaviour',              'MonoBehaviour'),
        (r'Monoiehaviour',              'MonoBehaviour'),
        (r'Monodchaviour',              'MonoBehaviour'),
        (r'Mono¥chavio',                'MonoBehavio'),
        (r'System\.Ccollections',       'System.Collections'),
        (r'System\.collections',        'System.Collections'),
        (r'System\.Collections\.\s*Generic', 'System.Collections.Generic'),

        # Header attribute
        (r'\[f[a-z]*Header\(',          '[Header('),
        (r'\[fleader\(',                '[Header('),
        (r'\[fileader\(',               '[Header('),
        (r'\[fieader\(',                '[Header('),
        (r'\[fHeader\(',                '[Header('),

        # GameObject / Prefab
        (r'GaneObject',                 'GameObject'),
        (r'Gameobject(?!Prefab)',       'GameObject'),
        (r'Game0bject',                 'GameObject'),
        (r'EamObject',                  'camObject'),
        (r'EanObJeet',                  'camObject'),
        (r'canObject',                  'camObject'),
        (r'camobject',                  'camObject'),
        (r'cambject',                   'camObject'),
        (r'camdbject',                  'camObject'),
        (r'pistolGamedbject',           'pistolGameObject'),
        (r'akmGamedbject',              'akmGameObject'),
        (r'm416Gamedbject',             'm416GameObject'),
        (r'pistolGamecbject',           'pistolGameObject'),
        (r'pistolGamebject',            'pistolGameObject'),
        (r'pilstolGameObject',          'pistolGameObject'),
        (r'pistorrrefab',              'pistolPrefab'),
        (r'pistorPrefab',              'pistolPrefab'),
        (r'mai6Prefab',                'm416Prefab'),
        (r'maigprefab',                'm416Prefab'),
        (r'mai6prefab',                'm416Prefab'),
        (r'maisprefab',                'm416Prefab'),
        (r'm4iepbjectPrefab',          'm416GameObjectPrefab'),
        (r'm4i6Prefab',                'm416Prefab'),
        (r'paseelPrefab',              'm416Prefab'),

        # Bool field names
        (r'riflelactive',              'rifle1Active'),
        (r'rifletactive',              'rifle1Active'),
        (r'riflelaActive',             'rifle1Active'),
        (r'niflgaActive',              'rifle1Active'),
        (r'rifleiActive',              'rifle1Active'),
        (r'rifleiactive',              'rifle1Active'),
        (r'riflezactive',             'rifle2Active'),
        (r'riflezActive',             'rifle2Active'),
        (r'mifleaActivel',            'rifle2Active'),
        (r'riflezactives',            'rifle2Active'),
        (r'riflesactive',             'rifle3Active'),
        (r'rifle3active',             'rifle3Active'),
        (r'niflesactive',             'rifle3Active'),
        (r'piFlgsActivel',            'rifle3Active'),
        (r'RAlRLEsAEEIVe!',           'rifle3Active'),

        # Misc
        (r'\[Header\("Player Money and kills"\)/\]\]',
         '[Header("Player Money and Kills")]'),
        (r'\[Header\("Player Money and kilf"\)\]\)',
         '[Header("Player Money and Kills")]'),

        # Common Unity/C# OCR glitches
        (r'FindobjectofType',           'FindObjectOfType'),
        (r'FindobjectOfType',           'FindObjectOfType'),
        (r'FindObjectoftype',           'FindObjectOfType'),
        (r'GetComponent\s+<',           'GetComponent<'),
        (r'Inputtanager',               'InputManager'),
        (r'tnputManager',               'InputManager'),
        (r'inputManager\. vertical Input', 'inputManager.verticalInput'),
        (r'horizontalinput',            'horizontalInput'),
        (r'verticalinput',              'verticalInput'),
        (r'verticaltnput',              'verticalInput'),
        (r'moveanount',                 'moveAmount'),
        (r'issprinting',                'isSprinting'),
        (r'istnteracting',              'isInteracting'),
        (r'targetDiffection',           'targetDirection'),
        (r'movenentVelocity',           'movementVelocity'),
        (r'HandleAli',                  'HandleAll'),
        (r'HandleAl1',                  'HandleAll'),
        (r'LookRotation\s+\(',          'LookRotation('),
        (r'transform\. forward',        'transform.forward'),
        (r'playerRigidbody\. velocity', 'playerRigidbody.velocity'),
    ]

    # ─── IDE UI Noise Patterns (lines matching these are discarded) ──
    UI_NOISE_PATTERNS: List[str] = [
        r'^.*File\s+Edit.*Selection.*View.*$',
        r'^\s*﻿?>\s+file\s+Edit.*$',
        r'^.*Restricted\s+Mode.*$',
        r'^.*Spaces:\d+.*$',
        r'^.*UTF-8.*CRLF.*$',
        r'^.*Ln\s*\d+.*Col\s*\d+.*$',

        # VS autocomplete / intellisense suggestions
        r'^.*OnParticlecollision.*MonoBehaviour.*$',
        r'^.*OnApplicationPause.*$',
        r'^.*OnApplicationFocus.*$',
        r'^.*OnPlayerDisconnected.*$',
        r'^.*OnParticleTrigger.*$',
        r'^.*OnPostRender.*$',
        r'^.*OnPreCull.*$',
        r'^.*OnPreRender.*$',
        r'^.*OnRenderObject.*$',
        r'^.*OnAudioFilterRead.*$',
        r'^.*OnAnimatorIK.*$',
        r'^.*MonoBehaviour\s+On\w+.*$',
        r'^.*MonoBehaviour\s+Reset.*$',
        r'^.*Honotehaviour\s+onapplication.*$',

        # IDE tab / breadcrumb / random garble
        r'^\s*\(C\)\s+©\s+Game.*$',
        r'^\s*\(Q\)\s+©\s+Same.*$',
        r'^\s*\(D\)\s+©\s+Game.*$',
        r'^\s*we\s+ee\s+re.*$',
        r'^\s*ere\s+i\}.*$',
        r'^\s*Py\s+oem.*$',
        r'^\s*Py\s+OSS.*$',
        r'^\s*wy\s+Cee.*$',
        r'^\s*wy\s+Cer.*$',
        r'^\s*wy\)\s+Cer.*$',
        r'^\s*wy\)\s+Pere.*$',
        r'^\s*ft\s+\|e\s+artinn.*$',
        r'^\s*E:\s+>\s+Unity.*$',
        r'^.*[Oo]nrender[Ii]mage.*$',
        r'^.*WE[BDG]?\s+O[Rri].*$',
        r'^.*abc\s+GameObject.*$',
        r'^\s*@\s+.*$',

        # Breadcrumb paths (keep for class detection but remove from code)
        r'^\s*E:\s*>\s*UnityProjects.*$',
    ]

    # ─── C# Code Keywords (used to anchor prefix removal) ──────────
    _CODE_KEYWORDS = (
        r'using|public|private|protected|internal|class|struct|enum|'
        r'void|bool|int|float|string|double|var|return|if|else|for|'
        r'foreach|while|switch|case|break|new|static|override|virtual|'
        r'\[Header|\[SerializeField|\[Tooltip|namespace|abstract|sealed'
    )

    def clean_line(self, line: str) -> Optional[str]:
        """
        Clean a single OCR line.

        Returns cleaned line string, or None if the line is noise.
        """
        line = self._normalize_symbols(line)

        # 1. Check UI noise patterns
        for pat in self.UI_NOISE_PATTERNS:
            if re.search(pat, line, re.IGNORECASE):
                return None

        if self._looks_like_editor_tabs(line):
            return None

        cleaned = line

        # 2. Remove random prefix garble before C# keywords
        cleaned = self._trim_to_code_anchor(cleaned)
        cleaned = re.sub(
            rf'^\s*[\W_a-z]{{1,4}}\s+(?=({self._CODE_KEYWORDS}))',
            '', cleaned, flags=re.IGNORECASE
        )

        # 3. Strip OCR line numbers (e.g. "p 1 using..." or "2 7 [Header...")
        cleaned = re.sub(r'^\s*(?:[a-z]{1,2}\s+)?(?:\d+\s+)+', '', cleaned)
        cleaned = re.sub(r'^\s*\d+\s+', '', cleaned)
        cleaned = cleaned.strip()

        # 4. Remove trailing cursor/IDE characters
        cleaned = re.sub(r'\s*[|I@]\s*$', '', cleaned)
        cleaned = re.sub(r'\s+(?:fod|cs|a|i|zm|os|se|Ww|fu|Bp|pil|bt|ju)\s*$', '', cleaned)
        cleaned = re.sub(r'\s+(?:i\}|==|=|a|-)$', '', cleaned)

        if not cleaned or len(cleaned) < 3:
            return None

        # 5. Re-check noise on cleaned line
        for pat in self.UI_NOISE_PATTERNS:
            if re.search(pat, cleaned, re.IGNORECASE):
                return None

        # 6. Apply OCR corrections
        for typo, fix in self.OCR_CORRECTIONS:
            cleaned = re.sub(typo, fix, cleaned, flags=re.IGNORECASE)

        cleaned = self._trim_to_code_anchor(cleaned)
        cleaned = self._fix_common_syntax_noise(cleaned)
        cleaned = self._trim_trailing_noise(cleaned)

        if not self._is_code_like(cleaned):
            return None

        return cleaned

    def clean_frame_text(self, raw_text: str) -> List[str]:
        """
        Clean all lines from one frame's OCR output.

        Returns deduplicated list of cleaned code lines.
        """
        cleaned_lines = []
        for raw_line in raw_text.splitlines():
            result = self.clean_line(raw_line)
            if result:
                # Avoid consecutive duplicate lines within same frame
                if not cleaned_lines or cleaned_lines[-1] != result:
                    cleaned_lines.append(result)
        return cleaned_lines

    def _normalize_symbols(self, line: str) -> str:
        replacements = {
            "â€œ": "\"",
            "â€": "\"",
            "â€˜": "'",
            "â€™": "'",
            "Â©": " ",
            "ï»¿": "",
            "â€”": " ",
        }
        for bad, good in replacements.items():
            line = line.replace(bad, good)
        return line

    def _looks_like_editor_tabs(self, line: str) -> bool:
        return len(re.findall(r'\b\w+\.cs\b', line, re.IGNORECASE)) >= 2

    def _trim_to_code_anchor(self, line: str) -> str:
        match = re.search(
            rf'({self._CODE_KEYWORDS}|[A-Za-z_][A-Za-z0-9_\.]*\s*[=.;(])',
            line,
            re.IGNORECASE,
        )
        if match and match.start() <= 18:
            return line[match.start():].strip()
        return line.strip()

    def _fix_common_syntax_noise(self, line: str) -> str:
        line = re.sub(r'\bPublic\b', 'public', line)
        line = re.sub(r'\bPrivate\b', 'private', line)
        line = re.sub(r'\bUnityEngines\b', 'UnityEngine;', line)
        line = re.sub(r'MonoBehaviour\s*[.;]+$', 'MonoBehaviour', line)
        line = re.sub(r'(MonoBehaviour)\s+\d+\s*$', r'\1', line)
        line = re.sub(r'\bSystem\.\s*collections\b', 'System.Collections', line, flags=re.IGNORECASE)
        line = re.sub(r'\bSystem\.Collections\.\s*Generic\b', 'System.Collections.Generic', line, flags=re.IGNORECASE)
        line = re.sub(r'(?<=\W)@(?=\.\d)', '0', line)
        line = re.sub(r'(?<=\d)[Â¢#](?=\W|$)', 'f', line)
        line = re.sub(r'\bSf\b', '5f', line)
        line = re.sub(r'\bIplayerManager\b', '!playerManager', line)
        line = re.sub(r'\|\s*playerManager', '!playerManager', line)
        line = re.sub(r'\blisGrounded\b', '!isGrounded', line)
        line = re.sub(r'\s+;', ';', line)
        line = re.sub(r'\s+\)', ')', line)
        line = re.sub(r'\(\s+', '(', line)
        return line.strip()

    def _trim_trailing_noise(self, line: str) -> str:
        stripped = line.strip()

        if ';' in stripped:
            return stripped[:stripped.rfind(';') + 1].strip()

        if stripped.startswith("[") and "]" in stripped:
            return stripped[:stripped.find("]") + 1].strip()

        method_match = re.match(
            r'^((?:public|private|protected|internal|static|override|virtual|'
            r'void|bool|int|float|string|double|var|Vector[234]|Quaternion|'
            r'Rigidbody|Transform|GameObject|Text|Image|Slider|Animator|'
            r'Collider|Collision)\b.*?\))\s+.+$',
            stripped,
            re.IGNORECASE,
        )
        if method_match:
            return method_match.group(1).strip()

        control_match = re.match(
            r'^((?:if|else if|for|foreach|while|switch)\s*\(.*?\))\s+.+$',
            stripped,
            re.IGNORECASE,
        )
        if control_match:
            return control_match.group(1).strip()

        return stripped

    def _is_code_like(self, line: str) -> bool:
        stripped = line.strip()
        if stripped in ("{", "}", "};"):
            return True

        if re.match(r'^(?:else|if|for|while|switch)\s+[A-Za-z]$', stripped, re.IGNORECASE):
            return False

        if len(stripped) > 140:
            return False

        noise_words = (
            "Open Execution",
            "Open Execut",
            "Add Component",
            "Perspective",
            "Inspector",
            "Hierarchy",
            "Project",
            "Console",
            "Scene",
            "Transform ",
            "New Layer",
            "Layout",
            "Navigation",
            "Regenerated",
        )
        if any(word.lower() in stripped.lower() for word in noise_words):
            return False

        if re.match(r'^\s*(?:if|for|foreach|while|switch)\b', stripped, re.IGNORECASE):
            if not re.match(r'^\s*(?:if|for|foreach|while|switch)\s*\(.+\)\s*$', stripped, re.IGNORECASE):
                return False

        if re.match(r'^\s*case\b', stripped, re.IGNORECASE):
            if not re.match(r'^\s*case\s+.+:\s*$', stripped, re.IGNORECASE):
                return False

        if re.match(r'^\s*new\b', stripped, re.IGNORECASE):
            if not re.match(r'^\s*new\s+[A-Za-z_][A-Za-z0-9_<>]*\s*\(.*\)\s*;?$', stripped):
                return False

        if stripped.startswith("[") and not re.match(
            r'^\[[A-Za-z_][A-Za-z0-9_]*(?:\(.*\))?\]$',
            stripped,
        ):
            return False

        if "..." in stripped:
            return False
        if re.search(r'\b(?:Mono|Hono|Nono|Monoie|Honolie)behaviour\s+On', stripped, re.IGNORECASE):
            return False
        if re.search(r'\bon[A-Z][A-Za-z]+\b', stripped) and '[' in stripped:
            return False

        non_ascii_count = sum(1 for c in stripped if ord(c) > 127)
        if len(stripped) > 8 and non_ascii_count / len(stripped) > 0.12:
            return False

        letters = re.findall(r'[A-Za-z]', stripped)
        if letters:
            upper_ratio = sum(1 for c in letters if c.isupper()) / len(letters)
            if len(letters) > 12 and upper_ratio > 0.85:
                return False

        class_match = re.search(
            r'\bclass\s+([A-Za-z_][A-Za-z0-9_]*)',
            stripped,
            re.IGNORECASE,
        )
        if class_match and not self._valid_identifier(class_match.group(1)):
            return False

        if re.search(r'\b\w+\.cs\b', stripped, re.IGNORECASE):
            return False

        access_match = re.match(
            r'^\s*(public|private|protected|internal)\b',
            stripped,
            re.IGNORECASE,
        )
        if access_match and not self._is_valid_access_declaration(stripped):
            return False

        assignment_match = re.match(
            r'^\s*([A-Za-z_][A-Za-z0-9_.]*)\s*=',
            stripped,
        )
        if assignment_match:
            lhs = assignment_match.group(1)
            if len(lhs.replace(".", "")) < 3:
                return False
            if ';' not in stripped:
                return False

        code_patterns = [
            r'^\s*(?:using|namespace|return|break|continue|else)\b',
            r'^\s*case\s+.+:\s*$',
            r'^\s*new\s+[A-Za-z_][A-Za-z0-9_<>]*\s*\(.*\)\s*;?$',
            r'^\s*\[[A-Za-z_][A-Za-z0-9_]*\(',
            r'^\s*[A-Za-z_][A-Za-z0-9_<>.\[\]]+\s+[A-Za-z_][A-Za-z0-9_]*\s*[;=]',
            r'^\s*[A-Za-z_][A-Za-z0-9_.]*\s*=',
            r'^\s*[A-Za-z_][A-Za-z0-9_.]*\s*\([^)]*\)\s*;',
            r'^\s*[A-Za-z_][A-Za-z0-9_.]*\.[A-Za-z_][A-Za-z0-9_]*\s*\(',
            r'^\s*(?:if|else if|for|foreach|while|switch)\s*\(',
        ]
        return any(re.search(pattern, stripped, re.IGNORECASE)
                   for pattern in code_patterns)

    def _is_valid_access_declaration(self, line: str) -> bool:
        type_pattern = (
            r'(?:int|float|bool|string|double|var|Vector[234]|Quaternion|'
            r'Rigidbody|Transform|GameObject|Text|Image|Slider|Animator|'
            r'LayerMask|Collider|Collision|RaycastHit|AudioSource|Camera|'
            r'[A-Z][A-Za-z0-9_<>.\[\]]*)'
        )
        patterns = [
            r'^\s*(?:public|private|protected|internal)\s+class\s+[A-Za-z_][A-Za-z0-9_]*(?:\s*:\s*[A-Za-z_][A-Za-z0-9_]*)?\s*$',
            rf'^\s*(?:public|private|protected|internal)\s+(?:static\s+)?(?:void|bool|int|float|string|double|{type_pattern})\s+[A-Za-z_][A-Za-z0-9_]*\s*\([^)]*\)\s*$',
            rf'^\s*(?:public|private|protected|internal)\s+(?:static\s+)?{type_pattern}\s+[A-Za-z_][A-Za-z0-9_]*(?:\s*[;=].*)?$',
        ]
        return any(re.match(pattern, line, re.IGNORECASE) for pattern in patterns)

    def _valid_identifier(self, name: str) -> bool:
        if len(name) < 3 or len(name) > 48:
            return False
        letters = re.findall(r'[A-Za-z]', name)
        if letters:
            upper_ratio = sum(1 for c in letters if c.isupper()) / len(letters)
            if len(letters) > 10 and upper_ratio > 0.75:
                return False
        return True
