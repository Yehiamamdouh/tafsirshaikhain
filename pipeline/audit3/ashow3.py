import json, re, sys, os, random
SC = '/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
src = open(SC + '/audit2/ashow2.py').read(); src = src[:src.index('hard = [')]
src = src.replace("/audit2/items.json", "/audit3/items.json").replace("json.load(open(SC + '/audit2/unreviewed.json'))", "[]")
exec(src)
RG = []
for ln in open(SC + '/audit3/ranges.txt'):
    h, note = ln.split('|', 1); h = h.split(); RG.append((h[0], int(h[1]), int(h[2]), int(h[3]), h[4], note.strip()))
def finding(x):
    for w, vol, a, b, au, note in RG:
        if x['w'] == w and x['vol'] == vol and a <= x['p'] <= b and x['a'] == au: return f"SECTION FINDING ({w} {vol}/{a}-{b}): {note}"
SW = [x for x in I if finding(x)]
swid = {x['id'] for x in SW}
R2 = [BY[i] for i in json.load(open(SC + '/audit3/round2.json')) if i not in swid]
SM = [BY[i] for i in json.load(open(SC + '/audit3/sample.json'))]
def blk(x, fnd=False):
    b = block(x)
    if fnd: b = b.replace('\nVERSE:', '\n' + finding(x) + '\nVERSE:', 1)
    return b
def write(name, L, size, fnd=False):
    n = 0
    for c in range(0, len(L), size):
        n += 1; open(f'{SC}/audit3/pk/{name}{n:02d}.txt', 'w').write('\n'.join(blk(x, fnd) for x in L[c:c + size]) + '\n')
    return n
h = [x for x in R2 if x['f']]; e = [x for x in R2 if not x['f']]
print('sweep', len(SW), write('W', SW, 80, True), '| hard', len(h), write('H', h, 110), '| easy', len(e), write('E', e, 110), '| sample', len(SM), write('R', SM, 100))
