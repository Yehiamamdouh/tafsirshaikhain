"""audit.py : phase-A automated audit of every summ and nuq item on the site.
Writes audit/items.json (all items with ids + flags) and prints flag statistics.
Flags:
  OPENQ   an attribution / debate opener within the record or up to 20 paragraphs before the excerpt, not closed
  XIMAM   text also found verbatim in the other imam's books (copying in either direction)
  CROSSNAME  IT book paragraph naming IQ as speaker nearby («قال ابن القيم») or IQ book with «قال شيخنا/شيخ الإسلام» nearby
  COMPILED   book/section compiled by someone else (Mustadrak, FatawaKubra vol5 Ikhtiyarat)
  QUESTION   excerpt sits in a question paragraph («سئل ...» before «فأجاب»)
  NOVERSE    verse words not found in the record or 2 paragraphs around it, and record not linked to the verse
  FMT        footnote digits glued to words / unbalanced brackets / starts or ends mid-word
  QUALIFY    the text right after the excerpt opens with a qualification («لكن», «إلا أن», «والصحيح», «وفيه نظر», ...)"""
import json, os, re, sys, glob, pickle, collections, zlib
SC = '/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
ws = lambda s: re.sub(r'\s+', ' ', s).strip()
DIA = re.compile(r'[ؐ-ًؚ-ٰٟۖ-ۭـ]')
def nz(s):
    s = DIA.sub('', s)
    s = re.sub('[إأآٱ]', 'ا', s).replace('ى', 'ي').replace('ة', 'ه').replace('ؤ', 'و').replace('ئ', 'ي')
    return ' '.join(re.sub(r'[^ء-ي ]', ' ', s).split())
# ---------- book paragraphs
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
def locate_para(w, r):
    pp = paras(w)
    if not pp: return None
    raw, P, first = pp; T = ws(r['t']); cs = first.get(T[:80], [])
    cs2 = [i for i in cs if T.startswith(P[i])] or cs
    cs3 = [i for i in cs2 if raw[i]['vol'] == r['v'] and raw[i]['p_start'] == r['p']] or cs2
    return cs3[0] if cs3 else None
# ---------- markers
SKIP = r'(?:تعالى|الله|سبحانه|النبي|رسول|صلى|عز|ربك|ربنا|لهم|له|لنبيه|لي|موسى|إبراهيم|عيسى|نوح|يوسف|لوط|يعقوب|هود|صالح|شعيب|فرعون|الملائكة|في|فيه|فيها|بعد|قبل|ذلك|هذا|هنا|عن|لموسى|لأبيه|لقومه)'
OPEN = re.compile(r'((?:و|ف)?(?:قال|قالت|يقول|حكى|ذكر|نقل|روى)\s+(?!' + SKIP + r'\b)[^\s:،.{}]{2,}(?:\s+[^\s:،.{}]{2,}){0,6}?\s*:|(?:و|ف)?قالوا\s*:|فإن قيل|فإن قال|قالت\s+(?:الفقراء|الأغنياء|طائفة|الجهمية|المعتزلة|الأشعرية|الرافضة|النصارى|اليهود)|وقالت طائفة|قال\s+(?:الموجبون|المانعون|المسقطون|المجوزون|الآخرون|المنازع|المعترض|الرافضي|المصنف|صاحب|أهل هذا القول|أصحاب)|ولفظه\s*:|ونصه\s*:|ما نصه|ومن الناس من يقول|يقولون\s*:|قالوا\s)')
CLOSE = re.compile(r'انتهى|انتهي|اهـ|قلت\s*:|قلت\b|والجواب|فالجواب|الجواب\s*:|فيقال|هذا كلامه|هذا لفظه|تم كلامه|آخر كلامه|والمقصود|والصواب|والصحيح|والتحقيق|قيل له|قيل\s*:|فصل\b|وهذا القول|وهذا باطل|وهذا ضعيف|وهذا خطأ|فأجاب|وبالجملة')
QUAL = re.compile(r'^\s*[،,.؛:]?\s*(?:لكن|ولكن|إلا أن|الا أن|غير أن|وفيه نظر|وهذا ضعيف|وهذا القول|والصحيح|والصواب|والتحقيق|وليس كذلك|وهو خطأ|وهذا خطأ|وهذا باطل|وفي هذا نظر|قلت)')
FMTR = re.compile(r'[ء-ي]\d|\d[ء-ي]|(?<![\[\(\d/:-])\s\d{1,2}\s*(?:[،.؛]|$)')
def unbalanced(t):
    return any(t.count(a) != t.count(b) for a, b in ('{}', '()', '[]', '«»'))
# ---------- other-imam corpus grams (exact 8-gram check of normalized text)
IMAMW = {}
for su in range(1, 115):
    for b in json.load(open(f'{SC}/site/s{su}.json'))['books']: IMAMW[b['w']] = b['a']
G = {'IT': set(), 'IQ': set()}
N = 8
def grams(s):
    w = s.split(); return {zlib.crc32(' '.join(w[i:i + N]).encode()) for i in range(len(w) - N + 1)}
for w, a in IMAMW.items():
    pp = paras(w)
    if not pp: continue
    for t in pp[1]: G[a] |= grams(nz(t))
print('grams', {k: len(v) for k, v in G.items()}, file=sys.stderr)
# ---------- items
items = []
for su in range(1, 115):
    d = json.load(open(f'{SC}/site/s{su}.json')); p = f'{SC}/site/s{su}i.json'
    inc = json.load(open(p)) if os.path.exists(p) else []
    R = {r['id']: r for r in d['recs'] + inc}; B = d['books']; V = d['verses']
    for kind in ('summ', 'nuq'):
        for a, vs in d.get(kind, {}).items():
            for v, xs in vs.items():
                for j, x in enumerate(xs):
                    r = R[x['r']]; w = B[r['b']]['w']; T = ws(r['t']); t = ws(x['t'])
                    it = {'id': f'{kind[0]}{su}:{v}:{a}:{j}', 'k': kind, 'su': su, 'v': int(v), 'a': a, 'r': r['id'], 'w': w,
                          'vol': r['v'], 'p': r['p'], 't': t, 'f': []}
                    if kind == 'nuq': it.update(who=x.get('who'), st=x.get('st'), rt=x.get('rt', ''))
                    i = T.find(t); k = locate_para(w, r); pp = paras(w)
                    pre = T[:i] if i >= 0 else ''
                    post = T[i + len(t):] if i >= 0 else ''
                    if pp and k is not None:
                        raw, P, _ = pp
                        pre = ' ‖ '.join(P[max(0, k - 20):k] + [pre])
                        post = post + ' ‖ ' + ' '.join(P[k + 1:k + 2]) if len(post) < 200 else post
                        near = ' '.join(P[max(0, k - 3):k + 2])
                    else: near = T
                    if kind == 'summ':
                        last = None
                        for m in OPEN.finditer(pre): last = m
                        if last and not CLOSE.search(pre[last.end():]) and not re.match(r'\s*[{﴿]', pre[last.end():]):
                            it['f'].append('OPENQ'); it['openq'] = last.group(0)[:60]; it['openq_dist'] = len(pre) - last.end()
                        other = 'IQ' if a == 'IT' else 'IT'
                        g = grams(nz(t))
                        if g and len(g & G[other]) >= max(2, len(g) // 2): it['f'].append('XIMAM')
                        if a == 'IT' and re.search(r'قال ابن القيم|قال ابن قيم الجوزية|قال تلميذه|قال الحافظ شمس الدين', near): it['f'].append('CROSSNAME')
                        if a == 'IQ' and re.search(r'قال شيخنا|قال شيخ الإسلام|وسمعت شيخ', near) and 'CROSSNAME' not in it['f']: it['f'].append('CROSSNAME')
                        if w == 'MustadrakCalaMajmucFatawa' or (w == 'FatawaKubra' and r['v'] == 5 and r['p'] >= 297): it['f'].append('COMPILED')
                        if re.match(r'\s*(?:و)?سئل', T) and 'فأجاب' in T and i >= 0 and i < T.find('فأجاب'): it['f'].append('QUESTION')
                        if QUAL.match(post[:80]): it['f'].append('QUALIFY'); it['qual'] = post[:80]
                    # verse presence
                    vt = nz(V[it['v'] - 1]) if 1 <= it['v'] <= len(V) else ''
                    vw = [x_ for x_ in vt.split() if len(x_) > 1]
                    found = False
                    if vw:
                        L = min(3, len(vw)); nn = nz(near)
                        for s0 in range(0, len(vw) - L + 1):
                            if ' '.join(vw[s0:s0 + L]) in nn: found = True; break
                    if not found and it['v'] not in r.get('ay', []) and it['v'] != 0: it['f'].append('NOVERSE')
                    if FMTR.search(t) or unbalanced(t): it['f'].append('FMT')
                    if i > 0 and re.match(r'[ء-ي]', T[i - 1]) and re.match(r'[ء-ي]', t[0]): it['f'].append('FMT')
                    items.append(it)
json.dump(items, open(f'{SC}/audit/items.json', 'w'), ensure_ascii=False)
c = collections.Counter(f for it in items for f in set(it['f']))
print('items', len(items), 'summ', sum(1 for i in items if i['k'] == 'summ'), 'nuq', sum(1 for i in items if i['k'] == 'nuq'))
print('flags', c.most_common())
print('summ flagged (any)', sum(1 for i in items if i['k'] == 'summ' and i['f']))
