import re,glob,zlib,sys,json,numpy as np
S='/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
sys.path.insert(0,S+'/scripts')
from parse import norm
N=5
def words(t):
    t=norm(t); t=re.sub(r'[^ء-ي ]',' ',t)
    return [w for w in t.split() if len(w)>1]
def grams(ws): return [zlib.crc32(' '.join(ws[i:i+N]).encode()) for i in range(len(ws)-N+1)]
def build(author_dir,out):
    H=[]
    for f in glob.glob(author_dir+'/*/*'):
        if f.endswith('.yml'): continue
        t=open(f,encoding='utf-8',errors='ignore').read()
        t=re.sub(r'PageV\d+P\d+|ms\d+|#|~~',' ',t)
        H.extend(grams(words(t)))
    a=np.unique(np.array(H,dtype=np.uint32)); np.save(out,a); print(out,len(a))
if __name__=='__main__':
    build('/home/claude/openiti/0750ah/data/0728IbnTaymiyya',S+'/books/IT_grams.npy')
    build('/home/claude/openiti/0775ah/data/0751IbnQayyimJawziyya',S+'/books/IQ_grams.npy')
