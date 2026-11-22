"""Check that every summary excerpt is a verbatim substring of the source text, and attach its reference."""
import sys, os, json, re, glob
sys.path.insert(0, os.path.dirname(__file__))
import parse

S = '/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
d = json.load(open(S + '/out/data.json', encoding='utf-8'))
B, R = d['books'], d['recs']
summ = json.load(open(S + '/summaries.json', encoding='utf-8'))
ws = lambda s: re.sub(r'\s+', ' ', s).strip()

out, bad = {}, 0
for a, verses in summ.items():
    out[a] = {}
    for v, pts in verses.items():
        out[a][v] = []
        for work, ex in pts:
            exn = ws(ex)
            hit = None
            for r in R:
                bk = B[r['b']]
                if bk['a'] == a and bk['w'] == work and exn in ws(r['t']):
                    hit = r; break
            if hit is None:
                print('MISSING', a, v, work, ex[:70]); bad += 1
                continue
            out[a][v].append({'t': exn, 'r': hit['id'], 'b': hit['b'], 'v': hit['v'], 'p': hit['p']})
d['summ'] = out
json.dump(d, open(S + '/out/data.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('missing:', bad, 'ok:', sum(len(x) for a in out.values() for x in a.values()))
