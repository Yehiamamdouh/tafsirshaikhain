#!/usr/bin/env python3
"""Passages for passage pages -> public/groups.json  (content session; re-run after any content update).

A passage = a run of consecutive verses of one surah where each verse shares at least one
identical summ excerpt (same imam, same text) with the next one.  Output: [{su, from, to}].
Nothing is written by hand and no text is copied: the file only names verse ranges.
Usage: python3 src/make_groups.py [repo_root]
"""
import json, sys, os, collections
root = sys.argv[1] if len(sys.argv) > 1 else '.'
out = []
for su in range(1, 115):
    d = json.load(open(os.path.join(root, 'public', f's{su}.json'), encoding='utf-8'))
    key = collections.defaultdict(set)
    for a in ('IT', 'IQ'):
        for v, items in d['summ'].get(a, {}).items():
            for it in items:
                key[int(v)].add((a, it['t']))
    cur = None
    for v in sorted(key) + [None]:
        if cur and v is not None and v == cur[-1] + 1 and key[v] & key[cur[-1]]:
            cur.append(v)
            continue
        if cur and len(cur) > 1:
            out.append({'su': su, 'from': cur[0], 'to': cur[-1]})
        cur = [v] if v is not None else None
json.dump(out, open(os.path.join(root, 'public', 'groups.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, separators=(',', ':'))
print(len(out), 'passages,', sum(g['to'] - g['from'] + 1 for g in out), 'verses')
