"""gvoice.py [spec files] : flag gap lines whose excerpt follows an attribution to someone else («قال الشافعي:», «قالوا:», «قالت الفقراء»)
in the same record or the 3 previous paragraphs, with no closing marker (انتهى / قلت / والمقصود) after it."""
import json, os, re, sys, glob, pickle, collections
SC = '/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
ws = lambda s: re.sub(r'\s+', ' ', s).strip()
files = sys.argv[1:] or sorted(glob.glob(SC + '/full/gspec*.txt'))
SKIP = r'(?:تعالى|الله|سبحانه|النبي|رسول|صلى|عز|ربك|ربنا|لهم|له|لنبيه|لي|موسى|إبراهيم|عيسى|نوح|يوسف|في|فيه|فيها|بعد|قبل|ذلك|هذا|هنا|شيخنا|شيخ الإسلام)'
ATT = re.compile(r'(?:^|[\s.،؛:])((?:و|ف)?(?:قال|قالت|قالوا|يقول|حكى|ذكر|نقل|روى)\s+(?!' + SKIP + r'\b)[^\s:،.]{2,}(?:\s+[^\s:،.]{2,}){0,5}?\s*:|(?:و|ف)?قالوا\s*:|قالت\s+(?:الفقراء|الأغنياء|طائفة|الجهمية|المعتزلة)|قال\s+(?:الموجبون|المانعون|المجوزون|الآخرون|المنازع|المعترض))')
CLOSE = re.compile(r'انتهى|قلت\s*:|قلت\b|والمقصود|اهـ|هذا لفظه|هذا كلامه|انتهى كلامه|والجواب|فيقال|قيل له')
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
_S = {}
def site(su):
    if su not in _S:
        d = json.load(open(f'{SC}/site/s{su}.json')); p = f'{SC}/site/s{su}i.json'
        inc = json.load(open(p)) if os.path.exists(p) else []
        _S[su] = (d, {r['id']: r for r in d['recs'] + inc})
    return _S[su]
n = 0
for f in files:
    for ln in open(f):
        m = re.match(r'(\d+):(\d+)\s+(IT|IQ)\s+(\d+)(?:\+(\d))?\s+«(.+)»\s*$', ln.strip())
        if not m: continue
        su, v, a, rid, K, t = int(m[1]), int(m[2]), m[3], int(m[4]), int(m[5] or 0), ws(m[6])
        d, R = site(su); r = R[rid]; w = d['books'][r['b']]['w']; T = ws(r['t'])
        if K:
            pp0 = paras(w)
            if pp0:
                k0 = pp0[1].get(T[:80], [None])[0]
                if k0 is not None: T = ' '.join(pp0[0][k0:k0 + K + 1])
        i = T.find(t)
        pre = T[:i]; pp = paras(w)
        if pp:
            P, first = pp; ks = first.get(T[:80], [])
            if ks: pre = ' ‖ '.join(P[max(0, ks[0] - 3):ks[0]] + [pre])
        last = None
        for mm in ATT.finditer(pre): last = mm
        if not last: continue
        after = pre[last.end():]
        if CLOSE.search(after): continue
        if re.match(r'\s*[{﴿]', after): continue          # attribution introduces a verse quote
        if re.match(r'\s*(?:قال|قالت|قالوا|وقال|فقال|يقول)\s+(?:فرعون|موسى|إبراهيم|نوح|لوط|يوسف|يعقوب|الملائكة|لموسى|لأبيه|لأهله|عن|في|فى|لسارة|للملائكة|إخوة)', last.group(1)): continue
        n += 1
        print(f'\n[{n}] {os.path.basename(f)} | {su}:{v} {a} {rid} {w} {r["v"]}/{r["p"]} | ATT «{last.group(1)}» +{len(after)}ch')
        print('   AFTER-ATT:', after[:220].replace('\n',' '))
        if len(after) > 440: print('   ...BEFORE-EXC:', after[-220:])
        print('   EXC:', t[:160])
print('flagged', n)
