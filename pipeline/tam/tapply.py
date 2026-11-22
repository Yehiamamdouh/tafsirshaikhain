"""tam/tapply.py : apply the «تمام المعنى للباحث» review (tam/out/*.txt, tam/manual.txt overrides) to batchN.json.
Runs in rebuild.sh after rext + gap2 (texts were cut from the rext-widened records).
  كاف            -> unchanged (CTX applied if approved)
  إكمال/استبدال -> the (surah, imam, verse) summ list is replaced by the proposed points (existing cx kept on point 1)
  لا يمكن        -> unchanged, listed in tam/specialist.txt
Approved CTX only: «وهذا اختيار الإمام» / «ينقل كلام … ويقرّه»."""
import json, re, glob, os
SC = '/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
T = SC + '/tam'
ws = lambda s: re.sub(r'\s+', ' ', s).strip()
I = json.load(open(T + '/items.json'))
OKCTX = re.compile(r'^(وهذا اختيار الإمام|ينقل كلام .{2,40} ويقرّه)$')
dec = {}
files = sorted(glob.glob(T + '/out/*.txt')) + ([T + '/manual.txt'] if os.path.exists(T + '/manual.txt') else [])
for f in files:
    for ln in open(f):
        p = [x.strip() for x in ln.strip().split(' | ')]
        if len(p) < 4 or p[0] not in I: continue
        dec[p[0]] = (p[1].replace('كافٍ', 'كاف'), p[2], ' | '.join(p[3:]), os.path.basename(f))
B = {}
def batch(su):
    if su not in B: B[su] = json.load(open(f'{SC}/batch{su}.json'))
    return B[su]
cnt = {}; miss = []; spec = []; badctx = []
for iid, (vd, pr, rs, src) in dec.items():
    it = I[iid]; su, a, v = it['su'], it['a'], str(it['v'])
    cm = re.search(r'CTX\s*«([^»]+)»', rs); cx = ws(cm[1]) if cm else None
    if cx and not OKCTX.match(cx): badctx.append(f'{iid} {cx}'); cx = None
    L = batch(su).get('summ', {}).get(a, {}).get(v)
    if L is None: miss.append(iid); continue
    if vd == 'لا يمكن':
        spec.append(f'{iid} | {rs}'); cnt[vd] = cnt.get(vd, 0) + 1; continue
    if vd in ('إكمال', 'استبدال'):
        parts = re.findall(r'rec(\d+)\s*«(.*?)»(?=\s*(?:\+\+|$))', pr)
        old_cx = next((e[2] for e in L if len(e) > 2 and e[2]), None)
        w = {}
        for e in it['ents']: w[str(e['r'])] = e['w']
        new = []
        for rid, t in parts:
            wk = w.get(rid) or next((e[0] for e in L), None)
            r = it['recs'].get(rid)
            if r is None or ws(t) not in ws(r['t']): miss.append(iid + ' NV'); new = None; break
            new.append([wk, ws(t)])
        if not new: continue
        if old_cx: new[0].append(old_cx)
        L[:] = new
    if cx:
        if len(L[0]) > 2: L[0][2] = cx
        else: L[0].append(cx)
        cnt['ctx'] = cnt.get('ctx', 0) + 1
    cnt[vd] = cnt.get(vd, 0) + 1
HIDE = [ws(l) for l in open(T + '/hide.txt')] if os.path.exists(T + '/hide.txt') else []
for iid in HIDE:
    if iid not in I: continue
    it = I[iid]; d = batch(it['su']).get('summ', {}).get(it['a'], {})
    if str(it['v']) in d: del d[str(it['v'])]; cnt['hidden'] = cnt.get('hidden', 0) + 1; spec.append(f'{iid} | HIDDEN: edition text likely missing «نفي» — reads opposite')
for su, d in B.items(): json.dump(d, open(f'{SC}/batch{su}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
open(T + '/specialist.txt', 'w').write('\n'.join(spec) + '\n')
print('tapply', cnt, 'items', len(dec), 'miss', len(miss), 'badctx', len(badctx))
for m in miss[:10]: print('MISS', m)
for b in badctx: print('BADCTX', b)
