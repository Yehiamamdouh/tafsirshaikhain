"""Mark scattered passages that only mention a verse in passing (field 'inc')."""
import sys, os, json, re, collections
sys.path.insert(0, os.path.dirname(__file__))
import parse
from parse import norm

PATH = sys.argv[1]
d = json.load(open(PATH, encoding='utf-8'))
B, R = d['books'], d['recs']

EXPLAIN = ['معني', 'قوله', 'تفسير', 'فسر', 'المراد', 'يعني', 'تضمن', 'تضمنت', 'دل علي', 'دلت', 'سر ', 'فان ', 'لان ', 'ولهذا']

def phrase_hits(n, v):
    if v == 0:
        return sum(n.count(s) for s in parse.SURAH)
    d = parse.VERSES[v]
    return sum(n.count(ph) for ph in set(d['braced'] + d['strong']))

stats = collections.Counter()
for r in R:
    if r['c']:
        continue
    n = norm(r['t'])
    best = 0
    for v in r['ay']:
        h = phrase_hits(n, v)
        expl = sum(k in n for k in EXPLAIN)
        neigh = any(v in parse.detect(x)[0] or (v == 0 and parse.detect(x)[1]) for x in (r.get('cb', ''), r.get('ca', '')) if x)
        score = (h >= 2) * 2 + (expl >= 2) + neigh * 2 + (len(n) > 400)
        best = max(best, score)
    if best < 2:
        r['inc'] = 1
    stats[(B[r['b']]['a'], 'inc' if r.get('inc') else 'keep')] += 1
json.dump(d, open(PATH, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print(stats)
