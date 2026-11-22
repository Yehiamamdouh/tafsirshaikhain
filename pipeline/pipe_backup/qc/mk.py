"""qc/mk.py : packets for (A) blind second review of the book-paragraph excerpts now on the site, (V) verse-placement flags."""
import json, re, glob, pickle, os
SC='/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
ws=lambda s: re.sub(r'\s+',' ',s).strip()
DIA=re.compile('[ً-ْٰـۖ-ۭ]')
os.makedirs(SC+'/qc/pk',exist_ok=True)
PC={}
def P(w):
    if w not in PC: PC[w]=pickle.load(open(f'{SC}/out/cache/{w}.pkl','rb'))['paras']
    return PC[w]
V={su:json.load(open(f'{SC}/site/s{su}.json')) for su in range(1,115)}
# ---- A: excerpts from bp that are live
dec={}
for f in sorted(glob.glob(SC+'/bp/out/B*.txt'))+[SC+'/bp/manual.txt']:
    cur={}
    for ln in open(f):
        p=[x.strip() for x in ln.strip().split(' | ')]
        if len(p)>1 and re.match(r'^\d+:\d+$',p[0]): cur.setdefault(p[0],[]).append(p)
    dec.update(cur)
items=[]
for k,L in dec.items():
    su,v=map(int,k.split(':'))
    for p in L:
        if p[1] not in ('IT','IQ'): continue
        t=ws(re.match(r'^«(.*)»$',p[3])[1]); live=[e for e in V[su]['summ'].get(p[1],{}).get(str(v),[]) if ws(e['t'])==t]
        if not live: continue
        w,i=p[2].split('#'); i=int(i); Pw=P(w)
        ctx='\n'.join(f'[#{j}] '+ws(Pw[j]['text'])[:1800] for j in range(max(0,i-1),min(len(Pw),i+3)))
        items.append(f"\n### A{len(items)+1:03d} — {k} — {p[1]} — {w}#{i} ({Pw[i]['vol']}/{Pw[i]['p_start']})\nVERSE: {DIA.sub('',V[su]['verses'][v-1])}\nEXCERPT: «{t}»\nCONTEXT (paragraphs #{max(0,i-1)}..):\n{ctx}")
for n in range(0,len(items),30):
    open(f'{SC}/qc/pk/QA{n//30+1}.txt','w').write(''.join(items[n:n+30]))
print('A items',len(items))
# ---- V: verse-placement flags
F=json.load(open(SC+'/qc/vflags2.json')); vi=[]
for f in F:
    d=V[f['su']]
    try: inc=json.load(open(f'{SC}/site/s{f["su"]}i.json'))
    except Exception: inc=[]
    r=next((r for r in d['recs']+inc if f['t'][:60] in ws(r['t'])),None)
    B=d['books'][r['b']]
    vi.append(f"\n### V{len(vi)+1:03d} — {f['su']}:{f['v']} — {f['a']} — {f['kind']} — w={B['w']} ({r['v']}/{r['p']}) header: {ws(r.get('h',''))[:120]}\nVERSE: {DIA.sub('',d['verses'][f['v']-1])}\nSITE TEXT ({'excerpt' if f['kind']=='summ' else 'نقل'}): «{f['t']}»\nFULL STORED PASSAGE: {ws(r['t'])[:3500]}")
for n in range(0,len(vi),27):
    open(f'{SC}/qc/pk/QV{n//27+1}.txt','w').write(''.join(vi[n:n+27]))
print('V items',len(vi))
