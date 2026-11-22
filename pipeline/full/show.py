import json,sys
I=json.load(open('/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad/full/items.json'))
a,b=int(sys.argv[1]),int(sys.argv[2]); last=None
for x in I[a:b]:
    key=(x['su'],x['v'])
    if key!=last: print(f"=== {x['su']}:{x['v']} {x['vt'][:90]}"); last=key
    if x['k']=='summ':
        print(f"{x['n']} {x['a']} S| …{x['b'][-80:]} [[{x['t']}]] {x['af'][:80]}…")
    else:
        print(f"{x['n']} {x['a']} N {x['who']}={x['st']}{' rt:'+x['rt'][:80] if x['rt'] else ''}| …{x['b'][-110:]} [[{x['t'][:260]}]] {x['af'][:150]}…")
