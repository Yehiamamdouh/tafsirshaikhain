// Cloudflare Worker: serves the static site (./public) and handles the feedback form.
// Secrets/vars (set in the Cloudflare dashboard, never in the repo):
//   TURNSTILE_SECRET  - Turnstile secret key
//   FEEDBACK_TO       - destination address (must be a verified Email Routing destination)
//   FEEDBACK_FROM     - sender on your domain, e.g. feedback@tafsirshaikhain.com
// Binding: MAIL (send_email) — see wrangler.jsonc
import { EmailMessage } from "cloudflare:email";

const json = (o, s = 200) => new Response(JSON.stringify(o), { status: s, headers: { "content-type": "application/json; charset=utf-8" } });
const b64 = s => btoa(String.fromCharCode(...new TextEncoder().encode(s)));
const hdr = s => "=?UTF-8?B?" + b64(s) + "?=";
const recent = new Map();
// Verse/surah pages for languages that have no static files: pre-rendered HTML lives in /lp/{lang}/{surah}_{chunk}.json
const DYN = /^\/(bn|ms|fa|ru|sw|ha|es|de|zh)(?:\/(?:(ayah\/(\d{1,3})-(\d{1,3})|surah\/(\d{1,3}))\.html)?)?$/;
async function langPage(req, env, url, m) {
  const [, l, , as, av, ss] = m;
  if (url.pathname === "/" + l) return Response.redirect(url.origin + "/" + l + "/", 301);
  const cache = caches.default, hit = await cache.match(req);
  if (hit) return hit;
  let file = "home", key = "";
  if (as) { file = as + "_" + Math.floor(+av / 50); key = "ayah/" + as + "-" + av + ".html"; }
  else if (ss) { file = ss + "_0"; key = "surah/" + ss + ".html"; }
  const r = await env.ASSETS.fetch(new Request(url.origin + "/lp/" + l + "/" + file + ".json"));
  const html = r.ok ? (await r.json())[key] : null;
  if (!html) return env.ASSETS.fetch(new Request(url.origin + "/404.html"));
  const res = new Response(html, { headers: { "content-type": "text/html; charset=utf-8", "cache-control": "public, max-age=3600" } });
  if (req.method === "GET") await cache.put(req, res.clone());
  return res;
} // soft per-isolate rate limit

export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    const m = url.pathname.match(DYN);
    if (m) return langPage(req, env, url, m);
    // html_handling is "none" so /x.html is served as-is (no redirect); directories map to index.html here
    if (url.pathname.endsWith("/")) return env.ASSETS.fetch(new Request(url.origin + url.pathname + "index.html", req));
    if (url.pathname !== "/api/feedback") {
      const r = await env.ASSETS.fetch(req);
      if (r.status !== 404 || /\.[a-z0-9]+$/i.test(url.pathname)) return r;
      // old pretty URLs (/ayah/2-255, /en) → canonical .html or directory
      for (const alt of [url.pathname + ".html", url.pathname + "/index.html"]) {
        const a = await env.ASSETS.fetch(new Request(url.origin + alt, { method: "HEAD" }));
        if (a.ok) return Response.redirect(url.origin + alt.replace(/index\.html$/, "") + url.search, 301);
      }
      return r;
    }
    if (req.method !== "POST") return json({ error: "method" }, 405);

    const ip = req.headers.get("cf-connecting-ip") || "0";
    const now = Date.now(), hits = (recent.get(ip) || []).filter(t => now - t < 3600e3);
    if (hits.length >= 5) return json({ error: "أرسلت ملاحظات كثيرة، حاول بعد ساعة." }, 429);

    const FROM = env.FEEDBACK_FROM || "feedback@tafsirshaikhain.com";
    if (!env.FEEDBACK_TO) return json({ error: "النموذج غير مهيأ بعد (FEEDBACK_TO)." }, 500);
    let f;
    try { f = await req.formData(); } catch { return json({ error: "bad form" }, 400); }
    const get = k => String(f.get(k) || "").trim();
    if (get("website")) return json({ ok: true });                       // honeypot: pretend success
    if (now - Number(get("t0") || now) < 4000) return json({ error: "تمهّل قليلًا ثم أرسل." }, 400);
    const ref = get("ref").slice(0, 60), body = get("body").slice(0, 3000);
    if (!ref || body.length < 5) return json({ error: "اكتب الآية والملاحظة." }, 400);
    if ((body.match(/https?:\/\//g) || []).length > 2) return json({ error: "الروابط الكثيرة غير مسموحة." }, 400);

    const ts = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", {
      method: "POST",
      body: new URLSearchParams({ secret: env.TURNSTILE_SECRET || env.SecretKey, response: get("cf-turnstile-response"), remoteip: ip }),
    }).then(r => r.json()).catch(() => ({}));
    if (!ts.success) return json({ error: "فشل التحقق، أعد المحاولة." }, 400);

    const email = get("email").slice(0, 120);
    const text = [
      "الآية: " + ref, "الإمام: " + get("imam"), "النوع: " + get("kind"),
      "البريد: " + (email || "-"), "", body,
    ].join("\n");
    const raw = [
      "From: " + hdr("جامع تفسير الشيخين") + " <" + FROM + ">",
      "To: <" + env.FEEDBACK_TO + ">",
      ...(email && /^[^@\s<>]+@[^@\s<>]+$/.test(email) ? ["Reply-To: <" + email + ">"] : []),
      "Subject: " + hdr("تصويب: " + ref),
      "Message-ID: <" + crypto.randomUUID() + "@" + FROM.split("@")[1] + ">",
      "Date: " + new Date().toUTCString(),
      "MIME-Version: 1.0",
      "Content-Type: text/plain; charset=UTF-8",
      "Content-Transfer-Encoding: base64",
      "", b64(text),
    ].join("\r\n");
    try {
      await env.MAIL.send(new EmailMessage(FROM, env.FEEDBACK_TO, raw));
    } catch (e) { return json({ error: "تعذّر الإرسال الآن." }, 500); }
    hits.push(now); recent.set(ip, hits);
    return json({ ok: true });
  },
};
