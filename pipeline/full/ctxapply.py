"""ctxapply.py : attach owner-DEC2 context lines (full/ctx_audit.txt) to summ entries in batchN.json.
Line:  SU IT|IQ «excerpt text» => «context line»   (matched by surah + imam + exact text, any verse)
The entry [work, text] becomes [work, text, ctx]; attach.py carries it to the site as 'cx'."""
import json, os, re, sys
SC = '/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
ws = lambda s: re.sub(r'\s+', ' ', s).strip()
n = miss = 0; B = {}
for p in (sys.argv[1:] or [SC + '/full/ctx_audit.txt', SC + '/gap2/ctx_gap2.txt']):
    if not os.path.exists(p): continue
    for ln in open(p):
        m = re.match(r'(\d+)\s+(IT|IQ)\s+«(.+?)»\s*=>\s*«(.+)»\s*$', ln.strip())
        if not m: continue
        su, a, t, cx = int(m[1]), m[2], ws(m[3]), ws(m[4]); bp = f'{SC}/batch{su}.json'
        if su not in B: B[su] = json.load(open(bp))
        hit = False
        for v, L in B[su].get('summ', {}).get(a, {}).items():
            for e in L:
                if ws(e[1]) == t:
                    hit = True
                    if len(e) > 2: e[2] = cx
                    else: e.append(cx)
        if hit: n += 1
        else: miss += 1; print('CTXMISS', ln.strip()[:90])
for su, d in B.items(): json.dump(d, open(f'{SC}/batch{su}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('ctx applied', n, 'missed', miss)
