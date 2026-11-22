# usage: python3 bp/cut.py WORK i "first words" "last words"  -> exact span from paragraph i (may run into i+1, i+2)
import pickle,sys,re
SC='/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
ws=lambda s: re.sub(r'\s+',' ',s).strip()
w,i,s,e=sys.argv[1],int(sys.argv[2]),ws(sys.argv[3]),ws(sys.argv[4])
P=pickle.load(open(f'{SC}/out/cache/{w}.pkl','rb'))['paras']
T=' '.join(ws(P[j]['text']) for j in range(i,min(len(P),i+3)))
a=ws(P[i]['text']).find(s)
if a<0: sys.exit('start not found in paragraph #%d'%i)
b=T.find(e,a)
if b<0: sys.exit('end not found within #%d..#%d'%(i,i+2))
print(T[a:b+len(e)])
