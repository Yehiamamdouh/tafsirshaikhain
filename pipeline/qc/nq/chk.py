# usage: python3 qc/nq/chk.py OUT PACKET
import json,sys,re
SC='/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
ws=lambda s: re.sub(r'\s+',' ',s).strip()
I=json.load(open(SC+'/qc/nq/items.json')); ids=re.findall(r'^### (N\d+) ',open(sys.argv[2]).read(),re.M)
ST={'أقرّه','استشهد به','حكاه','رجّح غيره','ردّه','أقرّه وزاد عليه','أقرّه وشرحه'}
bad=0; seen=[]
for ln in open(sys.argv[1]):
    p=[x.strip() for x in ln.strip().split(' | ')]
    if not p[0] or p[0] not in ids: continue
    seen.append(p[0])
    if p[1] in ('OK','DROP','HUMAN'): continue
    if p[1]!='FIX': print('BAD verdict',p[0]); bad+=1; continue
    for f in p[2].split(' ;; '):
        m=re.match(r'^(TEXT|WHO|ST|RT)(?:@(\w+)#(\d+))?\s*«(.*)»$',f.strip())
        if not m: print('BAD form',p[0],f[:60]); bad+=1; continue
        op,val=m[1],ws(m[4])
        if m[2]:
            import pickle
            Pw=pickle.load(open(f'{SC}/out/cache/{m[2]}.pkl','rb'))['paras']; i=int(m[3])
            T=' '.join(ws(Pw[j]['text']) for j in range(i,min(len(Pw),i+3)))
            if val not in T: print('BAD not verbatim in cache',p[0],op,val[:50]); bad+=1
        elif op in ('TEXT','RT') and val not in I[p[0]]['P']: print('BAD not verbatim',p[0],op,val[:50]); bad+=1
        if op=='ST' and val not in ST: print('BAD ST',p[0],val); bad+=1
miss=[x for x in ids if x not in seen]
if miss: print('MISSING',miss[:10]); bad+=len(miss)
if [x for x in ids if x in seen]!=seen[:len([x for x in ids if x in seen])]: pass
print('items',len(ids),'done',len(set(seen)),'bad',bad)
