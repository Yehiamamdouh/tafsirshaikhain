// Verse finder: as the user types, list Quran verses whose text matches the typed letters, narrowing to one.
(function(){
  const NAMES = ["الفاتحة","البقرة","آل عمران","النساء","المائدة","الأنعام","الأعراف","الأنفال","التوبة","يونس","هود","يوسف","الرعد","إبراهيم","الحجر","النحل","الإسراء","الكهف","مريم","طه","الأنبياء","الحج","المؤمنون","النور","الفرقان","الشعراء","النمل","القصص","العنكبوت","الروم","لقمان","السجدة","الأحزاب","سبأ","فاطر","يس","الصافات","ص","الزمر","غافر","فصلت","الشورى","الزخرف","الدخان","الجاثية","الأحقاف","محمد","الفتح","الحجرات","ق","الذاريات","الطور","النجم","القمر","الرحمن","الواقعة","الحديد","المجادلة","الحشر","الممتحنة","الصف","الجمعة","المنافقون","التغابن","الطلاق","التحريم","الملك","القلم","الحاقة","المعارج","نوح","الجن","المزمل","المدثر","القيامة","الإنسان","المرسلات","النبأ","النازعات","عبس","التكوير","الانفطار","المطففين","الانشقاق","البروج","الطارق","الأعلى","الغاشية","الفجر","البلد","الشمس","الليل","الضحى","الشرح","التين","العلق","القدر","البينة","الزلزلة","العاديات","القارعة","التكاثر","العصر","الهمزة","الفيل","قريش","الماعون","الكوثر","الكافرون","النصر","المسد","الإخلاص","الفلق","الناس"];
  const AR = n => String(n).replace(/\d/g, d => '٠١٢٣٤٥٦٧٨٩'[d]);
  const N = s => s.replace(/[ً-ْٰـ]/g, '').replace(/[إأآٱ]/g, 'ا').replace(/ى/g, 'ي').replace(/ة/g, 'ه').replace(/ؤ/g, 'و').replace(/ئ/g, 'ي').replace(/\s+/g, ' ').trim();
  let Q = null, loading = null;
  function load(){
    if (Q) return Promise.resolve(Q);
    return loading || (loading = fetch('/quran_clean.json').then(r => r.json()).then(d => {
      const rows = []; let k = 0;
      d.c.forEach((n, i) => { for (let v = 1; v <= n; v++){ const t = d.t[k++]; rows.push({s: i + 1, v, t, n: N(t)}); } });
      Q = rows; return Q;
    }));
  }
  const css = document.createElement('style');
  css.textContent = `.qs-box{position:absolute;inset-inline:0;top:calc(100% + 4px);z-index:50;background:var(--sheet,#fff);border:1px solid var(--gold-soft,#e3d8bf);border-radius:12px;box-shadow:0 8px 24px rgba(0,0,0,.12);max-height:min(60vh,420px);overflow:auto;text-align:start}
.qs-it{display:grid;gap:2px;width:100%;text-align:start;font:inherit;background:none;border:0;border-bottom:1px solid var(--line,#eee);padding:9px 14px;cursor:pointer;color:var(--ink,#222)}
.qs-it:last-child{border-bottom:0}.qs-it:hover,.qs-it[aria-selected=true]{background:var(--gold-soft,#f5ead2)}
.qs-t{font-family:"Amiri Quran","Amiri",serif;font-size:18px;line-height:1.9}.qs-t mark{background:var(--mark,#f7dc8f);color:inherit;border-radius:3px}
.qs-r{font-size:12.5px;color:var(--muted,#666)}.qs-h{font-size:12.5px;color:var(--muted,#666);padding:8px 14px}`;
  document.head.appendChild(css);
  function snippet(r, q){
    // map normalized match back onto the plain text by word position
    const words = r.t.split(' '), nw = words.map(N);
    const qw = q.split(' ');
    let start = -1;
    for (let i = 0; i < nw.length && start < 0; i++){
      const tail = nw.slice(i).join(' ');
      if (tail.startsWith(q) || (qw.length === 1 && nw[i].includes(q))) start = i;
    }
    const from = Math.max(0, start - 3), to = Math.min(words.length, (start < 0 ? 0 : start) + qw.length + 8);
    const esc = s => s.replace(/[&<>]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
    return (from > 0 ? '… ' : '') + words.slice(from, to).map((w, i) => {
      const j = from + i; return (start >= 0 && j >= start && j < start + qw.length) ? '<mark>' + esc(w) + '</mark>' : esc(w);
    }).join(' ') + (to < words.length ? ' …' : '');
  }
  window.attachVerseFinder = function(input, onPick){
    const host = input.parentElement; if (getComputedStyle(host).position === 'static') host.style.position = 'relative';
    const box = document.createElement('div'); box.className = 'qs-box'; box.hidden = true; box.setAttribute('role', 'listbox');
    host.appendChild(box);
    let items = [], sel = -1, timer;
    function close(){ box.hidden = true; sel = -1; }
    function pick(r){ close(); onPick(r.s, r.v); }
    function draw(q){
      const res = []; const starts = [];
      for (const r of Q){ const i = r.n.indexOf(q); if (i < 0) continue; (i === 0 ? starts : res).push(r); if (starts.length + res.length > 400) break; }
      if (!starts.length && !res.length){
        // the typed text may run across two verses: search each verse joined with the next
        for (let k = 0; k < Q.length - 1; k++){ const r = Q[k], nx = Q[k + 1]; if (nx.s !== r.s) continue;
          if ((r.n + ' ' + nx.n).indexOf(q) >= 0){ res.push(r); if (res.length > 400) break; } }
      }
      items = starts.concat(res).slice(0, 30);
      const total = starts.length + res.length;
      if (!items.length){ box.innerHTML = '<div class="qs-h">لا توجد آية بهذه الحروف.</div>'; box.hidden = false; return; }
      box.innerHTML = '<div class="qs-h">' + (total === 1 ? 'آية واحدة مطابقة — اضغطها لفتحها' : AR(total > 400 ? '٤٠٠+' : total) + ' آية مطابقة، اكتب أكثر لتضييق النتائج') + '</div>';
      items.forEach((r, k) => {
        const b = document.createElement('button'); b.type = 'button'; b.className = 'qs-it'; b.setAttribute('role', 'option');
        b.innerHTML = '<span class="qs-t">' + snippet(r, q) + '</span><span class="qs-r">سورة ' + NAMES[r.s - 1] + ' · الآية ' + AR(r.v) + '</span>';
        b.addEventListener('mousedown', e => { e.preventDefault(); pick(r); });
        box.appendChild(b);
      });
      sel = -1; box.hidden = false;
    }
    input.addEventListener('focus', () => load());
    input.addEventListener('input', () => {
      clearTimeout(timer);
      timer = setTimeout(() => {
        const q = N(input.value);
        if (q.replace(/ /g, '').length < 3){ close(); return; }
        load().then(() => draw(q));
      }, 120);
    });
    input.addEventListener('keydown', e => {
      if (box.hidden) return;
      const its = [...box.querySelectorAll('.qs-it')];
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp'){
        e.preventDefault(); sel = (sel + (e.key === 'ArrowDown' ? 1 : -1) + its.length) % its.length;
        its.forEach((x, k) => x.setAttribute('aria-selected', String(k === sel))); its[sel] && its[sel].scrollIntoView({block: 'nearest'});
      } else if (e.key === 'Enter' && sel >= 0){ e.preventDefault(); e.stopPropagation(); pick(items[sel]); }
      else if (e.key === 'Escape') close();
    });
    input.addEventListener('blur', () => setTimeout(close, 150));
  };
})();
