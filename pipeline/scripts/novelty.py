import sys,glob,json,numpy as np,re
S='/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
sys.path.insert(0,S+'/scripts')
from shingle import words,grams
def run(book,imam):
    A=np.load(f'{S}/books/{imam}_grams.npy')
    def frac(g):
        if not g: return None
        g=np.array(g,dtype=np.uint32); i=np.searchsorted(A,g); i[i>=len(A)]=0
        return float((A[i]==g).mean())
    rows=[]
    for f in sorted(glob.glob(f'{S}/books/{book}/*.txt')):
        pg=int(f[-8:-4])
        for k,para in enumerate(re.split(r'\n\s*\n',open(f).read())):
            ws=words(para)
            if len(ws)<15: continue
            rows.append((pg,k,len(ws),frac(grams(ws)),para.strip()))
    return rows
if __name__=='__main__':
    book,imam=sys.argv[1:3]
    rows=run(book,imam)
    json.dump(rows,open(f'{S}/books/{book}_nov.json','w'),ensure_ascii=False)
    W=sum(r[2] for r in rows)
    for lo,hi in [(0,.1),(.1,.3),(.3,.6),(.6,1.01)]:
        sel=[r for r in rows if lo<=r[3]<hi]; print(f'{book} overlap {lo}-{hi}: paras {len(sel)} words {sum(r[2] for r in sel)} ({100*sum(r[2] for r in sel)/W:.0f}%)')
