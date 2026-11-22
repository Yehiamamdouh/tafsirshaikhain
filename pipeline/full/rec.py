import json,sys,os
SC='/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
I=json.load(open(SC+'/full/items.json'))
def recs(su):
    d=json.load(open(f'{SC}/site/s{su}.json'))
    R={r['id']:r for r in d['recs']}
    p=f'{SC}/site/s{su}i.json'
    if os.path.exists(p):
        e=json.load(open(p))
        for r in (e.get('recs',e) if isinstance(e,dict) else e):
            if isinstance(r,dict) and 'id' in r: R[r['id']]=r
    return d,R
for n in map(int,sys.argv[1:]):
    it=I[n]; d,R=recs(it['su'])
    sec='summ' if it['k']=='summ' else 'nuq'
    hit=None
    for x in d[sec].get(it['a'],{}).get(str(it['v']),[]):
        if x['t']==it['t']: hit=x
    r=R.get(hit.get('r')) if hit else None
    bk=[b for b in d['books'] if b['id']==(r or {}).get('b')]
    print('==',n,it['su'],it['v'],it['a'],'rec',hit and hit.get('r'),bk[0]['t'] if bk else '', (r or {}).get('p'))
    if r:
        t=r['t']; i=t.find(it['t'][:30]); print(t[max(0,i-900):i+len(it['t'])+400])
