"""After split_packet: rows that cover the agenda pages (start at page 1) become one Agenda row. usage: fixagenda.py PACKET_DIR"""
import csv,sys,os
d=sys.argv[1]; p=f'{d}/index.csv'
rows=list(csv.reader(open(p,encoding='utf-8'))); h,body=rows[0],rows[1:]
ag=[r for r in body if r[6].startswith('1-') or r[6]=='1']
if ag:
    end=max(int(r[6].split('-')[-1]) for r in ag)
    for r in ag:
        if os.path.exists(f'{d}/{r[4]}'): os.remove(f'{d}/{r[4]}')
    body=[r for r in body if r not in ag]
    body.insert(0,['',f'Agenda (pages 1-{end})','','Agenda','../agenda.txt','',f'1-{end}','',''])
w=csv.writer(open(p,'w',encoding='utf-8',newline='')); w.writerow(h); w.writerows(body)  # CRLF like the rest of the repo
print(body[0])
