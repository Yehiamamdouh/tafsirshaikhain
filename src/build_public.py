"""Build the public site into REPO/public from site/ (data) + templates in pub/.
Pages: / (home), /tafsir.html (interactive app), /about.html, /surah/N.html, /ayah/S-V.html (static, indexable), sitemap.xml."""
import json, os, re, shutil, sys, glob, html
T=os.path.dirname(os.path.abspath(__file__))          # templates + scripts (repo/src)
DATA=os.environ.get('TS_DATA')                         # optional: folder with fresh s*.json/c*.json/si*.json; default = use public/ as-is
REPO=sys.argv[1]; P=os.path.join(REPO,'public'); os.makedirs(P,exist_ok=True)
BASE='https://tafsirshaikhain.com'
GA_ID=os.environ.get('GA_ID','G-ER9F5C2HC1')
GA=open(T+'/ga.html').read().replace('{{GA_ID}}',GA_ID)
SITEKEY=os.environ.get('TURNSTILE_SITEKEY','0x4AAAAAAFgr25YFTtOJHNYy')
NAMES=json.loads(re.search(r'\["الفاتحة".*?\]',open(T+'/app.html').read()).group(0))
AR=lambda n: str(n).translate(str.maketrans('0123456789','٠١٢٣٤٥٦٧٨٩'))
E=lambda s: html.escape(str(s), quote=True)
IMAM={'IT':'شيخ الإسلام ابن تيمية','IQ':'الإمام ابن القيم'}
Q=json.load(open(T+'/data/simple.json'))

# 1) data
for f in (glob.glob(DATA+'/*.json') if DATA else []): shutil.copy2(f,P)
idx=[];st={'ayat':set(),'IT':0,'IQ':0,'nuq':0,'books':set()}
SUR={}
for s in range(1,115):
    d=json.load(open(f'{DATA or P}/s{s}.json')); SUR[s]=d
    for b in d['books']: st['books'].add((b['a'],b['w']))
    for a,m in d.get('summ',{}).items():
        for v,l in m.items():
            st['ayat'].add((s,int(v))); st[a]+=1
            for x in l: idx.append([s,int(v),a,0,x['t']])
    for a,m in d.get('nuq',{}).items():
        for v,l in m.items():
            for x in l: st['nuq']+=1; idx.append([s,int(v),a,1,x.get('who',''),x['t']])
json.dump(idx,open(P+'/search.json','w'),ensure_ascii=False,separators=(',',':'))
stats={'ayat':len(st['ayat']),'IT':st['IT'],'IQ':st['IQ'],'nuq':st['nuq'],
       'booksIT':len({w for a,w in st['books'] if a=='IT'}),'booksIQ':len({w for a,w in st['books'] if a=='IQ'})}
json.dump(stats,open(P+'/stats.json','w'))

HEAD=open(T+'/head.html').read(); FOOT=open(T+'/footer.html').read()
def page(title,desc,path,body,jsonld=None):
    h=HEAD.replace('{{TITLE}}',E(title)).replace('{{DESC}}',E(desc)).replace('{{CANON}}',BASE+path).replace('{{GA}}',GA)
    h=h.replace('{{JSONLD}}','<script type="application/ld+json">'+json.dumps(jsonld,ensure_ascii=False)+'</script>' if jsonld else '')
    return h+body+FOOT+'\n</body>\n</html>\n'
def write(rel,txt):
    p=os.path.join(P,rel); os.makedirs(os.path.dirname(p),exist_ok=True); open(p,'w').write(txt)

# 2) interactive app -> tafsir.html
body=open(T+'/app.html').read()
body=body.replace('<title>الفاتحة عند الشيخين</title>\n','').replace('<meta name="claude:viewport-fit-sides" content="cover">\n','')
body=body.replace('<h1>تفسير الشيخين</h1>','<h1><a href="/" style="color:inherit;text-decoration:none">جامع تفسير الشيخين</a></h1>')
body=re.sub(r'\s*<details class="about">.*?</details>','\n  <p class="about-link"><a href="/about.html">عن المشروع ومنهج العمل</a> · <a href="/about.html#feedback">أرسل تصويبًا</a> · <button type="button" id="dlall" class="linkbtn">احفظ المصحف كله للقراءة دون إنترنت</button></p>',body,flags=re.S)
body=body.replace('})();\n</script>', open(T+'/patch.js').read()+'\n})();\n</script>')
style=re.search(r'<style>.*?</style>',body,re.S).group(0)
bios=re.search(r'<section class="shaykhs".*?</section>',open(T+'/home.html').read(),re.S).group(0)
body=re.sub(r'(<p class="lede">.*?</p>)',lambda m:m.group(1)+'\n    <details class="intro"><summary>التعريف بالشيخين</summary>'+bios+'</details>',body,count=1,flags=re.S)
write('tafsir.html',page('جامع تفسير الشيخين — تفسير القرآن بكلام ابن تيمية وابن القيم','تصفح معاني القرآن آية آية بكلام ابن تيمية وابن القيم: المختصر بنص كلامهما، والنصوص كاملة، وما نقلاه عن السلف.','/',body))

# 3) home
cnt={s:len({v for a in ('IT','IQ') for v in SUR[s].get('summ',{}).get(a,{})}) for s in range(1,115)}
suras=''.join(f'<a class="sura" href="/surah/{s}.html"><span><span class="n">{AR(s)}</span> <b>{E(NAMES[s-1])}</b></span><span class="c">{AR(cnt[s])} آية</span></a>' for s in range(1,115))
st_html=''.join(f'<div class="stat"><b>{AR(f"{n:,}")}</b><span>{l}</span></div>' for n,l in [(stats["ayat"],'آية لها مختصر'),(stats["IT"]+stats["IQ"],'مختصرًا بنص كلامهما'),(stats["nuq"],'نقلًا عن السلف'),(stats["booksIT"]+stats["booksIQ"],'كتابًا مصدرًا')])
home=open(T+'/home.html').read().replace('{{SURAS}}',suras).replace('{{STATS}}',st_html)
site_ld={"@context":"https://schema.org","@type":"WebSite","name":"جامع تفسير الشيخين","url":BASE+"/","inLanguage":"ar",
         "potentialAction":{"@type":"SearchAction","target":BASE+"/tafsir.html?q={q}","query-input":"required name=q"}}
write('index.html',page('جامع تفسير الشيخين — تفسير القرآن بكلام ابن تيمية وابن القيم',
      'جامع تفسير الشيخين: معاني القرآن الكريم بكلام شيخ الإسلام ابن تيمية والإمام ابن القيم، مختصر لكل آية بنص كلامهما مع الإحالة، والنصوص كاملة، وما نقلاه عن السلف، وبحث في المصحف كله.',
      '/',body,site_ld))

# 4) about
sc=json.load(open(T+'/scale.json'))
fmt=lambda n: AR(f'{n:,}')
scale_html=''.join(f'<div class="num"><b>{v}</b><span>{l}</span></div>' for v,l in [(fmt(sc['books']),'كتابًا مصدرًا للإمامين'),(fmt(round(sc['srcPages'],-2))+'+','صفحة مطبوعة فيها'),(AR(round(sc['srcWords']/1e6))+' مليون','كلمة قُرئت'),(fmt(round(sc['passages'],-2))+'+','موضعًا ذكرا فيه آية'),(fmt(sc['versesMentioned']),'آية ورد لهما فيها كلام'),(fmt(stats['ayat']),'آية لها مختصر حتى الآن'),(fmt(sc['summ']),'جملة في المختصرات'),(fmt(stats['nuq']),'نقلًا عن السلف والمفسرين')])
about=style+open(T+'/about.html').read().replace('{{SCALE}}',scale_html).replace('{{TURNSTILE_SITEKEY}}',SITEKEY)
write('about.html',page('عن المشروع — جامع تفسير الشيخين','الدافع ومنهج العمل والمصادر والقيمة المضافة لجامع تفسير الشيخين، ونموذج إرسال التصويبات.','/about.html',about))

write('privacy.html',page('الخصوصية وشروط الاستخدام — جامع تفسير الشيخين','حقوق النقل والاستخدام وسياسة الخصوصية في جامع تفسير الشيخين: النقل لنشر العلم مسموح والنقل للتربح ممنوع.','/privacy.html',style+open(T+'/privacy.html').read()))
# 5) static surah + verse pages (indexable)
def norm(t):
    t=re.sub(r'[ً-ٰٟۖ-ۭـ]','',t)
    t=re.sub('[إأآٱ]','ا',t).replace('ى','ي').replace('ة','ه').replace('ؤ','و').replace('ئ','ي')
    return ' '.join(re.sub(r'[^ء-ي ]',' ',t).split())
QN=[(int(c),i+1,' '+norm(x['text'])+' ') for c in Q for i,x in enumerate(Q[c])]
_cache={}
def cited(text):
    """Quran fragments in {..} inside the imam's text -> verse refs (only unambiguous matches)."""
    out=[]
    for frag in re.findall(r'\{([^{}]{8,})\}',text):
        f=norm(frag)
        if len(f.split())<3: continue
        if f not in _cache:
            hits=[(c,v) for c,v,t in QN if ' '+f+' ' in t]
            _cache[f]=hits[0] if len(hits)==1 or (hits and len(f.split())>=5) else None
        if _cache[f]: out.append(_cache[f])
    return out
def bslug(b): return re.sub(r'[^A-Za-z0-9]+','-',b['w']).strip('-')
def ref(d,x):
    b=d['books'][x['b']]; return f'<a href="/book/{bslug(b)}.html">«{E(b["t"])}»</a>'+(' '+AR(x['v'])+'/' if x.get('v') else ' ')+AR(x['p'])
def crumbs_ld(items):
    return {"@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":i+1,"name":n,"item":BASE+u} for i,(n,u) in enumerate(items)]}
AUTH={'IT':{"@type":"Person","name":"أحمد بن عبد الحليم ابن تيمية","alternateName":"شيخ الإسلام ابن تيمية"},
      'IQ':{"@type":"Person","name":"محمد بن أبي بكر ابن قيم الجوزية","alternateName":"ابن القيم"}}
# verse pages are regenerated from scratch so a verse whose summaries moved away doesn't keep a stale page
shutil.rmtree(P+'/ayah',ignore_errors=True)
urls=['/','/about.html','/privacy.html']
pages={(s,v) for s in range(1,115) for k in ('summ','nuq') for a in ('IT','IQ') for v in map(int,SUR[s].get(k,{}).get(a,{})) if v>=1}
BOOKS={}   # slug -> {'b':book,'v':set((s,v))}
for s in range(1,115):
    d=SUR[s]; name=NAMES[s-1]; verses=[v['text'] for v in Q[str(s)]]
    have=sorted(v for (ss,v) in pages if ss==s)
    for v in have:
        parts=[]; first=''; firsta=''; rel=[]; who=[]
        for a in ('IT','IQ'):
            pts=d.get('summ',{}).get(a,{}).get(str(v),[]); nq=d.get('nuq',{}).get(a,{}).get(str(v),[])
            if not pts and not nq: continue
            who.append(a)
            sec=f'<section><h2>{IMAM[a]}</h2>'
            for x in pts:
                if not first: first,firsta=x['t'],a
                rel+=cited(x['t'])
                sec+=f'<blockquote>{E(x["t"])}<cite>{ref(d,x)}</cite></blockquote>'
            if nq:
                sec+='<h3>ما نقله عن غيره</h3>'
                for x in nq:
                    sec+=f'<blockquote><span class="who">{E(x.get("who",""))}</span> <span class="st">{E(x.get("st",""))}</span><br>«{E(x["t"])}»'+(f'<br><b>تعقيبه:</b> {E(x["rt"])}' if x.get('rt') else '')+f'<cite>{ref(d,x)}</cite></blockquote>'
            for x in pts+nq:
                b=d['books'][x['b']]; BOOKS.setdefault(bslug(b),{'b':b,'v':set()})['v'].add((s,v))
            parts.append(sec+'</section>')
        rel=[r for r in dict.fromkeys(rel) if r!=(s,v)]
        relh=''
        if rel:
            relh='<section><h3>آيات ذكرها في كلامه هنا</h3><div class="rel">'+''.join(
                (f'<a href="/ayah/{c}-{w}.html">' if (c,w) in pages else '<span>')+f'{E(NAMES[c-1])} {AR(w)}'+('</a>' if (c,w) in pages else '</span>') for c,w in rel[:24])+'</div></section>'
        vt=verses[v-1]; short=' '.join(vt.split()[:7])+('…' if len(vt.split())>7 else '')
        title=f'تفسير {short} [{name}: {v}] — ابن تيمية وابن القيم'
        desc=((('قال ابن تيمية: ' if firsta=='IT' else 'قال ابن القيم: ')+first) if first else f'تفسير قوله تعالى ﴿{vt}﴾ بكلام ابن تيمية وابن القيم')[:155]
        i=have.index(v); prv=have[i-1] if i>0 else None; nxt=have[i+1] if i+1<len(have) else None
        nav='<div class="pn">'+(f'<a href="/ayah/{s}-{prv}.html">→ الآية {AR(prv)}</a>' if prv else '<span></span>')+(f'<a href="/ayah/{s}-{nxt}.html">الآية {AR(nxt)} ←</a>' if nxt else '')+'</div>'
        body=(style+f'<main class="sp"><nav class="crumbs"><a href="/">الرئيسية</a> › <a href="/surah/{s}.html">سورة {E(name)}</a> › الآية {AR(v)}</nav>'
              f'<h1>تفسير قوله تعالى في سورة {E(name)}، الآية {AR(v)}</h1><p class="vt">﴿{E(vt)}﴾</p>'+''.join(parts)+relh+
              f'<a class="btn pri open" href="/tafsir.html#s{s}a{v}">افتح الآية في التفسير التفاعلي (النصوص كاملة)</a>'+nav+'</main>'+'<script src="/share.js"></script>')
        ld={"@context":"https://schema.org","@graph":[
            {"@type":"Article","headline":title[:110],"description":desc,"inLanguage":"ar","url":BASE+f'/ayah/{s}-{v}.html',
             "mainEntityOfPage":BASE+f'/ayah/{s}-{v}.html',"image":BASE+"/og.png","about":f"سورة {name}، الآية {v}",
             "author":[AUTH[a] for a in who],"isPartOf":{"@type":"WebSite","name":"جامع تفسير الشيخين","url":BASE+"/"}},
            crumbs_ld([('الرئيسية','/'),(f'سورة {name}',f'/surah/{s}.html'),(f'الآية {v}',f'/ayah/{s}-{v}.html')])]}
        write(f'ayah/{s}-{v}.html',page(title,desc,f'/ayah/{s}-{v}.html',body,ld)); urls.append(f'/ayah/{s}-{v}.html')
    vl=''.join(f'<a class="vrow" href="/ayah/{s}-{v}.html"><b>{AR(v)}</b> <span>{E(" ".join(verses[v-1].split()[:8]))}…</span></a>' for v in have)
    sp=(style+f'<main class="sp"><nav class="crumbs"><a href="/">الرئيسية</a> › سورة {E(name)}</nav><h1>تفسير سورة {E(name)} عند ابن تيمية وابن القيم</h1>'
        f'<section><p>الآيات التي جُمع فيها كلام الشيخين من سورة {E(name)} ({AR(len(have))} من {AR(len(verses))} آية):</p><div class="vrows">{vl or "—"}</div></section>'
        f'<a class="btn pri open" href="/tafsir.html#s{s}a{1 if s>1 else 0}">افتح السورة في التفسير التفاعلي</a></main>')
    sld={"@context":"https://schema.org","@graph":[{"@type":"CollectionPage","name":f'تفسير سورة {name} — ابن تيمية وابن القيم',"inLanguage":"ar","url":BASE+f'/surah/{s}.html'},
         crumbs_ld([('الرئيسية','/'),(f'سورة {name}',f'/surah/{s}.html')])]}
    write(f'surah/{s}.html',page(f'تفسير سورة {name} — ابن تيمية وابن القيم',f'كلام شيخ الإسلام ابن تيمية والإمام ابن القيم في تفسير {AR(len(have))} آية من سورة {name}، بنص كلامهما مع الإحالة إلى الكتاب والصفحة.',f'/surah/{s}.html',sp,sld))
    urls.append(f'/surah/{s}.html')
# source-book pages: every verse a book is cited for
shutil.rmtree(P+'/book',ignore_errors=True)
blist=[]
for slug,o in sorted(BOOKS.items(),key=lambda kv:(kv[1]['b']['a'],-len(kv[1]['v']))):
    b=o['b']; vs=sorted(o['v']); au=IMAM[b['a']]
    rows=''.join(f'<a class="vrow" href="/ayah/{c}-{w}.html"><b>{E(NAMES[c-1])} {AR(w)}</b> <span>{E(" ".join(Q[str(c)][w-1]["text"].split()[:7]))}…</span></a>' for c,w in vs)
    body=(style+f'<main class="sp"><nav class="crumbs"><a href="/">الرئيسية</a> › <a href="/books.html">المصادر</a> › {E(b["t"])}</nav>'
          f'<h1>«{E(b["t"])}» — {au}</h1><section><p>الطبعة المعتمدة: {E(b.get("ed","—"))}</p><p>الآيات التي نُقل كلام {au} فيها من هذا الكتاب ({AR(len(vs))} آية):</p><div class="vrows">{rows}</div></section></main>')
    ld={"@context":"https://schema.org","@graph":[{"@type":"Book","name":b['t'],"author":AUTH[b['a']],"inLanguage":"ar","url":BASE+f'/book/{slug}.html'},
        crumbs_ld([('الرئيسية','/'),('المصادر','/books.html'),(b['t'],f'/book/{slug}.html')])]}
    write(f'book/{slug}.html',page(f'تفسير الآيات في كتاب {b["t"]} — {au}',f'الآيات التي فسّرها {au} في كتابه «{b["t"]}» ({len(vs)} آية)، بنص كلامه مع الإحالة إلى الجزء والصفحة.',f'/book/{slug}.html',body,ld))
    urls.append(f'/book/{slug}.html'); blist.append((b['a'],slug,b['t'],len(vs)))
bl=''.join(f'<section><h2>{IMAM[a]}</h2><div class="vrows">'+''.join(f'<a class="vrow bk" href="/book/{sl}.html"><b>{E(t)}</b> <span>{AR(n)} آية</span></a>' for aa,sl,t,n in blist if aa==a)+'</div></section>' for a in ('IT','IQ'))
write('books.html',page('مصادر جامع تفسير الشيخين — كتب ابن تيمية وابن القيم','كتب شيخ الإسلام ابن تيمية والإمام ابن القيم التي جُمع منها تفسيرهما، مع الآيات المنقولة من كل كتاب.','/books.html',
      style+f'<main class="sp"><nav class="crumbs"><a href="/">الرئيسية</a> › المصادر</nav><h1>المصادر</h1>'+bl+'</main>'))
urls.append('/books.html')
nf=page('الصفحة غير موجودة — جامع تفسير الشيخين','الصفحة المطلوبة غير موجودة.','/404.html',
        style+'<main class="sp"><h1>الصفحة غير موجودة</h1><p lang="en" dir="ltr">Page not found.</p><a class="btn pri open" href="/">الرئيسية · Home</a></main>')
write('404.html',nf.replace('<link rel="canonical" href="'+BASE+'/404.html">','<meta name="robots" content="noindex">'))
shutil.copy2(T+'/og.png',P)
sm='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'<url><loc>{BASE}{u}</loc></url>\n' for u in urls)+'</urlset>\n'
open(P+'/sitemap.xml','w').write(sm)
open(P+'/robots.txt','w').write(f'User-agent: *\nAllow: /\nDisallow: /api/\nSitemap: {BASE}/sitemap.xml\n')

# 6) static assets
for f in ('worker.js','wrangler.jsonc'): shutil.copy2(T+'/'+f,REPO)
for f in ('i18n.js','qsuggest.js','share.js','quran_clean.json','theme.css','sw.js','manifest.webmanifest','icon.svg','icon-192.png','icon-512.png','_headers'):
    if os.path.exists(T+'/'+f): shutil.copy2(T+'/'+f,P)
os.makedirs(P+'/i18n',exist_ok=True); os.makedirs(P+'/st',exist_ok=True)
for f in glob.glob(T+'/i18n/*.json'): shutil.copy2(f,P+'/i18n')
for f in glob.glob(T+'/st/*.json'): shutil.copy2(f,P+'/st')
print('built; pages',len(urls),'stats',stats)
import subprocess; subprocess.run([sys.executable,T+'/build_langs.py',REPO],check=True)
