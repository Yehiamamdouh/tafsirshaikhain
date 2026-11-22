"""g2conv.py : gap2/out/*.txt -> full/gspec_gap2.txt (+ gap2/ctx_gap2.txt CTX lines, gap2/flags.txt review list).
Skips ids listed in gap2/drop.txt (lines 'SU:V IMAM recN'). CTX overrides in gap2/ctx_ar.txt ('SU:V IMAM recN => «arabic»')."""
import re, glob, os, json
SC = '/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
G = SC + '/gap2'
ws = lambda s: re.sub(r'\s+', ' ', s).strip()
AR = re.compile(r'[؀-ۿ]')
drop = set(ws(l) for l in open(G + '/drop.txt')) if os.path.exists(G + '/drop.txt') else set()
ctxo = {}
if os.path.exists(G + '/ctx_ar.txt'):
    for l in open(G + '/ctx_ar.txt'):
        if '=>' in l:
            k, c = l.split('=>', 1); ctxo[ws(k)] = c.strip().strip('«»')
_S = {}
def recs(su):
    if su not in _S:
        d = json.load(open(f'{SC}/site/s{su}.json')); p = f'{SC}/site/s{su}i.json'
        inc = json.load(open(p)) if os.path.exists(p) else []
        _S[su] = (d, {r['id']: r for r in d['recs'] + inc})
    return _S[su]
spec, ctx, flags, bad = [], [], [], []
seen = set()
FLAG = re.compile(r'weak|borderline|near-duplicate|keep one|typo|athar|decision|review|drop', re.I)
for f in sorted(glob.glob(G + '/out/G*.txt')):
    for ln in open(f):
        ln = ln.rstrip('\n')
        m = re.match(r'\s*(\d+):(\d+)\s*\|\s*(IT|IQ)\s*\|\s*(?:rec)?(\d+)\s*\|\s*«', ln)
        if not m: continue
        su, v, a, rid = int(m[1]), int(m[2]), m[3], int(m[4])
        rest = ln[m.end():]
        j = rest.find('» |')
        if j < 0: j = rest.rfind('»')
        t, reason = ws(rest[:j]), rest[j + 3:].strip()
        key = f'{su}:{v} {a} rec{rid}'
        if key in drop: continue
        d, R = recs(su); r = R.get(rid)
        if not (r and d['books'][r['b']]['a'] == a and t in ws(r['t'])):
            bad.append(f'{os.path.basename(f)} {key} NOTVERBATIM'); continue
        if (su, v, a, t) in seen: continue
        seen.add((su, v, a, t))
        spec.append(f'{su}:{v} {a} {rid} «{t}»')
        cm = re.search(r'CTX\s*[«"]([^»"]+)[»"]', reason)
        c = ctxo.get(key) or (cm[1] if cm else None)
        if c:
            if AR.search(c) and not re.search(r'[A-Za-z]{3}', c): ctx.append(f'{su} {a} «{t}» => «{ws(c)}»')
            else: flags.append(f'CTX-EN {key} | {c}')
        if FLAG.search(reason): flags.append(f'FLAG {key} | {reason[:220]}')
open(SC + '/full/gspec_gap2.txt', 'w').write('# gap2 extraction (verses with imam passages but no summary)\n' + '\n'.join(spec) + '\n')
open(G + '/ctx_gap2.txt', 'w').write('\n'.join(ctx) + '\n')
open(G + '/flags.txt', 'w').write('\n'.join(flags + bad) + '\n')
vv = {l.split()[0] for l in spec}
print('spec', len(spec), 'verses', len(vv), 'ctx', len(ctx), 'flags', len(flags), 'bad', len(bad))
for b in bad: print(b)
