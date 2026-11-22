import json,glob,sys,re
task,key=sys.argv[1],sys.argv[2]
src={}
for f in glob.glob(f'waveRpkg/R{task}_*.json'):
    for it in json.load(open(f))['items']: src[it['id']]=it
rows=[]
for f in sorted(glob.glob(f'res/R/R{task}_*.json')):
    rows+=json.load(open(f,encoding='utf-8-sig'))[key]
a,b=int(sys.argv[3]),int(sys.argv[4])
for n,x in enumerate(rows[a:b],a):
    s=src.get(x['id'],{})
    print(f"#{n} {x['id']} {s.get('ayah')} | {json.dumps({k:v for k,v in x.items() if k not in ('id','t')},ensure_ascii=False)[:220]}")
    print(f"   آية: {s.get('verse','')[:80]}")
    print(f"   T: {s.get('t','')[:260]}")
    if task=='V': print(f"   BEFORE: …{s.get('context_before','')[-220:]}")
    if x.get('t'): print(f"   NEW: {x['t'][:300]}")
print('rows',len(rows))
