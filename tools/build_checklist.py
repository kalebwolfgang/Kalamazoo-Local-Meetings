"""Rebuild checklist.md: what has been collected and uploaded for every meeting, and what is still needed.

Reads meeting-list.csv (every meeting we expect, including ones not done yet) and looks
at each meeting folder to see which files are there. Run it after every new day of
meetings is added, so checklist.md always matches the repo.

usage: build_checklist.py            (run from the repo root)
"""
import csv
import os
from collections import Counter
from datetime import date

ROOT = "kalamazoo-city/city-commission"
COLS = [
    ("Transcript", "transcript.txt"),
    ("Agenda", "agenda.txt"),
    ("Packet", "packet/index.csv"),
    ("Minutes", "minutes.txt"),
    ("Public comment", "public-comment.csv"),
    ("Agenda items", "agenda-items.csv"),
]
YES, NO, NA = "yes", "**missing**", "n/a"


def folder_path(r):
    return f"{ROOT}/{r['date'][:4]}/{r['folder']}" if r["folder"] else ""


def same_as_agenda(path):
    info = f"{path}/info.txt"
    return os.path.exists(info) and "same as the agenda, no attachments" in open(info, encoding="utf-8").read()


rows = list(csv.DictReader(open("meeting-list.csv", encoding="utf-8")))
lines, status_count, needed = [], Counter(), []
for r in rows:
    path = folder_path(r)
    label = f"{r['date']} {r['meeting']}"
    if "Cancelled" in r["notes"]:
        status = "Cancelled"
        cells = [NA] * len(COLS)
    elif not path or not os.path.isdir(path):
        status = "Not started"
        cells = [NO] * len(COLS)
        needed.append(f"- {label}: not started" + (f" ({r['notes']})" if r["notes"] else ""))
    else:
        cells = []
        for name, f in COLS:
            if f == "packet/index.csv" and same_as_agenda(path):
                cells.append("same as agenda")
            elif f == "packet/index.csv" and os.path.exists(f"{path}/info.txt") and "Agenda packet: none posted" in open(f"{path}/info.txt", encoding="utf-8").read():
                cells.append("none posted")
            elif f == "minutes.txt" and not r["minutes_file_id"] and not os.path.exists(f"{path}/{f}"):
                cells.append("not posted yet")
            elif f == "transcript.txt" and not r["video_id"] and not os.path.exists(f"{path}/{f}"):
                cells.append("no video")
            else:
                cells.append(YES if os.path.exists(f"{path}/{f}") else NO)
        missing = [n for (n, _), c in zip(COLS, cells) if c == NO]
        waiting = [n for (n, _), c in zip(COLS, cells) if c == "not posted yet"]
        if missing:
            status = "Partly done"
            needed.append(f"- {label}: missing {', '.join(missing)}")
        elif waiting:
            status = "Done, waiting on minutes"
            needed.append(f"- {label}: add minutes once the city posts them")
        else:
            status = "Done"
    status_count[status] += 1
    lines.append(f"| {r['date']} | {r['meeting']} | {status} | " + " | ".join(cells) + f" | {r['notes']} |")

out = [
    "# Checklist",
    "",
    f"What has been collected and uploaded for each meeting, and what is still needed. Rebuilt by `tools/build_checklist.py` from `meeting-list.csv` and the meeting folders. Last rebuilt {date.today().isoformat()}.",
    "",
    "Goal: every City of Kalamazoo City Commission meeting back to January 2020. So far the meeting list covers October 2025 to September 2026. Earlier years are added to `meeting-list.csv` as we get to them.",
    "",
    "## Summary",
    "",
]
for s in ["Done", "Done, waiting on minutes", "Partly done", "Not started", "Cancelled"]:
    if status_count[s]:
        out.append(f"- {s}: {status_count[s]}")
out += ["", "## Still needed", ""] + (needed or ["- Nothing"]) + [
    "",
    "## Every meeting",
    "",
    "| Date | Meeting | Status | " + " | ".join(n for n, _ in COLS) + " | Notes |",
    "|" + "---|" * (len(COLS) + 4),
] + lines + [""]
open("checklist.md", "w", encoding="utf-8").write("\n".join(out))
print(dict(status_count))
