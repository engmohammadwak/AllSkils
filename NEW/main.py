"""
main.py
-------
Main entry point for the Skills Classifier project.

Usage:
    python main.py                    # default language (Arabic)
    python main.py --english          # force English UI
    python main.py --arabic           # force Arabic UI
    python main.py --lang en          # same as --english
    python main.py --html-only        # only regenerate the HTML report
    python main.py --no-html          # skip HTML generation

Every run saves a full log to:  logs/run_YYYY-MM-DD_HH-MM-SS.log
"""

from __future__ import annotations

import io
import sys
from datetime import datetime
from pathlib import Path

from colorama import Fore, Style, init

init(autoreset=True)

# ---- project modules -------------------------------------------------------
from mainFile.config import (
    DATA_FILE,
    INPUT_DIR,
    MAIN_CATEGORIES_ORDER,
    OUTPUT_DIR,
    SUPPORTED_EXTENSIONS,
)
from mainFile.classifier import (
    load_existing_data,
    run_classification,
)
from mainFile.html_generator import generate_html
from mainFile.language import lang


# ===========================================================================
# Tee: write to terminal AND log file simultaneously
# ===========================================================================

class _Tee(io.TextIOBase):
    """
    Wraps an existing stream (stdout / stderr) and mirrors every write
    to a log file, stripping ANSI colour codes from the file copy.
    """
    import re as _re
    _ANSI = _re.compile(r"\x1b\[[0-9;]*m")

    def __init__(self, original_stream, log_file: io.TextIOWrapper):
        self._orig = original_stream
        self._log  = log_file

    # forward encoding / fileno so colorama / other libs stay happy
    @property
    def encoding(self):  return getattr(self._orig, "encoding", "utf-8")
    @property
    def errors(self):    return getattr(self._orig, "errors",   "replace")
    def fileno(self):    return self._orig.fileno()
    def isatty(self):    return self._orig.isatty()
    def flush(self):
        self._orig.flush()
        self._log.flush()

    def write(self, text: str) -> int:
        self._orig.write(text)
        # strip colour codes before writing to file
        self._log.write(self._ANSI.sub("", text))
        return len(text)

    def writelines(self, lines):
        for line in lines:
            self.write(line)


def _setup_logging() -> tuple[Path, io.TextIOWrapper]:
    """
    Create logs/ dir, open a timestamped log file, and redirect
    sys.stdout + sys.stderr through _Tee.  Returns (log_path, log_fh).
    """
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    ts       = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_path = logs_dir / f"run_{ts}.log"
    log_fh   = open(log_path, "w", encoding="utf-8", buffering=1)

    # write a header so the file is self-describing
    log_fh.write(f"Skills Classifier — run started at {datetime.now().isoformat()}\n")
    log_fh.write("=" * 60 + "\n")

    sys.stdout = _Tee(sys.__stdout__, log_fh)   # type: ignore[assignment]
    sys.stderr = _Tee(sys.__stderr__, log_fh)   # type: ignore[assignment]

    return log_path, log_fh


def _teardown_logging(log_fh: io.TextIOWrapper, log_path: Path) -> None:
    """Restore original streams and close the log file."""
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__
    log_fh.write("\n" + "=" * 60 + "\n")
    log_fh.write(f"Run finished at {datetime.now().isoformat()}\n")
    log_fh.close()
    # inform the user on the real stdout now that it's restored
    print(Fore.CYAN + f"\n📄  Full log saved → {log_path}")


# ---------------------------------------------------------------------------
# CLI argument parsing
# ---------------------------------------------------------------------------

def _parse_args() -> dict:
    args = sys.argv[1:]
    opts = {
        "html_only": False,
        "no_html":   False,
    }
    i = 0
    while i < len(args):
        a = args[i]
        if a in ("--english", "-e"):
            lang.set_language("en")
        elif a in ("--arabic", "-a"):
            lang.set_language("ar")
        elif a in ("--lang", "-l") and i + 1 < len(args):
            lang.set_language(args[i + 1])
            i += 1
        elif a == "--html-only":
            opts["html_only"] = True
        elif a == "--no-html":
            opts["no_html"] = True
        elif a == "--toggle":
            lang.toggle()
        i += 1
    return opts


# ---------------------------------------------------------------------------
# HTML report helper
# ---------------------------------------------------------------------------

def _generate_report(skills_data: dict) -> None:
    print(Fore.YELLOW + lang.get("updatinghtml"))
    html_path = generate_html(skills_data, OUTPUT_DIR)
    if html_path and html_path.stat().st_size > 0:
        print(Fore.GREEN + lang.get("updatedhtml", html_path))
    else:
        print(Fore.RED + lang.get("nodataforhtml"))


# ---------------------------------------------------------------------------
# Build skills_data dict from saved JSON (for HTML-only mode)
# ---------------------------------------------------------------------------

def _load_skills_data_from_json() -> dict:
    existing = load_existing_data()
    if not existing:
        return {}

    skills_data: dict = {}
    for main_cat, cat_data in existing.get("skills", {}).items():
        skills_data[main_cat] = {}
        for sub_cat, sub_data in cat_data.get("subcategories", {}).items():
            skills_data[main_cat][sub_cat] = [
                (
                    s.get("originalName", ""),
                    s.get("filename",     ""),
                    s.get("skillName",    ""),
                    s.get("description",  ""),
                )
                for s in sub_data.get("skills", [])
            ]
    return skills_data


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    opts = _parse_args()

    # --- start logging BEFORE any output ---
    log_path, log_fh = _setup_logging()

    try:
        print(Fore.CYAN + Style.BRIGHT + "\n" + "=" * 52)
        print(Fore.YELLOW + Style.BRIGHT + "   " + lang.get("apptitle"))
        print(Fore.CYAN + Style.BRIGHT + "=" * 52 + "\n")

        # ---- HTML-only mode --------------------------------------------
        if opts["html_only"]:
            skills_data = _load_skills_data_from_json()
            if not skills_data:
                print(Fore.YELLOW + lang.get("nodataforhtml"))
            else:
                _generate_report(skills_data)
            return

        # ---- Validate input directory ----------------------------------
        if not INPUT_DIR.exists():
            print(Fore.RED + f"Input directory not found: {INPUT_DIR}")
            print(Fore.YELLOW + "Edit SOURCE_DIR in config.py to point to your skills folder.")
            return

        # ---- Collect files ---------------------------------------------
        source_files = [
            f for f in INPUT_DIR.rglob("*")
            if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
        ]

        if not source_files:
            print(Fore.YELLOW + lang.get("nofilesfound"))
            return

        # ---- Run full classification pipeline --------------------------
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        run_classification(source_files)

        # ---- Generate HTML report --------------------------------------
        if not opts["no_html"]:
            skills_data = _load_skills_data_from_json()
            if skills_data:
                _generate_report(skills_data)
            else:
                print(Fore.YELLOW + lang.get("nodataforhtml"))

        print()
        print(Fore.GREEN + Style.BRIGHT + lang.get("alldone"))
        print()

    finally:
        # always close the log, even if an exception is raised
        _teardown_logging(log_fh, log_path)


if __name__ == "__main__":
    main()
