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

        if len(master) > 200:
            return self._merge_fast(master, new_lines)

        merged = []
        sm = difflib.SequenceMatcher(None, master, new_lines)

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

    def _merge_fast(self, master: List[str], new_lines: List[str]) -> List[str]:
        merged = list(master)
        by_key = {}
        exact = set()

        for index, line in enumerate(merged):
            stripped = line.strip()
            if stripped and stripped not in ('{', '}'):
                exact.add(stripped)
                by_key.setdefault(self._line_key(stripped), index)

        appended_code = False
        for line in new_lines:
            stripped = line.strip()
            if not stripped:
                continue

            if stripped in ('{', '}'):
                if appended_code and (not merged or merged[-1].strip() != stripped):
                    merged.append(line)
                continue

            key = self._line_key(stripped)
            existing_index = by_key.get(key)
            if existing_index is not None:
                old = merged[existing_index].strip()
                if len(stripped) > len(old) + 4:
                    merged[existing_index] = line
                    exact.discard(old)
                    exact.add(stripped)
                appended_code = False
                continue

            if stripped not in exact:
                by_key[key] = len(merged)
                exact.add(stripped)
                merged.append(line)
                appended_code = True

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

    def _line_key(self, line: str) -> str:
        compact = ''.join(line.split())
        compact = compact.rstrip(';')
        if '=' in compact:
            return compact.split('=', 1)[0].lower()
        if '(' in compact:
            return compact.split('(', 1)[0].lower()
        parts = compact.split()
        if len(parts) >= 2:
            return parts[-1].lower()
        return compact.lower()

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
