import sys,glob,json,collections
S='/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
sys.path.insert(0,S+'/scripts')
from shingle import words,grams
book,imam=sys.argv[1:3]
G=collections.defaultdict(set); REC={}
for su in range(1,115):
    try: d=json.load(open(f'{S}/out/s{su}.json'))
    except: continue
    for r in d['recs']:
        if d['books'][r['b']]['a']!=imam or len(r['ay'])>4: continue
        key=(su,r['id']); REC[key]=r['ay']
        for g in set(grams(words(r['t']))): G[g].add(key)
rows=json.load(open(f'{S}/books/{book}_nov.json'))
hitv=collections.defaultdict(set)   # (su,v) -> pages
for pg,k,n,fr,para in rows:
    if fr is None or fr<0.3: continue
    c=collections.Counter()
    for g in grams(words(para)):
        for key in G.get(g,()): c[key]+=1
    for key,cnt in c.items():
        if cnt>=max(5,0.3*n):
            for v in REC[key]: hitv[(key[0],v)].add(pg)
have=set()
for su in range(1,115):
    s=json.load(open(f'{S}/site/s{su}.json')).get('summ',{}).get(imam,{})
    have|={(su,int(v)) for v in s}
inb=set(hitv); miss=sorted(inb-have)
print(book,imam,'verses linked via book paragraphs:',len(inb),' already summarized:',len(inb&have),' missing:',len(miss))
json.dump([f'{s}:{v}' for s,v in miss],open(f'{S}/books/{book}_missing.json','w'))
print(collections.Counter(s for s,v in miss).most_common(10))
