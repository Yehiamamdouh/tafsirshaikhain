"""need.py: per surah, verses per imam that have explanatory material but no summary yet."""
import json,sys,re,collections
S='/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
sys.path.insert(0,S+'/scripts')
from parse import norm
Qc=json.load(open('/home/claude/quran/quran-json/data/tanzil/simple-clean.json'))
MK=['اي ','يعني','يتضمن','فاخبر','فدل','فبين','والمراد','معناه','تفسير','فسر','قال ابن عباس','قال مجاهد','اخبر']
def need(su):
    d=json.load(open(S+'/out/s%d.json'%su));B=d['books'];R=d['recs'];q=Qc[str(su)]
    site=json.load(open(S+'/site/s%d.json'%su)); summ=site.get('summ',{})
    out={}
    for a in ('IT','IQ'):
        have=set(int(v) for v in summ.get(a,{}))
        vs=collections.defaultdict(int)
        for r in R:
            if B[r['b']]['a']!=a or r.get('inc') or B[r['b']]['w']=='IjtimacJuyush': continue
            if len(r['ay'])>2: continue
            n=norm(r['t'])
            for v in r['ay']:
                if r['c']>0: vs[v]+=3; continue
                key=' '.join(norm(q[v-1]['text']).split()[:3]); i=n.find(key)
                if i<0: continue
                if sum(n[i:i+500].count(m) for m in MK)>=1: vs[v]+=1
        out[a]=sorted(v for v in vs if v not in have)
    return out
if __name__=='__main__':
    T=collections.Counter()
    for su in range(2,115):
        o=need(su)
        T['IT']+=len(o['IT']);T['IQ']+=len(o['IQ'])
        if len(sys.argv)>1: print(su,len(o['IT']),len(o['IQ']))
    print(T)
