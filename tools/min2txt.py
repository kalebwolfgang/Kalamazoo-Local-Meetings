"""min2txt.py minutes.pdf : draft minutes.txt body (paragraphs joined, margin headings in [brackets]) from a text-layer PDF."""
import sys, subprocess, re
pdf = sys.argv[1]
n = int(re.search(r'Pages:\s+(\d+)', subprocess.run(['pdfinfo', pdf], capture_output=True, text=True).stdout).group(1))
DOC = re.compile(r'^\d{4}-\d{2}-\d{2}$')
out = []
for p in range(1, n + 1):
    t = subprocess.run(['pdftotext', '-layout', '-f', str(p), '-l', str(p), pdf, '-'], capture_output=True, text=True).stdout
    L = [l.rstrip() for l in t.replace('\f', '').split('\n')]
    while L and not L[0].strip(): L.pop(0)
    if not L: continue
    head = L[0]; m = re.search(r'Page (\d+)', head); pg = m.group(1) if m else '?'
    left = not head.strip().startswith('Page')
    L = [l for l in L[1:] if not re.fullmatch(r'\s*CC-\d{4}-\d+\s*', l)]
    out.append(f'--- page {pg} ---\n')
    rows = []  # (body_col, body_text, margin_text) or None for blank
    for l in L:
        if not l.strip(): rows.append(None); continue
        chunks = [(mm.start(), mm.group()) for mm in re.finditer(r'\S+(?: \S+)*', l)]
        b = []; mg = []
        for s, c in chunks:
            if left and s < 24 and any(cs >= 24 for cs, _ in chunks): mg.append(c)
            elif left and s < 24 and len(c) < 34 and not c.startswith('-') and not re.match(r'[a-z]', c): mg.append(c)
            elif not left and s >= 76: mg.append(c)
            else: b.append((s, c))
        rows.append((b[0][0] if b else None, ' '.join(c for _, c in b), ' '.join(mg)))
    cols = sorted(r[0] for r in rows if r and r[0] is not None)
    base = min(cols) if cols else 0
    paras = []; cur = None
    for r in rows:
        if r is None:
            if cur and cur['body']: paras.append(cur); cur = None
            continue
        col, body, mg = r
        if cur is None: cur = {'body': [], 'marg': [], 'col': None}
        if mg: cur['marg'].append(mg)
        if body:
            if cur['col'] is None: cur['col'] = col
            cur['body'].append(body)
    if cur and (cur['body'] or cur['marg']): paras.append(cur)
    pending = []
    for pa in paras:
        marg = pending + pa['marg']; pending = []
        if not pa['body']: pending = marg; continue
        docs = [x for x in marg if DOC.match(x)]; rest = [x for x in marg if not DOC.match(x)]
        tags = ([f'[{" ".join(rest)}]'] if rest else []) + [f'[{d}]' for d in docs]
        txt = ''
        for b in pa['body']:
            if not txt: txt = b
            elif txt.endswith('-') and re.match(r'\d', b): txt += b
            else: txt += ' ' + b
        roll = txt.startswith('COMMISSIONERS')
        if roll:
            first = pa['body'][0]
            txt = re.sub(r'\s{2,}', ' ', first.replace(':', ':', 1))
            k, v = first.split(':', 1)
            txt = k + ': ' + ', '.join([v.strip()] + pa['body'][1:])
        ind = '    ' if pa['col'] is not None and pa['col'] > base + 2 and not roll else ''
        if tags: out.append(' '.join(tags))
        out.append(ind + txt + '\n')
    if pending: out.append(' '.join(f'[{x}]' for x in pending) + '\n')
print('\n'.join(out).rstrip() + '\n')
