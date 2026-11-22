import json,sys,re
sys.path.insert(0,'/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad/scripts')
from parse import norm
import re
def win(t,v,w):
    key=norm(q[v-1]['text']).split()[:3]
    n=norm(t)
    i=n.find(' '.join(key))
    if i<0: return t[:w]
    s=max(0,i-w//3)
    return t[s:s+w]
d=json.load(open('/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad/out/s2.json'));B=d['books'];R=d['recs']
q=json.load(open('/home/claude/quran/quran-json/data/tanzil/simple-clean.json'))['2']
a=sys.argv[1]; vs=[int(x) for x in sys.argv[2].split(',')]; n=int(sys.argv[3]); w=int(sys.argv[4])
for v in vs:
    print('=====',a,v,q[v-1]['text'][:80])
    xs=[r for r in R if B[r['b']]['a']==a and v in r['ay'] and not r.get('inc')]
    key=' '.join(norm(q[v-1]['text']).split()[:3])
    MK=['اي ','يعني','وهذا يتضمن','يتضمن','فاخبر','فدل','فبين','فان ','والمراد','معناه','قيل','دل علي','وفي هذا','ففيه','فهذا']
    def lex(r):
        n=norm(r['t']); i=n.find(key)
        if i<0: return 0
        seg=n[i:i+600]
        return sum(seg.count(m) for m in MK)
    xs.sort(key=lambda r:(-r['c'], -lex(r), len(r['ay'])>3))
    for r in xs[:n]:
        print('#%d c%d %s %s/%s ay=%s | %s'%(r['id'],r['c'],B[r['b']]['t'][:20],r['v'],r['p'],r['ay'][:5],win(r['t'],v,w)));print()
