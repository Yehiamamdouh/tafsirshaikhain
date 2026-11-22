import json,sys,re
Q=json.load(open('/home/claude/quran/quran-json/data/tanzil/simple.json'))
ws=lambda s: re.sub(r'\s+',' ',s).strip()
L=[o for o in json.load(open('review/_wrongverse.json')) if not any(k[0]==o['s'] and abs(k[1]-o['v'])<=2 for k in o['others'])]
for i,o in enumerate(L): o['i']=i
a,b=int(sys.argv[1]),int(sys.argv[2])
for o in L[a:b]:
    t=ws(o['t']); w=o['win']; j=w.find(t)
    pre=w[max(0,j-140):j]; post=w[j+len(t):j+len(t)+60]
    vt=' '.join(Q[str(o['s'])][o['v']-1]['text'].split()[:9])
    oth=','.join(f'{x}:{y}' for x,y in o['others'])
    print(f"#{o['i']} {o['s']}:{o['v']} {o['a']}｜{vt}  [قرب: {oth}]\n S: {t[:170]}\n C: {pre}【…】{post}")
