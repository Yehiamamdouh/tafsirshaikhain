import sys; args=sys.argv[1:]; sys.argv=['x','0','0']
exec(open('/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad/full/xshow.py').read().split("if __name__")[0])
# ctx.py n [before] [after] [prevparas]
n=int(args[0]); B=int(args[1]) if len(args)>1 else 1500; A=int(args[2]) if len(args)>2 else 300; PP=int(args[3]) if len(args)>3 else 1
it=I[n]; d,r=locate(n); bk=d['books'][r['b']]; P,M=paras(bk['w']); T=ws(r['t']); pi=M.get(T)
pre=''
if pi is not None:
    for k in range(PP,0,-1):
        if pi-k>=0: pre+=P[pi-k]+' ‖ '
T2=pre+T; i=T2.find(it['t'])
print(n, it['k'], it['a'], it['su'], it['v'], it.get('who',''), bk['w'], r['id'])
print(T2[max(0,i-B):i]+' [['+it['t']+']] '+T2[i+len(it['t']):i+len(it['t'])+A])
