import sys,csv,re,importlib.util
d=sys.argv[1]
src=open(__import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)),'finish_tables.py')).read()
ns={}
exec(src.split('plain, times = load_transcript')[0].replace('mdir','_m'),ns) if False else None
# minimal reimplementation: pull load_transcript function text
start=src.index('def load_transcript'); end=src.index('\ndef read(')
code='import re\n'+src[:src.index('def load_transcript')].split('\n',1)[1] if False else None
exec('import re,csv\n'+src[start:end],ns)
plain,times=ns['load_transcript'](d+'/transcript.txt')
for r in csv.DictReader(open(d+'/public-comment-topics.csv',encoding='utf-8')):
    q=r['quote (exact words from transcript)']
    if q not in plain: print('MISSING:',r['speaker_order'],q)
