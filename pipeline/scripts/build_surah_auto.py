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
        sur_cnt = []      # citations per surah, per paragraph (for the tafsir volumes)
        for p in paras:
            f, _ = qmap.map_paragraph(Q, p['text'])
            cnt = {v: c for (s, v), c in f.items() if s == SUR}
            per.append(cnt)
            if work == 'MajmucFatawa' and 14 <= p['vol'] <= 17:
                c2 = collections.Counter()
                for (s, v), c in f.items(): c2[s] += c
                sur_cnt.append(c2)
            else:
                sur_cnt.append(None)
        # Sections of the tafsir volumes: a section opens with "فصل", a question, or "قال شيخ الإسلام".
        # Its topic = verses of this surah quoted in its first two paragraphs.
        sec_topic = [None] * len(paras)
        if work == 'MajmucFatawa' and SUR not in CORE:
            OPEN = re.compile(r'^\s*(فصل|وسئل|سئل|قال شيخ الإسلام|وقال شيخ الإسلام|قال الشيخ|وقال الشيخ|في قوله تعالى|عن قوله تعالى|في الكلام على قوله|قوله تعالى)')
            start = None
            for i, p in enumerate(paras):
                if not (14 <= p['vol'] <= 17):
                    start = None; continue
                if OPEN.match(p['text']) or start is None:
                    start = i
                    cur = [i]           # section marker (list identity)
                sec_topic[i] = cur
            # decide each section: this surah must lead its citations with at least 35%
            secs = collections.OrderedDict()
            for i, s_ in enumerate(sec_topic):
                if s_ is not None:
                    secs.setdefault(id(s_), []).append(i)
            prev_ok, chain = None, 0
            for idxs in secs.values():
                # an untitled "فصل" that continues an accepted section inherits its topic
                opener_txt = paras[idxs[0]]['text'].strip()
                own = set()
                for k in idxs: own |= set(per[k])
                other = collections.Counter()
                for k in idxs[:2]:
                    if sur_cnt[k]: other.update({s: c for s, c in sur_cnt[k].items() if s != SUR})
                nxt = paras[idxs[1]]['text'].strip() if len(idxs) > 1 else ''
                cont = re.match(r'^(وقوله|ثم قال|وأما قوله|وقوله تعالى)', nxt) is not None
                if prev_ok and chain < 4 and opener_txt.startswith('فصل') and paras[idxs[0]]['vol'] == paras[prev_ok[-1]]['vol'] \
                        and idxs[0] - prev_ok[-1] <= 1 and (own or cont or sum(other.values()) <= 2):
                    topic = own or sec_topic[prev_ok[0]]
                    for k in idxs: sec_topic[k] = topic
                    prev_ok, chain = idxs, chain + 1
                    continue
                tot = collections.Counter()
                for k in idxs:
                    if sur_cnt[k]: tot.update(sur_cnt[k])
                opener = any(per[k] for k in idxs[:3])
                explicit = False
                if re.match(r'^\s*(في قوله تعالى|عن قوله تعالى|في الكلام على قوله|قوله تعالى)', opener_txt):
                    mq = re.search(r'\{([^{}]*)\}', opener_txt)
                    if mq:
                        f1, _ = qmap.map_paragraph(Q, '{' + mq.group(1) + '}')
                        explicit = {s for s, v in f1} == {SUR}
                ok = explicit or bool(tot) and opener and (tot.most_common(1)[0][0] == SUR or tot[SUR] / sum(tot.values()) >= 0.2) and tot[SUR] / sum(tot.values()) >= 0.15
                topic = set()
                for k in idxs[:3]: topic |= set(per[k])
                if not topic:
                    for k in idxs: topic |= set(per[k])
                for k in idxs:
                    sec_topic[k] = topic if ok and topic else None
                prev_ok, chain = (idxs, 0) if (ok and topic) else (None, 0)
        def in_tafsir_section(i):
            return bool(sec_topic[i])
        def _unused(i):
            # Majmu' al-Fatawa vols 14-17 are its "Book of Tafsir": a paragraph belongs to this
            # surah's section when the surrounding paragraphs cite this surah more than any other.
            if sur_cnt[i] is None or SUR in CORE:
                return False
            tot = collections.Counter()
            for j in range(max(0, i - 4), min(len(paras), i + 5)):
                if sur_cnt[j]: tot.update(sur_cnt[j])
            return bool(tot) and tot.most_common(1)[0][0] == SUR and tot[SUR] >= 3
        # header-named sections
        hcache = {}
        hits = []
        last_v, last_i = None, -99
        for i, p in enumerate(paras):
            cnt = per[i]
            in_core = any(a <= i <= b for a, b in core_rng) or in_tafsir_section(i)
            if p['header'] not in hcache:
                hcache[p['header']] = header_verses(p['header'])
            hv, whole = hcache[p['header']]
            vs = set(cnt)
            if in_core and sec_topic[i]:
                hits.append((i, vs | sec_topic[i] if not vs else vs, 1)); continue
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
            sh = B0.shingles(recs[k]['t'])
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
