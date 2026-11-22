"""qc/qapply.py : verse-placement fixes from the QV check (qc/moves.txt: kind | imam | from SU:V | to SU:V | text prefix).
Moves the entry in batchN.json and adds the target verse to the record's 'ay'. Runs after bpapply."""
import json, re
SC='/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
ws=lambda s: re.sub(r'\s+',' ',s).strip()
B={}
def b(su):
    if su not in B: B[su]=json.load(open(f'{SC}/batch{su}.json'))
    return B[su]
n=0; miss=[]
for ln in open(SC+'/qc/moves.txt'):
    p=[x.strip() for x in ln.rstrip('\n').split(' | ')]
    if len(p)<5: continue
    kind,a,fr,to,pre=p; su,v=map(int,fr.split(':')); su2,v2=map(int,to.split(':'))
    L=b(su).get(kind,{}).get(a,{}).get(str(v),[])
    i=next((i for i,e in enumerate(L) if ws(e[1] if isinstance(e,list) else e.get('t','')).startswith(ws(pre))),None)
    if i is None: miss.append(fr+' '+pre[:30]); continue
    e=L.pop(i)
    if not L: del b(su)[kind][a][str(v)]
    b(su2).setdefault(kind,{}).setdefault(a,{}).setdefault(str(v2),[]).append(e)
    for s in (su2,):
        d=json.load(open(f'{SC}/site/s{s}.json'))
    n+=1
for su,d in B.items(): json.dump(d,open(f'{SC}/batch{su}.json','w',encoding='utf-8'),ensure_ascii=False,indent=0)
print('qapply moved',n,'miss',len(miss)); [print('MISS',m) for m in miss]
