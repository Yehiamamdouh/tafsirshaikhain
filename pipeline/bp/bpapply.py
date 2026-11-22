"""bp/bpapply.py : add the book-paragraph excerpts (bp/out/B*.txt; bp/manual.txt lines replace all lines of the same
verse) to batchN.json. Each excerpt gets a record: an existing site record of the same work/imam that contains it,
else a new incidental record (site/sNi.json) cut from the cache paragraphs around it. Runs after sapply in rebuild.sh.
Line: SU:V | IT|IQ | WORK#i | «text» | reason [CTX «…»]   or   SU:V | NONE | reason"""
import json, re, glob, os, pickle, collections
SC = '/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
ws = lambda s: re.sub(r'\s+', ' ', s).strip()
OKCTX = re.compile(r'^(وهذا اختيار الإمام|ينقل كلام .{2,40} ويقرّه)$')
WA = json.load(open(SC + '/bp/wa.json'))
# decisions per verse
dec = collections.OrderedDict()
files = sorted(glob.glob(SC + '/bp/out/B*.txt'))
man = SC + '/bp/manual.txt'
for f in files + ([man] if os.path.exists(man) else []):
    cur = {}
    for ln in open(f):
        p = [x.strip() for x in ln.strip().split(' | ')]
        if len(p) < 2 or not re.match(r'^\d+:\d+$', p[0]): continue
        cur.setdefault(p[0], []).append(p)
    for k, L in cur.items(): dec[k] = L          # a later file (manual) replaces the verse's lines
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
def book_entry(w, a):
    if (w, a) in BOOKS: return dict(BOOKS[(w, a)])
    paras(w); m = META[w]; g = lambda k: m.get(k, 'NODATA')
    ed = '، '.join(x for x in (g('040.EdEDITOR'), g('043.EdPUBLISHER'), g('041.EdNUMBER')) if x and x != 'NODATA')
    sh = re.sub(r'\D', '', g('000.SortField')); return {'a': a, 'w': w, 't': g('020.BookTITLE'), 'ed': ed, 'sh': int(sh) if sh else 0, 'pr': 5}
st = collections.Counter(); bad = []
for k, L in dec.items():
    su, v = map(int, k.split(':'))
    for p in L:
        if p[1] == 'NONE': st['none'] += 1; st['human'] += p[2].startswith('HUMAN') if len(p) > 2 else 0; continue
        a = p[1]; m = re.match(r'(\w+)#(\d+)$', p[2]); q = re.match(r'^«(.*)»$', p[3])
        if not (m and q) or WA.get(m[1]) != a: bad.append(k + ' format/imam'); continue
        w, i, t = m[1], int(m[2]), ws(q[1]); P = paras(w)
        T = [ws(x['text']) for x in P]
        j = next((j for j in range(i, min(len(P), i + 3)) if t in ' '.join(T[i:j + 1])), None)
        if j is None: bad.append(k + ' not verbatim'); continue
        cm = re.search(r'CTX\s*«([^»]+)»', ' | '.join(p[4:])); cx = ws(cm[1]) if cm else None
        if cx and not OKCTX.match(cx): bad.append(k + ' ctx'); cx = None
        d, inc = site(su)
        bi = next((n for n, b in enumerate(d['books']) if b['w'] == w and b['a'] == a), None)
        r = None
        if bi is not None:
            r = next((r for r in d['recs'] + inc if r['b'] == bi and t in ws(r['t'])), None)
        if r is None:
            if bi is None:
                be = book_entry(w, a); be['id'] = len(d['books']); d['books'].append(be); bi = be['id']; st['new-book'] += 1
            i0, i1 = i, j; hdr = P[i].get('header', '')
            while True:   # give the reader some context: grow within the same section up to ~2500 chars
                n = len(' '.join(T[i0:i1 + 1])); grew = False
                if n < 2500 and i0 > 0 and P[i0 - 1].get('header', '') == hdr and n + len(T[i0 - 1]) < 4000: i0 -= 1; grew = True
                n = len(' '.join(T[i0:i1 + 1]))
                if n < 2500 and i1 + 1 < len(P) and P[i1 + 1].get('header', '') == hdr and n + len(T[i1 + 1]) < 4000: i1 += 1; grew = True
                if not grew: break
            nid = max([x['id'] for x in d['recs'] + inc] + [-1]) + 1
            r = {'b': bi, 'v': P[i0]['vol'], 'p': P[i0]['p_start'], 'pe': P[i1]['p_end'], 'h': hdr, 't': ' '.join(T[i0:i1 + 1]),
                 'ay': [v], 'c': 0, 'inc': 1, 'id': nid, 'x': 1}
            inc.append(r); d['incCount'] = len(inc); st['new-rec'] += 1
        elif v not in r.get('ay', []): r.setdefault('ay', []).append(v)
        e = [w, t] + ([cx] if cx else [])
        batch(su).setdefault('summ', {}).setdefault(a, {}).setdefault(str(v), []).append(e); st['excerpt'] += 1
        st['ctx'] += bool(cx)
for su, (d, inc) in SITE.items():
    json.dump(d, open(f'{SC}/site/s{su}.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    json.dump(inc, open(f'{SC}/site/s{su}i.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
for su, b in B.items(): json.dump(b, open(f'{SC}/batch{su}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('bpapply verses', len(dec), dict(st), 'bad', len(bad))
for x in bad[:20]: print('BAD', x)
