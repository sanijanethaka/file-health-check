import ollama
from pathlib import Path
from folder_map import get_folder_map
from scan import scan_folder, choose_keeper

MODEL = "gemma4"
folder = Path("test-folder")

folder_map = get_folder_map(folder)
results = scan_folder(folder)

# Decide deletions in code: every duplicate except the keeper
to_delete = set()
for group in results["duplicate_groups"]:
    keeper = choose_keeper(group)
    for path in group:
        if path != keeper:
            to_delete.add(path)

# Only show the AI files that will remain after duplicates are removed
clean_map = []
for entry in folder_map:
    path = entry.split("  (modified")[0]
    if path not in to_delete:
        clean_map.append(entry)
file_list = "\n".join(clean_map)

old_lines = []
for path, age in results["old_files"]:
    if path not in to_delete:
        old_lines.append(f"{path} ({age // 365} years old)")
old_text = "\n".join(old_lines) or "None"

prompt = f"""You are an expert at organising business files.

FOLDER CONTENTS (names and last-modified dates only):
{file_list}

FILES CONFIRMED AS OLD (not changed in over 2 years):
{old_text}

YOUR TASKS:
1. Suggest a clean folder structure, at most 3 levels deep, shown as an indented tree. Include an Archive folder.
2. Suggest a file naming convention, with 2 examples renaming real files from the list.
3. Pick up to 10 files and say which new folder each should move to.

RULES YOU MUST FOLLOW:
- Do NOT suggest deleting any files. Duplicates have already been handled.
- Only files listed under FILES CONFIRMED AS OLD may go to the Archive folder.
- The current year is 2026.
- Dates in file names use YYYY-MM-DD. Only use the real modified dates shown above. Never invent dates.
- New file names must never contain "final", "copy", "new" or numbers in brackets like "(1)".
- Always keep the original file extension.
- Your own examples must follow every rule above.
- Only refer to files that appear in the list above, spelled exactly as shown.

Be practical and concise."""

print(f"Asking {MODEL} to analyse {len(clean_map)} items ({len(to_delete)} duplicates already removed)...\n")

response = ollama.chat(
    model=MODEL,
    messages=[{"role": "user", "content": prompt}],
)

print(response["message"]["content"])