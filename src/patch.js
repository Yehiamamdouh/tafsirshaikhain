// ===== public-site additions: whole-mushaf search, verse link, offline =====
state.scope = 'all';
(function scopeToggle(){
  const box = document.querySelector('.search');
  const sel = document.createElement('select');
  sel.id = 'scope'; sel.setAttribute('aria-label', 'نطاق البحث');
  sel.innerHTML = '<option value="all">في المصحف كله</option><option value="surah">في هذه السورة</option>';
  sel.addEventListener('change', () => { state.scope = sel.value; if (state.q) render(); updatePh(); });
  box.appendChild(sel);
})();
function updatePh(){
  qEl.placeholder = 'اكتب الآية…';
}
const _go = go;
go = async function(s, v, scroll){ await _go(s, v, scroll); updatePh(); };

let SEARCH = null, SEARCHN = null;
async function loadSearch(){
  if (SEARCH) return SEARCH;
  const r = await fetch('search.json'); SEARCH = await r.json();
  SEARCHN = SEARCH.map(e => norm((e[3] ? e[4] + ' ' + e[5] : e[4])));
  return SEARCH;
}
const _renderSearch = renderSearch;
renderSearch = function(S){
  if (state.scope !== 'all') return _renderSearch(S);
  main.innerHTML = '<div class="loading">جارٍ البحث في المصحف كله…</div>';
  loadSearch().then(() => {
    const terms = norm(state.q).split(/\s+/).filter(Boolean);
    const res = [];
    SEARCH.forEach((e, i) => { if (state.a && e[2] !== state.a) return; if (terms.every(t => SEARCHN[i].includes(t))) res.push(e); });
    main.innerHTML = '';
    status.textContent = AR(res.length) + ' نتيجة في المصحف كله فيها «' + state.q + '»' + (state.a ? ' · ' + NAME[state.a] : '');
    const head = document.createElement('div'); head.className = 'row';
    head.innerHTML = '<button type="button" class="more">← رجوع إلى الآية</button>';
    head.querySelector('button').addEventListener('click', () => { state.q=''; qEl.value=''; render(); });
    main.appendChild(head);
    const list = document.createElement('div'); list.className = 'list';
    if (!res.length) list.innerHTML = '<div class="empty">لا توجد نتائج في المختصرات والنقول. جرّب «في هذه السورة» للبحث في النصوص الكاملة.</div>';
    res.slice(0, state.qshown).forEach(e => {
      const [s, v, a, isN] = e;
      const el = document.createElement('button'); el.type = 'button'; el.className = 'gres';
      el.innerHTML = '<span class="gres-h">سورة ' + esc(SURAHS[s].name) + ' · الآية ' + AR(v) + ' · ' + NAME[a] + ' · ' + (isN ? 'نقل عن ' + esc(e[4]) : 'مختصر') + '</span>'
        + '<span class="gres-t">' + highlight(isN ? e[5] : e[4], terms) + '</span>';
      el.addEventListener('click', () => { state.q=''; qEl.value=''; go(s, v, true); });
      list.appendChild(el);
    });
    main.appendChild(list);
    if (res.length > state.qshown) main.appendChild(moreBtn(res.length - state.qshown, () => { state.qshown += 25; render(); }));
  }).catch(() => { main.innerHTML = '<div class="empty">تعذّر تحميل فهرس البحث.</div>'; });
};

// share button for the current verse: the shared text is the verse + the imams' summary quotations verbatim, with their book refs, then the link
const _render = render;
render = function(){
  _render();
  if (state.q || !cache[state.s]) return;
  const s = state.s, v = state.ay;
  const wrap = document.createElement('div'); wrap.className = 'sharewrap';
  const b = document.createElement('button'); b.type = 'button'; b.className = 'linkbtn sharebtn';
  b.textContent = 'مشاركة';
  const menu = document.createElement('div'); menu.className = 'sharemenu'; menu.hidden = true;
  const hashUrl = location.origin + location.pathname + '#s' + s + 'a' + v;
  const pageUrl = () => !v ? Promise.resolve(hashUrl) : fetch('ayah/' + s + '-' + v + '.html', {method: 'HEAD'}).then(r => r.ok ? location.origin + '/ayah/' + s + '-' + v + '.html' : hashUrl).catch(() => hashUrl);
  const title = (v ? 'تفسير الآية ' + AR(v) + ' من سورة ' : 'كلام ابن تيمية وابن القيم على سورة ') + SURAHS[s].name + (v ? ' — ابن تيمية وابن القيم' : ' عامةً');
  const S = cache[s];
  const fullText = url => {
    const parts = v ? ['﴿' + S.verses[v-1] + '﴾ [' + SURAHS[s].name + ': ' + AR(v) + ']'] : [];
    ['IT','IQ'].forEach(a => {
      const pts = ((S.summ || {})[a] || {})[v] || [];
      if (!pts.length) return;
      parts.push(FULL[a] + ':\n' + pts.map(pt => pt.t + '\n— ' + shortRef(S, pt.b, pt.v, pt.p)).join('\n\n'));
    });
    parts.push(title + '\n' + url);
    return parts.join('\n\n');
  };
  const copyText = txt => {
    const done = () => toast('نُسخ النص مع الرابط');
    try { navigator.clipboard.writeText(txt).then(done, () => prompt('انسخ النص:', txt)); } catch(e){ prompt('انسخ النص:', txt); }
  };
  const copyLink = url => {
    const done = () => toast('نُسخ رابط الآية');
    try { navigator.clipboard.writeText(url).then(done, () => prompt('انسخ الرابط:', url)); } catch(e){ prompt('انسخ الرابط:', url); }
  };
  const mk = (label, fn) => { const a = document.createElement('button'); a.type = 'button'; a.textContent = label; a.addEventListener('click', async () => { const url = await pageUrl(); menu.hidden = true; fn(url); }); menu.appendChild(a); };
  const open = u => window.open(u, '_blank', 'noopener');
  mk('WhatsApp', url => open('https://wa.me/?text=' + encodeURIComponent(fullText(url))));
  mk('Telegram', url => open('https://t.me/share/url?url=' + encodeURIComponent(url) + '&text=' + encodeURIComponent(fullText(url))));
  mk('Facebook', url => open('https://www.facebook.com/sharer/sharer.php?u=' + encodeURIComponent(url)));
  mk('X', url => open('https://twitter.com/intent/tweet?url=' + encodeURIComponent(url) + '&text=' + encodeURIComponent(title)));
  mk('نسخ النص مع الرابط', url => copyText(fullText(url)));
  mk('نسخ الرابط', copyLink);
  b.addEventListener('click', async () => {
    if (navigator.share){
      const url = await pageUrl();
      try { await navigator.share({title: title, text: fullText(url)}); } catch(e){ if (e && e.name !== 'AbortError') menu.hidden = false; }
    } else menu.hidden = !menu.hidden;
  });
  wrap.append(b, menu);
  main.prepend(wrap);
};
window.addEventListener('hashchange', () => {
  const m2 = /^#s(\d{1,3})a(\d{1,3})$/.exec(location.hash || '');
  if (m2 && SURAHS[+m2[1]] && (+m2[1] !== state.s || +m2[2] !== state.ay)) go(+m2[1], +m2[2], true);
});

// offline: service worker + "save everything"
if ('serviceWorker' in navigator) navigator.serviceWorker.register('sw.js').catch(() => {});
const dl = document.getElementById('dlall');
if (dl) dl.addEventListener('click', async () => {
  if (!confirm('سيُحفظ نص المختصرات والنصوص الرئيسية لكل السور (نحو ٧٠ ميجا) لتعمل دون إنترنت. متابعة؟')) return;
  dl.disabled = true;
  const files = ['search.json'];
  for (let n = 1; n <= 114; n++) files.push('s' + n + '.json', 'tr/muyassar/' + n + '.json');
  let done = 0;
  for (const f of files){
    try { await fetch(f, {cache: 'reload'}); } catch(e){}
    done++; dl.textContent = 'جارٍ الحفظ… ' + AR(Math.round(done * 100 / files.length)) + '٪';
  }
  dl.textContent = 'حُفظ المصحف كله للقراءة دون إنترنت';
});
updatePh();

// ===== translations: verse meaning (QuranEnc) + approximate translation of summaries =====
const TRV = {}, TRS = {};
function fnv(s){ s = s.replace(/\s+/g, ' ').trim(); let h = 0x811c9dc5; for (let i = 0; i < s.length; i++){ h ^= s.charCodeAt(i); h = Math.imul(h, 0x01000193) >>> 0; } return h.toString(36); }
function curLang(){ return (window.I18N && I18N.lang) || 'ar'; }
async function ensureTr(l, s){
  const kv = l + s;
  if (!TRV[kv]) TRV[kv] = await fetch('tr/' + l + '/' + s + '.json').then(r => r.json()).catch(() => []);
  if (!TRS[l]) TRS[l] = await fetch('st/' + l + '.json').then(r => r.ok ? r.json() : {}).catch(() => ({}));
}
function trBlock(text, cls, l){
  const p = document.createElement('p'); p.className = cls; p.setAttribute('dir', (I18N.meta && I18N.meta[l] && I18N.meta[l].dir) || 'auto'); p.setAttribute('lang', l);
  p.textContent = text; return p;
}
const _render2 = render;
render = function(){
  _render2();
  const l = curLang(); if (l === 'ar' || state.q) return;
  const s = state.s, v = state.ay;
  if (!TRV[l + s] || !TRS[l]){ ensureTr(l, s).then(() => { if (state.s === s && curLang() === l) render(); }); return; }
  const m = (I18N.meta || {})[l] || {};
  const vt = document.querySelector('.verse-title');
  if (vt && v && TRV[l + s][v - 1]){
    const [t, fn] = TRV[l + s][v - 1];
    const box = document.createElement('div'); box.className = 'tr-verse';
    box.innerHTML = '<span class="tr-label">ترجمة معاني الآية</span>';
    box.appendChild(trBlock(t, 'tr-text', l));
    if (fn){ const d = document.createElement('details'); d.innerHTML = '<summary>…</summary>'; d.appendChild(trBlock(fn, 'tr-fn', l)); box.appendChild(d); }
    const cr = document.createElement('a'); cr.className = 'tr-credit'; cr.href = m.url || 'https://quranenc.com'; cr.target = '_blank'; cr.rel = 'noopener';
    cr.textContent = (m.title || '') + ' — v' + (m.version || '') + ' · QuranEnc.com'; cr.setAttribute('dir', 'ltr');
    box.appendChild(cr);
    vt.after(box);
  }
  const map = TRS[l] || {};
  let any = false;
  document.querySelectorAll('.pt .quote, .nq-q').forEach(q => {
    const t = q.textContent.replace(/^«|»$/g, '');
    const tr = map[fnv(t)]; if (!tr) return;
    any = true; q.after(trBlock(tr, 'tr-sum', l));
  });
  if (any && !document.querySelector('.tr-note')){
    const n = document.createElement('p'); n.className = 'tr-note tr-label'; n.textContent = 'ترجمة تقريبية للمختصر — النص العربي هو المرجع';
    const first = document.querySelector('.imam'); if (first) first.before(n);
  }
};
if (window.I18N) I18N.onChange.push(() => render());

// ===== التفسير الميسر (QuranEnc): the overall meaning shown with every verse: after the imams' words, or alone when the verse has none =====
const MUY = {}; let MUYM = null;
async function ensureMuy(s){
  if (!MUY[s]) MUY[s] = await fetch('tr/muyassar/' + s + '.json').then(r => r.ok ? r.json() : []).catch(() => []);
  if (!MUYM) MUYM = await fetch('tr/muyassar/meta.json').then(r => r.ok ? r.json() : {}).catch(() => ({}));
}
function noImamWords(S, v){
  return ['IT','IQ'].every(a => !((((S.summ||{})[a]||{})[v]||[]).length) && !((((S.nuq||{})[a]||{})[v]||[]).length));
}
const _render3 = render;
render = function(){
  _render3();
  if (state.q || curLang() !== 'ar') return;
  const s = state.s, v = state.ay, S = cache[s];
  if (!S || !v) return;
  if (!MUY[s] || !MUYM){ ensureMuy(s).then(() => { if (state.s === s && state.ay === v) render(); }); return; }
  const row = MUY[s][v - 1]; if (!row || !row[0]) return;
  const vt = document.querySelector('.verse-title'); if (!vt) return;
  const box = document.createElement('div'); box.className = 'muy';
  box.innerHTML = '<div class="muy-head"><b>التفسير الميسر</b><small>' + (noImamWords(S, v) ? 'ليس لهذه الآية بعدُ مختصر من كلام الشيخين، فهذا معناها من «التفسير الميسر»، وليس من كلامهما' : 'المعنى الإجمالي للآية من «التفسير الميسر»، وليس من كلام الشيخين') + '</small></div>';
  const p = document.createElement('p'); p.className = 'muy-text'; p.textContent = row[0]; box.appendChild(p);
  if (row[1]){ const f = document.createElement('p'); f.className = 'muy-fn'; f.textContent = row[1]; box.appendChild(f); }
  const cr = document.createElement('a'); cr.className = 'muy-credit'; cr.href = MUYM.url || 'https://quranenc.com/ar/browse/arabic_moyassar'; cr.target = '_blank'; cr.rel = 'noopener';
  cr.textContent = (MUYM.credit || 'التفسير الميسر') + ' — الإصدار ' + (MUYM.version || '') + ' · QuranEnc.com';
  box.appendChild(cr);
  const imams = document.querySelectorAll('#main section.imam');
  if (noImamWords(S, v) || !imams.length) vt.after(box); else imams[imams.length - 1].after(box);
};



// ===== «انسخ بالإحالة»: copy one summary sentence with its imam, book/page and the verse link =====
const _render4 = render;
render = function(){
  _render4();
  if (state.q) return;
  const s = state.s, v = state.ay, S = cache[s]; if (!S) return;
  const hasPage = v && ['IT','IQ'].some(a => ((((S.summ||{})[a]||{})[v]||[]).length) || ((((S.nuq||{})[a]||{})[v]||[]).length));
  const link = hasPage ? location.origin + '/ayah/' + s + '-' + v + '.html' : location.origin + '/tafsir.html#s' + s + 'a' + v;
  document.querySelectorAll('section.imam').forEach(sec => {
    const a = sec.classList.contains('IT') ? 'IT' : 'IQ';
    const pts = ((S.summ||{})[a]||{})[v] || [];
    sec.querySelectorAll('ul.points > li.pt').forEach((li, i) => {
      const pt = pts[i]; if (!pt || li.querySelector('.cpybtn')) return;
      const b = document.createElement('button'); b.type = 'button'; b.className = 'cite cpybtn'; b.textContent = 'انسخ بالإحالة';
      b.addEventListener('click', () => {
        const txt = '«' + pt.t + '»\n— ' + FULL[a] + '، ' + shortRef(S, pt.b, pt.v, pt.p) + '\n' + (v ? 'تفسير ' + SURAHS[s].name + ' ' + AR(v) + ' — ' : '') + 'جامع تفسير الشيخين: ' + link;
        const done = () => toast('نُسخت الجملة مع الإحالة');
        try { navigator.clipboard.writeText(txt).then(done, () => prompt('انسخ:', txt)); } catch(e){ prompt('انسخ:', txt); }
      });
      const body = li.querySelector('.pt-body'); if (body) body.appendChild(b);
    });
  });
};

// start a search from ?q= (home page search box)
(function(){ const q0 = new URLSearchParams(location.search).get('q'); if (q0){ qEl.value = q0; state.q = q0; state.qshown = 25; setTimeout(() => render(), 300); } })();

// verse finder on the tafsir search box
if (window.attachVerseFinder) attachVerseFinder(qEl, (s, v) => { state.q = ''; qEl.value = ''; go(s, v, true); });

// home surah index: plain links to /surah/N.html for crawlers; a click opens that surah's verse grid in the app (every verse, incl. ones with only al-Muyassar)
document.querySelectorAll('.sura-index a.sura').forEach(a => a.addEventListener('click', e => {
  const m = /\/surah\/(\d+)\.html$/.exec(a.getAttribute('href') || '');
  if (!m || e.ctrlKey || e.metaKey || e.shiftKey || e.button) return;
  e.preventDefault();
  goSurah(+m[1]).then(() => {
    const g = document.querySelector('section.surah'); if (!g) return;
    const top = [...document.querySelectorAll('header, .controls, .search')].filter(x => /sticky|fixed/.test(getComputedStyle(x).position)).reduce((h, x) => Math.max(h, x.getBoundingClientRect().bottom), 0);
    window.scrollTo({top: g.getBoundingClientRect().top + scrollY - top - 8});
  });
}));
