"""cshow.py IMAM SU [range] : collation candidates for imam IMAM (IT|IQ) in surah SU: verses where a printed compilation
(Daqaiq / Badai' / Hilal) contains a passage of this imam linked to the verse, but the site has nothing from this imam.
Shows each candidate record with a window around the place the verse is quoted (or the record start if not located)."""
import json, os, re, sys, pickle
SC = '/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
A_, su = sys.argv[1], int(sys.argv[2])
def _rng(a):
    out = set()
    for part in a.split(','):
        if '-' in part: x, y = part.split('-'); out.update(range(int(x), int(y) + 1))
        elif part: out.add(int(part))
    return out
ONLY = _rng(sys.argv[3]) if len(sys.argv) > 3 else None
ws = lambda s: re.sub(r'\s+', ' ', s).strip()
DIA = re.compile(r'[ؐ-ًؚ-ٰٟۖ-ۭـ]')
def norm_map(s):
    out, idx = [], []
    for i, ch in enumerate(s):
        if DIA.match(ch): continue
        c = {'أ': 'ا', 'إ': 'ا', 'آ': 'ا', 'ٱ': 'ا', 'ى': 'ي', 'ة': 'ه', 'ؤ': 'و', 'ئ': 'ي'}.get(ch, ch)
        out.append(c); idx.append(i)
    return ''.join(out), idx
def locate(T, vt):
    nT, mT = norm_map(T); nv, _ = norm_map(vt)
    words = [w for w in re.sub(r'[^ء-ي ]', ' ', nv).split() if len(w) > 1]
    if not words: return None
    lo = min(3, len(words))
    for L in range(len(words), lo - 1, -1):
        for i in range(0, len(words) - L + 1):
            seg = ' '.join(words[i:i + L]); j = nT.find(seg)
            if j >= 0: return (mT[j], mT[min(len(mT) - 1, j + len(seg) - 1)] + 1, L, len(words))
    return None
_P = {}
def paras(w):
    if w not in _P:
        pk = f'{SC}/out/cache/{w}.pkl'
        _P[w] = [ws(x['text']) for x in pickle.load(open(pk, 'rb'))['paras']] if os.path.exists(pk) else None
    return _P[w]
C = json.load(open(f'{SC}/coll/cand_{A_}.json'))
d = json.load(open(f'{SC}/site/s{su}.json')); p = f'{SC}/site/s{su}i.json'
inc = json.load(open(p)) if os.path.exists(p) else []
B = d['books']; R = {r['id']: r for r in d['recs'] + inc}
SRC = {'daqaiqT1': 'دقائق التفسير م1', 'daqaiqT2': 'دقائق التفسير م2', 'daqaiqT3': 'دقائق التفسير م3', 'daqaiq': 'دقائق التفسير م1', 'daqaiq3': 'دقائق التفسير م3', 'daqaiq_sh': 'دقائق التفسير (الشاملة)', 'qaysi': 'تفسير شيخ الإسلام (القيسي)', 'badaic5': 'بدائع التفسير ج1', 'badaic2': 'بدائع التفسير ج2', 'badaic3': 'بدائع التفسير ج3', 'hilal': 'تفسير ابن القيم (الهلال)'}
for v in range(1, len(d['verses']) + 1):
    k = f'{su}:{v}'
    if k not in C or (ONLY and v not in ONLY): continue
    vt = d['verses'][v - 1]
    print(f'\n######## {k} {A_} | {ws(DIA.sub("", vt))[:110]}')
    items = sorted(C[k].items(), key=lambda kv: kv[1]['nay'])
    for rid, e in items[:5]:
        r = R[int(rid)]; T = ws(r['t']); bk = B[r['b']]
        loc = locate(T, vt)
        src = ' + '.join(SRC[s] for s in e['src'])
        print(f"--- {A_} rec{rid} {bk['w']} {r['v']}/{r['p']}  (verses cited in record: {e['nay']}; in: {src})")
        if loc:
            s, e2, L, NW = loc
            print('   ' + T[max(0, s - 250):s] + ' ⟦' + T[s:e2][:100] + '⟧ ' + T[e2:e2 + 450])
        else:
            print('   (verse words not located) ' + T[:600])
        P = paras(bk['w']); p0 = e['i']
        if P and p0 is not None:
            for kk in (1, 2, 3):
                if p0 + kk < len(P) and P[p0 + kk] not in T: print(f'   +{kk}: ' + P[p0 + kk][:380])
    if len(items) > 5: print(f'   (+{len(items) - 5} more records with more verse citations)')
