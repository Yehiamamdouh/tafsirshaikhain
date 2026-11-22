import json,glob,re,subprocess
S='/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
ws=lambda s: re.sub(r'\s+',' ',s).strip()
def src(task):
    d={}
    for f in glob.glob(f'{S}/waveRpkg/R{task}_*.json'):
        for it in json.load(open(f))['items']: d[it['id']]=it
    return d
def rows(task,key):
    r=[]
    for f in sorted(glob.glob(f'{S}/res/R/R{task}_*.json')): r+=json.load(open(f,encoding='utf-8-sig'))[key]
    return r
def dec(fn): return set(int(n) for l in open(f'{S}/res/{fn}') for n in l.split(':')[1].split())
B={};touched=set();st={'extend':0,'move':0,'drop':0,'nuq':0,'miss':0}
def bt(su):
    if su not in B: B[su]=json.load(open(f'{S}/batch{su}.json'))
    return B[su]
def find(su,a,v,t):
    import os
    if not os.path.exists(f'{S}/batch{su}.json'): return [],None
    lst=bt(su).get('summ',{}).get(a,{}).get(v,[])
    for i,e in enumerate(lst):
        if ws(e[1])==ws(t): return lst,i
    return lst,None
# K extend
sk=src('K'); rk=rows('K','extend'); sp=json.load(open(f'{S}/res/rk_split.json'))
for n in sp['ok']+[x for x in sp['after'] if x!=57]:
    x=rk[n]; su,a,v,_=x['id'].split('|'); lst,i=find(su,a,v,sk[x['id']]['t'])
    if i is None: st['miss']+=1; continue
    lst[i][1]=x['t']; st['extend']+=1; touched.add(su)
# W move_nuq
sw=src('W'); rw=rows('W','who')
for n in dec('rw_dec.txt'):
    x=rw[n]; su,a,v,_=x['id'].split('|'); lst,i=find(su,a,v,sw[x['id']]['t'])
    if i is None: st['miss']+=1; continue
    w,t=lst.pop(i); bt(su).setdefault('nuq',{}).setdefault(a,{}).setdefault(v,[]).append({'who':x['who'],'st':x.get('st','حكاه'),'w':w,'t':t})
    st['nuq']+=1; touched.add(su)
# V move
sv=src('V'); rv=rows('V','verse')
for n in dec('rv_dec.txt'):
    x=rv[n]; su,a,v,_=x['id'].split('|'); lst,i=find(su,a,v,sv[x['id']]['t'])
    if i is None: st['miss']+=1; continue
    e=lst.pop(i); touched.add(su)
    if x['verdict']=='move':
        s2,v2=x['to'].split(':')
        cur=bt(s2).setdefault('summ',{}).setdefault(a,{}).setdefault(v2,[])
        if not any(ws(c[1])==ws(e[1]) for c in cur): cur.append(e)
        touched.add(s2); st['move']+=1
    else: st['drop']+=1
for su,b in B.items():
    for a in b.get('summ',{}):
        for v in [k for k,l in b['summ'][a].items() if not l]: del b['summ'][a][v]
    json.dump(b,open(f'{S}/batch{su}.json','w'),ensure_ascii=False,indent=1)
for su in sorted(touched,key=int): subprocess.run(['python3','-I',S+'/scripts/attach.py',su],cwd=S,stdout=subprocess.DEVNULL)
print(st,'surahs',len(touched))
