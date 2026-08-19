import os
import sys
import re
import glob
import difflib
from pathlib import Path

# Common OCR typo corrections in C#/Unity context
OCR_CORRECTIONS = [
    (r'Unityéngine', 'UnityEngine'),
    (r'Unityengine', 'UnityEngine'),
    (r'MonoBchaviour', 'MonoBehaviour'),
    (r'Monofehaviour', 'MonoBehaviour'),
    (r'NonoBehaviour', 'MonoBehaviour'),
    (r'Honodchaviour', 'MonoBehaviour'),
    (r'System\.Ccollections', 'System.Collections'),
    (r'System\.collections', 'System.Collections'),
    (r'\[f[a-z]*Header\(', '[Header('),
    (r'\[fleader\(', '[Header('),
    (r'\[fileader\(', '[Header('),
    (r'GaneObject', 'GameObject'),
    (r'pistolGamedbject', 'pistolGameObject'),
    (r'pistolGamedbjectPrefab', 'pistolGameObjectPrefab'),
    (r'akmGamedbjectPrefab', 'akmGameObjectPrefab'),
    (r'm416GamedbjectPrefab', 'm416GameObjectPrefab'),
    (r'pistorrrefab', 'pistolPrefab'),
    (r'pistorPrefab', 'pistolPrefab'),
    (r'mai6Prefab', 'm416Prefab'),
    (r'm4iepbjectPrefab', 'm416GameObjectPrefab'),
    (r'riflelactive', 'rifle1Active'),
    (r'riflezactive', 'rifle2Active'),
    (r'riflezActive', 'rifle2Active'),
    (r'riflesactive', 'rifle3Active'),
    (r'rifle3active', 'rifle3Active'),
    (r'riflelaActive', 'rifle1Active'),
    (r'niflgaActive', 'rifle1Active'),
    (r'mifleaActivel', 'rifle2Active'),
    (r'\[Header\("Player Money and kills"\)/\]\]', '[Header("Player Money and Kills")]'),
]

# Patterns for IDE UI noise to ignore
UI_NOISE_PATTERNS = [
    r'^.*File\s+Edit.*Selection.*View.*$',
    r'^.*Restricted\s+Mode.*$',
    r'^.*Spaces:\d+.*$',
    r'^.*UTF-8.*CRLF.*$',
    r'^.*OnParticlecollision.*$',
    r'^.*OnApplicationPause.*$',
    r'^.*OnApplicationFocus.*$',
    r'^.*OnPlayerDisconnected.*$',
    r'^.*OnParticleTrigger.*$',
    r'^.*OnPostRender.*$',
    r'^.*OnPreCull.*$',
    r'^.*OnPreRender.*$',
    r'^.*OnRenderObject.*$',
    r'^.*OnAudioFilterRead.*$',
    r'^.*MonoBehaviour\s+On.*$',
    r'^\s*we\s+ee\s+re.*$',
    r'^\s*ere\s+i\}.*$',
    r'^\s*Py\s+oem.*$',
    r'^\s*wy\s+Cee.*$',
    r'^\s*ft\s+\|e\s+artinnesie.*$',
    r'^\s*\(C\)\s+©\s+Gamenanagercs.*$',
    r'^\s*﻿?>\s+file\s+Edit.*$',
]

def clean_line(line):
    # Check if line matches UI noise
    for pat in UI_NOISE_PATTERNS:
        if re.search(pat, line, re.IGNORECASE):
            return None
            
    # Remove random non-code prefix characters (e.g. "o aa public...", "Fey public...", "Sb 6")
    line_clean = re.sub(r'^\s*[\W_a-z]{1,4}\s+(?=(using|public|private|protected|class|void|bool|int|float|string|\[Header|override))', '', line, flags=re.IGNORECASE)
    
    # Strip line numbers at beginning of lines like "p 1 using...", "12 public bool...", "2 7 [Header..."
    line_clean = re.sub(r'^\s*(?:[a-z]{1,2}\s+)?(?:\d+\s+)+', '', line_clean)
    line_clean = re.sub(r'^\s*\d+\s+', '', line_clean)
    line_clean = line_clean.strip()
    
    # Remove trailing cursor / IDE status characters like "|", "I", "3", "w", "@", "fod"
    line_clean = re.sub(r'\s*[|I@]\s*$', '', line_clean)
    line_clean = re.sub(r'\s+fod$', '', line_clean)
    
    if not line_clean or len(line_clean) < 2:
        return None
        
    # Re-check noise on cleaned line
    for pat in UI_NOISE_PATTERNS:
        if re.search(pat, line_clean, re.IGNORECASE):
            return None

    # Apply OCR replacements
    for typo, fix in OCR_CORRECTIONS:
        line_clean = re.sub(typo, fix, line_clean, flags=re.IGNORECASE)
        
    return line_clean

def extract_class_name(lines):
    for line in lines:
        match = re.search(r'class\s+([A-Za-z0-9_]+)', line)
        if match:
            return match.group(1)
    return "ExtractedScript"

def clean_ocr_file(filepath):
    cleaned_lines = []
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        for raw_line in f:
            cleaned = clean_line(raw_line)
            if cleaned:
                # Avoid duplicate adjacent lines in same frame
                if not cleaned_lines or cleaned_lines[-1] != cleaned:
                    cleaned_lines.append(cleaned)
    return cleaned_lines

def merge_code_snapshots(frames_lines):
    """
    Combines lines across chronologically ordered frames.
    Keeps unique code structure while expanding code as new lines are added.
    """
    master_lines = []
    
    for frame_idx, lines in frames_lines:
        if not lines:
            continue
            
        if not master_lines:
            master_lines = list(lines)
            continue
            
        # Sequence matcher to align lines
        sm = difflib.SequenceMatcher(None, master_lines, lines)
        opcodes = sm.get_opcodes()
        
        new_master = []
        for tag, i1, i2, j1, j2 in opcodes:
            if tag == 'equal':
                new_master.extend(master_lines[i1:i2])
            elif tag == 'insert':
                new_master.extend(lines[j1:j2])
            elif tag == 'replace':
                # Prefer lines with better syntax indicators (like semicolons, braces, valid C# keywords)
                orig_block = master_lines[i1:i2]
                new_block = lines[j1:j2]
                
                # Check if new block extends or cleans original block
                orig_str = "\n".join(orig_block)
                new_str = "\n".join(new_block)
                
                if len(new_str) >= len(orig_str) and (';' in new_str or '{' in new_str or '}' in new_str):
                    new_master.extend(new_block)
                else:
                    new_master.extend(orig_block)
            elif tag == 'delete':
                # Keep original lines unless empty/noise
                new_master.extend(master_lines[i1:i2])
                
        master_lines = new_master

    # Final post-processing pass on master_lines
    final_lines = []
    seen = set()
    for l in master_lines:
        # Basic check to avoid identical duplicate lines except closing braces
        if l == '}' or l == '{':
            final_lines.append(l)
        elif l not in seen:
            final_lines.append(l)
            seen.add(l)
            
    return final_lines, master_lines

def process_video_folder(target_dir):
    ocr_dir = os.path.join(target_dir, "OCR")
    if not os.path.exists(ocr_dir):
        print(f"Error: OCR directory not found at {ocr_dir}")
        return

    ocr_files = sorted(glob.glob(os.path.join(ocr_dir, "frame_*.txt")))
    if not ocr_files:
        print(f"No frame_*.txt files found in {ocr_dir}")
        return

    print(f"Processing {len(ocr_files)} OCR text files in {target_dir}...")
    
    frames_data = []
    for fpath in ocr_files:
        fname = os.path.basename(fpath)
        cleaned = clean_ocr_file(fpath)
        if cleaned:
            frames_data.append((fname, cleaned))
            
    if not frames_data:
        print("No valid code lines extracted after denoising.")
        return

    # Detect primary class name
    all_cleaned_sample = [line for _, lines in frames_data for line in lines]
    class_name = extract_class_name(all_cleaned_sample)
    print(f"Detected primary C# Class Name: {class_name}")

    # Build output directories
    scripts_dir = os.path.join(target_dir, "Scripts")
    history_dir = os.path.join(target_dir, "ScriptHistory")
    os.makedirs(scripts_dir, exist_ok=True)
    os.makedirs(history_dir, exist_ok=True)

    # Reconstruct history step-by-step
    cumulative_lines = []
    snapshot_count = 0
    
    for fname, lines in frames_data:
        if not lines:
            continue
            
        if not cumulative_lines:
            cumulative_lines = list(lines)
        else:
            sm = difflib.SequenceMatcher(None, cumulative_lines, lines)
            opcodes = sm.get_opcodes()
            temp_master = []
            for tag, i1, i2, j1, j2 in opcodes:
                if tag == 'equal':
                    temp_master.extend(cumulative_lines[i1:i2])
                elif tag == 'insert':
                    temp_master.extend(lines[j1:j2])
                elif tag == 'replace':
                    # If new line is longer or contains semicolons, update
                    if sum(len(x) for x in lines[j1:j2]) > sum(len(x) for x in cumulative_lines[i1:i2]):
                        temp_master.extend(lines[j1:j2])
                    else:
                        temp_master.extend(cumulative_lines[i1:i2])
                elif tag == 'delete':
                    temp_master.extend(cumulative_lines[i1:i2])
            cumulative_lines = temp_master
            
        snapshot_count += 1
        history_path = os.path.join(history_dir, f"{class_name}_{snapshot_count:03d}.cs")
        with open(history_path, 'w', encoding='utf-8') as hf:
            hf.write(f"// Snapshot {snapshot_count:03d} from {fname}\n")
            hf.write("\n".join(cumulative_lines) + "\n")

    # Clean and finalize master file
    clean_final_lines, _ = merge_code_snapshots([(f, l) for f, l in frames_data])
    
    # Save Final Script
    final_script_path = os.path.join(scripts_dir, f"{class_name}.cs")
    with open(final_script_path, 'w', encoding='utf-8') as sf:
        sf.write(f"// ============================================================\n")
        sf.write(f"// RECONSTRUCTED C# SCRIPT - VERSION 2 ENGINE\n")
        sf.write(f"// Class: {class_name}\n")
        sf.write(f"// Snapshots merged: {snapshot_count}\n")
        sf.write(f"// ============================================================\n\n")
        sf.write("\n".join(clean_final_lines) + "\n")
        
    # Also save FINAL snapshot in ScriptHistory
    final_hist_path = os.path.join(history_dir, f"{class_name}_FINAL.cs")
    with open(final_hist_path, 'w', encoding='utf-8') as fh:
        fh.write(f"// FINAL RECONSTRUCTED CODE FOR {class_name}\n\n")
        fh.write("\n".join(clean_final_lines) + "\n")

    print(f"Reconstruction Complete!")
    print(f"Final Clean Script: {final_script_path}")
    print(f"Script History: {history_dir} ({snapshot_count} snapshots + FINAL)")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        target = r"d:\Programming\New folder\Mobile Game Development Tutorial 2025\Test_Video_26\_Extracted_CSharp\26 - Unity Shop System Tutorial Mobile Game Development Full Course GTA Vice City Game Clone(720P_60FPS)"
    process_video_folder(target)
