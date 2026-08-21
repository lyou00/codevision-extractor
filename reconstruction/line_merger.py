"""
Chronological line differ and incremental merger.

Uses Python's difflib.SequenceMatcher to align code across consecutive
video frames and merge only new/changed lines, preventing duplication.
"""

import difflib
from typing import List, Tuple


class LineMerger:
    """Merges code lines chronologically across multiple video frames."""

    def merge_incremental(self, master: List[str],
                          new_lines: List[str]) -> List[str]:
        """
        Merge new_lines into the existing master code, keeping new additions
        and preferring longer/more complete lines on replacements.

        Args:
            master: Current accumulated code lines.
            new_lines: Cleaned code lines from the next frame.

        Returns:
            Updated master lines with new content merged in.
        """
        if not master:
            return list(new_lines)
        if not new_lines:
            return list(master)

        master_meaningful = {
            line.strip() for line in master
            if self._is_meaningful_line(line)
        }
        new_meaningful = {
            line.strip() for line in new_lines
            if self._is_meaningful_line(line)
        }
        if new_meaningful and not (master_meaningful & new_meaningful):
            return self._append_unseen(master, new_lines)

        sm = difflib.SequenceMatcher(None, master, new_lines)
        if sm.ratio() < 0.25:
            return self._append_unseen(master, new_lines)

        merged = []

        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == 'equal':
                merged.extend(master[i1:i2])
            elif tag == 'insert':
                merged.extend(new_lines[j1:j2])
            elif tag == 'replace':
                orig = master[i1:i2]
                new = new_lines[j1:j2]
                # Prefer the block with more content / better syntax
                orig_len = sum(len(x) for x in orig)
                new_len = sum(len(x) for x in new)
                new_has_syntax = any(
                    c in "\n".join(new) for c in ";{}"
                )
                if new_len >= orig_len and new_has_syntax:
                    merged.extend(new)
                else:
                    merged.extend(orig)
            elif tag == 'delete':
                merged.extend(master[i1:i2])

        return merged

    def _append_unseen(self, master: List[str],
                       new_lines: List[str]) -> List[str]:
        merged = list(master)
        existing = {line.strip() for line in master if line.strip()}
        for line in new_lines:
            stripped = line.strip()
            if stripped in ('{', '}', '') or stripped not in existing:
                merged.append(line)
                if stripped:
                    existing.add(stripped)
        return merged

    def _is_meaningful_line(self, line: str) -> bool:
        stripped = line.strip()
        return len(stripped) > 2 and stripped not in ('{', '}')

    def deduplicate_final(self, lines: List[str]) -> List[str]:
        """
        Remove only accidental adjacent duplicates and repeated using lines.

        Code can legitimately repeat statements like SetActive(false), so a
        global "seen line" pass can delete real code from later methods.
        """
        final = []
        seen_usings = set()
        previous = None

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("using "):
                if stripped in seen_usings:
                    continue
                seen_usings.add(stripped)

            if stripped and stripped == previous:
                continue

            final.append(line)
            previous = stripped

        return final
