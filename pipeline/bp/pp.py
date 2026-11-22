# usage: python3 bp/pp.py WORK i [before] [after]  -> print paragraphs i-before .. i+after (index, vol/page, header, text)
import pickle,sys,re
SC='/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
w,i=sys.argv[1],int(sys.argv[2]); b=int(sys.argv[3]) if len(sys.argv)>3 else 1; a=int(sys.argv[4]) if len(sys.argv)>4 else 2
P=pickle.load(open(f'{SC}/out/cache/{w}.pkl','rb'))['paras']
for j in range(max(0,i-b),min(len(P),i+a+1)):
    p=P[j]; print(f'[#{j}] {p["vol"]}/{p["p_start"]} [{(p.get("header") or "")[:80]}]', re.sub(r'\s+',' ',p['text'])); print()
