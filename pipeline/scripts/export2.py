import json,sys,re,os,glob,collections
S='/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
sys.path.insert(0,S+'/scripts')
from parse import norm
from need import Qc,MK
NAME={'IT':'ابن تيمية','IQ':'ابن القيم'}
ws=lambda s: re.sub(r'\s+',' ',s).strip()
OUT=S+'/wave3'; os.makedirs(OUT,exist_ok=True)
for f in glob.glob(OUT+'/*'): os.remove(f)
# normalize stances in batch files
MAP={'أقرّه وشرحه':'أقرّه','أقرّه وزاد عليه':'أقرّه','رجّحه':'أقرّه','وجّهه':'أقرّه','ردّه في هذه الآية':'ردّه','حكاه ورجّح غيره':'رجّح غيره'}
for su in range(2,115):
    p=S+f'/batch{su}.json'
    if not os.path.exists(p): continue
    b=json.load(open(p)); ch=0
    for a,m in b.get('nuq',{}).items():
        for v,l in m.items():
            for it in l:
                if it.get('st') in MAP: it['st']=MAP[it['st']]; ch=1
    if ch: json.dump(b,open(p,'w'),ensure_ascii=False,indent=1)
def window(t,key,W):
    n=norm(t); i=n.find(key) if key else -1
    s=0 if i<0 else max(0,i-500); return t[s:s+W]
A=[];Bt=[];C=[]
for su in range(2,115):
    d=json.load(open(S+'/out/s%d.json'%su));B=d['books'];R=d['recs'];q=Qc[str(su)]
    bt=json.load(open(S+f'/batch{su}.json')) if os.path.exists(S+f'/batch{su}.json') else {}
    summ=bt.get('summ',{})
    for a in ('IT','IQ'):
        have={int(v):[x[1] for x in l] for v,l in summ.get(a,{}).items()}
        byv=collections.defaultdict(list)
        for r in R:
            if B[r['b']]['a']!=a or r.get('inc') or len(r['ay'])>4: continue
            for v in r['ay']: byv[v].append(r)
        for v,rs in byv.items():
            key=' '.join(norm(q[v-1]['text']).split()[:3])
            def sc(r):
                n=norm(r['t']); i=n.find(key)
                return (-(r['c']>0), -(-1 if i<0 else sum(n[i:i+600].count(m) for m in MK)), len(r['ay']))
            rs.sort(key=sc)
            mk=lambda r,W:{'w':B[r['b']]['w'],'ref':'%s/%s'%(r['v'],r['p']),'text':window(ws(r['t']),key,W)}
            base={'surah':su,'imam':a,'imam_name':NAME[a],'ayah':v,'ayah_text':q[v-1]['text']}
            if v in have:
                L=sum(len(x) for x in have[v])
                if L<80:
                    Bt.append(dict(base,task='B',existing=have[v],passages=[mk(r,1800) for r in rs if B[r['b']]['w']!='IjtimacJuyush'][:3]))
            else:
                ps=[r for r in rs if B[r['b']]['w']!='IjtimacJuyush'][:2]
                pj=[r for r in rs if B[r['b']]['w']=='IjtimacJuyush'][:1]
                ps=[mk(r,1500) for r in ps+pj]
                if ps: A.append(dict(base,task='A',passages=ps))
    # C: stances
    allrecs=[(B[r['b']]['a'],B[r['b']]['w'],ws(r['t'])) for r in R]
    for a,m in bt.get('nuq',{}).items():
        for v,l in m.items():
            for i,it in enumerate(l):
                t=ws(it['t']); ctx=''
                for aa,w,txt in allrecs:
                    if aa==a and w==it['w'] and t in txt:
                        j=txt.find(t); ctx=txt[max(0,j-700):j+len(t)+700]; break
                if not ctx: continue
                C.append({'task':'C','id':f'{su}|{a}|{v}|{i}','surah':su,'ayah':int(v),'imam':a,'imam_name':NAME[a],'w':it['w'],'who':it['who'],'t':it['t'],'current_st':it['st'],'current_rt':it.get('rt',''),'context':ctx})
def dump(items,pre,n):
    for k in range(0,len(items),n):
        json.dump({'task':pre,'items':items[k:k+n]},open(f'{OUT}/{pre}_{k//n+1:03d}.json','w'),ensure_ascii=False,indent=1)
    return (len(items)+n-1)//n
print('A',len(A),dump(A,'A',45),'B',len(Bt),dump(Bt,'B',40),'C',len(C),dump(C,'C',60))
