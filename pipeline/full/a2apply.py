"""a2apply.py : apply full-pass decisions (audit2/out/*.txt) to batchN.json summ entries, matched by surah+imam+verse+text
(snapshot audit2/items.json). Order per item: TRIM -> CTX -> MOVE -> DROP/NUQ. Cross-surah MOVE copies the source record."""
import json, os, re, glob, collections
SC = '/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
ws = lambda s: re.sub(r'\s+', ' ', s).strip()
import sys
AD = sys.argv[1] if len(sys.argv) > 1 else 'audit2'
SNAP = {x['id']: x for x in json.load(open(f'{SC}/{AD}/items.json'))}
DEC = collections.defaultdict(list)
for f in sorted(glob.glob(f'{SC}/{AD}/out/*.txt')) + [f'{SC}/{AD}/manual.txt']:
    if not os.path.exists(f): continue
    for ln in open(f):
        p = [x.strip() for x in ln.rstrip('\n').split('|')]
        if len(p) >= 2 and re.match(r'^[sn]\d+:\d+:(IT|IQ):\d+$', p[0]): DEC[p[0]].append((p[1].upper(), p[2:]))
B, S = {}, {}
def batch(su):
    if su not in B:
        p = f'{SC}/batch{su}.json'; B[su] = json.load(open(p)) if os.path.exists(p) else {'summ': {}, 'nuq': {}}
        B[su].setdefault('summ', {}); B[su].setdefault('nuq', {})
    return B[su]
def site(su):
    if su not in S:
        d = json.load(open(f'{SC}/site/s{su}.json')); p = f'{SC}/site/s{su}i.json'
        S[su] = [d, json.load(open(p)) if os.path.exists(p) else [], False]
    return S[su]
def q1(a):
    m = re.match(r'^«(.*)»$', (a[0] if a else '').strip()); return ws(m.group(1)) if m else None
cnt = collections.Counter(); miss = []
for aid, L in DEC.items():
    acts = [x[0] for x in L]
    if set(acts) <= {'KEEP', 'FULL'}: continue
    s = SNAP.get(aid)
    if not s: miss.append(('nosnap', aid)); continue
    su, a, v, t = s['su'], s['a'], str(s['v']), ws(s['t'])
    if s['k'] == 'nuq':
        Bt = batch(su); lst = Bt['nuq'].get(a, {}).get(v, []); e = next((x for x in lst if ws(x['t']) == t), None)
        if e is None: miss.append(('nonuq', aid)); continue
        for act, g in L:
            if act == 'DROP': lst.remove(e); cnt['nDROP'] += 1; break
            if act == 'WHO' and g: e['who'] = g[0]; cnt['nWHO'] += 1
            if act == 'ST' and g: e['st'] = g[0]; cnt['nST'] += 1
            if act == 'TRIM' and q1(g): e['t'] = q1(g); cnt['nTRIM'] += 1
            if act == 'RT' and g:
                if g[0].strip() == '-': e.pop('rt', None); e.pop('rw', None); cnt['nRTdel'] += 1
                elif q1(g): e['rt'] = q1(g); e.pop('rw', None); cnt['nRT'] += 1
            if act == 'MOVE' and g:
                m = re.match(r'(\d+):(\d+)', g[0])
                if m and int(m[1]) == su:
                    lst.remove(e); L2 = Bt['nuq'].setdefault(a, {}).setdefault(m[2], [])
                    if not any(ws(x['t']) == ws(e['t']) for x in L2): L2.append(e)
                    cnt['nMOVE'] += 1; break
                elif m:   # cross-surah: copy a record holding quote (and rejoinder) into the target surah
                    su2, v2 = int(m[1]), m[2]; d, inc, _ = site(su)
                    src = next((r for r in d['recs'] + inc if d['books'][r['b']]['w'] == e['w'] and ws(e['t']) in ws(r['t'])), None)
                    if src is None: miss.append(('nuq-movesrc', aid)); continue
                    d2, inc2, _ = site(su2)
                    if not any(ws(e['t']) in ws(r['t']) and d2['books'][r['b']]['w'] == e['w'] for r in d2['recs'] + inc2):
                        bw = d['books'][src['b']]; bi = next((i for i, b in enumerate(d2['books']) if b['w'] == bw['w']), None)
                        if bi is None: d2['books'].append(bw); bi = len(d2['books']) - 1
                        nid = max([r['id'] for r in d2['recs'] + inc2] + [-1]) + 1
                        nr = dict(src); nr.update({'b': bi, 'ay': [int(v2)], 'c': 0, 'inc': 1, 'id': nid}); inc2.append(nr); S[su2][2] = True
                    lst.remove(e); L2 = batch(su2)['nuq'].setdefault(a, {}).setdefault(v2, [])
                    if not any(ws(x['t']) == ws(e['t']) for x in L2): L2.append(e)
                    cnt['nMOVEx'] += 1; break
            if act == 'SUMM':
                lst.remove(e); Bt['summ'].setdefault(a, {}).setdefault(v, []).append([e['w'], e['t']]); cnt['nSUMM'] += 1; break
        continue
    Bt = batch(su); lst = Bt['summ'].get(a, {}).get(v, [])
    e = next((x for x in lst if ws(x[1]) == t), None)
    if e is None: miss.append(('noentry', aid)); continue
    for act, g in L:
        if act == 'TRIM':
            nt = q1(g)
            if nt and not os.path.exists(f'{SC}/out/cache/{e[0]}.pkl'):   # book without paragraph cache: rext cannot widen the passage
                d0, inc0, _ = site(su)
                if not any(nt in ws(r['t']) for r in d0['recs'] + inc0 if d0['books'][r['b']]['w'] == e[0]):
                    miss.append(('trim-needs-full-nocache', aid)); continue
            if nt: e[1] = nt; cnt['TRIM'] += 1
        elif act == 'CTX':
            c = q1(g)
            if c:
                if len(e) > 2: e[2] = c
                else: e.append(c)
                cnt['CTX'] += 1
    for act, g in L:
        if act == 'MOVE':
            m = re.match(r'(\d+):(\d+)', g[0] if g else '')
            if not m: miss.append(('moveparse', aid)); continue
            su2, v2 = int(m[1]), m[2]; lst.remove(e)
            if su2 != su:   # copy a record holding the text into the target surah
                d, inc, _ = site(su); src = next((r for r in d['recs'] + inc if d['books'][r['b']]['w'] == e[0] and ws(e[1]) in ws(r['t'])), None)
                d2, inc2, _ = site(su2)
                if src is None: miss.append(('movesrc', aid)); continue
                if not any(ws(e[1]) in ws(r['t']) and d2['books'][r['b']]['w'] == e[0] for r in d2['recs'] + inc2):
                    bw = d['books'][src['b']]; bi = next((i for i, b in enumerate(d2['books']) if b['w'] == bw['w']), None)
                    if bi is None: d2['books'].append(bw); bi = len(d2['books']) - 1
                    nid = max([r['id'] for r in d2['recs'] + inc2] + [-1]) + 1
                    nr = dict(src); nr.update({'b': bi, 'ay': [int(v2)], 'c': 0, 'inc': 1, 'id': nid}); inc2.append(nr); S[su2][2] = True
            L2 = batch(su2)['summ'].setdefault(a, {}).setdefault(v2, [])
            if not any(ws(x[1]) == ws(e[1]) for x in L2): L2.append(e)
            cnt['MOVE'] += 1; break
    else:
        for act, g in L:
            if act == 'DROP': lst.remove(e); cnt['DROP'] += 1; break
            if act == 'NUQ' and len(g) >= 2:
                lst.remove(e); Bt['nuq'].setdefault(a, {}).setdefault(v, []).append({'w': e[0], 'who': g[0], 'st': g[1], 't': ws(e[1])}); cnt['NUQ'] += 1; break
for su, Bt in B.items():
    for k in ('summ', 'nuq'):
        for a in Bt[k]: Bt[k][a] = {vv: L for vv, L in sorted(Bt[k][a].items(), key=lambda kv: int(kv[0])) if L}
    json.dump(Bt, open(f'{SC}/batch{su}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
for su, (d, inc, ch) in S.items():
    if ch:
        json.dump(inc, open(f'{SC}/site/s{su}i.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
        d['incCount'] = len(inc); json.dump(d, open(f'{SC}/site/s{su}.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('a2apply', dict(cnt), 'miss', len(miss))
for m in miss[:15]: print('A2MISS', m)
