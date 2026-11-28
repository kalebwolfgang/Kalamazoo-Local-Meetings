"""List a packet's bookmarks with page numbers. usage: bookmarks.py PACKET.pdf"""
import sys
from pypdf import PdfReader
r=PdfReader(sys.argv[1])
def walk(o,d=0):
    for x in o:
        if isinstance(x,list): walk(x,d+1)
        else:
            n=r.get_destination_page_number(x)
            if d<=1 and n in (None,0) and d>0: continue
            print('  '*d+x.title[:75], '' if n is None else n+1)
walk(r.outline)
