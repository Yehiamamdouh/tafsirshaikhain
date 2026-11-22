"""tam/cut.py ID recN "START words" "END words"
Prints the exact (whitespace-normalised) substring of record recN of item ID from the first START match
through the end of the first END match after it. Use it to build proposed excerpts — never retype Arabic."""
import json, re, sys
SC = '/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
ws = lambda s: re.sub(r'\s+', ' ', s).strip()
it = json.load(open(SC + '/tam/items.json'))[sys.argv[1]]
rid = sys.argv[2].replace('rec', '')
t = ws(it['recs'][rid]['t']); s, e = ws(sys.argv[3]), ws(sys.argv[4])
i = t.find(s)
if i < 0: sys.exit('START not found')
j = t.find(e, i)
if j < 0: sys.exit('END not found after START')
print(t[i:j + len(e)])
