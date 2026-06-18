# 📚 AllSkills — نظام تصنيف المهارات التلقائي

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge)

**نظام Python يصنف ملفات Markdown تلقائياً إلى تصنيفات ذكية، ويولّد تقرير HTML تفاعلي ثنائي اللغة.**

</div>

---

## ✨ المميزات

- 🔍 **تصنيف تلقائي** — يكتشف التصنيف الرئيسي والفرعي والتقنية من محتوى الملف
- 🌐 **ثنائي اللغة** — دعم كامل للعربية والإنجليزية في التقرير
- 🎨 **تقرير HTML** — واجهة تفاعلية بتصميم Dark Mode مع بحث فوري
- 🔄 **كشف التكرار** — يتعرف على الملفات المكررة عبر hash المحتوى
- 📊 **17 تصنيفاً رئيسياً** — Web, Mobile, AI, DevOps, Security وغيرها
- ⚡ **معالجة تدريجية** — لا يُعيد معالجة الملفات الموجودة

---

## 🗂️ هيكل المشروع

```
AllSkills/
├── NEW/
│   ├── run.py              ← 🚀 نقطة التشغيل الرئيسية
│   ├── ruun.py             ← 🔧 Git Manager (رفع/تنزيل)
│   ├── main.py             ← ⚙️ منسق العمليات
│   ├── mainFile/
│   │   ├── classifier.py   ← 🧠 محرك التصنيف
│   │   ├── config.py       ← ⚙️ الإعدادات والتصنيفات
│   │   ├── html_generator.py ← 🎨 مولّد HTML
│   │   └── language.py     ← 🌐 إدارة اللغات
│   ├── slills/             ← 📥 ملفات Markdown المصدر
│   └── sorted_skills/      ← 📤 الملفات المصنفة + التقرير
└── old/                    ← 📦 النسخ القديمة
```

---

## 🚀 طريقة التشغيل

### المتطلبات
```bash
pip install colorama tqdm
```

### التشغيل
```bash
cd NEW
python run.py
```

### Git Manager
```bash
python ruun.py
# اختر: 1 رفع | 2 تنزيل | 3 إعادة ضبط
```

---

## 📂 التصنيفات المدعومة

| التصنيف | Sub-categories |
|---------|----------------|
| 🌐 Web Development | Frontend, Backend, Fullstack, API, Auth |
| 📱 Mobile Development | Android, iOS, Flutter, React Native |
| 🧠 AI & Machine Learning | LLMs, ML Models, Agents, Computer Vision |
| ⚙️ DevOps | Docker, CI/CD, Monitoring, Servers |
| 🗄️ Databases | SQL, NoSQL, Redis, Firebase, Vector DB |
| ☁️ Cloud & Infrastructure | AWS, Azure, GCP, Cloudflare, Hosting |
| 🔐 Security | Auth, AppSec, Pentest, Forensics |
| 🎮 Game Development | Unity, Unreal, Godot, Web Games |
| + 9 تصنيفات أخرى | Blockchain, Data, WordPress, Finance... |

---

## 📤 المخرجات

بعد التشغيل ستجد في `sorted_skills/`:

```
sorted_skills/
├── Web Development/
│   ├── backend/
│   │   └── laravel/        ← مثال: ملفات Laravel
│   └── frontend/
│       └── react/
├── skills_data.json        ← بيانات JSON الكاملة
├── index.html              ← تقرير HTML تفاعلي
├── unclassified.md         ← ملفات تحتاج مراجعة يدوية
└── duplicates_report.md    ← تقرير الملفات المكررة
```

---

## ⚙️ الإعدادات

في `mainFile/config.py` يمكنك تخصيص:

- **`SOURCE_DIR`** — مجلد ملفات Markdown المصدر
- **`OUTPUT_DIR`** — مجلد الإخراج
- **`MAIN_CATEGORY_KEYWORDS`** — كلمات مفتاحية للتصنيف الرئيسي
- **`SUB_CATEGORIES`** — التصنيفات الفرعية وكلماتها المفتاحية
- **`TECH_STACKS`** — التقنيات المحددة (المستوى الثالث)

---

## 🤝 المساهمة

1. Fork المشروع
2. أنشئ branch جديد: `git checkout -b feature/my-feature`
3. Commit التغييرات: `git commit -m 'Add: feature'`
4. Push: `git push origin feature/my-feature`
5. افتح Pull Request

---

<div align="center">
صُنع بـ ❤️ بواسطة <a href="https://github.com/engmohammadwak">engmohammadwak</a>
</div>
