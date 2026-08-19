"""
Ultra-Clean, Sleek & Modern Terminal Banner for CodeVision Extractor v2.0.

Designed for perfect rendering on any terminal window size (PowerShell, CMD, Bash).
Branded for Eng. Ibrahim Anas Al-Azzani | CyberPro for Technical & Engineering Works.
"""

import sys
import time

def print_banner(animated: bool = False):
    """Print a clean, professional, non-wrapping banner."""

    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

    banner_lines = [
        f"{CYAN}┌───────────────────────────────────────────────────────────────────────────┐{RESET}",
        f"{CYAN}│{RESET}  {WHITE}{BOLD}⚡ CODEVISION EXTRACTOR v2.0{RESET}                                          {CYAN}│{RESET}",
        f"{CYAN}│{RESET}  {YELLOW}Universal Video-to-Code Reconstruction Engine{RESET}                          {CYAN}│{RESET}",
        f"{CYAN}├───────────────────────────────────────────────────────────────────────────┤{RESET}",
        f"{CYAN}│{RESET}  {GRAY}• Engine{RESET}      : {GREEN}100% Offline Processing (FFmpeg + Tesseract OCR){RESET}       {CYAN}│{RESET}",
        f"{CYAN}│{RESET}  {GRAY}• Author{RESET}      : {WHITE}{BOLD}Eng. Ibrahim Anas Al-Azzani{RESET}                         {CYAN}│{RESET}",
        f"{CYAN}│{RESET}  {GRAY}• Enterprise{RESET}  : {CYAN}CyberPro for Technical & Engineering Works{RESET}              {CYAN}│{RESET}",
        f"{CYAN}│{RESET}  {GRAY}• Contact{RESET}     : {YELLOW}+967 773 256 961{RESET}                                        {CYAN}│{RESET}",
        f"{CYAN}└───────────────────────────────────────────────────────────────────────────┘{RESET}",
    ]

    for line in banner_lines:
        print(line)
        if animated:
            sys.stdout.flush()
            time.sleep(0.01)
    print()


def print_interactive_menu():
    """Print clean interactive input prompt."""
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

    print(f"{CYAN}🎯 SELECT INPUT MODE:{RESET}")
    print(f"   {GREEN}{BOLD}[ 1 ]{RESET} {WHITE}Process Single Video File{RESET}")
    print(f"   {GREEN}{BOLD}[ 2 ]{RESET} {WHITE}Process Entire Video Folder (Batch Course Extraction){RESET}")
    print()
