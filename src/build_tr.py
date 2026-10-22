import json,os,sys
S='/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
REPO=sys.argv[1]; P=REPO+'/public'
Q='/home/claude/quran/quran-json/data'
src={x['path'].split('/')[-1][:-5]:x for x in json.load(open(Q+'/meta/sources.json')) if 'quranenc' in x['path']}
meta={}
for code,name,d,key in json.load(open(S+'/pub/langs.json')):
    T=json.load(open(f'{Q}/quranenc/{key}.json')); os.makedirs(f'{P}/tr/{code}',exist_ok=True)
    for s in range(1,115):
        rows=[[x['text'],x.get('footnotes') or ''] for x in sorted(T[str(s)],key=lambda x:x['verse'])]
        json.dump(rows,open(f'{P}/tr/{code}/{s}.json','w'),ensure_ascii=False,separators=(',',':'))
    m=src[key]['source_metadata']; meta[code]={'name':name,'dir':d,'title':m['title'],'version':m['version'],'url':m['browse_url']}
json.dump(meta,open(P+'/tr/langs.json','w'),ensure_ascii=False)
print(len(meta),'languages')
