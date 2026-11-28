"""Write agenda-items.csv from stdin: item|title|section|outcome|vote|no_votes|moved|seconded|resolution|minutes_doc|topics|intro|vote_at|minutes_page|packet_pages|notes . usage: ai.py OUTDIR DATE MEETING [agenda.txt]  (title '*' = take full title from agenda)"""
import os, csv,sys,subprocess
H="meeting_date,government,board,meeting,item,title,section,outcome,vote,no_votes,moved_by,seconded_by,resolution,minutes_document,topics (AI-assigned),categories,other_notes,introduced_at,introduced_link,vote_at,vote_link,minutes_page,packet_pages,notes".split(",")
d,date,meeting=sys.argv[1:4]
T={}
if len(sys.argv)>4:
    T=dict(l.split('\t',1) for l in subprocess.run(['python3',os.path.join(os.path.dirname(os.path.abspath(__file__)),'agenda_titles.py'),sys.argv[4]],capture_output=True,text=True).stdout.splitlines())
rows=[]
for line in sys.stdin:
    if not line.strip(): continue
    p=line.rstrip('\n').split('|')
    assert len(p)==16, f'need 16 fields, got {len(p)}: {line[:60]}'
    it,ti,sec,out,vote,no,mv,sd,res,md,top,intro,va,mp,pp,notes=p
    if ti=='*': ti=T[it]
    elif ti.startswith('*'): ti=T[ti[1:]]
    rows.append(dict(zip(H,[date,"City of Kalamazoo","City Commission",meeting,it,ti,sec,out,vote,no,mv,sd,res,md,top,"","",intro,"",va,"",mp,pp,notes])))
w=csv.DictWriter(open(f'{d}/agenda-items.csv','w',newline='',encoding='utf-8'),fieldnames=H); w.writeheader(); w.writerows(rows)
print(len(rows))
