"""bp/mk.py TIER : packets bp/pk/B###.txt for uncovered verses. TIER 1 = some hit with explanation markers or a
paragraph quoting <=2 verses; TIER 2 = the rest. Per verse up to 3 paragraphs (best per imam first)."""
import json, pickle, re, sys, collections
SC='/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
ws=lambda s: re.sub(r'\s+',' ',s).strip()
DIA=re.compile('[ً-ْٰـۖ-ۭ]')
tier=int(sys.argv[1]); start=int(sys.argv[2]) if len(sys.argv)>2 else 1
C=json.load(open(SC+'/bp/cand.json'))
V={su:json.load(open(f'{SC}/site/s{su}.json'))['verses'] for su in range(1,115)}
def t1(L): return any(x['mk']>=1 or x['nv']<=2 for x in L)
keys=sorted([k for k,L in C.items() if (t1(L) if tier==1 else not t1(L))], key=lambda k:tuple(map(int,k.split(':'))))
PC={}
def P(w):
    if w not in PC: PC[w]=pickle.load(open(f'{SC}/out/cache/{w}.pkl','rb'))['paras']
    return PC[w]
blocks=[]
for k in keys:
    su,v=map(int,k.split(':')); L=C[k]
    pick=[]; seen=set()
    for a in ('IT','IQ'):
        x=next((x for x in L if x['a']==a),None)
        if x: pick.append(x)
    for x in L:
        if len(pick)>=3: break
        if x not in pick: pick.append(x)
    pick.sort(key=lambda x:-x['sc'])
    out=[f"\n### {k} — VERSE: {DIA.sub('',V[su][v-1])}   ({len(L)} paragraphs quote it)"]
    for x in pick:
        Pw=P(x['w']); i=x['i']; T=ws(Pw[i]['text'])
        sig=T[max(0,x['pos']-80):x['pos']+200]
        if sig in seen: continue
        seen.add(sig)
        if len(T)<=2600: a0,a1=0,len(T)
        else: a0,a1=max(0,x['pos']-600),min(len(T),x['pos']+1600)
        txt=('…' if a0 else '')+T[a0:a1]+('…' if a1<len(T) else '')
        p=Pw[i]
        out.append(f"-- {x['a']} {x['w']}#{i} ({p['vol']}/{p['p_start']}) [{ws(p.get('header','') or '')[:80]}]\n{txt}")
        if a1>=len(T)-400 and i+1<len(Pw):
            N=ws(Pw[i+1]['text']); out.append(f"   [#{i+1} التالية] {N[:900]}{'…' if len(N)>900 else ''}")
    blocks.append('\n'.join(out))
n=start; cur=[]
import os; os.makedirs(SC+'/bp/pk',exist_ok=True)
def flush():
    global n,cur
    if cur: open(f'{SC}/bp/pk/B{n:03d}.txt','w').write(''.join(cur)); n+=1; cur=[]
for b in blocks:
    cur.append(b)
    if len(cur)>=25: flush()
flush()
print('tier',tier,'verses',len(keys),'packets up to',n-1)
