# جامع تفسير الشيخين — tafsirshaikhain.com

Interactive tafsir of Ibn Taymiyya (IT) and Ibn al-Qayyim (IQ). Owner talks in Egyptian Arabic; reply in Arabic.
Footer credit is "Developed by Doers" only — never put the owner's name on the site.

## Layout
- `public/` — the deployed site (Cloudflare Workers static assets). **Generated** — don't hand-edit.
- `src/` — templates + build scripts (source of truth for the site look/behaviour):
  - `build_public.py` → writes everything in `public/` (home = interactive app `app.html` + `patch.js`,
    about/privacy/books pages, static Arabic pages `ayah/S-V.html`, `surah/N.html`, `book/*.html`, sitemap, robots),
    then runs `build_langs.py` (14 languages; their pages are pre-rendered into `public/lp/{lang}/*.json`
    packs and served by `worker.js` — keeps the file count far below the 20k free-plan limit).
  - `head.html`, `footer.html`, `theme.css`, `home.html` (shaykh bios), `about.html`, `privacy.html`,
    `patch.js` (app add-ons), `qsuggest.js` (Quran-text verse finder), `i18n.js` + `i18n/` (UI strings), `sw.js`.
  - `data/simple.json` (Tanzil Quran text), `data/chapters.json` (surah names).
- `worker.js` + `wrangler.jsonc` are copied to the repo root by the build. Worker: `/api/feedback`
  (Turnstile + Email Routing; secrets live in the Cloudflare dashboard only) and language pages.

## Build & deploy
```
python3 src/build_public.py .      # rebuild public/ from src/ + current public/*.json data
git add -A && git commit && git pull --rebase && git push   # push to main = auto deploy (Workers Builds)
```
Check pages at a 390px mobile viewport (Playwright/Chromium is available) before pushing; no horizontal scroll.

## Content data — do NOT edit here
`public/s*.json` (verses, summaries `summ`, quotations `nuq`, records) come from a separate content pipeline
(another Claude session) that verifies every summary verbatim against the books. A website session must not
change quoted text, summaries, or their attribution. Layout, SEO, UX, translations of the UI = fine.

## Rules
- Imams' words are shown verbatim in Arabic; never translate or paraphrase them (risk of distortion).
- QuranEnc translations: show unmodified with title + version credit.
- Usage terms: sharing for knowledge allowed, selling forbidden (2:41).
