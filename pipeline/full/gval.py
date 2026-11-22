"""gval.py : validate full/gspec.txt lines  'SU:V A RECID «text»'  -> verbatim in record, author matches, sane length."""
import json, os, re, sys
SC = '/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
ws = lambda s: re.sub(r'\s+', ' ', s).strip()
_S = {}
def site(su):
    if su not in _S:
        d = json.load(open(f'{SC}/site/s{su}.json')); p = f'{SC}/site/s{su}i.json'
        inc = json.load(open(p)) if os.path.exists(p) else []
        _S[su] = (d, {r['id']: r for r in d['recs'] + inc})
    return _S[su]
bad = 0; n = 0; seen = set()
SPECF = sys.argv[1] if len(sys.argv) > 1 else SC + '/full/gspec.txt'
for ln in open(SPECF):
    ln = ln.strip()
    if not ln or ln.startswith('#'): continue
    m = re.match(r'(\d+):(\d+)\s+(IT|IQ)\s+(\d+)\s+«(.+)»\s*$', ln)
    if not m: print('PARSE', ln[:80]); bad += 1; continue
    su, v, a, rid, t = int(m[1]), int(m[2]), m[3], int(m[4]), ws(m[5]); n += 1
    d, R = site(su); r = R.get(rid)
    if not r: print('NOREC', ln[:80]); bad += 1; continue
    if d['books'][r['b']]['a'] != a: print('AUTHOR', ln[:80]); bad += 1
    if t not in ws(r['t']): print('NOTVERBATIM', su, v, a, rid, t[:70]); bad += 1
    if len(t) > 420: print('LONG', su, v, len(t), t[:60])
    if (su, v, a) in seen: print('DUP', su, v, a)
    seen.add((su, v, a))
print('gspec', n, 'bad', bad)
