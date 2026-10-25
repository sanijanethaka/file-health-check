import ollama
from pathlib import Path
from folder_map import get_folder_map
from scan import scan_folder

MODEL = "gemma4"
folder = Path("test-folder")

folder_map = get_folder_map(folder)
results = scan_folder(folder)

file_list = "\n".join(folder_map)

duplicate_lines = []
for number, group in enumerate(results["duplicate_groups"], start=1):
    duplicate_lines.append(f"Group {number}: " + " | ".join(group))
duplicates_text = "\n".join(duplicate_lines) or "None"

old_lines = []
for path, age in results["old_files"]:
    old_lines.append(f"{path} ({age // 365} years old)")
old_text = "\n".join(old_lines) or "None"

prompt = f"""You are an expert at organising business files.

FOLDER CONTENTS (names and last-modified dates only):
{file_list}

SCAN FINDINGS (checked by software, treat these as facts):
Identical duplicate files (same content, different names):
{duplicates_text}

Files not changed in over 2 years:
{old_text}

YOUR TASKS:
1. Suggest a clean folder structure, at most 3 levels deep, shown as an indented tree. Include an Archive folder.
2. Suggest a file naming convention, with 2 examples renaming real files from the list.
3. For each duplicate group, say which ONE file to keep and that the others can be deleted. Prefer the cleanest name.
4. Pick up to 10 files and say which new folder each should move to. Old files go to the Archive folder.

RULES YOU MUST FOLLOW:
- The current year is 2026.
- Dates in file names use YYYY-MM-DD. Only use the real modified dates shown above. Never invent dates.
- New file names must never contain "final", "copy", "new" or numbers in brackets like "(1)".
- Always keep the original file extension.
- Your own examples must follow every rule above.
- Only refer to files that appear in the list above, spelled exactly as shown.

Be practical and concise."""

print(f"Asking {MODEL} to analyse {len(folder_map)} items and {len(results['duplicate_groups'])} duplicate groups...\n")

response = ollama.chat(
    model=MODEL,
    messages=[{"role": "user", "content": prompt}],
)

print(response["message"]["content"])