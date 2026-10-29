import html
import time
import webbrowser
from pathlib import Path
from scan import scan_folder, choose_keeper

folder = Path("demo-drive")
REPORT_FILE = Path("report.html")

# Maximum marks each problem can take away (adds up to 100)
WEIGHTS = {"duplicates": 30, "loose": 25, "bad_names": 20, "old": 15, "deep": 10}

LABELS = {
    "duplicates": "Duplicate copies",
    "loose": "Loose files (not in a folder)",
    "bad_names": "Badly named files",
    "old": "Old files (2+ years)",
    "deep": "Files buried too deep",
}


def calculate_score(results):
    """Start at 100 and take away marks for each problem."""
    total = results["total_files"]
    if total == 0:
        return 100, []

    counts = {
        "duplicates": sum(len(group) - 1 for group in results["duplicate_groups"]),
        "loose": len(results["loose_files"]),
        "bad_names": len(results["bad_names"]),
        "old": len(results["old_files"]),
        "deep": len(results["deep_files"]),
    }

    score = 100
    breakdown = []
    for problem, max_marks in WEIGHTS.items():
        marks_lost = round(counts[problem] / total * max_marks)
        score -= marks_lost
        breakdown.append((problem, counts[problem], marks_lost))
    return score, breakdown


def grade(score):
    """Turn a score into a label and a colour."""
    if score >= 85:
        return "Healthy", "#1a7f37"
    if score >= 70:
        return "Fair", "#b08800"
    if score >= 50:
        return "Needs attention", "#d1600b"
    return "Critical", "#cf222e"


def readable_size(num_bytes):
    """Show a size in bytes, KB, MB or GB, whichever reads best."""
    if num_bytes < 1024:
        return f"{num_bytes} bytes"
    if num_bytes < 1024 ** 2:
        return f"{num_bytes / 1024:.1f} KB"
    if num_bytes < 1024 ** 3:
        return f"{num_bytes / 1024 ** 2:.1f} MB"
    return f"{num_bytes / 1024 ** 3:.1f} GB"


def build_html(folder, results, score, breakdown):
    """Build the full report as one HTML page."""
    label, colour = grade(score)
    e = html.escape

    rows = ""
    for problem, count, marks_lost in breakdown:
        marks_text = f"-{marks_lost}" if marks_lost else "0"
        rows += f"<tr><td>{LABELS[problem]}</td><td>{count}</td><td>{marks_text}</td></tr>"

    duplicates = ""
    for group in results["duplicate_groups"]:
        keeper = choose_keeper(group)
        duplicates += f"<li><b>Keep:</b> {e(keeper)}<ul>"
        for path in group:
            if path != keeper:
                duplicates += f"<li>Delete: {e(path)}</li>"
        duplicates += "</ul></li>"
    duplicates = duplicates or "<li>None found</li>"

    old = ""
    for path, age in results["old_files"]:
        old += f"<li>{e(path)} <span class='muted'>({age // 365} years old)</span></li>"
    old = old or "<li>None found</li>"

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>File Health Report</title>
<style>
  body {{ font-family: -apple-system, Helvetica, Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; color: #222; }}
    .score {{ font-size: 64px; font-weight: bold; color: {colour}; }}
    .label {{ font-size: 24px; color: {colour}; margin-bottom: 24px; }}
    .cards {{ display: flex; gap: 12px; margin: 24px 0; }}
    .cards {{ display: flex; flex-wrap: wrap; gap: 12px; margin: 24px 0; }}
    .card {{ flex: 1; background: #f4f5f7; border-radius: 8px; padding: 16px; }}
    .card b {{ display: block; font-size: 24px; }}
  table {{ width: 100%; border-collapse: collapse; }}
  td, th {{ text-align: left; padding: 8px; border-bottom: 1px solid #ddd; }}
  .muted {{ color: #777; }}
</style>
</head>
<body>
  <h1>File Health Report</h1>
  <p class="muted">Folder: {e(str(folder))} · {time.strftime("%d %B %Y")}</p>

  <div class="score">{score}/100</div>
  <div class="label">{label}</div>

  <div class="cards">
    <div class="card"><b>{results['total_files']}</b>files scanned</div>
    <div class="card"><b>{readable_size(results['wasted_size'])}</b>wasted on duplicates</div>
    <div class="card"><b>{len(results['loose_files'])}</b>loose files</div>
    <div class="card"><b>{len(results['old_files'])}</b>old files</div>
  </div>

  <h2>Where marks were lost</h2>
  <table>
    <tr><th>Problem</th><th>Files</th><th>Marks</th></tr>
    {rows}
  </table>

  <h2>Duplicates</h2>
  <ul>{duplicates}</ul>

  <h2>Old files</h2>
  <ul>{old}</ul>
</body>
</html>"""


if __name__ == "__main__":
    results = scan_folder(folder)
    score, breakdown = calculate_score(results)
    REPORT_FILE.write_text(build_html(folder, results, score, breakdown))
    print(f"Score: {score}/100. Report saved to {REPORT_FILE}")
    webbrowser.open(REPORT_FILE.resolve().as_uri())