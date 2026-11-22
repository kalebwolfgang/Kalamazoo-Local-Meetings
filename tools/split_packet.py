"""Split an agenda packet PDF into one text file per attachment, all in one folder.

- Uses the PDF's own bookmarks to find each agenda item and attachment.
- Every page is marked "--- packet page N ---" so facts can be cited to the page.
- Pages with no text layer, or with garbled text, are read with OCR and marked.
- Budget summary tables on OCR'd pages are read TWICE (300 and 400 dpi) and their
  group totals are checked against their lines. Anything that disagrees is written
  to needs-review.txt so a person can check it against the page image.
- Fee and rate schedules with a clean text layer are also saved as CSV.
- Writes index.csv listing every attachment, its pages, and its files.

usage: split_packet.py PACKET.pdf OUT_DIR "Meeting label" [ITEM_SLUGS.csv]
  Meeting label   e.g. "January 5, 2026 Business Meeting"
  ITEM_SLUGS.csv  optional, columns: item,slug,title  (short folder names and full agenda titles)
"""
import csv
import os
import re
import subprocess
import sys
import tempfile

import pdfplumber
import pypdf

pdf_path, out_dir, meeting_label = sys.argv[1:4]
slugs, titles = {}, {}
if len(sys.argv) > 4:
    for r in csv.DictReader(open(sys.argv[4], encoding="utf-8")):
        slugs[r["item"]] = r["slug"]
        if r.get("title"):
            titles[r["item"]] = r["title"]

reader = pypdf.PdfReader(pdf_path)
NPAGES = len(reader.pages)
tmp = tempfile.mkdtemp()


def run(*a):
    return subprocess.run(a, capture_output=True, text=True).stdout


# ---------- classify pages ----------
OK_CHARS = set("\u2013\u2014\u2019\u2018\u201c\u201d\u2022\u00b7\u2026\u00a7\u00b0\u00bd\u00bc\u00be\u00d7\u00ae\u00a9\u2122\u00e9")


def classify(p):
    t = run("pdftotext", "-layout", "-f", str(p), "-l", str(p), pdf_path, "-")
    s = re.sub(r"\s", "", t)
    if len(s) < 40:
        return "empty"
    odd = sum(1 for c in s if ord(c) > 127 and c not in OK_CHARS and c != "�")
    return "garbled" if ("ÿ" in s or odd / len(s) > 0.02) else "good"


pageclass = {p: classify(p) for p in range(1, NPAGES + 1)}

# ---------- bookmarks ----------
entries = []


def page_of(x):
    return reader.get_destination_page_number(x) + 1


def walk(nodes, section=None, item=None, depth=0):
    i = 0
    while i < len(nodes):
        node = nodes[i]
        kids = nodes[i + 1] if i + 1 < len(nodes) and isinstance(nodes[i + 1], list) else None
        if isinstance(node, list):
            i += 1
            continue
        title = node.title.strip().replace("​", "")
        m_sec = re.match(r"^([A-Z])\.\s", title)
        m_item = re.match(r"^(\d+)\.\s", title)
        m_sub = re.match(r"^([a-z])\.\s", title)
        if depth == 0 and m_sec:
            if kids:
                walk(kids, section=m_sec.group(1), depth=1)
        elif depth == 1 and m_item:
            if kids:
                walk(kids, section=section, item=(f"{section}{m_item.group(1)}", title), depth=2)
        elif depth == 2 and m_sub and kids:
            walk(kids, section=section, item=(f"{item[0]}{m_sub.group(1)}", title), depth=3)
        elif depth >= 2 and item:
            entries.append({"code": item[0], "item_title": item[1], "attach": title, "start": page_of(node)})
        i += 2 if kids else 1


walk(reader.outline)
entries.sort(key=lambda e: e["start"])
starts = sorted({e["start"] for e in entries})
for e in entries:
    later = [s for s in starts if s > e["start"]]
    e["end"] = (later[0] - 1) if later else NPAGES


# ---------- page text ----------
def ocr(page, dpi, psm):
    png = os.path.join(tmp, f"p{page}_{dpi}")
    subprocess.run(["pdftoppm", "-r", str(dpi), "-png", "-singlefile", "-f", str(page), "-l", str(page), pdf_path, png], check=True)
    return run("tesseract", png + ".png", "-", "--psm", str(psm))


cache = {}


def page_text(p):
    if p in cache:
        return cache[p]
    kind = pageclass[p]
    if kind == "good":
        t = run("pdftotext", "-layout", "-f", str(p), "-l", str(p), pdf_path, "-").replace("�", "").replace("\f", "")
        note = ""
    else:
        t = ocr(p, 400, 6 if kind == "garbled" else 3)
        if len(re.sub(r"\s", "", t)) < 30:
            t, note = "", "[image only: no readable text on this page]"
        else:
            note = "[scanned page, text read by software: may contain small errors]"
    t = re.sub(r"\n{3,}", "\n\n", "\n".join(l.rstrip() for l in t.splitlines())).strip("\n")
    cache[p] = (t, note)
    return cache[p]


# ---------- budget tables on OCR'd pages ----------
NUM = r"\(?-?\$?\s?[\d,]+(?:\.\d+)?\)?"
ROW = re.compile(rf"^\s*([vy>»]+(?=\s))?\s*(.+?)\s+((?:{NUM}\s+){{3}}{NUM})\s*$")


def clean_num(n):
    v = n.replace("$", "").replace(",", "").replace(" ", "")
    return "-" + v.strip("()") if v.startswith("(") and v.endswith(")") else v.strip("()")


def parse_budget(text, page):
    rows, header = [], None
    for line in text.splitlines():
        if not header and re.search(r"20\d\d (Actuals?|Adopted|Amended|Proposed)", line):
            header = re.findall(r"20\d\d [A-Za-z]+(?: [A-Za-z]+)?", line)
            continue
        m = ROW.match(line)
        if m:
            level = "group" if (m.group(1) or "")[:1] in ("v", "y") else ("detail" if m.group(1) else "")
            rows.append([page, level, m.group(2).strip().rstrip("$").strip()] + [clean_num(n) for n in re.findall(NUM, m.group(3))])
    return header, rows


def sum_problems(rows):
    out, i = [], 0
    while i < len(rows):
        if rows[i][1] == "group":
            j, kids = i + 1, []
            while j < len(rows) and rows[j][1] == "detail":
                kids.append(rows[j])
                j += 1
            for c in range(3, 7):
                if not kids:
                    break
                try:
                    if abs(sum(float(k[c]) for k in kids) - float(rows[i][c])) > 1:
                        out.append(f"packet page {rows[i][0]}, '{rows[i][2]}', column {c - 2}: total does not equal the sum of its lines")
                except ValueError:
                    out.append(f"packet page {rows[i][0]}, '{rows[i][2]}': unreadable number")
        i += 1
    return out


def double_read(page):
    """Rows where the 300 dpi and 400 dpi readings disagree."""
    a = {r[2]: r[3:] for r in parse_budget(ocr(page, 300, 6), page)[1]}
    b = {r[2]: r[3:] for r in parse_budget(page_text(page)[0], page)[1]}
    return [f"packet page {page}, '{k}': readings disagree {a.get(k)} vs {b.get(k)}" for k in sorted(set(a) | set(b)) if a.get(k) != b.get(k)]


def plumber_rows(pages):
    out = []
    with pdfplumber.open(pdf_path) as pdf:
        for p in pages:
            for tb in pdf.pages[p - 1].extract_tables():
                for row in tb:
                    cells = [re.sub(r"\s+", " ", c or "").strip() for c in row]
                    if any(cells):
                        out.append([p] + cells)
    return out


def slug(s, n=50):
    s = re.sub(r"\.pdf$", "", s, flags=re.I)
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s[:n].rstrip("-") or "attachment"


# ---------- write ----------
os.makedirs(out_dir, exist_ok=True)
index_rows, review, counters = [], [], {}
for e in entries:
    code = e["code"]
    item_code = re.sub(r"^([A-Z])(\d+)", lambda m: f"{m.group(1)}{int(m.group(2)):02d}", code)
    prefix = f"{item_code}-{slugs.get(code, slug(e['item_title'], 40))}"
    counters[prefix] = counters.get(prefix, 0) + 1
    n = counters[prefix]
    base = f"{prefix}--{n:02d}-{slug(e['attach'])}"
    pages = list(range(e["start"], e["end"] + 1))
    parts, scanned, image_only = [], [], []
    for p in pages:
        t, note = page_text(p)
        (scanned if note.startswith("[scanned") else image_only if note else []).append(p)
        parts.append(f"--- packet page {p} ---" + (f"\n{note}" if note else "") + (f"\n\n{t}" if t else ""))
    title = titles.get(code, e["item_title"])
    with open(os.path.join(out_dir, base + ".txt"), "w", encoding="utf-8") as f:
        f.write(f"# Agenda item {code}: {title}\n# Attachment: {e['attach']}\n"
                f"# Packet pages {pages[0]}-{pages[-1]} of the {meeting_label} agenda packet. Full text, not summarized.\n\n")
        f.write("\n\n".join(parts) + "\n")

    csv_name = ""
    budget_rows, header = [], None
    for p in pages:
        if pageclass[p] == "garbled":
            h, r = parse_budget(page_text(p)[0], p)
            if len(r) >= 3:
                header = header or h
                budget_rows += r
                review += double_read(p)
    if budget_rows:
        csv_name = base + ".csv"
        cols = header if header and len(header) == 4 else ["col1", "col2", "col3", "col4"]
        with open(os.path.join(out_dir, csv_name), "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerows([["packet_page", "row_type", "line"] + cols] + budget_rows)
        review += [f"{csv_name}: {x}" for x in sum_problems(budget_rows)]
    elif re.search(r"fee schedule|rates", e["attach"], re.I):
        rows = plumber_rows([p for p in pages if pageclass[p] == "good"])
        if rows:
            csv_name = base + ".csv"
            width = max(len(r) for r in rows)
            with open(os.path.join(out_dir, csv_name), "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerows([["packet_page"] + [f"col{i}" for i in range(1, width)]] + [r + [""] * (width - len(r)) for r in rows])
            review.append(f"{csv_name}: fee table saved as CSV, check the columns line up before keeping it")

    index_rows.append([code, title, n, e["attach"], base + ".txt", csv_name, f"{pages[0]}-{pages[-1]}",
                       " ".join(map(str, scanned)), " ".join(map(str, image_only))])

first = min(starts) if starts else 1
with open(os.path.join(out_dir, "index.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["agenda_item", "item_title", "attachment_no", "attachment_title", "text_file", "table_file",
                "packet_pages", "scanned_pages", "image_only_pages"])
    if first > 1:
        w.writerow(["", f"Agenda (pages 1-{first - 1})", "", "Agenda", "../agenda.txt", "", f"1-{first - 1}", "", ""])
    w.writerows(index_rows)

with open(os.path.join(out_dir, "needs-review.txt"), "w", encoding="utf-8") as f:
    f.write("# Check each line against the page image. Fix confirmed errors and log them in corrections.txt.\n")
    f.write("# Some sum warnings are false alarms on tables with more than two levels of totals.\n\n")
    f.write("\n".join(review) + "\n")

covered = {p for e in entries for p in range(e["start"], e["end"] + 1)}
print(f"attachments: {len(entries)}  pages covered: {len(covered)}  missing: {[p for p in range(first, NPAGES + 1) if p not in covered]}")
print(f"needs review: {len(review)} lines (see needs-review.txt; delete that file before uploading)")
