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

        sm = difflib.SequenceMatcher(None, master, new_lines)
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

    def deduplicate_final(self, lines: List[str]) -> List[str]:
        """
        Remove exact duplicate lines from the final output,
        while preserving structural duplicates like braces.

        Args:
            lines: All merged code lines.

        Returns:
            Deduplicated line list.
        """
        final = []
        seen = set()

        for line in lines:
            stripped = line.strip()
            # Always allow structural characters
            if stripped in ('{', '}', ''):
                final.append(line)
            elif stripped not in seen:
                final.append(line)
                seen.add(stripped)

        return final
