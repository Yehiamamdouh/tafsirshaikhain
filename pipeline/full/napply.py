"""napply.py [files] : add quotation (nuq) entries from full/nspec*.txt to batchN.json, idempotent.
Line:  SU:V IT|IQ RECID «verbatim text» || WHO || STANCE
Cross-surah: SU:V IT|IQ SRCSU/RECID «...» || WHO || STANCE  -> record SRCSU/RECID is copied into surah SU (sNi.json)."""
import json, os, re, sys, glob
SC = '/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
ws = lambda s: re.sub(r'\s+', ' ', s).strip()
files = sys.argv[1:] or sorted(glob.glob(SC + '/full/nspec*.txt'))

def findrec(d, R, rid, a, t):
    """record id rid if it holds text t by author a; else (inc ids shift between rebuilds) any record of a holding t"""
    r = R.get(rid)
    if r and d['books'][r['b']]['a'] == a and t in ws(r['t']): return r
    c = [x for x in R.values() if d['books'][x['b']]['a'] == a and t in ws(x['t'])]
    c.sort(key=lambda x: (x.get('inc', 0), len(x['t'])))
    return c[0] if c else None
add = {}; bad = 0
for f in files:
    for ln in open(f):
        ln = ln.strip()
        if not ln or ln.startswith('#'): continue
        m = re.match(r'(\d+):(\d+)\s+(IT|IQ)\s+(?:(\d+)/)?(\d+)\s+«(.+)»\s*\|\|\s*(.+?)\s*\|\|\s*(.+?)\s*$', ln)
        if not m: print('PARSE', ln[:80]); bad += 1; continue
        su, v, a, ssu, rid, t, who, st = int(m[1]), m[2], m[3], int(m[4] or m[1]), int(m[5]), ws(m[6]), m[7], m[8]
        d = json.load(open(f'{SC}/site/s{su}.json')); p = f'{SC}/site/s{su}i.json'
        inc = json.load(open(p)) if os.path.exists(p) else []
        if ssu != su:   # copy the source record into this surah (once)
            ds = json.load(open(f'{SC}/site/s{ssu}.json')); ps = f'{SC}/site/s{ssu}i.json'
            incs = json.load(open(ps)) if os.path.exists(ps) else []
            RS = {r['id']: r for r in ds['recs'] + incs}
            r0 = findrec(ds, RS, rid, a, t)
            if not r0: print('BADX', ln[:80]); bad += 1; continue
            T0 = ws(r0['t']); ex = [r for r in d['recs'] + inc if ws(r['t']) == T0]
            if ex: rid = ex[0]['id']
            else:
                bw = ds['books'][r0['b']]; bi = next((i for i, b in enumerate(d['books']) if b['w'] == bw['w']), None)
                if bi is None: d['books'].append(bw); bi = len(d['books']) - 1
                nid = max([r['id'] for r in d['recs'] + inc] + [-1]) + 1
                nr0 = dict(r0); nr0.update({'b': bi, 'ay': [int(v)], 'c': 0, 'inc': 1, 'id': nid}); inc.append(nr0); rid = nid
                json.dump(inc, open(p, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
                d['incCount'] = len(inc); json.dump(d, open(f'{SC}/site/s{su}.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
        R = {r['id']: r for r in d['recs'] + inc}
        if not K:
            r1 = findrec(d, R, rid, a, t)
            if r1: rid = r1['id']
        if rid not in R or t not in ws(R[rid]['t']) or d['books'][R[rid]['b']]['a'] != a: print('BAD', ln[:80]); bad += 1; continue
        add.setdefault(su, []).append((a, v, d['books'][R[rid]['b']]['w'], t, who, st))
aff = []
for su, items in sorted(add.items()):
    bp = f'{SC}/batch{su}.json'
    B = json.load(open(bp)) if os.path.exists(bp) else {'summ': {}, 'nuq': {}}
    B.setdefault('summ', {}); B.setdefault('nuq', {}); n = 0
    for a, v, w, t, who, st in items:
        L = B['nuq'].setdefault(a, {}).setdefault(v, [])
        if any(ws(x['t']) == t for x in L): continue
        L.append({'w': w, 'who': who, 'st': st, 't': t}); n += 1
    if n:
        for a in B['nuq']: B['nuq'][a] = dict(sorted(B['nuq'][a].items(), key=lambda kv: int(kv[0])))
        json.dump(B, open(bp, 'w', encoding='utf-8'), ensure_ascii=False, indent=0); aff.append(su)
print('nspec bad', bad, 'AFFECTED', ' '.join(map(str, aff)))
