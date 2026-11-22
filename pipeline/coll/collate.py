"""collate.py : collation of the site against printed compilations.
For every compilation (OCR or digital text) find the corpus paragraphs it contains (5-gram overlap), then every
verse those paragraphs are linked to (site records' 'ay') where the paragraph's imam has NO summ/nuq on the site
(after pending gap specs) -> candidate gap.  Output: coll/cand_<comp>.json  + summary."""
import json, os, re, sys, glob, pickle, zlib, collections
SC = '/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
sys.path.insert(0, SC + '/scripts')
from parse import norm
N = 5
def words(t):
    t = norm(t); t = re.sub(r'[^ء-ي ]', ' ', t)
    return [w for w in t.split() if len(w) > 1]
def grams(ws): return [zlib.crc32(' '.join(ws[i:i + N]).encode()) for i in range(len(ws) - N + 1)]
ws_ = lambda s: re.sub(r'\s+', ' ', s).strip()

def comp_paras(name):
    """list of (loc, text) paragraphs of a compilation"""
    out = []
    if os.path.isdir(f'{SC}/books/{name}'):
        for f in sorted(glob.glob(f'{SC}/books/{name}/*.txt')):
            pg = int(f[-8:-4])
            for k, para in enumerate(re.split(r'\n\s*\n', open(f).read())):
                out.append((f'p{pg}', para))
    else:
        path = {'daqaiq_sh': SC + '/coll/src/IT.DaqaiqTafsir.Shamela0005487-ara1',
                'hilal': SC + '/coll/src/IQ.TafsirQuran.Shamela0023606-ara1'}[name]
        T = open(path, encoding='utf-8').read().split('#META#Header#End#', 1)[1]
        pg = '?'
        for para in re.split(r'\n# ', T):
            m = re.search(r'PageV(\d+)P(\d+)', para)
            if m: pg = f'{int(m[1])}/{int(m[2])}'
            para = re.sub(r'PageV\d+P\d+|ms\d+|~~|###? ?\|?', ' ', para)
            out.append((pg, para))
    return out

COMPS = {k: v for k, v in {'daqaiqT1': 'IT', 'daqaiqT2': 'IT', 'daqaiqT3': 'IT', 'qaysi': 'IT', 'badaic5': 'IQ', 'badaic2': 'IQ', 'badaic3': 'IQ', 'hilal': 'IQ'}.items()
         if k in ('daqaiq_sh', 'hilal') or os.path.isdir(f'{SC}/books/{k}')}
ONLY_C = os.environ.get('COMPS'); COMPS = {k: v for k, v in COMPS.items() if not ONLY_C or k in ONLY_C.split(',')}
# ---- compilation gram sets
CG = {}
for c in COMPS:
    s = set()
    for loc, t in comp_paras(c): s.update(grams(words(t)))
    CG[c] = s
    print(c, 'grams', len(s), file=sys.stderr)
# ---- site: books -> imam, records by first-80 chars, coverage
IMAM = {}; RECS = collections.defaultdict(list); COV = set()
for su in range(1, 115):
    d = json.load(open(f'{SC}/site/s{su}.json')); p = f'{SC}/site/s{su}i.json'
    inc = json.load(open(p)) if os.path.exists(p) else []
    for b in d['books']: IMAM[b['w']] = b['a']
    for r in d['recs'] + inc:
        RECS[(d['books'][r['b']]['w'], ws_(r['t'])[:80])].append((su, r['id'], r.get('ay', []), len(r.get('ay', []))))
    for k in ('summ', 'nuq'):
        for a, vs in d.get(k, {}).items():
            for v in vs: COV.add((a, su, int(v)))
for f in glob.glob(SC + '/full/gspec*.txt') + glob.glob(SC + '/coll/cspec*.txt'):
    for ln in open(f):
        m = re.match(r'(\d+):(\d+)\s+(IT|IQ)\s', ln)
        if m: COV.add((m[3], int(m[1]), int(m[2])))
# ---- scan corpus paragraphs
TH = float(os.environ.get('TH', '0.35'))
res = {c: [] for c in COMPS}
for pk in sorted(glob.glob(SC + '/out/cache/*.pkl')):
    w = os.path.basename(pk)[:-4]; a = IMAM.get(w)
    if not a: continue
    P = pickle.load(open(pk, 'rb'))['paras']
    for i, p in enumerate(P):
        t = ws_(p['text']); g = grams(words(t))
        if len(g) < 8: continue
        for c, ca in COMPS.items():
            if ca != a: continue
            G = CG[c]; h = sum(1 for x in g if x in G) / len(g)
            if h >= TH: res[c].append((w, i, round(h, 2), len(g), t[:80]))
# ---- candidates
summary = {}
for c in COMPS:
    a = COMPS[c]; cand = collections.defaultdict(list); nrec = 0; norec = 0; verses = set()
    for w, i, h, n, key in res[c]:
        rs = RECS.get((w, key))
        if not rs: norec += 1; continue
        nrec += 1
        for su, rid, ay, nay in rs:
            for v in ay:
                verses.add((su, v))
                if (a, su, v) not in COV: cand[f'{su}:{v}'].append([rid, w, i, h, nay])
    json.dump(cand, open(f'{SC}/coll/cand_{c}.json', 'w'), ensure_ascii=False)
    summary[c] = dict(paras_in_comp=len(res[c]), with_rec=nrec, no_rec=norec, verses_linked=len(verses),
                      verses_gap=len(cand), verses_gap_singlecite=sum(1 for k, L in cand.items() if any(x[4] <= 3 for x in L)))
    json.dump(res[c], open(f'{SC}/coll/paras_{c}.json', 'w'), ensure_ascii=False)
print(json.dumps(summary, ensure_ascii=False, indent=1))
