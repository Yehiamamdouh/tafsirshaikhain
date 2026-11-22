"""bp/cand.py : score every cache paragraph that quotes an uncovered verse; write bp/cand.json (verse -> ranked hits)."""
import json, pickle, os, re, collections, sys
SC='/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
ws=lambda s: re.sub(r'\s+',' ',s).strip()
DIA=re.compile('[ً-ْٰـۖ-ۭ]')
def norm_map(t):
    out,idx=[],[]
    for i,ch in enumerate(t):
        if DIA.match(ch): continue
        out.append({'أ':'ا','إ':'ا','آ':'ا','ٱ':'ا','ى':'ي','ة':'ه'}.get(ch,ch)); idx.append(i)
    return ''.join(out),idx
MARK=re.compile(r'أي |يعني|معناه|المراد|فأخبر|أخبر|فدل|دل على|دلت|ففيه|فبين|بين أن|تضمن|يتضمن|فسر|تفسير|ومعنى|والمعنى|ذكر .{0,20}أن|وهذا يدل|فهذا')
hits=json.load(open(SC+'/bp/hits.json'))
verses={}
for su in range(1,115): verses[su]=json.load(open(f'{SC}/site/s{su}.json'))['verses']
WA=json.load(open(SC+'/bp/wa.json'))
need=collections.defaultdict(list)
for k,L in hits.items():
    for w,a,i,n in L: need[w].append((k,i))
out=collections.defaultdict(list)
for w,L in need.items():
    d=pickle.load(open(f'{SC}/out/cache/{w}.pkl','rb')); P=d['paras']; per=d['per']
    for k,i in L:
        su,v=map(int,k.split(':'))
        T=ws(P[i]['text']); tn,mp=norm_map(T)
        vn,_=norm_map(ws(verses[su][v-1])); words=vn.split()
        j=-1
        for m in (4,3,2):
            if len(words)>=m:
                j=tn.find(' '.join(words[:m]))
                if j>=0: break
        if j<0 and len(words)>=3:
            j=tn.find(' '.join(words[-3:]))
        pos=mp[j] if j>=0 else T.find('{')
        aft=T[pos:pos+600]
        nver=len(per[i]); mk=len(MARK.findall(aft))
        hdr=P[i].get('header','') or ''
        sc=mk*2-max(0,nver-3)+(4 if '{' in hdr and k in str(per[i]) else 0)-(2 if len(T)<120 else 0)
        out[k].append(dict(w=w,a=WA.get(w,'?'),i=i,sc=sc,mk=mk,nv=nver,pos=pos,L=len(T)))
for k in out: out[k].sort(key=lambda x:-x['sc'])
json.dump(out,open(SC+'/bp/cand.json','w'),ensure_ascii=False)
best=collections.Counter()
for k,L in out.items():
    b=L[0]; best['mk0' if b['mk']==0 else 'mk1' if b['mk']==1 else 'mk2+']+=1
print(len(out),best)
print('hits total',sum(len(L) for L in out.values()),'with mk>=1',sum(1 for L in out.values() for x in L if x['mk']>=1))
