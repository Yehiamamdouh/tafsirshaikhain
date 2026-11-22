"""rd3.py K N W surah... : per surah and imam, top-K verses by material, N best passages each (W chars)."""
import json,sys,re,collections
S='/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
sys.path.insert(0,S+'/scripts')
from parse import norm
K,N,W=int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3])
Qc=json.load(open('/home/claude/quran/quran-json/data/tanzil/simple-clean.json'))
MK=['اي ','يعني','يتضمن','فاخبر','فدل','فبين','والمراد','معناه','قيل','دل علي','وفي هذا','ففيه','فهذا','تفسير','فسر']
for su in sys.argv[4:]:
    d=json.load(open(S+'/out/s%s.json'%su));B=d['books'];R=d['recs'];q=Qc[su]
    for a in ('IT','IQ'):
        c=collections.Counter()
        xs_all=[r for r in R if B[r['b']]['a']==a and not r.get('inc') and B[r['b']]['w']!='IjtimacJuyush' and len(norm(r['t']))>60]
        for r in xs_all:
            if len(r['ay'])<=2:
                for v in r['ay']: c[v]+=1+2*(r['c']>0)
        for v,_ in c.most_common(K):
            key=' '.join(norm(q[v-1]['text']).split()[:3])
            def lex(r):
                n=norm(r['t']); i=n.find(key)
                return -1 if i<0 else sum(n[i:i+600].count(m) for m in MK)
            xs=[r for r in xs_all if v in r['ay']]
            xs.sort(key=lambda r:(-r['c'],-lex(r),len(r['ay'])))
            print('=== S%s %s v%d %s'%(su,a,v,q[v-1]['text'][:60]))
            for r in xs[:N]:
                t=re.sub(r'\s+',' ',r['t']); n=norm(t); i=n.find(key)
                s=0 if i<0 else max(0,i-60)
                print(' #%d c%d %s %s/%s | %s'%(r['id'],r['c'],B[r['b']]['w'][:14],r['v'],r['p'],t[s:s+W]))
