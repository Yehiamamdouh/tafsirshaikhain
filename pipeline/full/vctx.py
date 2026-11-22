import json, re, os, sys, pickle, collections
SC='/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
exec(open(SC+'/full/voice2.py').read().split('flags = []')[0].replace("BASE = sys.argv[1] if len(sys.argv) > 1 else SC + '/site'","BASE = SC + '/site'"))
want=[tuple(x.split(':',2)) for x in sys.argv[1:]]  # su:v:prefix
for su_, v_, pre in want:
    su=int(su_); d=json.load(open(f'{BASE}/s{su}.json')); p=f'{BASE}/s{su}i.json'
    inc=json.load(open(p)) if os.path.exists(p) else []
    R={r['id']:r for r in d['recs']+inc}; B=d['books']
    for a,vs in d['summ'].items():
        for x in vs.get(v_,[]):
            if not x['t'].startswith(pre): continue
            r=R[x['r']]; w=B[r['b']]['w']; T=ws(r['t']); P,first=paras(w); k=first[T[:80]][0]; i=T.find(x['t'])
            ctx=' ‖ '.join(P[max(0,k-14):k]+[T[:i]])
            o=[m for m in OPEN.finditer(ctx)][-1]
            print('=====',su,v_,a,w,r['v'],r['p']); print(ctx[o.start():][-3000:] if len(ctx)-o.start()>3000 else ctx[o.start():]); print('   [[ITEM]]', x['t'][:200]); print()
