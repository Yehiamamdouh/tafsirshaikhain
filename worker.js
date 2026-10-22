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
const recent = new Map(); // soft per-isolate rate limit

export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    if (url.pathname !== "/api/feedback") return env.ASSETS.fetch(req);
    if (req.method !== "POST") return json({ error: "method" }, 405);

    const ip = req.headers.get("cf-connecting-ip") || "0";
    const now = Date.now(), hits = (recent.get(ip) || []).filter(t => now - t < 3600e3);
    if (hits.length >= 5) return json({ error: "أرسلت ملاحظات كثيرة، حاول بعد ساعة." }, 429);

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
    if (!ts.success) return json({ error: "فشل التحقق، أعد المحاولة." + ((env.TURNSTILE_SECRET || env.SecretKey) ? "" : " [no secret]") + " (" + (ts["error-codes"] || []).join(",") + ")" }, 400);

    const email = get("email").slice(0, 120);
    const text = [
      "الآية: " + ref, "الإمام: " + get("imam"), "النوع: " + get("kind"),
      "البريد: " + (email || "-"), "", body,
    ].join("\n");
    const raw = [
      "From: " + hdr("جامع تفسير الشيخين") + " <" + env.FEEDBACK_FROM + ">",
      "To: <" + env.FEEDBACK_TO + ">",
      ...(email && /^[^@\s<>]+@[^@\s<>]+$/.test(email) ? ["Reply-To: <" + email + ">"] : []),
      "Subject: " + hdr("تصويب: " + ref),
      "Message-ID: <" + crypto.randomUUID() + "@" + env.FEEDBACK_FROM.split("@")[1] + ">",
      "Date: " + new Date().toUTCString(),
      "MIME-Version: 1.0",
      "Content-Type: text/plain; charset=UTF-8",
      "Content-Transfer-Encoding: base64",
      "", b64(text),
    ].join("\r\n");
    try {
      await env.MAIL.send(new EmailMessage(env.FEEDBACK_FROM, env.FEEDBACK_TO, raw));
    } catch (e) { return json({ error: "تعذّر الإرسال الآن. (" + String(e && e.message || e).slice(0, 200) + (env.FEEDBACK_TO ? "" : " | no FEEDBACK_TO") + ")" }, 500); }
    hits.push(now); recent.set(ip, hits);
    return json({ ok: true });
  },
};
