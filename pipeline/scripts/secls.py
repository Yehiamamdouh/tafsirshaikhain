import pickle, collections, re, sys
S='/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
P=pickle.load(open(S+'/majmu.pkl','rb')); M=pickle.load(open(S+'/out/majmap.pkl','rb')); secs=pickle.load(open(S+'/out/majsecs.pkl','rb'))
a,b=int(sys.argv[1]),int(sys.argv[2])
for k,s in enumerate(secs[a:b],a):
    c=collections.Counter(); first=None
    for i in s:
        for (su,v),n in M[i].items():
            c[su]+=n
            if first is None: first=(su,v)
    op=' '.join(P[i]['text'] for i in s)[:110].replace('\n',' ')
    print(f"{k} [{s[0]}-{s[-1]}] {P[s[0]]['vol']}/{P[s[0]]['p_start']}-{P[s[-1]]['p_start']} n={len(s)} first={first} top={c.most_common(3)} | {op}")
