"""Build the Fatiha dataset from OpenITI texts of Ibn Taymiyya and Ibn al-Qayyim."""
import sys, os, re, glob, json, collections
sys.path.insert(0, os.path.dirname(__file__))
import parse
from parse import norm

IT = '/home/claude/openiti/0750ah/data/0728IbnTaymiyya'
IQ = '/home/claude/openiti/0775ah/data/0751IbnQayyimJawziyya'
OUT = sys.argv[1] if __name__ == '__main__' else None

# Works dropped: later compilations, OCR texts without page numbers, lists of titles.
DROP = {'DaqaiqTafsir', 'TafsirQuran', 'LaaliNayyirat', 'RisalaBaclabakkiyya', 'AsmaMuallafatIbnTaymiya'}
# Lower number wins when the same passage appears in two books.
PRIORITY = collections.defaultdict(lambda: 5, {
    'MajmucFatawa': 1, 'MadarijSalikin': 1, 'BadaicFawaid': 1, 'ZadMacad': 2,
    'FatawaKubra': 8, 'MustadrakCalaMajmucFatawa': 8, 'MajmucatRasailWaMasail': 8, 'JamicRasail': 7,
    'RasailWaFatawa': 9, 'MinFatawaIbnTaymiyya': 9, 'TibbNabawi': 9, 'IghathatLahfan': 5,
})

def title_of(path, m):
    t = m.get('020.BookTITLE')
    if t and t != 'NODATA':
        return t
    with open(path, encoding='utf-8') as f:
        head = f.read(6000)
    for pat in [r'#META#\s*bk:\s*(.+)', r'الكتاب:\s*([^¶\n]+)', r'#META#\s*iso:\s*(.+)']:
        mm = re.search(pat, head)
        if mm:
            return re.sub(r'\s+ط\s.*$', '', mm.group(1)).strip()
    return os.path.basename(path).split('.')[1]

def edition_of(m):
    parts = []
    for k in ('040.EdEDITOR', '043.EdPUBLISHER', '041.EdNUMBER'):
        v = m.get(k)
        if v and v != 'NODATA':
            parts.append(v)
    return '، '.join(parts)

def shamela_id(path):
    mm = re.search(r'\.Shamela0*(\d+)-ara', path)
    return int(mm.group(1)) if mm else None

# ---- Core chapters devoted to al-Fatiha: (paragraph range, verses) ----------
# Ranges were read off the chapter headings of each edition (see notes in the app).
CORE = {
    'MadarijSalikin': [
        ((0, 18), [0]),          # هداية القرآن (مقدمة الكلام على الفاتحة)
        ((19, 55), [0]),         # اشتمال الفاتحة على أمهات المطالب
        ((56, 89), [6]),         # الصراط المستقيم
        ((90, 99), [7]),         # الذين أنعم الله عليهم
        ((100, 106), [6]),       # كيفية سؤال الهداية
        ((107, 172), [2, 3]),    # أنواع التوحيد والأسماء في الفاتحة
        ((173, 261), [6]),       # مراتب الهداية
        ((262, 289), [0]),       # الشفاء
        ((290, 400), [0]),       # الرد على المبطلين
        ((401, 729), [5]),       # إياك نعبد وإياك نستعين
    ],
    'RisalaIlaAhadIkhwan': [
        ((5, 8), [6, 7]),        # المنعم عليهم والمغضوب عليهم والضالون
        ((9, 20), [6]),          # افتقار العبد إلى الهداية في كل لحظة
    ],
    'BadaicFawaid': [
        ((59, 61), [1]),         # اسم الله والاشتقاق
        ((62, 64), [1, 3]),      # الرحمن في البسملة
        ((65, 66), [1]),         # حذف العامل في بسم الله
        ((472, 488), [6]),       # عشرون مسألة: البدل، التعريف، الصراط
        ((489, 532), [7]),       # المنعم عليهم، المغضوب عليهم، الضالون
        ((533, 544), [6]),       # أنواع الهداية وحقيقة الصراط المستقيم
    ],
    'Salat': [
        ((561, 564), [2]),
        ((565, 566), [3]),
        ((567, 568), [4]),
        ((569, 569), [4, 5]),
        ((570, 572), [6, 7]),
    ],
    'MajmucFatawa': [
        ((10680, 10681), [6]),
        ((10684, 10686), [0]),
        ((10687, 10698), [5]),
        ((10699, 10702), [2, 5]),
        ((10703, 10735), [5]),
        ((10736, 10743), [6]),
    ],
}
CORE_LABEL = {
    'MadarijSalikin': 'الكلام على الفاتحة في صدر مدارج السالكين',
    'RisalaIlaAhadIkhwan': 'الكلام على الهداية في رسالته إلى أحد إخوانه',
    'BadaicFawaid': 'فوائد في البسملة، والعشرون مسألة في قوله اهدنا الصراط المستقيم',
    'Salat': 'وقفات المصلي مع آيات الفاتحة (كتاب الصلاة)',
    'MajmucFatawa': 'كتاب التفسير: سورة الفاتحة (مجموع الفتاوى ج14)',
}

def detect(text):
    verses, surah, how = parse.detect(text)
    v = set(verses)
    n = norm(text)
    if surah:
        if 'البسمله' in n or 'بسم الله الرحمن الرحيم' in n:
            v.add(1)
        if 'الحمد لله رب العالمين' in n:
            v.add(2)
        if 'الرحمن الرحيم' in n.replace('بسم الله الرحمن الرحيم', ''):
            v.add(3)
    return sorted(v), surah

FIQH = ['الصلاه', 'المامom', 'الماموم', 'الامام', 'ركعه', 'الركعه', 'الجهر', 'يجهر', 'القراءه', 'يقرا', 'السجود', 'التامين', 'امين', 'الجنازه']

def shingles(t, k=5):
    w = norm(re.sub(r'[^\w\s]', ' ', t)).split()
    return {' '.join(w[i:i + k]) for i in range(max(1, len(w) - k + 1))}

def main():
    books, recs = [], []
    paths = sorted(glob.glob(IT + '/*/*-ara*')) + sorted(glob.glob(IQ + '/*/*-ara*'))
    for path in paths:
        if path.endswith('.yml') or path.endswith('.inProgress'):
            continue
        work = os.path.basename(path).split('.')[1]
        if work in DROP or work == 'IghathatLahfan' and 'Shamela0007513' in path:
            continue
        author = 'IT' if '0728IbnTaymiyya' in path else 'IQ'
        m = parse.meta(path)
        paras = parse.paragraphs(path)
        core_map = {}
        for (a, b), vs in CORE.get(work, []):
            for i in range(a, b + 1):
                core_map[i] = vs
        hit_idx = []
        for i, p in enumerate(paras):
            vs, surah = detect(p['text'])
            if i in core_map:
                vs = sorted(set(vs) | set(core_map[i]))
                hit_idx.append((i, vs, True))
            elif vs or surah:
                hit_idx.append((i, vs or [0], False))
        if not hit_idx:
            continue
        bi = len(books)
        books.append({'id': bi, 'a': author, 'w': work, 't': title_of(path, m), 'ed': edition_of(m),
                      'sh': shamela_id(path), 'pr': PRIORITY[work], 'core': CORE_LABEL.get(work, '')})
        for i, vs, core in hit_idx:
            p = paras[i]
            if len(norm(p['text'])) < 25 and not core:
                continue
            r = {'b': bi, 'i': i, 'v': p['vol'], 'p': p['p_start'], 'pe': p['p_end'],
                 'h': re.sub(r'^(CHECK|AUTO)\s+', '', p['header']), 't': p['text'], 'ay': vs, 'c': 1 if core else 0}
            n = norm(p['text'])
            if not core and set(vs) <= {0, 1} and sum(w in n for w in FIQH) >= 2:
                r['f'] = 1     # rulings on reciting al-Fatiha in prayer
            if not core:   # one paragraph of context on each side
                r['cb'] = paras[i - 1]['text'] if i > 0 else ''
                r['ca'] = paras[i + 1]['text'] if i + 1 < len(paras) else ''
            recs.append(r)
        print(f"{len(hit_idx):5d} {author} {work}", file=sys.stderr)

    # ---- de-duplicate the same passage across books of the same author ----
    by_author = collections.defaultdict(list)
    for k, r in enumerate(recs):
        by_author[books[r['b']]['a']].append(k)
    drop = set()
    for a, ks in by_author.items():
        ks.sort(key=lambda k: (books[recs[k]['b']]['pr'], -recs[k]['c']))
        index = collections.defaultdict(set)
        kept_sh = {}
        for k in ks:
            sh = shingles(recs[k]['t'])
            if len(sh) < 3:
                kept_sh[k] = sh; continue
            cands = collections.Counter()
            for s in sh:
                for o in index.get(s, ()):
                    cands[o] += 1
            dup_of = None
            for o, c in cands.most_common(5):
                if recs[o]['b'] != recs[k]['b'] and c / min(len(sh), len(kept_sh[o])) > 0.6:
                    dup_of = o; break
            if dup_of is not None:
                drop.add(k)
                recs[dup_of].setdefault('also', []).append([recs[k]['b'], recs[k]['v'], recs[k]['p']])
                # merge verse tags
                recs[dup_of]['ay'] = sorted(set(recs[dup_of]['ay']) | set(recs[k]['ay']))
                continue
            kept_sh[k] = sh
            for s in sh:
                index[s].add(k)
    recs = [r for k, r in enumerate(recs) if k not in drop]
    print('dropped duplicates:', len(drop), 'kept:', len(recs), file=sys.stderr)

    used = sorted({r['b'] for r in recs} | {x[0] for r in recs for x in r.get('also', [])})
    remap = {b: n for n, b in enumerate(used)}
    books = [dict(books[b], id=remap[b]) for b in used]
    for r in recs:
        r['b'] = remap[r['b']]
        for x in r.get('also', []):
            x[0] = remap[x[0]]
    recs.sort(key=lambda r: (books[r['b']]['a'], -r['c'], books[r['b']]['pr'], r['b'], r['i']))
    for n, r in enumerate(recs):
        r['id'] = n
        del r['i']
    json.dump({'books': books, 'recs': recs}, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    c = collections.Counter()
    for r in recs:
        for v in r['ay']:
            c[(books[r['b']]['a'], v, r['c'])] += 1
    for k in sorted(c):
        print(k, c[k], file=sys.stderr)

if __name__ == '__main__':
    main()
