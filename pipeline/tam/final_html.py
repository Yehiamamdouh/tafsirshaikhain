import json,re,html,glob,random
SC='/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
I=json.load(open(SC+'/tam/items.json'))
Q=json.load(open('/home/claude/tafsirshaikhain/src/data/simple.json'))
CH=json.load(open('/home/claude/tafsirshaikhain/src/data/chapters.json'))['chapters']
rows=[]
for f in sorted(glob.glob(SC+'/tam/out/T*.txt')):
  for ln in open(f):
    p=[x.strip() for x in ln.split(' | ')]
    if len(p)>=4 and p[1] in ('إكمال','استبدال'): rows.append(p)
random.seed(11); S=random.sample(rows,50)
def why(r):
  r2=r.lower(); out=[]
  if re.search(r'duplicat|repeat|overlap|copy',r2): out.append('جملة مكررة اتشالت أو اندمجت')
  if re.search(r'cond\.?\s*1|verdict|conclusion',r2): out.append('كان ناقصه حكم الإمام أو نتيجته')
  if re.search(r'cond\.?\s*2|referent|dangling|points? (back|to)',r2): out.append('كان فيه كلمة بتشاور على حاجة مش ظاهرة')
  if re.search(r'cond\.?\s*3|restriction|qualif|لكن',r2): out.append('كان مقطوع قبل قيد بيغير المعنى')
  if re.search(r'cond\.?\s*4|views|meanings|choice',r2): out.append('الإمام ذكر أكتر من معنى أو اختار واحد')
  if re.search(r'cond\.?\s*5|unrelated|off-topic|other verse',r2): out.append('كان فيه كلام ملوش علاقة بالآية')
  return '، '.join(dict.fromkeys(out)) or 'تحسين تمام المعنى'
VN={'إكمال':'إكمال','استبدال':'استبدال'}
out=[]
for n,(iid,vd,pr,*rs) in enumerate(S,1):
  it=I[iid]; su,v=it['su'],it['v']; xs=Q[str(su)]; x=xs[str(v)] if isinstance(xs,dict) else xs[v-1]; vt=x['text'] if isinstance(x,dict) else x
  cur=''.join(f'<p class="q">«{html.escape(e["t"])}»</p>' for e in it['ents'])
  parts=re.findall(r'rec(\d+)\s*«(.*?)»(?=\s*(?:\+\+|$))',pr)
  prop=''.join(f'<p class="q new">«{html.escape(t)}»</p>' for _,t in parts)
  out.append(f'<section><h2>{n}. {CH[su-1]["name"]} {v} — {"ابن تيمية" if it["a"]=="IT" else "ابن القيم"} <span class="v">{VN[vd]}</span></h2><p class="ay">﴿{html.escape(vt)}﴾</p><div class="lbl">الحالي:</div>{cur}<div class="lbl">الجديد:</div>{prop}<p class="why">السبب: {why(" ".join(rs))}</p></section>')
css='''<style>:root{--bg:#f7f3ea;--fg:#2a2a2a;--card:#fffdf8;--line:#e6dcc6;--acc:#1f5c46;--new:#e8f3ec}@media (prefers-color-scheme:dark){:root{--bg:#1b1a17;--fg:#ece6d8;--card:#24221e;--line:#3a362e;--acc:#7fc4a4;--new:#20352b}}body{background:var(--bg);color:var(--fg);font:17px/1.9 "Amiri","Noto Naskh Arabic",serif;margin:0;padding:16px}main{max-width:760px;margin:auto}h1{color:var(--acc);font-size:1.4em}section{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px 16px;margin:14px 0}h2{font-size:1.05em;margin:.2em 0}.ay{color:var(--acc)}.q{margin:.3em 0;padding:.3em .6em;border-right:3px solid var(--line);overflow-wrap:anywhere}.new{background:var(--new);border-color:var(--acc)}.lbl{font-weight:bold;font-size:.9em;margin-top:.5em}.why{font-size:.92em;opacity:.85}.v{font-size:.8em;padding:1px 8px;border-radius:9px;background:var(--line)}</style>'''
page=f'<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>عينة نسخة 2.4</title>{css}</head><body><main><h1>عينة ٥٠ تعديل قبل نشر نسخة ٢.٤</h1><p>اتختاروا عشوائيًا من الـ١٢٦٤ تعديل. كل نص جديد متقصوص من الكتاب حرف بحرف.</p>{"".join(out)}</main></body></html>'
open(SC+'/tam/final_sample.html','w').write(page); print(len(rows))
