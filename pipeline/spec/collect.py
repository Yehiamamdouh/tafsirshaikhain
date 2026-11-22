"""spec/collect.py : gather every open '?' item from all review rounds, map to the CURRENT site, drop the ones
whose text no longer exists on the site (already fixed/replaced), and bucket the rest by question type."""
import json, re, glob, os, collections
SC = '/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
ws = lambda s: re.sub(r'\s+', ' ', s).strip()
# current site
site = {}
for su in range(1, 115):
    d = json.load(open(f'{SC}/site/s{su}.json'))
    for a, x in d.get('summ', {}).items():
        for v, L in x.items():
            for i, e in enumerate(L): site[('s', su, int(v), a, i)] = ws(e['t'])
    for a, x in d.get('nuq', {}).items():
        for v, L in x.items():
            for i, e in enumerate(L): site[('n', su, int(v), a, i)] = ws(e['t'])
bytext = collections.defaultdict(list)
for k, t in site.items(): bytext[t].append(k)
# snapshots (items.json) per audit dir give the text that was reviewed
snap = {}
for d in ('audit2', 'audit3', 'audit4'):
    p = f'{SC}/{d}/items.json'
    if os.path.exists(p):
        J = json.load(open(p))
        for it in (J if isinstance(J, list) else J.values()):
            snap[(d, it.get('id'))] = ws(it.get('t', ''))
rows = []
for d in ('audit', 'audit2', 'audit3', 'audit4'):
    for f in sorted(glob.glob(f'{SC}/{d}/out/*.txt')):
        for ln in open(f):
            if '?' not in ln: continue
            p = [x.strip() for x in ln.rstrip('\n').split(' | ')]
            if len(p) < 3: continue
            m = re.match(r'([sn])(\d+):(\d+):(IT|IQ):(\d+)', p[0])
            if not m: continue
            kind, su, v, a, i = m[1], int(m[2]), int(m[3]), m[4], int(m[5])
            t = snap.get((d, p[0]), '')
            q = ' | '.join(p[2:]) if p[1] in ('KEEP', 'TRIM', 'DROP', 'NUQ', 'MOVE', 'CTX', 'FULL') else ' | '.join(p[1:])
            rows.append(dict(src=d, id=p[0], kind=kind, su=su, v=v, a=a, t=t, q=q))
for ln in open(f'{SC}/tam/specialist.txt'):
    p = [x.strip() for x in ln.split(' | ', 1)]
    m = re.match(r't(\d+):(\d+):(IT|IQ)', p[0])
    if m: rows.append(dict(src='tam', id=p[0], kind='s', su=int(m[1]), v=int(m[2]), a=m[3], t='', q=p[1] if len(p) > 1 else ''))
# status on the current site
alive = []
for r in rows:
    same = [k for k in bytext.get(r['t'], []) if k[0] == r['kind'] and k[3] == r['a']] if r['t'] else None
    group = [k for k in site if k[0] == r['kind'] and k[1] == r['su'] and k[2] == r['v'] and k[3] == r['a']]
    if r['t'] and not same: r['status'] = 'text-gone'
    elif not group: r['status'] = 'verse-gone'
    else: r['status'] = 'alive'; alive.append(r)
# buckets
def bucket(q):
    s = q.lower()
    if re.search(r'suhayl|السهيلي', s): return 'A-suhayli'
    if re.search(r'fana|فناء|النار', s): return 'B-fana'
    if re.search(r'typo|edition|طبع|corrupt|garbled|missing word|dropped', s): return 'C-edition'
    if re.search(r'no (book )?cache|not in cache|ashkal|cache', s): return 'D-nocache'
    if re.search(r'speaker|voice|قائل|quot|narrat|قال |يعني:|mufassir|reported', s): return 'E-speaker'
    if re.search(r'full|paragraph|beyond|ends? (on|mid|at)|cut off|truncat|passage (ends|stops|starts)', s): return 'F-passage'
    if re.search(r'only (one|an) (item|example)|list of|among (several|examples)|example of|cited as|proof', s): return 'G-weaklink'
    if re.search(r'readable|clear|fine|ok\b|acceptable|stands', s): return 'H-reviewer-ok'
    return 'Z-other'
for r in alive: r['b'] = bucket(r['q'])
c = collections.Counter(r['status'] for r in rows); print('total', len(rows), dict(c))
print(collections.Counter(r['b'] for r in alive))
json.dump(alive, open(f'{SC}/spec/alive.json', 'w'), ensure_ascii=False, indent=0)
