"""qc/nq/mk.py : «تمام المعنى» review packets for every نقل on the site (items.json + pk/N###.txt, 40 per packet)."""
import json, re
SC='/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
ws=lambda s: re.sub(r'\s+',' ',s).strip()
DIA=re.compile('[ً-ْٰـۖ-ۭ]')
items={}; blocks=[]
for su in range(1,115):
    d=json.load(open(f'{SC}/site/s{su}.json'))
    try: inc=json.load(open(f'{SC}/site/s{su}i.json'))
    except Exception: inc=[]
    R={r['id']:r for r in d['recs']+inc}; B=d['books']
    for a,x in d.get('nuq',{}).items():
        for v in sorted(x,key=int):
            for i,e in enumerate(x[v]):
                t=ws(e['t']); r=R.get(int(e['r'])) if str(e.get('r','')).isdigit() else None
                if r is None: r=next((r for r in R.values() if t[:60] in ws(r['t'])),None)
                P=ws(r['t']) if r else ''
                k=f'N{len(items)+1:04d}'
                items[k]=dict(su=su,v=int(v),a=a,i=i,t=t,who=e['who'],st=e['st'],rt=ws(e.get('rt','')),P=P,w=B[r['b']]['w'] if r else '',ref=f"{r['v']}/{r['p']}" if r else '')
                j=P.find(t[:40]); lo=max(0,j-1500) if j>=0 else 0; hi=min(len(P),(j if j>=0 else 0)+len(t)+1800)
                win=('…' if lo else '')+P[lo:hi]+('…' if hi<len(P) else '')
                rt=f"\nRT (imam's rejoinder now shown): «{items[k]['rt']}»" if items[k]['rt'] else ''
                blocks.append(f"\n### {k} — {su}:{v} — {a} — w={items[k]['w']} ({items[k]['ref']})\nVERSE: {DIA.sub('',d['verses'][int(v)-1])}\nWHO: {e['who']} | ST: {e['st']}\nNUQ TEXT: «{t}»{rt}\nPASSAGE (stored, window): {win}")
json.dump(items,open(SC+'/qc/nq/items.json','w'),ensure_ascii=False)
for n in range(0,len(blocks),40): open(f'{SC}/qc/nq/pk/N{n//40+1:03d}.txt','w').write(''.join(blocks[n:n+40]))
print(len(items),'packets',(len(blocks)+39)//40)
