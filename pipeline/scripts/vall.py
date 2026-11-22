import json,re,glob,sys,collections
S='/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
ws=lambda s: re.sub(r'\s+',' ',s).strip()
def load(p):
    raw=open(p).read(); raw=raw.replace('\\[','[').replace('\\]',']')
    raw=raw[raw.find('{'):raw.rfind('}')+1]; f=0
    while True:
        try: return json.loads(raw),f
        except json.JSONDecodeError as e:
            i=raw.rfind('"',0,e.pos); raw=raw[:i]+'\\"'+raw[i+1:]; f+=1
            if f>300: raise
idx={}
for fn in glob.glob(S+'/out/s*.json'):
    d=json.load(open(fn))
    for r in d['recs']:
        b=d['books'][r['b']]; idx.setdefault((b['a'],b['w']),[]).append(ws(r['t']))
def hit(a,w,t):
    t=ws(t); return any(t in s for s in idx.get((a,w),()))
BAD=re.compile(r'^(قالوا|فإن قيل|احتجوا|زعموا|قال الجهمية|قالت)')
M=collections.defaultdict(lambda:{'summ':{},'nuq':{}}); stats=collections.Counter(); flags=[]
files=sys.argv[1:]
for p in files:
    D,f=load(p); stats['repairs']+=f
    bn=p.split('/')[-1][:-4]
    want={(str(x['surah']),x['imam'],str(x['ayah'])) for x in json.load(open(S+'/astra/%s.json'%bn))}
    for su,x in D.items():
        for k in ('summ','nuq'):
            for a,vs in x.get(k,{}).items():
                for v,its in vs.items():
                    for it in its:
                        w,t=(it if k=='summ' else (it['w'],it['t']))
                        if not hit(a,w,t): stats['notverbatim']+=1; flags.append(('NV',bn,su,a,v,t[:60])); continue
                        if k=='nuq' and it.get('rt') and not hit(a,w,it['rt']): it.pop('rt'); stats['rt_dropped']+=1
                        if (su,a,v) not in want: stats['offlist']+=1
                        if BAD.match(ws(t)): flags.append(('OPP',bn,su,a,v,t[:60])); stats['opp']+=1; continue
                        stats[k]+=1
                        M[su][k].setdefault(a,{}).setdefault(v,[]).append(it)
json.dump(M,open(S+'/out/d_chat.json','w'),ensure_ascii=False,indent=1)
print(dict(stats)); [print(*f) for f in flags]
