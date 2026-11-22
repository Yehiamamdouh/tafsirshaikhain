"""List sections of Majmu' al-Fatawa vols 14-17 with citation profile. Caches mapping in out/majsec.pkl"""
import sys, os, re, pickle, collections
sys.path.insert(0, os.path.dirname(__file__))
import qmap
S='/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
P=pickle.load(open(S+'/majmu.pkl','rb'))
cache=S+'/out/majmap.pkl'
if os.path.exists(cache): M=pickle.load(open(cache,'rb'))
else:
    Q=qmap.Quran(); M={}
    for i,p in enumerate(P):
        if 14<=p['vol']<=17: M[i]=qmap.map_paragraph(Q,p['text'])[0]
    pickle.dump(M,open(cache,'wb'))
OPEN=re.compile(r'^\s*(فصل|وسئل|سئل|قال شيخ الإسلام|وقال شيخ الإسلام|قال الشيخ|وقال الشيخ|وقال أيضا|قال أيضا|في قوله تعالى|عن قوله تعالى|في الكلام على قوله|قوله تعالى|بسم الله)')
secs=[]; cur=None
for i in sorted(M):
    t=P[i]['text'].strip()
    if cur is None or OPEN.match(t) or i!=cur[-1]+1: cur=[i]; secs.append(cur)
    else: cur.append(i)
# merge bare opener lines ("فصل:", "وقال شيخ الإسلام ...:") into next section
out=[]; pend=[]
for s in secs:
    if len(s)==1 and len(P[s[0]]['text'])<120: pend+=s; continue
    out.append(pend+s); pend=[]
pickle.dump(out,open(S+'/out/majsecs.pkl','wb'))
print(len(out))
