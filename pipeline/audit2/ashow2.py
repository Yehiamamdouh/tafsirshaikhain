"""ashow2.py : packets for the full pass (audit2/unreviewed.json) with excerpt + full-passage context."""
import json, re, sys, os
SC = '/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
src = open(SC + '/audit/ashow.py').read(); src = src[:src.index('RISK = ')]
exec(src)
I = json.load(open(SC + '/audit2/items.json')); BY = {x['id']: x for x in I}
U = [BY[i] for i in json.load(open(SC + '/audit2/unreviewed.json'))]
def block(it):
    d, R = site(it['su']); r = R[it['r']]; T = ws(r['t']); pre, post, vt, k = ctx(it, nb=1)
    pp = paras(it['w']); prevp = nextp = ''
    if pp and k is not None:
        raw, P, first = pp
        prevp = P[k - 1][-250:] if k > 0 else ''
        nlen = len(T); j = k; acc = len(P[k])
        while acc < nlen - 5 and j + 1 < len(P): j += 1; acc += len(P[j]) + 1
        nextp = P[j + 1][:250] if j + 1 < len(P) else ''
    return '\n'.join([head(it), f"VERSE: {re.sub(r'[ً-ْٰۖ-ۭ]', '', vt)}",
        f"PASSAGE START: {T[:220]}", f"PASSAGE END: …{T[-220:]}",
        f"BOOK BEFORE PASSAGE: …{prevp}", f"BOOK AFTER PASSAGE: {nextp}…",
        f"BEFORE EXCERPT: …{(T[:T.find(it['t'])] if T.find(it['t']) > 0 else '')[-500:]}",
        f"EXCERPT: «{it['t']}»", f"AFTER EXCERPT: {T[T.find(it['t']) + len(it['t']):][:400] if T.find(it['t']) >= 0 else ''}"])
hard = [x for x in U if x['f']]; easy = [x for x in U if not x['f']]
def write(name, L, size):
    n = 0
    for c in range(0, len(L), size):
        n += 1; open(f'{SC}/audit2/pk/{name}{n:02d}.txt', 'w').write('\n'.join(block(x) for x in L[c:c + size]) + '\n')
    return n
print('hard', len(hard), 'packets', write('H', hard, 90), '| easy', len(easy), 'packets', write('E', easy, 110))
