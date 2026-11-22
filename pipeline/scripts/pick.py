import sys,re,collections
files=[l.strip() for l in sys.stdin if re.search(r'-ara\d$',l.strip())]
by=collections.defaultdict(list)
for f in files: by[f.split('/')[2]].append(f)
def rank(f):
    n=f.split('.')[-1]
    for i,p in enumerate(['Shamela','Sham19Y','ShamAY','JK']):
        if n.startswith(p): return (i,'Vols' in n,'BK' in n,n)
    return (9,False,False,n)
skip=set(sys.argv[1:])
for w,fs in sorted(by.items()):
    if any(s in w for s in skip): continue
    print(sorted(fs,key=rank)[0])
