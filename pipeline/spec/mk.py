"""spec/mk.py : packets for the specialist triage (spec/alive.json -> spec/pk/S01..)."""
import json, os, re, collections
SC='/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
ws=lambda s: re.sub(r'\s+',' ',s).strip()
A=json.load(open(SC+'/spec/alive.json'))
Q=json.load(open('/home/claude/tafsirshaikhain/src/data/simple.json'))
CH=json.load(open('/home/claude/tafsirshaikhain/src/data/chapters.json'))['chapters']
IM={'IT':'ابن تيمية','IQ':'ابن القيم'}
def qv(su,v):
    x=Q[str(su)]; x=x.get(str(v)) if isinstance(x,dict) else x[v-1]; return x['text'] if isinstance(x,dict) else x
site={}
for su in range(1,115):
    d=json.load(open(f'{SC}/site/s{su}.json')); p=f'{SC}/site/s{su}i.json'
    inc=json.load(open(p)) if os.path.exists(p) else []
    site[su]=(d,{r['id']:r for r in d['recs']+inc},{b['id']:b for b in d['books']})
# group questions by (kind,su,v,a)
G=collections.OrderedDict()
for r in A: G.setdefault((r['kind'],r['su'],r['v'],r['a']),[]).append(r)
blocks=[]
for (kind,su,v,a),rs in G.items():
    d,R,B=site[su]; L=d['summ' if kind=='s' else 'nuq'][a][str(v)]
    iid=f'{kind}{su}:{v}:{a}'
    o=[f'### {iid} — {CH[su-1]["name"]} {v} — {IM[a]} — {"مختصر" if kind=="s" else "نقل"}', f'الآية: {qv(su,v)}']
    recs={}
    for i,e in enumerate(L):
        b=B.get(e['b'],{}); extra=''
        if kind=='n': extra=f'  [who: {e.get("who","")} | st: {e.get("st","")} | rt: «{e.get("rt","")}»]'
        o.append(f'  [{i}] rec{e["r"]} ({b.get("t","")} {e.get("v")}/{e.get("p")}) w={b.get("w","")}: «{ws(e["t"])}»'+(f'  [سطر سياق: {e["cx"]}]' if e.get('cx') else '')+extra)
        r=R.get(e['r'])
        if r and e['r'] not in recs: recs[e['r']]=(r,b)
    o.append('الأسئلة المفتوحة من الجولات السابقة:')
    for r in rs: o.append(f'  - ({r["src"]}) {r["q"]}')
    for rid,(r,b) in recs.items():
        o.append(f'النص الكامل rec{rid} ({b.get("t","")} {r.get("v")}/{r.get("p")}-{r.get("pe",r.get("p"))}) w={b.get("w","")}:'); o.append(ws(r['t']))
    blocks.append((iid,'\n'.join(o)+'\n'))
os.makedirs(SC+'/spec/pk',exist_ok=True); n=35
for k in range(0,len(blocks),n):
    open(f'{SC}/spec/pk/S{k//n+1:02d}.txt','w').write('\n'.join(b for _,b in blocks[k:k+n]))
json.dump([i for i,_ in blocks],open(SC+'/spec/ids.json','w'))
print('items',len(blocks),'packets',(len(blocks)+n-1)//n)
