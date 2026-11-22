"""apply_audit.py [--dry] : turn reviewer decisions (audit/out/*.txt) into pipeline inputs.
Uses the snapshot audit/items.json (what each audit ID pointed to) and finds each item's origin:
  - a gap/collation spec line (full/gspec*.txt, coll/cspec*.txt)  -> edited in place (commented out / text or verse changed)
  - an original reviewed item n (full/items.json, possibly X-modified) -> decisions in full/dec_audit.txt
New lines go to full/gspec_audit.txt (summ) and full/nspec_audit.txt (nuq). Prints a report; re-runnable."""
import json, os, re, sys, glob, collections
SC = '/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
DRY = '--dry' in sys.argv
ws = lambda s: re.sub(r'\s+', ' ', s).strip()
SNAP = {it['id']: it for it in json.load(open(SC + '/audit/items.json'))}
ITEMS = json.load(open(SC + '/full/items.json'))
XN = {int(k): v for k, v in json.load(open(SC + '/full/xnew.json')).items()}
# ---- decisions
DEC = collections.defaultdict(list)
for f in sorted(glob.glob(SC + '/audit/out/*.txt')) + [SC + '/audit/manual.txt']:
    if not os.path.exists(f): continue
    for ln in open(f):
        p = [x.strip() for x in ln.rstrip('\n').split('|')]
        if len(p) < 2 or not re.match(r'^[sn]\d+:\d+:(IT|IQ):\d+$', p[0]): continue
        DEC[p[0]].append((p[1].upper(), p[2:], os.path.basename(f)))
# sweep packets (audit/out/W*.txt) were written with the section-level finding in view: they override S/N/R decisions
for k in list(DEC):
    if any(src[0] in 'WXYZ' for _, _, src in DEC[k]):
        DEC[k] = [d for d in DEC[k] if d[2][0] in 'WXYZ' or d[2] == 'manual.txt']
# a stance / speaker fix on an item that is also re-created (TRIM, cross-surah MOVE) must reach the new line
OV_ST = {k: d[1][0] for k, L in DEC.items() for d in L if d[0] == 'ST' and d[1]}
OV_WHO = {k: d[1][0] for k, L in DEC.items() for d in L if d[0] == 'WHO' and d[1]}
# ---- spec line index
SPEC = {}
specfiles = sorted(glob.glob(SC + '/full/gspec*.txt')) + sorted(glob.glob(SC + '/coll/cspec*.txt'))
specfiles = [f for f in specfiles if not f.endswith('gspec_audit.txt') and not f.endswith('cspec_zaudit.txt')]
# always start from the pre-audit snapshot (audit/spec_pre/...) so the script is re-runnable
def _pre(f):
    q = f.replace(SC + '/', SC + '/audit/spec_pre/'); return q if os.path.exists(q) else f
LINES = {f: open(_pre(f)).read().split('\n') for f in specfiles}
for f, L in LINES.items():
    for i, ln in enumerate(L):
        m = re.match(r'(\d+):(\d+)\s+(IT|IQ)\s+(\d+)(\+\d)?\s+«(.+)»\s*$', ln)
        if m: SPEC[(int(m[1]), int(m[2]), m[3], ws(m[6]))] = (f, i, int(m[4]), m[5] or '')
def q1(args):   # the quoted text is the first field, wrapped in «...» (it may itself contain «»)
    a0 = args[0].strip() if args else ''
    return re.match(r'^«(.*)»$', a0)
def cur_text(it):
    n = int(it['n']); return ws(XN[n]['t']) if n in XN and XN[n].get('t') else ws(it['t'])
EX = collections.defaultdict(list)
for it in ITEMS: EX[(int(it['su']), int(it['v']), it['a'])].append(it)
def origin(s):
    key = (s['su'], s['v'], s['a'], s['t'])
    if key in SPEC: return ('spec', SPEC[key])
    cands = EX.get((s['su'], s['v'], s['a']), [])
    ex = [it for it in cands if cur_text(it) == s['t']] or [it for it in cands if cur_text(it)[:40] in s['t'] or s['t'][:40] in cur_text(it)]
    if ex: return ('item', int(ex[0]['n']))
    # moved items (M) keep their original verse in items.json
    allc = [it for it in ITEMS if int(it['su']) == s['su'] and it['a'] == s['a'] and cur_text(it) == s['t']]
    if allc: return ('item', int(allc[0]['n']))
    return (None, None)
dec_lines, gnew, nnew, cnew, report = [], [], [], [], collections.Counter()
problems = []
def comment(f, i, tag):
    if not LINES[f][i].startswith('#'): LINES[f][i] = f'# audit-{tag}: ' + LINES[f][i]
rtfix = []; ctxl = []
for aid, act, args, src in [(k, *d) for k, L in DEC.items() for d in L]:
    if act in ('KEEP', 'OK'): report['KEEP'] += 1; continue
    s = SNAP.get(aid)
    if not s: problems.append(('NOSNAP', aid)); continue
    kind, o = origin(s)
    if kind is None: problems.append(('NOORIGIN', aid, act, s['t'][:50])); continue
    report[act] += 1
    reason = args[-1] if args else ''
    if s['k'] == 'summ':
        if act == 'DROP':
            if kind == 'spec': comment(o[0], o[1], 'drop')
            else: dec_lines.append(f'D {o}')
        elif act == 'NUQ':
            who, st = args[0], args[1]
            if kind == 'spec':
                f, i, rid, K = o
                if K: problems.append(('NUQ+K', aid)); continue
                comment(f, i, 'nuq'); nnew.append(f"{s['su']}:{s['v']} {s['a']} {rid} «{s['t']}» || {who} || {st}")
            else: dec_lines.append(f'N {o} {who}={st}')
        elif act == 'MOVE':
            m = re.match(r'(\d+):(\d+)', args[0] if args else '')
            if not m: problems.append(('MOVE-parse', aid)); continue
            if int(m[1]) != s['su']:
                tsu, tv = int(m[1]), int(m[2])
                d2 = json.load(open(f'{SC}/site/s{tsu}.json')); p2 = f'{SC}/site/s{tsu}i.json'
                inc2 = json.load(open(p2)) if os.path.exists(p2) else []
                hit = [r for r in d2['recs'] + inc2 if d2['books'][r['b']]['w'] == s['w'] and s['t'] in ws(r['t'])]
                if kind == 'spec': comment(o[0], o[1], 'move')
                else: dec_lines.append(f'D {o}')
                cnew.append(f"{tsu}:{tv} {s['a']} {s['su']}/{s['r']} «{s['t']}»")   # copy approach is robust to shifting inc ids
                continue
            if kind == 'spec':
                f, i, rid, K = o; LINES[f][i] = re.sub(r'^\d+:\d+', f"{m[1]}:{m[2]}", LINES[f][i])
            else: dec_lines.append(f'M {o} {m[1]}:{m[2]}')
        elif act == 'CTX':
            mm = re.search(r'«(.+?)»', args[0] if args else '')
            if not mm: problems.append(('CTX-parse', aid)); continue
            tt = s['t']
            for a2, g2, _ in DEC[aid]:
                if a2 == 'TRIM':
                    m2 = q1(g2)
                    if m2: tt = ws(m2.group(1))
            su2 = s['su']
            for a2, g2, _ in DEC[aid]:
                if a2 == 'MOVE' and g2:
                    m3 = re.match(r'(\d+):(\d+)', g2[0])
                    if m3: su2 = int(m3[1])
            ctxl.append(f"{su2} {s['a']} «{tt}» => «{ws(mm.group(1))}»")
        elif act == 'TRIM':
            mm = q1(args)
            if not mm: problems.append(('TRIM-parse', aid)); continue
            nt = ws(mm.group(1))
            if kind == 'spec':
                f, i, rid, K = o; LINES[f][i] = re.sub(r'«.+»\s*$', f'«{nt}»', LINES[f][i])
            else:
                dec_lines.append(f'D {o}'); gnew.append(f"{s['su']}:{s['v']} {s['a']} {s['r']} «{nt}»")
        else: problems.append(('ACT?', aid, act))
    else:  # nuq
        if kind != 'item': problems.append(('NUQ-not-item', aid)); continue
        if act == 'DROP': dec_lines.append(f'D {o}')
        elif act == 'WHO': dec_lines.append(f'W {o} {args[0]}')
        elif act == 'ST': dec_lines.append(f'S {o} {args[0]}')
        elif act == 'CTX':   # nuq turned into the imam's own words (SUMM) inside a DEC2 frame
            mm = re.search(r'«(.+?)»', args[0] if args else '')
            if mm: ctxl.append(f"{s['su']} {s['a']} «{s['t']}» => «{ws(mm.group(1))}»")
        elif act == 'SUMM': dec_lines.append(f'D {o}'); gnew.append(f"{s['su']}:{s['v']} {s['a']} {s['r']} «{s['t']}»")
        elif act == 'MOVE':
            m = re.match(r'(\d+):(\d+)', args[0] if args else '')
            if not m: problems.append(('NUQ-MOVE', aid, args[0] if args else '')); continue
            if int(m[1]) != s['su']:   # cross-surah: drop here, re-add in target surah from a copied record, keep rejoinder
                dec_lines.append(f'D {o}'); nnew.append(f"{m[1]}:{m[2]} {s['a']} {s['su']}/{s['r']} «{s['t']}» || {OV_WHO.get(aid, s.get('who'))} || {OV_ST.get(aid, s.get('st'))}")
                if s.get('rt'): rtfix.append(f"{m[1]}:{m[2]} {s['a']} «{s['t']}» => «{ws(s['rt'])}»")
                continue
            dec_lines.append(f'M {o} {m[1]}:{m[2]}')
        elif act == 'RT':
            mm = q1(args); rtfix.append(f"{s['su']}:{s['v']} {s['a']} «{s['t']}» => {('«' + ws(mm.group(1)) + '»') if mm else '-'}")
        elif act == 'TRIM':
            mm = q1(args)
            if not mm: problems.append(('TRIM-parse', aid)); continue
            st2 = OV_ST.get(aid, s.get('st')); rs = '|'.join(args)
            for cand in ('أقرّه وزاد عليه', 'أقرّه وشرحه', 'استشهد به', 'رجّح غيره', 'أقرّه', 'حكاه', 'ردّه'):
                if re.search(r'(?:stance|ST|موقف)[^|]{0,30}' + cand, rs) or ('→ ' + cand) in rs or ('-> ' + cand) in rs: st2 = cand; break
            dec_lines.append(f'D {o}'); nnew.append(f"{s['su']}:{s['v']} {s['a']} {s['r']} «{ws(mm.group(1))}» || {OV_WHO.get(aid, s.get('who'))} || {st2}")
        else: problems.append(('ACT?', aid, act))
print('decisions', len(DEC), dict(report))
for p_ in problems: print('PROBLEM', p_)
for _L in (dec_lines, gnew, nnew, cnew, rtfix, ctxl): _L[:] = list(dict.fromkeys(_L))
_seen = set(); _c2 = []
for _l in cnew:   # same text moved to the same verse from two places -> keep one
    _k = re.sub(r' \d+/\d+ ', ' ', _l)
    if _k not in _seen: _seen.add(_k); _c2.append(_l)
cnew[:] = _c2
if not DRY:
    for f, L in LINES.items(): open(f, 'w').write('\n'.join(L))
    open(SC + '/full/dec_audit.txt', 'w').write('# generated by audit/apply_audit.py\n' + '\n'.join(dec_lines) + '\n')
    open(SC + '/full/gspec_audit.txt', 'w').write('# generated by audit/apply_audit.py\n' + '\n'.join(gnew) + '\n')
    open(SC + '/coll/cspec_zaudit.txt', 'w').write('# generated by audit/apply_audit.py (cross-surah moves)\n' + '\n'.join(cnew) + '\n')
    open(SC + '/full/rtfix.txt', 'w').write('# generated by audit/apply_audit.py\n' + '\n'.join(rtfix) + '\n')
    open(SC + '/full/ctx_audit.txt', 'w').write('# generated by audit/apply_audit.py (owner DEC2 context lines)\n' + '\n'.join(ctxl) + '\n')
    open(SC + '/full/nspec_audit.txt', 'w').write('# generated by audit/apply_audit.py\n' + '\n'.join(nnew) + '\n')
print('ctx', len(ctxl)); print('dec', len(dec_lines), 'new summ', len(gnew), 'new nuq', len(nnew), 'cross-surah', len(cnew))
