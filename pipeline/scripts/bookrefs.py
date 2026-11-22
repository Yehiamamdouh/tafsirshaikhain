import re,json,glob,sys,collections
S='/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
sys.path.insert(0,S+'/scripts')
from parse import norm
html=open(S+'/site/index.html').read()
m=re.search(r'\["الفاتحة".*?\]',html); NAMES=json.loads(m.group(0))
NN={norm(n).replace('ال','',1) if norm(n).startswith('ال') else norm(n):i+1 for i,n in enumerate(NAMES)}
def sid(name):
    k=norm(name).strip()
    if k.startswith('ال'): k=k[2:]
    return NN.get(k)
AR='٠١٢٣٤٥٦٧٨٩'
def toint(s): return int(''.join(str(AR.index(c)) if c in AR else c for c in s))
pat=re.compile(r'[\[\(]\s*(?:سورة\s*)?([^\[\]\(\):\d٠-٩]{2,14}?)\s*[:،]\s*([0-9٠-٩]{1,3})(?:\s*[-–]\s*([0-9٠-٩]{1,3}))?\s*[\]\)]')
def refs(book):
    out=collections.defaultdict(set)
    for f in sorted(glob.glob(f'{S}/books/{book}/*.txt')):
        pg=int(f[-8:-4]); t=open(f).read()
        for nm,a,b in pat.findall(t):
            s=sid(nm)
            if not s: continue
            a=toint(a); b=toint(b) if b else a
            if b<a or b-a>15: b=a
            for v in range(a,b+1): out[(s,v)].add(pg)
    return out
if __name__=='__main__':
    for bk in sys.argv[1:]:
        r=refs(bk); su=collections.Counter(s for s,v in r)
        json.dump({f'{s}:{v}':sorted(p) for (s,v),p in r.items()},open(f'{S}/books/{bk}_refs.json','w'))
        print(bk,len(r),'verses; top surahs',su.most_common(8))
