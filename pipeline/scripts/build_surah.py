"""Collect both imams' passages on the verses of one surah (generic, quotation-based).

usage: build_surah.py SURAH OUT.json
"""
import sys, os, re, json, glob, collections
sys.path.insert(0, os.path.dirname(__file__))
import parse, qmap
from parse import norm
import build as B0   # reuse metadata helpers (title_of, edition_of, shamela_id, PRIORITY, DROP, shingles)

SUR = int(sys.argv[1]); OUT = sys.argv[2]
Q = qmap.Quran()
NV = len(Q.starts[SUR])
SNAME = Q.names[SUR]

# Chapters each imam devoted to this surah: (work, first paragraph, last paragraph)
CORE = {
    2: [('MajmucFatawa', 10744, 10919)],
}
EXPLAIN = ['معني', 'يعني', 'المراد', 'تفسير', 'فسر', 'قيل', 'دل علي', 'دلت', 'تضمن', 'وهذا', 'فان ', 'لان ', 'ولهذا', 'اي ']
SECMAP = json.load(open(os.path.join(os.path.dirname(__file__), '..', 'secmap.json'), encoding='utf-8'))
FIQH_BOOKS = {'SharhCumdatFiqh', 'IkhtiyaratFiqhiyya', 'MusawwadaFiUsulFiqh', 'RafcYadaynFiSalat'}

def header_verses(h):
    if not h or not ('{' in h or 'قوله' in h or 'سوره' in norm(h) or 'آية' in h):
        return set(), False
    f, _ = qmap.map_paragraph(Q, h if '{' in h else '{' + h + '}')
    vs = {v for (s, v) in f if s == SUR}
    whole = ('سوره ' + letters_name()) in norm(h)
    return vs, whole

def letters_name():
    return norm(SNAME)

def main():
    books, recs = [], []
    paths = sorted(glob.glob(B0.IT + '/*/*-ara*')) + sorted(glob.glob(B0.IQ + '/*/*-ara*'))
    for path in paths:
        if path.endswith('.yml') or path.endswith('.inProgress'):
            continue
        work = os.path.basename(path).split('.')[1]
        if work in B0.DROP or work in FIQH_BOOKS or (work == 'IghathatLahfan' and 'Shamela0007513' in path):
            continue
        author = 'IT' if '0728IbnTaymiyya' in path else 'IQ'
        m = parse.meta(path)
        paras = parse.paragraphs(path)
        core_rng = [(a, b) for w, a, b in CORE.get(SUR, []) if w == work]
        per = []          # (verses set, count map) per paragraph
        for p in paras:
            f, _ = qmap.map_paragraph(Q, p['text'])
            cnt = {v: c for (s, v), c in f.items() if s == SUR}
            per.append(cnt)
        # chapters devoted to a verse, from the hand-made map (secmap.json)
        msecs = [(x, y, t) for w, x, y, t in SECMAP[author] if w == work]
        def mapped(i):
            for x, y, t in msecs:
                if x <= i <= y:
                    return t
            return None
        # header-named sections
        hcache = {}
        hits = []
        last_v, last_i = None, -99
        for i, p in enumerate(paras):
            cnt = per[i]
            t = mapped(i)
            if t is not None:
                tg = [set(vs) for s_, vs in t if s_ == SUR]
                own = set(cnt)
                if tg:
                    near = {v for v in own if any(abs(v - x) <= 3 for x in tg[0])}
                    hits.append((i, tg[0] | near, 1))
                elif own:
                    hits.append((i, own, 0))      # another verse's chapter: an ordinary passing passage here
                continue
            in_core = any(a <= i <= b for a, b in core_rng)
            if p['header'] not in hcache:
                hcache[p['header']] = header_verses(p['header'])
            hv, whole = hcache[p['header']]
            vs = set(cnt)
            if in_core:
                t0 = p['text'].strip()
                if t0.startswith('فصل') or t0.startswith('وسئل') or t0.startswith('سئل') or t0.startswith('قال شيخ'):
                    last_v = None             # a new section starts; do not carry the previous verse over
                if not vs and last_v and i - last_i <= 1:
                    vs = set(last_v)          # continuing the discussion of the previous verse
                if vs:
                    hits.append((i, vs, 1)); last_v, last_i = vs, i
                continue
            if hv:
                hits.append((i, vs | hv, 2)); continue
            if vs:
                hits.append((i, vs, 0))
        if not hits:
            continue
        bi = len(books)
        books.append({'id': bi, 'a': author, 'w': work, 't': B0.title_of(path, m), 'ed': B0.edition_of(m),
                      'sh': B0.shamela_id(path), 'pr': B0.PRIORITY[work]})
        for i, vs, core in hits:
            p = paras[i]
            n = norm(p['text'])
            if len(n) < 25:
                continue
            r = {'b': bi, 'i': i, 'v': p['vol'], 'p': p['p_start'], 'pe': p['p_end'],
                 'h': re.sub(r'^(CHECK|AUTO)\s+', '', p['header']), 't': p['text'], 'ay': sorted(vs), 'c': core}
            if core != 1:
                r['cb'] = paras[i - 1]['text'] if i > 0 else ''
                r['ca'] = paras[i + 1]['text'] if i + 1 < len(paras) else ''
            if core == 0:
                # passing mention or real discussion?
                cnt = per[i]
                rep = max(cnt.values())
                expl = sum(k in n for k in EXPLAIN)
                neigh = any(set(per[j]) & vs for j in (i - 1, i + 1) if 0 <= j < len(per))
                q_lead = re.search(r'(قوله|قال تعالى|قوله تعالى)\s*:?\s*\{', p['text'][:120]) is not None
                q_expl = re.search(r'(قوله|لقوله)\s*(تعالى)?\s*:?\s*\{[^{}]*\}\s*(\[[^\]]*\])?\s*:?\s*(أي|أى|يعني|معناه|يتضمن|فأخبر|فبين|فدل)', p['text']) is not None or 'تفسير لقوله' in p['text']
                score = (rep >= 2) * 2 + neigh * 2 + q_lead * 2 + q_expl * 3 + (expl >= 3) + (len(n) > 500)
                if score < 3:
                    r['inc'] = 1
            recs.append(r)
        print(f"{len(hits):5d} {author} {work}", file=sys.stderr)

    # de-duplicate across books of the same author (same rule as the Fatiha build)
    by_author = collections.defaultdict(list)
    for k, r in enumerate(recs):
        by_author[books[r['b']]['a']].append(k)
    drop = set()
    for a, ks in by_author.items():
        ks.sort(key=lambda k: (books[recs[k]['b']]['pr'], recs[k]['c'] != 1))
        index = collections.defaultdict(set); kept = {}
        for k in ks:
            sh = B0.shingles(re.sub(r'\{[^{}]*\}', ' ', recs[k]['t']))   # ignore quoted verses: two passages quoting the same verse are not duplicates
            if len(sh) < 3:
                kept[k] = sh; continue
            cands = collections.Counter()
            for s in sh:
                for o in index.get(s, ()):
                    cands[o] += 1
            dup = None
            for o, c in cands.most_common(5):
                if recs[o]['b'] != recs[k]['b'] and c / min(len(sh), len(kept[o])) > 0.6:
                    dup = o; break
            if dup is not None:
                drop.add(k)
                recs[dup].setdefault('also', []).append([recs[k]['b'], recs[k]['v'], recs[k]['p']])
                recs[dup]['ay'] = sorted(set(recs[dup]['ay']) | set(recs[k]['ay']))
                if not recs[k].get('inc'):
                    recs[dup].pop('inc', None)
                continue
            kept[k] = sh
            for s in sh:
                index[s].add(k)
    recs = [r for k, r in enumerate(recs) if k not in drop]
    recs.sort(key=lambda r: (-r['c'] if r['c']==1 else 0, books[r['b']]['pr'], r['b'], r['i']))
    for n, r in enumerate(recs):
        r['id'] = n; del r['i']
    json.dump({'surah': SUR, 'books': books, 'recs': recs}, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    c = collections.Counter()
    cov = collections.defaultdict(set)
    for r in recs:
        a = books[r['b']]['a']
        c[(a, 'core' if r['c'] else ('inc' if r.get('inc') else 'keep'))] += 1
        if r['c'] or not r.get('inc'):
            for v in r['ay']:
                cov[a].add(v)
    print('dropped', len(drop), 'kept', len(recs), dict(c), file=sys.stderr)
    print('verses with substantive material:', {a: len(v) for a, v in cov.items()}, 'of', NV, file=sys.stderr)

main()
