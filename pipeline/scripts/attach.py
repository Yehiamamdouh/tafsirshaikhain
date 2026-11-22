"""attach.py N : verify batch{N}.json (summ + nuq, verbatim) against site/s{N}.json(+i) and attach."""
import json, sys, re
S = '/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
n = sys.argv[1]
d = json.load(open(S+'/site/s%s.json' % n)); B = d['books']
inc = json.load(open(S+'/site/s%si.json' % n))
main_ids = {r['id'] for r in d['recs']}
ALL = d['recs'] + inc
ws = lambda s: re.sub(r'\s+', ' ', s).strip()
W = {r['id']: ws(r['t']) for r in ALL}
src = json.load(open(S+'/batch%s.json' % n))
bad = 0
def find(a, work, txt, prefer=None):
    t = ws(txt)
    if prefer is not None and t in W[prefer['id']]: return prefer
    for r in ALL:
        bk = B[r['b']]
        if bk['a'] == a and (work is None or bk['w'] == work) and t in W[r['id']]:
            return r
    return None
def ref(r, out, pre=''):
    out[pre+'r'] = r['id']; out[pre+'b'] = r['b']; out[pre+'v'] = r['v']; out[pre+'p'] = r['p']
    if r['id'] not in main_ids and not pre: out['ft'] = r['t']
summ, nuq = {}, {}
for a, vs in src.get('summ', {}).items():
    for v, pts in vs.items():
        for e in pts:
            work, ex = e[0], e[1]
            r = find(a, work, ex)
            if not r: print('MISSING summ', a, v, work, ex[:60]); bad += 1; continue
            o = {'t': ws(ex)}; ref(r, o)
            if len(e) > 2 and e[2]: o['cx'] = e[2]
            summ.setdefault(a, {}).setdefault(v, []).append(o)
for a, vs in src.get('nuq', {}).items():
    for v, items in vs.items():
        for it in items:
            r = find(a, it.get('w'), it['t'])
            if not r: print('MISSING nuq', a, v, it['who'], it['t'][:60]); bad += 1; continue
            o = {'who': it['who'], 'st': it['st'], 't': ws(it['t'])}; ref(r, o)
            if it.get('rt'):
                r2 = find(a, it.get('rw', it.get('w')), it['rt'], prefer=r)
                if not r2: print('MISSING rt', a, v, it['rt'][:60]); bad += 1; continue
                o['rt'] = ws(it['rt']); ref(r2, o, 'r')
                o['rr'] = o.pop('rr'); 
            nuq.setdefault(a, {}).setdefault(v, []).append(o)
d['summ'] = summ; d['nuq'] = nuq
json.dump(d, open(S+'/site/s%s.json' % n, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('surah', n, 'bad', bad, 'summ', sum(len(x) for a in summ.values() for x in a.values()), 'nuq', sum(len(x) for a in nuq.values() for x in a.values()))
