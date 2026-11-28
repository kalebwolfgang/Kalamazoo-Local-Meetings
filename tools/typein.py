"""typein.py PACKET_DIR PAGE TEXTFILE : replace the body of one packet page in whichever .txt holds it"""
import sys,glob,re
d,p,tf=sys.argv[1],int(sys.argv[2]),sys.argv[3]
body=open(tf).read().strip('\n')
for f in glob.glob(d+'/*.txt'):
    s=open(f).read()
    m=re.search(rf'(--- packet page {p} ---\n)(.*?)(?=\n--- packet page \d+ ---|\Z)',s,re.S)
    if m:
        s=s[:m.start(2)]+'\n'+body+'\n'+s[m.end(2):]
        open(f,'w').write(s); print('page',p,'->',f.split('/')[-1]); break
else: print('page not found',p)
