"""
classifier.py
-------------
Core processing engine:
  - skill-name / description extraction from Markdown front-matter
  - main-category & sub-category detection (keyword scoring)
  - technology/framework detection (3rd level -- uses TECH_STACKS)
  - duplicate detection via content hashing
  - file copying with collision-safe naming
  - JSON persistence (incremental -- never overwrites existing skills)
  - unclassified / duplicate logging

All I/O paths and category definitions come from ``config``.
All user-visible strings come from ``language.lang``.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import sys
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

from colorama import Fore, Style

from config import (
    DATA_FILE,
    DUPLICATES_FILE,
    MAIN_CATEGORIES_AR,
    MAIN_CATEGORIES_EN,
    MAIN_CATEGORY_KEYWORDS,
    OUTPUT_DIR,
    SIGNATURES_FILE,
    SUB_CATEGORIES,
    TECH_STACKS,
    UNCLASSIFIED_FILE,
)
from language import lang

# ---------------------------------------------------------------------------
# Type aliases
# ---------------------------------------------------------------------------

# (original_name, dest_filename, skill_name, description, techstack)
SkillTuple = tuple[str, str, str, str, str]
FileInfo   = dict[str, Any]


# ===========================================================================
# Progress bar
# ===========================================================================

def _draw_progress(current: int, total: int, label: str = "") -> None:
    bar_width = 40
    pct       = current / total if total else 0
    filled    = int(bar_width * pct)
    bar       = "\u2588" * filled + "\u2591" * (bar_width - filled)
    pct_str   = f"{pct * 100:5.1f}%"
    counter   = f"({current}/{total})"
    line      = f"\r  [{bar}]  {pct_str}  {counter}  {label}"
    sys.stdout.write(line)
    sys.stdout.flush()


# ===========================================================================
# Text helpers
# ===========================================================================

def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\-]", "-", text)
    text = re.sub(r"-+", "-", text)
    if len(text) > 80:
        text = text[:80]
    return text.strip("-")


def extract_skill_name(content: str, fallback_name: str) -> str:
    match = re.search(r"^name[:\s]+(.+)", content, re.MULTILINE)
    if match:
        name = match.group(1).strip()
        return re.sub(r"[\"']", "", name)

    for line in content.split("\n")[:20]:
        line = line.strip()
        if not line or line.startswith(("#", "-", "---")):
            continue
        clean = re.sub(r"[\"']", "", line)
        clean = re.sub(r"skill", "", clean, flags=re.IGNORECASE)
        clean = re.sub(r"[^\w\s-]", "", clean)
        if clean and len(clean) > 3:
            return clean.strip()

    clean = re.sub(r"SKILL[\??-]?", "", fallback_name)
    clean = re.sub(r"[\"']", "", clean)
    if clean and clean != fallback_name:
        return clean.strip()

    return fallback_name


def extract_description(content: str) -> str:
    match = re.search(
        r"^(?:description|overview|about|summary)[:\s]+(.+)",
        content, re.MULTILINE | re.IGNORECASE,
    )
    if match:
        return match.group(1).strip()

    lines = content.split("\n")
    for i, line in enumerate(lines):
        if re.search(r"description|overview|about|summary", line, re.IGNORECASE):
            if i + 1 < len(lines) and lines[i + 1].strip():
                return lines[i + 1].strip()
    return ""


# ===========================================================================
# Category detection
# ===========================================================================

def detect_main_category(text: str, skill_name: str) -> str | None:
    text_lower  = text.lower()
    skill_lower = skill_name.lower()
    scores: dict[str, int] = {}

    for category, keywords in MAIN_CATEGORY_KEYWORDS.items():
        score = 0
        for kw in keywords:
            kw_l = kw.lower()
            if kw_l in skill_lower:
                score += 5
            score += text_lower.count(kw_l) * 2
        if score > 0:
            scores[category] = score

    return max(scores, key=scores.get) if scores else None  # type: ignore[arg-type]


def detect_sub_category(text: str, main_category: str, skill_name: str) -> str | None:
    if not main_category or main_category not in SUB_CATEGORIES:
        return None

    text_lower  = text.lower()
    skill_lower = skill_name.lower()
    scores: dict[str, int] = {}

    for sub_id, sub_data in SUB_CATEGORIES[main_category].items():
        score = 0
        for kw in sub_data["keywords"]:
            kw_l = kw.lower()
            if kw_l in skill_lower:
                score += 5
            score += text_lower.count(kw_l) * 2
        if score > 0:
            scores[sub_id] = score

    return max(scores, key=scores.get) if scores else None  # type: ignore[arg-type]


def detect_technology(text: str, main_category: str, sub_category: str) -> str:
    """
    Detect the specific technology/framework for the 3rd folder level.
    Uses TECH_STACKS from config.
    Returns 'general' when no specific technology is found.
    """
    if main_category not in TECH_STACKS:
        return "general"
    if sub_category not in TECH_STACKS[main_category]:
        return "general"

    text_lower = text.lower()
    tech_scores: dict[str, int] = {}

    for tech_name, keywords in TECH_STACKS[main_category][sub_category].items():
        score = 0
        for kw in keywords:
            kw_l = kw.lower()
            score += text_lower.count(kw_l) * 2
        if score > 0:
            tech_scores[tech_name] = score

    if not tech_scores:
        return "general"

    return max(tech_scores, key=tech_scores.get)  # type: ignore[arg-type]


# ===========================================================================
# Hashing / deduplication helpers
# ===========================================================================

def get_file_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def get_file_signature(content: str, file_size: int) -> str:
    normalised = re.sub(r"\s+", " ", content.strip())
    return f"{file_size}{normalised[:500]}"


# ===========================================================================
# Filename helpers
# ===========================================================================

def get_unique_filename(
    base_name: str,
    full_path: str,
    output_dir: Path,
    used_names: set[str],
) -> str:
    if len(base_name) > 60:
        base_name = base_name[:60]

    clean_name = slugify(base_name)
    if not clean_name or len(clean_name) < 2:
        clean_name = "unnamed"
    if len(clean_name) > 50:
        clean_name = clean_name[:50].rstrip("-")

    dest_dir = output_dir / full_path
    filename = f"{clean_name}.md"
    counter  = 1

    for _ in range(50):
        candidate = f"{clean_name}-{counter}.md" if counter > 1 else f"{clean_name}.md"
        full_check = dest_dir / candidate
        if len(str(full_check)) > 240:
            clean_name = clean_name[:30].rstrip("-")
            candidate  = f"{clean_name}-{counter}.md"
            full_check = dest_dir / candidate
        if not full_check.exists() and candidate not in used_names:
            filename = candidate
            break
        counter += 1
    else:
        filename = f"skill-{int(time.time())}.md"
        while (dest_dir / filename).exists() or filename in used_names:
            filename = f"skill-{int(time.time())}.md"

    used_names.add(filename)
    return filename


# ===========================================================================
# Persistence helpers
# ===========================================================================

def load_existing_data() -> dict | None:
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except Exception:
            return None
    return None


def load_existing_signatures() -> dict[str, Any]:
    if SIGNATURES_FILE.exists():
        try:
            with open(SIGNATURES_FILE, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except Exception:
            return {}
    return {}


def save_signatures(signatures: dict[str, Any]) -> None:
    with open(SIGNATURES_FILE, "w", encoding="utf-8") as fh:
        json.dump(signatures, fh, ensure_ascii=False, indent=2)


def get_existing_hashes() -> set[str]:
    existing: set[str] = set()
    signatures = load_existing_signatures()
    existing.update(signatures.keys())

    if OUTPUT_DIR.exists():
        for md_file in OUTPUT_DIR.rglob("*.md"):
            try:
                content = md_file.read_text(encoding="utf-8", errors="ignore")
                existing.add(get_file_hash(content))
            except Exception:
                pass

    return existing


# ===========================================================================
# Logging helpers
# ===========================================================================

def log_unclassified_file(
    filename: str,
    skill_name: str,
    reason: str,
    details: str,
    main_category: str,
    sub_category: str,
) -> None:
    try:
        with open(UNCLASSIFIED_FILE, "a", encoding="utf-8") as fh:
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            fh.write(lang.get("fileheader", filename))
            fh.write(f"{lang.get('timestamp', ts)}\n")
            fh.write(f"{lang.get('skillname', skill_name)}\n")
            fh.write(f"{lang.get('classificationissue', reason)}\n")
            if main_category:
                fh.write(f"{lang.get('proposedmain', main_category)}\n")
            if sub_category:
                fh.write(f"{lang.get('proposedsub', sub_category)}\n")
            if details:
                fh.write(f"{lang.get('additionaldetails', details)}\n")
            fh.write(f"{lang.get('requiredaction')}\n")
            fh.write("---\n")
    except Exception:
        pass


def log_duplicates(duplicates_found: list[dict], new_files_count: int) -> None:
    with open(DUPLICATES_FILE, "a", encoding="utf-8") as fh:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        fh.write(lang.get("sessionheader", ts))
        fh.write(lang.get("newfilescount", new_files_count))
        fh.write(lang.get("duplicategroupscount", len(duplicates_found)))
        for dup in duplicates_found:
            fh.write(lang.get("duplicateitem", dup["original_name"]))
            fh.write(lang.get("skillnameitem", dup["skill_name"]))
            fh.write(lang.get("copiescount",   dup["total_count"]))
            fh.write(lang.get("duplicatelist"))
            for d in dup["duplicates"]:
                fh.write(f"  - {d}\n")
            fh.write("\n")
        fh.write("---\n")


def _ensure_log_files() -> None:
    if not UNCLASSIFIED_FILE.exists():
        with open(UNCLASSIFIED_FILE, "w", encoding="utf-8") as fh:
            fh.write(lang.get("unclassifiedtitle"))
            fh.write(lang.get("unclassifieddesc"))
            fh.write("---\n")

    if not DUPLICATES_FILE.exists():
        with open(DUPLICATES_FILE, "w", encoding="utf-8") as fh:
            fh.write(lang.get("duplicatestitle"))
            fh.write(lang.get("duplicatesdesc"))
            fh.write("---\n")


# ===========================================================================
# JSON save
# ===========================================================================

def save_data_to_json(
    skills_data: dict[str, dict[str, list[SkillTuple]]],
    total_files: int,
    new_files_count: int,
    duplicates_count: int,
    unclassified_count: int,
) -> Path:
    existing = load_existing_data()

    metadata: dict[str, Any] = {
        "totalFiles":         total_files,
        "totalSkills":        sum(len(s) for s in skills_data.values()),
        "lastUpdated":        datetime.now().isoformat(),
        "newFilesAdded":      new_files_count,
        "duplicatesFound":    duplicates_count,
        "unclassifiedFiles":  unclassified_count,
    }

    def _skill_dict(s: SkillTuple) -> dict:
        """Convert a skill tuple to a JSON-serialisable dict.

        Tuple layout: (original_name, dest_filename, skill_name, description, techstack)
        techstack is at index 4; older tuples (len==4) default to 'general'.
        """
        return {
            "originalName": s[0],
            "filename":     s[1],
            "skillName":    s[2],
            "description":  s[3],
            "techstack":    s[4] if len(s) > 4 else "general",
        }

    if existing:
        metadata["totalSkills"] = sum(
            len(s) for s in existing.get("skills", {}).values()
        )
        metadata["totalFiles"] = existing.get("metadata", {}).get("totalFiles", total_files)
        existing_skills: dict = existing.get("skills", {})

        for main_cat, subcats in skills_data.items():
            if main_cat not in existing_skills:
                existing_skills[main_cat] = {
                    "displayNameAr": MAIN_CATEGORIES_AR.get(main_cat, main_cat),
                    "displayNameEn": MAIN_CATEGORIES_EN.get(main_cat, main_cat),
                    "subcategories": {},
                }
            for sub_cat, skills in subcats.items():
                if sub_cat not in existing_skills[main_cat]["subcategories"]:
                    sub_name = (
                        SUB_CATEGORIES
                        .get(main_cat, {})
                        .get(sub_cat, {})
                        .get("name", sub_cat)
                    )
                    existing_skills[main_cat]["subcategories"][sub_cat] = {
                        "displayNameAr": sub_name,
                        "displayNameEn": sub_name,
                        "skills": [],
                    }
                existing_names = {
                    s["skillName"]
                    for s in existing_skills[main_cat]["subcategories"][sub_cat]["skills"]
                }
                for skill in skills:
                    if skill[2] not in existing_names:
                        existing_skills[main_cat]["subcategories"][sub_cat]["skills"].append(
                            _skill_dict(skill)
                        )

        data = {
            "metadata":       metadata,
            "maincategories": {"ar": MAIN_CATEGORIES_AR, "en": MAIN_CATEGORIES_EN},
            "skills":         existing_skills,
            "language":       lang.language,
        }
    else:
        skills_json: dict = {}
        for main_cat, subcats in skills_data.items():
            skills_json[main_cat] = {
                "displayNameAr": MAIN_CATEGORIES_AR.get(main_cat, main_cat),
                "displayNameEn": MAIN_CATEGORIES_EN.get(main_cat, main_cat),
                "subcategories": {},
            }
            for sub_cat, skills in subcats.items():
                sub_name = (
                    SUB_CATEGORIES
                    .get(main_cat, {})
                    .get(sub_cat, {})
                    .get("name", sub_cat)
                )
                skills_json[main_cat]["subcategories"][sub_cat] = {
                    "displayNameAr": sub_name,
                    "displayNameEn": sub_name,
                    "skills": [_skill_dict(s) for s in skills],
                }
        data = {
            "metadata":       {
                **metadata,
                "createdAt":  datetime.now().isoformat(),
            },
            "maincategories": {"ar": MAIN_CATEGORIES_AR, "en": MAIN_CATEGORIES_EN},
            "skills":         skills_json,
            "language":       lang.language,
        }

    with open(DATA_FILE, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)

    return DATA_FILE


# ===========================================================================
# Per-file processor
# ===========================================================================

def process_file(
    file_info: FileInfo,
    skills_by_category: dict,
    used_names: set[str],
    unclassified_files: list[dict],
) -> None:
    """
    Classify a single file and copy it into the correct output folder.
    Path structure: OUTPUT_DIR / main_category / sub_category / technology
    """
    try:
        content    = file_info["content"]
        skill_name = file_info["skill_name"]
        filename   = file_info["original_name"]

        description   = extract_description(content)
        main_category = detect_main_category(content, skill_name)
        sub_category  = detect_sub_category(content, main_category or "", skill_name) if main_category else None

        if not main_category:
            unclassified_files.append({
                "filename":      filename,
                "skill_name":    skill_name,
                "reason":        "No main category found",
                "main_category": "",
                "sub_category":  "",
            })
            log_unclassified_file(filename, skill_name, "No main category", "", "", "")
            return

        if not sub_category:
            unclassified_files.append({
                "filename":      filename,
                "skill_name":    skill_name,
                "reason":        f"No sub-category found -> placed in '{main_category}/general'",
                "main_category": main_category,
                "sub_category":  "general",
            })
            log_unclassified_file(filename, skill_name, "No sub-category", "", main_category, "general")
            sub_category = "general"

        # detect technology (3rd level)
        technology = detect_technology(content, main_category, sub_category)

        # build destination path: main_category / sub_category / technology
        relative_path = Path(main_category) / sub_category / technology
        dest_dir      = OUTPUT_DIR / relative_path
        dest_dir.mkdir(parents=True, exist_ok=True)

        new_filename = get_unique_filename(skill_name, str(relative_path), OUTPUT_DIR, used_names)
        destination  = dest_dir / new_filename

        shutil.copy2(file_info["source_path"], destination)

        # *** include techstack (5th element) in the tuple ***
        skills_by_category[main_category][sub_category].append(
            (filename, new_filename, skill_name, description, technology)
        )

    except Exception as exc:
        unclassified_files.append({
            "filename":      file_info.get("original_name", "?"),
            "skill_name":    file_info.get("skill_name", "?"),
            "reason":        f"Exception: {exc}",
            "main_category": "",
            "sub_category":  "",
        })
        log_unclassified_file(
            file_info.get("original_name", "?"),
            file_info.get("skill_name", "?"),
            str(exc), "", "", "",
        )


# ===========================================================================
# Main pipeline
# ===========================================================================

def run_classification(source_files: list[Path]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    _ensure_log_files()

    LINE = Fore.WHITE + "-" * 60

    print(Fore.CYAN + Style.BRIGHT + f"\n\U0001f4c2  Found {len(source_files)} files")
    print(LINE)
    print(Fore.YELLOW + "\U0001f50d  Checking for already-processed files...")

    existing_hashes = get_existing_hashes()
    all_signatures  = load_existing_signatures()
    file_groups: dict[str, list[FileInfo]] = defaultdict(list)
    new_files: list[Path] = []

    for file in source_files:
        try:
            content    = file.read_text(encoding="utf-8", errors="ignore")
            file_hash  = get_file_hash(content)
            file_size  = file.stat().st_size
            signature  = get_file_signature(content, file_size)
            skill_name = extract_skill_name(content, file.stem)
            if not skill_name or len(skill_name) < 2:
                skill_name = file.stem.replace("-", " ").replace("_", " ").title()

            if file_hash not in existing_hashes:
                new_files.append(file)
                file_groups[signature].append({
                    "file":          file,
                    "content":       content,
                    "skill_name":    skill_name,
                    "original_name": file.name,
                    "file_size":     file_size,
                    "file_hash":     file_hash,
                    "source_path":   file,
                })
                all_signatures[file_hash] = {
                    "originalName": file.name,
                    "skillName":    skill_name,
                    "dateAdded":    datetime.now().isoformat(),
                }
        except Exception as exc:
            print(Fore.RED + f"\n\u274c  Read error: {file.name} -- {exc}")

    if not new_files:
        print(LINE)
        print(Fore.GREEN + Style.BRIGHT + "\u2705  No new files to add!")
        print(Fore.CYAN  + f"   All {len(source_files)} files already exist in the repository.")
        print(LINE)
        return

    print(Fore.GREEN + f"\U0001f195  {len(new_files)} new files found -- starting classification...")
    print(LINE)

    total_to_process    = len(file_groups)
    new_skills:          dict       = defaultdict(lambda: defaultdict(list))
    used_names:          set[str]   = set()
    processed_files:     int        = 0
    duplicates_found:    list[dict] = []
    unclassified_files:  list[dict] = []

    print(Fore.CYAN + Style.BRIGHT +
          f"\u23f3  Processing and classifying {len(new_files)} files...\n")

    for signature, group in file_groups.items():
        processed_files += 1
        _draw_progress(processed_files, total_to_process)

        if len(group) == 1:
            process_file(group[0], new_skills, used_names, unclassified_files)
        else:
            duplicates_found.append({
                "original_name": group[0]["original_name"],
                "skill_name":    group[0]["skill_name"],
                "duplicates":    [f["original_name"] for f in group[1:]],
                "total_count":   len(group),
            })
            process_file(group[0], new_skills, used_names, unclassified_files)

    _draw_progress(total_to_process, total_to_process)
    print()

    if duplicates_found:
        log_duplicates(duplicates_found, len(new_files))

    save_signatures(all_signatures)

    print(Fore.YELLOW + "\U0001f4be  Saving data...")
    json_file = save_data_to_json(
        new_skills,
        total_files=len(source_files),
        new_files_count=processed_files,
        duplicates_count=len(duplicates_found),
        unclassified_count=len(unclassified_files),
    )
    print(Fore.GREEN + f"\u2705  JSON updated -> {json_file}")

    print(LINE)
    print(Fore.GREEN + Style.BRIGHT + "\U0001f4ca  Session Summary")
    print(LINE)
    print(Fore.CYAN  + f"   Total source files  : {len(source_files)}")
    print(Fore.CYAN  + f"   Already existing    : {len(existing_hashes)}")
    print(Fore.GREEN + f"   \u2705  Added             : {processed_files}")

    if duplicates_found:
        print(Fore.RED  + f"   \u26a0\ufe0f  Duplicate groups  : {len(duplicates_found)}")
        print(Fore.CYAN + f"      -> logged to: {DUPLICATES_FILE}")

    if unclassified_files:
        print(LINE)
        print(Fore.YELLOW + Style.BRIGHT +
              f"\u26a0\ufe0f  {len(unclassified_files)} files need manual review:")
        print()

        no_main = [f for f in unclassified_files if not f["main_category"]]
        no_sub  = [f for f in unclassified_files if f["main_category"]]

        if no_main:
            print(Fore.RED + Style.BRIGHT +
                  f"   \u274c  No category found ({len(no_main)} files):")
            for fi in no_main[:20]:
                print(Fore.RED + f"      * {fi['filename']}")
                print(Fore.WHITE + f"        skill : {fi['skill_name']}")
            if len(no_main) > 20:
                print(Fore.RED + f"      ... and {len(no_main) - 20} more")
            print()

        if no_sub:
            print(Fore.YELLOW + Style.BRIGHT +
                  f"   \u2753  No sub-category -> placed in /general ({len(no_sub)} files):")
            for fi in no_sub[:20]:
                print(Fore.YELLOW + f"      * {fi['filename']}")
                print(Fore.WHITE +
                      f"        category : {fi['main_category']}  |  reason: {fi['reason']}")
            if len(no_sub) > 20:
                print(Fore.YELLOW + f"      ... and {len(no_sub) - 20} more")
            print()

        print(Fore.CYAN + f"\U0001f4c4  Full details -> {UNCLASSIFIED_FILE}")
        print(Fore.CYAN + "   To fix: add keywords in config.py -> MAIN_CATEGORY_KEYWORDS / SUB_CATEGORIES / TECH_STACKS")

    print(LINE)
    print(Fore.GREEN + Style.BRIGHT + f"\U0001f389  Done! {processed_files} file(s) classified successfully.")
    if unclassified_files:
        print(Fore.YELLOW + Style.BRIGHT +
              f"\u26a0\ufe0f   {len(unclassified_files)} file(s) need attention -- see {UNCLASSIFIED_FILE}")
    print(LINE)
