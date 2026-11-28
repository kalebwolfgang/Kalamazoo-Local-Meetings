"""Write public-comment.csv. usage: pc.py OUTDIR DATE MEETING  (reads rows from stdin: period|order|speaker|residency|affiliation|spoke_about|time|time_note|minutes_page)"""
import csv,sys
H="meeting_date,government,board,meeting,comment_period,order,speaker,residency,affiliation,spoke_about (from minutes),topics_mentioned (AI-assigned),categories,other_notes,video_time,video_link,time_note,minutes_page".split(",")
d,date,meeting=sys.argv[1:4]
rows=[]
for line in sys.stdin:
    if not line.strip(): continue
    p=line.rstrip('\n').split('|')
    per,o,s,res,aff,ab,t,tn,mp=p
    rows.append(dict(zip(H,[date,"City of Kalamazoo","City Commission",meeting,per,o,s,res,aff,ab,"","","",t,"",tn,mp])))
w=csv.DictWriter(open(f'{d}/public-comment.csv','w',newline='',encoding='utf-8'),fieldnames=H); w.writeheader(); w.writerows(rows)
print(len(rows))
