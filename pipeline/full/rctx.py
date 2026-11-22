"""rctx.py SU RECID [nprev] [chars] : show the book context of a record: header, previous paragraphs (start+end), record start."""
import json, os, re, sys, pickle
SC = '/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
ws = lambda s: re.sub(r'\s+', ' ', s).strip()
su, rid = int(sys.argv[1]), int(sys.argv[2]); NP = int(sys.argv[3]) if len(sys.argv) > 3 else 4
CH = int(sys.argv[4]) if len(sys.argv) > 4 else 160
d = json.load(open(f'{SC}/site/s{su}.json')); p = f'{SC}/site/s{su}i.json'
inc = json.load(open(p)) if os.path.exists(p) else []
r = {r['id']: r for r in d['recs'] + inc}[rid]; w = d['books'][r['b']]['w']; T = ws(r['t'])
raw = pickle.load(open(f'{SC}/out/cache/{w}.pkl', 'rb'))['paras']; P = [ws(x['text']) for x in raw]
ks = [i for i, t in enumerate(P) if t[:80] == T[:80]]
print(f'== {su} rec{rid} {w} {r["v"]}/{r["p"]}  para {ks[:3]}  header: {raw[ks[0]]["header"] if ks else "?"}')
if ks:
    k = ks[0]
    for j in range(max(0, k - NP), k):
        t = P[j]; print(f'  [{j}] {raw[j]["v"] if "v" in raw[j] else raw[j]["vol"]}/{raw[j]["p_start"]} H={raw[j]["header"][:50]!r}: {t[:CH]}  …  {t[-CH:] if len(t) > 2 * CH else ""}')
print(f'  [REC] {T[:CH * 3]}')
