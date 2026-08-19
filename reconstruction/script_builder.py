"""
Final script assembler and history exporter.

Orchestrates class detection, line merging, and output generation.
Produces:
  - Scripts/<ClassName>.cs          — Final clean reconstructed code.
  - ScriptHistory/<ClassName>_NNN.cs — Chronological build snapshots.
  - ScriptHistory/<ClassName>_FINAL.cs — Copy of final version in history.
"""

import os
from pathlib import Path
from typing import List
from datetime import datetime

from core.models import OcrResult, CodeSnapshot, ReconstructedScript
from core.interfaces import ICodeReconstructor
from reconstruction.class_detector import ClassDetector
from reconstruction.line_merger import LineMerger


class ScriptBuilder(ICodeReconstructor):
    """Builds reconstructed C# scripts from chronological OCR results."""

    def __init__(self):
        self._detector = ClassDetector()
        self._merger = LineMerger()

    def reconstruct(self, ocr_results: List[OcrResult]) -> ReconstructedScript:
        """
        Reconstruct a clean C# script from chronological OCR results.

        Args:
            ocr_results: Time-ordered list of OcrResult objects.

        Returns:
            ReconstructedScript with final code and history snapshots.
        """
        # Filter to only code-candidate frames with content
        code_frames = [
            r for r in ocr_results
            if r.is_code and r.cleaned_lines
        ]

        if not code_frames:
            return ReconstructedScript(class_name="ExtractedScript")

        # Detect class name from all cleaned lines
        all_lines = [line for r in code_frames for line in r.cleaned_lines]
        class_name = self._detector.detect_class_name(all_lines)

        # Build history snapshots incrementally
        history: List[CodeSnapshot] = []
        cumulative: List[str] = []
        snapshot_idx = 0

        for result in code_frames:
            cumulative = self._merger.merge_incremental(
                cumulative, result.cleaned_lines
            )
            snapshot_idx += 1
            history.append(CodeSnapshot(
                index=snapshot_idx,
                source_frame=result.frame.image_path.stem,
                lines=list(cumulative),
            ))

        # Final deduplication pass
        final_lines = self._merger.deduplicate_final(cumulative)

        return ReconstructedScript(
            class_name=class_name,
            final_lines=final_lines,
            history=history,
        )

    def export(self, script: ReconstructedScript, output_dir: Path,
               video_name: str = "") -> None:
        """
        Write the reconstructed script and history to disk.

        Args:
            script: The reconstructed script to export.
            output_dir: Base output directory for this video.
            video_name: Name of the source video (for header comment).
        """
        scripts_dir = output_dir / "Scripts"
        history_dir = output_dir / "ScriptHistory"
        scripts_dir.mkdir(parents=True, exist_ok=True)
        history_dir.mkdir(parents=True, exist_ok=True)

        cn = script.class_name
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # ── Write final clean script ─────────────────────────────────
        header = [
            "// ============================================================",
            "// RECONSTRUCTED C# SCRIPT — CodeVision Extractor v2.0",
            f"// Class: {cn}",
            f"// Source: {video_name}" if video_name else "",
            f"// Generated: {now}",
            f"// Snapshots merged: {len(script.history)}",
            "// CyberPro for Technical & Engineering Works",
            "// Eng. Ibrahim Anas Al-Azzani",
            "// ============================================================",
            "",
        ]
        header = [h for h in header if h or h == ""]

        final_path = scripts_dir / f"{cn}.cs"
        with open(final_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(header))
            f.write("\n".join(script.final_lines))
            f.write("\n")

        # ── Write history snapshots ──────────────────────────────────
        for snapshot in script.history:
            snap_path = history_dir / f"{cn}_{snapshot.index:03d}.cs"
            with open(snap_path, 'w', encoding='utf-8') as f:
                f.write(f"// Snapshot {snapshot.index:03d} from {snapshot.source_frame}\n")
                f.write("\n".join(snapshot.lines))
                f.write("\n")

        # ── Write FINAL copy in history ──────────────────────────────
        final_hist = history_dir / f"{cn}_FINAL.cs"
        with open(final_hist, 'w', encoding='utf-8') as f:
            f.write(f"// FINAL RECONSTRUCTED CODE FOR {cn}\n")
            f.write(f"// Generated: {now}\n\n")
            f.write("\n".join(script.final_lines))
            f.write("\n")
