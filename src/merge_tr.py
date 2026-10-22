"""merge_tr.py RESULTS_DIR : merge agent translation results into pub/i18n and pub/st (with sanity checks)."""
import json,glob,os,re,sys
S='/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
def load(p):
    raw=open(p,encoding='utf-8').read(); raw=raw[raw.find('{'):raw.rfind('}')+1]
    return json.loads(raw)
ui=set(json.load(open(S+'/pub/ui_ar.json'))); st={}
for f in sorted(glob.glob(sys.argv[1]+'/*.json')):
    n=os.path.basename(f)[:-5]
    try: R=load(f)
    except Exception as e: print('BAD JSON',n,e); continue
    if n.startswith('U_'):
        lang=n[2:]; good={k:v for k,v in R.items() if k in ui and isinstance(v,str) and v.strip()}
        json.dump(good,open(f'{S}/pub/i18n/{lang}.json','w'),ensure_ascii=False); print(n,len(good),'/',len(ui))
    elif n.startswith('T_'):
        lang=n.split('_')[1]; B=json.load(open(f'{S}/wave_tr/{n}.json')); keys={it['k'] for it in B['items']}
        p=f'{S}/pub/st/{lang}.json'; cur=json.load(open(p)) if os.path.exists(p) else {}
        good={k:v for k,v in R.items() if k in keys and isinstance(v,str) and v.strip() and not re.search('[؀-ۿ]{20,}',v) or (k in keys and lang in ('ur','fa'))}
        cur.update(good); json.dump(cur,open(p,'w'),ensure_ascii=False); print(n,len(good),'/',len(keys))
