"""Append Tafsir Ayat Ashkalat (Shamela 496, al-Khalifa ed.) records to out/s*.json; only text not already in the IT corpus."""
import sys,os,re,json,collections,csv,numpy as np
S='/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
sys.path.insert(0,S+'/scripts')
import qmap
from parse import norm
from shingle import words,grams
W='TafsirAyatAshkalat'
Q=qmap.Quran()
A=np.load(S+'/books/IT_grams.npy')
def known(t):
    g=np.array(grams(words(t)),dtype=np.uint32)
    if len(g)==0: return 1.0
    i=np.searchsorted(A,g);i[i>=len(A)]=0;return float((A[i]==g).mean())
pages=json.load(open(S+'/books/ashkalat_pages.json'))
# TOC: page id -> heading
toc=[]
B='/mnt/user-data/uploads/shaikhan/496/496.bok'
import subprocess
rows=list(csv.reader(subprocess.run(['mdb-export',B,'t17'],capture_output=True,text=True).stdout.splitlines()))[1:]
for r in rows: toc.append((int(r[0]),r[1]))
toc.sort()
def heading(pid):
    h=''
    for i,t in toc:
        if i<=pid: h=t
    return h
hv_cache={}
def hverses(h):
    if h not in hv_cache: hv_cache[h]={k for k in qmap.map_paragraph(Q,h)[0]} if '{' in h else set()
    return hv_cache[h]
paras=[]
for pid,part,page,t in pages:
    t=t.replace('\\n','\n')
    for para in re.split(r'\n+',t):
        if len(norm(para))<40: continue
        paras.append((pid,part,page,para.strip()))
by=collections.defaultdict(list); stats=collections.Counter()
for k,(pid,part,page,para) in enumerate(paras):
    if known(para)>=0.5: stats['known']+=1; continue
    own=dict(qmap.map_paragraph(Q,para)[0]); h=heading(pid); hv=hverses(h)
    vs=collections.defaultdict(set)
    for (s,v) in own: vs[s].add(v)
    for (s,v) in hv: vs[s].add(v)
    if not vs: stats['noverse']+=1; continue
    for s,v in vs.items():
        core=1 if any(x[0]==s for x in hv) else 0
        by[s].append({'v':part or 1,'p':page,'pe':page,'h':h,'t':para,'ay':sorted(v),'c':core})
    stats['new']+=1
for s,rs in by.items():
    p=f'{S}/out/s{s}.json'; d=json.load(open(p))
    if any(b['w']==W for b in d['books']): continue
    bi=len(d['books'])
    d['books'].append({'id':bi,'a':'IT','w':W,'t':'تفسير آيات أشكلت على كثير من العلماء','ed':'تحقيق عبد العزيز الخليفة، مكتبة الرشد، الرياض 1417هـ','sh':None,'pr':2})
    nid=max(r['id'] for r in d['recs'])+1
    for r in rs:
        r['b']=bi; r['id']=nid; nid+=1
        if len(r['ay'])>6: r['inc']=1
        d['recs'].append(r)
    json.dump(d,open(p,'w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
print(dict(stats),'surahs',len(by),'records',sum(len(v) for v in by.values()))
json.dump(sorted(by),open(S+'/books/ashkalat_surahs.json','w'))
