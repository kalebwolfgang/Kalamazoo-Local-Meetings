"""Rewrite flat 'Item: G1: Title' bookmarks into the standard 'G. ' > '1. Title' > 'Agenda Report' + attachments layout. usage: rebookmark.py IN OUT"""
import sys,re
from pypdf import PdfReader,PdfWriter
r=PdfReader(sys.argv[1]); w=PdfWriter(); w.append(r,import_outline=False)
items=[]; o=r.outline; i=0
while i<len(o):
    x=o[i]; kids=o[i+1] if i+1<len(o) and isinstance(o[i+1],list) else []
    if not isinstance(x,list):
        m=re.match(r'^Item:\s*([A-Z])(\d+):\s*(.*)',x.title.strip())
        if m: items.append((m.group(1),m.group(2),m.group(3).strip(),r.get_destination_page_number(x),[(k.title,r.get_destination_page_number(k)) for k in kids if not isinstance(k,list)]))
    i+=2 if kids else 1
secs={}
for s,n,t,p,k in items:
    if s not in secs: secs[s]=w.add_outline_item(f"{s}. SECTION",p)
    it=w.add_outline_item(f"{n}. {t}",p,parent=secs[s])
    if not any(kp==p for kt,kp in k): w.add_outline_item("Agenda Report",p,parent=it)
    for kt,kp in k: w.add_outline_item(kt,kp,parent=it)
w.write(sys.argv[2]); print(len(items),'items')
