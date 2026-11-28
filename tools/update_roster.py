"""Update roster: roster.py DATE "Name1,Name2" [new rows as JSON list]"""
import os, csv, sys, json
p=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'rosters','kalamazoo-city-commission.csv')
date=sys.argv[1]; present=set(x.strip() for x in sys.argv[2].split(',') if x.strip())
new=json.loads(sys.argv[3]) if len(sys.argv)>3 else []
rows=list(csv.DictReader(open(p,encoding='utf-8'))); f=list(rows[0].keys())
seen=set()
for r in rows:
    if r['official_name'] in present:
        seen.add(r['official_name'])
        if r['last_seen']<date: r['last_seen']=date
for n in new:
    n={k:n.get(k,'') for k in f}; n.setdefault('first_seen',date)
    if not n['first_seen']: n['first_seen']=date
    if not n['last_seen']: n['last_seen']=date
    if not n['verified_from']: n['verified_from']=f'{date} minutes'
    seen.add(n['official_name'])
    i=[k for k,r in enumerate(rows) if r['type']=='place'][0]; rows.insert(i,n)
miss=present-seen
w=csv.DictWriter(open(p,'w',encoding='utf-8',newline=''),fieldnames=f,lineterminator='\n'); w.writeheader(); w.writerows(rows)
print('not in roster:',miss or 'none')
