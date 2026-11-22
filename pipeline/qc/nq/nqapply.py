"""qc/nq/nqapply.py : apply the «تمام المعنى» review of the نقول (qc/nq/out/N*.txt, qc/nq/manual.txt last) to batchN.json.
Line: N#### | OK|FIX|DROP|HUMAN | fixes | reason ; fixes joined by ' ;; ' :
  TEXT «t» | WHO «x» | ST «x» | RT «t»     (TEXT/RT verbatim from the item's stored passage)
  TEXT@WORK#i «t» | RT@WORK#i «t»          (verbatim from cache paragraphs i..i+2: a new incidental record is made)
Entries are found by their current text (items.json snapshot). Runs after qapply in rebuild.sh."""
import json, re, glob, os, pickle, collections
SC = '/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
ws = lambda s: re.sub(r'\s+', ' ', s).strip()
I = json.load(open(SC + '/qc/nq/items.json'))
WA = json.load(open(SC + '/bp/wa.json'))
dec = {}
for f in sorted(glob.glob(SC + '/qc/nq/out/N*.txt')) + ([SC + '/qc/nq/manual.txt'] if os.path.exists(SC + '/qc/nq/manual.txt') else []):
    for ln in open(f):
        p = [x.strip() for x in ln.strip().split(' | ')]
        if len(p) >= 2 and p[0] in I: dec[p[0]] = p
B = {}; SITE = {}; _P = {}; META = {}
def batch(su):
    if su not in B: B[su] = json.load(open(f'{SC}/batch{su}.json'))
    return B[su]
def site(su):
    if su not in SITE:
        d = json.load(open(f'{SC}/site/s{su}.json')); p = f'{SC}/site/s{su}i.json'
        SITE[su] = (d, json.load(open(p)) if os.path.exists(p) else [])
    return SITE[su]
def paras(w):
    if w not in _P:
        D = pickle.load(open(f'{SC}/out/cache/{w}.pkl', 'rb')); _P[w] = D['paras']; META[w] = D.get('meta', {})
    return _P[w]
BOOKS = {}
for su in range(1, 115):
    for b in json.load(open(f'{SC}/site/s{su}.json'))['books']: BOOKS.setdefault((b['w'], b['a']), b)
def new_rec(su, a, w, i, t, v):
    """make an incidental record holding cache paragraphs around #i that contain t"""
    P = paras(w); T = [ws(x['text']) for x in P]
    j = next((j for j in range(i, min(len(P), i + 3)) if t in ' '.join(T[i:j + 1])), None)
    if j is None: return False
    d, inc = site(su); ba = WA.get(w, a)
    bi = next((n for n, b in enumerate(d['books']) if b['w'] == w and b['a'] == ba), None)
    if bi is None:
        if (w, ba) not in BOOKS: return False
        be = dict(BOOKS[(w, ba)]); be['id'] = len(d['books']); d['books'].append(be); bi = be['id']
    if any(r['b'] == bi and t in ws(r['t']) for r in d['recs'] + inc): return True
    i0, i1 = max(0, i - 1), j
    nid = max([x['id'] for x in d['recs'] + inc] + [-1]) + 1
    inc.append({'b': bi, 'v': P[i0]['vol'], 'p': P[i0]['p_start'], 'pe': P[i1]['p_end'], 'h': P[i].get('header', ''),
                't': ' '.join(T[i0:i1 + 1]), 'ay': [v], 'c': 0, 'inc': 1, 'id': nid, 'x': 1})
    d['incCount'] = len(inc); return True
st = collections.Counter(); miss = []; human = []
for k, p in dec.items():
    it = I[k]; su, v, a = it['su'], str(it['v']), it['a']
    if p[1] == 'OK': st['ok'] += 1; continue
    if p[1] == 'HUMAN': human.append(f"{k} {su}:{v} {a} | {p[2] if len(p) > 2 else ''}"); st['human'] += 1; continue
    L = batch(su).get('nuq', {}).get(a, {}).get(v, [])
    e = next((e for e in L if ws(e['t']) == it['t']), None)
    if e is None: miss.append(k + ' not found'); continue
    if p[1] == 'DROP': L.remove(e); st['drop'] += 1; continue
    ok = True
    for f in p[2].split(' ;; '):
        m = re.match(r'^(TEXT|WHO|ST|RT)(?:@(\w+)#(\d+))?\s*«(.*)»$', f.strip())
        if not m: miss.append(k + ' form'); ok = False; continue
        op, w, i, val = m[1], m[2], m[3], ws(m[4])
        if w and not new_rec(su, a, w, int(i), val, int(v)): miss.append(k + f' {op}@ not placed'); ok = False; continue
        if op == 'TEXT': e['t'] = val; (e.__setitem__('w', w) if w else None)
        elif op == 'WHO': e['who'] = val
        elif op == 'ST': e['st'] = val
        elif op == 'RT': e['rt'] = val; e['rw'] = w or e.get('w')
        st[op.lower()] += 1
    st['fix'] += ok
for su, (d, inc) in SITE.items():
    json.dump(d, open(f'{SC}/site/s{su}.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    json.dump(inc, open(f'{SC}/site/s{su}i.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
for su, b in B.items(): json.dump(b, open(f'{SC}/batch{su}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
open(SC + '/qc/nq/human.txt', 'w').write('\n'.join(human) + '\n')
print('nqapply', len(dec), dict(st), 'miss', len(miss))
for m in miss[:15]: print('MISS', m)
