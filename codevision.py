#!/usr/bin/env python3
"""
CodeVision Extractor v2.0 — CLI Entry Point

Video-to-Code Reconstruction Engine.
Extracts C# source code from programming tutorial videos using
FFmpeg (frame extraction) and Tesseract OCR (text recognition),
then reconstructs clean, deduplicated scripts with full build history.

Usage:
    python codevision.py --file "path/to/video.mp4"
    python codevision.py --folder "path/to/videos/"
    python codevision.py --folder "." --interval 5 --output "./output"

Author: Eng. Ibrahim Anas Al-Azzani
        CyberPro for Technical & Engineering Works
"""

import sys
import os
import argparse
import shutil
from pathlib import Path
from datetime import datetime

# Configure UTF-8 for Windows console output
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        pass

# Add project root to path for package imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.banner import print_banner, print_interactive_menu
from utils.logger import Logger
from utils.validator import InputValidator
from extraction.ffmpeg_extractor import FFmpegExtractor
from ocr.tesseract_engine import TesseractEngine
from reconstruction.script_builder import ScriptBuilder
from core.models import VideoFile, ExtractionReport
from core.exceptions import CodeVisionError


log = Logger()


def find_local_tesseract(script_dir: str):
    """Check for a local portable Tesseract install next to the script."""
    tess_exe = os.path.join(script_dir, "tesseract", "tesseract.exe")
    tess_data = os.path.join(script_dir, "tesseract", "tessdata")
    if os.path.isfile(tess_exe):
        return tess_exe, tess_data
    return None, None


def process_video(video: VideoFile, output_base: Path, interval: int,
                  ffmpeg: FFmpegExtractor, ocr: TesseractEngine,
                  builder: ScriptBuilder) -> ExtractionReport:
    """
    Process a single video through the full extraction pipeline.

    Args:
        video: VideoFile to process.
        output_base: Base output directory.
        interval: Frame extraction interval in seconds.
        ffmpeg: FFmpeg extractor instance.
        ocr: Tesseract OCR engine instance.
        builder: Script reconstruction builder.

    Returns:
        ExtractionReport with results summary.
    """
    report = ExtractionReport(video_name=video.name)

    # Create video-specific output directory
    video_dir = output_base / video.name
    frames_dir = video_dir / "Frames"
    cand_dir = video_dir / "CandidateFrames"
    ocr_dir = video_dir / "OCR"

    # ── Step 1: Extract Frames ───────────────────────────────────
    log.step(f"Extracting frames (1 every {interval}s)...")
    frames = ffmpeg.extract_frames(video.path, frames_dir, interval)
    report.total_frames = len(frames)
    log.step(f"Frames extracted: {len(frames)}")

    if not frames:
        log.warn("No frames extracted. Skipping video.")
        return report

    # ── Step 2: OCR Processing ───────────────────────────────────
    log.step("Running OCR on frames...")
    ocr_results = []
    cand_dir.mkdir(parents=True, exist_ok=True)

    for i, frame in enumerate(frames):
        result = ocr.process_frame(frame, ocr_dir)
        ocr_results.append(result)

        # Copy candidate frames for visual reference
        if result.is_code:
            report.candidate_frames += 1
            try:
                shutil.copy2(str(frame.image_path), str(cand_dir))
            except Exception:
                pass

        # Show progress every 20 frames
        if (i + 1) % 20 == 0 or (i + 1) == len(frames):
            log.progress(i + 1, len(frames),
                         f"OCR: {i+1}/{len(frames)} frames | "
                         f"Code candidates: {report.candidate_frames}")

    log.step(f"Candidate code frames: {report.candidate_frames}")

    # ── Step 3: Code Reconstruction ──────────────────────────────
    if report.candidate_frames > 0:
        log.step("Reconstructing C# scripts...")
        script = builder.reconstruct(ocr_results)

        if script.final_lines:
            script.source_video = video.name
            builder.export(script, video_dir, video.name)
            report.scripts_found.append(f"{script.class_name}.cs")
            log.step(f"Script reconstructed: {script.class_name}.cs "
                     f"({len(script.history)} snapshots)")
        else:
            log.warn("No code lines survived the cleaning pipeline.")
    else:
        log.warn("No code frames detected in this video.")

    # ── Step 4: Cleanup temp frames ──────────────────────────────
    try:
        shutil.rmtree(str(frames_dir), ignore_errors=True)
    except Exception:
        pass

    # ── Step 5: Generate Report ──────────────────────────────────
    report.output_dir = str(video_dir)
    report_path = video_dir / "REPORT.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("CODEVISION EXTRACTOR — VIDEO REPORT\n")
        f.write("=" * 50 + "\n")
        f.write(f"Video: {video.name}\n")
        f.write(f"Path: {video.path}\n")
        f.write(f"Interval: {interval}s\n")
        f.write(f"Total frames: {report.total_frames}\n")
        f.write(f"Code candidate frames: {report.candidate_frames}\n")
        f.write(f"Scripts found: {', '.join(report.scripts_found) or 'None'}\n")
        f.write(f"Output: {video_dir}\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("\nWARNING: OCR may confuse ; : . , {{ }} ( ) and identifiers.\n")
        f.write("Review reconstructed scripts before compiling.\n")

    return report


def main():
    """Main CLI entry point."""

    # ── Parse Arguments ──────────────────────────────────────────
    parser = argparse.ArgumentParser(
        prog="codevision",
        description="CodeVision Extractor v2.0 — Extract C# code from tutorial videos.",
        epilog="CyberPro for Technical & Engineering Works | Eng. Ibrahim Anas Al-Azzani"
    )

    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument(
        "--file", "-f",
        type=str,
        help="Path to a single video file to process."
    )
    group.add_argument(
        "--folder", "-d",
        type=str,
        help="Path to a folder containing video files."
    )

    parser.add_argument(
        "--output", "-o",
        type=str,
        default="./_CodeVision_Output",
        help="Output directory (default: ./_CodeVision_Output)"
    )
    parser.add_argument(
        "--interval", "-i",
        type=int,
        default=3,
        help="Frame extraction interval in seconds (default: 3)"
    )
    parser.add_argument(
        "--ffmpeg-path",
        type=str,
        default=None,
        help="Custom path to FFmpeg binary."
    )
    parser.add_argument(
        "--tesseract-path",
        type=str,
        default=None,
        help="Custom path to Tesseract binary."
    )

    args = parser.parse_args()

    # ── Interactive Mode if no arguments provided ─────────────────
    if not args.file and not args.folder:
        print_banner(animated=True)
        print_interactive_menu()

        try:
            choice = input("\033[96m[➔] Enter your choice (1 or 2): \033[0m").strip()
            if choice == "1":
                raw_path = input("\n\033[92m[➔] Enter video file path (or drag & drop video file here): \033[0m").strip().strip('"\'')
                args.file = raw_path
            elif choice == "2":
                raw_path = input("\n\033[92m[➔] Enter folder path (or drag & drop folder here): \033[0m").strip().strip('"\'')
                args.folder = raw_path
            else:
                log.error("Invalid choice. Exiting.")
                sys.exit(1)
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            sys.exit(0)
    else:
        # Print banner for CLI flag invocation
        print_banner(animated=False)

    # ── Validate Dependencies ────────────────────────────────────
    script_dir = os.path.dirname(os.path.abspath(__file__))

    ffmpeg = FFmpegExtractor(custom_path=args.ffmpeg_path)
    if not ffmpeg.is_available():
        log.error("FFmpeg not found!")
        log.step("Install FFmpeg: https://ffmpeg.org/download.html")
        log.step("Or specify path: --ffmpeg-path \"C:\\path\\to\\ffmpeg.exe\"")
        sys.exit(1)
    log.info(f"FFmpeg: {ffmpeg.get_binary_path()}")

    # Check for local portable Tesseract first
    tess_path = args.tesseract_path
    tess_data = None
    if not tess_path:
        tess_path, tess_data = find_local_tesseract(script_dir)

    ocr = TesseractEngine(custom_path=tess_path, tessdata_dir=tess_data)
    if not ocr.is_available():
        log.error("Tesseract OCR not found!")
        log.step("Install: https://github.com/UB-Mannheim/tesseract/wiki")
        log.step("Or place portable Tesseract in: ./tesseract/")
        log.step("Or specify path: --tesseract-path \"C:\\path\\to\\tesseract.exe\"")
        sys.exit(1)
    log.info(f"Tesseract: {ocr.get_binary_path()}")

    # ── Validate Input ───────────────────────────────────────────
    validator = InputValidator()

    try:
        if args.file:
            videos = [validator.validate_file(args.file)]
        else:
            videos = validator.validate_folder(args.folder)
    except CodeVisionError as e:
        log.error(str(e))
        sys.exit(1)

    log.info(f"Videos to process: {len(videos)}")

    # ── Process Videos ───────────────────────────────────────────
    output_base = Path(args.output).resolve()
    output_base.mkdir(parents=True, exist_ok=True)

    builder = ScriptBuilder()
    all_reports = []

    for idx, video in enumerate(videos, 1):
        log.header(f"[{idx}/{len(videos)}] {video.name}")
        try:
            report = process_video(
                video, output_base, args.interval,
                ffmpeg, ocr, builder
            )
            all_reports.append(report)
        except Exception as e:
            log.error(f"Failed to process {video.name}: {e}")
            continue

    # ── Summary ──────────────────────────────────────────────────
    total_scripts = sum(len(r.scripts_found) for r in all_reports)
    total_candidates = sum(r.candidate_frames for r in all_reports)

    log.success("ALL VIDEOS PROCESSED SUCCESSFULLY")
    log.info(f"Videos processed: {len(all_reports)}")
    log.info(f"Total code frames detected: {total_candidates}")
    log.info(f"Total scripts reconstructed: {total_scripts}")
    log.info(f"Output directory: {output_base}")

    # ── Master Report CSV ────────────────────────────────────────
    csv_path = output_base / "MASTER_REPORT.csv"
    with open(csv_path, 'w', encoding='utf-8') as f:
        f.write("Video,Total Frames,Code Frames,Scripts Found,Output Dir\n")
        for r in all_reports:
            scripts = "; ".join(r.scripts_found) if r.scripts_found else "None"
            f.write(f'"{r.video_name}",{r.total_frames},'
                    f'{r.candidate_frames},"{scripts}","{r.output_dir}"\n')

    log.info(f"Master report: {csv_path}")


if __name__ == "__main__":
    main()
