"""capply.py [--check] [spec files] : add collation headline excerpts (coll/cspec*.txt) to batchN.json (summ), idempotent.
Line format:  SU:V IT|IQ RECID[+K] «verbatim text»
  +K (1..3) = the text is in the K-th book paragraph after the record's paragraph; a joined record (record paragraph ..
  paragraph+K) is created in site/sNi.json so that "read the full paragraph" shows the verse and the comment together.
--check : validate only (verbatim, author, duplicates, length), print problems, change nothing."""
import json, os, re, sys, glob, pickle
SC = '/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
CHECK = '--check' in sys.argv
args = [a for a in sys.argv[1:] if not a.startswith('--')]
files = args or sorted(glob.glob(SC + '/coll/cspec*.txt'))
ws = lambda s: re.sub(r'\s+', ' ', s).strip()
_S, _P = {}, {}
def site(su):
    if su not in _S:
        d = json.load(open(f'{SC}/site/s{su}.json')); p = f'{SC}/site/s{su}i.json'
        inc = json.load(open(p)) if os.path.exists(p) else []
        _S[su] = [d, inc, False]
    return _S[su]
def paras(w):
    if w not in _P:
        raw = pickle.load(open(f'{SC}/out/cache/{w}.pkl', 'rb'))['paras']
        P = [ws(x['text']) for x in raw]; first = {}
        for i, t in enumerate(P): first.setdefault(t[:80], []).append(i)
        _P[w] = (raw, P, first)
    return _P[w]

def findrec(d, R, rid, a, t):
    """record id rid if it holds text t by author a; else (inc ids shift between rebuilds) any record of a holding t"""
    r = R.get(rid)
    if r and d['books'][r['b']]['a'] == a and t in ws(r['t']): return r
    c = [x for x in R.values() if d['books'][x['b']]['a'] == a and t in ws(x['t'])]
    c.sort(key=lambda x: (x.get('inc', 0), len(x['t'])))
    return c[0] if c else None
add = {}; bad = 0; seen = set(); n = 0
for f in files:
    for ln in open(f):
        ln = ln.strip()
        if not ln or ln.startswith('#'): continue
        mx = re.match(r'(\d+):(\d+)\s+(IT|IQ)\s+(\d+)/(\d+)\s+«(.+)»\s*$', ln)
        if mx:   # cross-surah: copy record SRCSU/RECID into this surah
            su, v, a, ssu, rid, t = int(mx[1]), int(mx[2]), mx[3], int(mx[4]), int(mx[5]), ws(mx[6]); n += 1
            ds, incs, _ = site(ssu); RS = {r['id']: r for r in ds['recs'] + incs}
            r0 = findrec(ds, RS, rid, a, t)
            if not r0: print('BADX', ln[:80]); bad += 1; continue
            rid = r0['id']
            if (su, v, a, t) in seen: print('DUP', ln[:70]); bad += 1; continue
            seen.add((su, v, a, t)); w = ds['books'][RS[rid]['b']]['w']
            add.setdefault(su, []).append((a, str(v), w, t, ('copy', ssu, rid))); continue
        m = re.match(r'(\d+):(\d+)\s+(IT|IQ)\s+(\d+)(?:\+(\d))?\s+«(.+)»\s*$', ln)
        if not m: print('PARSE', os.path.basename(f), ln[:70]); bad += 1; continue
        su, v, a, rid, k, t = int(m[1]), int(m[2]), m[3], int(m[4]), int(m[5] or 0), ws(m[6])
        n += 1
        d, inc, _ = site(su); R = {r['id']: r for r in d['recs'] + inc}
        if rid not in R: print('NOREC', ln[:70]); bad += 1; continue
        r = R[rid]; bk = d['books'][r['b']]; w = bk['w']
        if bk['a'] != a: print('AUTHOR', ln[:70]); bad += 1; continue
        if len(t) > 420 or len(t) < 15: print('LEN', len(t), ln[:70]); bad += 1
        if (su, v, a, t) in seen: print('DUP', ln[:70]); bad += 1; continue
        seen.add((su, v, a, t))
        T = ws(r['t'])
        if k == 0:
            if t not in T: print('NOTVERBATIM', ln[:80]); bad += 1; continue
            add.setdefault(su, []).append((a, str(v), w, t, None))
        else:
            raw, P, first = paras(w); cs = first.get(T[:80], [])
            cs2 = [i for i in cs if T.startswith(P[i])] or cs
            cs3 = [i for i in cs2 if raw[i]['vol'] == r['v'] and raw[i]['p_start'] == r['p']] or cs2
            p0 = cs3[0] if cs3 else None
            if p0 is None: print('NOPARA', ln[:70]); bad += 1; continue
            J = ' '.join(P[p0:p0 + k + 1])
            if t not in J: print('NOTVERBATIM+K', ln[:80]); bad += 1; continue
            if t in T: k = 0
            add.setdefault(su, []).append((a, str(v), w, t, None if k == 0 else (r['b'], p0, k)))
print('lines', n, 'bad', bad)
if CHECK or bad: sys.exit(1 if bad else 0)
aff = []; newrec = 0
for su, items in sorted(add.items()):
    d, inc, _ = site(su)
    bp = f'{SC}/batch{su}.json'
    B = json.load(open(bp)) if os.path.exists(bp) else {'summ': {}, 'nuq': {}}
    B.setdefault('summ', {}); B.setdefault('nuq', {})
    na = 0; nr = 0
    allrecs = d['recs'] + inc; nid = max([r['id'] for r in allrecs] + [-1]) + 1
    texts = {ws(r['t']) for r in allrecs}
    for a, v, w, t, J in items:
        if J and J[0] == 'copy':
            _, ssu, rid = J; ds, incs, _ = site(ssu); r0 = {r['id']: r for r in ds['recs'] + incs}[rid]
            if ws(r0['t']) not in texts:
                bw = ds['books'][r0['b']]
                bi = next((i for i, b in enumerate(d['books']) if b['w'] == bw['w']), None)
                if bi is None: d['books'].append(bw); bi = len(d['books']) - 1
                nr0 = dict(r0); nr0.update({'b': bi, 'ay': [int(v)], 'c': 0, 'inc': 1, 'id': nid}); inc.append(nr0)
                texts.add(ws(r0['t'])); nid += 1; nr += 1
        elif J:
            b, p0, k = J; raw, P, first = paras(w); jt = ' '.join(P[p0:p0 + k + 1])
            if jt not in texts:
                inc.append({'b': b, 'v': raw[p0]['vol'], 'p': raw[p0]['p_start'], 'pe': raw[p0 + k]['p_end'], 'h': raw[p0]['header'],
                            't': jt, 'ay': [int(v)], 'c': 0, 'inc': 1, 'id': nid, 'x': 1})
                texts.add(jt); nid += 1; nr += 1
        L = B['summ'].setdefault(a, {}).setdefault(v, [])
        if any(ws(x[1]) == t for x in L): continue
        L.append([w, t]); na += 1
    if nr:
        json.dump(inc, open(f'{SC}/site/s{su}i.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
        d['incCount'] = len(inc)
        json.dump(d, open(f'{SC}/site/s{su}.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    if na:
        for a in B['summ']: B['summ'][a] = dict(sorted(B['summ'][a].items(), key=lambda kv: int(kv[0])))
        json.dump(B, open(bp, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    if na or nr: aff.append(su)
    newrec += nr
    print('surah', su, 'added', na, 'newrec', nr)
print('NEWREC', newrec, 'AFFECTED', ' '.join(map(str, aff)))
