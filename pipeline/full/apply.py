"""apply.py [--dry] : apply review decisions (dec.txt + dec2.txt + xnew.json) to batchN.json, create joined records in site/sNi.json.
Order per item: D (delete) > N (summ->nuq) > W/S (who/stance) > X (new verbatim text) > M (move verse). Then auto-dedupe
(an entry whose text is contained in a changed entry of the same surah/kind/author/verse is dropped)."""
import json, sys, re, os, shutil, pickle, collections
SC = '/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
DRY = '--dry' in sys.argv
ws = lambda s: re.sub(r'\s+', ' ', s).strip()
I = json.load(open(SC + '/full/items.json'))
DEC = collections.defaultdict(list)
for f in ('dec.txt', 'dec2.txt', 'dec_audit.txt'):
    if not os.path.exists(SC + '/full/' + f): continue
    for ln in open(SC + '/full/' + f):
        p = ln.rstrip('\n').split(None, 2)
        if len(p) >= 2 and p[1].isdigit(): DEC[int(p[1])].append((p[0], p[2].strip() if len(p) > 2 else ''))
XN = {int(k): v for k, v in json.load(open(SC + '/full/xnew.json')).items()}
DEL, NN, WW, SS, MM, XT = set(), {}, {}, {}, {}, {}
for n, cs in DEC.items():
    for c, arg in cs:
        if c == 'D': DEL.add(n)
        elif c == 'N': who, st = arg.rsplit('=', 1); NN[n] = (who.strip(), st.strip())
        elif c == 'W': WW[n] = arg
        elif c == 'S': SS[n] = arg
        elif c == 'M': MM[n] = arg
for n, o in XN.items():
    if o.get('op') == 'D': DEL.add(n)
    elif o.get('op') == 'K': pass
    else: XT[n] = o
conf = [n for n in XT if n in DEL]
print('decisions: D', len(DEL), 'N', len(NN), 'W', len(WW), 'S', len(SS), 'M', len(MM), 'X-text', len(XT), 'conflicts D&X', conf)
for n in conf: del XT[n]

# backups (once)
BK = SC + '/backup_apply'
if not DRY and not os.path.exists(BK):
    os.makedirs(BK + '/site')
    for f in os.listdir(SC):
        if re.match(r'batch\d+\.json$', f): shutil.copy(SC + '/' + f, BK + '/' + f)
    for f in os.listdir(SC + '/site'):
        if re.match(r's\d+i?\.json$', f): shutil.copy(SC + '/site/' + f, BK + '/site/' + f)
    print('backup ->', BK)

def site(su):
    d = json.load(open(f'{SC}/site/s{su}.json'))
    p = f'{SC}/site/s{su}i.json'
    inc = json.load(open(p)) if os.path.exists(p) else []
    return d, inc

def batch_from_site(su):
    d, inc = site(su); R = {r['id']: r for r in d['recs'] + inc}; B = d['books']
    out = {'summ': {}, 'nuq': {}}
    for a, vs in d.get('summ', {}).items():
        for v, xs in vs.items():
            for x in xs: out['summ'].setdefault(a, {}).setdefault(v, []).append([B[R[x['r']]['b']]['w'], x['t']])
    for a, vs in d.get('nuq', {}).items():
        for v, xs in vs.items():
            for x in xs:
                o = {'w': B[R[x['r']]['b']]['w'], 'who': x['who'], 'st': x['st'], 't': x['t']}
                if x.get('rt'):
                    o['rt'] = x['rt']; rw = B[R[x['rr']]['b']]['w']
                    if rw != o['w']: o['rw'] = rw
                out['nuq'].setdefault(a, {}).setdefault(v, []).append(o)
    return out

_P = {}
def paras(work):
    if work not in _P:
        d = pickle.load(open(f'{SC}/out/cache/{work}.pkl', 'rb'))
        _P[work] = (d['paras'], [ws(p['text']) for p in d['paras']])
    return _P[work]

BYSU = collections.defaultdict(list)
for n, it in enumerate(I): BYSU[it['su']].append(n)
tot = collections.Counter(); problems = []
for su in range(1, 115):
    bp = f'{SC}/batch{su}.json'
    if os.path.exists(bp): B = json.load(open(bp))
    else:
        B = batch_from_site(su); tot['batch_from_site'] += 1
        if not B['summ'] and not B['nuq']: print('skip empty surah', su); continue
    B.setdefault('summ', {}); B.setdefault('nuq', {})
    # wrap every entry
    E = []
    for kind in ('summ', 'nuq'):
        for a, vs in B[kind].items():
            for v, xs in vs.items():
                for e in xs:
                    E.append({'kind': kind, 'a': a, 'v': v, 'e': e, 'n': None, 'chg': False})
    txt = lambda w: ws(w['e'][1] if w['kind'] == 'summ' else w['e']['t'])
    idx = collections.defaultdict(list)
    for w in E: idx[(w['kind'], w['a'], w['v'], txt(w))].append(w)
    for n in BYSU[su]:
        it = I[n]; key = (it['k'], it['a'], str(it['v']), ws(it['t']))
        cand = [w for w in idx.get(key, []) if w['n'] is None]
        if not cand:
            if n in DEL or n in XT or n in NN or n in WW or n in SS or n in MM: problems.append(('NOMATCH', n, key[:3], key[3][:50]))
            continue
        cand[0]['n'] = n
    out = []
    for w in E:
        n = w['n']
        if n is None: out.append(w); continue
        if n in DEL: tot['D'] += 1; continue
        if n in NN:
            assert w['kind'] == 'summ', n
            who, st = NN[n]; w['e'] = {'w': w['e'][0], 'who': who, 'st': st, 't': w['e'][1]}; w['kind'] = 'nuq'; w['chg'] = True; tot['N'] += 1
        if n in WW: assert w['kind'] == 'nuq', n; w['e']['who'] = WW[n]; tot['W'] += 1
        if n in SS: assert w['kind'] == 'nuq', n; w['e']['st'] = SS[n]; tot['S'] += 1
        if n in XT:
            t = XT[n]['t']
            if w['kind'] == 'summ': w['e'] = [w['e'][0], t]
            else: w['e']['t'] = t
            w['chg'] = True; tot['X'] += 1
        if n in MM:
            s2, v2 = MM[n].split(':'); assert int(s2) == su, (n, MM[n]); w['v'] = str(int(v2)); w['chg'] = True; tot['M'] += 1
        out.append(w)
    # auto-dedupe
    G = collections.defaultdict(list)
    for w in out: G[(w['kind'], w['a'], w['v'])].append(w)
    keep = []
    for g, ws_ in G.items():
        drop = set()
        for i, x in enumerate(ws_):
            tx = txt(x)
            for j, y in enumerate(ws_):
                if i == j or j in drop: continue
                ty = txt(y)
                if tx == ty and j < i: drop.add(i); break
                if tx != ty and tx in ty and y['chg']:
                    drop.add(i)
                    if '--show' in sys.argv: print('DEDUPE', su, x['v'], x['n'], 'in', y['n'], '|', tx[:70])
                    break
        for i, x in enumerate(ws_):
            if i in drop:
                tot['dedupe'] += 1
                if x['n'] is not None and x['n'] not in DEL: tot['dedupe_item'] += 1
            else: keep.append(x)
    # rebuild batch
    NB = {'summ': {}, 'nuq': {}}
    for w in keep: NB[w['kind']].setdefault(w['a'], {}).setdefault(w['v'], []).append(w['e'])
    for kind in NB:
        for a in NB[kind]: NB[kind][a] = dict(sorted(NB[kind][a].items(), key=lambda kv: int(kv[0])))
    # joined records
    d, inc = site(su); newrecs = []
    allrecs = d['recs'] + inc; nid = max([r['id'] for r in allrecs] + [-1]) + 1
    RID = {r['id']: r for r in allrecs}
    for n in BYSU[su]:
        o = XT.get(n)
        if not o or 'join' not in o or n in DEL: continue
        j = o['join']; raw, P = paras(j['w']); pi = j['pi']; t = o['t']
        lo, hi = max(0, pi - j['prev']), min(len(P) - 1, pi + j['next'])
        found = None
        for L in range(1, hi - lo + 2):
            for i in range(lo, hi - L + 2):
                if t in ' '.join(P[i:i + L]): found = (i, i + L - 1); break
            if found: break
        if not found: problems.append(('JOINFAIL', n)); continue
        i0, i1 = found; jt = ' '.join(P[i0:i1 + 1])
        if any(ws(r['t']) == jt for r in allrecs + newrecs): continue
        r0 = RID[o['rec']]
        nr = {'b': r0['b'], 'v': raw[i0]['vol'], 'p': raw[i0]['p_start'], 'pe': raw[i1]['p_end'], 'h': raw[i0]['header'],
              't': jt, 'ay': [I[n]['v']], 'c': 0, 'inc': 1, 'id': nid, 'x': 1}
        nid += 1; newrecs.append(nr); tot['newrec'] += 1
    if not DRY:
        json.dump(NB, open(bp, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
        if newrecs:
            inc += newrecs
            json.dump(inc, open(f'{SC}/site/s{su}i.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
            d['incCount'] = len(inc)
            json.dump(d, open(f'{SC}/site/s{su}.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print(dict(tot))
for p in problems: print('PROBLEM', p)
