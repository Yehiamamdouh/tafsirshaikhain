import json, sys
S='/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
plain=json.load(open('/home/claude/quran/quran-json/data/tanzil/simple.json',encoding='utf-8'))
for sur in map(int, sys.argv[1:]):
    d=json.load(open(S+'/out/s%d.json'%sur,encoding='utf-8'))
    ctx={}
    for r in d['recs']:
        r.pop('i',None)
        if 'cb' in r or 'ca' in r:
            ctx[r['id']]=[r.pop('cb',''), r.pop('ca','')]; r['x']=1
    inc=[r for r in d['recs'] if r.get('inc')]
    d['recs']=[r for r in d['recs'] if not r.get('inc')]
    d['verses']=[v['text'] for v in plain[str(sur)]]; d['surah']=sur; d['incCount']=len(inc)
    for name,obj in (('s%d.json'%sur,d),('s%di.json'%sur,inc),('c%d.json'%sur,ctx)):
        json.dump(obj,open(S+'/site/'+name,'w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
