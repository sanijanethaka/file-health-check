from pathlib import Path
import time


def get_folder_map(folder, max_items=300):
    """Return a list of file and folder paths, with last-modified dates for files."""
    paths = []
    for item in sorted(folder.rglob("*")):
        if item.name.startswith("."):
            continue
        relative = item.relative_to(folder)
        if item.is_dir():
            paths.append(f"{relative}/")
        else:
            modified = time.strftime("%Y-%m-%d", time.localtime(item.stat().st_mtime))
            paths.append(f"{relative}  (modified {modified})")
        if len(paths) >= max_items:
            break
    return paths


if __name__ == "__main__":
    folder = Path("test-folder")
    folder_map = get_folder_map(folder)
    print(f"{len(folder_map)} items:")
    for path in folder_map:
        print(path)