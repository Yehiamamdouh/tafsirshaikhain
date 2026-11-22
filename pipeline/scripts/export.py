import json,sys,re
S='/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
sys.path.insert(0,S+'/scripts')
from parse import norm
from need import need,Qc,MK
NAME={'IT':'ابن تيمية','IQ':'ابن القيم'}
items=[]
for su in range(2,115):
    d=json.load(open(S+'/out/s%d.json'%su));B=d['books'];R=d['recs'];q=Qc[str(su)]
    nd=need(su)
    for a in ('IT','IQ'):
        for v in nd[a]:
            key=' '.join(norm(q[v-1]['text']).split()[:3])
            def lex(r):
                n=norm(r['t']); i=n.find(key)
                return -1 if i<0 else sum(n[i:i+500].count(m) for m in MK)
            xs=[r for r in R if B[r['b']]['a']==a and v in r['ay'] and not r.get('inc') and B[r['b']]['w']!='IjtimacJuyush' and len(r['ay'])<=2]
            xs.sort(key=lambda r:(-(r['c']>0),-lex(r),len(r['ay'])))
            ps=[]
            for r in xs[:3]:
                t=re.sub(r'\s+',' ',r['t']); n=norm(t); i=n.find(key)
                s=0 if i<0 else max(0,i-500)
                ps.append({'w':B[r['b']]['w'],'ref':'%s/%s'%(r['v'],r['p']),'text':t[s:s+1800]})
            if ps: items.append({'surah':su,'imam':a,'imam_name':NAME[a],'ayah':v,'ayah_text':q[v-1]['text'],'passages':ps})
n=40
for k in range(0,len(items),n):
    json.dump(items[k:k+n],open(S+'/astra/batch_%02d.json'%(k//n+1),'w'),ensure_ascii=False,indent=1)
print(len(items),(len(items)+n-1)//n)
