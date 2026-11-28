"""minfmt.py minutes.pdf : draft minutes.txt body from a text-layer PDF (margin headings in [brackets])"""
import sys,subprocess,re
pdf=sys.argv[1]
n=int(re.search(r'Pages:\s+(\d+)',subprocess.run(['pdfinfo',pdf],capture_output=True,text=True).stdout).group(1))
out=[]
for p in range(1,n+1):
    t=subprocess.run(['pdftotext','-layout','-f',str(p),'-l',str(p),pdf,'-'],capture_output=True,text=True).stdout
    L=[l.rstrip() for l in t.split('\n')]
    L=[l for l in L if l.strip()]
    head=L[0]; m=re.search(r'Page (\d+)',head); pg=m.group(1) if m else '?'
    left = head.strip().startswith('Page')==False  # odd page: margin on left
    out.append(f'--- page {pg} ---\n')
    body=[];marg=[]
    for l in L[1:]:
        if re.fullmatch(r'\s*CC-\d{4}-\d+\s*',l): continue
        chunks=[(m.start(),m.group()) for m in re.finditer(r'\S+(?: \S+)*',l)]
        b=[];mg=[]
        for s,c in chunks:
            if left and s<24 and len(l)-len(l.lstrip())<24 and any(cs>=24 for cs,_ in chunks) : mg.append(c)
            elif left and s<24 and not any(cs>=24 for cs,_ in chunks) and len(c)<30 and not c.startswith('-'): mg.append(c)
            elif not left and s>=78: mg.append(c)
            else: b.append(c)
        body.append(' '.join(b)); marg.append(' '.join(mg))
    for b,mg in zip(body,marg):
        out.append(('{{'+mg+'}} ' if mg else '')+b)
    out.append('')
print('\n'.join(out))
