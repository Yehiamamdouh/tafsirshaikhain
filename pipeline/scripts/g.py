import json,sys
S='/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
d=json.load(open(S+'/out/s%s.json'%sys.argv[1],encoding='utf-8')); R={r['id']:r for r in d['recs']}
for spec in sys.argv[2:]:
    i,_,key=spec.partition(':'); r=R[int(i)]; t=r['t']; k=t.find(key) if key else 0
    if k<0: print('#',i,'NOKEY',key); continue
    print('#%s %s %s/%s | %s\n'%(i,d['books'][r['b']]['t'][:20],r['v'],r['p'],t[max(0,k-100):k+1100]))
