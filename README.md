# File Health Check

A Python tool that scans a folder and reports on its health: duplicate files, messy file names, old files and deeply nested folders.

The first step towards an AI-powered file cleanup service for businesses.

## What it checks
- Total files, total size and file types
- Duplicate files, detected by content fingerprint (SHA-256), even when names differ
- Badly named files ("copy", "final", "v2", "(1)")
- Files not modified in over 2 years
- Files buried more than 5 folders deep

## Privacy and safety
- Read-only: never moves, changes or deletes files
- File contents are only read to calculate fingerprints, and are never stored or sent anywhere

## How to run
Set the folder to scan at the top of `scan.py`, then run:

```
python3 scan.py
```

## Roadmap
- [ ] AI-suggested folder structure and naming rules
- [ ] Health score and PDF report
- [ ] SharePoint and Google Drive support