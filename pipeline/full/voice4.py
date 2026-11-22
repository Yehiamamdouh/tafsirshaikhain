"""voice4.py : flag summ excerpts that sit inside an UNCLOSED quotation mark opened after «قال/ذكر ... :» within the
previous 60 paragraphs (marks: ( ) « » " ")."""
import json, re, os, sys, pickle, collections
SC = '/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
BASE = sys.argv[1] if len(sys.argv) > 1 else SC + '/site'
ws = lambda s: re.sub(r'\s+', ' ', s).strip()
OPEN = re.compile(r'(?:قال|وقال|ذكر|وذكر|حكى|وحكى|نقل|ونقل|يقول|ولفظه|ونصه|ما نصه)[^:«"(]{0,120}?:\s*(?P<m>[(«"])')
PAIR = {'(': ')', '«': '»', '"': '"'}
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
def unclosed(ctx):
    """return the last opener whose quote is still open at the end of ctx"""
    best = None
    for m in OPEN.finditer(ctx):
        mk = m.group('m'); cl = PAIR[mk]; s = m.end()
        rest = ctx[s:]
        if mk == '"':
            if rest.count('"') % 2 == 0: best = m
        else:
            depth = 1
            for ch in rest:
                if ch == mk: depth += 1
                elif ch == cl:
                    depth -= 1
                    if depth == 0: break
            if depth > 0: best = m
    return best
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
                ctx = ' ‖ '.join(P[max(0, k - 60):k] + [T[:i]])
                m = unclosed(ctx)
                if not m: continue
                dist = len(ctx) - m.end()
                if dist > 25000: continue
                flags.append((su, a, v, x['t'][:60], w, r['v'], r['p'], dist, ctx[max(0, m.start() - 60):m.end() + 80]))
print(len(flags))
for f in flags: print(f)
