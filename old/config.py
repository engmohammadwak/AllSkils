"""
config.py
---------
Central configuration: paths, category definitions, keyword maps.
All other modules import from here — never hardcode these values elsewhere.
"""


from pathlib import Path


# ─── Paths ────────────────────────────────────────────────────────────────────────────────────


SOURCE_DIR        = Path(r"slills") # ← Root folder containing skill files
INPUT_DIR         = SOURCE_DIR                             # alias used in main.py
OUTPUT_DIR        = Path("sorted_skills")                  # Output root (relative to cwd)
DATA_FILE         = OUTPUT_DIR / "skills_data.json"
UNCLASSIFIED_FILE = OUTPUT_DIR / "unclassified.md"
DUPLICATES_FILE   = OUTPUT_DIR / "duplicates_report.md"
SIGNATURES_FILE   = OUTPUT_DIR / "file_signatures.json"


# Supported file extensions to scan
SUPPORTED_EXTENSIONS: set[str] = {".md", ".txt"}


# ─── Category order (controls display order in HTML) ────────────────────────────────────────


MAIN_CATEGORIES_ORDER: list[str] = [
    "Web Development",
    "Mobile Development",
    "AI & Machine Learning",
    "Blockchain",
    "DevOps",
    "Design",
    "Data",
    "WordPress",
    "Finance",
    "Programming Languages",
    "Databases",
    "Cloud & Infrastructure",
    "Security",
    "Game Development",
    "Networking",
]


# ─── Display names ─────────────────────────────────────────────────────────────────────────────────


MAIN_CATEGORIES_AR: dict[str, str] = {
    "Web Development":        "تطوير الويب",
    "Mobile Development":     "تطوير التطبيقات",
    "AI & Machine Learning":  "الذكاء الاصطناعي",
    "Blockchain":             "البلوكتشين",
    "DevOps":                 "DevOps",
    "Design":                 "التصميم",
    "Data":                   "البيانات",
    "WordPress":              "ووردبريس",
    "Finance":                "المالية",
    "Programming Languages":  "لغات البرمجة",
    "Databases":              "قواعد البيانات",
    "Cloud & Infrastructure": "السحابة والبنية التحتية",
    "Security":               "الأمان",
    "Game Development":       "تطوير الألعاب",
    "Networking":             "الشبكات",
}


MAIN_CATEGORIES_EN: dict[str, str] = {k: k for k in MAIN_CATEGORIES_ORDER}


# ─── Per-category detection keywords ──────────────────────────────────────────────────────────


MAIN_CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "Web Development": [
        "react", "nextjs", "next.js", "vue", "vuejs", "angular", "svelte", "sveltekit",
        "html", "css", "tailwind", "bootstrap", "webpack", "vite",
        "frontend", "backend", "fullstack", "full-stack",
        "rest api", "graphql", "express", "expressjs",
        "nodejs", "node.js", "django", "spring boot", "springboot",
        "laravel", "fastapi", "nestjs", "rails",
        "web browser", "web-design", "web development",
        "wpcli", "wp-cli", "wp db", "wp search-replace",
        "wordpress plugin", "wordpress theme", "gutenberg", "wpds",
    ],
    "Mobile Development": [
        "android", "ios", "flutter", "react native", "kotlin",
        "swift", "swiftui", "mobile app", "xcode", "android-studio",
        "ionic", "cordova", "capacitor", "xamarin", "expo",
        "mobile development", "dart",
    ],
    "AI & Machine Learning": [
        "llm", "gpt", "gemini", "claude", "llama", "mistral",
        "openai", "chatgpt", "machine learning", "deep learning",
        "tensorflow", "pytorch", "scikit-learn", "nlp", "rag",
        "langchain", "huggingface", "autogen", "neural network",
        "artificial intelligence", "ai model", "fine-tuning",
    ],
    "Blockchain": [
        "blockchain", "web3", "cryptocurrency", "token", "defi", "solidity",
        "smart contract", "ethereum", "solana", "binance", "polygon",
        "dex", "liquidity pool", "cairo", "substrate", "nft",
    ],
    "DevOps": [
        "devops", "docker", "kubernetes", "container", "cicd", "ci/cd",
        "jenkins", "github-actions", "gitlab-ci", "monitoring",
        "observability", "prometheus", "grafana", "terraform",
        "ansible", "pulumi", "helm", "deployment pipeline",
    ],
    "Design": [
        "figma", "prototype", "wireframe",
        "graphic design", "visual design", "brand identity", "typography",
        "motion design", "storybook", "component library",
        "ui design", "ux design", "user interface", "user experience",
    ],
    "Data": [
        "analytics", "business intelligence", "tableau", "powerbi", "power bi",
        "etl", "data pipeline", "data warehouse", "airflow", "kafka",
        "bigquery", "redshift", "snowflake", "data science",
        "data engineering", "data analysis", "dataset",
    ],
    "WordPress": [
        "wordpress", "gutenberg",
        "wp-block", "wp-rest-api", "wp-interactivity",
        "wordpress plugin", "wordpress theme",
    ],
    "Finance": [
        "finance", "stock market", "trading", "investment", "forex",
        "portfolio management", "asset management", "wealth management",
        "financial", "fintech", "accounting",
    ],
    "Programming Languages": [
        "python script", "python code", "python programming",
        "typescript", "rust programming", "golang", "go lang",
        "c++ programming", "c++ code", "cpp programming",
        "c# programming", "csharp", "ruby programming",
        "php programming", "scala", "java programming",
        "swift programming", "kotlin programming",
    ],
    "Databases": [
        "postgresql", "mysql", "sqlite",
        "mongodb", "firebase", "dynamodb", "couchdb", "redis",
        "database design", "firestore", "cosmos-db",
        "sql query", "database schema",
    ],
    "Cloud & Infrastructure": [
        "aws", "azure", "google cloud", "gcp", "cloudflare",
        "cloud infrastructure", "serverless", "lambda function",
        "ec2", "s3 bucket", "amplify", "netlify", "vercel deployment",
    ],
    "Security": [
        "cybersecurity", "encryption", "authentication", "authorization",
        "auth0", "sentry", "security audit", "vulnerability",
        "penetration testing", "jwt", "oauth", "cors",
        "firebase auth", "two-factor", "ssl", "https",
    ],
    "Game Development": [
        "unity", "unreal engine", "gaming", "game development",
        "ue4", "ue5", "game design", "game mechanics",
    ],
    "Networking": [
        "networking", "tcp/ip", "dns", "routing", "firewall",
        "network protocol", "websocket", "socket programming",
        "network configuration", "vpn",
    ],
}


# ─── Technology / framework detection (3rd level) ──────────────────────────────────────────────────


TECH_STACKS: dict[str, dict[str, dict[str, list[str]]]] = {
    "Web Development": {
        "backend": {
            "laravel":   ["laravel", "blade", "eloquent", "artisan", "livewire"],
            "django":    ["django", "drf", "django-rest"],
            "express":   ["express", "expressjs"],
            "fastapi":   ["fastapi", "pydantic", "uvicorn"],
            "spring":    ["spring", "springboot", "spring-boot"],
            "nodejs":    ["nodejs", "node.js"],
            "nestjs":    ["nestjs", "nest.js"],
            "rails":     ["rails", "ruby on rails", "ror"],
            "asp":       ["asp.net", "aspnet", "dotnet", ".net"],
            # ── WordPress operational / design-system skills ──
            "wordpress": [
                "wordpress", "wp-cli", "wpcli", "wp db", "wp search-replace",
                "wp plugin", "wp theme", "wp core", "wp option", "wp user",
                "wpds", "wordpress design system", "wp project",
                "playground blueprint", "wp-project-triage",
            ],
        },
        "frontend": {
            "react":    ["react", "jsx", "react-dom", "react-query"],
            "nextjs":   ["nextjs", "next.js"],
            "vue":      ["vue", "vuejs", "nuxt"],
            "angular":  ["angular", "angularjs"],
            "svelte":   ["svelte", "sveltekit"],
            "tailwind": ["tailwind", "tailwindcss"],
        },
    },
    "Mobile Development": {
        "android":      {"kotlin": ["kotlin"], "java-android": ["java android"]},
        "ios":          {"swift": ["swift", "swiftui"], "objc": ["objective-c"]},
        "flutter":      {"dart": ["dart", "flutter"]},
        "react-native": {"rn": ["react native", "expo"]},
    },
    "Databases": {
        "sql":      {"postgres": ["postgres", "postgresql"], "mysql": ["mysql"], "sqlite": ["sqlite"]},
        "nosql":    {"mongodb": ["mongodb", "mongoose"], "redis": ["redis"], "dynamodb": ["dynamodb"]},
        "firebase": {"firestore": ["firestore", "firebase"]},
    },
    "Cloud & Infrastructure": {
        "aws":   {"ec2": ["ec2"], "s3": ["s3 bucket", "amazon s3"], "lambda": ["lambda function"]},
        "azure": {"azure-ai": ["azure-ai", "azure cognitive"], "azure-db": ["azure cosmos"]},
        "gcp":   {"bigquery": ["bigquery"], "gke": ["gke"]},
    },
    "AI & Machine Learning": {
        "llm-models": {
            "openai":  ["openai", "gpt", "chatgpt"],
            "gemini":  ["gemini", "google ai"],
            "claude":  ["claude", "anthropic"],
            "llama":   ["llama", "meta ai"],
        },
        "ml-models": {
            "pytorch":    ["pytorch"],
            "tensorflow": ["tensorflow", "keras"],
            "sklearn":    ["scikit-learn", "sklearn"],
        },
    },
}


# ─── Sub-category definitions ─────────────────────────────────────────────────────────────────────────────────


SUB_CATEGORIES: dict[str, dict[str, dict]] = {
    "Web Development": {
        "frontend":    {"name": "Frontend",  "keywords": ["react", "nextjs", "next.js", "vue", "angular", "svelte", "html", "css", "frontend", "tailwind", "bootstrap"]},
        "backend":     {"name": "Backend",   "keywords": [
            "backend", "rest api", "graphql", "express", "fastapi", "nodejs", "node.js",
            "django", "spring", "laravel",
            "wpcli", "wp-cli", "wp db", "wp search-replace", "wordpress plugin",
            "wordpress theme", "wpds", "wp project", "playground blueprint",
        ]},
        "fullstack":   {"name": "Fullstack", "keywords": ["fullstack", "full-stack", "mern", "mean"]},
        "image-optimization": {"name": "Image Optimization", "keywords": ["compress-images", "image optimization", "compress image"]},
        "general-web": {"name": "General Web", "keywords": ["web-general", "web-dev", "web-tools", "build-in-public"]},
    },
    "Mobile Development": {
        "android":        {"name": "Android",        "keywords": ["android", "kotlin", "android-studio", "gradle"]},
        "ios":            {"name": "iOS",             "keywords": ["ios", "swift", "swiftui", "xcode", "cocoa", "objective-c"]},
        "flutter":        {"name": "Flutter",         "keywords": ["flutter", "dart"]},
        "react-native":   {"name": "React Native",    "keywords": ["react native", "expo", "cross-platform"]},
        "cross-platform": {"name": "Cross Platform",  "keywords": ["ionic", "cordova", "capacitor", "xamarin"]},
        "general-mobile": {"name": "General Mobile",  "keywords": ["mobile-general", "mobile-dev", "mobile-tools"]},
    },
    "AI & Machine Learning": {
        "llm-models": {"name": "LLM Models",  "keywords": ["gpt", "llm", "gemini", "claude", "llama", "mistral", "openai", "chatgpt"]},
        "ml-models":  {"name": "ML Models",   "keywords": ["machine learning", "deep learning", "tensorflow", "pytorch", "scikit-learn", "nlp", "rag"]},
        "ai-tools":   {"name": "AI Tools",    "keywords": ["langchain", "huggingface", "composio", "autogen"]},
        "azure-ai":   {"name": "Azure AI",    "keywords": ["azure-ai", "azure-cosmos", "document-intelligence"]},
        "general-ai": {"name": "General AI",  "keywords": ["ai-general", "artificial intelligence", "fine-tuning"]},
    },
    "Blockchain": {
        "defi":             {"name": "DeFi",            "keywords": ["defi", "token", "cryptocurrency", "dex", "liquidity pool"]},
        "smart-contracts":  {"name": "Smart Contracts", "keywords": ["smart contract", "solidity", "cairo", "vyper"]},
        "networks":         {"name": "Networks",        "keywords": ["ethereum", "solana", "binance", "polygon", "avalanche"]},
    },
    "DevOps": {
        "containerization": {"name": "Containerization", "keywords": ["docker", "kubernetes", "container", "podman"]},
        "cicd":             {"name": "CI/CD",            "keywords": ["cicd", "ci/cd", "jenkins", "github-actions", "gitlab-ci"]},
        "infrastructure":   {"name": "Infrastructure",   "keywords": ["terraform", "ansible", "pulumi", "infrastructure"]},
        "monitoring":       {"name": "Monitoring",       "keywords": ["monitoring", "observability", "prometheus", "grafana", "datadog"]},
    },
    "Design": {
        "ui-ux":  {"name": "UI/UX",  "keywords": ["ui design", "ux design", "figma", "prototype", "wireframe", "user interface", "user experience"]},
        "visual": {"name": "Visual", "keywords": ["graphic design", "visual design", "brand identity", "typography"]},
        "motion": {"name": "Motion", "keywords": ["motion design", "gsap", "animation"]},
    },
    "Data": {
        "analytics":       {"name": "Analytics",       "keywords": ["analytics", "business intelligence", "tableau", "powerbi", "data science"]},
        "engineering":     {"name": "Engineering",     "keywords": ["etl", "data pipeline", "data warehouse", "airflow", "kafka"]},
        "seo":             {"name": "SEO",             "keywords": ["seo", "search engine optimization", "metadata api", "add-seo"]},
        "data-management": {"name": "Data Management", "keywords": ["dataset", "data management", "dummy data"]},
        "caching":         {"name": "Caching",         "keywords": ["caching", "next-cache", "cache strategy"]},
        "general-data":    {"name": "General Data",    "keywords": ["data flow", "data processing"]},
    },
    "WordPress": {
        "development": {"name": "Development", "keywords": ["wordpress", "gutenberg", "wp-block", "wordpress plugin", "wordpress theme"]},
    },
    "Finance": {
        "trading":    {"name": "Trading",    "keywords": ["trading", "stock market", "forex", "investment"]},
        "investment": {"name": "Investment", "keywords": ["portfolio management", "asset management"]},
    },
    "Programming Languages": {
        "python":     {"name": "Python",     "keywords": ["python"]},
        "javascript": {"name": "JavaScript", "keywords": ["javascript", "typescript"]},
        "java":       {"name": "Java",       "keywords": ["java programming", "java code"]},
        "cpp":        {"name": "C/C++",      "keywords": ["c++", "cpp", "c programming"]},
        "rust":       {"name": "Rust",       "keywords": ["rust programming", "rust lang"]},
        "go":         {"name": "Go",         "keywords": ["golang", "go lang"]},
        "csharp":     {"name": "C#",         "keywords": ["c#", "csharp", ".net"]},
        "php":        {"name": "PHP",        "keywords": ["php programming", "php code"]},
        "general-programming": {"name": "General", "keywords": ["programming-general", "software development", "coding"]},
    },
    "Databases": {
        "sql":        {"name": "SQL",        "keywords": ["postgresql", "mysql", "sqlite", "sql query"]},
        "nosql":      {"name": "NoSQL",      "keywords": ["mongodb", "dynamodb", "couchdb", "redis"]},
        "firebase":   {"name": "Firebase",   "keywords": ["firebase", "firestore", "firebase auth"]},
        "general-db": {"name": "General DB", "keywords": ["database design", "database schema", "db tools"]},
    },
    "Cloud & Infrastructure": {
        "aws":           {"name": "AWS",           "keywords": ["aws", "ec2", "s3 bucket", "lambda function"]},
        "azure":         {"name": "Azure",         "keywords": ["azure"]},
        "gcp":           {"name": "GCP",           "keywords": ["gcp", "google cloud"]},
        "cloudflare":    {"name": "Cloudflare",    "keywords": ["cloudflare"]},
        "netlify":       {"name": "Netlify",       "keywords": ["netlify", "edge-functions"]},
        "general-cloud": {"name": "General Cloud", "keywords": ["cloud deployment", "serverless"]},
    },
    "Security": {
        "authentication": {"name": "Authentication", "keywords": ["authentication", "authorization", "auth0", "jwt", "oauth", "two-factor"]},
        "audit":          {"name": "Audit",          "keywords": ["security audit", "vulnerability", "penetration testing", "sentry"]},
    },
    "Game Development": {
        "unity":   {"name": "Unity",   "keywords": ["unity", "c#"]},
        "unreal":  {"name": "Unreal",  "keywords": ["unreal engine", "ue4", "ue5"]},
        "metrics": {"name": "Metrics", "keywords": ["game metrics", "gaming analytics"]},
    },
    "Networking": {
        "networking": {"name": "Networking", "keywords": ["networking", "tcp/ip", "dns", "routing", "firewall"]},
    },
}
