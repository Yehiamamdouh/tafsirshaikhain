"""gap2/mk.py : packets for verses that have imam passages but no summary. Per verse: top 3 records (by explanation
markers right after the verse citation), each shown as a window around the citation."""
import json, os, re, collections
SC = '/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
ws = lambda s: re.sub(r'\s+', ' ', s).strip()
DIA = re.compile('[ً-ْٰـۖ-ۭ]')
def norm_map(t):
    out, idx = [], []
    for i, ch in enumerate(t):
        if DIA.match(ch): continue
        c = {'أ': 'ا', 'إ': 'ا', 'آ': 'ا', 'ٱ': 'ا', 'ى': 'ي', 'ة': 'ه'}.get(ch, ch)
        out.append(c); idx.append(i)
    return ''.join(out), idx
MARK = re.compile(r'أي |يعني|معناه|المراد|فأخبر|أخبر|فدل|دل على|ففيه|وهذا|فبين|بين أن|قال تعالى|كما قال')
blocks = []
for su in range(1, 115):
    d = json.load(open(f'{SC}/site/s{su}.json')); p = f'{SC}/site/s{su}i.json'; inc = json.load(open(p)) if os.path.exists(p) else []
    B = d['books']; have = {int(v) for a in ('IT', 'IQ') for v in d.get('summ', {}).get(a, {})}
    by = collections.defaultdict(list)
    for r in d['recs'] + inc:
        for v in r.get('ay', []):
            if v not in have and 1 <= v <= len(d['verses']): by[v].append(r)
    for v in sorted(by):
        vt = d['verses'][v - 1]; vn, _ = norm_map(ws(vt)); key = ' '.join(vn.split()[:4])
        cands = []
        for r in by[v]:
            T = ws(r['t']); tn, mp = norm_map(T); j = tn.find(key) if key else -1
            if j < 0: j = tn.find(' '.join(vn.split()[:2])) if len(vn.split()) > 1 else -1
            pos = mp[j] if j >= 0 else 0
            win_after = T[pos:pos + 700]
            score = len(MARK.findall(win_after)) * 2 - win_after.count('{') + (3 if j >= 0 else 0) + (2 if r.get('c') else 0)
            cands.append((score, r, pos, T))
        cands.sort(key=lambda x: -x[0])
        lines = [f"\n### {su}:{v}  VERSE: {DIA.sub('', vt)}"]
        for score, r, pos, T in cands[:3]:
            bk = B[r['b']]; a, b0 = max(0, pos - 350), pos + 750
            lines.append(f"-- {bk['a']} rec{r['id']} {bk['w']} {r['v']}/{r['p']}  ({len(by[v])} passages for this verse; score {score})\n" + ('…' if a else '') + T[a:b0] + ('…' if b0 < len(T) else ''))
        blocks.append('\n'.join(lines))
size, n, cur, cl = 90000, 0, [], 0
def flush():
    global n, cur, cl
    if cur: n += 1; open(f'{SC}/gap2/pk/G{n:02d}.txt', 'w').write('\n'.join(cur) + '\n'); cur, cl = [], 0
for b in blocks:
    cur.append(b); cl += len(b)
    if cl > size: flush()
flush()
print('verses', len(blocks), 'packets', n)
