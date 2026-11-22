"""Check and fill in a meeting's spreadsheets so every row is consistent and citable.

Run after writing public-comment.csv, public-comment-topics.csv, and agenda-items.csv
for a meeting. It:
- checks every topic is in topics.csv, and that every Other has a note
- checks every quote in public-comment-topics.csv appears word for word in the
  transcript, and sets mentioned_at to the time of the sentence it is in
- fills in categories, video links, topics_mentioned, and other_notes
Stops with an error if anything fails, so nothing unverified gets uploaded.

usage: finish_tables.py MEETING_DIR VIDEO_ID TOPICS.csv
"""
import csv
import re
import sys

mdir, vid, topics_path = sys.argv[1:4]
CATS = {r["topic"]: r["category"].split("; ") for r in csv.DictReader(open(topics_path, encoding="utf-8"))}


def sec(t):
    h, m, s = map(int, t.split(":"))
    return h * 3600 + m * 60 + s


def ts(n):
    return f"{n // 3600}:{n % 3600 // 60:02d}:{n % 60:02d}"


def link(t):
    return f"https://www.youtube.com/watch?v={vid}&t={sec(t)}s" if t else ""


def cats_for(topics):
    out = []
    for t in topics:
        assert t in CATS, f"topic not in topics.csv: {t}"
        out += [c for c in CATS[t] if c not in out]
    return out


def load_transcript(p):
    plain, times, cur, prev_space = "", [], 0, False
    for line in open(p, encoding="utf-8").read().splitlines():
        if line.startswith(("#", "---")) or not line.strip():
            continue
        for part in re.split(r"(\[\d+:\d{2}:\d{2}\] )", line + " "):
            m = re.match(r"\[(\d+):(\d{2}):(\d{2})\] ", part)
            if m:
                cur = int(m[1]) * 3600 + int(m[2]) * 60 + int(m[3])
                continue
            for ch in part:
                if ch.isspace():
                    if prev_space:
                        continue
                    ch, prev_space = " ", True
                else:
                    prev_space = False
                plain += ch
                times.append(cur)
    return plain, times


def read(name):
    with open(f"{mdir}/{name}", encoding="utf-8") as f:
        r = csv.DictReader(f)
        return r.fieldnames, list(r)


def write(name, cols, rows):
    with open(f"{mdir}/{name}", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)


plain, times = load_transcript(f"{mdir}/transcript.txt")

# public-comment-topics.csv
tcols, trows = read("public-comment-topics.csv")
QUOTE = "quote (exact words from transcript)"
for r in trows:
    q = r[QUOTE]
    hits = [m.start() for m in re.finditer(re.escape(q), plain)]
    assert hits, f"quote not found in transcript: {q}"
    guess = sec(r["mentioned_at"]) if r.get("mentioned_at") else 0
    r["mentioned_at"] = ts(times[min(hits, key=lambda h: abs(times[h] - guess))])
    r["video_link"] = link(r["mentioned_at"])
    r["categories"] = "; ".join(cats_for([r["topic"]]))
    assert r["topic"] != "Other" or r["other_note"], f"Other needs a note: {q}"
trows.sort(key=lambda r: (r["comment_period"] != "General public comment", r["comment_period"], int(r["speaker_order"]), sec(r["mentioned_at"])))
write("public-comment-topics.csv", tcols, trows)

# public-comment.csv
pcols, prows = read("public-comment.csv")
TM = "topics_mentioned (AI-assigned)"
for p in prows:
    mine = [r for r in trows if r["comment_period"] == p["comment_period"] and r["speaker_order"] == p["order"]]
    topics = list(dict.fromkeys(r["topic"] for r in mine))
    p[TM] = "; ".join(topics)
    p["categories"] = "; ".join(cats_for(topics))
    p["other_notes"] = "; ".join(dict.fromkeys(r["other_note"] for r in mine if r["other_note"]))
    p["video_link"] = link(p["video_time"])
write("public-comment.csv", pcols, prows)

# agenda-items.csv
acols, arows = read("agenda-items.csv")
for a in arows:
    a["categories"] = "; ".join(cats_for(a["topics (AI-assigned)"].split("; ")))
    a["introduced_link"] = link(a["introduced_at"])
    a["vote_link"] = link(a["vote_at"])
write("agenda-items.csv", acols, arows)

print(f"ok: {len(prows)} speakers, {len(trows)} topic mentions, {len(arows)} agenda items")
