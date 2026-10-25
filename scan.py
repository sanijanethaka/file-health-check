from pathlib import Path
from collections import Counter, defaultdict
import hashlib
import re
import time

OLD_AFTER_DAYS = 730
MAX_DEPTH = 5
WARNING_WORDS = ["copy", "final", "v2", "v3", "backup"]


def scan_folder(folder):
    """Scan a folder and return the findings as a dictionary."""
    total_files = 0
    total_size = 0
    file_types = Counter()
    fingerprints = defaultdict(list)
    bad_names = []
    old_files = []
    deep_files = []
    now = time.time()

    for file in folder.rglob("*"):
        if not file.is_file():
            continue

        relative = str(file.relative_to(folder))
        size = file.stat().st_size

        total_files += 1
        total_size += size
        extension = file.suffix.lower() or "(no extension)"
        file_types[extension] += 1

        fingerprint = hashlib.sha256(file.read_bytes()).hexdigest()
        fingerprints[fingerprint].append((relative, size))

        name = file.stem.lower()
        found_words = [word for word in WARNING_WORDS if word in name]
        if re.search(r"\(\d+\)", name):
            found_words.append("(number)")
        if found_words:
            bad_names.append((relative, found_words))

        age_days = int((now - file.stat().st_mtime) / (60 * 60 * 24))
        if age_days > OLD_AFTER_DAYS:
            old_files.append((relative, age_days))

        depth = len(file.relative_to(folder).parts) - 1
        if depth > MAX_DEPTH:
            deep_files.append((relative, depth))

    duplicate_groups = []
    wasted_size = 0
    for copies in fingerprints.values():
        if len(copies) > 1:
            duplicate_groups.append([path for path, size in copies])
            wasted_size += copies[0][1] * (len(copies) - 1)

    return {
        "total_files": total_files,
        "total_size": total_size,
        "file_types": file_types,
        "duplicate_groups": duplicate_groups,
        "wasted_size": wasted_size,
        "bad_names": bad_names,
        "old_files": old_files,
        "deep_files": deep_files,
    }

def name_score(path):
    """Lower score = cleaner name. Used to pick which duplicate to keep."""
    name = Path(path).stem.lower()
    bad_words = sum(1 for word in WARNING_WORDS if word in name)
    if re.search(r"\(\d+\)", name):
        bad_words += 1
    depth = len(Path(path).parts)
    return (bad_words, depth, len(name))


def choose_keeper(group):
    """Pick the best file to keep from a group of identical duplicates."""
    return min(group, key=name_score)


def print_report(results):
    """Print the scan results in a readable way."""
    mb = 1024 * 1024

    print(f"Total files: {results['total_files']}")
    print(f"Total size: {results['total_size'] / mb:.2f} MB")
    print("File types:")
    for extension, count in results["file_types"].most_common():
        print(f"  {extension}: {count}")

    print(f"\nDuplicate groups ({len(results['duplicate_groups'])}):")
    for group in results["duplicate_groups"]:
        keeper = choose_keeper(group)
        print(f"  Keep:   {keeper}")
        for path in group:
            if path != keeper:
                print(f"  Delete: {path}")
        print()
    if results["duplicate_groups"]:
        print(f"Wasted space: {results['wasted_size'] / mb:.2f} MB")

    print(f"\nBadly named files ({len(results['bad_names'])}):")
    for path, words in results["bad_names"]:
        print(f"  - {path}  (contains: {', '.join(words)})")

    print(f"\nOld files, not changed in {OLD_AFTER_DAYS} days ({len(results['old_files'])}):")
    for path, age in results["old_files"]:
        print(f"  - {path}  ({age} days old)")

    print(f"\nFiles more than {MAX_DEPTH} folders deep ({len(results['deep_files'])}):")
    for path, depth in results["deep_files"]:
        print(f"  - {path}  ({depth} levels)")


if __name__ == "__main__":
    results = scan_folder(Path("test-folder"))
    print_report(results)