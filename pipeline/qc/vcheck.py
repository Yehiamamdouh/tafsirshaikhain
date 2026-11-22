"""qc/vcheck.py : for every excerpt (summ) and نقل on the site, check that its full record actually quotes the verse it is
shown under (3 consecutive words of the verse, or the whole verse if shorter). Flags possible wrong-verse placements."""
import json, re, collections
SC='/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
ws=lambda s: re.sub(r'\s+',' ',s).strip()
DIA=re.compile('[ً-ْٰـۖ-ۭ]')
def n(s):
    s=DIA.sub('',s)
    for a,b in (('أ','ا'),('إ','ا'),('آ','ا'),('ٱ','ا'),('ى','ي'),('ة','ه'),('ؤ','و'),('ئ','ي')): s=s.replace(a,b)
    return ws(re.sub(r'[^\w\s]',' ',s))
out=[]; st=collections.Counter()
for su in range(1,115):
    d=json.load(open(f'{SC}/site/s{su}.json'))
    try: inc=json.load(open(f'{SC}/site/s{su}i.json'))
    except Exception: inc=[]
    R=d['recs']+inc; B=d['books']
    for kind in ('summ','nuq'):
        for a,x in d.get(kind,{}).items():
            for v,L in x.items():
                vw=n(d['verses'][int(v)-1]).split()
                grams=[' '.join(vw[i:i+3]) for i in range(max(1,len(vw)-2))] if len(vw)>=3 else [' '.join(vw)]
                for i,e in enumerate(L):
                    t=ws(e['t']); w=e.get('w') or e.get('b')
                    recs=[r for r in R if t[:60] in ws(r['t'])]
                    if not recs: st['norec']+=1; continue
                    T=' '.join(n(r['t']) for r in recs); E=n(t)
                    ok=any(g in T for g in grams)
                    st[kind+(' ok' if ok else ' FLAG')]+=1
                    if not ok: out.append(dict(su=su,v=int(v),a=a,kind=kind,i=i,t=t[:300],verse=d['verses'][int(v)-1],ref=f"{B[recs[0]['b']]['w']} {recs[0]['v']}/{recs[0]['p']}",inex=any(g in E for g in grams)))
json.dump(out,open(SC+'/qc/vflags.json','w'),ensure_ascii=False,indent=0)
print(dict(st)); print('flags',len(out))
