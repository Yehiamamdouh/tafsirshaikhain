"""xres.py [N...] : resolve full/xspec.txt into new verbatim spans -> full/xnew.json; print problems (and the new text for N...).
spec line:  n  S«start»  E«end»   (S/E extend-or-keep; s/e trim inside the item)   |  n K  (keep)  |  n D (delete instead)
S: new text starts at the nearest occurrence of «start» at/before the old start (may reach into the previous paragraph)
E: new text ends at the first occurrence of «end» ending at/after the old end (may reach into the next paragraph)
"""
import json, sys, re
sys.argv_save = sys.argv[1:]; sys.argv = ['x', '0', '0']
exec(open('/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad/full/xshow.py').read().split("if __name__")[0])
SPEC = {}
for ln in open(SC + '/full/xspec.txt'):
    ln = ln.strip()
    if not ln or ln.startswith('#'): continue
    m = re.match(r'(\d+)\s*(.*)$', ln); n = int(m.group(1)); rest = m.group(2)
    sp = {'raw': rest}
    for k, v in re.findall(r'([SsEeAZ])«(.*?)»', rest): sp[k] = ws(v)
    if re.match(r'^[KD]\b', rest): sp['op'] = rest[0]
    SPEC[n] = sp
out, bad = {}, 0
for n, sp in sorted(SPEC.items()):
    if sp.get('op'): out[n] = {'op': sp['op']}; continue
    it = I[n]; d, r = locate(n)
    if not r: print(n, 'NO RECORD'); bad += 1; continue
    bk = d['books'][r['b']]; T = ws(r['t']); P, M = paras(bk['w']); pi = M.get(T)
    pos = T.find(it['t']); end = pos + len(it['t']); joined = [0, 0]
    def fail(msg):
        global bad; print(n, 'FAIL', msg); bad += 1
    s0, e0 = pos, end; ok = True
    if 'A' in sp:
        # absolute span: start at occurrence of A nearest the item (prev/next paragraph allowed), end at first Z after it
        if pi is not None and pi > 0:
            T = P[pi - 1] + ' ' + T; sh = len(P[pi - 1]) + 1; pos += sh; end += sh; joined[0] = 1
        if pi is not None and pi > 1:
            T = P[pi - 2] + ' ' + T; sh = len(P[pi - 2]) + 1; pos += sh; end += sh; joined[0] = 2
        if pi is not None and pi + 1 < len(P):
            T = T + ' ' + P[pi + 1]; joined[1] = 1
        if pi is not None and pi + 2 < len(P):
            T = T + ' ' + P[pi + 2]; joined[1] = 2
        ks = [m.start() for m in re.finditer(re.escape(sp['A']), T)]
        if not ks: fail('A not found ' + sp['A']); continue
        s0 = min(ks, key=lambda k: abs(k - pos))
        k2 = T.find(sp['Z'], s0)
        if k2 < 0: fail('Z not found ' + sp['Z']); continue
        e0 = k2 + len(sp['Z'])
        new = T[s0:e0].strip()
        # trim joins that are not used
        o = {'t': new, 'rec': r['id'], 'su': it['su'], 'join': {'pi': pi, 'prev': joined[0], 'next': joined[1], 'w': bk['w']}}
        out[n] = o
        if str(n) in sys.argv_save or 'all' in sys.argv_save: print(f"\n{n} ABS {len(it['t'])}->{len(new)}\n  {new}")
        continue
    if 'S' in sp:
        k = T.rfind(sp['S'], 0, pos + len(sp['S']))
        if k < 0 and pi is not None and pi > 0:
            T = P[pi - 1] + ' ' + T; sh = len(P[pi - 1]) + 1; pos += sh; end += sh; joined[0] = 1
            k = T.rfind(sp['S'], 0, pos + len(sp['S']))
        if k < 0: fail('S not found ' + sp['S']); continue
        s0 = k
    elif 's' in sp:
        k = T.find(sp['s'], pos, end)
        if k < 0: fail('s not found ' + sp['s']); continue
        s0 = k
    else: s0 = pos
    if 'E' in sp:
        k = T.find(sp['E'], max(0, end - len(sp['E'])))
        if k < 0 and pi is not None and pi + 1 < len(P):
            T = T + ' ' + P[pi + 1]; joined[1] = 1
            k = T.find(sp['E'], max(0, end - len(sp['E'])))
        if k < 0: fail('E not found ' + sp['E']); continue
        e0 = k + len(sp['E'])
    elif 'e' in sp:
        k = T.rfind(sp['e'], pos, end)
        if k < 0: fail('e not found ' + sp['e']); continue
        e0 = k + len(sp['e'])
    else: e0 = end
    new = T[s0:e0].strip()
    if new == it['t']: print(n, 'UNCHANGED (spec ' + sp['raw'][:40] + ')')
    o = {'t': new, 'rec': r['id'], 'su': it['su']}
    if any(joined): o['join'] = {'pi': pi, 'prev': joined[0], 'next': joined[1], 'w': bk['w']}
    out[n] = o
    if str(n) in sys.argv_save or 'all' in sys.argv_save:
        print(f"\n{n} {'JOIN' if any(joined) else ''} {len(it['t'])}->{len(new)}\n  {new}")
json.dump(out, open(SC + '/full/xnew.json', 'w'), ensure_ascii=False, indent=0)
XS_ = set(XS); print('specs', len(SPEC), 'bad', bad, 'missing', len(XS_ - set(SPEC)), 'extra', sorted(set(SPEC) - XS_)[:20])
