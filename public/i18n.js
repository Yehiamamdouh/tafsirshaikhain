// Interface language: translates chrome only (never the imams' Arabic texts).
(function(){
  const CHROME = 'header.top,.controls,.surah-head,.grid-legend,.imam-head,.none,.nuq h3,.nq-head .st,.cite,.drawer-btn,.nav,.about-link,.site-foot,#status,.gres-h,.more,main.ab,.toast,.drawer-tools,.tr-label';
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
    if (l === 'ar'){ if (I.dict){ location.reload(); return; } return; }
    const meta = I.meta || (I.meta = await fetch('tr/langs.json').then(r => r.json()).catch(() => ({})));
    I.dict = await fetch('i18n/' + l + '.json').then(r => r.ok ? r.json() : {}).catch(() => ({}));
    subs = keysBySize();
    const ab = document.querySelector('main.ab'); if (ab && meta[l]) ab.setAttribute('dir', meta[l].dir);
    document.documentElement.setAttribute('lang', l);
    sweep(); observe();
    I.onChange.forEach(f => { try { f(l); } catch(e){} });
  }
  I.setLang = setLang;
  function picker(){
    const host = document.querySelector('.about-link') || document.querySelector('.site-foot');
    if (!host) return;
    const sel = document.createElement('select'); sel.id = 'langsel'; sel.setAttribute('aria-label', 'اللغة / Language');
    sel.innerHTML = '<option value="ar">العربية</option>';
    fetch('tr/langs.json').then(r => r.json()).then(m => {
      I.meta = m;
      Object.entries(m).forEach(([k, v]) => { const o = document.createElement('option'); o.value = k; o.textContent = v.name; sel.appendChild(o); });
      sel.value = I.lang;
    });
    sel.addEventListener('change', () => setLang(sel.value));
    host.appendChild(sel);
  }
  I.ready = new Promise(res => {
    const go = () => { picker(); (I.lang !== 'ar' ? setLang(I.lang) : Promise.resolve()).then(res); };
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', go); else go();
  });
})();
