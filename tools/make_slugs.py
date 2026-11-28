"""make_slugs.py agenda.txt "G1=slug,G2=slug,..." > slugs.csv"""
import os, subprocess,sys,csv
T=dict(l.split('\t',1) for l in subprocess.run(['python3',os.path.join(os.path.dirname(os.path.abspath(__file__)),'agenda_titles.py'),sys.argv[1]],capture_output=True,text=True).stdout.splitlines())
w=csv.writer(sys.stdout,lineterminator='\n'); w.writerow(['item','slug','title'])
for kv in sys.argv[2].split(','):
    k,s=kv.split('='); w.writerow([k,s,T[k]])
