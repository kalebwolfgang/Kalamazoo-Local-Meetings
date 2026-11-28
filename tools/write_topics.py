"""Write public-comment-topics.csv from stdin lines: period|order|topic|quote|other_note. usage: tags.py OUTDIR"""
import csv,sys
d=sys.argv[1]
H="meeting_date,government,board,meeting,comment_period,speaker_order,speaker,topic,categories,mentioned_at,video_link,quote (exact words from transcript),other_note".split(",")
P=list(csv.DictReader(open(f'{d}/public-comment.csv',encoding='utf-8')))
spk={(r['comment_period'],r['order']):r for r in P}
out=[]
for line in sys.stdin:
    if not line.strip(): continue
    per,o,topic,q,note=(line.rstrip('\n').split('|')+[''])[:5]
    r=spk[(per,o)]
    out.append(dict(zip(H,[r['meeting_date'],r['government'],r['board'],r['meeting'],per,o,r['speaker'],topic,"","","",q,note])))
w=csv.DictWriter(open(f'{d}/public-comment-topics.csv','w',newline='',encoding='utf-8'),fieldnames=H); w.writeheader(); w.writerows(out)
