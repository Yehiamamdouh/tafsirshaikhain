"""tam/chk.py tam/out/XX.txt [packet] : validate an output file.
Line format:  ID | VERDICT | PROPOSAL | reason
  VERDICT  كاف | إكمال | استبدال | لا يمكن
  PROPOSAL '-' for كاف / لا يمكن; else one or more  recN «text»  joined by ' ++ ' (each text must be an exact
           whitespace-normalised substring of that record of the item)."""
import json, re, sys
SC = '/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
ws = lambda s: re.sub(r'\s+', ' ', s).strip()
I = json.load(open(SC + '/tam/items.json'))
V = {'كاف', 'كافٍ', 'إكمال', 'استبدال', 'لا يمكن'}
bad = 0; seen = []; cnt = {}
for n, ln in enumerate(open(sys.argv[1]), 1):
    ln = ln.strip()
    if not ln or ln.startswith('#'): continue
    f = [x.strip() for x in ln.split(' | ')]
    if len(f) < 4: print(n, 'FIELDS', ln[:80]); bad += 1; continue
    iid, vd, pr = f[0], f[1], f[2]
    if iid not in I: print(n, 'NOID', iid); bad += 1; continue
    if vd not in V: print(n, 'VERDICT', vd); bad += 1; continue
    seen.append(iid); cnt[vd] = cnt.get(vd, 0) + 1
    if vd in ('كاف', 'كافٍ', 'لا يمكن'):
        if pr != '-': print(n, 'PROPOSAL should be -'); bad += 1
        continue
    parts = re.findall(r'rec(\d+)\s*«(.*?)»(?=\s*(?:\+\+|$))', pr)
    if not parts: print(n, 'NOPARTS', iid); bad += 1; continue
    for rid, t in parts:
        r = I[iid]['recs'].get(rid)
        if not r: print(n, 'REC not in item', iid, rid); bad += 1
        elif ws(t) not in ws(r['t']): print(n, 'NOTVERBATIM', iid, 'rec' + rid, ws(t)[:60]); bad += 1
if len(sys.argv) > 2:
    want = re.findall(r'^### (t\d+:\d+:I[TQ])', open(sys.argv[2]).read(), re.M)
    miss = [x for x in want if x not in seen]
    if miss: print('MISSING', miss); bad += len(miss)
    if seen != [x for x in want if x in seen]: print('ORDER differs from packet')
print('lines', len(seen), cnt, 'bad', bad)
