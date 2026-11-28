"""sheet.py PDF OUTPREFIX pages...  -> contact sheets, 8 pages each, labelled"""
import sys,subprocess,os
from PIL import Image,ImageDraw
pdf,out=sys.argv[1],sys.argv[2]; pages=[int(x) for x in sys.argv[3:]]
tmp='/tmp/sheetpng'; os.makedirs(tmp,exist_ok=True)
ims=[]
for p in pages:
    f=f'{tmp}/p{p}'
    subprocess.run(['pdftoppm','-r','40','-png','-singlefile','-f',str(p),'-l',str(p),pdf,f])
    im=Image.open(f+'.png').convert('RGB'); im.thumbnail((340,440)); 
    c=Image.new('RGB',(350,470),'white'); c.paste(im,(5,25)); ImageDraw.Draw(c).text((5,5),f'p{p}',fill='red'); ims.append(c)
for i in range(0,len(ims),8):
    s=Image.new('RGB',(350*4,470*2),'white')
    for j,im in enumerate(ims[i:i+8]): s.paste(im,((j%4)*350,(j//4)*470))
    s.save(f'{out}-{i//8+1}.png'); print(f'{out}-{i//8+1}.png')
