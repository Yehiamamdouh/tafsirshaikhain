import json,re,glob
S='/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
D=re.compile('[ً-ْٰـۖ-ۭ]')
def norm(s):
    s=D.sub('',s); s=re.sub('[إأآٱ]','ا',s); s=s.replace('ى','ي').replace('ة','ه').replace('ؤ','و').replace('ئ','ي')
    return re.sub('[^ء-ي ]',' ',s)
def words(s): return [w for w in norm(s).split() if w]
ws=lambda s: re.sub(r'\s+',' ',s).strip()
def load(n):
    d=json.load(open(f'{S}/site/s{n}.json'))
    try: inc=json.load(open(f'{S}/site/s{n}i.json'))
    except: inc=[]
    R={r['id']:r for r in d['recs']+inc}
    return d,R
def ctx(R,it,before=500,after=500):
    r=R.get(it['r']); 
    if not r: return '',''
    t=ws(r['t']); k=t.find(ws(it['t']))
    if k<0: return t[:before+after],''
    return t[max(0,k-before):k], t[k+len(ws(it['t'])):k+len(ws(it['t']))+after]
