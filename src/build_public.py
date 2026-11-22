"""Build the public site into REPO/public from site/ (data) + templates in pub/.
Pages: / (home), /tafsir.html (interactive app), /about.html, /surah/N.html, /ayah/S-V.html (static, indexable), sitemap.xml."""
import sys; sys.path.insert(0,__import__('os').path.dirname(__file__)); from edfix import fx
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
idx=[];st={'ayat':set(),'IT':0,'IQ':0,'nuq':0,'books':set(),'summN':0}
SUR={}
for s in range(1,115):
    d=json.load(open(f'{DATA or P}/s{s}.json')); SUR[s]=d
    for b in d['books']: st['books'].add((b['a'],b['w']))
    for a,m in d.get('summ',{}).items():
        for v,l in m.items():
            st['ayat'].add((s,int(v))); st[a]+=1
            for x in l: idx.append([s,int(v),a,0,x['t']]); st['summN']+=1
    for a,m in d.get('nuq',{}).items():
        for v,l in m.items():
            for x in l: st['nuq']+=1; idx.append([s,int(v),a,1,x.get('who',''),x['t']])
json.dump(idx,open(P+'/search.json','w'),ensure_ascii=False,separators=(',',':'))
stats={'ayat':len(st['ayat']),'IT':st['IT'],'IQ':st['IQ'],'nuq':st['nuq'],
       'booksIT':len({w for a,w in st['books'] if a=='IT'}),'booksIQ':len({w for a,w in st['books'] if a=='IQ'})}
json.dump(stats,open(P+'/stats.json','w'))

HEAD=open(T+'/head.html').read(); FOOT=open(T+'/footer.html').read()
ORG={"@type":"Organization","@id":BASE+"/#org","name":"جامع تفسير الشيخين","url":BASE+"/","logo":BASE+"/icon-512.png",
     "description":"جمع كلام شيخ الإسلام ابن تيمية والإمام ابن القيم في تفسير القرآن من كتبهما، بنصه مع الإحالة إلى الكتاب والجزء والصفحة.",
     "publishingPrinciples":BASE+"/about.html",
     "member":{"@type":"Person","name":"يحيى دسوقي","jobTitle":"المشرف العلمي","description":"طالب علوم القرآن والعلوم الشرعية في أكثر من أكاديمية"}}
ORG_LD='<script type="application/ld+json">'+json.dumps({"@context":"https://schema.org","@graph":[ORG,{"@type":"WebSite","@id":BASE+"/#site","name":"جامع تفسير الشيخين","url":BASE+"/","inLanguage":"ar","publisher":{"@id":BASE+"/#org"}}]},ensure_ascii=False)+'</script>\n'
def page(title,desc,path,body,jsonld=None):
    h=HEAD.replace('{{TITLE}}',E(title)).replace('{{DESC}}',E(desc)).replace('{{CANON}}',BASE+path).replace('{{GA}}',GA)
    h=h.replace('{{JSONLD}}',ORG_LD+('<script type="application/ld+json">'+json.dumps(jsonld,ensure_ascii=False)+'</script>' if jsonld else ''))
    return h+body+FOOT+'\n</body>\n</html>\n'
def write(rel,txt):
    p=os.path.join(P,rel); os.makedirs(os.path.dirname(p),exist_ok=True); open(p,'w').write(txt)
# sitemap <lastmod>: per-URL hash of the <main> content, kept in src/data/lastmod.json (shared with build_langs.py)
import hashlib, datetime
TODAY=datetime.date.today().isoformat()
LM_F=T+'/data/lastmod.json'; LM=json.load(open(LM_F)) if os.path.exists(LM_F) else {}
def touch(url,txt):
    m=re.search(r'<main\b.*</main>',txt,re.S); h=hashlib.sha1((m.group(0) if m else txt).encode()).hexdigest()[:10]
    if LM.get(url,[None])[0]!=h: LM[url]=[h,TODAY]

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
# the home page is the interactive app; add a plain-link surah index under it so crawlers reach /surah/N.html
sidx=('<section class="sura-index" aria-labelledby="suras-h" style="width:100%;max-width:1100px;box-sizing:border-box;margin:24px auto 0;padding:0 16px">'
      '<h2 id="suras-h" style="font-size:20px;margin:0 0 12px">فهرس السور</h2><nav class="suras" aria-label="فهرس السور" style="grid-template-columns:repeat(auto-fill,minmax(140px,1fr))">'+suras+'</nav></section>')
mline=re.search(r'<main id="main".*?</main>',body,re.S).group(0)
body_home=body.replace(mline,mline+'\n  '+sidx,1)
write('index.html',page('جامع تفسير الشيخين — تفسير القرآن بكلام ابن تيمية وابن القيم',
      'جامع تفسير الشيخين: معاني القرآن الكريم بكلام شيخ الإسلام ابن تيمية والإمام ابن القيم، مختصر لكل آية بنص كلامهما مع الإحالة، والنصوص كاملة، وما نقلاه عن السلف، وبحث في المصحف كله.',
      '/',body_home,site_ld))

# 4) about
sc=json.load(open(T+'/scale.json'))
fmt=lambda n: AR(f'{n:,}')
scale_html=''.join(f'<div class="num"><b>{v}</b><span>{l}</span></div>' for v,l in [(fmt(sc['books']),'كتابًا مصدرًا للإمامين'),(fmt(round(sc['srcPages'],-2))+'+','صفحة مطبوعة فيها'),(AR(round(sc['srcWords']/1e6))+' مليون','كلمة قُرئت'),(fmt(round(sc['passages'],-2))+'+','موضعًا ذكرا فيه آية'),(fmt(sc['versesMentioned']),'آية ورد لهما فيها كلام'),(fmt(stats['ayat']),'آية لها مختصر حتى الآن'),(fmt(st['summN']),'جملة في المختصرات'),(fmt(stats['nuq']),'نقلًا عن السلف والمفسرين')])
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
TASH=re.compile('[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED\u0640]')
def plain(t): return TASH.sub('',t).replace('\u0671','ا')
def refr(d,r):
    b=d['books'][r['b']]; pg=AR(r['p'])+('–'+AR(r['pe']) if r.get('pe') and r['pe']!=r['p'] else '')
    return f'<a href="/book/{bslug(b)}.html">«{E(b["t"])}»</a> '+(AR(r['v'])+'/' if r.get('v') else '')+pg
def full_html(d,items):
    # the source paragraphs the excerpts above were taken from, verbatim from the data (same text the app shows)
    B=d.setdefault('_byid',{r['id']:r for r in d['recs']}); seen=[]
    for x in items:
        for k in ('r','rr'):
            try: rid=int(x.get(k))
            except (TypeError,ValueError): continue
            if rid in B and rid not in seen: seen.append(rid)
    if not seen: return ''
    out=''.join('<div class="fp">'+(f'<b class="fh">{E(B[i]["h"])}</b>' if B[i].get('h') else '')+'<p>'+fx(E(B[i]['t'])).replace('\n','<br>')+f'</p><cite>{refr(d,B[i])}</cite></div>' for i in seen)
    return f'<details class="full"><summary>النص الكامل للفقرة التي أُخذ منها الكلام ({AR(len(seen))})</summary>{out}</details>'
# verse pages are regenerated from scratch so a verse whose summaries moved away doesn't keep a stale page
shutil.rmtree(P+'/ayah',ignore_errors=True)
# التفسير الميسر (QuranEnc, unmodified): the overall meaning on every static verse page, after the imams' words
MYD=json.load(open(T+'/data/arabic_moyassar.json'))
def muy_html(s,v):
    r=MYD['verses'][str(s)].get(str(v)) or {}
    if not r.get('text'): return ''
    fn=f'<p class="muy-fn">{E(r["footnotes"])}</p>' if r.get('footnotes') else ''
    return ('<div class="muy"><div class="muy-head"><b>التفسير الميسر</b><small>المعنى الإجمالي للآية من «التفسير الميسر»، وليس من كلام الشيخين</small></div>'
            f'<p class="muy-text">{E(r["text"])}</p>{fn}<a class="muy-credit" href="https://quranenc.com/ar/browse/arabic_moyassar" target="_blank" rel="noopener">'
            f'التفسير الميسر، مجمع الملك فهد لطباعة المصحف الشريف — الإصدار {E(MYD["edition"]["version"])} · QuranEnc.com</a></div>')
# well-known names people search by (used in the verse page title/h1)
FAMOUS={(2,255):'آية الكرسي',(2,285):'خواتيم سورة البقرة',(2,286):'خواتيم سورة البقرة',(24,35):'آية النور',(2,282):'آية الدين',
        (5,6):'آية الوضوء',(3,61):'آية المباهلة',(33,33):'آية التطهير',(5,3):'آية إكمال الدين',(7,172):'آية الميثاق',
        (33,53):'آية الحجاب',(9,5):'آية السيف',(2,183):'آية الصيام',(4,11):'آية المواريث',(4,12):'آية المواريث',
        (4,176):'آية الكلالة',(16,90):'آية العدل والإحسان',(17,23):'آية بر الوالدين',(2,256):'آية لا إكراه في الدين',(39,53):'آية الرجاء'}
urls=['/','/about.html','/privacy.html']
pages={(s,v) for s in range(1,115) for k in ('summ','nuq') for a in ('IT','IQ') for v in map(int,SUR[s].get(k,{}).get(a,{})) if v>=1}
THIN=120; THIN_N=[]
BOOKS={}   # slug -> {'b':book,'v':set((s,v))}
# passages (content session's src/make_groups.py -> public/groups.json): consecutive verses sharing one excerpt get one
# page /passage/S-A-B.html; the single verse pages inside stay, with their canonical pointing at the passage
if os.path.exists(T+'/make_groups.py'):
    import subprocess; subprocess.run([sys.executable,T+'/make_groups.py',REPO],check=True,stdout=subprocess.DEVNULL)
GROUPS=json.load(open(P+'/groups.json')) if os.path.exists(P+'/groups.json') else []
GOF={}
for g in GROUPS:
    if all((g['su'],v) in pages for v in range(g['from'],g['to']+1)):
        for v in range(g['from'],g['to']+1): GOF[(g['su'],v)]=(g['from'],g['to'])
def curl(c,w):
    g=GOF.get((c,w)); return f'/passage/{c}-{g[0]}-{g[1]}.html' if g else f'/ayah/{c}-{w}.html'
shutil.rmtree(P+'/passage',ignore_errors=True)
METH='<p class="meth">كلام الإمامين منقول بنصه من كتبهما مع الإحالة إلى الجزء والصفحة، ومطابَق آليًا مع أصله. <a href="/about.html">منهج العمل والمصادر</a></p>'
def sections(d,s,vs,books=True):
    """the imams' sections for one verse or a passage (an excerpt repeated across its verses is shown once)"""
    parts=[]; first=''; firsta=''; rel=[]; who=[]
    for a in ('IT','IQ'):
        pts=[]; nq=[]; seen=set()
        for v in vs:
            for x in d.get('summ',{}).get(a,{}).get(str(v),[]):
                if ('s',x['t']) not in seen: seen.add(('s',x['t'])); pts.append(x)
            for x in d.get('nuq',{}).get(a,{}).get(str(v),[]):
                k=('n',x.get('who',''),x['t'])
                if k not in seen: seen.add(k); nq.append(x)
            if books:
                for x in d.get('summ',{}).get(a,{}).get(str(v),[])+d.get('nuq',{}).get(a,{}).get(str(v),[]):
                    b=d['books'][x['b']]; BOOKS.setdefault(bslug(b),{'b':b,'v':set()})['v'].add((s,v))
        if not pts and not nq: continue
        who.append(a)
        sec=f'<section><h2>{IMAM[a]}</h2>'
        for x in pts:
            if not first: first,firsta=fx(x['t'],False),a
            rel+=cited(x['t'])
            sec+=f'<blockquote>{fx(E(x["t"]))}'+(f'<small class="pcx">{E(x["cx"])}</small>' if x.get('cx') else '')+f'<cite>{ref(d,x)}</cite></blockquote>'
        if nq:
            sec+='<h3>ما نقله عن غيره</h3>'
            for x in nq:
                sec+=f'<blockquote><span class="who">{E(x.get("who",""))}</span> <span class="st">{E(x.get("st",""))}</span><br>«{fx(E(x["t"]))}»'+(f'<br><b>تعقيبه:</b> {fx(E(x["rt"]))}' if x.get('rt') else '')+f'<cite>{ref(d,x)}</cite></blockquote>'
        sec+=full_html(d,pts+nq)
        # verses the source paragraphs are linked to (record "ay")
        B=d.setdefault('_byid',{r['id']:r for r in d['recs']})
        for x in pts+nq:
            try: r=B.get(int(x.get('r')))
            except (TypeError,ValueError): r=None
            if r and len(r.get('ay') or [])<=8: rel+=[(s,w) for w in r['ay'] if w]   # skip paragraphs about a whole surah
        parts.append(sec+'</section>')
    rel=[r for r in dict.fromkeys(rel) if not (r[0]==s and r[1] in vs)]
    relh=''
    if rel:
        relh='<section><h3>آيات متصلة في كلام الإمامين هنا</h3><div class="rel">'+''.join(
            (f'<a href="{curl(c,w)}">' if (c,w) in pages else '<span>')+f'{E(NAMES[c-1])} {AR(w)}'+('</a>' if (c,w) in pages else '</span>') for c,w in rel[:30])+'</div></section>'
    return parts,first,firsta,relh,who
def nav_of(s,have,lo,hi):
    prv=max([w for w in have if w<lo],default=None); nxt=min([w for w in have if w>hi],default=None)
    lab=lambda w: (f'الآيات {AR(GOF[(s,w)][0])}–{AR(GOF[(s,w)][1])}' if (s,w) in GOF else f'الآية {AR(w)}')
    return '<div class="pn">'+(f'<a href="{curl(s,prv)}">→ {lab(prv)}</a>' if prv else '<span></span>')+(f'<a href="{curl(s,nxt)}">{lab(nxt)} ←</a>' if nxt else '')+'</div>'
def words_of(body):
    return len(re.sub(r'<[^>]+>',' ',re.sub(r'<(script|style)\b.*?</\1>','',re.search(r'<main\b.*?</main>',body,re.S).group(0),flags=re.S)).split())
PASS_N=0
# topic index (content session: public/topics.json) — a classification only: every item points at an existing excerpt
# {su,v,a,i,kind:'summ'|'nuq',t0}; t0 (first 40 chars) must match the excerpt or the item is skipped with a warning
TOPICS=json.load(open(P+'/topics.json')) if os.path.exists(P+'/topics.json') else []
TOPIC_MIN=5; TOPIC_OF={}; TOPIC_BAD=[]
for tp in TOPICS:
    ok=[]
    for it in tp.get('items',[]):
        try: x=SUR[it['su']][it.get('kind','summ')][it['a']][str(it['v'])][it['i']]
        except (KeyError,IndexError,TypeError): x=None
        if not x or (it.get('t0') and not x['t'].startswith(it['t0'])): TOPIC_BAD.append((tp['id'],it)); continue
        ok.append((it['su'],it['v'],it['a'],it.get('kind','summ'),x))
    tp['_ok']=sorted(ok,key=lambda q:(q[2],q[0],q[1]))
    tp['_page']=len(ok)>=TOPIC_MIN
    for q in ok: TOPIC_OF.setdefault((q[0],q[1]),[]).append(tp)
def topic_tags(keys):
    tl=[]; 
    for k in keys:
        for tp in TOPIC_OF.get(k,[]):
            if tp not in tl: tl.append(tp)
    if not tl: return ''
    return '<p class="ttags"><b>الموضوعات:</b> '+' '.join(f'<a href="/topic/{tp["id"]}.html">{E(tp["title"])}</a>' if tp['_page'] else f'<a href="/topics.html#{tp["id"]}">{E(tp["title"])}</a>' for tl_ in [tl] for tp in tl_)+'</p>'
for s in range(1,115):
    d=SUR[s]; name=NAMES[s-1]; verses=[v['text'] for v in Q[str(s)]]
    have=sorted(v for (ss,v) in pages if ss==s)
    for v in have:
        parts,first,firsta,relh,who=sections(d,s,[v])
        vt=verses[v-1]; pw=plain(vt).split(); short=' '.join(pw[:5])+('…' if len(pw)>5 else '')
        fam=FAMOUS.get((s,v))
        title=f'تفسير {fam or short} ({name} {v}) — ابن تيمية وابن القيم'
        lead=f'تفسير سورة {name} الآية {v}: '
        desc=(lead+((('قال ابن تيمية: ' if firsta=='IT' else 'قال ابن القيم: ')+first) if first else f'﴿{plain(vt)}﴾ بكلام ابن تيمية وابن القيم'))[:155]
        g=GOF.get((s,v))
        note=(f'<p class="pnote">هذه الآية من مقطع شرحه الإمام بكلام واحد: <a href="/passage/{s}-{g[0]}-{g[1]}.html">تفسير الآيات {AR(g[0])}–{AR(g[1])} معًا</a></p>' if g else '')
        body=(style+f'<main class="sp"><nav class="crumbs"><a href="/">الرئيسية</a> › <a href="/surah/{s}.html">سورة {E(name)}</a> › الآية {AR(v)}</nav>'
              f'<h1>تفسير قوله تعالى في سورة {E(name)}، الآية {AR(v)}'+(f' — {E(fam)}' if fam else '')+f'</h1><p class="vt">﴿{E(vt)}﴾</p>'+note+''.join(parts)+METH+topic_tags([(s,v)])+muy_html(s,v)+relh+
              f'<a class="btn pri open" href="/tafsir.html#s{s}a{v}">افتح الآية في التفسير التفاعلي (كل النصوص والنقول)</a>'+nav_of(s,have,v,v)+'</main>'+'<script src="/share.js"></script>')
        ld={"@context":"https://schema.org","@graph":[
            {"@type":"Article","headline":title[:110],"description":desc,"inLanguage":"ar","url":BASE+f'/ayah/{s}-{v}.html',
             "mainEntityOfPage":BASE+f'/ayah/{s}-{v}.html',"image":BASE+"/og.png","about":f"سورة {name}، الآية {v}",
             "author":[AUTH[a] for a in who],"isPartOf":{"@id":BASE+"/#site"},"publisher":{"@id":BASE+"/#org"}},
            crumbs_ld([('الرئيسية','/'),(f'سورة {name}',f'/surah/{s}.html'),(f'الآية {v}',f'/ayah/{s}-{v}.html')])]}
        if g:   # canonical -> the passage page; the passage is what goes in the sitemap
            html_=page(title,desc,f'/passage/{s}-{g[0]}-{g[1]}.html',body,ld)
        else:
            html_=page(title,desc,f'/ayah/{s}-{v}.html',body,ld)
            # very short verse pages stay readable but out of search engines until the site's standing recovers (Nov 2026)
            if words_of(body)<THIN: html_=html_.replace('<link rel="canonical"','<meta name="robots" content="noindex,follow">\n<link rel="canonical"',1); THIN_N.append(f'{s}-{v}')
            else: urls.append(f'/ayah/{s}-{v}.html')
        write(f'ayah/{s}-{v}.html',html_)
    for (gs,lo),hi in sorted({(k[0],gv[0]):gv[1] for k,gv in GOF.items() if k[0]==s}.items()):
        vs=list(range(lo,hi+1)); parts,first,firsta,relh,who=sections(d,s,vs,books=False)
        pw=plain(verses[lo-1]).split(); short=' '.join(pw[:5])+('…' if len(pw)>5 else '')
        fam=next((FAMOUS[(s,w)] for w in vs if (s,w) in FAMOUS),None)
        title=f'تفسير {fam or short} ({name} {lo}–{hi}) — ابن تيمية وابن القيم'
        desc=(f'تفسير سورة {name} الآيات {lo}–{hi}: '+((('قال ابن تيمية: ' if firsta=='IT' else 'قال ابن القيم: ')+first) if first else ''))[:155]
        vts=''.join(f'<p class="vt">﴿{E(verses[w-1])}﴾ <span class="vn">({AR(w)})</span></p>' for w in vs)
        mrows=[]   # one Muyassar box for the passage; identical consecutive texts are merged under one verse range
        for w in vs:
            r=MYD['verses'][str(s)].get(str(w)) or {}
            if not r.get('text'): continue
            if mrows and mrows[-1][2]==r['text'] and mrows[-1][1]==w-1: mrows[-1][1]=w
            else: mrows.append([w,w,r['text'],r.get('footnotes')])
        muys=('<div class="muy"><div class="muy-head"><b>التفسير الميسر</b><small>المعنى الإجمالي للآيات من «التفسير الميسر»، وليس من كلام الشيخين</small></div>'
              +''.join(f'<p class="muy-text"><b>({AR(a_)}'+(f'–{AR(b_)}' if b_!=a_ else '')+f')</b> {E(t_)}</p>'+(f'<p class="muy-fn">{E(fn_)}</p>' if fn_ else '') for a_,b_,t_,fn_ in mrows)
              +f'<a class="muy-credit" href="https://quranenc.com/ar/browse/arabic_moyassar" target="_blank" rel="noopener">التفسير الميسر، مجمع الملك فهد لطباعة المصحف الشريف — الإصدار {E(MYD["edition"]["version"])} · QuranEnc.com</a></div>') if mrows else ''
        vlinks='<p class="pnote">الآيات منفردة: '+' · '.join(f'<a href="/ayah/{s}-{w}.html">الآية {AR(w)}</a>' for w in vs)+'</p>'
        path=f'/passage/{s}-{lo}-{hi}.html'
        body=(style+f'<main class="sp"><nav class="crumbs"><a href="/">الرئيسية</a> › <a href="/surah/{s}.html">سورة {E(name)}</a> › الآيات {AR(lo)}–{AR(hi)}</nav>'
              f'<h1>تفسير قوله تعالى في سورة {E(name)}، الآيات {AR(lo)}–{AR(hi)}'+(f' — {E(fam)}' if fam else '')+f'</h1>{vts}'+''.join(parts)+METH+topic_tags([(s,w) for w in vs])+muys+relh+vlinks+
              f'<a class="btn pri open" href="/tafsir.html#s{s}a{lo}">افتح الآيات في التفسير التفاعلي (كل النصوص والنقول)</a>'+nav_of(s,have,lo,hi)+'</main>'+'<script src="/share.js"></script>')
        ld={"@context":"https://schema.org","@graph":[
            {"@type":"Article","headline":title[:110],"description":desc,"inLanguage":"ar","url":BASE+path,"mainEntityOfPage":BASE+path,"image":BASE+"/og.png",
             "about":f"سورة {name}، الآيات {lo}–{hi}","author":[AUTH[a] for a in who],"isPartOf":{"@id":BASE+"/#site"},"publisher":{"@id":BASE+"/#org"}},
            crumbs_ld([('الرئيسية','/'),(f'سورة {name}',f'/surah/{s}.html'),(f'الآيات {lo}–{hi}',path)])]}
        write(path[1:],page(title,desc,path,body,ld)); urls.append(path); PASS_N+=1
    def lead_of(v):
        for a in ('IT','IQ'):
            l=d.get('summ',{}).get(a,{}).get(str(v),[])
            if l:
                t=fx(l[0]['t'],False); cut=t if len(t)<=220 else t[:220].rsplit(' ',1)[0]+'…'
                return f'<p class="vsum"><b>{"ابن تيمية" if a=="IT" else "ابن القيم"}:</b> {E(cut)}</p>'
        return ''
    vl=''.join(f'<div class="vitem"><a class="vrow" href="{curl(s,v)}"><b>{AR(v)}</b> <span>{E(" ".join(verses[v-1].split()[:8]))}…</span></a>{lead_of(v)}</div>' for v in have)
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
# 6c) updates page (version history + live numbers)
UPD=json.load(open(T+'/updates.json'))
AV=lambda v: AR(v).replace('.','٫')
AD=lambda d: AR(d[8:10].lstrip('0'))+' '+['يناير','فبراير','مارس','أبريل','مايو','يونيو','يوليو','أغسطس','سبتمبر','أكتوبر','نوفمبر','ديسمبر'][int(d[5:7])-1]+' '+AR(d[:4])
nums=''.join(f'<div class="num"><b>{v}</b><span>{l}</span></div>' for v,l in [(fmt(stats['ayat']),'آية لها مختصر من كلام الإمامين'),(fmt(st['summN']),'جملة بنص كلامهما'),(fmt(stats['nuq']),'نقلًا عن السلف والمفسرين'),(fmt(stats['booksIT']+stats['booksIQ']),'كتابًا مصدرًا')])
ent=''.join(f'<section><h2>الإصدار {AV(u["v"])} — {E(u["title"])}</h2><p class="upd-date">{AD(u["date"])}</p><ul>'+''.join(f'<li>{E(i)}</li>' for i in u['items'])+'</ul></section>' for u in UPD)
ub=(style+'<style>.upd-nums{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:10px}.upd-nums .num{display:grid;gap:2px;background:var(--sheet,#fff);border:1px solid var(--line,#d9dee6);border-radius:10px;padding:10px 12px}.upd-nums b{font-size:20px}.upd-nums span{font-size:13px;color:var(--muted,#5b6676)}.upd-date{margin:0;font-size:13px;color:var(--muted,#5b6676)}</style>'
    f'<main class="sp"><nav class="crumbs"><a href="/">الرئيسية</a> › آخر التحديثات</nav><h1>آخر التحديثات</h1>'
    f'<p>الموقع يُحدَّث باستمرار، وهذه أرقامه الآن (الإصدار {AV(UPD[0]["v"])}، {AD(UPD[0]["date"])}):</p><div class="upd-nums">{nums}</div>'+ent+'</main>')
write('updates.html',page('آخر التحديثات — جامع تفسير الشيخين','سجل إصدارات جامع تفسير الشيخين وما أضيف في كل إصدار، مع أرقام الموقع الحالية.','/updates.html',ub))
urls.append('/updates.html')
nf=page('الصفحة غير موجودة — جامع تفسير الشيخين','الصفحة المطلوبة غير موجودة.','/404.html',
        style+'<main class="sp"><h1>الصفحة غير موجودة</h1><p lang="en" dir="ltr">Page not found.</p><a class="btn pri open" href="/">الرئيسية · Home</a></main>')
write('404.html',nf.replace('<link rel="canonical" href="'+BASE+'/404.html">','<meta name="robots" content="noindex">'))
shutil.copy2(T+'/og.png',P)
for u in urls:
    f=P+(u+'index.html' if u.endswith('/') else u)
    if os.path.exists(f): touch(u,open(f).read())
open(LM_F,'w').write('{\n'+',\n'.join(json.dumps(k,ensure_ascii=False)+':'+json.dumps(LM[k]) for k in sorted(LM))+'\n}\n')  # one URL per line keeps git diffs small
shutil.rmtree(P+'/topic',ignore_errors=True)
def topic_items_html(tp):
    out=''
    for a in ('IT','IQ'):
        rows=[q for q in tp['_ok'] if q[2]==a]
        if not rows: continue
        out+=f'<section><h2>{IMAM[a]}</h2>'
        for su,v,_,kind,x in rows:
            d=SUR[su]; lab=f'{E(NAMES[su-1])} {AR(v)}'
            body_=(f'<span class="who">{E(x.get("who",""))}</span> <span class="st">{E(x.get("st",""))}</span><br>«{fx(E(x["t"]))}»' if kind=='nuq' else fx(E(x['t'])))
            out+=f'<blockquote><a class="tv" href="{curl(su,v)}">﴿{lab}﴾</a> {body_}<cite>{ref(d,x)}</cite></blockquote>'
        out+='</section>'
    return out
if TOPICS:
    tl=''
    for tp in TOPICS:
        n=len(tp['_ok'])
        if not n: continue
        intro=f'<p class="tintro">{E(tp["intro"])} <small>(تعريف من إعداد الموقع)</small></p>' if tp.get('intro') else ''
        if tp['_page']:
            path=f'/topic/{tp["id"]}.html'
            body=(style+f'<main class="sp"><nav class="crumbs"><a href="/">الرئيسية</a> › <a href="/topics.html">الموضوعات</a> › {E(tp["title"])}</nav>'
                  f'<h1>{E(tp["title"])} في تفسير ابن تيمية وابن القيم</h1>{intro}<p>{AR(n)} موضعًا من كلام الإمامين، مرتبة بترتيب المصحف، كل نص بلفظه مع آيته ومصدره.</p>'
                  +topic_items_html(tp)+METH+'</main>')
            x0=tp['_ok'][0][4]
            ld={"@context":"https://schema.org","@graph":[{"@type":"CollectionPage","name":tp['title'],"inLanguage":"ar","url":BASE+path,"isPartOf":{"@id":BASE+"/#site"},"publisher":{"@id":BASE+"/#org"}},
                crumbs_ld([('الرئيسية','/'),('الموضوعات','/topics.html'),(tp['title'],path)])]}
            write(path[1:],page(f'{tp["title"]} — تفسير ابن تيمية وابن القيم',(f'{tp["title"]} في كلام ابن تيمية وابن القيم: {AR(n)} موضعًا بنصها مع الآية والمصدر. '+fx(x0['t'],False))[:155],path,body,ld)); urls.append(path)
            tl+=f'<div class="vitem"><a class="vrow" id="{tp["id"]}" href="{path}"><b>{E(tp["title"])}</b> <span>{AR(n)} موضعًا</span></a></div>'
        else:
            tl+=f'<div class="vitem" id="{tp["id"]}"><p class="vrow"><b>{E(tp["title"])}</b> <span>{AR(n)}</span></p>{intro}'+topic_items_html(tp)+'</div>'
    body=(style+f'<main class="sp"><nav class="crumbs"><a href="/">الرئيسية</a> › الموضوعات</nav><h1>الفهرس الموضوعي لتفسير ابن تيمية وابن القيم</h1>'
          f'<p>كلام الإمامين مصنفًا على الموضوعات؛ التصنيف من إعداد الموقع، والنصوص بلفظها كما في كتبهما.</p><div class="vrows">{tl}</div>'+METH+'</main>')
    write('topics.html',page('الفهرس الموضوعي — تفسير ابن تيمية وابن القيم','كلام شيخ الإسلام ابن تيمية والإمام ابن القيم في تفسير القرآن مصنفًا على الموضوعات، بنصه مع الآية والمصدر.','/topics.html',body,
          {"@context":"https://schema.org","@type":"CollectionPage","name":"الفهرس الموضوعي","inLanguage":"ar","url":BASE+"/topics.html"}))
    urls.append('/topics.html')
    print('topics:',len(TOPICS),'pages:',sum(1 for t in TOPICS if t['_page']),'bad items skipped:',len(TOPIC_BAD))
    for b_ in TOPIC_BAD[:10]: print('  WARNING topic item does not match the data:',b_)
sm='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'<url><loc>{BASE}{u}</loc></url>\n' for u in urls)+'</urlset>\n'
open(P+'/sitemap.xml','w').write(sm)
open(P+'/robots.txt','w').write(f'User-agent: *\nAllow: /\nDisallow: /api/\nSitemap: {BASE}/sitemap.xml\n')

# 6) static assets
for f in ('worker.js','wrangler.jsonc'): shutil.copy2(T+'/'+f,REPO)
for f in [os.path.basename(x) for x in glob.glob(T+'/*.txt') if re.fullmatch(r'[0-9a-f]{32}\.txt',os.path.basename(x))]+['i18n.js','qsuggest.js','share.js','quran_clean.json','theme.css','sw.js','manifest.webmanifest','icon.svg','icon-192.png','icon-512.png','_headers']:
    if os.path.exists(T+'/'+f): shutil.copy2(T+'/'+f,P)
# service-worker cache version = fingerprint of the data, so every content release replaces old cached surah data
import hashlib
_fp=hashlib.sha1(''.join(f'{os.path.basename(x)}:{os.path.getsize(x)};' for x in sorted(glob.glob(P+'/*.json'))).encode()+open(P+'/stats.json','rb').read()).hexdigest()[:10]
_sw=open(P+'/sw.js').read().replace("'shaykhain-v2'",f"'shaykhain-{_fp}'"); open(P+'/sw.js','w').write(_sw)
os.makedirs(P+'/i18n',exist_ok=True); os.makedirs(P+'/st',exist_ok=True)
for f in glob.glob(T+'/i18n/*.json'): shutil.copy2(f,P+'/i18n')
for f in glob.glob(T+'/st/*.json'): shutil.copy2(f,P+'/st')
# 6b) التفسير الميسر (QuranEnc, unmodified) -> public/tr/muyassar/{s}.json, shown only for verses without the imams' words
MY=json.load(open(T+'/data/arabic_moyassar.json')); ed=MY['edition']
os.makedirs(P+'/tr/muyassar',exist_ok=True)
for s in range(1,115):
    vs=MY['verses'][str(s)]
    rows=[[vs[str(v)]['text'],vs[str(v)].get('footnotes') or ''] for v in range(1,len(vs)+1)]
    json.dump(rows,open(f'{P}/tr/muyassar/{s}.json','w'),ensure_ascii=False,separators=(',',':'))
json.dump({'title':ed['name'],'credit':'التفسير الميسر، مجمع الملك فهد لطباعة المصحف الشريف','version':ed['version'],
           'url':'https://quranenc.com/ar/browse/arabic_moyassar','transcript':ed.get('transcript','')},open(P+'/tr/muyassar/meta.json','w'),ensure_ascii=False)
print('thin verse pages (noindex):',len(THIN_N),'passages:',PASS_N)
print('built; pages',len(urls),'stats',stats)
import subprocess; subprocess.run([sys.executable,T+'/build_langs.py',REPO],check=True)
