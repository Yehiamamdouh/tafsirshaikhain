"""rtfix.py : apply rejoinder fixes from full/rtfix.txt to batchN.json nuq entries.
Line: SU:V IMAM «quote text» => «new rejoinder» | -   (- removes the rejoinder)"""
import json, os, re
SC = '/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
ws = lambda s: re.sub(r'\s+', ' ', s).strip()
p = SC + '/full/rtfix.txt'; n = miss = 0
if os.path.exists(p):
    for ln in open(p):
        m = re.match(r'(\d+):(\d+)\s+(IT|IQ)\s+«(.+?)»\s*=>\s*(-|«(.+)»)\s*$', ln.strip())
        if not m: continue
        su, v, a, t, new = int(m[1]), m[2], m[3], ws(m[4]), (ws(m[6]) if m[6] else None)
        bp = f'{SC}/batch{su}.json'; B = json.load(open(bp)); hit = False
        for e in B.get('nuq', {}).get(a, {}).get(v, []):
            if ws(e['t']) == t:
                hit = True
                if new: e['rt'] = new
                else: e.pop('rt', None); e.pop('rw', None)
        if hit: json.dump(B, open(bp, 'w', encoding='utf-8'), ensure_ascii=False, indent=0); n += 1
        else: miss += 1; print('RTMISS', ln.strip()[:80])
print('rtfix applied', n, 'missed', miss)
