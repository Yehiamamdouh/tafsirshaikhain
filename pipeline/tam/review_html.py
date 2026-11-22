import json,re,html
SC='/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
I=json.load(open(SC+'/tam/items.json'))
Q=json.load(open('/home/claude/tafsirshaikhain/src/data/simple.json'))
CH=json.load(open('/home/claude/tafsirshaikhain/src/data/chapters.json'))['chapters']
AR={
't46:14:IQ':'حذف كلمة «الثالث» من البداية لأنها بتشاور على وجهين مش ظاهرين.',
't2:3:IT':'الجملة لوحدها ممكن تتفهم إنها بتنفي الغيب، فاتضاف كلامه إن الله غيب عنا ومن الغيب المؤمَن به، لكنه ليس غائبًا.',
't2:136:IQ':'اتضاف قوله إن الآية دي هي الرد على ادعائهم ملة إبراهيم، لأن الجملة الحالية مش مربوطة بالآية.',
't9:7:IT':'الجملة بقت تبدأ من الآية عشان «فهؤلاء» يبان راجعة على مين.',
't18:54:IT':'«هذا الحديث» كان بيشاور على حديث علي وهو مش موجود، فاتضاف الحديث كنقطة أولى.',
't45:18:IQ':'اتضاف حكمه «فأمر بالأول، ونهى عن الثاني» اللي بيكمّل نفس الجملة.',
't26:197:IT':'بيبدأ بـ«وهذا غير شهادة أهل الكتاب» و«هذا» راجعة على كلام قبل بداية النص المتاح. معنى الآية نفسه واضح.',
't2:215:IQ':'المختصر كان مقطوع في نص الجملة عند «بالسياق،»، فاتكمّل لحد ما يوصل لجواب سؤالهم.',
't36:10:IQ':'المختصر مقدمة بس، والنص مقطوع قبل جواب ابن القيم نفسه.',
't33:71:IQ':'شيل آيات يوسف اللي في أوله ومالهاش علاقة، والمختصر بقى من الآيتين ٧٠ و٧١ لحد حكمه.',
't18:2:IQ':'«أنه» كانت مش واضحة راجعة على إيه، فاتضاف نص الآية اللي فيه «الكتاب».',
't29:64:IQ':'«والمراد» مكانش واضح المقصود بيها، فاتضافت الآية وتفسيره «دار الحياة التي لا موت فيها».',
't11:108:IT':'المختصر كان ناقصه أصل المعنى (السماوات والأرض هنا هي سماوات الجنة وأرضها)، واتقسم لنقطتين.',
't82:9:IT':'«فلهذا» و«هو» كانوا مش واضحين، فاتضاف تعريفه ليوم الدين اللي الكلام مبني عليه.',
't8:48:IT':'اتضافت النتيجة اللي بعده على طول: العقوبة على ترك الأمر، مش على عدم الاعتقاد.',
't50:20:IT':'«القيامتين» محتاجة الآيتين اللي قبلها (سكرة الموت والنفخ في الصور).',
't48:27:IQ':'اتضاف تفسيره لـ«فتحا قريبا» بإنه صلح الحديبية، ودي أهم نقطة في الآية.',
't17:1:IQ':'اتضاف نص الآية عشان «فذكره» يبان راجعة على مين.',
't4:11:IT':'المختصر كان المقدمة بس، واتضافت نقطة تانية فيها نتيجته: البنتين ليهم الثلثين.',
't2:210:IQ':'ابن القيم بينقل كلام ابن سينا ويقرّه، وابن سينا متذكر في بداية النص بعد كلام ملوش علاقة بالآية. محتاج يتقرر نكتب سطر سياق ولا لأ.',
't10:2:IT':'معنى كلمة «الإنذار» بس، والفكرة الأساسية مفهومة ضمنًا.',
't113:5:IT':'كلمة «أيضا» في المختصر.',
't41:35:IT':'الجملة مش بتذكر الآية صراحة.',
't21:69:IT':'«فسلب النار طبيعتها» قصيرة.',
}
VN={'كاف':'كافٍ','كافٍ':'كافٍ','إكمال':'يحتاج إكمال','استبدال':'يحتاج استبدال','لا يمكن':'لا يمكن إكماله (للمتخصص)'}
rows=[]
for i in range(1,5):
  for ln in open(f'{SC}/tam/out/P0{i}.txt'):
    f=[x.strip() for x in ln.split(' | ')]
    if len(f)<4 or f[0] not in AR: continue
    rows.append(f)
def esc(s): return html.escape(s)
out=[]
for n,(iid,vd,pr,rs) in enumerate(rows,1):
  it=I[iid]; su,v=it['su'],it['v']; xs=Q[str(su)]; x=xs[str(v)] if isinstance(xs,dict) else xs[v-1]; vt=x['text'] if isinstance(x,dict) else x
  cur=''.join(f'<p class="q">«{esc(e["t"])}»</p>' for e in it['ents'])
  prop=''
  if pr!='-':
    parts=re.findall(r'rec(\d+)\s*«(.*?)»(?=\s*(?:\+\+|$))',pr)
    prop='<div class="lbl">المقترح:</div>'+''.join(f'<p class="q new">«{esc(t)}»</p>' for _,t in parts)
  out.append(f'''<section><h2>{n}. {CH[su-1]["name"]} {v} — {"ابن تيمية" if it["a"]=="IT" else "ابن القيم"} <span class="v v{vd[:2]}">{VN[vd]}</span></h2>
<p class="ay">﴿{esc(vt)}﴾</p><div class="lbl">الحالي:</div>{cur}{prop}<p class="why">السبب: {esc(AR[iid])}</p></section>''')
page=f'''<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>عينة تجربة تمام المعنى</title>
<style>:root{{--bg:#f7f3ea;--fg:#2a2a2a;--card:#fffdf8;--line:#e6dcc6;--acc:#1f5c46;--new:#e8f3ec}}
@media (prefers-color-scheme:dark){{:root{{--bg:#1b1a17;--fg:#ece6d8;--card:#24221e;--line:#3a362e;--acc:#7fc4a4;--new:#20352b}}}}
body{{background:var(--bg);color:var(--fg);font:17px/1.9 "Amiri","Noto Naskh Arabic",serif;margin:0;padding:16px}}
main{{max-width:760px;margin:auto}}h1{{color:var(--acc);font-size:1.4em}}section{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px 16px;margin:14px 0}}
h2{{font-size:1.05em;margin:.2em 0}}.ay{{color:var(--acc)}}.q{{margin:.3em 0;padding:.3em .6em;border-right:3px solid var(--line)}}.new{{background:var(--new);border-color:var(--acc)}}
.lbl{{font-weight:bold;font-size:.9em;margin-top:.5em}}.why{{font-size:.92em;opacity:.85}}.v{{font-size:.8em;padding:1px 8px;border-radius:9px;background:var(--line);white-space:nowrap}}</style></head><body><main>
<h1>عينة تجربة «تمام المعنى للباحث»</h1>
<p>نتيجة الـ١٠٠ مختصر: ٨٠ كافٍ، ١٦ يحتاج إكمال، ١ يحتاج استبدال، ٣ لا يمكن إكمالهم. تحت كل التعديلات الـ٢٠، ومعاهم ٤ مختصرات اتحكم عليها بـ«كافٍ» بس عليها شوية شك. كل نص مقترح متقصوص من الكتاب حرف بحرف.</p>
{"".join(out)}</main></body></html>'''
open(SC+'/tam/pilot_review.html','w').write(page); print(len(rows))
