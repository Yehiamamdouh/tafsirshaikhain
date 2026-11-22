import json,sys
fl=json.load(open('review/_sorted.json'))
a,b=int(sys.argv[1]),int(sys.argv[2]); W=int(sys.argv[3]) if len(sys.argv)>3 else 130
prev=None
for x in fl[a:b]:
    s=x['summary']; c=x['context']; j=c.find(s[:30])
    v=' '.join(x['ayah_text'].split()[:8])
    if s==prev:
        print(f"#{x['n']} {x['ayah']} ｜{v}  (same S)"); continue
    prev=s
    cc=c[max(0,j-W):j]+'【…】'+c[j+len(s):j+len(s)+W] if j>=0 else c[:2*W]
    print(f"#{x['n']} {x['ayah']} {x['imam'][4:]}｜{v}\n S: {s}\n C: {cc}")
