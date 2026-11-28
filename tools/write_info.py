"""info.py OUTDIR DATE TYPE EVENT AGENDA PACKET MINUTES VIDEO START_VIDEO CALLED ADJ MINDOC APPROVED NOTES_FILE RELATED"""
import sys,os,csv,re,datetime
(d,date,typ,ev,ag,pk,mn,vid,start,called,adj,mindoc,appr,notesf,related)=sys.argv[1:16]
label={'committee-of-the-whole':'Committee of the Whole','business':'Business Meeting','retreat':'Planning Retreat','special-committee-of-the-whole':'Special Committee of the Whole','special-business':'Special Business Meeting','oath-of-office':'Business Meeting and Oath of Office Ceremony','budget-work-session':'Budget Work Session'}[typ]
sched={'committee-of-the-whole':'5:00 PM','business':'7:00 PM','retreat':'','special-committee-of-the-whole':'','special-business':'5:00 PM','oath-of-office':'5:00 PM','budget-work-session':'5:00 PM'}[typ]
u=lambda f:f"https://kalamazoomi.portal.civicclerk.com/event/{ev}/files/agenda/{f}"
def cnt(f): return sum(1 for _ in csv.DictReader(open(f'{d}/{f}',encoding='utf-8')))
L=["Government: City of Kalamazoo","Board: City Commission",f"Meeting: {label}",f"Date: {date}",f"Scheduled start: {sched}",
   f"Called to order: {called} (per minutes)" if called else "Called to order: not recorded (minutes not posted yet)",
   f"Adjourned: {adj} (per minutes)" if adj else "Adjourned: not recorded (minutes not posted yet)",
   "Location: City Commission Chambers, City Hall, 241 West South Street",""]
if vid:
    h,m,s=map(int,start.split(':'))
    parts=[f"{h} hour"+("s" if h>1 else "")] if h else []
    if m: parts.append(f"{m} minute"+("s" if m!=1 else ""))
    if s: parts.append(f"{s} second"+("s" if s!=1 else ""))
    L+= [f"Video: https://www.youtube.com/watch?v={vid}", f"Note: the meeting starts about {' and '.join(parts)} into the video.",""]
else: L+=["Video: none found on the city's YouTube channel",""]
haspk=os.path.isdir(f'{d}/packet')
L.append(f"Agenda: {u(ag)}")
if haspk:
    import subprocess
    L.append(f"Agenda packet: {u(pk)}")
else: L.append(f"Agenda packet: {u(pk)} (same as the agenda, no attachments; not stored separately)")
if mn: L+= [f"Minutes: {u(mn)}", f"Minutes document number: {mindoc}", f"Minutes approved: {appr}"]
else: L+= ["Minutes: not posted on CivicClerk yet (checked 2026-11-27). Add them when they are posted."]
L+=["","Files in this folder:"]
if os.path.exists(f'{d}/transcript.txt'):
    t=open(f'{d}/transcript.txt').read()
    L.append(f"  transcript.txt  cleaned YouTube automatic captions; {len(re.findall(r'^--- ',t,re.M))} blocks, each sentence timestamped ({len(re.findall(r'\[\d+:\d\d:\d\d\]',t))} timestamps)")
L.append("  agenda.txt      full agenda text")
if os.path.exists(f'{d}/minutes.txt'): L.append("  minutes.txt     full minutes text (scanned original, checked by hand)")
if os.path.exists(f'{d}/public-comment.csv'):
    P=list(csv.DictReader(open(f'{d}/public-comment.csv',encoding='utf-8')))
    per={}
    for r in P: per[r['comment_period']]=per.get(r['comment_period'],0)+1
    detail=', '.join(f"{v} in {k[0].lower()+k[1:]}" for k,v in per.items())
    L.append(f"  public-comment.csv  one row per public comment speaker ({len(P)} rows){': '+detail if len(per)>1 else ''}")
    L.append(f"  public-comment-topics.csv  one row per topic each speaker mentioned ({cnt('public-comment-topics.csv')} rows), with time and exact quote")
L.append(f"  agenda-items.csv    one row per agenda item ({cnt('agenda-items.csv')} rows): outcome, vote, mover, video times, minutes page, packet pages")
if haspk:
    I=list(csv.DictReader(open(f'{d}/packet/index.csv',encoding='utf-8')))
    items=len({r['agenda_item'] for r in I if r['agenda_item']}); att=sum(1 for r in I if r['agenda_item'])
    L.append(f"  packet/         full agenda packet split into {items} agenda items and {att} attachments; see packet/index.csv")
    if os.path.exists(f'{d}/packet/corrections.txt'): L.append("                  packet/corrections.txt lists pages whose text was typed in or fixed by hand")
notes=[l.rstrip() for l in open(notesf)] if notesf and os.path.exists(notesf) else []
if notes: L+=["","Notes:"]+["  "+n for n in notes if n.strip()]
if related: L+=["",f"Related meeting: {related}"]
open(f'{d}/info.txt','w').write('\n'.join(L)+'\n')
print('\n'.join(L))
