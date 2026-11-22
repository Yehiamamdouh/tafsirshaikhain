import json,glob,sys,re
L=lambda f: json.load(open(f,encoding='utf-8-sig'))
qb={};src={};rs={}
for f in glob.glob('res/Q/QB_*.json'):
    for x in L(f)['fix']: qb[x['id']]=x
for f in glob.glob('waveQ/B/QB_*.json'):
    for it in L(f)['items']: src[it['id']]=it
for f in glob.glob('res/R/RS_*.json'):
    for x in L(f)['st']: rs[x['id']]=x
sp=json.load(open('res/stance_split.json'))
ids=sp['agree'][int(sys.argv[1]):int(sys.argv[2])]
for n,i in enumerate(ids,int(sys.argv[1])):
    s=src[i]; c=re.sub(r'\s+',' ',s['context']); t=s['t']; k=c.find(t[:40])
    a=c[max(0,k-150):k] if k>=0 else ''; b=c[k+len(t):k+len(t)+330] if k>=0 else c[:300]
    print(f"#{n} {i} | {s['who']} | {s['current_st']}→{qb[i]['st']} rt:{(qb[i].get('rt') or '')[:70]}")
    print(f"   …{a[-150:]} [[{t[:160]}]] {b}")
