"""rext.py : widen record passages ("اقرأ الفقرة كاملة") with whole neighbouring book paragraphs, verbatim.
 - automatic: a record that starts or ends mid-sentence (previous paragraph / its own last paragraph ends with a comma
   or a function word) gets the neighbouring paragraph (1 each side, if not huge);
 - reviewer FULL decisions (audit2/out/*.txt, prev=N next=M) matched by audit2/recmap.json record identity."""
import json, os, re, glob, pickle, collections
SC = '/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
ws = lambda s: re.sub(r'\s+', ' ', s).strip()
FW = set('في من على إلى عن أن إن الذي التي الذين و ف ثم أو بل لا ما كما قال يقول وقال فقال قوله لأن لكن حتى إذا إلا هو هي ذلك وهو وهي بين مثل كل'.split())
def midend(t):   # a paragraph that clearly breaks off mid-sentence (ends with a comma or a function word)
    t = t.rstrip(); return bool(t) and (t.endswith('،') or t.endswith(',') or t.split()[-1] in FW)
FULL = collections.defaultdict(lambda: [0, 0])
for AD in ('audit2', 'audit3', 'audit4'):
  if not os.path.exists(f'{SC}/{AD}/recmap.json'): continue
  RM = json.load(open(f'{SC}/{AD}/recmap.json'))
  for f in glob.glob(f'{SC}/{AD}/out/*.txt'):
    for ln in open(f):
        p = [x.strip() for x in ln.split('|')]
        if len(p) >= 3 and p[1].upper() == 'FULL' and p[0] in RM:
            m1 = re.search(r'prev=(\d)', p[2]); m2 = re.search(r'next=(\d)', p[2]); k = RM[p[0]]
            key = (k['su'], k['w'], k['v'], k['p'], k['head'][:60])
            FULL[key][0] = max(FULL[key][0], int(m1[1]) if m1 else 0); FULL[key][1] = max(FULL[key][1], int(m2[1]) if m2 else 0)
_P = {}
def paras(w):
    if w not in _P:
        p = f'{SC}/out/cache/{w}.pkl'
        if not os.path.exists(p): _P[w] = None
        else:
            raw = pickle.load(open(p, 'rb'))['paras']; P = [ws(x['text']) for x in raw]; first = collections.defaultdict(list)
            for i, t in enumerate(P): first[t[:60]].append(i)
            _P[w] = (raw, P, first)
    return _P[w]
st = collections.Counter()
for su in range(1, 115):
    d = json.load(open(f'{SC}/site/s{su}.json')); pi = f'{SC}/site/s{su}i.json'
    inc = json.load(open(pi)) if os.path.exists(pi) else []; ch = False
    for r in d['recs'] + inc:
        w = d['books'][r['b']]['w']; pp = paras(w)
        if not pp: continue
        raw, P, first = pp; T = ws(r['t'])
        cs = [i for i in first.get(T[:60], []) if T.startswith(P[i][:200])]
        cs = [i for i in cs if raw[i]['vol'] == r['v']] or cs
        if not cs: st['nolocate'] += 1; continue
        p0 = cs[0]; p1 = p0
        while p1 < len(P) - 1 and p1 < p0 + 10 and T not in ' '.join(P[p0:p1 + 1]): p1 += 1
        if T not in ' '.join(P[p0:p1 + 1]): st['nospan'] += 1; continue
        pv = nx = 0
        if p0 > 0 and raw[p0 - 1]['vol'] == raw[p0]['vol'] and midend(P[p0 - 1]) and len(P[p0 - 1]) < 1500: pv = 1
        if p1 + 1 < len(P) and raw[p1 + 1]['vol'] == raw[p1]['vol'] and midend(P[p1]) and len(P[p1 + 1]) < 1500: nx = 1
        f = FULL.get((su, w, r['v'], r['p'], T[:60]))
        if f: pv = max(pv, f[0]); nx = max(nx, f[1]); st['full'] += 1
        pv = min(pv, p0); nx = min(nx, len(P) - 1 - p1)
        if not pv and not nx: continue
        nt = ' '.join(P[p0 - pv:p1 + nx + 1])
        if len(nt) > 12000: st['toolong'] += 1; continue
        r['t'] = nt; r['p'] = raw[p0 - pv]['p_start']; r['pe'] = raw[p1 + nx]['p_end']; ch = True
        st['ext'] += 1; st['prev'] += pv > 0; st['next'] += nx > 0
    if ch:
        json.dump(d, open(f'{SC}/site/s{su}.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
        if inc: json.dump(inc, open(pi, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('rext', dict(st))
