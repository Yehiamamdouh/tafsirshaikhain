"""Collect both imams' passages on the verses of many surahs in one run.

usage: build_multi.py FIRST LAST OUTDIR
Each book is parsed and quotation-mapped once (cached in out/cache/), then every surah is built from the cache.
Same rules as build_surah.py: hand-made chapter map (secmap.json), header-named sections, scattered passages with
an incidental/substantive score, de-duplication across books of the same author ignoring quoted verses.
"""
import sys, os, re, json, glob, collections, pickle
sys.path.insert(0, os.path.dirname(__file__))
import parse, qmap
from parse import norm
import build as B0

FIRST, LAST, OUTDIR = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, '..', 'out', 'cache'); os.makedirs(CACHE, exist_ok=True)
SECMAP = json.load(open(os.path.join(HERE, '..', 'secmap.json'), encoding='utf-8'))
CORE = {2: [('MajmucFatawa', 10744, 10917)]}
EXPLAIN = ['معني', 'يعني', 'المراد', 'تفسير', 'فسر', 'قيل', 'دل علي', 'دلت', 'تضمن', 'وهذا', 'فان ', 'لان ', 'ولهذا', 'اي ']
FIQH_BOOKS = {'SharhCumdatFiqh', 'IkhtiyaratFiqhiyya', 'MusawwadaFiUsulFiqh', 'RafcYadaynFiSalat'}
Q = None

def load(path, work):
    """paragraphs + per-paragraph Counter{(surah, verse): n} + per-header Counter, cached."""
    global Q
    cf = os.path.join(CACHE, work + '.pkl')
    if os.path.exists(cf) and os.path.getmtime(cf) > os.path.getmtime(path):
        return pickle.load(open(cf, 'rb'))
    if Q is None: Q = qmap.Quran()
    m = parse.meta(path); paras = parse.paragraphs(path)
    per = [dict(qmap.map_paragraph(Q, p['text'])[0]) for p in paras]
    hmap = {}
    for p in paras:
        h = p['header']
        if h in hmap: continue
        if not h or not ('{' in h or 'قوله' in h or 'سوره' in norm(h) or 'آية' in h):
            hmap[h] = {}; continue
        hmap[h] = dict(qmap.map_paragraph(Q, h if '{' in h else '{' + h + '}')[0])
    d = {'meta': m, 'paras': paras, 'per': per, 'hmap': hmap}
    pickle.dump(d, open(cf, 'wb'))
    return d

BOOKS = []
paths = sorted(glob.glob(B0.IT + '/*/*-ara*')) + sorted(glob.glob(B0.IQ + '/*/*-ara*'))
for path in paths:
    if path.endswith('.yml') or path.endswith('.inProgress'): continue
    work = os.path.basename(path).split('.')[1]
    if work in B0.DROP or work in FIQH_BOOKS or (work == 'IghathatLahfan' and 'Shamela0007513' in path): continue
    author = 'IT' if '0728IbnTaymiyya' in path else 'IQ'
    d = load(path, work)
    BOOKS.append((path, work, author, d))
    print('loaded', work, file=sys.stderr)

def build(SUR):
    books, recs = [], []
    for path, work, author, d in BOOKS:
        paras, P, hmap = d['paras'], d['per'], d['hmap']
        per = [{v: c for (s, v), c in f.items() if s == SUR} for f in P]
        msecs = [(x, y, t) for w, x, y, t in SECMAP[author] if w == work]
        core_rng = [(a, b) for w, a, b in CORE.get(SUR, []) if w == work]
        hits = []; last_v, last_i = None, -99; sticky = None
        for i, p in enumerate(paras):
            cnt = per[i]; own = set(cnt)
            t = None
            for x, y, tt in msecs:
                if x <= i <= y: t = tt; break
            if t is not None:
                tg = [vs for s_, vs in t if s_ == SUR]
                if tg:
                    if tg[0] == '*':
                        if own: sticky = own
                        vs = own or sticky or {1}
                    else:
                        vs = set(tg[0]) | {v for v in own if any(abs(v - x) <= 3 for x in tg[0])}
                    hits.append((i, vs, 1))
                elif own:
                    hits.append((i, own, 0))
                continue
            hv = {v for (s, v) in hmap.get(p['header'], {}) if s == SUR}
            if any(a <= i <= b for a, b in core_rng):
                t0 = p['text'].strip()
                if t0.startswith(('فصل', 'وسئل', 'سئل', 'قال شيخ')): last_v = None
                vs = own
                if not vs and last_v and i - last_i <= 1: vs = set(last_v)
                if vs: hits.append((i, vs, 1)); last_v, last_i = vs, i
                continue
            if hv:
                hits.append((i, own | hv, 2)); continue
            if own:
                hits.append((i, own, 0))
        if not hits: continue
        m = d['meta']; bi = len(books)
        books.append({'id': bi, 'a': author, 'w': work, 't': B0.title_of(path, m), 'ed': B0.edition_of(m),
                      'sh': B0.shamela_id(path), 'pr': B0.PRIORITY[work]})
        for i, vs, core in hits:
            p = paras[i]; n = norm(p['text'])
            if len(n) < 25: continue
            r = {'b': bi, 'i': i, 'v': p['vol'], 'p': p['p_start'], 'pe': p['p_end'],
                 'h': re.sub(r'^(CHECK|AUTO)\s+', '', p['header']), 't': p['text'], 'ay': sorted(vs), 'c': core}
            if core != 1:
                r['cb'] = paras[i - 1]['text'] if i > 0 else ''
                r['ca'] = paras[i + 1]['text'] if i + 1 < len(paras) else ''
            if core == 0:
                cnt = per[i]
                rep = max(cnt.values())
                expl = sum(k in n for k in EXPLAIN)
                neigh = any(set(per[j]) & vs for j in (i - 1, i + 1) if 0 <= j < len(per))
                q_lead = re.search(r'(قوله|قال تعالى|قوله تعالى)\s*:?\s*\{', p['text'][:120]) is not None
                q_expl = re.search(r'(قوله|لقوله)\s*(تعالى)?\s*:?\s*\{[^{}]*\}\s*(\[[^\]]*\])?\s*:?\s*(أي|أى|يعني|معناه|يتضمن|فأخبر|فبين|فدل)', p['text']) is not None or 'تفسير لقوله' in p['text']
                score = (rep >= 2) * 2 + neigh * 2 + q_lead * 2 + q_expl * 3 + (expl >= 3) + (len(n) > 500)
                if score < 3: r['inc'] = 1
            recs.append(r)
    # de-duplicate across books of the same author, ignoring quoted verses
    by_author = collections.defaultdict(list)
    for k, r in enumerate(recs): by_author[books[r['b']]['a']].append(k)
    drop = set()
    for a, ks in by_author.items():
        ks.sort(key=lambda k: (books[recs[k]['b']]['pr'], recs[k]['c'] != 1))
        index = collections.defaultdict(set); kept = {}
        for k in ks:
            sh = B0.shingles(re.sub(r'\{[^{}]*\}', ' ', recs[k]['t']))
            if len(sh) < 3: kept[k] = sh; continue
            cands = collections.Counter()
            for s in sh:
                for o in index.get(s, ()): cands[o] += 1
            dup = None
            for o, c in cands.most_common(5):
                if recs[o]['b'] != recs[k]['b'] and c / min(len(sh), len(kept[o])) > 0.6: dup = o; break
            if dup is not None:
                drop.add(k)
                recs[dup].setdefault('also', []).append([recs[k]['b'], recs[k]['v'], recs[k]['p']])
                recs[dup]['ay'] = sorted(set(recs[dup]['ay']) | set(recs[k]['ay']))
                if not recs[k].get('inc'): recs[dup].pop('inc', None)
                continue
            kept[k] = sh
            for s in sh: index[s].add(k)
    recs = [r for k, r in enumerate(recs) if k not in drop]
    recs.sort(key=lambda r: (-r['c'] if r['c'] == 1 else 0, books[r['b']]['pr'], r['b'], r['i']))
    for n, r in enumerate(recs): r['id'] = n; del r['i']
    json.dump({'surah': SUR, 'books': books, 'recs': recs}, open(os.path.join(OUTDIR, 's%d.json' % SUR), 'w', encoding='utf-8'),
              ensure_ascii=False, separators=(',', ':'))
    c = collections.Counter(); cov = collections.defaultdict(set)
    for r in recs:
        a = books[r['b']]['a']
        c[(a, 'core' if r['c'] else ('inc' if r.get('inc') else 'keep'))] += 1
        if r['c'] or not r.get('inc'):
            for v in r['ay']: cov[a].add(v)
    print(SUR, 'kept', len(recs), dict(c), {a: len(v) for a, v in cov.items()}, file=sys.stderr)

for s in range(FIRST, LAST + 1):
    build(s)
