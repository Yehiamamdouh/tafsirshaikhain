"""booksecs.py WORKGLOB : sections of a book split at 'فصل' openers with citation profile."""
import sys, glob, re, collections, pickle, os
sys.path.insert(0, os.path.dirname(__file__))
import parse, qmap, build as B0
w = sys.argv[1]
ps = [p for p in glob.glob(B0.IT+'/*/*.'+w+'.*-ara*')+glob.glob(B0.IQ+'/*/*.'+w+'.*-ara*') if not p.endswith('.yml')]
P = parse.paragraphs(ps[0]); Q = qmap.Quran()
OPEN = re.compile(r'^\s*(فصل|وسئل|سئل|قال شيخ|وقال شيخ|سورة|ومنها قوله|ومن ذلك)')
secs = []; cur = None
for i, p in enumerate(P):
    if cur is None or OPEN.match(p['text']): cur = [i]; secs.append(cur)
    else: cur.append(i)
for s in secs:
    c = collections.Counter(); first = None
    for i in s:
        f, _ = qmap.map_paragraph(Q, P[i]['text'])
        for (su, v), n in f.items():
            c[su] += n
            if first is None: first = (su, v)
    op = ' '.join(P[i]['text'] for i in s)[:120].replace('\n', ' ')
    print(f"[{s[0]}-{s[-1]}] p{P[s[0]]['p_start']} n={len(s)} first={first} top={c.most_common(3)} | {op}")
