import re
import shutil
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter
from colorama import init, Fore, Style

# تهيئة colorama
init(autoreset=True)

SOURCE_DIR = Path(r"C:\Users\MWAK\OneDrive\سطح المكتب\slills")
OUTPUT_DIR = Path("sorted_skills")
MAX_FILENAME_LENGTH = 50  # Maximum length for the name part before extension
MAX_TOTAL_PATH = 240  # Leave room for the directory path

def slugify(text, max_length=50):
    """Convert text to valid filename with length limit"""
    # Remove common prefixes
    text = re.sub(r'^(skill|build|how to|guide|tutorial)\s+', '', text, flags=re.IGNORECASE)
    
    # Convert to lowercase and replace invalid chars
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    text = re.sub(r'-+', '-', text)
    text = text.strip('-')
    
    # Truncate to max length, keeping whole words if possible
    if len(text) > max_length:
        # Try to cut at a word boundary
        truncated = text[:max_length]
        last_hyphen = truncated.rfind('-')
        if last_hyphen > max_length // 2:  # Only cut at hyphen if it's not too short
            text = truncated[:last_hyphen]
        else:
            text = truncated
    
    return text

def extract_skill_name(content, fallback_name):
    """Extract skill name from file content"""
    # Try to extract name from name: field
    match = re.search(r'^name:\s*(.+)$', content, re.MULTILINE)
    if match:
        name = match.group(1).strip()
        name = re.sub(r'\s*\(\d+\)\s*$', '', name)
        name = re.sub(r'\s*-\s*\d{4}-\d{2}-\d{2}T\d{6}\.\d{3}\s*$', '', name)
        return name
    
    # Try to extract from first non-empty line
    lines = content.split('\n')
    for line in lines[:20]:
        line = line.strip()
        if not line:
            continue
        
        if line.startswith('#') or line.startswith('```') or line.startswith('---'):
            continue
        
        clean_name = re.sub(r'^#\s*', '', line)
        clean_name = re.sub(r'\s*\(skill\)$', '', clean_name, flags=re.IGNORECASE)
        clean_name = re.sub(r'\s*-\s*\d{4}-\d{2}-\d{2}T\d{6}\.\d{3}\s*$', '', clean_name)
        clean_name = re.sub(r'\s*\(\d+\)\s*$', '', clean_name)
        
        if clean_name and len(clean_name) > 3:
            return clean_name.strip()
    
    # Fallback to cleaned filename
    clean_name = re.sub(r'^SKILL\s*\(?\d+\)?\s*-\s*', '', fallback_name)
    clean_name = re.sub(r'\s*\(\d+\)\s*$', '', clean_name)
    clean_name = re.sub(r'-\s*\d{4}-\d{2}-\d{2}T\d{6}\.\d{3}$', '', clean_name)
    clean_name = re.sub(r'^SKILL\s+', '', clean_name)
    clean_name = re.sub(r'^SKILL-', '', clean_name)
    
    if clean_name and clean_name != fallback_name:
        return clean_name.strip()
    
    return fallback_name

def get_file_signature(content, file_size):
    """Create a signature of the file using size and content hash"""
    normalized = re.sub(r'\s+', ' ', content.strip())
    content_sig = normalized[:300]
    return f"{file_size}|{content_sig}"

def get_unique_filename(base_name, output_dir, used_names, counter_offset=0):
    """Get unique filename with length limitations"""
    # Clean and truncate the base name
    clean_name = slugify(base_name, MAX_FILENAME_LENGTH)
    
    if not clean_name:
        clean_name = "unnamed"
    
    # Check if the full path would be too long
    filename = clean_name + ".md"
    counter = 1 + counter_offset
    
    while (output_dir / filename).exists() or filename in used_names:
        # Add counter to filename
        # Reserve space for counter: -1, -2, etc.
        max_name_len = MAX_FILENAME_LENGTH - len(f" -{counter}") 
        if max_name_len < 10:
            # If name is too short, use hash instead
            import hashlib
            short_hash = hashlib.md5(base_name.encode()).hexdigest()[:8]
            filename = f"skill-{short_hash}-{counter}.md"
        else:
            clean_base = slugify(base_name, max_name_len)
            filename = f"{clean_base}-{counter}.md"
        counter += 1
    
    used_names.add(filename)
    return filename

def main():
    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Find all .md files
    files = list(SOURCE_DIR.glob("*.md"))
    
    print(Fore.CYAN + "\n📂" + Style.BRIGHT + f" Found {len(files)} Markdown files\n")
    print(Fore.WHITE + "="*60)
    
    # Dictionary to track files by signature
    file_groups = defaultdict(list)
    
    # First pass: read all files and group them
    for file in files:
        try:
            content = file.read_text(encoding="utf-8", errors="ignore")
            file_size = file.stat().st_size
            skill_name = extract_skill_name(content, file.stem)
            
            if not skill_name or skill_name == file.stem or len(skill_name) < 3:
                lines = content.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#') and not line.startswith('```'):
                        clean = re.sub(r'[^a-zA-Z0-9\s\-_\u0600-\u06FF]', '', line)
                        if len(clean) > 3:
                            skill_name = clean
                            break
            
            if not skill_name or len(skill_name) < 2:
                skill_name = file.stem
            
            signature = get_file_signature(content, file_size)
            
            file_groups[signature].append({
                'file': file,
                'content': content,
                'skill_name': skill_name,
                'original_name': file.name,
                'file_size': file_size
            })
            
        except Exception as e:
            print(Fore.RED + f"❌ Error reading {file.name}: {e}")
    
    # Process files
    success_count = 0
    duplicate_removed = 0
    used_names = set()
    all_skill_names = []
    total_duplicates_found = 0
    
    # Second pass: process each group
    for signature, files_list in file_groups.items():
        if len(files_list) == 1:
            file_info = files_list[0]
            all_skill_names.append(file_info['skill_name'])
            new_filename = get_unique_filename(file_info['skill_name'], OUTPUT_DIR, used_names)
            destination = OUTPUT_DIR / new_filename
            try:
                shutil.copy2(file_info['file'], destination)
                success_count += 1
            except OSError as e:
                print(Fore.RED + f"❌ Error copying {file_info['original_name']}: {e}")
                # Try with a shorter name
                short_name = slugify(file_info['skill_name'], 20)
                new_filename = f"{short_name}-{hash(file_info['skill_name']) % 10000}.md"
                destination = OUTPUT_DIR / new_filename
                try:
                    shutil.copy2(file_info['file'], destination)
                    success_count += 1
                    print(Fore.YELLOW + f"   ⚠️  Renamed to: {new_filename}")
                except OSError as e2:
                    print(Fore.RED + f"❌ Failed again: {e2}")
        else:
            # Multiple files with same signature - keep only the first one
            first_file = files_list[0]
            all_skill_names.append(first_file['skill_name'])
            new_filename = get_unique_filename(first_file['skill_name'], OUTPUT_DIR, used_names)
            destination = OUTPUT_DIR / new_filename
            try:
                shutil.copy2(first_file['file'], destination)
                success_count += 1
                duplicate_removed += len(files_list) - 1
                
                # Show which duplicates were removed
                print(Fore.YELLOW + f"\n   🗑️  Found {len(files_list)} identical files (size: {first_file['file_size']} bytes):")
                print(Fore.GREEN + f"      ✅ Keeping: {first_file['original_name']} -> {new_filename}")
                for i, file_info in enumerate(files_list[1:], 1):
                    print(Fore.RED + f"      ❌ Removing: {file_info['original_name']}")
            except OSError as e:
                print(Fore.RED + f"❌ Error copying {first_file['original_name']}: {e}")
    
    # Calculate statistics
    name_counts = Counter(all_skill_names)
    duplicates = {name: count for name, count in name_counts.items() if count > 1}
    unique_names = len(name_counts)
    
    # Display statistics
    print(Fore.WHITE + "\n" + "="*60)
    print(Fore.YELLOW + Style.BRIGHT + "📊 PROCESSING STATISTICS:")
    print(Fore.WHITE + "="*60)
    print(Fore.CYAN + f"📄 Total files found: {Style.BRIGHT}{len(files)}")
    print(Fore.GREEN + f"✅ Files kept: {Style.BRIGHT}{success_count}")
    print(Fore.RED + f"🗑️  Duplicates removed: {Style.BRIGHT}{duplicate_removed}")
    print(Fore.MAGENTA + f"📝 Unique skill names: {Style.BRIGHT}{unique_names}")
    print(Fore.YELLOW + f"🔄 Names with duplicates (different content): {Style.BRIGHT}{len(duplicates)}")
    print(Fore.CYAN + f"📁 Output folder: {Style.BRIGHT}{OUTPUT_DIR}")
    print(Fore.CYAN + f"📅 Date: {Style.BRIGHT}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Display duplicate names (different content)
    if duplicates:
        print(Fore.WHITE + "\n" + "="*60)
        print(Fore.RED + Style.BRIGHT + "🔄 DUPLICATE NAMES (Different Content):")
        print(Fore.WHITE + "="*60)
        sorted_dups = sorted(duplicates.items(), key=lambda x: x[1], reverse=True)
        for name, count in sorted_dups[:20]:
            display_name = name[:50] + '...' if len(name) > 50 else name
            print(Fore.YELLOW + f"   • {display_name} → {count} different versions")
        if len(sorted_dups) > 20:
            print(Fore.WHITE + f"   ... and {len(sorted_dups) - 20} more")
        print(Fore.WHITE + "-"*60)
        print(Fore.GREEN + Style.BRIGHT + f"✅ These were kept with numbers (-1, -2) because content differs")
    else:
        print(Fore.GREEN + Style.BRIGHT + "\n✅ No duplicate names found!")
    
    print(Fore.WHITE + "\n" + "="*60)
    print(Fore.CYAN + Style.BRIGHT + f"✨ {success_count} unique files renamed and organized successfully!")
    if duplicate_removed > 0:
        print(Fore.GREEN + Style.BRIGHT + f"🗑️  {duplicate_removed} duplicate files removed (identical size & content)")

if __name__ == "__main__":
    main()