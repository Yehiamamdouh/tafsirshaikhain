"""spec/sapply.py : apply the specialist-triage FIX decisions (spec/out/S*.txt) to batchN.json (+ widen site records
from the book cache when an EXT text lies outside the stored passage). Runs after tapply in rebuild.sh.
Forms (detail field): [i] optional anywhere; EXT «t» | TRIM «t» | DROP | NUQ WHO ST [+ RT «t»] | CTX «t» | RT «t» | SRC (skipped)"""
import json, re, glob, os, pickle, collections
SC = '/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
S = SC + '/spec'
ws = lambda s: re.sub(r'\s+', ' ', s).strip()
ST = r'(أقرّه وزاد عليه|أقرّه وشرحه|أقرّه|حكاه|استشهد به|رجّح غيره|ردّه|رد وتكذيب|ضعّفه|رده)'
B = {}; SITE = {}; st = collections.Counter(); miss = []
def batch(su):
    if su not in B: B[su] = json.load(open(f'{SC}/batch{su}.json'))
    return B[su]
def site(su):
    if su not in SITE:
        d = json.load(open(f'{SC}/site/s{su}.json')); p = f'{SC}/site/s{su}i.json'
        inc = json.load(open(p)) if os.path.exists(p) else []
        SITE[su] = (d, inc, {r['id']: r for r in d['recs'] + inc}, {b['id']: b for b in d['books']})
    return SITE[su]
_P = {}
def paras(w):
    if w not in _P:
        p = f'{SC}/out/cache/{w}.pkl'
        _P[w] = None if not os.path.exists(p) else [ws(x['text']) for x in pickle.load(open(p, 'rb'))['paras']]
    return _P[w]
def rec_for(su, a, kind, t):
    """record of imam a in surah su whose text contains t (ws-normalised)."""
    d, inc, R, Bk = site(su)
    for r in d['recs'] + inc:
        if Bk[r['b']]['a'] == a and t in ws(r['t']): return r
    return None
def widen(su, a, w, t):
    """make some record of work w (imam a) contain t by replacing its text with the cache span that contains t
    (joined with the old text when adjacent). Returns True on success."""
    P = paras(w)
    if not P: return False
    d, inc, R, Bk = site(su)
    # cache span holding t
    i0 = next((i for i in range(len(P)) if t[:50] in P[i]), None)
    if i0 is None: i0 = next((i for i in range(len(P)) if len(P[i]) >= 80 and P[i][:80] in t), None)
    if i0 is None: return False
    i1 = i0
    while i1 < len(P) - 1 and i1 < i0 + 12 and t not in ' '.join(P[i0:i1 + 1]): i1 += 1
    if t not in ' '.join(P[i0:i1 + 1]): return False
    # candidate records of the same work, pick the one closest in the cache
    best = None
    for r in d['recs'] + inc:
        if Bk[r['b']]['w'] != w or Bk[r['b']]['a'] != a: continue
        T = ws(r['t']); j0 = next((j for j in range(max(0, i0 - 15), min(len(P), i1 + 16)) if (len(P[j]) >= 80 and P[j][:80] in T) or T[:80] in P[j]), None)
        if j0 is None: continue
        j1 = j0
        while j1 < len(P) - 1 and j1 < j0 + 30 and T not in ' '.join(P[j0:j1 + 1]): j1 += 1
        dist = max(0, i0 - j1, j0 - i1)
        if best is None or dist < best[0]: best = (dist, r, j0, j1)
    if best is None or best[0] > 6:
        return False
    _, r, j0, j1 = best; a0, a1 = min(i0, j0), max(i1, j1)
    nt = ' '.join(P[a0:a1 + 1])
    if len(nt) > 14000: return False
    r['t'] = nt; st['widened'] += 1; return True
def ensure(su, a, kind, t, rid=None):
    """return a record containing t (widening if needed)."""
    r = rec_for(su, a, kind, t)
    if r: return r
    d, inc, R, Bk = site(su)
    works = {Bk[x['b']]['w'] for x in d['recs'] + inc if Bk[x['b']]['a'] == a}
    if rid is not None and rid in R: works = [Bk[R[rid]['b']]['w']] + [x for x in works if x != Bk[R[rid]['b']]['w']]
    for w in works:
        if widen(su, a, w, t): return rec_for(su, a, kind, t)
    return None
def quoted(s): return [ws(x) for x in re.findall(r'«(.*?)»', s)]
rows = []
for f in sorted(glob.glob(S + '/out/S*.txt')):
    for ln in open(f):
        p = [x.strip() for x in ln.rstrip('\n').split(' | ')]
        if len(p) >= 3 and p[1] == 'FIX' and re.match(r'[sn]\d+:\d+:I[TQ]$', p[0]): rows.append((p[0], p[2], f))
for iid, det, f in rows:
    m = re.match(r'([sn])(\d+):(\d+):(IT|IQ)', iid); kind, su, v, a = m[1], int(m[2]), m[3], m[4]
    Bt = batch(su); key = 'summ' if kind == 's' else 'nuq'
    L = Bt.get(key, {}).get(a, {}).get(str(v))
    if L is None: miss.append((iid, 'no-list')); continue
    im = re.search(r'\[(\d)\]', det); idx = int(im[1]) if im else None
    op = re.search(r'\b(EXT|TRIM|DROP|NUQ|CTX|RT|SRC)\b', det)
    if not op: miss.append((iid, 'no-op')); continue
    op = op[1]; q = quoted(det)
    if idx is not None and idx >= len(L): miss.append((iid, f'idx {idx} > {len(L)}')); continue
    ent = lambda e: e[1] if kind == 's' else e['t']
    def pick():
        if idx is not None: return idx
        if len(L) == 1: return 0
        return None
    if op == 'SRC': miss.append((iid, 'SRC manual')); continue
    if op == 'DROP':
        i = pick()
        if i is None: miss.append((iid, 'DROP ambiguous')); continue
        del L[i]; st['drop'] += 1; continue
    if op == 'CTX':
        if not q: miss.append((iid, 'CTX no text')); continue
        i = pick() if pick() is not None else 0
        if kind == 's':
            if len(L[i]) > 2: L[i][2] = q[0]
            else: L[i].append(q[0])
        else: L[i]['cx'] = q[0]
        st['ctx'] += 1; continue
    if op == 'RT':
        if kind != 'n' or not q: miss.append((iid, 'RT form')); continue
        t = q[0]; i = pick() if pick() is not None else 0
        if not ensure(su, a, kind, t): miss.append((iid, 'RT not in book')); continue
        L[i]['rt'] = t; st['rt'] += 1; continue
    if op == 'NUQ':
        body = det.split('NUQ', 1)[1]; body = re.sub(r'\[\d\]', '', body)
        rt = None
        mrt = re.search(r'RT\s*«(.*?)»', body)
        if mrt: rt = ws(mrt[1]); body = body[:mrt.start()]
        body = re.sub(r'\(rt unchanged\)|\(بلا rt\)|\(.*?\)$', '', body.strip()).strip(' +;—-')
        ms = re.search(ST + r'\s*$', body.strip())
        if not ms:
            # «who» «st» form
            qq = quoted(body)
            if len(qq) >= 2: who, stn = qq[0], qq[1]
            else: miss.append((iid, 'NUQ parse: ' + body[:60])); continue
        else: stn = ms[1]; who = body[:ms.start()].strip(' «»')
        who = who.strip(' «»')
        if rt and not ensure(su, a, kind, rt): miss.append((iid, 'NUQ rt not in book')); rt = None
        if kind == 'n':
            i = pick() if pick() is not None else None
            targets = [i] if i is not None else range(len(L))
            for j in targets:
                L[j]['who'] = who; L[j]['st'] = stn
                if rt: L[j]['rt'] = rt
                elif '(بلا rt)' in det: L[j].pop('rt', None); L[j].pop('rw', None)
            st['nuq-upd'] += 1
        else:
            i = pick()
            if i is None: miss.append((iid, 'NUQ ambiguous idx')); continue
            e = L.pop(i); n = {'w': e[0], 'who': who, 'st': stn, 't': ws(e[1])}
            if rt: n['rt'] = rt
            Bt.setdefault('nuq', {}).setdefault(a, {}).setdefault(str(v), []).append(n); st['to-nuq'] += 1
        continue
    if op in ('EXT', 'TRIM'):
        if not q: miss.append((iid, op + ' no text')); continue
        t = q[0]
        i = pick()
        if i is None:  # find the entry whose text overlaps the proposal
            cand = [j for j, e in enumerate(L) if ws(ent(e)) in t or t in ws(ent(e)) or ws(ent(e))[:40] in t]
            i = cand[0] if cand else None
        rid = None if i is None or kind == 'n' else None
        r = ensure(su, a, kind, t, rid)
        if not r: miss.append((iid, op + ' not in book')); continue
        if i is None:
            if 'second sentence' in det or 'add' in det.lower(): (L.append([L[0][0], t]) if kind == 's' else L.append({**L[0], 't': t})); st['ext-add'] += 1
            else: miss.append((iid, op + ' no target'));
            continue
        wk = site(su)[3][r['b']]['w']
        if kind == 's': L[i][1] = t; L[i][0] = wk
        else: L[i]['t'] = t; L[i]['w'] = wk
        st[op.lower()] += 1
for su, d in B.items(): json.dump(d, open(f'{SC}/batch{su}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
for su, (d, inc, R, Bk) in SITE.items():
    json.dump(d, open(f'{SC}/site/s{su}.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    if inc: json.dump(inc, open(f'{SC}/site/s{su}i.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('sapply', dict(st), 'rows', len(rows), 'miss', len(miss))
for m in miss: print('MISS', m)
