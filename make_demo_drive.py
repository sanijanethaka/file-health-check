from pathlib import Path
import os
import time

DEMO = Path("demo-drive")
DAY = 60 * 60 * 24

# (path, content, age in days)
# Files with the same content are duplicates.
FILES = [
    # Already filed properly
    ("Clients/Acme Pty Ltd/Acme_Service_Agreement_2025-02-10.pdf", "acme-agreement", 620),
    ("Clients/Acme Pty Ltd/Acme_Project_Plan_2026-03-01.docx", "acme-plan", 230),
    ("Clients/Smith & Co/Smith_Engagement_Letter_2024-08-19.pdf", "smith-letter", 800),
    ("Finance/Invoices/INV-1042_Acme_2026-05-31.pdf", "inv-1042", 150),
    ("Finance/Receipts/Receipt_Officeworks_2026-06-12.pdf", "receipt-officeworks", 136),
    ("HR/Policies/Leave_Policy_2025-01-15.pdf", "leave-policy", 650),
    ("HR/Staff Onboarding/Onboarding_Checklist_2025-07-01.docx", "onboarding", 480),
    ("Marketing/Brand/Logo_Primary_2024-11-03.png", "logo", 720),
    ("Marketing/Social Media/Content_Calendar_2026-Q2.xlsx", "calendar-q2", 200),
    # The mess: loose files at the top level
    ("invoice acme june.pdf", "inv-1050", 120),
    ("invoice acme june (1).pdf", "inv-1050", 120),
    ("Smith proposal v2.docx", "smith-proposal", 90),
    ("Smith proposal FINAL.docx", "smith-proposal-final", 85),
    ("receipt bunnings.pdf", "receipt-bunnings", 60),
    ("Leave Policy copy.pdf", "leave-policy", 650),
    ("new starter form.docx", "starter-form", 40),
    ("logo_new_blue.png", "logo-blue", 30),
    ("Q3 social posts.xlsx", "q3-posts", 20),
    ("budget 2024.xlsx", "budget-2024", 900),
    ("Scan_20230411.pdf", "scan-2023", 1290),
    ("Untitled document.docx", "untitled", 400),
    ("meeting notes.txt", "notes", 10),
]

if DEMO.exists():
    print(f"'{DEMO}' already exists. Delete it yourself first if you want to rebuild it.")
else:
    for path, content, age_days in FILES:
        file = DEMO / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(f"Demo file: {content}")
        old_time = time.time() - age_days * DAY
        os.utime(file, (old_time, old_time))
    print(f"Created {len(FILES)} demo files in '{DEMO}'.")