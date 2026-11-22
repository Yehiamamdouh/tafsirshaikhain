"""fnd.py N AUTHOR WIDTH phrase... : print text around each phrase in site/s{N}.json (+i) records of AUTHOR."""
import json, sys, re
S = '/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
n, a, w = sys.argv[1], sys.argv[2], int(sys.argv[3])
d = json.load(open(S+'/site/s%s.json' % n)); B = d['books']; R = d['recs']
try: R = R + json.load(open(S+'/site/s%si.json' % n))['recs']
except Exception: pass
ws = lambda s: re.sub(r'\s+', ' ', s)
for ph in sys.argv[4:]:
    k = 0
    for r in R:
        if B[r['b']]['a'] != a: continue
        t = ws(r['t']); i = t.find(ph)
        if i < 0: continue
        print('## [%s] %s %s/%s #%s:' % (ph[:20], B[r['b']]['w'], r['v'], r['p'], r['id']), t[max(0, i - w//3):i + w]); print()
        k += 1
        if k >= 2: break
    if not k: print('## NONE', ph)
