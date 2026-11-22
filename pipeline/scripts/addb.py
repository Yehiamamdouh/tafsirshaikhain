"""addb.py DELTA.json : DELTA = {surah: {"summ":{a:{v:[[w,t]]}}, "nuq":{a:{v:[{...}]}}}}; merges into batch{surah}.json then attach."""
import json,sys,subprocess
S='/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
D=json.load(open(sys.argv[1]))
for n,dd in D.items():
    p=S+'/batch%s.json'%n
    try: b=json.load(open(p))
    except FileNotFoundError: b={"summ":{},"nuq":{}}
    for k in ('summ','nuq'):
        for a,vs in dd.get(k,{}).items():
            for v,items in vs.items():
                L=b.setdefault(k,{}).setdefault(a,{}).setdefault(v,[])
                for it in items:
                    if it not in L: L.append(it)
    json.dump(b,open(p,'w'),ensure_ascii=False,indent=1)
    subprocess.run(['python3','-I',S+'/scripts/attach.py',n],cwd=S)
