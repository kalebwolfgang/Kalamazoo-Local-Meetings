"""Print what each public comment speaker said, from their start time to the next speaker's.

Used to read every comment in full before tagging topics, because the minutes'
one-line summaries leave topics out.

usage: speaker_text.py MEETING_DIR [ROW,ROW,...] [ROW=END_TIME ...]
  ROW       0-based row numbers in public-comment.csv (default: all)
  ROW=TIME  where a speaker's comment ends, for the last speaker in a comment period
"""
import csv
import re
import sys

mdir = sys.argv[1]
text = open(f"{mdir}/transcript.txt", encoding="utf-8").read()
S = [(m.group(1), m.group(2).strip()) for m in re.finditer(r"\[(\d+:\d{2}:\d{2})\] ([^\[]*)", text)]


def sec(x):
    h, m, s = map(int, x.split(":"))
    return h * 3600 + m * 60 + s


rows = list(csv.DictReader(open(f"{mdir}/public-comment.csv", encoding="utf-8")))
which = [int(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 and "=" not in sys.argv[2] else range(len(rows))
stops = dict(a.split("=") for a in sys.argv[2:] if "=" in a)
for i in which:
    r = rows[i]
    a = sec(r["video_time"])
    end = stops.get(str(i)) or (rows[i + 1]["video_time"] if i + 1 < len(rows) else "9:59:59")
    b = sec(end)
    print(f"\n##### row {i}: {r['speaker']} ({r['comment_period']}) {r['video_time']}")
    print(" ".join(f"[{t}] {re.sub(r'--- .*', '', x).strip()}" for t, x in S if a <= sec(t) < b))
