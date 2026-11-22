"""rdv.py SURAH IMAM N W [from-to]: for verses still needing a summary, print N best passages."""
import json,sys,re
S='/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
sys.path.insert(0,S+'/scripts')
from parse import norm
from need import need,Qc,MK
su=int(sys.argv[1]);a=sys.argv[2];N=int(sys.argv[3]);W=int(sys.argv[4])
lo,hi=(map(int,sys.argv[5].split('-')) if len(sys.argv)>5 else (1,999))
d=json.load(open(S+'/out/s%d.json'%su));B=d['books'];R=d['recs'];q=Qc[str(su)]
for v in need(su)[a]:
    if not lo<=v<=hi: continue
    key=' '.join(norm(q[v-1]['text']).split()[:3])
    def lex(r):
        n=norm(r['t']); i=n.find(key)
        return -1 if i<0 else sum(n[i:i+500].count(m) for m in MK)
    xs=[r for r in R if B[r['b']]['a']==a and v in r['ay'] and not r.get('inc') and B[r['b']]['w']!='IjtimacJuyush' and len(r['ay'])<=2]
    xs.sort(key=lambda r:(-(r['c']>0),-lex(r),len(r['ay'])))
    print('=== %s v%d %s'%(a,v,q[v-1]['text'][:70]))
    for r in xs[:N]:
        t=re.sub(r'\s+',' ',r['t']); n=norm(t); i=n.find(key)
        s=0 if i<0 else max(0,i-40)
        print(' #%d c%d %s %s/%s | %s'%(r['id'],r['c'],B[r['b']]['w'][:16],r['v'],r['p'],t[s:s+W]))
