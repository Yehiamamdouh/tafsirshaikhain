import re,json,sys,os
S='/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
t=open(sys.argv[1]).read()
parts=re.split(r'={20,}\n(batch_\d+)\.json\n.*?\n.*?\n={20,}\n',t)
os.makedirs(S+'/astra/resp',exist_ok=True)
for i in range(1,len(parts),2):
    name,body=parts[i],parts[i+1]
    open(S+'/astra/resp/%s.txt'%name,'w').write(body)
    print(name,len(body))
