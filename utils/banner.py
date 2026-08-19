"""
Modern Cyberpunk / Matrix Cascading ASCII Art Banner for CodeVision Extractor v2.0.

Provides an impressive, high-impact cyber-security aesthetic when launched in the terminal.
Designed for Eng. Ibrahim Anas Al-Azzani | CyberPro for Technical & Engineering Works.
"""

import sys
import time

def print_banner(animated: bool = True):
    """Print the CodeVision Extractor branded Cyberpunk banner with optional waterfall animation."""

    # ANSI Colors
    NEON_CYAN = "\033[96m"
    NEON_MAGENTA = "\033[95m"
    NEON_GREEN = "\033[92m"
    NEON_YELLOW = "\033[93m"
    BRIGHT_WHITE = "\033[97m"
    DIM_GRAY = "\033[90m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

    lines = [
        f"{DIM_GRAY}⚡ 01000011 01001111 01000100 01000101 01010110 01001001 01010011 01001001 01001111 01001110 ⚡{RESET}",
        f"{NEON_CYAN}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓{RESET}",
        f"{NEON_CYAN}┃{RESET}                                                                                            {NEON_CYAN}┃{RESET}",
        f"{NEON_CYAN}┃{RESET}   {BRIGHT_WHITE}{BOLD} ██████╗ ██████╗ ██████╗ ███████╗██╗   ██╗██╗███████╗██╗  ██╗██╗███████╗███╗   ██╗{RESET}   {NEON_CYAN}┃{RESET}",
        f"{NEON_CYAN}┃{RESET}   {BRIGHT_WHITE}{BOLD}██╔════╝██╔═══██╗██╔══██╗██╔════╝██║   ██║██║██╔════╝██║  ██║██║██╔════╝████╗  ██║{RESET}   {NEON_CYAN}┃{RESET}",
        f"{NEON_CYAN}┃{RESET}   {NEON_CYAN}{BOLD}██║     ██║   ██║██║  ██║█████╗  ██║   ██║██║███████╗███████║██║█████╗  ██╔██╗ ██║{RESET}   {NEON_CYAN}┃{RESET}",
        f"{NEON_CYAN}┃{RESET}   {NEON_CYAN}{BOLD}██║     ██║   ██║██║  ██║██╔══╝  ╚██╗ ██╔╝██║╚════██║██╔══██║██║██╔══╝  ██║╚██╗██║{RESET}   {NEON_CYAN}┃{RESET}",
        f"{NEON_CYAN}┃{RESET}   {NEON_MAGENTA}{BOLD}╚██████╗╚██████╔╝██████╔╝███████╗ ╚████╔╝ ██║███████║██║  ██║██║███████╗██║ ╚████║{RESET}   {NEON_CYAN}┃{RESET}",
        f"{NEON_CYAN}┃{RESET}   {NEON_MAGENTA}{BOLD} ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝  ╚═══╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝╚══════╝╚═╝  ╚═══╝{RESET}   {NEON_CYAN}┃{RESET}",
        f"{NEON_CYAN}┃{RESET}                                                                                            {NEON_CYAN}┃{RESET}",
        f"{NEON_CYAN}┃{RESET}   {NEON_GREEN}{BOLD}⚡ EXTRACTOR v2.0{RESET}  │  {NEON_YELLOW}Universal Multi-Language Video-to-Code Engine{RESET}                   {NEON_CYAN}┃{RESET}",
        f"{NEON_CYAN}┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫{RESET}",
        f"{NEON_CYAN}┃{RESET}   {DIM_GRAY}[ ENGINE ]{RESET}  FFmpeg + Tesseract OCR + Python  │  {NEON_GREEN}100% Local & Offline Processing{RESET}       {NEON_CYAN}┃{RESET}",
        f"{NEON_CYAN}┃{RESET}   {DIM_GRAY}[ AUTHOR ]{RESET}  {BRIGHT_WHITE}{BOLD}Eng. Ibrahim Anas Al-Azzani{RESET}        │  {NEON_CYAN}CyberPro Engineering Works{RESET}           {NEON_CYAN}┃{RESET}",
        f"{NEON_CYAN}┃{RESET}   {DIM_GRAY}[ CONTACT]{RESET}  {NEON_YELLOW}+967 773 256 961{RESET}                           │  {DIM_GRAY}Open-Source Edition v2.0{RESET}             {NEON_CYAN}┃{RESET}",
        f"{NEON_CYAN}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛{RESET}",
    ]

    for line in lines:
        print(line)
        if animated:
            sys.stdout.flush()
            time.sleep(0.018)  # Smooth matrix waterfall effect
    print()


def print_interactive_menu():
    """Print a high-tech glowing menu prompt for interactive mode."""
    NEON_CYAN = "\033[96m"
    NEON_GREEN = "\033[92m"
    BRIGHT_WHITE = "\033[97m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

    menu = f"""
{NEON_CYAN}┌────────────────────────────────────────────────────────────────────────────────────────────┐{RESET}
{NEON_CYAN}│{RESET}  {BRIGHT_WHITE}{BOLD}🎯 CHOOSE INPUT SOURCE:{RESET}                                                                    {NEON_CYAN}│{RESET}
{NEON_CYAN}│{RESET}                                                                                            {NEON_CYAN}│{RESET}
{NEON_CYAN}│{RESET}   {NEON_GREEN}{BOLD}[ 1 ]{RESET} {BRIGHT_WHITE}Process Single Video File{RESET}    (e.g., MP4, MKV, AVI, WEBM)                              {NEON_CYAN}│{RESET}
{NEON_CYAN}│{RESET}   {NEON_GREEN}{BOLD}[ 2 ]{RESET} {BRIGHT_WHITE}Process Entire Video Folder{RESET}  (Batch process full tutorial course)                     {NEON_CYAN}│{RESET}
{NEON_CYAN}│{RESET}                                                                                            {NEON_CYAN}│{RESET}
{NEON_CYAN}└────────────────────────────────────────────────────────────────────────────────────────────┘{RESET}
"""
    print(menu)
