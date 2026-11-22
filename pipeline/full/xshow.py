"""xshow.py A B : show X items [A,B) (index into sorted X list) with record context for resolving."""
import json, sys, os, re, pickle, collections
SC = '/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
ws = lambda s: re.sub(r'\s+', ' ', s).strip()
I = json.load(open(SC + '/full/items.json'))
DEC = collections.defaultdict(list)
for ln in open(SC + '/full/dec.txt'):
    p = ln.split(None, 2)
    if len(p) >= 2 and p[1].isdigit(): DEC[int(p[1])].append((p[0], p[2].strip() if len(p) > 2 else ''))
XS = sorted(n for n, c in DEC.items() if any(x[0] == 'X' for x in c))
_S = {}
def surah(su):
    if su not in _S:
        d = json.load(open(f'{SC}/site/s{su}.json'))
        R = {r['id']: r for r in d['recs']}
        p = f'{SC}/site/s{su}i.json'
        if os.path.exists(p):
            for r in json.load(open(p)): R[r['id']] = r
        _S[su] = (d, R)
    return _S[su]
_P = {}
def paras(work):
    if work not in _P:
        if not os.path.exists(f'{SC}/out/cache/{work}.pkl'): _P[work] = ([], {}); return _P[work]
        d = pickle.load(open(f'{SC}/out/cache/{work}.pkl', 'rb'))
        P = [ws(p['text']) for p in d['paras']]
        _P[work] = (P, {t: i for i, t in enumerate(P)})
    return _P[work]
def locate(n):
    it = I[n]; d, R = surah(it['su'])
    sec = 'summ' if it['k'] == 'summ' else 'nuq'
    for x in d[sec].get(it['a'], {}).get(str(it['v']), []):
        if x['t'] == it['t']:
            return d, R.get(x['r'])
    return d, None
if __name__ == '__main__':
    a, b = int(sys.argv[1]), int(sys.argv[2])
    for n in XS[a:b]:
        it = I[n]; d, r = locate(n)
        codes = ' '.join(c + (' ' + t if t else '') for c, t in DEC[n])
        who = f" who={it['who']} st={it['st']}" if it['k'] == 'nuq' else ''
        print(f"\n##### {n} [{codes}] {it['k']} {it['a']} {it['su']}:{it['v']}{who} | {it['vt'][:70]}")
        if not r: print('  !! record not found'); continue
        bk = d['books'][r['b']]
        T = ws(r['t']); i = T.find(it['t'])
        pre, post = '', ''
        P, M = paras(bk['w'])
        pi = M.get(T)
        if i < 250 and pi is not None and pi > 0: pre = P[pi - 1][-400:] + ' ‖ '
        if len(T) - (i + len(it['t'])) < 250 and pi is not None and pi + 1 < len(P): post = ' ‖ ' + P[pi + 1][:350]
        if pi is None: print('  (para idx unknown)')
        print(f"  {bk['w']} {r['v']}/{r['p']} rec{r['id']}")
        print('  ' + pre + T[max(0, i - 700):i] + ' [[' + it['t'] + ']] ' + T[i + len(it['t']):i + len(it['t']) + 450] + post)
        for m in range(max(0, n - 6), min(len(I), n + 7)):
            o = I[m]
            if m != n and (o['su'], o['a'], o['v']) == (it['su'], it['a'], it['v']) and o['t'] in T:
                print(f"   ~ {m} {o['k']} [{' '.join(c for c,_ in DEC.get(m, []))}] {o['t'][:90]}")
