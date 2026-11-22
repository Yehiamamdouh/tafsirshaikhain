# usage: python3 bp/chk.py OUT PACKET  -> validate output lines (format, verbatim, order, coverage)
import pickle,sys,re
SC='/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
ws=lambda s: re.sub(r'\s+',' ',s).strip()
out,pk=sys.argv[1],sys.argv[2]
ids=re.findall(r'^### (\d+:\d+) ',open(pk).read(),re.M)
PC={}
def P(w):
    if w not in PC: PC[w]=pickle.load(open(f'{SC}/out/cache/{w}.pkl','rb'))['paras']
    return PC[w]
OKCTX=re.compile(r'^(وهذا اختيار الإمام|ينقل كلام .{2,40} ويقرّه)$')
bad=0; seen=[]; n=0; cnt={}
for ln in open(out):
    ln=ln.strip()
    if not ln: continue
    p=[x.strip() for x in ln.split(' | ')]
    if p[0] not in ids: print('BAD id',ln[:80]); bad+=1; continue
    if not seen or seen[-1]!=p[0]: seen.append(p[0])
    if len(p)>=2 and p[1]=='NONE': n+=1; continue
    if len(p)<5 or p[1] not in ('IT','IQ'): print('BAD format',ln[:100]); bad+=1; continue
    m=re.match(r'(\w+)#(\d+)$',p[2])
    if not m: print('BAD ref',ln[:100]); bad+=1; continue
    w,i=m[1],int(m[2])
    try: Pw=P(w)
    except Exception: print('BAD work',w); bad+=1; continue
    q=re.match(r'^«(.*)»$',p[3])
    if not q: print('BAD quote marks',ln[:100]); bad+=1; continue
    t=ws(q[1]); T=' '.join(ws(Pw[j]['text']) for j in range(i,min(len(Pw),i+3)))
    Pi=ws(Pw[i]['text'])
    if t not in T or not (Pi.find(t[:30])>=0 or (len(Pi)<30 and t.startswith(Pi)) or T.find(t)<len(Pi)): print('BAD not verbatim / not starting in #%d'%i,p[0],t[:60]); bad+=1
    if not (15<=len(t)<=700): print('WARN length',len(t),p[0])
    c=re.search(r'CTX\s*«([^»]+)»',' | '.join(p[4:]))
    if c and not OKCTX.match(ws(c[1])): print('BAD CTX',p[0],c[1]); bad+=1
    k=(p[0],p[1]); cnt[k]=cnt.get(k,0)+1
    if cnt[k]>2: print('BAD >2 excerpts',k); bad+=1
miss=[x for x in ids if x not in seen]
order=[x for x in ids if x in seen]==seen
if miss: print('MISSING',len(miss),miss[:10]); bad+=len(miss)
if not order: print('BAD order'); bad+=1
print('verses',len(ids),'done',len(seen),'none',n,'excerpts',sum(cnt.values()),'bad',bad)
