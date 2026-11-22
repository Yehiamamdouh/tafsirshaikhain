"""gshow.py SU [maxcand] : for every verse of surah SU that has no summ/nuq, show candidate records (recs+inc with v in ay)
with a window around the place the verse is quoted. Output for picking a short verbatim headline sentence."""
import json, os, re, sys, collections
SC = '/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
su = int(sys.argv[1]); MAXC = int(sys.argv[2]) if len(sys.argv) > 2 else 4
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
d = json.load(open(f'{SC}/site/s{su}.json')); p = f'{SC}/site/s{su}i.json'
inc = json.load(open(p)) if os.path.exists(p) else []
B = d['books']; RECS = d['recs'] + inc
covered = set()
for k in ('summ', 'nuq'):
    for a, vs in d.get(k, {}).items():
        for v in vs: covered.add(int(v))
A = collections.defaultdict(list)
for r in RECS:
    for v in r.get('ay', []): A[v].append(r)
def locate(T, vt):
    nT, mT = norm_map(T); nv, _ = norm_map(vt)
    words = [w for w in re.sub(r'[^\u0621-\u064A ]', ' ', nv).split() if len(w) > 1]
    if not words: return None
    lo = min(3, len(words))
    for L in range(len(words), lo - 1, -1):
        for i in range(0, len(words) - L + 1):
            seg = ' '.join(words[i:i + L])
            j = nT.find(seg)
            if j >= 0:
                return (mT[j], mT[min(len(mT) - 1, j + len(seg) - 1)] + 1, L, len(words))
    return None
EXPL = re.compile(r'^(أي|يعني|فأخبر|وأخبر|أخبر|فبين|بين|يدل|تدل|دليل|فدل|فهذا|وهذا|هذا|فإن|المراد|معناه|والمعنى|فيه|ففيه|هو|هي|فجعل|فذكر|وفي هذا|فهو|فهي)')
for v in range(1, len(d['verses']) + 1):
    if v in covered or v not in A or (ONLY and v not in ONLY): continue
    vt = d['verses'][v - 1]
    rs = A[v]
    print(f'\n######## {su}:{v} | {ws(DIA.sub("", vt))[:110]}   ({len(rs)} recs)')
    cands = []; seen = set()
    for r in rs:
        T = ws(r['t'])
        if T in seen: continue
        seen.add(T)
        loc = locate(T, vt)
        if not loc: continue
        s, e, L, NW = loc
        cb = T.find('}', e)
        if 0 <= cb - e < 400: e = cb + 1
        m = re.match(r'\s*(\[[^\]]{0,40}\]|\([^)]{0,30}\))?\s*[،,.]?\s*', T[e:]); e2 = e + (m.end() if m else 0)
        aft = T[e2:e2 + 330]; bef = T[max(0, s - 170):s]
        a = B[r['b']]['a']
        score = 40 * min(L, 6) + (80 if re.search(r'قوله', bef[-30:]) else 0) + (70 if EXPL.match(aft) else 0) + min(len(aft), 300) // 10 - 60 * aft[:200].count('{') - 30 * bef[-120:].count('{')
        cands.append((score, a, r, bef, T[s:e], aft))
    shown = 0
    for A_ in ('IT', 'IQ'):
        cs = sorted([c for c in cands if c[1] == A_], key=lambda c: -c[0])[:3]
        for score, a, r, bef, q, aft in cs:
            bk = B[r['b']]
            print(f"--- {a} rec{r['id']} {bk['w']} {r['v']}/{r['p']} sc{score}")
            print('   ' + bef + ' ⟦' + q[:90] + ('…' if len(q) > 90 else '') + '⟧ ' + aft)
            shown += 1
    if not shown: print('   (verse text not located in any record)')
