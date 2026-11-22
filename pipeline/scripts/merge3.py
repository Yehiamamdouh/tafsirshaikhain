"""merge3.py FILE... : merge wave3 agent results (A/B delta or C fix) into batch files, verbatim+dedupe."""
import json,re,glob,sys,subprocess,os
S='/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
ws=lambda s: re.sub(r'\s+',' ',s).strip()
idx={}
for fn in glob.glob(S+'/out/s*.json'):
    d=json.load(open(fn))
    for r in d['recs']:
        b=d['books'][r['b']]; idx.setdefault((b['a'],b['w']),[]).append(ws(r['t']))
hit=lambda a,w,t: any(ws(t) in s for s in idx.get((a,w),()))
ST={'حكاه','أقرّه','ردّه','استشهد به','رجّح غيره'}
touched=set();st={'add':0,'dup':0,'bad':0,'fix':0,'toSumm':0}
B={}
def bt(su):
    if su not in B: B[su]=json.load(open(f'{S}/batch{su}.json'))
    return B[su]
for f in sys.argv[1:]:
    R=json.load(open(f))
    if 'fix' in R:
        for fx in R['fix']:
            su,a,v,i=fx['id'].split('|'); b=bt(su)
            try: it=b['nuq'][a][v][int(i)]
            except Exception: st['bad']+=1; continue
            if fx['st']=='كلام الإمام':
                it['_tosumm']=1; st['toSumm']+=1
            elif fx['st'] in ST:
                it['st']=fx['st']; st['fix']+=1
                if fx.get('rt') and hit(a,it['w'],fx['rt']): it['rt']=fx['rt']
            touched.add(su)
        continue
    for su,x in R.items():
        b=bt(su)
        for k in ('summ','nuq'):
            for a,vs in x.get(k,{}).items():
                for v,its in vs.items():
                    cur=b.setdefault(k,{}).setdefault(a,{}).setdefault(v,[])
                    have=[ws(e[1] if k=='summ' else e['t']) for e in cur]
                    for it in its:
                        w,t=(it if k=='summ' else (it['w'],it['t']))
                        if not hit(a,w,t): st['bad']+=1; continue
                        if any(ws(t) in h or h in ws(t) for h in have): st['dup']+=1; continue
                        if k=='nuq':
                            if it.get('st') not in ST: it['st']='حكاه'
                            if it.get('rt') and not hit(a,w,it['rt']): it.pop('rt')
                        cur.append(it if k=='nuq' else [w,t]); have.append(ws(t)); st['add']+=1; touched.add(su)
# move nuq marked as imam's own words into summ
for su,b in B.items():
    for a,m in b.get('nuq',{}).items():
        for v in list(m):
            keep=[]
            for it in m[v]:
                if it.pop('_tosumm',0): b.setdefault('summ',{}).setdefault(a,{}).setdefault(v,[]).append([it['w'],it['t']])
                else: keep.append(it)
            m[v]=keep
for su,b in B.items(): json.dump(b,open(f'{S}/batch{su}.json','w'),ensure_ascii=False,indent=1)
for su in sorted(touched,key=int): subprocess.run(['python3','-I',S+'/scripts/attach.py',su],cwd=S,stdout=subprocess.DEVNULL)
open(S+'/out/touched.txt','a').write(' '.join(sorted(touched,key=int))+'\n')
print(st,'surahs',len(touched))
