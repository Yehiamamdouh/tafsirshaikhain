import json,sys; sys.path.insert(0,'/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad/scripts'); from parse import norm
d=json.load(open('/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad/out/data.json'));B=d['books'];R=d['recs']
a,v=sys.argv[1],int(sys.argv[2]); must=sys.argv[3].split('+') if sys.argv[3] else []; lim=int(sys.argv[4]); w=int(sys.argv[5])
n=0
for r in R:
  if B[r['b']]['a']!=a or v not in r['ay'] or r.get('inc'): continue
  t=norm(r['t'])
  if all(m in t for m in must):
    i=min([t.find(m) for m in must] or [0]); s=max(0,i-w//3)
    print('#%d c%d %s %s/%s | %s'%(r['id'],r['c'],B[r['b']]['t'][:22],r['v'],r['p'],r['t'][s:s+w]));print(); n+=1
    if n>=lim: break
