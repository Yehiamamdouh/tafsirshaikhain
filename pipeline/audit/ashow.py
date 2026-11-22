"""ashow.py : build review packets from audit/items.json.
  S packets: summ items with risk flags (OPENQ / XIMAM / CROSSNAME / COMPILED / QUESTION / QUALIFY / NOVERSE)
  N packets: every nuq item
  R packets: random sample of 300 summ items (full independent check)
Each item block shows the context a reviewer needs; reviewers can dig further in out/cache/{WORK}.pkl."""
import json, os, re, sys, random, pickle, collections, glob
SC = '/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
sys.path.insert(0, SC + '/audit')
ws = lambda s: re.sub(r'\s+', ' ', s).strip()
I = json.load(open(SC + '/audit/items.json'))
# items already given a dedicated voice review today (gap + collation lines flagged by gvoice and kept)
reviewed = set()
for f in (SC + '/full/gvoice_out.txt', SC + '/coll/cvoice_out.txt'):
    for m in re.finditer(r'\| (\d+):(\d+) (IT|IQ) (\d+) ', open(f).read()): reviewed.add((int(m[1]), int(m[2]), m[3], int(m[4])))
_P = {}
def paras(w):
    if w not in _P:
        p = f'{SC}/out/cache/{w}.pkl'
        if not os.path.exists(p): _P[w] = None; return None
        raw = pickle.load(open(p, 'rb'))['paras']; P = [ws(x['text']) for x in raw]
        first = collections.defaultdict(list)
        for i, t in enumerate(P): first[t[:80]].append(i)
        _P[w] = (raw, P, first)
    return _P[w]
_S = {}
def site(su):
    if su not in _S:
        d = json.load(open(f'{SC}/site/s{su}.json')); p = f'{SC}/site/s{su}i.json'
        inc = json.load(open(p)) if os.path.exists(p) else []
        _S[su] = (d, {r['id']: r for r in d['recs'] + inc})
    return _S[su]
def ctx(it, nb=20):
    d, R = site(it['su']); r = R[it['r']]; T = ws(r['t']); t = it['t']; i = T.find(t)
    pp = paras(it['w']); k = None
    if pp:
        raw, P, first = pp; cs = first.get(T[:80], [])
        cs2 = [j for j in cs if T.startswith(P[j])] or cs
        cs3 = [j for j in cs2 if raw[j]['vol'] == r['v'] and raw[j]['p_start'] == r['p']] or cs2
        k = cs3[0] if cs3 else None
    pre = T[:i] if i >= 0 else ''
    if pp and k is not None: pre = ' ‖ '.join(pp[1][max(0, k - nb):k] + [pre])
    post = T[i + len(t):] if i >= 0 else ''
    if pp and k is not None and len(post) < 400: post = post + ' ‖ ' + ' '.join(pp[1][k + 1:k + 2])
    vt = d['verses'][it['v'] - 1] if 1 <= it['v'] <= len(d['verses']) else ''
    return pre, post, vt, k
def head(it, extra=''):
    return f"\n### {it['id']}  [{','.join(it['f']) or '-'}]  {it['a']}  {it['w']} {it['vol']}/{it['p']}  rec{it['r']}  verse {it['su']}:{it['v']}{extra}"
def vshort(vt): return ' '.join(re.sub(r'[ً-ْٰۖ-ۭ]', '', vt).split()[:14])
def block_S(it):
    pre, post, vt, k = ctx(it)
    out = [head(it), f"VERSE: {vshort(vt)}"]
    if 'OPENQ' in it['f']:
        oq = it.get('openq', ''); j = pre.rfind(oq[:20]) if oq else -1
        between = pre[j:] if j >= 0 else pre[-700:]
        if len(between) > 900: between = between[:350] + ' … ' + between[-500:]
        out.append(f"OPENER→EXCERPT: {between}")
    else:
        out.append(f"BEFORE: {pre[-500:]}")
    if 'CROSSNAME' in it['f']:
        m = re.search(r'.{0,80}(?:قال ابن القيم|قال ابن قيم الجوزية|قال تلميذه|قال الحافظ شمس الدين|قال شيخنا|قال شيخ الإسلام|وسمعت شيخ).{0,80}', pre[-3000:] + ' ' + post[:800])
        if m: out.append(f"NAMING: …{m.group(0)}…")
    if 'XIMAM' in it['f']: out.append('NOTE: this exact text also occurs in a book of the OTHER imam (copying in one direction).')
    if 'COMPILED' in it['f']: out.append('NOTE: book compiled by someone else (Mustadrak / al-Ikhtiyarat); check whose wording this is.')
    out.append(f"EXCERPT: «{it['t']}»")
    out.append(f"AFTER: {post[:350]}")
    return '\n'.join(out)
def block_N(it):
    pre, post, vt, k = ctx(it, nb=6)
    out = [head(it), f"VERSE: {vshort(vt)}", f"WHO: {it.get('who')}   STANCE: {it.get('st')}"]
    out.append(f"BEFORE: {pre[-450:]}")
    out.append(f"QUOTE: «{it['t']}»")
    out.append(f"AFTER: {post[:700]}")
    if it.get('rt'): out.append(f"REJOINDER (rt): «{it['rt']}»")
    return '\n'.join(out)
def block_R(it):
    pre, post, vt, k = ctx(it, nb=4)
    return '\n'.join([head(it), f"VERSE: {re.sub(r'[ً-ْٰۖ-ۭ]', '', vt)}", f"BEFORE: {pre[-900:]}",
                      f"EXCERPT: «{it['t']}»", f"AFTER: {post[:600]}"])
RISK = {'OPENQ', 'XIMAM', 'CROSSNAME', 'COMPILED', 'QUESTION', 'QUALIFY', 'NOVERSE'}
S = []
for it in I:
    if it['k'] != 'summ' or not (set(it['f']) & RISK): continue
    if set(it['f']) & RISK == {'OPENQ'} and (it['su'], it['v'], it['a'], it['r']) in reviewed: continue
    S.append(it)
N = [it for it in I if it['k'] == 'nuq']
random.seed(20261027)
R = random.sample([it for it in I if it['k'] == 'summ'], 300)
os.makedirs(SC + '/audit/pk', exist_ok=True)
for f in glob.glob(SC + '/audit/pk/*.txt'): os.remove(f)
def write(name, lst, fn, size):
    n = 0
    for c in range(0, len(lst), size):
        n += 1
        open(f'{SC}/audit/pk/{name}{n:02d}.txt', 'w').write('\n'.join(fn(it) for it in lst[c:c + size]) + '\n')
    return n
ns = write('S', S, block_S, 115); nn = write('N', N, block_N, 125); nr = write('R', R, block_R, 100)
json.dump({'S': [i['id'] for i in S], 'N': [i['id'] for i in N], 'R': [i['id'] for i in R]}, open(SC + '/audit/packets.json', 'w'))
print('S items', len(S), 'packets', ns, '| N items', len(N), 'packets', nn, '| R items', len(R), 'packets', nr)
