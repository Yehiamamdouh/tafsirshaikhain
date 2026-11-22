"""fanafilter.py [--dry] : remove every summ/nuq entry (from batchN.json) whose text comes from the fana' al-nar debate sections
(user decision 2026-10-27: «شيل موضوع فناء النار»):
  ShifaCalil paragraphs 513-530 (1/252-265), HadiArwah paragraphs 1311-1374 (1/348-388), RaddCalaManQalaBiFanaJanna (whole book)."""
import json, os, re, sys, pickle
SC = '/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
DRY = '--dry' in sys.argv
ws = lambda s: re.sub(r'\s+', ' ', s).strip()
RANGES = {'ShifaCalil': (513, 530), 'HadiArwah': (1311, 1374), 'RaddCalaManQalaBiFanaJanna': (0, 10 ** 9)}
ZONE = {}
for w, (a, b) in RANGES.items():
    raw = pickle.load(open(f'{SC}/out/cache/{w}.pkl', 'rb'))['paras']
    ZONE[w] = ' ‖ '.join(ws(p['text']) for p in raw[a:b + 1])
def bad(work, t):
    z = ZONE.get(work)
    return z is not None and ws(t) in z
tot = 0
for su in range(1, 115):
    bp = f'{SC}/batch{su}.json'
    if not os.path.exists(bp): continue
    B = json.load(open(bp)); ch = 0
    for kind in ('summ', 'nuq'):
        for a, vs in B.get(kind, {}).items():
            for v in list(vs):
                keep = []
                for e in vs[v]:
                    w, t = (e[0], e[1]) if kind == 'summ' else (e.get('w'), e['t'])
                    if bad(w, t) or (kind == 'nuq' and e.get('rt') and bad(e.get('rw', w), e['rt'])):
                        print('REMOVE', su, v, kind, a, w, '|', ws(t)[:90]); ch += 1
                    else: keep.append(e)
                if keep: vs[v] = keep
                else: del vs[v]
    tot += ch
    if ch and not DRY: json.dump(B, open(bp, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('removed', tot)
