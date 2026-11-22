"""Flag summary excerpts that may be someone else's words quoted by the imam."""
import json,sys,re,glob
S='/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
MK=re.compile(r'(قالوا|قال القدري|قال الجبري|قال السني|المعترض|هذا لفظه|انتهى|إلى أن قال|قال أبو|قال ابن|قال الإمام|قال القاضي|وقال بعض|قال بعض|قال صاحب|قال الشيخ|قال شيخنا|قال المصنف|ذكر الإمام|وحكى|فإن قيل|قيل:)')
ws=lambda s: re.sub(r'\s+',' ',s)
for n in [int(x) for x in sys.argv[1:]]:
    d=json.load(open(S+'/site/s%d.json'%n)); R={r['id']:r for r in d['recs']}
    try:
        for r in json.load(open(S+'/site/s%di.json'%n)): R.setdefault(r['id'],r)
    except Exception: pass
    for a,vs in d.get('summ',{}).items():
        for v,pts in vs.items():
            for p in pts:
                t=ws(p.get('ft') or R[p['r']]['t']); i=t.find(p['t'])
                pre=t[max(0,i-350):i]; after=t[i+len(p['t']):i+len(p['t'])+120]
                m=[x for x in MK.findall(pre)]
                if m or 'هذا لفظه' in after or 'انتهى' in after:
                    print('S%d %s v%s | %s | PRE:...%s'%(n,a,v,p['t'][:60],pre[-160:]))
