"""wsweep.py CLASS [PREFIX] : build section-sweep packets audit/pk/{PREFIX}NN.txt for every item (summ+nuq) inside the
page ranges of audit/sweep_ranges.txt with that CLASS. Each block shows the section finding and earlier decisions.
Sweep decisions (audit/out/W*.txt) override S/N/R decisions for the same ID (see apply_audit.py)."""
import json, re, sys, glob, collections
SC = '/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
src = open(SC + '/audit/ashow.py').read(); src = src[:src.index('RISK = ')]
exec(src)   # helpers only (ctx, block_S, block_N, head ...); does not touch packets
CLS = sys.argv[1]; PFX = sys.argv[2] if len(sys.argv) > 2 else 'W'
dec = collections.defaultdict(list)
for f in sorted(glob.glob(SC + '/audit/out/*.txt')):
    for ln in open(f):
        p = [x.strip() for x in ln.rstrip('\n').split('|')]
        if len(p) > 1 and re.match(r'^[sn]\d+:\d+:(IT|IQ):\d+$', p[0]): dec[p[0]].append(f"{f.split('/')[-1][:-4]}: {' | '.join(p[1:])[:300]}")
blocks = []; seen = set()
for ln in open(SC + '/audit/sweep_ranges.txt'):
    if ln.startswith('#') or not ln.strip(): continue
    h, note = ln.split('|', 1); h = h.split(); w, vol, p1, p2, a, cl = h[0], int(h[1]), int(h[2]), int(h[3]), h[4], h[5]
    if cl != CLS: continue
    for it in I:
        if it['w'] == w and it['vol'] == vol and p1 <= it['p'] <= p2 and it['a'] == a and it['id'] not in seen:
            seen.add(it['id'])
            b = (block_S(it) if it['k'] == 'summ' else block_N(it)).split('\n')
            b.insert(1, f"SECTION FINDING ({w} {vol}/{p1}-{p2}): {note.strip()}")
            for d in dec.get(it['id'], []): b.insert(2, f"EARLIER DECISION ({d})")
            blocks.append('\n'.join(b))
size = 80; n = 0
for c in range(0, len(blocks), size):
    n += 1; open(f'{SC}/audit/pk/{PFX}{n:02d}.txt', 'w').write('\n'.join(blocks[c:c + size]) + '\n')
print(CLS, 'items', len(blocks), 'packets', n)
