# usage: python3 qc/nq/cut.py N#### "first words" "last words"  -> exact span from that item's stored passage
import json,sys,re
SC='/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
ws=lambda s: re.sub(r'\s+',' ',s).strip()
I=json.load(open(SC+'/qc/nq/items.json'))[sys.argv[1]]; P=I['P']; s,e=ws(sys.argv[2]),ws(sys.argv[3])
a=P.find(s)
if a<0: sys.exit('start not found')
b=P.find(e,a)
if b<0: sys.exit('end not found after start')
print(P[a:b+len(e)])
