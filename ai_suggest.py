import ollama
from collections import defaultdict
from pathlib import Path
from typing import Literal
from pydantic import BaseModel
from folder_map import get_folder_map
from scan import scan_folder, choose_keeper

MODEL = "gemma4"
REVIEW_FOLDER = "_To Review"
folder = Path("demo-drive")


# The exact shape we want the AI's answer in
class Placement(BaseModel):
    file: str
    folder: str
    confidence: Literal["high", "medium", "low"]
    reason: str


class Plan(BaseModel):
    placements: list[Placement]


def decide_destinations(plan, loose_files, allowed_folders):
    """Turn AI suggestions into final destinations. Anything doubtful goes to review."""
    destinations = {}
    for p in plan.placements:
        if p.file not in loose_files or p.file in destinations:
            continue
        folder_name = p.folder.strip("/")
        if folder_name not in allowed_folders:
            destinations[p.file] = (REVIEW_FOLDER, f"AI suggested unknown folder '{p.folder}'")
        elif p.confidence != "high":
            destinations[p.file] = (REVIEW_FOLDER, f"{p.confidence} confidence: {p.reason}")
        else:
            destinations[p.file] = (folder_name, p.reason)

    for file in loose_files:
        if file not in destinations:
            destinations[file] = (REVIEW_FOLDER, "AI did not place this file")
    return destinations


# ---------- STAGE 1: gather the facts with code ----------
folder_map = get_folder_map(folder)
results = scan_folder(folder)

to_delete = {}
for group in results["duplicate_groups"]:
    keeper = choose_keeper(group)
    for path in group:
        if path != keeper:
            to_delete[path] = keeper

existing_folders = set()
loose_entries = []
loose_files = set()
for entry in folder_map:
    path = entry.split("  (modified")[0]
    if path.endswith("/"):
        existing_folders.add(path.strip("/"))
    elif "/" not in path and path not in to_delete:
        loose_entries.append(entry)
        loose_files.add(path)

allowed_folders = existing_folders | {REVIEW_FOLDER}

# ---------- STAGE 2: ask the AI to sort the loose files ----------
folders_text = "\n".join(sorted(allowed_folders))
files_text = "\n".join(loose_entries)

prompt = f"""You are helping tidy a company's shared drive.

EXISTING FOLDERS (you may ONLY use these):
{folders_text}

LOOSE FILES TO SORT (names and last-modified dates):
{files_text}

For every loose file, choose the single best folder from the list.
- Use "{REVIEW_FOLDER}" if no folder clearly fits, or the file name is too vague to tell.
- confidence: "high" only if you are sure. Otherwise "medium" or "low".
- reason: a few words explaining your choice.
- Use file names exactly as shown, without the modified date.
- Never invent folders."""

print(f"Asking {MODEL} to sort {len(loose_files)} loose files into {len(existing_folders)} folders...\n")

response = ollama.chat(
    model=MODEL,
    messages=[{"role": "user", "content": prompt}],
    format=Plan.model_json_schema(),
    options={"temperature": 0, "seed": 42},
)
plan = Plan.model_validate_json(response["message"]["content"])

# ---------- STAGE 3: the code makes the final decisions ----------
destinations = decide_destinations(plan, loose_files, allowed_folders)

# ---------- STAGE 4: show the plan ----------
print(f"DUPLICATES TO DELETE ({len(to_delete)}):")
for path, keeper in sorted(to_delete.items()):
    print(f"  - {path}  (copy of {keeper})")

by_folder = defaultdict(list)
for file, (destination, reason) in destinations.items():
    by_folder[destination].append((file, reason))

print(f"\nFILES TO MOVE ({len(destinations)}):")
for destination in sorted(by_folder):
    print(f"\n  {destination}/")
    for file, reason in by_folder[destination]:
        print(f"    - {file}  ({reason})")