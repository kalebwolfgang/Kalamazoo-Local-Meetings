"""Print full agenda item titles keyed like G1, H2 from agenda.txt. usage: titles.py agenda.txt"""
import re,sys
t=open(sys.argv[1]).read()
t=re.sub(r'--- page \d+ ---','',t)
t=re.sub(r'City Commission Agenda\s+Page \d+ of \d+\s+\w+ \d+, \d{4}','',t)
t=t.split('ADDITIONAL INFORMATION')[0]
sec=None; items={}; cur=None
for line in t.splitlines():
    m=re.match(r'^\s*([A-Z])\.\s{2,}(.*)',line)
    if m: sec=m.group(1); cur=None; continue
    m=re.match(r'^\s*(\d+)\.\s{2,}(.*)',line)
    if m and sec: cur=f"{sec}{m.group(1)}"; items[cur]=m.group(2).strip(); continue
    m=re.match(r'^\s*([a-z])\.\s{2,}(.*)',line)
    if m and sec and cur: cur=re.sub(r'[a-z]$','',cur)+m.group(1); items[cur]=m.group(2).strip(); continue
    if cur and line.strip() and not line.strip().startswith('(Action'):
        items[cur]+=' '+line.strip()
for k,v in items.items(): print(f"{k}\t{re.sub(chr(32)+'+',chr(32),v).split(' (Action')[0]}")
