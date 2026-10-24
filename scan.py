from pathlib import Path
from collections import Counter, defaultdict
import hashlib
import re
import time

folder = Path("test-folder")

OLD_AFTER_DAYS = 730
MAX_DEPTH = 5
WARNING_WORDS = ["copy", "final", "v2", "v3", "backup"]

total_files = 0
total_size = 0
file_types = Counter()
fingerprints = defaultdict(list)
bad_names = []
old_files = []
deep_files = []

now = time.time()

for file in folder.rglob("*"):
    if file.is_file():
        total_files += 1
        total_size += file.stat().st_size
        extension = file.suffix.lower() or "(no extension)"
        file_types[extension] +=1

        fingerprint = hashlib.sha256(file.read_bytes()).hexdigest()
        fingerprints[fingerprint].append(file)

        name = file.stem.lower()
        found_words = [word for word in WARNING_WORDS if word in name]
        if re.search(r"\(\d+\)", name):
            found_words.append("(number)")
        if found_words:
            bad_names.append((file, found_words))

        age_days = (now - file.stat().st_mtime) / (60 * 60 * 24)
        if age_days > OLD_AFTER_DAYS:
            old_files.append((file, int(age_days)))

        depth = len(file.relative_to(folder).parts) - 1
        if depth > MAX_DEPTH:
            deep_files.append((file, depth))

total_mb = total_size / (1024 * 1024)

print(f"Total files: {total_files}")
print(f"Total size: {total_mb:.2f} MB")
print("File Types: ")
for extension, count in file_types.most_common():
    print(f" {extension}: {count}")

print("\nDuplicate Files: ")
duplicate_groups = 0
wasted_size = 0

for fingerprint, files in fingerprints.items():
    if len(files) > 1:
        duplicate_groups += 1
        wasted_size += files[0].stat().st_size * (len(files) - 1)
        print(f" Same Content ({len(files)} copies)")
        for f in files:
            print(f"     -{f.name}")

if duplicate_groups == 0:
    print(" None found")
else:
    print(f"Wasted space: {wasted_size / (1024 * 1024):.2f} MB")

print(f"\nBadly named files ({len(bad_names)}):")
if bad_names:
    for file, words in bad_names:
        print(f" -{file.name}  (contains: {', '.join(words)})")
else:
        print(" None found")

print(f"\nOld files, not changed in {OLD_AFTER_DAYS} days ({len(old_files)}):")
if old_files:
    for file, age in old_files:
        print(f" -{file.name} ({age} days old)")
else:
    print(" None found")

print(f"\nFiles buried more than {MAX_DEPTH} folders deep ({len(deep_files)}):")
if deep_files:
    for file, depth in deep_files:
        print(f"  -{file.relative_to(folder)}  ({depth} levels)")
else:
    print("  None found")