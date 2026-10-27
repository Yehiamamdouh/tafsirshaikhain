"""Static, indexable verse/surah pages in 5 languages (+ hreflang). Run after build_public.py."""
import json, os, sys, html, re, shutil
T=os.path.dirname(os.path.abspath(__file__))
REPO=sys.argv[1]; P=REPO+'/public'; BASE='https://tafsirshaikhain.com'
E=lambda s: html.escape(str(s), quote=True)
CH=json.load(open(T+'/data/chapters.json'))['chapters']
QA=json.load(open(T+'/data/simple.json'))
GA=open(T+'/ga.html').read().replace('{{GA_ID}}',os.environ.get('GA_ID','G-ER9F5C2HC1'))
META=json.load(open(P+'/tr/langs.json'))
L={
 'en':{'dir':'ltr','site':'Tafsir al-Shaykhayn','tag':'The meanings of the Qur\'an in the words of Ibn Taymiyyah and Ibn al-Qayyim',
       'tafsir':'Tafsir of','surah':'Surah','verse':'Verse','home':'Home','IT':'Shaykh al-Islam Ibn Taymiyyah','IQ':'Imam Ibn al-Qayyim',
       'quoted':'What he quoted from others','meaning':'Translation of the meaning','open':'Open in the interactive tafsir (full texts)',
       'note':'The words of the two imams are given in their original Arabic, verbatim, with references.','choose':'Verses with commentary in this surah:',
       'by':'by Ibn Taymiyyah and Ibn al-Qayyim','prev':'Previous verse','next':'Next verse','about':'About the project','privacy':'Privacy & terms'},
 'ur':{'dir':'rtl','site':'جامع تفسیر الشیخین','tag':'ابن تیمیہ اور ابن القیم کے کلام میں قرآن کے معانی',
       'tafsir':'تفسیر','surah':'سورۃ','verse':'آیت','home':'صفحۂ اول','IT':'شیخ الاسلام ابن تیمیہ','IQ':'امام ابن القیم',
       'quoted':'جو انہوں نے دوسروں سے نقل کیا','meaning':'ترجمۂ معانی','open':'تفاعلی تفسیر میں کھولیں (مکمل متون)',
       'note':'دونوں ائمہ کا کلام اصل عربی میں لفظ بلفظ، حوالوں کے ساتھ دیا گیا ہے۔','choose':'اس سورۃ کی وہ آیات جن پر کلام موجود ہے:',
       'by':'ابن تیمیہ اور ابن القیم کے کلام میں','prev':'پچھلی آیت','next':'اگلی آیت','about':'منصوبے کے بارے میں','privacy':'رازداری اور شرائط'},
 'id':{'dir':'ltr','site':'Tafsir al-Syaikhain','tag':'Makna Al-Qur\'an dari perkataan Ibnu Taimiyah dan Ibnul Qayyim',
       'tafsir':'Tafsir','surah':'Surah','verse':'Ayat','home':'Beranda','IT':'Syaikhul Islam Ibnu Taimiyah','IQ':'Imam Ibnul Qayyim',
       'quoted':'Yang beliau nukil dari selainnya','meaning':'Terjemah makna','open':'Buka di tafsir interaktif (teks lengkap)',
       'note':'Perkataan kedua imam disajikan dalam bahasa Arab aslinya, apa adanya, beserta rujukannya.','choose':'Ayat-ayat yang memiliki penjelasan dalam surah ini:',
       'by':'menurut Ibnu Taimiyah dan Ibnul Qayyim','prev':'Ayat sebelumnya','next':'Ayat berikutnya','about':'Tentang proyek','privacy':'Privasi & ketentuan'},
 'tr':{'dir':'ltr','site':'Tefsîru\'ş-Şeyhayn','tag':'İbn Teymiyye ve İbnü\'l-Kayyim\'in sözleriyle Kur\'an\'ın manaları',
       'tafsir':'Tefsiri:','surah':'Sûre','verse':'Âyet','home':'Ana sayfa','IT':'Şeyhülislam İbn Teymiyye','IQ':'İmam İbnü\'l-Kayyim',
       'quoted':'Başkalarından naklettikleri','meaning':'Meal','open':'Etkileşimli tefsirde aç (tam metinler)',
       'note':'İki imamın sözleri, kaynaklarıyla birlikte, aslı olan Arapça metinle aynen verilmiştir.','choose':'Bu sûrede açıklaması bulunan âyetler:',
       'by':'İbn Teymiyye ve İbnü\'l-Kayyim\'e göre','prev':'Önceki âyet','next':'Sonraki âyet','about':'Proje hakkında','privacy':'Gizlilik ve şartlar'},
 'fr':{'dir':'ltr','site':'Tafsir des deux Cheikhs','tag':'Le sens du Coran à travers les paroles d\'Ibn Taymiyya et d\'Ibn al-Qayyim',
       'tafsir':'Tafsir de','surah':'Sourate','verse':'Verset','home':'Accueil','IT':'Cheikh al-Islam Ibn Taymiyya','IQ':'L\'imam Ibn al-Qayyim',
       'quoted':'Ce qu\'il a rapporté d\'autrui','meaning':'Traduction du sens','open':'Ouvrir dans le tafsir interactif (textes complets)',
       'note':'Les paroles des deux imams sont données dans l\'arabe original, mot pour mot, avec leurs références.','choose':'Versets commentés dans cette sourate :',
       'by':'selon Ibn Taymiyya et Ibn al-Qayyim','prev':'Verset précédent','next':'Verset suivant','about':'À propos du projet','privacy':'Confidentialité et conditions'},
}

# languages rendered by the Worker from packs (keeps the static file count under the free-plan limit)
L2={
 'bn':{'dir':'ltr','site':'তাফসীরুশ শাইখাইন','tag':'ইবনে তাইমিয়া ও ইবনুল কাইয়্যিমের বক্তব্যে কুরআনের অর্থ','tafsir':'তাফসীর','surah':'সূরা','verse':'আয়াত','home':'প্রথম পাতা','IT':'শাইখুল ইসলাম ইবনে তাইমিয়া','IQ':'ইমাম ইবনুল কাইয়্যিম','quoted':'অন্যদের থেকে যা তিনি উদ্ধৃত করেছেন','meaning':'অর্থের অনুবাদ','open':'ইন্টারঅ্যাকটিভ তাফসীরে খুলুন (পূর্ণ পাঠ)','note':'দুই ইমামের বক্তব্য মূল আরবিতে হুবহু, সূত্রসহ দেওয়া হয়েছে।','choose':'এই সূরার যেসব আয়াতের ব্যাখ্যা আছে:','by':'ইবনে তাইমিয়া ও ইবনুল কাইয়্যিমের মতে','prev':'আগের আয়াত','next':'পরের আয়াত','about':'প্রকল্প সম্পর্কে','privacy':'গোপনীয়তা ও শর্তাবলি'},
 'ms':{'dir':'ltr','site':'Tafsir al-Syaikhain','tag':'Makna al-Quran menerusi kata-kata Ibnu Taimiyah dan Ibnu al-Qayyim','tafsir':'Tafsir','surah':'Surah','verse':'Ayat','home':'Laman utama','IT':'Syeikhul Islam Ibnu Taimiyah','IQ':'Imam Ibnu al-Qayyim','quoted':'Apa yang beliau nukilkan daripada orang lain','meaning':'Terjemahan makna','open':'Buka dalam tafsir interaktif (teks penuh)','note':'Kata-kata kedua-dua imam dipaparkan dalam bahasa Arab asal, kata demi kata, berserta rujukan.','choose':'Ayat-ayat yang mempunyai huraian dalam surah ini:','by':'menurut Ibnu Taimiyah dan Ibnu al-Qayyim','prev':'Ayat sebelumnya','next':'Ayat seterusnya','about':'Tentang projek','privacy':'Privasi & terma'},
 'fa':{'dir':'rtl','site':'جامع تفسیر الشیخین','tag':'معانی قرآن در سخنان ابن تیمیه و ابن قیم','tafsir':'تفسیر','surah':'سوره','verse':'آیه','home':'صفحهٔ اصلی','IT':'شیخ‌الاسلام ابن تیمیه','IQ':'امام ابن قیم','quoted':'آنچه از دیگران نقل کرده است','meaning':'ترجمهٔ معانی','open':'باز کردن در تفسیر تعاملی (متن کامل)','note':'سخنان دو امام به همان عربی اصلی، کلمه به کلمه و همراه با منبع آمده است.','choose':'آیاتی از این سوره که شرح دارند:','by':'از سخنان ابن تیمیه و ابن قیم','prev':'آیهٔ قبلی','next':'آیهٔ بعدی','about':'دربارهٔ پروژه','privacy':'حریم خصوصی و شرایط'},
 'ru':{'dir':'ltr','site':'Тафсир двух шейхов','tag':'Смыслы Корана в словах Ибн Таймии и Ибн аль-Каййима','tafsir':'Тафсир:','surah':'Сура','verse':'Аят','home':'Главная','IT':'Шейх-уль-Ислам Ибн Таймия','IQ':'Имам Ибн аль-Каййим','quoted':'Что он передал от других','meaning':'Перевод смыслов','open':'Открыть в интерактивном тафсире (полные тексты)','note':'Слова двух имамов приводятся на арабском языке оригинала, дословно, со ссылками на источники.','choose':'Аяты этой суры с комментарием:','by':'по словам Ибн Таймии и Ибн аль-Каййима','prev':'Предыдущий аят','next':'Следующий аят','about':'О проекте','privacy':'Конфиденциальность и условия'},
 'sw':{'dir':'ltr','site':'Tafsiri ya Masheikh Wawili','tag':"Maana ya Qur'ani kwa maneno ya Ibn Taymiyyah na Ibn al-Qayyim",'tafsir':'Tafsiri ya','surah':'Sura','verse':'Aya','home':'Mwanzo','IT':'Sheikh al-Islam Ibn Taymiyyah','IQ':'Imam Ibn al-Qayyim','quoted':'Aliyoyanukuu kutoka kwa wengine','meaning':'Tafsiri ya maana','open':'Fungua katika tafsiri shirikishi (maandiko kamili)','note':'Maneno ya maimamu wawili yametolewa kwa Kiarabu asilia, neno kwa neno, pamoja na marejeo.','choose':'Aya za sura hii zenye maelezo:','by':'kwa mujibu wa Ibn Taymiyyah na Ibn al-Qayyim','prev':'Aya iliyotangulia','next':'Aya inayofuata','about':'Kuhusu mradi','privacy':'Faragha na masharti'},
 'ha':{'dir':'ltr','site':'Tafsirin Shehunan Biyu',"tag":"Ma'anonin Alkur'ani a cikin maganganun Ibn Taimiyya da Ibn al-Qayyim",'tafsir':'Tafsirin','surah':'Sura','verse':'Aya','home':'Shafin farko','IT':'Shaikhul Islam Ibn Taimiyya','IQ':'Imam Ibn al-Qayyim','quoted':'Abin da ya ruwaito daga wasu','meaning':"Fassarar ma'ana",'open':"Bude a cikin tafsiri mai mu'amala (cikakkun rubutu)",'note':'An kawo maganganun limaman biyu da Larabci na asali, kalma bayan kalma, tare da madogara.','choose':'Ayoyin wannan sura da ke da bayani:','by':'bisa ga Ibn Taimiyya da Ibn al-Qayyim','prev':'Ayar da ta gabata','next':'Aya ta gaba','about':'Game da aikin','privacy':'Sirri da sharudda'},
 'es':{'dir':'ltr','site':'Tafsir de los dos Shaij','tag':'El significado del Corán en las palabras de Ibn Taymiyya e Ibn al-Qayyim','tafsir':'Tafsir de','surah':'Sura','verse':'Aleya','home':'Inicio','IT':'Shaij al-Islam Ibn Taymiyya','IQ':'El imam Ibn al-Qayyim','quoted':'Lo que citó de otros','meaning':'Traducción del significado','open':'Abrir en el tafsir interactivo (textos completos)','note':'Las palabras de los dos imames se ofrecen en el árabe original, literalmente, con sus referencias.','choose':'Aleyas comentadas en esta sura:','by':'según Ibn Taymiyya e Ibn al-Qayyim','prev':'Aleya anterior','next':'Aleya siguiente','about':'Sobre el proyecto','privacy':'Privacidad y condiciones'},
 'de':{'dir':'ltr','site':'Tafsir der beiden Schaichs','tag':'Die Bedeutungen des Korans in den Worten von Ibn Taimiyya und Ibn al-Qayyim','tafsir':'Tafsir von','surah':'Sura','verse':'Vers','home':'Startseite','IT':'Schaich al-Islam Ibn Taimiyya','IQ':'Imam Ibn al-Qayyim','quoted':'Was er von anderen überliefert hat','meaning':'Übersetzung der Bedeutung','open':'Im interaktiven Tafsir öffnen (vollständige Texte)','note':'Die Worte der beiden Imame werden im arabischen Original wortgetreu und mit Quellenangaben wiedergegeben.','choose':'Kommentierte Verse dieser Sura:','by':'nach Ibn Taimiyya und Ibn al-Qayyim','prev':'Vorheriger Vers','next':'Nächster Vers','about':'Über das Projekt','privacy':'Datenschutz & Bedingungen'},
 'zh':{'dir':'ltr','site':'两位谢赫经注汇编','tag':'伊本·泰米叶与伊本·盖伊姆论《古兰经》的意义','tafsir':'经注：','surah':'章','verse':'节','home':'首页','IT':'伊斯兰谢赫 伊本·泰米叶','IQ':'伊玛目 伊本·盖伊姆','quoted':'他引述他人的说法','meaning':'意义翻译','open':'在互动经注中打开（完整原文）','note':'两位伊玛目的话以阿拉伯语原文逐字呈现，并附出处。','choose':'本章有注释的经文：','by':'伊本·泰米叶与伊本·盖伊姆的解释','prev':'上一节','next':'下一节','about':'关于项目','privacy':'隐私与条款'},
}
L.update(L2); DYN=set(L)  # all languages are Worker-rendered from packs (static file count stays flat as content grows)
for _l in L:
    shutil.rmtree(f'{P}/{_l}/ayah',ignore_errors=True); shutil.rmtree(f'{P}/{_l}/surah',ignore_errors=True)
    if os.path.exists(f'{P}/{_l}/index.html'): os.remove(f'{P}/{_l}/index.html')
shutil.rmtree(P+'/lp',ignore_errors=True)
packs={}
def out(l,tail,s,v,h):
    if l in DYN:
        packs.setdefault((l,f'{s}_{v//50}' if s else 'home'),{})[tail]=h
    else:
        f=f'{P}/{l}/{tail or "index.html"}'; os.makedirs(os.path.dirname(f),exist_ok=True); open(f,'w').write(h)
SUR={s:json.load(open(f'{P}/s{s}.json')) for s in range(1,115)}
def name(l,s): c=CH[s-1]; return c['name'] if l in ('ur','fa') else c['transliteration']
def alts(path_tail):
    out=f'<link rel="alternate" hreflang="ar" href="{BASE}/{path_tail}">\n<link rel="alternate" hreflang="x-default" href="{BASE}/{path_tail}">\n'
    return out+''.join(f'<link rel="alternate" hreflang="{k}" href="{BASE}/{k}/{path_tail}">\n' for k in L)
def crumbs(l,tail):
    t=L[l]; it=[(t['home'],f'/{l}/')]
    m=re.match(r'(ayah|surah)/(\d+)(?:-(\d+))?\.html',tail)
    if not m: return None
    s=int(m.group(2)); it.append((f"{t['surah']} {name(l,s)}",f'/{l}/surah/{s}.html'))
    if m.group(3): it.append((f"{t['verse']} {m.group(3)}",f'/{l}/{tail}'))
    return {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":i+1,"name":n,"item":BASE+u} for i,(n,u) in enumerate(it)]}
LOC={'en':'en_US','ur':'ur_PK','id':'id_ID','tr':'tr_TR','fr':'fr_FR','bn':'bn_BD','ms':'ms_MY','fa':'fa_IR','ru':'ru_RU','sw':'sw_KE','ha':'ha_NG','es':'es_ES','de':'de_DE','zh':'zh_CN'}
def switcher(l,path_tail):
    o=[f'<a href="/{path_tail}" hreflang="ar" lang="ar" data-l="ar">العربية</a>']
    o+=[(f'<b lang="{k}">{E(META[k]["name"])}</b>' if k==l else f'<a href="/{k}/{path_tail}" hreflang="{k}" lang="{k}" data-l="{k}">{E(META[k]["name"])}</a>') for k in L]
    return '<nav class="langs" aria-label="Language">🌐 '+' · '.join(o)+'</nav>\n'
def ld_extra(l,title,desc,path_tail):
    t=L[l]; u=f'{BASE}/{l}/{path_tail}'
    if not path_tail: return {"@context":"https://schema.org","@type":"WebSite","name":t['site'],"alternateName":"جامع تفسير الشيخين","url":u,"inLanguage":l,"description":t['tag']}
    if path_tail.startswith('ayah/'):
        return {"@context":"https://schema.org","@type":"Article","headline":title[:110],"description":desc,"inLanguage":l,"url":u,"mainEntityOfPage":u,
                "image":BASE+"/og.png","author":[{"@type":"Person","name":t['IT']},{"@type":"Person","name":t['IQ']}],
                "isPartOf":{"@type":"WebSite","name":t['site'],"url":f'{BASE}/{l}/'}}
    return {"@context":"https://schema.org","@type":"CollectionPage","name":title,"inLanguage":l,"url":u}
def page(l,title,desc,path_tail,body):
    t=L[l]; LD=crumbs(l,path_tail); X=ld_extra(l,title,desc,path_tail)
    return (f'<!doctype html>\n<html lang="{l}" dir="{t["dir"]}">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f'<title>{E(title)}</title>\n<meta name="description" content="{E(desc)}">\n<link rel="canonical" href="{BASE}/{l}/{path_tail}">\n{alts(path_tail)}'
            f'<meta property="og:title" content="{E(title)}">\n<meta property="og:description" content="{E(desc)}">\n<meta property="og:url" content="{BASE}/{l}/{path_tail}">\n'
            f'<meta property="og:site_name" content="{E(t["site"])}">\n<meta property="og:locale" content="{LOC[l]}">\n<meta property="og:type" content="{"article" if path_tail.startswith("ayah/") else "website"}">\n'
            f'<meta name="theme-color" content="#1f4d3a">\n<meta property="og:image" content="https://tafsirshaikhain.com/og.png">\n<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">\n<meta name="twitter:card" content="summary_large_image">\n'
            '<link rel="manifest" href="/manifest.webmanifest">\n<link rel="apple-touch-icon" href="/icon-192.png">\n'
            '<script type="application/ld+json">'+json.dumps(X,ensure_ascii=False)+'</script>\n'
            +(('<script type="application/ld+json">'+json.dumps(LD,ensure_ascii=False)+'</script>\n') if LD else '')+
            '<link rel="icon" href="/icon.svg" type="image/svg+xml">\n<link rel="preconnect" href="https://fonts.googleapis.com">\n'
            '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Amiri+Quran&family=Amiri:wght@400;700&family=Noto+Naskh+Arabic:wght@400;600&display=swap">\n'
            '<link rel="stylesheet" href="/theme.css">\n<style>body{font-family:system-ui,"Segoe UI",sans-serif;color:var(--ink);padding:20px 16px 48px;line-height:1.6}'
            '.tr{font-size:17px;line-height:1.8;margin:0}.cr{font-size:12px;color:var(--muted)}.ar{direction:rtl;text-align:right}.langs{max-width:1100px;margin:24px auto 0;font-size:14px;line-height:2;color:var(--muted)}.langs a{color:var(--lapis)}</style>\n'+GA+'</head>\n<body>\n'
            +body+switcher(l,path_tail)+f'<footer class="site-foot"><span>{E(t["site"])} · <a href="/{l}/">{E(t["home"])}</a> · <a href="/about.html">{E(t["about"])}</a> · <a href="/privacy.html">{E(t["privacy"])}</a></span>'
            '<a href="https://doersadv.com" rel="noopener" dir="ltr">Developed by Doers</a></footer>\n'
            f'<script>try{{localStorage.setItem("lang","{l}")}}catch(e){{}}document.addEventListener("click",function(e){{var a=e.target.closest&&e.target.closest("[data-l]");if(a)try{{localStorage.setItem("lang",a.dataset.l)}}catch(x){{}}}})</script>\n</body>\n</html>\n')
def ref(d,x):
    b=d['books'][x['b']]; return '«'+b['t']+'» '+(str(x['v'])+'/' if x.get('v') else '')+str(x['p'])
urls=[]; n=0
for l,t in L.items():
    m=META[l]; cred=f'{m["title"]} — v{m["version"]} · QuranEnc.com'
    st=json.load(open(f'{P}/st/{l}.json')) if os.path.exists(f'{P}/st/{l}.json') else {}
    sur_links=[]
    for s in range(1,115):
        d=SUR[s]; tr=json.load(open(f'{P}/tr/{l}/{s}.json')); sn=name(l,s)
        have=sorted({int(v) for k in ('summ','nuq') for a in ('IT','IQ') for v in d.get(k,{}).get(a,{})}); have=[v for v in have if v>=1]
        for i,v in enumerate(have):
            parts=''
            for a in ('IT','IQ'):
                pts=d.get('summ',{}).get(a,{}).get(str(v),[]); nq=d.get('nuq',{}).get(a,{}).get(str(v),[])
                if not pts and not nq: continue
                parts+=f'<section><h2>{E(t[a])}</h2>'+''.join(f'<blockquote class="ar" lang="ar">{E(x["t"])}'+(f'<small class="pcx">{E(x["cx"])}</small>' if x.get('cx') else '')+f'<cite>{E(ref(d,x))}</cite></blockquote>' for x in pts)
                if nq: parts+=f'<h3>{E(t["quoted"])}</h3>'+''.join(f'<blockquote class="ar" lang="ar"><span class="who">{E(x.get("who",""))}</span> <span class="st">{E(x.get("st",""))}</span> «{E(x["t"])}»<cite>{E(ref(d,x))}</cite></blockquote>' for x in nq)
                parts+='</section>'
            vtr=re.sub(r'\[\d+\]','',re.sub(r'^\(\d+\)\s*','',tr[v-1][0])).strip() if v-1<len(tr) else ''
            title=f'{t["tafsir"]} {sn} {s}:{v} — {t["by"]}'
            prv=have[i-1] if i>0 else None; nxt=have[i+1] if i+1<len(have) else None
            nav='<div class="pn">'+(f'<a href="/{l}/ayah/{s}-{prv}.html">{E(t["prev"])} ({s}:{prv})</a>' if prv else '<span></span>')+(f'<a href="/{l}/ayah/{s}-{nxt}.html">{E(t["next"])} ({s}:{nxt})</a>' if nxt else '')+'</div>'
            body=(f'<main class="sp"><nav class="crumbs"><a href="/{l}/">{E(t["home"])}</a> › <a href="/{l}/surah/{s}.html">{E(t["surah"])} {E(sn)}</a> › {E(t["verse"])} {v}</nav>'
                  f'<h1>{E(t["tafsir"])} {E(t["surah"])} {E(sn)} {s}:{v}</h1><p class="vt ar" lang="ar">﴿{E(QA[str(s)][v-1]["text"])}﴾</p>'
                  f'<section><h3>{E(t["meaning"])}</h3><p class="tr">{E(vtr)}</p><span class="cr" dir="ltr">{E(cred)}</span></section>'
                  f'<p class="cr">{E(t["note"])}</p>'+parts+f'<a class="btn pri open" href="/tafsir.html?lang={l}#s{s}a{v}">{E(t["open"])}</a>'+nav+'</main>')
            out(l,f'ayah/{s}-{v}.html',s,v,page(l,title,vtr[:155] or title,f'ayah/{s}-{v}.html',body)); urls.append(f'/{l}/ayah/{s}-{v}.html'); n+=1
        vl=''.join(f'<a href="/{l}/ayah/{s}-{v}.html">{v}</a>' for v in have)
        body=(f'<main class="sp"><nav class="crumbs"><a href="/{l}/">{E(t["home"])}</a> › {E(t["surah"])} {E(sn)}</nav><h1>{E(t["tafsir"])} {E(t["surah"])} {E(sn)} — {E(t["by"])}</h1>'
              f'<section><p>{E(t["choose"])}</p><div class="vl">{vl or "—"}</div></section><a class="btn pri open" href="/tafsir.html?lang={l}#s{s}a{1 if s>1 else 0}">{E(t["open"])}</a></main>')
        out(l,f'surah/{s}.html',s,0,page(l,f'{t["tafsir"]} {t["surah"]} {sn} — {t["by"]}',f'{t["tafsir"]} {t["surah"]} {sn} — {t["tag"]}',f'surah/{s}.html',body)); urls.append(f'/{l}/surah/{s}.html')
        sur_links.append(f'<a class="sura" href="/{l}/surah/{s}.html"><span><span class="n">{s}</span> <b>{E(sn)}</b></span><span class="c">{len(have)}</span></a>')
    body=(f'<main class="home"><section class="hero"><div class="bism" lang="ar">بسم الله الرحمن الرحيم</div><h1>{E(t["site"])}</h1><p>{E(t["tag"])}</p>'
          f'<div class="cta"><a class="btn pri" href="/tafsir.html?lang={l}">{E(t["open"])}</a><a class="btn sec" href="/">العربية</a></div></section>'
          f'<nav class="suras">{"".join(sur_links)}</nav></main>')
    out(l,'',0,0,page(l,f'{t["site"]} — {t["tag"]}',t['tag'],'',body)); urls.append(f'/{l}/')
for (l,k),d in packs.items():
    os.makedirs(f'{P}/lp/{l}',exist_ok=True); json.dump(d,open(f'{P}/lp/{l}/{k}.json','w'),ensure_ascii=False,separators=(',',':'))
print('packs',len(packs))
# add hreflang to the Arabic static pages and extend the sitemap
for root,_,files in os.walk(P):
    rel=os.path.relpath(root,P)
    if rel.split(os.sep)[0] not in ('ayah','surah'): continue
    for f in files:
        p=os.path.join(root,f); tail=f'{rel}/{f}'.replace(os.sep,'/'); h=open(p).read()
        if 'rel="alternate" hreflang' not in h: open(p,'w').write(h.replace('</head>',alts(tail)+'</head>',1))
import datetime
today=datetime.date.today().isoformat()
def smap(name,us):
    open(f'{P}/{name}','w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'<url><loc>{BASE}{u}</loc></url>\n' for u in us)+'</urlset>\n')
ar_urls=re.findall(r'<loc>'+re.escape(BASE)+r'(.*?)</loc>',open(P+'/sitemap.xml').read())
smap('sitemap-ar.xml',ar_urls)
for l in L: smap(f'sitemap-{l}.xml',[u for u in urls if u.startswith(f'/{l}/')])
open(P+'/sitemap.xml','w').write('<?xml version="1.0" encoding="UTF-8"?>\n<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    +''.join(f'<sitemap><loc>{BASE}/{n}</loc><lastmod>{today}</lastmod></sitemap>\n' for n in ['sitemap-ar.xml']+[f'sitemap-{l}.xml' for l in L])+'</sitemapindex>\n')
# Arabic home links to the language homes too
h=open(P+'/index.html').read()
if 'rel="alternate" hreflang' not in h: open(P+'/index.html','w').write(h.replace('</head>',alts('')+'</head>',1))
print('language pages',n,'total urls added',len(urls))
rb=open(P+'/robots.txt').read()
if '/lp/' not in rb: open(P+'/robots.txt','w').write(rb.replace('User-agent: *','User-agent: *\nDisallow: /lp/',1))
