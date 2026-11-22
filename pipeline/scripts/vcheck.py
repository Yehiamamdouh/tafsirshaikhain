import json,re,sys,glob
S='/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
ws=lambda s: re.sub(r'\s+',' ',s).strip()
raw=open(sys.argv[1]).read(); raw=raw[raw.find('{'):raw.rfind('}')+1]
fixes=0
while True:
    try: D=json.loads(raw); break
    except json.JSONDecodeError as e:
        i=raw.rfind('"',0,e.pos)
        # walk back to the quote that wrongly closed the string
        raw=raw[:i]+'\\"'+raw[i+1:]; fixes+=1
        if fixes>200: raise
if fixes: print('repaired inner quotes:',fixes)
idx={}
for f in glob.glob(S+'/out/s*.json'):
    d=json.load(open(f))
    for r in d['recs']:
        b=d['books'][r['b']]; idx.setdefault((b['a'],b['w']),set()).add(ws(r['t']))
ok=bad=0
for su,x in D.items():
    for a,vs in x.get('summ',{}).items():
        for v,pts in vs.items():
            for w,t in pts:
                hit=any(ws(t) in s for s in idx.get((a,w),()))
                ok+=hit; bad+=not hit
                print('S' if hit else 'X',su,a,v,w,t[:90])
    for a,vs in x.get('nuq',{}).items():
        for v,its in vs.items():
            for it in its:
                hit=any(ws(it['t']) in s for s in idx.get((a,it['w']),()))
                ok+=hit; bad+=not hit
                print('N' if hit else 'X',su,a,v,it['who'],it['st'],it['t'][:70])
print('ok',ok,'bad',bad)
