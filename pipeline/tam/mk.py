"""tam/mk.py : build the 'تمام المعنى للباحث' review items (one per verse x imam summary group) and packets.
usage: python3 tam/mk.py pilot      -> 50 shortest + 50 random (seed 7) -> tam/pk/P01..P04
       python3 tam/mk.py all N      -> remaining items, shortest first, N per packet -> tam/pk/T001..
Writes tam/items.json (all groups, snapshot of current site/)."""
import json, os, random, sys
SC = '/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
T = SC + '/tam'
Q = json.load(open('/home/claude/tafsirshaikhain/src/data/simple.json'))
CH = json.load(open('/home/claude/tafsirshaikhain/src/data/chapters.json'))
def sname(su): return CH['chapters'][su - 1]['name']
def qv(su, v):
    x = Q[str(su)]; x = x.get(str(v), '') if isinstance(x, dict) else x[v - 1]
    return x['text'] if isinstance(x, dict) else x
items = {}
for su in range(1, 115):
    d = json.load(open(f'{SC}/site/s{su}.json')); p = f'{SC}/site/s{su}i.json'
    inc = json.load(open(p)) if os.path.exists(p) else []
    R = {r['id']: r for r in d['recs'] + inc}
    B = {b['id']: b for b in d['books']}
    for a, x in d.get('summ', {}).items():
        for v, L in x.items():
            iid = f't{su}:{v}:{a}'
            ents, recs = [], {}
            for e in L:
                r = R.get(e['r']); b = B.get(e['b'], {})
                ents.append({'t': e['t'], 'cx': e.get('cx', ''), 'r': e['r'], 'w': b.get('w', ''), 'bt': b.get('t', ''), 'vp': f"{e.get('v')}/{e.get('p')}"})
                if r and e['r'] not in recs:
                    recs[e['r']] = {'t': r['t'], 'bt': b.get('t', ''), 'vp': f"{r.get('v')}/{r.get('p')}-{r.get('pe', r.get('p'))}", 'h': r.get('h', '')}
            items[iid] = {'su': su, 'v': int(v), 'a': a, 'ents': ents, 'recs': recs, 'len': sum(len(e['t']) for e in ents)}
json.dump(items, open(T + '/items.json', 'w'), ensure_ascii=False)
IM = {'IT': 'ابن تيمية', 'IQ': 'ابن القيم'}
def block(iid):
    it = items[iid]; su, v = it['su'], it['v']
    o = [f'### {iid} — {sname(su)} {v} — {IM[it["a"]]}', f'الآية: {qv(su, v)}', f'المختصر ({len(it["ents"])} جملة):']
    for i, e in enumerate(it['ents'], 1):
        o.append(f'  [{i}] rec{e["r"]} ({e["bt"]} {e["vp"]}): «{e["t"]}»' + (f'   [سطر سياق: {e["cx"]}]' if e['cx'] else ''))
    for rid, r in it['recs'].items():
        o.append(f'النص الكامل rec{rid} ({r["bt"]} {r["vp"]}){" — " + r["h"] if r["h"] else ""}:')
        o.append(r['t'])
    return '\n'.join(o) + '\n'
os.makedirs(T + '/pk', exist_ok=True)
if sys.argv[1] == 'pilot':
    ids = sorted(items, key=lambda k: items[k]['len'])
    short = ids[:50]; random.seed(7); rnd = random.sample(ids[50:], 50)
    sel = []
    for i in range(50): sel += [short[i], rnd[i]]
    json.dump(sel, open(T + '/pilot_ids.json', 'w'))
    for k in range(4):
        part = sel[k * 25:(k + 1) * 25]
        open(f'{T}/pk/P{k + 1:02d}.txt', 'w').write('\n'.join(block(i) for i in part))
    print('pilot', len(sel), 'shortest len', items[short[0]]['len'], items[short[-1]]['len'])
else:
    n = int(sys.argv[2]); done = set(json.load(open(T + '/pilot_ids.json')))
    ids = [k for k in sorted(items, key=lambda k: items[k]['len']) if k not in done]
    for k in range(0, len(ids), n):
        open(f'{T}/pk/T{k // n + 1:03d}.txt', 'w').write('\n'.join(block(i) for i in ids[k:k + n]))
    print('packets', (len(ids) + n - 1) // n, 'items', len(ids))
print('items', len(items))
