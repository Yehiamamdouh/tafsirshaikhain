"""Map Quranic quotations in a paragraph to (surah, verse) pairs.

Quotations in the Shamela texts sit in {braces}, sometimes followed by a
citation like [البقرة: 255]. Spacing in the texts varies (ياأيها / يا أيها),
so matching is done on letter-only strings.
"""
import json, re, os, sys, collections
sys.path.insert(0, os.path.dirname(__file__))
from parse import norm, AR_DIG

QDIR = '/home/claude/quran/quran-json/data/tanzil'
K = 10                      # n-gram size (letters) for the index
MIN = 12                    # shortest quotation segment we try to place (letters)

def letters(s):
    return re.sub(r'[^ء-ي]', '', norm(s))

class Quran:
    def __init__(self):
        clean = json.load(open(os.path.join(QDIR, 'simple-clean.json'), encoding='utf-8'))
        chap = json.load(open(os.path.join(QDIR, 'chapters.json'), encoding='utf-8'))['chapters']
        self.names = {c['id']: c['name'] for c in chap}
        self.name2id = {letters(c['name']): c['id'] for c in chap}
        self.text = {}      # surah -> letters string
        self.starts = {}    # surah -> list of verse start offsets
        self.index = collections.defaultdict(list)
        for s, verses in clean.items():
            s = int(s)
            buf, st = [], []
            pos = 0
            for v in verses:
                st.append(pos)
                t = letters(v['text'])
                buf.append(t); pos += len(t)
            txt = ''.join(buf)
            self.text[s] = txt; self.starts[s] = st
            for i in range(0, len(txt) - K + 1):
                self.index[txt[i:i + K]].append((s, i))

    def verses_at(self, s, a, b):
        st = self.starts[s]
        import bisect
        v1 = bisect.bisect_right(st, a)
        v2 = bisect.bisect_right(st, b - 1)
        return list(range(v1, v2 + 1))

    def find(self, seg):
        """Return list of (surah, [verses]) where the letter string seg occurs."""
        if len(seg) < MIN:
            return []
        hits = []
        for s, i in self.index.get(seg[:K], ()):
            if self.text[s].startswith(seg, i):
                hits.append((s, self.verses_at(s, i, i + len(seg))))
        return hits

SPLIT = re.compile(r'\.\.\.|…|إلى قوله|الى قوله|إلى آخر|الآية|الايه|الآيات|\(\d+\)|\[[^\]]*\]')
CITE = re.compile(r'\[\s*([ء-ي ]+?)\s*:\s*([٠-٩\d]+)\s*(?:[-–]\s*([٠-٩\d]+))?\s*\]')
BRACE = re.compile(r'\{([^{}]*)\}')

def quotes_in(text):
    """Yield (quote_text, end_offset) for innermost brace groups."""
    t = text
    for m in BRACE.finditer(t):
        yield m.group(1), m.end()

def map_paragraph(Q, text):
    """Return dict {(surah, verse): kind} kind in {'cite','quote'}; plus count of quotes per verse."""
    found = collections.Counter()
    kinds = {}
    for m in CITE.finditer(text):
        name = letters(m.group(1))
        s = Q.name2id.get(name)
        if not s:
            continue
        a = int(m.group(2).translate(AR_DIG)); b = int((m.group(3) or m.group(2)).translate(AR_DIG))
        if a > b or b - a > 20:
            continue
        for v in range(a, b + 1):
            if v <= len(Q.starts[s]):
                found[(s, v)] += 1; kinds[(s, v)] = 'cite'
    for q, end in quotes_in(text):
        for seg in SPLIT.split(q):
            L = letters(seg)
            if len(L) < MIN:
                continue
            hits = Q.find(L)
            if not hits:
                # quotation may carry a few extra words of the author's: try trimming from the end
                words = norm(seg).split()
                while len(words) > 3 and not hits:
                    words = words[:-1]
                    L2 = letters(' '.join(words))
                    if len(L2) < MIN:
                        break
                    hits = Q.find(L2)
            surahs = {s for s, _ in hits}
            if len(surahs) == 1 and len(hits) <= 2:
                for s, vs in hits:
                    for v in vs:
                        found[(s, v)] += 1; kinds.setdefault((s, v), 'quote')
            elif len(surahs) > 1:
                # ambiguous: keep only if a citation in this paragraph names one of the candidates
                for s, vs in hits:
                    for v in vs:
                        if kinds.get((s, v)) == 'cite':
                            found[(s, v)] += 1
    return found, kinds

if __name__ == '__main__':
    Q = Quran()
    tests = ['قال تعالى: {ذلك الكتاب لا ريب فيه هدى للمتقين} أي',
             '{الله لا إله إلا هو الحي القيوم} [البقرة: 255]',
             '{ياأيها الناس اعبدوا ربكم الذي خلقكم}',
             '{إن الله على كل شيء قدير}']
    for t in tests:
        print(t[:40], dict(map_paragraph(Q, t)[0]))
