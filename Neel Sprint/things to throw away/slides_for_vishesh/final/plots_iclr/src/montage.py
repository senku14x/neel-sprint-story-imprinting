import sys
from PIL import Image
files=sys.argv[2:]; out=sys.argv[1]
ims=[Image.open(f).convert("RGB") for f in files]
W=900
ims=[im.resize((W,int(im.size[1]*W/im.size[0]))) for im in ims]
cols=2; rows=(len(ims)+1)//2
hs=[max(ims[i].size[1] for i in range(r*cols,min(len(ims),(r+1)*cols))) for r in range(rows)]
c=Image.new("RGB",(W*cols,sum(hs)),"white"); y=0
for r in range(rows):
    for j in range(cols):
        i=r*cols+j
        if i<len(ims): c.paste(ims[i],(j*W,y))
    y+=hs[r]
c.save(out)
