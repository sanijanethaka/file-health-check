import ollama
from pathlib import Path
from folder_map import get_folder_map

MODEL = "gemma4"
folder = Path("test-folder")

folder_map = get_folder_map(folder)
file_list = "\n".join(folder_map)

prompt = f"""You are an expert at organising business files.

Below is the current structure of a shared folder (file and folder names only):

{file_list}

Your tasks:
1. Suggest a clean folder structure, at most 3 levels deep, shown as an indented tree.
2. Suggest a simple file naming convention, with 2 examples based on real files from the list.
3. Pick up to 10 specific files from the list and say which new folder each should move to.

Rules you must follow:
- The current year is 2026.
- Dates in file names must use the format YYYY-MM-DD.
- File names must never contain "final", "copy", "new" or numbers in brackets like "(1)".
- Always keep the original file extension.
- Your own examples must follow every rule above.
- Only refer to files that appear in the list above.

Be practical and concise."""

print(f"Asking {MODEL} to analyse {len(folder_map)} items... (this can take a minute)\n")

response = ollama.chat(
    model=MODEL,
    messages=[{"role": "user", "content": prompt}],
)

print(response["message"]["content"])