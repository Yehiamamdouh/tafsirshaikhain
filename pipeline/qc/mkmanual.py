"""qc/mkmanual.py : turn the blind second review (qc/out/QA*.txt) into bp/manual.txt lines (whole-verse replacement).
A010 (7:4 first line) is left for the owner's decision."""
import re, glob
SC='/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
ws=lambda s: re.sub(r'\s+',' ',s).strip()
hdr={}
for f in glob.glob(SC+'/qc/pk/QA*.txt'):
    for m in re.finditer(r'^### (A\d+) — (\d+:\d+) — (IT|IQ) — (\w+#\d+) .*\nVERSE: .*\nEXCERPT: «(.*)»$',open(f).read(),re.M):
        hdr[m[1]]=(m[2],m[3],m[4],ws(m[5]))
cur={}
for f in sorted(glob.glob(SC+'/bp/out/B*.txt'))+[SC+'/bp/manual.txt']:
    c={}
    for ln in open(f):
        p=[x.strip() for x in ln.strip().split(' | ')]
        if len(p)>1 and re.match(r'^\d+:\d+$',p[0]): c.setdefault(p[0],[]).append(p)
    cur.update(c)
SKIP={'A010'}; changes={}
for f in sorted(glob.glob(SC+'/qc/out/QA*.txt')):
    for ln in open(f):
        p=[x.strip() for x in ln.strip().split(' | ')]
        if not p[0] in hdr or p[1]=='OK' or p[0] in SKIP: continue
        k,a,ref,t=hdr[p[0]]
        if p[1]=='TRIM': new=ws(re.match(r'^«(.*)»$',p[2])[1])
        elif p[1]=='DROP':
            m=re.search(r'extend the span to «(.*)»',' | '.join(p[2:]))
            new=ws(m[1]) if m else None
        changes.setdefault(k,[]).append((a,ref,t,new,p[0]+' '+p[1]))
out=[]
for k,ch in changes.items():
    L=[]
    for p in cur[k]:
        if p[1] not in ('IT','IQ'): continue
        t=ws(re.match(r'^«(.*)»$',p[3])[1]); c=next((c for c in ch if c[1]==p[2] and c[2]==t),None)
        if c is None: L.append(' | '.join(p)); continue
        if c[3]: L.append(f'{k} | {p[1]} | {p[2]} | «{c[3]}» | second review {c[4]}')
    out+= L if L else [f'{k} | NONE | second review: '+'; '.join(c[4] for c in ch)]
open(SC+'/bp/manual.txt','a').write('\n'.join(out)+'\n'); print('\n'.join(x[:160] for x in out))
