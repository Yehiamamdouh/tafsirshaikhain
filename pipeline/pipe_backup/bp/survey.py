"""bp/survey.py : per uncovered verse, count book paragraphs (all caches) that quote it, by imam."""
import json, pickle, glob, os, collections
SC='/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
cov=set(); nv={}
for su in range(1,115):
    d=json.load(open(f'{SC}/site/s{su}.json')); nv[su]=len(d['verses'])
    for k in ('summ','nuq'):
        for a,x in d.get(k,{}).items():
            for v in x: cov.add((su,int(v)))
# imam per work
wa={}
for su in range(1,115):
    for b in json.load(open(f'{SC}/site/s{su}.json'))['books']: wa[b['w']]=b['a']
hits=collections.defaultdict(list)
noa=set()
for f in sorted(glob.glob(SC+'/out/cache/*.pkl')):
    w=os.path.basename(f)[:-4]; d=pickle.load(open(f,'rb'))
    a=wa.get(w) or d.get('meta',{}).get('a') or d.get('meta',{}).get('author')
    if a not in ('IT','IQ'): noa.add((w,str(d.get('meta'))[:120])); 
    for i,c in enumerate(d['per']):
        for (su,v),n in c.items():
            if (su,v) not in cov: hits[(su,v)].append((w,a,i,n))
unc=[(su,v) for su in nv for v in range(1,nv[su]+1) if (su,v) not in cov]
print('uncovered',len(unc))
c=collections.Counter()
for k in unc:
    h=hits.get(k,[]); n=len(h)
    c['0' if n==0 else '1' if n==1 else '2-3' if n<=3 else '4-9' if n<=9 else '10+']+=1
print(c)
print('no-author works',len(noa)); [print(x) for x in list(noa)[:10]]
json.dump({f'{su}:{v}':hits.get((su,v),[]) for su,v in unc}, open(SC+'/bp/hits.json','w'))
