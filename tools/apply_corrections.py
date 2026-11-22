"""Apply hand-checked fixes to software-read packet tables and log them.

Use after split_packet.py, once each line in needs-review.txt has been checked
against the page image. Every fix is written to corrections.txt.

usage: apply_corrections.py PACKET_DIR FIXES.csv

FIXES.csv columns:
  file          base file name without .csv/.txt
  packet_page   page number
  line          the row's line label exactly as in the CSV
  column        1-4 to replace one number, or "add" to insert a missing row
  value         correct number (no commas); for "add", the four numbers separated by spaces
  before_line   for "add" only: the line label the new row goes in front of
  wrong_text    for a replacement: the wrong number as it appears in the .txt (with commas)
"""
import csv
import re
import sys

root, fixes_path = sys.argv[1:3]
log = []
for fx in csv.DictReader(open(fixes_path, encoding="utf-8")):
    base, page = f"{root}/{fx['file']}", fx["packet_page"]
    rows = list(csv.reader(open(base + ".csv", encoding="utf-8")))
    text = open(base + ".txt", encoding="utf-8").read()
    if fx["column"] == "add":
        vals = fx["value"].split()
        i = next(i for i, r in enumerate(rows) if r[0] == page and r[2] == fx["before_line"])
        rows.insert(i, [page, "detail", fx["line"]] + vals)
        shown = " ".join(f"{int(v):,}" for v in vals)
        marker = f"--- packet page {page} ---\n"
        at = text.index(marker) + len(marker)
        nl = text.index("\n", at) + 1 if text[at:].startswith("[scanned") else at
        text = text[:nl] + f"[corrected by hand from page image: the row '{fx['line']} {shown}' was unreadable to software]\n" + text[nl:]
        log.append(f"{fx['file']}.csv, packet page {page}: row '{fx['line']}' was unreadable to software, added from page image: {shown}")
    else:
        col = int(fx["column"])
        hit = [r for r in rows if r[0] == page and r[2] == fx["line"]]
        assert len(hit) == 1, f"line not found once: {fx['line']}"
        hit[0][2 + col] = fx["value"]
        right = f"{int(fx['value']):,}"
        assert fx["wrong_text"] in text, f"wrong text not in .txt: {fx['wrong_text']}"
        text = text.replace(fx["wrong_text"], right + " [corrected by hand from page image]", 1)
        log.append(f"{fx['file']}.csv / .txt, packet page {page}, '{fx['line']}', column {col}: software read {fx['wrong_text']}, page shows {right}")
    csv.writer(open(base + ".csv", "w", newline="", encoding="utf-8")).writerows(rows)
    open(base + ".txt", "w", encoding="utf-8").write(text)

with open(f"{root}/corrections.txt", "w", encoding="utf-8") as f:
    f.write("# Hand corrections to software-read (scanned) pages in this packet\n")
    f.write("# Budget tables were read twice by software and checked so that group totals equal the sum of their lines.\n")
    f.write("# Every disagreement below was checked against the page image.\n\n")
    f.write("\n".join(log) + "\n")
print(f"{len(log)} corrections applied")
