"""bp/narrow.py : stricter filter — a hit counts only if an explanation marker follows the verse quote closely."""
import json, pickle, re, glob, collections, sys
SC='/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
ws=lambda s: re.sub(r'\s+',' ',s).strip()
C=json.load(open(SC+'/bp/cand.json'))
STRONG=re.compile(r'أي[: ]|أى |يعني|يعنى|معناه|ومعنى|والمعنى|المراد|فأخبر|أخبر سبحانه|أخبر تعالى|فدل|يدل على|دليل على|فبين|فبيّن|يتضمن|تضمنت|فسر|تفسير|والصحيح|والصواب|والتحقيق|فيه دليل|ففيه|وهذا يقتضي|فنهى|فأمر')
PC={}
def P(w):
    if w not in PC: PC[w]=pickle.load(open(f'{SC}/out/cache/{w}.pkl','rb'))['paras']
    return PC[w]
def strong(x, win):
    T=ws(P(x['w'])[x['i']]['text']); e=T.find('}',x['pos'])
    if e<0: return False
    tail=T[e+1:e+1+win]
    if x['nv']>4: return False
    return bool(STRONG.search(tail))
def keep(L,win): return any(strong(x,win) for x in L)
if __name__=='__main__':
    win=int(sys.argv[1])
    done={}
    for f in sorted(glob.glob(SC+'/bp/out/B*.txt')):
        for ln in open(f):
            p=ln.split(' | ')
            if len(p)>1: done[p[0]]=done.get(p[0],False) or p[1] in ('IT','IQ')
    kept=[k for k in done if keep(C[k],win)]
    hit=[k for k in done if done[k]]
    print('win',win,'reviewed',len(done),'kept',len(kept),'excerpt verses',len(hit),'excerpts kept',sum(1 for k in hit if k in kept))
    rest=[k for k in C if k not in done]
    print('unreviewed',len(rest),'would keep',sum(1 for k in rest if keep(C[k],win)))
