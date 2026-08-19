"""
Colored console logger for CodeVision Extractor.

Provides consistent, branded terminal output with color-coded
severity levels.
"""


class Logger:
    """Simple colored console logger."""

    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    WHITE = "\033[97m"
    DIM = "\033[2m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

    @staticmethod
    def info(msg: str):
        print(f"\033[92m[+]\033[0m {msg}")

    @staticmethod
    def warn(msg: str):
        print(f"\033[93m[!]\033[0m {msg}")

    @staticmethod
    def error(msg: str):
        print(f"\033[91m[ERROR]\033[0m {msg}")

    @staticmethod
    def step(msg: str):
        print(f"\033[96m  ->\033[0m {msg}")

    @staticmethod
    def header(msg: str):
        print(f"\n\033[93m{'='*64}\033[0m")
        print(f"\033[1m\033[97m  {msg}\033[0m")
        print(f"\033[93m{'='*64}\033[0m")

    @staticmethod
    def progress(current: int, total: int, label: str):
        pct = int((current / total) * 100) if total > 0 else 0
        bar_len = 30
        filled = int(bar_len * current / total) if total > 0 else 0
        bar = "█" * filled + "░" * (bar_len - filled)
        print(f"\r\033[96m  [{bar}] {pct}% — {label}\033[0m", end="", flush=True)
        if current >= total:
            print()  # newline at completion

    @staticmethod
    def success(msg: str):
        print(f"\n\033[92m{'='*64}\033[0m")
        print(f"\033[1m\033[92m  ✓ {msg}\033[0m")
        print(f"\033[92m{'='*64}\033[0m")
