"""
Final script assembler and history exporter.

The builder keeps a project-wide class map while videos are processed in
chronological order. If a later lesson reopens PlayerController.cs, the new
frames update the same reconstructed class instead of creating an isolated
per-video result.
"""

from pathlib import Path
from typing import Dict, List, Set
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
        self._project_lines: Dict[str, List[str]] = {}
        self._project_history: Dict[str, List[CodeSnapshot]] = {}
        self._current_class = ""

    def reconstruct(self, ocr_results: List[OcrResult]) -> ReconstructedScript:
        """
        Reconstruct the primary script from a video.

        This method is kept for compatibility. New code should use
        reconstruct_many() so class switches inside one video are preserved.
        """
        scripts = self.reconstruct_many(ocr_results)
        if scripts:
            return scripts[0]
        return ReconstructedScript(class_name="ExtractedScript")

    def reconstruct_many(self, ocr_results: List[OcrResult],
                         video_name: str = "") -> List[ReconstructedScript]:
        """
        Merge all visible scripts from one video into the project state.

        Returns only classes touched by this video, while get_project_scripts()
        returns the full accumulated codebase.
        """
        code_frames = [
            r for r in ocr_results
            if r.is_code and r.cleaned_lines
        ]

        if not code_frames:
            return []

        all_lines = [line for r in code_frames for line in r.cleaned_lines]
        fallback_class = self._detector.detect_class_name(all_lines)
        if fallback_class == "ExtractedScript" and self._current_class:
            fallback_class = self._current_class

        touched: Set[str] = set()

        for result in code_frames:
            class_name = self._detector.detect_frame_class(
                result.cleaned_lines,
                result.raw_text,
            )
            if not class_name:
                class_name = fallback_class
            if not class_name or class_name == "ExtractedScript":
                class_name = self._current_class or "ExtractedScript"

            self._current_class = class_name
            touched.add(class_name)

            current_lines = self._project_lines.get(class_name, [])
            merged = self._merger.merge_incremental(
                current_lines,
                result.cleaned_lines,
            )
            self._project_lines[class_name] = merged

            history = self._project_history.setdefault(class_name, [])
            history.append(CodeSnapshot(
                index=len(history) + 1,
                source_frame=self._format_source_frame(result, video_name),
                lines=list(merged),
            ))

        return [
            self._make_script(class_name)
            for class_name in sorted(touched)
            if self._project_lines.get(class_name)
        ]

    def get_project_scripts(self) -> List[ReconstructedScript]:
        """Return final scripts for every class seen in the whole run."""
        return [
            self._make_script(class_name)
            for class_name in sorted(self._project_lines)
            if self._project_lines[class_name]
        ]

    def export(self, script: ReconstructedScript, output_dir: Path,
               video_name: str = "") -> None:
        """
        Write one reconstructed script and its class history to disk.
        """
        scripts_dir = output_dir / "Scripts"
        history_dir = output_dir / "ScriptHistory"
        scripts_dir.mkdir(parents=True, exist_ok=True)
        history_dir.mkdir(parents=True, exist_ok=True)

        self._write_script(script, scripts_dir, video_name)
        self._write_history(script, history_dir)

    def export_project(self, output_dir: Path) -> None:
        """
        Write the final accumulated codebase across all processed videos.
        """
        scripts = self.get_project_scripts()
        project_scripts_dir = output_dir / "ProjectScripts"
        project_history_dir = output_dir / "ProjectHistory"
        project_scripts_dir.mkdir(parents=True, exist_ok=True)
        project_history_dir.mkdir(parents=True, exist_ok=True)

        for script in scripts:
            self._write_script(script, project_scripts_dir, "ALL_VIDEOS")
            self._write_history(script, project_history_dir)

        index_path = output_dir / "PROJECT_INDEX.md"
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(index_path, "w", encoding="utf-8") as f:
            f.write("# CodeVision Project Index\n\n")
            f.write(f"Generated: {now}\n\n")
            f.write("| Class | Final file | Snapshots |\n")
            f.write("|---|---:|---:|\n")
            for script in scripts:
                f.write(
                    f"| {script.class_name} | "
                    f"ProjectScripts/{script.class_name}.cs | "
                    f"{len(script.history)} |\n"
                )

    def _make_script(self, class_name: str) -> ReconstructedScript:
        final_lines = self._merger.deduplicate_final(
            self._project_lines.get(class_name, [])
        )
        return ReconstructedScript(
            class_name=class_name,
            final_lines=final_lines,
            history=list(self._project_history.get(class_name, [])),
        )

    def _format_source_frame(self, result: OcrResult, video_name: str) -> str:
        frame_name = result.frame.image_path.stem
        if video_name:
            return f"{video_name}/{frame_name}"
        return frame_name

    def _write_script(self, script: ReconstructedScript, output_dir: Path,
                      source_name: str = "") -> None:
        cn = script.class_name
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        header = [
            "// ============================================================",
            "// RECONSTRUCTED C# SCRIPT - CodeVision Extractor v2.1",
            f"// Class: {cn}",
            f"// Source: {source_name}" if source_name else "",
            f"// Generated: {now}",
            f"// Snapshots merged: {len(script.history)}",
            "// CyberPro for Technical & Engineering Works",
            "// Eng. Ibrahim Anas Al-Azzani",
            "// ============================================================",
            "",
        ]

        final_path = output_dir / f"{cn}.cs"
        with open(final_path, "w", encoding="utf-8") as f:
            f.write("\n".join(h for h in header if h or h == ""))
            f.write("\n".join(script.final_lines))
            f.write("\n")

    def _write_history(self, script: ReconstructedScript,
                       output_dir: Path) -> None:
        cn = script.class_name
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for snapshot in script.history:
            snap_path = output_dir / f"{cn}_{snapshot.index:03d}.cs"
            with open(snap_path, "w", encoding="utf-8") as f:
                f.write(
                    f"// Snapshot {snapshot.index:03d} "
                    f"from {snapshot.source_frame}\n"
                )
                f.write("\n".join(snapshot.lines))
                f.write("\n")

        final_hist = output_dir / f"{cn}_FINAL.cs"
        with open(final_hist, "w", encoding="utf-8") as f:
            f.write(f"// FINAL RECONSTRUCTED CODE FOR {cn}\n")
            f.write(f"// Generated: {now}\n\n")
            f.write("\n".join(script.final_lines))
            f.write("\n")
