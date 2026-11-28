"""Prep one meeting: agenda.txt, transcript.txt, minutes OCR, page images. usage: prep_meeting.py DIR DATE TYPE VIDEO"""
import subprocess, sys, os, glob, datetime
d, date, typ, vid = sys.argv[1:5]
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
label={'committee-of-the-whole':'Committee of the Whole','business':'Business Meeting','retreat':'Planning Retreat'}[typ]
nice=datetime.date.fromisoformat(date).strftime('%B %-d, %Y')
title=f"Kalamazoo City Commission, {label}, {nice}"
os.makedirs(f'{d}/out',exist_ok=True)
# agenda
n=int([l for l in subprocess.run(['pdfinfo',f'{d}/raw/agenda.pdf'],capture_output=True,text=True).stdout.splitlines() if l.startswith('Pages')][0].split()[1])
parts=[f"# {title}: Agenda","# Source: agenda PDF, full text. Page numbers match the original.",""]
for p in range(1,n+1):
    t=subprocess.run(['pdftotext','-layout','-f',str(p),'-l',str(p),f'{d}/raw/agenda.pdf','-'],capture_output=True,text=True).stdout
    t='\n'.join(l.rstrip() for l in t.replace('\f','').splitlines()).strip('\n')
    parts+=[f"--- page {p} ---","",t,""]
open(f'{d}/out/agenda.txt','w').write('\n'.join(parts))
# transcript
if os.path.exists(f'{d}/raw/transcript-paste.txt'):
    subprocess.run(['python3',f'{R}/tools/clean_transcript.py',f'{d}/raw/transcript-paste.txt',f'{R}/rosters/kalamazoo-city-commission.csv',f'{d}/out/transcript.txt',f'{d}/transcript-report.txt',title,vid,date])
# minutes OCR
if os.path.exists(f'{d}/raw/minutes.pdf') and not os.path.exists(f'{d}/minutes-ocr.txt'):
    os.makedirs(f'{d}/img',exist_ok=True)
    subprocess.run(['pdftoppm','-r','300','-png',f'{d}/raw/minutes.pdf',f'{d}/img/min'])
    for f in sorted(glob.glob(f'{d}/img/min-*.png')):
        subprocess.run(['tesseract',f,f[:-4],'--psm','4','-l','eng'],capture_output=True)
    with open(f'{d}/minutes-ocr.txt','w') as o:
        for f in sorted(glob.glob(f'{d}/img/min-*.txt')): o.write(f'===== {f}\n'+open(f).read())
print(title)
