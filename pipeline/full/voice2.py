"""voice2.py : multi-paragraph scan — flag summ excerpts that sit inside a long quotation of someone else
(an opener like «قال فلان في كتابه:» / «قال الرافضي» before the excerpt with no closer like «قلت/انتهى/والجواب» in between)."""
import json, re, os, sys, pickle, collections
SC = '/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
BASE = sys.argv[1] if len(sys.argv) > 1 else SC + '/site'
ws = lambda s: re.sub(r'\s+', ' ', s).strip()
OPEN = re.compile(r'(?:^|[\s.:؛])(?:و?قال|و?ذكر|و?حكى|و?نقل)\s+(?:الإمام\s+|الشيخ\s+|القاضي\s+|الحافظ\s+|شيخ الإسلام\s+)?'
                  r'(?:أبو|ابن|الرازي|الغزالي|الآمدي|الشهرستاني|الجويني|الباقلاني|الأشعري|صاحب|المصنف|الرافضي|المعترض|الخطابي|البيهقي|اللالكائي|الكرماني|السهروردي|الأرموي|القرطبي|الزمخشري|الثعلبي|الواحدي|البغوي|محمد|أحمد|عبد|علي|حرب|الهروي|الأنصاري|المروزي|الطبري|الدارمي|عثمان)'
                  r'[^.:]{0,90}?(?:في كتابه|في رسالته|في كتاب|في مصنفه|في تفسيره)[^.:]{0,80}?:|(?:^|[\s.])قال الرافضي|(?:^|[\s.])قال المعترض|(?:^|[\s.])قال المصنف')
CLOSE = re.compile(r'(?:^|[\s.(])(?:قلت|انتهى|إلى هنا|هذا آخر|هذا كلامه|هذا لفظه|والجواب|فالجواب|فيقال|فنقول|أقول|والمقصود هنا|وهذا الكلام)')
_P = {}
def paras(w):
    if w not in _P:
        p = f'{SC}/out/cache/{w}.pkl'
        if not os.path.exists(p): _P[w] = None; return None
        P = [ws(x['text']) for x in pickle.load(open(p, 'rb'))['paras']]
        first = collections.defaultdict(list)
        for i, t in enumerate(P): first[t[:80]].append(i)
        _P[w] = (P, first)
    return _P[w]
flags = []
for su in range(1, 115):
    d = json.load(open(f'{BASE}/s{su}.json')); p = f'{BASE}/s{su}i.json'
    inc = json.load(open(p)) if os.path.exists(p) else []
    R = {r['id']: r for r in d['recs'] + inc}; B = d['books']
    for a, vs in d.get('summ', {}).items():
        for v, xs in vs.items():
            for x in xs:
                r = R[x['r']]; w = B[r['b']]['w']; T = ws(r['t']); pp = paras(w)
                if not pp: continue
                P, first = pp; ks = first.get(T[:80], [])
                if not ks: continue
                k = ks[0]; i = T.find(x['t'])
                # text before the excerpt: previous 14 paragraphs + record prefix
                ctx = ' ‖ '.join(P[max(0, k - 14):k] + [T[:i]])
                opens = [m for m in OPEN.finditer(ctx)]
                if not opens: continue
                o = opens[-1]; tail = ctx[o.end():]
                if CLOSE.search(tail): continue
                dist = len(tail)
                flags.append((su, a, v, x['t'][:70], w, r['v'], r['p'], dist, ctx[max(0, o.start() - 40):o.end() + 60]))
print(len(flags))
for f in flags: print(f)
