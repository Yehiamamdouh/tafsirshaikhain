// Interface language: translates chrome only (never the imams' Arabic texts).
(function(){
  const CHROME = 'header.top,.controls,.surah-head,.grid-legend,.imam-head,.none,.nuq h3,.nq-head .st,.cite,.drawer-btn,.nav,.about-link,.site-foot,#status,.gres-h,.more,main.ab,.toast,.drawer-tools,.tr-label,details.intro';
  const qs = new URLSearchParams(location.search);
  let lang = qs.get('lang') || (function(){ try { return localStorage.getItem('lang'); } catch(e){ return null; } })() || 'ar';
  const I = window.I18N = { lang, dict: null, meta: null, ready: null, t: s => (I.dict && I.dict[s]) || s, onChange: [] };
  const keysBySize = () => Object.keys(I.dict || {}).sort((a, b) => b.length - a.length);
  let subs = [];
  function trText(node){
    const raw = node.nodeValue, s = raw.trim(); if (!s || !/[؀-ۿ]/.test(s)) return;
    if (I.dict[s]){ node.nodeValue = raw.replace(s, I.dict[s]); return; }
    let out = raw, hit = false;
    for (const k of subs){ if (k.length > 2 && out.includes(k)){ out = out.split(k).join(I.dict[k]); hit = true; } }
    if (hit) node.nodeValue = out;
  }
  function trEl(root){
    if (!I.dict) return;
    const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    const nodes = []; while (w.nextNode()) nodes.push(w.currentNode);
    nodes.forEach(trText);
    root.querySelectorAll && root.querySelectorAll('[placeholder],[aria-label]').forEach(e => {
      ['placeholder','aria-label'].forEach(a => { const v = e.getAttribute(a); if (v && I.dict[v.trim()]) e.setAttribute(a, I.dict[v.trim()]); });
    });
  }
  function sweep(){ if (!I.dict) return; document.querySelectorAll(CHROME).forEach(trEl); }
  let pending = false;
  const mo = new MutationObserver(() => { if (pending) return; pending = true; requestAnimationFrame(() => { pending = false; mo.disconnect(); sweep(); observe(); }); });
  const observe = () => mo.observe(document.body, {subtree: true, childList: true, characterData: true});
  async function setLang(l){
    I.lang = l; try { localStorage.setItem('lang', l); } catch(e){}
    const ls = document.getElementById('langsel'); if (ls && ls.options.length > 1) ls.value = l;
    if (l === 'ar'){ if (I.dict){ location.reload(); return; } return; }
    const meta = I.meta || (I.meta = await fetch('/tr/langs.json').then(r => r.json()).catch(() => ({})));
    I.dict = await fetch('/i18n/' + l + '.json').then(r => r.ok ? r.json() : {}).catch(() => ({}));
    subs = keysBySize();
    // translated prose reads in its own direction; Arabic verse/quote areas keep RTL
    const dir = (meta[l] && meta[l].dir) || 'ltr';
    document.querySelectorAll('main.ab, header.top h1, header.top .lede, details.intro, .about-link, .site-foot, .crumbs, .gres-h').forEach(e => { e.setAttribute('dir', dir); e.setAttribute('lang', l); });
    document.documentElement.setAttribute('lang', l);
    sweep(); observe();
    I.onChange.forEach(f => { try { f(l); } catch(e){} });
  }
  I.setLang = setLang;
  // static Arabic verse/surah pages have pre-rendered twins at /{lang}/...; the app translates in place
  const twin = l => { const m = location.pathname.match(/^\/((?:ayah|surah)\/[\d-]+\.html)$/); return m ? '/' + l + '/' + m[1] : (document.getElementById('q') ? null : '/' + l + '/'); };
  function choose(l){
    try { localStorage.setItem('lang', l); } catch(e){}
    const t = l === 'ar' ? null : twin(l);
    if (t) location.href = t; else setLang(l);
  }
  function picker(){
    const host = document.querySelector('header.top') || document.querySelector('.about-link') || document.querySelector('.site-foot');
    if (!host) return;
    const sel = document.createElement('select'); sel.id = 'langsel'; sel.setAttribute('aria-label', 'اللغة / Language');
    sel.innerHTML = '<option value="ar">🌐 العربية</option>';
    fetch('/tr/langs.json').then(r => r.json()).then(m => {
      I.meta = m;
      Object.entries(m).forEach(([k, v]) => { const o = document.createElement('option'); o.value = k; o.textContent = v.name; sel.appendChild(o); });
      sel.value = I.lang;
    });
    sel.addEventListener('change', () => choose(sel.value));
    if (host.matches('header.top')) host.prepend(sel); else host.appendChild(sel);
  }
  // visitors whose browser language is supported get a one-tap offer (no forced redirect: keeps Arabic URLs crawlable)
  const OFFER = {en:'Read this site in English',fr:'Lire ce site en français',es:'Leer este sitio en español',de:'Diese Seite auf Deutsch lesen',
    tr:'Bu siteyi Türkçe okuyun',id:'Baca situs ini dalam Bahasa Indonesia',ms:'Baca laman ini dalam Bahasa Melayu',ru:'Читать сайт на русском',
    ur:'یہ سائٹ اردو میں پڑھیں',fa:'این سایت را به فارسی بخوانید',bn:'এই সাইটটি বাংলায় পড়ুন',zh:'以中文阅读本网站',sw:'Soma tovuti hii kwa Kiswahili',ha:'Karanta shafin nan da Hausa'};
  function offer(){
    let seen = null; try { seen = localStorage.getItem('lang') || localStorage.getItem('langOffer'); } catch(e){}
    if (seen || I.lang !== 'ar' || qs.get('lang')) return;
    const l = (navigator.languages || [navigator.language || '']).map(x => String(x).toLowerCase().split('-')[0]).find(x => x === 'ar' || OFFER[x]);
    if (!l || l === 'ar') return;
    const b = document.createElement('div'); b.className = 'lang-offer'; b.setAttribute('lang', l); b.setAttribute('dir', l === 'ur' || l === 'fa' ? 'rtl' : 'ltr');
    const a = document.createElement('button'); a.type = 'button'; a.className = 'lo-go'; a.textContent = OFFER[l] + ' →';
    const x = document.createElement('button'); x.type = 'button'; x.className = 'lo-x'; x.setAttribute('aria-label', 'إغلاق / Close'); x.textContent = '×';
    a.onclick = () => { b.remove(); choose(l); };
    x.onclick = () => { b.remove(); try { localStorage.setItem('langOffer', 'ar'); } catch(e){} };
    b.append(a, x); document.body.prepend(b);
  }
  I.ready = new Promise(res => {
    const go = () => {
      // returning visitor who chose a language: send static Arabic verse/surah pages to their translated twin
      const t = I.lang !== 'ar' && !qs.get('lang') && /^\/(ayah|surah)\//.test(location.pathname) && twin(I.lang);
      if (t){ location.replace(t); return; }
      picker(); offer(); (I.lang !== 'ar' ? setLang(I.lang) : Promise.resolve()).then(res); };
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', go); else go();
  });
})();
