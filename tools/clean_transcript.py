"""Clean a YouTube transcript copied from the "Show transcript" panel.

Format only: strips the doubled spoken timestamp, joins caption lines into
sentences, marks every sentence with its start time, groups sentences into short
blocks that each start with a video link, removes noise tags, and fixes names from
the roster only when a title word comes first and the meeting date falls inside the
person's first_seen/last_seen dates. Words are never reworded.

usage: clean_transcript.py RAW.txt ROSTER.csv OUT.txt REPORT.txt "Header line" VIDEO_ID MEETING_DATE
  RAW.txt       text copied from YouTube's "Show transcript" panel
  REPORT.txt    lists every name fix made and any lines that did not parse
  MEETING_DATE  YYYY-MM-DD
"""
import csv
import re
import sys
from collections import Counter

raw_path, roster_path, out_path, report_path, header, video_id = sys.argv[1:7]
meeting_date = sys.argv[7] if len(sys.argv) > 7 else None

# ---------- 1. parse lines ----------
def spoken(h, m, s):
    parts = []
    if h:
        parts.append(f"{h} hour" + ("s" if h != 1 else ""))
    if m:
        parts.append(f"{m} minute" + ("s" if m != 1 else ""))
    if s:
        parts.append(f"{s} second" + ("s" if s != 1 else ""))
    return ", ".join(parts)

segments = []  # (seconds, text)
bad = []
for n, line in enumerate(open(raw_path, encoding="utf-8").read().splitlines(), 1):
    if not line.strip():
        continue
    m = re.match(r"^(\d+):(\d{2})(?::(\d{2}))?", line)
    if not m:
        bad.append((n, line[:80]))
        continue
    if m.group(3) is not None:
        h, mi, s = int(m.group(1)), int(m.group(2)), int(m.group(3))
    else:
        h, mi, s = 0, int(m.group(1)), int(m.group(2))
    rest = line[m.end():]
    words = spoken(h, mi, s)
    if words and rest.startswith(words):
        rest = rest[len(words):]
    elif h == 0 and mi == 0 and s == 0 and rest.startswith("0 seconds"):
        rest = rest[len("0 seconds"):]
    else:
        bad.append((n, line[:80]))
    segments.append((h * 3600 + mi * 60 + s, rest.strip()))

# ---------- 2. noise tags ----------
NOISE = re.compile(r"\s*\[(snorts|clears throat|gasps|sighs|coughs|music)\]\s*", re.I)
segments = [(t, NOISE.sub(" ", x).strip()) for t, x in segments]
segments = [(t, re.sub(r"\s{2,}", " ", x)) for t, x in segments if x]

# ---------- 3. name fixes ----------
fixes = Counter()
rules = []
for row in csv.DictReader(open(roster_path, encoding="utf-8")):
    wrong = [w for w in row["wrong_spellings"].split("|") if w]
    if not wrong:
        continue
    if meeting_date and row.get("first_seen") and not (row["first_seen"] <= meeting_date <= (row.get("last_seen") or "9999")):
        continue
    surname = row["official_name"].split()[-1] if row["type"] != "place" else row["official_name"]
    wrong.sort(key=len, reverse=True)
    wrong_re = "|".join(re.escape(w) for w in wrong)
    if row["type"] == "place":
        pat = re.compile(rf"\b({wrong_re})\b", re.I)
        rules.append((pat, lambda mt, s=surname: s, row["official_name"]))
    else:
        titles = [t for t in row["fix_only_after"].split("|") if t]
        titles.sort(key=len, reverse=True)
        title_re = "|".join(re.escape(t) for t in titles)
        pat = re.compile(rf"\b({title_re}),?\s+(?:(?:uh|um),?\s+)?({wrong_re})\b", re.I)
        rules.append((pat, lambda mt, s=surname: f"{mt.group(1)} {s}", row["official_name"]))

def fix_names(text):
    for pat, repl, name in rules:
        def sub(mt, repl=repl, name=name):
            fixes[f"{mt.group(0)}  ->  {repl(mt)}"] += 1
            return repl(mt)
        text = pat.sub(sub, text)
    return text

# ---------- 4. sentences ----------
sentences = []  # (start seconds, sentence, end seconds)
buf, buf_t = "", None
ABBR = re.compile(r"\b(Mr|Mrs|Ms|Dr|St|Rev)\.(?=\s)")
for t, x in segments:
    x = ABBR.sub(r"\1<DOT>", x)
    for piece in re.split(r"(?<=[.?!])\s+", x):
        if not piece:
            continue
        if buf_t is None:
            buf_t = t
        buf = (buf + " " + piece).strip()
        if re.search(r"[.?!][\"')\]]?$", piece):
            sentences.append((buf_t, buf, t))
            buf, buf_t = "", None
if buf:
    sentences.append((buf_t, buf, segments[-1][0]))

# ---------- 5. paragraphs (every sentence keeps its own timestamp) ----------
def ts(sec):
    return f"{sec // 3600}:{sec % 3600 // 60:02d}:{sec % 60:02d}"

paras = []
cur, cur_t, last_t = [], None, None
for t0, s, t1 in sentences:
    new = cur_t is None
    if not new and (t0 - last_t > 5 or t0 - cur_t > 45):
        new = True
    if new and cur:
        paras.append((cur_t, cur))
        cur = []
    if not cur:
        cur_t = t0
    cur.append((t0, fix_names(s.replace("<DOT>", "."))))
    last_t = t1
if cur:
    paras.append((cur_t, cur))

def render(sents):
    out, shown = [], None
    for t0, s in sents:
        out.append((f"[{ts(t0)}] " if t0 != shown else "") + s)
        shown = t0
    text = " ".join(out)
    return re.sub(r"(\[(applause|laughter)\])(\s*\1)+", r"\1", text)

with open(out_path, "w", encoding="utf-8") as f:
    f.write(f"# {header}\n")
    f.write(f"# Video: https://www.youtube.com/watch?v={video_id}\n")
    f.write("# Source: YouTube automatic captions, cleaned for format only. Check the video before quoting.\n")
    f.write("# Each block starts with a link to that moment in the video. Each sentence is marked with the time it starts.\n")
    f.write("# Times are within a few seconds; YouTube captions only mark when each caption line begins.\n\n")
    for t, sents in paras:
        f.write(f"--- {ts(t)} | https://www.youtube.com/watch?v={video_id}&t={t}s\n")
        f.write(render(sents) + "\n\n")

with open(report_path, "w", encoding="utf-8") as f:
    f.write(f"caption lines: {len(segments)}\nparagraphs: {len(paras)}\n")
    f.write(f"lines with unexpected format: {len(bad)}\n")
    for n, l in bad[:20]:
        f.write(f"  line {n}: {l}\n")
    f.write(f"\nname fixes ({sum(fixes.values())}):\n")
    for k, v in fixes.most_common():
        f.write(f"  {v:3d}  {k}\n")
print(open(report_path).read())
