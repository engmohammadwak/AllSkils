"""
language.py
-----------
LanguageManager: bilingual (AR/EN) string registry.
All UI strings live here — never hardcode display text in other modules.

Usage:
    from language import lang
    print(lang.get("foundfiles", 42))
"""

from __future__ import annotations


class LanguageManager:
    """
    Centralised translation store.

    Supports Arabic and English. Call ``lang.get(key, *args)`` to retrieve
    a formatted string in the current language.  Missing keys fall back to
    the key name itself so the app never crashes on a missing translation.
    """

    TRANSLATIONS: dict[str, dict[str, str]] = {
        # ── English ──────────────────────────────────────────────────────────
        "en": {
            # Console — general flow
            "foundfiles":          "📂 Found {} Markdown files",
            "existingfiles":       "📦 Existing files: {}",
            "checkingfiles":       "🔍 Checking for new files...",
            "nonewfiles":          "✅ No new files to add!",
            "allfilesexist":       "📌 All {} files already exist in the repository",
            "foundnewfiles":       "🆕 Found {} new files — processing...",
            "processing":          "⚙️  Processing and classifying...",
            "savingdata":          "💾 Saving data...",
            "updatedjson":         "✅ Updated JSON → {}",
            "updatinghtml":        "🔄 Updating HTML report...",
            "updatedhtml":         "✅ Updated HTML → {}",
            "nodataforhtml":       "❌ No data to display in report",
            "deletingolddata":     "🗑️  Deleting old data file...",

            # Console — session stats
            "sessionstats":        "📊 Session Statistics",
            "totalsourcefiles":    "   Total source files : {}",
            "existingfilescount":  "   Existing files     : {}",
            "filesadded":          "   Files added        : {}",
            "duplicategroups":     "   Duplicate groups   : {}",
            "loggedto":            "   Logged to          → {}",
            "duplicatefiles":      "   Duplicate files:",
            "copies":              "copies",
            "unclassifiedfiles":   "⚠️  Unclassified files : {}",
            "reasons":             "      Reason  : {}",
            "proposedcategory":    "      Category: {}",
            "moreitems":           "   ... and {} more",
            "loggedtounclassified":"   Logged to → {}",
            "checkfulldetails":    "   Open the file to see full details",
            "successfullyadded":   "🎉 Successfully added {} files!",
            "duplicatewarning":    "⚠️  Found {} duplicate groups",
            "unclassifiedwarning": "⚠️  Found {} unclassified files",
            "checkunclassified":   "   Check → {}",
            "line":                "─" * 60,

            # Console — per-file processing
            "noskillfound":        "⚠️  No skill name found in '{}', using fallback: '{}'",
            "nocategoryfound":     "⚠️  No main category found for '{}'",
            "nosubcategoryfound":  "⚠️  No sub-category found in '{}' → '{}'",
            "processingsuccess":   "✅ Processed: {}",
            "copyingfile":         "📋 Copying: {} → {}",
            "errorreading":        "❌ Error reading '{}': {}",
            "errorprocessing":     "❌ Error processing '{}': {}",

            # Unclassified log
            "unclassifiedtitle":   "# Unclassified Files\n",
            "unclassifieddesc":    "These files were not automatically classified. "
                                   "Please review and classify them manually.\n\n",
            "fileheader":          "\n## {}\n",
            "timestamp":           "- **Date**              : {}",
            "skillname":           "- **Skill Name**        : {}",
            "classificationissue": "- **Issue**             : {}",
            "proposedmain":        "- **Proposed Category** : {}",
            "proposedsub":         "- **Proposed Sub**      : {}",
            "additionaldetails":   "- **Details**           : {}",
            "requiredaction":      "- **Action Required**   : Please review and classify this file manually\n",

            # Duplicates log
            "duplicatestitle":      "# Duplicate Files Report\n",
            "duplicatesdesc":       "List of duplicate files detected.\n\n",
            "sessionheader":        "\n## Session — {}\n",
            "newfilescount":        "- New files        : {}\n",
            "duplicategroupscount": "- Duplicate groups : {}\n\n",
            "duplicateitem":        "\n### {}\n",
            "skillnameitem":        "- Skill Name : {}\n",
            "copiescount":          "- Copies     : {}\n",
            "duplicatelist":        "- Files      :\n",

            # HTML report
            "htmltitle":           "Skills Repository",
            "htmlsubtitle":        "Professional Bilingual Report",
            "totalskills":         "Total Skills",
            "totalcategories":     "Main Specializations",
            "totalfiles":          "Processed Files",
            "lastupdated":         "Last Updated",
            "searchplaceholder":   "Search for a skill...",
            "noresults":           "No results match your search",
            "footer":              "Automatically generated by the Skill Classification System",
            "togglelanguage":      "Language",
            "skillscount":         "skill",
            "nodescription":       "No description available",
            "filelabel":           "📄 ",
            "alldone":             "✅ All done!",
            "nofilesfound":        "⚠️  No files found in the source directory.",
            "apptitle":            "Skills Classification System",
        },

        # ── Arabic ───────────────────────────────────────────────────────────
        "ar": {
            # Console — general flow
            "foundfiles":          "📂 تم العثور على {} ملف Markdown",
            "existingfiles":       "📦 الملفات الموجودة: {}",
            "checkingfiles":       "🔍 جاري التحقق من الملفات الجديدة...",
            "nonewfiles":          "✅ لا توجد ملفات جديدة للإضافة!",
            "allfilesexist":       "📌 جميع الملفات الـ {} موجودة بالفعل",
            "foundnewfiles":       "🆕 تم العثور على {} ملف جديد — جاري المعالجة...",
            "processing":          "⚙️  جاري المعالجة والتصنيف...",
            "savingdata":          "💾 حفظ البيانات...",
            "updatedjson":         "✅ تم تحديث JSON ← {}",
            "updatinghtml":        "🔄 جاري تحديث تقرير HTML...",
            "updatedhtml":         "✅ تم تحديث HTML ← {}",
            "nodataforhtml":       "❌ لا توجد بيانات لعرضها في التقرير",
            "deletingolddata":     "🗑️  جاري حذف ملف البيانات القديم...",

            # Console — session stats
            "sessionstats":        "📊 إحصائيات الجلسة",
            "totalsourcefiles":    "   إجمالي الملفات المصدر : {}",
            "existingfilescount":  "   الملفات الموجودة     : {}",
            "filesadded":          "   الملفات المضافة      : {}",
            "duplicategroups":     "   مجموعات التكرار      : {}",
            "loggedto":            "   تم التسجيل في        ← {}",
            "duplicatefiles":      "   الملفات المكررة:",
            "copies":              "نسخة",
            "unclassifiedfiles":   "⚠️  الملفات غير المصنفة : {}",
            "reasons":             "      السبب    : {}",
            "proposedcategory":    "      الفئة    : {}",
            "moreitems":           "   ... و {} أخرى",
            "loggedtounclassified":"   تم التسجيل في ← {}",
            "checkfulldetails":    "   افتح الملف لرؤية التفاصيل الكاملة",
            "successfullyadded":   "🎉 تمت إضافة {} ملف بنجاح!",
            "duplicatewarning":    "⚠️  تم العثور على {} مجموعة مكررة",
            "unclassifiedwarning": "⚠️  تم العثور على {} ملف غير مصنف",
            "checkunclassified":   "   راجع ← {}",
            "line":                "─" * 60,

            # Console — per-file processing
            "noskillfound":        "⚠️  لم يُعثر على اسم مهارة في '{}' — الاسم الافتراضي: '{}'",
            "nocategoryfound":     "⚠️  لم يُعثر على فئة رئيسية لـ '{}'",
            "nosubcategoryfound":  "⚠️  لم يُعثر على فئة فرعية في '{}' ← '{}'",
            "processingsuccess":   "✅ تمت المعالجة: {}",
            "copyingfile":         "📋 جاري النسخ: {} ← {}",
            "errorreading":        "❌ خطأ في قراءة '{}': {}",
            "errorprocessing":     "❌ خطأ في معالجة '{}': {}",

            # Unclassified log
            "unclassifiedtitle":   "# الملفات غير المصنفة\n",
            "unclassifieddesc":    "هذه الملفات لم يتم تصنيفها تلقائياً. "
                                   "يرجى مراجعتها وتصنيفها يدوياً.\n\n",
            "fileheader":          "\n## {}\n",
            "timestamp":           "- **التاريخ**          : {}",
            "skillname":           "- **اسم المهارة**      : {}",
            "classificationissue": "- **المشكلة**          : {}",
            "proposedmain":        "- **الفئة المقترحة**   : {}",
            "proposedsub":         "- **الفئة الفرعية**    : {}",
            "additionaldetails":   "- **تفاصيل إضافية**    : {}",
            "requiredaction":      "- **الإجراء المطلوب**  : يرجى مراجعة هذا الملف وتصنيفه يدوياً\n",

            # Duplicates log
            "duplicatestitle":      "# تقرير الملفات المكررة\n",
            "duplicatesdesc":       "قائمة بالملفات المكررة التي تم اكتشافها.\n\n",
            "sessionheader":        "\n## جلسة — {}\n",
            "newfilescount":        "- الملفات الجديدة    : {}\n",
            "duplicategroupscount": "- مجموعات التكرار    : {}\n\n",
            "duplicateitem":        "\n### {}\n",
            "skillnameitem":        "- اسم المهارة : {}\n",
            "copiescount":          "- عدد النسخ   : {}\n",
            "duplicatelist":        "- الملفات     :\n",

            # HTML report
            "htmltitle":           "مستودع المهارات",
            "htmlsubtitle":        "تقرير احترافي ثنائي اللغة",
            "totalskills":         "إجمالي المهارات",
            "totalcategories":     "التخصصات الرئيسية",
            "totalfiles":          "الملفات المعالجة",
            "lastupdated":         "آخر تحديث",
            "searchplaceholder":   "ابحث عن مهارة...",
            "noresults":           "لا توجد نتائج تطابق بحثك",
            "footer":              "تم الإنشاء تلقائياً بواسطة نظام تصنيف المهارات",
            "togglelanguage":      "اللغة",
            "skillscount":         "مهارة",
            "nodescription":       "لا يوجد وصف",
            "filelabel":           "📄 ",
            "alldone":             "✅ تم بنجاح!",
            "nofilesfound":        "⚠️  لا توجد ملفات في مجلد المصدر.",
            "apptitle":            "نظام تصنيف المهارات",
        },
    }

    def __init__(self, language: str = "en") -> None:
        self.language: str = language if language in self.TRANSLATIONS else "en"

    # ── Public API ────────────────────────────────────────────────────────────

    def get(self, key: str, *args) -> str:
        """Return the translated string for *key*, formatted with *args*."""
        translation = self.TRANSLATIONS.get(self.language, {}).get(key, key)
        if args:
            try:
                return translation.format(*args)
            except (IndexError, KeyError):
                return translation
        return translation

    def set_language(self, language: str) -> bool:
        """Switch language. Returns True on success, False if unknown."""
        if language in self.TRANSLATIONS:
            self.language = language
            return True
        return False

    def toggle(self) -> str:
        """Switch between AR and EN, return the new language code."""
        self.language = "en" if self.language == "ar" else "ar"
        return self.language

    def is_rtl(self) -> bool:
        """True when the current language is right-to-left."""
        return self.language == "ar"


# Module-level singleton — import this everywhere instead of instantiating
lang = LanguageManager(language="en")
