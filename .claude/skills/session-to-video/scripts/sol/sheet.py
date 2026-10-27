# -*- coding: utf-8 -*-
import sys, glob, os
from PIL import Image, ImageDraw, ImageFont
W=r"C:\Azlanti\Video\Session0\02__Жульничество\art\sol_run1"
out=sys.argv[1]; frames=[int(x) for x in sys.argv[2:]]
f=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',26)
w,h,pad,lab,cols=640,360,10,34,4
fs=[]
for n in frames:
    g=sorted(glob.glob(os.path.join(W,"shot%02d_*.png"%n)))
    if g: fs.append((n,g[-1]))
rows=(len(fs)+cols-1)//cols
c=Image.new('RGB',(cols*(w+pad)+pad,rows*(h+lab+pad)+pad),'white'); d=ImageDraw.Draw(c)
for k,(n,p) in enumerate(fs):
    x=pad+(k%cols)*(w+pad); y=pad+(k//cols)*(h+lab+pad)
    d.text((x,y+2),os.path.basename(p)[:-4],fill=(40,30,20),font=f)
    im=Image.open(p).convert('RGB').resize((w,h)); c.paste(im,(x,y+lab))
c.save(out,quality=85); print(out,c.size,len(fs))
