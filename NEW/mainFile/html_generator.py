"""
html_generator.py
-----------------
Generates a bilingual (AR/EN) dark glassmorphism HTML report from skills data.
Both languages are embedded in a single HTML file; JavaScript switches between
them instantly -- no page reload, no ?lang= parameter needed.

Structure rendered:
  Main Category
    └── Sub Category  (e.g. Backend)
          └── Tech Group  (e.g. Laravel, Django, Express …)
                └── Skill Cards

Usage (standalone):
    python html_generator.py

Usage (from main.py):
    from html_generator import generate_html
    html_path = generate_html(skills_data, OUTPUT_DIR)
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any
try:
  from .config import (
      DATA_FILE,
      MAIN_CATEGORIES_AR,
      MAIN_CATEGORIES_EN,
      MAIN_CATEGORIES_ORDER,
      OUTPUT_DIR,
      SUB_CATEGORIES,
  )
  from .language import LanguageManager, lang
except ImportError:
  from config import (
      DATA_FILE,
      MAIN_CATEGORIES_AR,
      MAIN_CATEGORIES_EN,
      MAIN_CATEGORIES_ORDER,
      OUTPUT_DIR,
      SUB_CATEGORIES,
  )
  from language import LanguageManager, lang

# ---------------------------------------------------------------------------
# Arabic labels for tech groups (level 3)
# ---------------------------------------------------------------------------

TECH_LABELS_AR: dict[str, str] = {
    "laravel":    "لارافيل",
    "django":     "جانغو",
    "express":    "إكسبريس",
    "fastapi":    "فاست API",
    "spring":     "سبرينج",
    "nodejs":     "Node.js",
    "nestjs":     "NestJS",
    "rails":      "رايلز",
    "asp":        "ASP.NET",
    "wordpress":  "ووردبريس",
    "react":      "ريأكت",
    "nextjs":     "Next.js",
    "vue":        "فيو",
    "angular":    "أنغيولار",
    "svelte":     "سفيلت",
    "tailwind":   "تيلويند",
    "general":    "عام",
    "kotlin":     "كوتلن",
    "swift":      "سويفت",
    "dart":       "دارت",
    "flutter":    "فلاتر",
    "openai":     "OpenAI",
    "gemini":     "جيميني",
    "claude":     "كلود",
    "llama":      "لاما",
    "pytorch":    "PyTorch",
    "tensorflow": "TensorFlow",
    "sklearn":    "Scikit-Learn",
    "postgres":   "PostgreSQL",
    "mysql":      "MySQL",
    "sqlite":     "SQLite",
    "mongodb":    "MongoDB",
    "redis":      "Redis",
    "dynamodb":   "DynamoDB",
    "firestore":  "Firestore",
    "ec2":        "EC2",
    "s3":         "S3",
    "lambda":     "Lambda",
    "bigquery":   "BigQuery",
    "gke":        "GKE",
}

# ---------------------------------------------------------------------------
# HTML escape helper
# ---------------------------------------------------------------------------

def _esc(text: Any) -> str:
    """HTML-escape *text* and return an empty string for falsy values."""
    if not text:
        return ""
    return (
        str(text)
        .replace("&",  "&amp;")
        .replace("<",  "&lt;")
        .replace(">",  "&gt;")
        .replace('"',  "&quot;")
    )


# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------

_STYLES = """
:root {
  --bg:      #07111f;
  --bg2:     #0c1726;
  --glass:   rgba(255,255,255,.07);
  --glass2:  rgba(255,255,255,.11);
  --border:  rgba(255,255,255,.12);
  --text:    #f8fbff;
  --muted:   #b6c2d9;
  --accent:  #2b7de9;
  --accent2: #d4a017;
  --shadow:  0 20px 60px rgba(0,0,0,.35);
  --radius:  22px;
}
*{box-sizing:border-box;margin:0;padding:0}
html[data-lang="ar"] body { font-family: Tajawal, Cairo, system-ui; direction: rtl; }
html[data-lang="en"] body { font-family: Inter, system-ui; direction: ltr; }
body{
  background:
    radial-gradient(circle at top right,   rgba(43,125,233,.22), transparent 30%),
    radial-gradient(circle at bottom left, rgba(212,160,23,.15),  transparent 28%),
    linear-gradient(135deg, #050b14 0%, #0a1422 45%, #09111c 100%);
  color:var(--text);min-height:100vh;padding:22px;overflow-x:hidden;position:relative;
}
body::before{
  content:"";position:fixed;inset:0;
  background:linear-gradient(120deg,rgba(255,255,255,.04),transparent 35%,rgba(255,255,255,.03));
  pointer-events:none;backdrop-filter:blur(2px);z-index:0;
}
.container{max-width:1450px;margin:auto;position:relative;z-index:1}
.glass{
  backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);
  background:var(--glass);border:1px solid var(--border);box-shadow:var(--shadow);
}
.header{border-radius:28px;padding:30px 28px;margin-bottom:22px;text-align:center;position:relative;overflow:hidden}
.header::before{
  content:"";position:absolute;inset:-2px;
  background:linear-gradient(135deg,rgba(43,125,233,.24),rgba(212,160,23,.12),transparent 70%);
  z-index:-1;
}
.header-top{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;flex-wrap:wrap;gap:12px}
.lang-toggle{
  background:rgba(255,255,255,.08);border:1px solid var(--border);border-radius:999px;
  padding:8px 22px;color:var(--text);cursor:pointer;font-size:15px;
  transition:all .3s;display:flex;align-items:center;gap:8px;
  font-family: inherit;
}
.lang-toggle:hover{background:rgba(255,255,255,.18);transform:scale(1.04)}
h1{
  font-family: Cairo, Inter, system-ui;
  font-size:clamp(28px,4vw,46px);margin-bottom:8px;
  background:linear-gradient(135deg,#60a5fa,#a78bfa);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;display:inline-block;
}
.subtitle{color:var(--muted);font-size:15px}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px;margin-top:22px}
.stat-item{
  border-radius:18px;padding:16px 18px;
  background:linear-gradient(180deg,rgba(255,255,255,.08),rgba(255,255,255,.04));text-align:center;
}
.number{font-family:Cairo,Inter,system-ui;font-size:28px;font-weight:800;color:#fff;margin-bottom:4px}
.label{color:var(--muted);font-size:13px}
.search-box{border-radius:22px;padding:16px;margin-bottom:22px}
.search-box input{
  width:100%;padding:16px 18px;border-radius:16px;border:1px solid var(--border);
  background:rgba(3,10,20,.45);color:var(--text);font-size:16px;outline:none;transition:all .3s;
  font-family:inherit;
}
.search-box input::placeholder{color:#93a4c6}
.search-box input:focus{border-color:rgba(43,125,233,.7);box-shadow:0 0 0 4px rgba(43,125,233,.12)}
.category{border-radius:26px;margin-bottom:18px;overflow:hidden}
.category-header{
  padding:18px 22px;cursor:pointer;display:flex;justify-content:space-between;align-items:center;
  background:linear-gradient(135deg,rgba(43,125,233,.35),rgba(118,75,162,.28));
  border-bottom:1px solid rgba(255,255,255,.08);transition:all .3s;
}
.category-header:hover{background:linear-gradient(135deg,rgba(43,125,233,.45),rgba(118,75,162,.38))}
.cat-title{
  font-family:Cairo,Inter,system-ui;font-size:20px;font-weight:800;
  display:flex;gap:10px;align-items:center;flex-wrap:wrap;color:#f8fbff;
}
.badge{background:rgba(255,255,255,.14);padding:4px 14px;border-radius:999px;font-size:13px;font-weight:600;color:#f8fbff}
.category-body{padding:18px 18px 8px}
/* ── Sub-category (level 2) ── */
.sub-category{margin-bottom:16px}
.sub-category-header{
  padding:12px 16px;border-radius:16px;display:flex;justify-content:space-between;align-items:center;
  background:rgba(255,255,255,.05);cursor:pointer;transition:all .3s;
}
.sub-category-header:hover{background:rgba(255,255,255,.08)}
.sub-title{font-family:Cairo,Inter,system-ui;font-size:17px;font-weight:700;display:flex;gap:8px;align-items:center;color:#f8fbff}
/* ── Tech group (level 3) ── */
.tech-group{margin:10px 0 4px 0}
.tech-group-header{
  padding:9px 14px;border-radius:12px;
  display:flex;justify-content:space-between;align-items:center;
  background:rgba(43,125,233,.12);border:1px solid rgba(43,125,233,.22);
  cursor:pointer;transition:all .25s;
}
.tech-group-header:hover{background:rgba(43,125,233,.2)}
.tech-title{
  font-family:Cairo,Inter,system-ui;font-size:14px;font-weight:700;
  display:flex;align-items:center;gap:7px;color:#93c5fd;
  text-transform:capitalize;letter-spacing:.03em;
}
.tech-title::before{
  content:"";display:inline-block;width:7px;height:7px;
  border-radius:50%;background:#2b7de9;flex-shrink:0;
}
/* ── Skills grid ── */
.skills-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(270px,1fr));gap:12px;padding:10px 0 4px 0}
.skill-card{
  border-radius:18px;padding:14px 16px;
  background:linear-gradient(180deg,rgba(255,255,255,.08),rgba(255,255,255,.04));
  transition:all .25s;cursor:pointer;border:1px solid transparent;
}
.skill-card:hover{
  transform:translateY(-3px);border-color:rgba(43,125,233,.45);
  background:rgba(255,255,255,.1);box-shadow:0 8px 25px rgba(43,125,233,.15);
}
.skill-name{font-family:Cairo,Inter,system-ui;font-weight:800;margin-bottom:5px;font-size:15px;color:#f8fbff}
.skill-desc{color:#c9d3e8;font-size:13px;line-height:1.6}
.skill-file{color:#8ea0bf;font-size:11px;margin-top:6px;font-family:monospace;opacity:.7}
.toggle-icon{transition:transform .3s;font-size:14px;color:#f8fbff}
.toggle-icon.open{transform:rotate(180deg)}
.hidden{display:none!important}
.no-results{text-align:center;padding:36px;color:var(--muted);font-size:18px}
.footer{text-align:center;padding:24px 10px;color:var(--muted);font-size:13px;opacity:.7}
html[data-lang="ar"] [data-en] { display: none !important; }
html[data-lang="en"] [data-ar] { display: none !important; }
@media(max-width:768px){
  body{padding:12px}
  .cat-title{font-size:16px}
  .skills-grid{grid-template-columns:1fr}
  .header{padding:20px 16px}
  .stats{grid-template-columns:repeat(2,1fr);gap:10px}
  .stat-item{padding:12px 10px}
  .number{font-size:22px}
  .header-top{flex-direction:column;align-items:center}
}
"""


def _build_js():
    globe  = "\U0001F310"
    arabic = "\u0639\u0631\u0628\u064a"
    return (
        "(function() {\n"
        "  var params = new URLSearchParams(window.location.search);\n"
        "  var initLang = params.get('lang') || 'ar';\n"
        "  applyLanguage(initLang);\n"
        "\n"
        "  function applyLanguage(lang) {\n"
        "    var html = document.documentElement;\n"
        "    html.setAttribute('data-lang', lang);\n"
        "    html.setAttribute('lang', lang);\n"
        "    html.setAttribute('dir', lang === 'ar' ? 'rtl' : 'ltr');\n"
        "    var btn = document.getElementById('langToggleBtn');\n"
        f"    if (btn) btn.textContent = lang === 'ar' ? '{globe} English' : '{globe} {arabic}';\n"
        "    var inp = document.getElementById('searchInput');\n"
        "    if (inp) inp.placeholder = inp.getAttribute('data-placeholder-' + lang);\n"
        "    window.__currentLang = lang;\n"
        "  }\n"
        "\n"
        "  window.toggleLanguage = function() {\n"
        "    var newLang = window.__currentLang === 'ar' ? 'en' : 'ar';\n"
        "    applyLanguage(newLang);\n"
        "    if (window.history && window.history.replaceState) {\n"
        "      window.history.replaceState(null, '', window.location.pathname + '?lang=' + newLang);\n"
        "    }\n"
        "  };\n"
        "})();\n"
        "\n"
        "function filterSkills() {\n"
        "  var f = document.getElementById('searchInput').value.toLowerCase().trim();\n"
        "  var anyVisible = false;\n"
        "  document.querySelectorAll('.category').forEach(function(cat) {\n"
        "    var catVisible = false;\n"
        "    cat.querySelectorAll('.sub-category').forEach(function(sub) {\n"
        "      var subVisible = false;\n"
        "      sub.querySelectorAll('.skill-card').forEach(function(card) {\n"
        "        var ok = !f || card.textContent.toLowerCase().includes(f);\n"
        "        card.style.display = ok ? '' : 'none';\n"
        "        if (ok) subVisible = true;\n"
        "      });\n"
        "      sub.querySelectorAll('.tech-group').forEach(function(tg) {\n"
        "        var tgVisible = Array.from(tg.querySelectorAll('.skill-card'))\n"
        "          .some(function(c){ return c.style.display !== 'none'; });\n"
        "        tg.style.display = (tgVisible || !f) ? '' : 'none';\n"
        "        if (tgVisible) subVisible = true;\n"
        "      });\n"
        "      sub.style.display = (subVisible || !f) ? '' : 'none';\n"
        "      if (subVisible) catVisible = true;\n"
        "    });\n"
        "    cat.style.display = (catVisible || !f) ? '' : 'none';\n"
        "    if (catVisible) anyVisible = true;\n"
        "  });\n"
        "  var nr = document.getElementById('noResults');\n"
        "  if (nr) nr.classList.toggle('hidden', anyVisible || !f);\n"
        "}\n"
        "\n"
        "function toggleCategory(header) {\n"
        "  var body = header.nextElementSibling;\n"
        "  var icon = header.querySelector('.toggle-icon');\n"
        "  body.classList.toggle('hidden');\n"
        "  icon.classList.toggle('open');\n"
        "}\n"
        "\n"
        "function toggleSubCategory(header) {\n"
        "  var body = header.nextElementSibling;\n"
        "  body.classList.toggle('hidden');\n"
        "}\n"
        "\n"
        "function toggleTechGroup(header) {\n"
        "  var grid = header.nextElementSibling;\n"
        "  grid.classList.toggle('hidden');\n"
        "  var icon = header.querySelector('.toggle-icon');\n"
        "  if (icon) icon.classList.toggle('open');\n"
        "}\n"
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_html(
    skills_data: dict,
    output_dir: Path,
    language: str | None = None,
) -> Path:
    """
    Build a fully bilingual HTML report and write it to
    *output_dir/skills_report.html*.

    skills_data shape (3-level):
        {
          "Web Development": {
            "backend": {
              "laravel":  [skill_tuple, ...],
              "django":   [skill_tuple, ...],
              "general":  [skill_tuple, ...],
            },
            "frontend": { ... },
          },
          ...
        }

    Legacy 2-level shape is also accepted:
        { "Web Development": { "backend": [skill_tuple, ...] } }
    """
    lm_ar = LanguageManager("ar")
    lm_en = LanguageManager("en")

    # ── Load from JSON if nothing passed in ──────────────────────────────────
    if not skills_data and DATA_FILE.exists():
        try:
            try:
                from .classifier import load_existing_data
            except ImportError:
                from classifier import load_existing_data
            alldata = load_existing_data()
            if alldata:
                for maincat, data in alldata.get("skills", {}).items():
                    skills_data[maincat] = {}
                    for subcat, subdata in data.get("subcategories", {}).items():
                        tech_map: dict[str, list] = {}
                        for s in subdata.get("skills", []):
                            tech = s.get("techstack", "general")
                            tech_map.setdefault(tech, []).append((
                                s.get("originalName", ""),
                                s.get("filename",     ""),
                                s.get("skillName",    ""),
                                s.get("description",  ""),
                            ))
                        skills_data[maincat][subcat] = tech_map
        except Exception:
            pass

    # ── Normalise: convert flat list → {"general": [...]} ───────────────────
    def _normalise(sub_val):
        if isinstance(sub_val, list):
            return {"general": sub_val}
        return sub_val  # already dict[tech → list]

    # ── Totals ───────────────────────────────────────────────────────────────
    total_skills = 0
    for subcats in skills_data.values():
        for sub_val in subcats.values():
            tech_map = _normalise(sub_val)
            for skill_list in tech_map.values():
                total_skills += len(skill_list)
    total_cats  = len(skills_data)
    total_files = total_skills

    font_url = (
        "https://fonts.googleapis.com/css2?"
        "family=Cairo:wght@400;600;700;800&"
        "family=Tajawal:wght@300;400;500;700;800&"
        "family=Inter:wght@300;400;500;600;700;800&"
        "display=swap"
    )

    ordered_keys = (
        [k for k in MAIN_CATEGORIES_ORDER if k in skills_data]
        + [k for k in skills_data if k not in MAIN_CATEGORIES_ORDER]
    )

    search_placeholder_ar = lm_ar.get("searchplaceholder")
    search_placeholder_en = lm_en.get("searchplaceholder")
    today    = datetime.now().strftime("%Y-%m-%d")
    globe_en = "\U0001F310 English"
    js_block = _build_js()

    lines: list[str] = []
    a = lines.append

    # ── HTML head ─────────────────────────────────────────────────────────────
    a('<!DOCTYPE html>')
    a('<html data-lang="ar" lang="ar" dir="rtl">')
    a('<head>')
    a('<meta charset="UTF-8">')
    a('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
    a(f'<title>{lm_ar.get("htmltitle")} | {lm_en.get("htmltitle")}</title>')
    a('<link rel="preconnect" href="https://fonts.googleapis.com">')
    a('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>')
    a(f'<link href="{font_url}" rel="stylesheet">')
    a(f'<style>{_STYLES}</style>')
    a('<script>')
    a('(function(){')
    a('  var p=new URLSearchParams(location.search);')
    a('  var l=p.get("lang")||"ar";')
    a('  document.documentElement.setAttribute("data-lang",l);')
    a('  document.documentElement.setAttribute("lang",l);')
    a('  document.documentElement.setAttribute("dir",l==="ar"?"rtl":"ltr");')
    a('  window.__currentLang=l;')
    a('})();')
    a('</script>')
    a('</head>')
    a('<body>')
    a('<div class="container">')

    # ── Header ────────────────────────────────────────────────────────────────
    a('<div class="header glass">')
    a('  <div class="header-top">')
    a('    <div></div>')
    a(f'    <button id="langToggleBtn" class="lang-toggle" onclick="toggleLanguage()">{globe_en}</button>')
    a('  </div>')
    a(f'  <h1><span data-ar>{lm_ar.get("htmltitle")}</span><span data-en>{lm_en.get("htmltitle")}</span></h1>')
    a(f'  <p class="subtitle"><span data-ar>{lm_ar.get("htmlsubtitle")}</span><span data-en>{lm_en.get("htmlsubtitle")}</span></p>')
    a('  <div class="stats">')
    a(f'    <div class="stat-item"><div class="number">{total_skills}</div>')
    a(f'      <div class="label"><span data-ar>{lm_ar.get("totalskills")}</span><span data-en>{lm_en.get("totalskills")}</span></div></div>')
    a(f'    <div class="stat-item"><div class="number">{total_cats}</div>')
    a(f'      <div class="label"><span data-ar>{lm_ar.get("totalcategories")}</span><span data-en>{lm_en.get("totalcategories")}</span></div></div>')
    a(f'    <div class="stat-item"><div class="number">{total_files}</div>')
    a(f'      <div class="label"><span data-ar>{lm_ar.get("totalfiles")}</span><span data-en>{lm_en.get("totalfiles")}</span></div></div>')
    a(f'    <div class="stat-item"><div class="number">{today}</div>')
    a(f'      <div class="label"><span data-ar>{lm_ar.get("lastupdated")}</span><span data-en>{lm_en.get("lastupdated")}</span></div></div>')
    a('  </div>')
    a('</div>')

    # ── Search ────────────────────────────────────────────────────────────────
    a('<div class="search-box glass">')
    a('  <input id="searchInput" type="text"')
    a(f'    data-placeholder-ar="{search_placeholder_ar}"')
    a(f'    data-placeholder-en="{search_placeholder_en}"')
    a(f'    placeholder="{search_placeholder_ar}"')
    a('    onkeyup="filterSkills()">')
    a('</div>')

    # ── Categories ────────────────────────────────────────────────────────────
    a('<div id="categoriesContainer">')

    for main_cat in ordered_keys:
        subcats   = skills_data[main_cat]
        name_ar   = MAIN_CATEGORIES_AR.get(main_cat, main_cat)
        name_en   = MAIN_CATEGORIES_EN.get(main_cat, main_cat)
        skills_lbl_ar = lm_ar.get("skillscount")
        skills_lbl_en = lm_en.get("skillscount")

        # Total for this main category
        cat_total = 0
        for sv in subcats.values():
            tm = _normalise(sv)
            for sl in tm.values():
                cat_total += len(sl)

        a(f'<div class="category glass" data-category="{_esc(main_cat)}">')
        a(f'  <div class="category-header" onclick="toggleCategory(this)">')
        a(f'    <span class="cat-title">')
        a(f'      <span data-ar>{_esc(name_ar)}</span>')
        a(f'      <span data-en>{_esc(name_en)}</span>')
        a(f'      <span class="badge">{cat_total} <span data-ar>{skills_lbl_ar}</span><span data-en>{skills_lbl_en}</span></span>')
        a(f'    </span>')
        a(f'    <span class="toggle-icon open">&#9660;</span>')
        a(f'  </div>')
        a(f'  <div class="category-body">')

        for sub_cat in sorted(subcats.keys()):
            tech_map = _normalise(subcats[sub_cat])
            sub_total = sum(len(v) for v in tech_map.values())

            # FIX: use .lower() so "Backend" matches "backend" in config
            sub_cat_cfg = SUB_CATEGORIES.get(main_cat, {}).get(sub_cat.lower(), {})
            sub_display_ar = sub_cat_cfg.get("name_ar") or sub_cat_cfg.get("name", sub_cat)
            sub_display_en = sub_cat_cfg.get("name_en") or sub_cat_cfg.get("name", sub_cat)

            a(f'    <div class="sub-category" data-subcategory="{_esc(sub_cat)}">')
            a(f'      <div class="sub-category-header" onclick="toggleSubCategory(this)">')
            a(f'        <span class="sub-title">')
            a(f'          <span data-ar>{_esc(sub_display_ar)}</span>')
            a(f'          <span data-en>{_esc(sub_display_en)}</span>')
            a(f'        </span>')
            a(f'        <span class="badge">{sub_total} <span data-ar>{skills_lbl_ar}</span><span data-en>{skills_lbl_en}</span></span>')
            a(f'      </div>')
            a(f'      <div class="sub-category-body">')  # wrapper toggled by toggleSubCategory

            # ── Tech groups (level 3) ────────────────────────────────────────
            # Sort: "general" always last
            tech_keys = sorted(
                tech_map.keys(),
                key=lambda t: (t == "general", t)
            )

            for tech in tech_keys:
                skill_list = tech_map[tech]
                if not skill_list:
                    continue

                # FIX: bilingual tech-group labels
                tech_label_en = tech.replace("-", " ").title()
                tech_label_ar = TECH_LABELS_AR.get(tech.lower(), tech_label_en)

                a(f'        <div class="tech-group" data-tech="{_esc(tech)}">')
                a(f'          <div class="tech-group-header" onclick="toggleTechGroup(this)">')
                a(f'            <span class="tech-title">')
                a(f'              <span data-ar>{_esc(tech_label_ar)}</span>')
                a(f'              <span data-en>{_esc(tech_label_en)}</span>')
                a(f'            </span>')
                a(f'            <span style="display:flex;align-items:center;gap:8px;">')
                a(f'              <span class="badge">{len(skill_list)}</span>')
                a(f'              <span class="toggle-icon open" style="font-size:11px;">&#9660;</span>')
                a(f'            </span>')
                a(f'          </div>')
                a(f'          <div class="skills-grid">')

                for skill in sorted(skill_list, key=lambda x: x[2] if len(x) > 2 else ""):
                    s_name    = _esc(skill[2]) if len(skill) > 2 else ""
                    s_desc    = _esc(skill[3]) if len(skill) > 3 and skill[3] else ""
                    s_file    = _esc(skill[1]) if len(skill) > 1 else ""
                    s_desc_ar = s_desc if s_desc else lm_ar.get("nodescription")
                    s_desc_en = s_desc if s_desc else lm_en.get("nodescription")
                    file_icon = "\U0001F4C4"

                    a(f'            <div class="skill-card" data-skill="{s_name.lower()}">')
                    a(f'              <div class="skill-name">{s_name}</div>')
                    a(f'              <div class="skill-desc">')
                    a(f'                <span data-ar>{s_desc_ar}</span>')
                    a(f'                <span data-en>{s_desc_en}</span>')
                    a(f'              </div>')
                    a(f'              <div class="skill-file">{file_icon} {s_file}</div>')
                    a(f'            </div>')

                a(f'          </div>')  # .skills-grid
                a(f'        </div>')    # .tech-group

            a(f'      </div>')  # .sub-category-body
            a(f'    </div>')    # .sub-category

        a(f'  </div>')  # .category-body
        a(f'</div>')    # .category

    a('</div>')  # #categoriesContainer

    a('<div id="noResults" class="no-results hidden">')
    a(f'  <span data-ar>{lm_ar.get("noresults")}</span>')
    a(f'  <span data-en>{lm_en.get("noresults")}</span>')
    a('</div>')
    a('<div class="footer">')
    a(f'  <span data-ar>{lm_ar.get("footer")}</span>')
    a(f'  <span data-en>{lm_en.get("footer")}</span>')
    a('</div>')
    a('</div>')  # .container
    a(f'<script>{js_block}</script>')
    a('</body>')
    a('</html>')

    output_dir.mkdir(parents=True, exist_ok=True)
    html_file = output_dir / "skills_report.html"
    html_file.write_text("\n".join(lines), encoding="utf-8")
    return html_file


# ---------------------------------------------------------------------------
# Standalone entry-point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        from colorama import Fore, init
        init(autoreset=True)
    except ImportError:
        class Fore:
            GREEN = YELLOW = RED = ""
    print(Fore.YELLOW + "Updating HTML report...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    html_file = generate_html({}, OUTPUT_DIR)
    if html_file and html_file.stat().st_size > 0:
        print(Fore.GREEN + f"Done: {html_file}")
    else:
        print(Fore.RED + "No data to display.")
