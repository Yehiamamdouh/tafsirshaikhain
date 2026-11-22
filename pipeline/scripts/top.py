import json,collections,sys
S='/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
n=int(sys.argv[1]); k=int(sys.argv[2]) if len(sys.argv)>2 else 12
d=json.load(open(S+'/site/s%d.json'%n));B=d['books']
for a in ('IT','IQ'):
    c=collections.Counter()
    for r in d['recs']:
        if B[r['b']]['a']==a and len(r['ay'])<=2:
            for v in r['ay']: c[v]+=1+2*(r['c']>0)
    print(n,a,c.most_common(k))
