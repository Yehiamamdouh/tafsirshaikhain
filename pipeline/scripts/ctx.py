import json,sys,re
S='/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
f=sys.argv[1]; d=json.load(open(S+'/site/'+f,encoding='utf-8'))
recs={r['id']:r for r in d['recs']}
try:
    for r in json.load(open(S+'/site/'+f.replace('.json','i.json'),encoding='utf-8')): recs[r['id']]=r
except Exception: pass
for spec in sys.argv[2:]:
    i,key=spec.split(':',1)
    r=recs[int(i)]; t=r['t']; k=t.find(key)
    if k<0: print('#',i,'KEY NOT FOUND',key); continue
    print('#%s %s %s/%s | %s\n'%(i,d['books'][r['b']]['t'][:20],r['v'],r['p'],t[max(0,k-250):k+700]))
