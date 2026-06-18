"""
inspect_general.py
------------------
Scans every  .../general/  subfolder inside sorted_skills and prints:
  - full path of the file
  - first non-empty lines (preview)
  - suggested keyword to add to TECH_STACKS in config.py

Usage:
    python inspect_general.py              # عرض التقرير في الشاشة
    python inspect_general.py --report     # إنشاء general_report.txt في مجلد المشروع
    python inspect_general.py --csv        # export to general_report.csv
    python inspect_general.py --fix        # interactive: assign each file a tech
    
    
    # أو استخدم --txt (نفس الشيء)
    python inspect_general.py --txt
"""

from __future__ import annotations

import argparse
import csv
import re
import shutil
import sys
from pathlib import Path
from datetime import datetime

# Handle Windows console encoding for Unicode
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    from colorama import Fore, Style, init as _cinit
    _cinit(autoreset=True)
except ImportError:
    class Fore:   GREEN = YELLOW = RED = CYAN = WHITE = MAGENTA = ""
    class Style:  BRIGHT = RESET_ALL = ""

from config import OUTPUT_DIR, TECH_STACKS, SUB_CATEGORIES

# Use ASCII-compatible characters for Windows compatibility
BULLET = ">>" if sys.platform == "win32" else "\u25B6"  # >> or ▶
LINE = Fore.WHITE + "-" * 70
LINE_PLAIN = "-" * 70
PREVIEW_LINES = 5


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _strip_ansi(text: str) -> str:
    """Remove ANSI escape codes from a string."""
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


def _content_preview(path: Path, n: int = PREVIEW_LINES) -> list[str]:
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception:
        return ["<unreadable>"]

    start = 0
    if lines and lines[0].strip() == "---":
        for i, l in enumerate(lines[1:], 1):
            if l.strip() == "---":
                start = i + 1
                break

    result = []
    for l in lines[start:]:
        stripped = l.strip()
        if stripped and not stripped.startswith("#"):
            result.append(stripped[:120])
        if len(result) >= n:
            break
    return result or ["<empty>"]


def _auto_suggest(content: str, main_cat: str, sub_cat: str) -> str:
    if main_cat not in TECH_STACKS or sub_cat not in TECH_STACKS[main_cat]:
        return "?"
    text = content.lower()
    best, best_score = "?", 0
    for tech, kws in TECH_STACKS[main_cat][sub_cat].items():
        score = sum(text.count(k.lower()) for k in kws)
        if score > best_score:
            best, best_score = tech, score
    return best if best_score > 0 else "?"


# ---------------------------------------------------------------------------
# core scan
# ---------------------------------------------------------------------------

def find_general_files() -> list[dict]:
    records: list[dict] = []
    if not OUTPUT_DIR.exists():
        print(Fore.RED + f"Output dir not found: {OUTPUT_DIR}")
        return records

    for md_file in sorted(OUTPUT_DIR.rglob("*.md")):
        if "general" not in [p.name for p in md_file.parents]:
            continue
        if md_file.parent == OUTPUT_DIR:
            continue

        rel_parts = md_file.relative_to(OUTPUT_DIR).parts
        main_cat  = rel_parts[0] if len(rel_parts) > 0 else ""
        sub_cat   = rel_parts[1] if len(rel_parts) > 1 else ""

        try:
            content = md_file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            content = ""

        suggestion = _auto_suggest(content, main_cat, sub_cat)
        preview    = _content_preview(md_file)

        records.append({
            "path":       md_file,
            "filename":   md_file.name,
            "main_cat":   main_cat,
            "sub_cat":    sub_cat,
            "suggestion": suggestion,
            "preview":    preview,
            "content":    content,
        })

    return records


# ---------------------------------------------------------------------------
# display (console with colors)
# ---------------------------------------------------------------------------

def print_report(records: list[dict]) -> None:
    if not records:
        print(Fore.GREEN + Style.BRIGHT + "No files found in general/ folders.")
        return

    from collections import defaultdict
    groups: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(list))
    for r in records:
        groups[r["main_cat"]][r["sub_cat"]].append(r)

    total = len(records)
    print(Fore.CYAN + Style.BRIGHT + f"\n{'='*70}")
    print(Fore.CYAN + Style.BRIGHT + f"  GENERAL FILES REPORT  ({total} files)")
    print(Fore.CYAN + Style.BRIGHT + f"{'='*70}")

    for main_cat, subcats in sorted(groups.items()):
        print(f"\n{Fore.MAGENTA + Style.BRIGHT}{BULLET}  {main_cat}")
        for sub_cat, recs in sorted(subcats.items()):
            # Use different bullet for sub-items
            sub_bullet = "└" if sys.platform != "win32" else "-"
            print(f"   {Fore.YELLOW + Style.BRIGHT}{sub_bullet} {sub_cat}/general  ({len(recs)} files)")
            for r in recs:
                sug_color = Fore.GREEN if r["suggestion"] != "?" else Fore.RED
                print(f"      {Fore.WHITE + Style.BRIGHT}{r['filename']}  "
                      f"{sug_color}[suggest: {r['suggestion']}]")
                for line in r["preview"][:3]:
                    print(f"        {Fore.WHITE + Style.RESET_ALL}{line}")
                print()

    print(LINE)
    print(Fore.CYAN + "To fix: either run  python inspect_general.py --fix")
    print(Fore.CYAN + "  or add keywords in TECH_STACKS (config.py) then re-run main.py")
    print(LINE)


# ---------------------------------------------------------------------------
# Generate report file (inside project folder)
# ---------------------------------------------------------------------------

def generate_report_file(records: list[dict], out: Path = Path("general_report.txt")) -> None:
    """
    Generate a plain text report file inside the project folder.
    This is the main method for creating the report without redirection.
    """
    if not records:
        out.write_text("No files found in general/ folders.\n", encoding="utf-8")
        print(Fore.GREEN + f"Report created -> {out.absolute()}")
        return

    from collections import defaultdict
    groups: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(list))
    for r in records:
        groups[r["main_cat"]][r["sub_cat"]].append(r)

    lines: list[str] = []
    total = len(records)
    
    # Header
    lines.append("=" * 70)
    lines.append(f"  GENERAL FILES REPORT  ({total} files)")
    lines.append(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 70)
    lines.append("")

    # Summary
    lines.append("SUMMARY:")
    lines.append(f"  Total files in general/ folders: {total}")
    lines.append("")
    
    for main_cat, subcats in sorted(groups.items()):
        lines.append("")
        lines.append(f">> {main_cat}")
        lines.append("-" * 50)
        
        for sub_cat, recs in sorted(subcats.items()):
            lines.append(f"   - {sub_cat}/general  ({len(recs)} files)")
            lines.append("")
            
            # List files with their suggestions
            for r in recs:
                lines.append(f"      File    : {r['filename']}")
                lines.append(f"      Path    : {r['path']}")
                lines.append(f"      Suggest : {r['suggestion']}")
                lines.append(f"      Preview :")
                for line in r["preview"][:3]:
                    lines.append(f"        {line}")
                lines.append(LINE_PLAIN)
                lines.append("")

    # Footer
    lines.append("")
    lines.append("=" * 70)
    lines.append("HOW TO FIX:")
    lines.append("  1. Run: python inspect_general.py --fix  (interactive mode)")
    lines.append("  2. Or add keywords in TECH_STACKS (config.py) then re-run main.py")
    lines.append("  3. After fixing, run: python html_generator.py  to rebuild the report")
    lines.append("=" * 70)

    # Write to file
    out.write_text("\n".join(lines), encoding="utf-8")
    print(Fore.GREEN + Style.BRIGHT + f"\n✓ Report saved to: {out.absolute()}")
    print(Fore.CYAN + f"  ({total} files analyzed)")


# ---------------------------------------------------------------------------
# TXT export (plain, no ANSI) - kept for backward compatibility
# ---------------------------------------------------------------------------

def export_txt(records: list[dict], out: Path = Path("general_report.txt")) -> None:
    """Legacy method - use generate_report_file instead"""
    generate_report_file(records, out)


# ---------------------------------------------------------------------------
# CSV export
# ---------------------------------------------------------------------------

def export_csv(records: list[dict], out: Path = Path("general_report.csv")) -> None:
    with open(out, "w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=[
            "filename", "main_cat", "sub_cat", "suggestion", "path", "preview"
        ])
        writer.writeheader()
        for r in records:
            writer.writerow({
                "filename":   r["filename"],
                "main_cat":   r["main_cat"],
                "sub_cat":    r["sub_cat"],
                "suggestion": r["suggestion"],
                "path":       str(r["path"]),
                "preview":    " | ".join(r["preview"]),
            })
    print(Fore.GREEN + f"CSV saved -> {out}  ({len(records)} rows)")


# ---------------------------------------------------------------------------
# interactive fix mode
# ---------------------------------------------------------------------------

def _available_techs(main_cat: str, sub_cat: str) -> list[str]:
    if main_cat not in TECH_STACKS or sub_cat not in TECH_STACKS[main_cat]:
        return []
    return list(TECH_STACKS[main_cat][sub_cat].keys())


def _move_file(src: Path, tech: str) -> None:
    new_dir = src.parent.parent / tech
    new_dir.mkdir(parents=True, exist_ok=True)
    dest = new_dir / src.name
    counter = 1
    while dest.exists():
        dest = new_dir / f"{src.stem}-{counter}{src.suffix}"
        counter += 1
    shutil.move(str(src), dest)
    print(Fore.GREEN + f"  Moved -> {dest}")


def interactive_fix(records: list[dict]) -> None:
    if not records:
        print(Fore.GREEN + "Nothing to fix.")
        return

    print(Fore.CYAN + Style.BRIGHT + f"\nInteractive fix mode \u2014 {len(records)} files\n")
    print(Fore.YELLOW + "For each file type the target tech name (or press Enter to skip).")
    print(Fore.YELLOW + "Type  q  to quit.\n")

    moved = 0
    for r in records:
        techs = _available_techs(r["main_cat"], r["sub_cat"])
        tech_hint = "  |  ".join(techs) if techs else "(no TECH_STACKS entry)"
        print(LINE)
        print(Fore.WHITE + Style.BRIGHT + r["filename"])
        print(Fore.YELLOW + f"  Path   : {r['path']}")
        print(Fore.YELLOW + f"  Techs  : {tech_hint}")
        print(Fore.YELLOW + f"  Auto   : {r['suggestion']}")
        print(Fore.WHITE  + "  Preview:")
        for line in r["preview"]:
            print(f"    {line}")

        choice = input(
            Fore.CYAN + f"  Move to [{r['suggestion'] if r['suggestion'] != '?' else '?'}] "
            "(Enter=skip, q=quit): "
        ).strip().lower()

        if choice == "q":
            break
        if not choice:
            if r["suggestion"] != "?":
                choice = r["suggestion"]
            else:
                print(Fore.YELLOW + "  Skipped.")
                continue

        if choice and choice in (techs or [choice]):
            _move_file(r["path"], choice)
            moved += 1
        else:
            confirm = input(
                Fore.RED + f"  '{choice}' not in TECH_STACKS. Create folder anyway? [y/N]: "
            ).strip().lower()
            if confirm == "y":
                _move_file(r["path"], choice)
                moved += 1
            else:
                print(Fore.YELLOW + "  Skipped.")

    print(LINE)
    print(Fore.GREEN + Style.BRIGHT + f"Done. {moved} file(s) moved.")
    if moved:
        print(Fore.CYAN + "Run  python html_generator.py  to rebuild the report.")


# ---------------------------------------------------------------------------
# entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Inspect / fix files sitting in general/ folders"
    )
    parser.add_argument("--report", action="store_true", 
                       help="Generate general_report.txt in project folder")
    parser.add_argument("--csv", action="store_true", 
                       help="Export results to general_report.csv")
    parser.add_argument("--txt", action="store_true", 
                       help="Legacy: export to general_report.txt (same as --report)")
    parser.add_argument("--fix", action="store_true", 
                       help="Interactive mode: move files to correct tech folder")
    args = parser.parse_args()

    records = find_general_files()

    if args.csv:
        export_csv(records)
    elif args.report or args.txt:
        # Generate report file in project folder
        generate_report_file(records)
    elif args.fix:
        print_report(records)
        interactive_fix(records)
    else:
        # Default: display in console
        print_report(records)
        
        
        