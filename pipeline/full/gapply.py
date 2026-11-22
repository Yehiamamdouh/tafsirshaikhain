"""gapply.py [spec files...] : add gap-fill headline excerpts to batchN.json (summ), idempotent; prints affected surahs."""
import json, os, re, sys, glob
SC = '/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
ws = lambda s: re.sub(r'\s+', ' ', s).strip()
files = sys.argv[1:] or sorted(glob.glob(SC + '/full/gspec*.txt'))
_S = {}
def site(su):
    if su not in _S:
        d = json.load(open(f'{SC}/site/s{su}.json')); p = f'{SC}/site/s{su}i.json'
        inc = json.load(open(p)) if os.path.exists(p) else []
        _S[su] = (d, {r['id']: r for r in d['recs'] + inc})
    return _S[su]
add = {}

def findrec(d, R, rid, a, t):
    """record id rid if it holds text t by author a; else (inc ids shift between rebuilds) any record of a holding t"""
    r = R.get(rid)
    if r and d['books'][r['b']]['a'] == a and t in ws(r['t']): return r
    c = [x for x in R.values() if d['books'][x['b']]['a'] == a and t in ws(x['t'])]
    c.sort(key=lambda x: (x.get('inc', 0), len(x['t'])))
    return c[0] if c else None
for f in files:
    for ln in open(f):
        ln = ln.strip()
        if not ln or ln.startswith('#'): continue
        m = re.match(r'(\d+):(\d+)\s+(IT|IQ)\s+(\d+)\s+«(.+)»\s*$', ln)
        if not m: print('PARSE', f, ln[:60]); continue
        su, v, a, rid, t = int(m[1]), int(m[2]), m[3], int(m[4]), ws(m[5])
        d, R = site(su); r = findrec(d, R, rid, a, t)
        if not r: print('BAD', ln[:90]); continue
        w = d['books'][r['b']]['w']
        add.setdefault(su, []).append((a, str(v), w, t))
aff = []
for su, items in sorted(add.items()):
    bp = f'{SC}/batch{su}.json'
    B = json.load(open(bp)) if os.path.exists(bp) else {'summ': {}, 'nuq': {}}
    B.setdefault('summ', {}); B.setdefault('nuq', {})
    n = 0
    for a, v, w, t in items:
        L = B['summ'].setdefault(a, {}).setdefault(v, [])
        if any(ws(x[1]) == t for x in L): continue
        L.append([w, t]); n += 1
    if n:
        for a in B['summ']: B['summ'][a] = dict(sorted(B['summ'][a].items(), key=lambda kv: int(kv[0])))
        json.dump(B, open(bp, 'w', encoding='utf-8'), ensure_ascii=False, indent=0); aff.append(su)
    print('surah', su, 'added', n)
print('AFFECTED', ' '.join(map(str, aff)))
