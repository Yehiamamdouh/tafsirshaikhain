// share button for the static verse pages (/ayah/S-V.html): verse + the imams' summary quotations verbatim + refs + link
(function(){
  const vt = document.querySelector('main.sp .vt'), h1 = document.querySelector('main.sp h1');
  if (!vt || !h1) return;
  const m = /سورة\s+(.+?)،\s*الآية\s+(\S+)/.exec(h1.textContent); if (!m) return;
  const title = 'تفسير الآية ' + m[2] + ' من سورة ' + m[1] + ' — ابن تيمية وابن القيم';
  const url = location.origin + location.pathname;
  const toast = msg => { const t = document.createElement('div'); t.textContent = msg; t.setAttribute('role', 'status'); t.style.cssText = 'position:fixed;inset-inline:16px;bottom:24px;margin:auto;max-width:320px;text-align:center;background:#18212e;color:#fff;padding:10px 14px;border-radius:10px;font-size:14px;z-index:9'; document.body.appendChild(t); setTimeout(() => t.remove(), 1800); };
  const fullText = () => {
    const parts = [vt.textContent.trim() + ' [' + m[1] + ': ' + m[2] + ']'];
    document.querySelectorAll('main.sp > section').forEach(sec => {
      const h2 = sec.querySelector('h2'); if (!h2) return;
      const items = [];
      for (const el of sec.children){
        if (el.tagName === 'H3') break;
        if (el.tagName !== 'BLOCKQUOTE') continue;
        const c = el.cloneNode(true), cite = c.querySelector('cite'), ref = cite ? cite.textContent.trim() : '';
        if (cite) cite.remove();
        items.push(c.textContent.trim() + (ref ? '\n— ' + ref : ''));
      }
      if (items.length) parts.push(h2.textContent.trim() + ':\n' + items.join('\n\n'));
    });
    parts.push(title + '\n' + url);
    return parts.join('\n\n');
  };
  const st = document.createElement('style');
  st.textContent = '.sharewrap{display:grid;justify-items:start;gap:6px;margin:8px 0}.sharemenu{display:flex;flex-wrap:wrap;gap:6px}.sharemenu button{font:inherit;font-size:14px;padding:6px 12px;border:1px solid var(--line,#d9dee6);border-radius:8px;background:var(--sheet,#fff);color:var(--ink,#18212e);cursor:pointer}.sharemenu[hidden]{display:none}';
  document.head.appendChild(st);
  const wrap = document.createElement('div'); wrap.className = 'sharewrap';
  const b = document.createElement('button'); b.type = 'button'; b.className = 'linkbtn sharebtn'; b.textContent = 'مشاركة';
  const menu = document.createElement('div'); menu.className = 'sharemenu'; menu.hidden = true;
  const open = u => window.open(u, '_blank', 'noopener');
  const copy = (txt, msg) => { const done = () => toast(msg); try { navigator.clipboard.writeText(txt).then(done, () => prompt('انسخ:', txt)); } catch(e){ prompt('انسخ:', txt); } };
  const mk = (label, fn) => { const a = document.createElement('button'); a.type = 'button'; a.textContent = label; a.addEventListener('click', () => { menu.hidden = true; fn(); }); menu.appendChild(a); };
  mk('WhatsApp', () => open('https://wa.me/?text=' + encodeURIComponent(fullText())));
  mk('Telegram', () => open('https://t.me/share/url?url=' + encodeURIComponent(url) + '&text=' + encodeURIComponent(fullText())));
  mk('Facebook', () => open('https://www.facebook.com/sharer/sharer.php?u=' + encodeURIComponent(url)));
  mk('X', () => open('https://twitter.com/intent/tweet?url=' + encodeURIComponent(url) + '&text=' + encodeURIComponent(title)));
  mk('نسخ النص مع الرابط', () => copy(fullText(), 'نُسخ النص مع الرابط'));
  mk('نسخ الرابط', () => copy(url, 'نُسخ رابط الآية'));
  b.addEventListener('click', async () => {
    if (navigator.share){ try { await navigator.share({title: title, text: fullText()}); } catch(e){ if (e && e.name !== 'AbortError') menu.hidden = false; } }
    else menu.hidden = !menu.hidden;
  });
  wrap.append(b, menu);
  vt.insertAdjacentElement('afterend', wrap);
})();
