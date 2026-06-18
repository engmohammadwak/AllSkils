# run.py
import sys
from pathlib import Path

ROOT = Path(__file__).parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# استدعي classifier مباشرة
from mainFile import classifier
from mainFile.config import SOURCE_DIR

if __name__ == "__main__":
    source_files = list(SOURCE_DIR.rglob("*.md"))
    classifier.run_classification(source_files)