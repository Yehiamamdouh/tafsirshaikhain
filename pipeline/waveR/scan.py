import sys,json,re
sys.path.insert(0,'/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad/scripts')
from waveR_scan import *
V=[];K=[];W=[]
START=re.compile(r'^(و?(هذا|هذه|ذلك|تلك|هو|هي|هم|فإن|فإنه|لأن|لأنه|ف|ثم|أي|بل|لكن|ولكن|أو|إلا|حتى|كما|فهذا|فهو|فلهذا|ولهذا|وهذا))\b')
SAY=re.compile(r'(^|\s)(و?قال|وقالوا|قالوا|قيل|يقال|روى|روي|حكى|ذكر|زعم|زعموا|عن)\s')
for n in range(1,115):
    d,R=load(n)
    for a,av in d.get('summ',{}).items():
        for v,lst in av.items():
            vt=d['verses'][int(v)-1]; vw=words(vt)
            big={(vw[i],vw[i+1]) for i in range(len(vw)-1)}; uni={w for w in vw if len(w)>=4}
            for i,it in enumerate(lst):
                iid=f'{n}|{a}|{v}|{i}'
                b,af=ctx(R,it,400,400)
                near=words(b[-300:]+' '+it['t']+' '+af[:300])
                hasbig=any((near[j],near[j+1]) in big for j in range(len(near)-1))
                hasuni=len(uni & set(near))
                base=dict(id=iid,imam=a,ayah=f'{n}:{v}',verse=vt,t=it['t'])
                if not hasbig and hasuni<2:
                    V.append(dict(base,context_before=b,context_after=af))
                t=it['t'].strip()
                end_ok=re.search(r'[\.\!\؟\?»\]\}\)"]\s*$',t)
                if START.match(t) or not end_ok:
                    K.append(dict(base,context_before=b,context_after=af))
                if SAY.search(t[:120]) or t.startswith('"') or t.startswith('«'):
                    W.append(dict(base,context_before=b,context_after=af))
print(len(V),len(K),len(W))
json.dump(dict(V=V,K=K,W=W),open('/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad/waveR/cands.json','w'),ensure_ascii=False)
