# جامع تفسير الشيخين — tafsirshaikhain.com

Static site (`public/`) + a small Cloudflare Worker (`worker.js`) for the feedback form.
Developed by [Doers](https://doersadv.com).

## Deploy (Cloudflare Workers + Git, one time)
1. Cloudflare dashboard → Workers & Pages → Create → Import a repository → this repo.
   Build command: *(none)* · Deploy command: `npx wrangler deploy`.
2. Domain (registered at Namecheap): add `tafsirshaikhain.com` to Cloudflare (Free plan),
   then in Namecheap → Domain → Nameservers → Custom DNS → paste the two Cloudflare nameservers.
3. Worker → Settings → Domains & Routes → add custom domain `tafsirshaikhain.com` (and `www`).
4. Feedback e-mail:
   - Domain → Email → Email Routing → enable, and add/verify the Gmail destination address.
   - Turnstile → add widget for `tafsirshaikhain.com` → copy **site key** into `TURNSTILE_SITEKEY`
     in `about.html` (or tell the maintainer) and the **secret key** as Worker secret `TURNSTILE_SECRET`.
   - Worker → Settings → Variables and secrets: add secret `FEEDBACK_TO` = the Gmail address.

Data updates are committed to `public/*.json`; every push redeploys automatically.
