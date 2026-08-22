#!/usr/bin/env python3
"""
Rebuild final project scripts from existing CodeVision OCR outputs.

This skips FFmpeg and Tesseract, reuses OCR/*.txt files already generated,
then applies the latest cleaning, class normalization, and project merge logic.
"""

import argparse
import re
from pathlib import Path
from typing import List

from core.models import ExtractedFrame, OcrResult
from ocr.noise_filter import NoiseFilter
from reconstruction.script_builder import ScriptBuilder


def natural_key(path: Path):
    parts = re.split(r'(\d+)', path.name)
    return [int(part) if part.isdigit() else part.lower() for part in parts]


def load_video_ocr(video_dir: Path, noise_filter: NoiseFilter) -> List[OcrResult]:
    ocr_dir = video_dir / "OCR"
    if not ocr_dir.is_dir():
        return []

    results = []
    for txt_path in sorted(ocr_dir.glob("*.txt"), key=natural_key):
        raw_text = txt_path.read_text(encoding="utf-8", errors="ignore")
        cleaned = noise_filter.clean_frame_text(raw_text)
        frame = ExtractedFrame(
            image_path=txt_path.with_suffix(".png"),
            frame_index=len(results) + 1,
        )
        results.append(OcrResult(
            frame=frame,
            raw_text=raw_text,
            cleaned_lines=cleaned,
            is_code=bool(cleaned),
        ))

    return results


def rebuild(input_dir: Path, output_dir: Path,
            include_history: bool = True,
            limit: int = 0) -> int:
    noise_filter = NoiseFilter()
    builder = ScriptBuilder()
    video_count = 0

    video_dirs = sorted(
        [p for p in input_dir.iterdir() if p.is_dir()],
        key=natural_key,
    )
    if limit > 0:
        video_dirs = video_dirs[:limit]

    for video_dir in video_dirs:
        results = load_video_ocr(video_dir, noise_filter)
        if not results:
            continue
        builder.reconstruct_many(results, video_dir.name)
        video_count += 1
        if video_count % 5 == 0:
            print(f"Processed {video_count} OCR folders...")

    output_dir.mkdir(parents=True, exist_ok=True)
    builder.export_project(output_dir, include_history=include_history)
    return video_count


def main():
    parser = argparse.ArgumentParser(
        description="Rebuild clean project scripts from existing OCR outputs."
    )
    parser.add_argument(
        "--input",
        default="./_CodeVision_Output",
        help="Existing CodeVision output directory containing video OCR folders.",
    )
    parser.add_argument(
        "--output",
        default="./_CodeVision_Rebuilt",
        help="Directory for rebuilt ProjectScripts and ProjectHistory.",
    )
    parser.add_argument(
        "--scripts-only",
        action="store_true",
        help="Write only final ProjectScripts and PROJECT_INDEX.md.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Only process the first N OCR folders for quick testing.",
    )
    args = parser.parse_args()

    input_dir = Path(args.input).resolve()
    output_dir = Path(args.output).resolve()
    count = rebuild(
        input_dir,
        output_dir,
        include_history=not args.scripts_only,
        limit=args.limit,
    )
    print(f"Rebuilt project scripts from {count} video OCR folders.")
    print(f"Output: {output_dir}")
    print(f"Final scripts: {output_dir / 'ProjectScripts'}")


if __name__ == "__main__":
    main()
