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

## Two sessions share this repo — coordination
Two Claude sessions push here: the **website session** (edits `src/` only: templates, build scripts, worker, UI
strings) and the **content session** (edits `public/s*.json` data only). Both then run the build and commit `public/`.
- **Pull first, build last:** `git pull origin main` before building, and build again right before committing, so
  `public/` is always generated from the latest `src/` + latest data. Never commit a `public/` built from an old checkout.
- **Never hand-merge generated files.** If a pull/rebase conflicts in `public/**` or `src/data/lastmod.json`, take
  either side (`git checkout --theirs …`), re-run `python3 src/build_public.py .`, then `git add -A` and continue.
- **`src/data/lastmod.json` must be committed with every build and never deleted or reset.** It holds each page's
  content hash + the date that content last changed; the sitemaps' `<lastmod>` comes from it. Deleting it would stamp
  every URL with today's date.
- Stay in your lane: the website session never edits `public/s*.json`; the content session doesn't change `src/`
  templates or scripts (ask the owner and leave it to the website session instead).
- `build_public.py` rebuilds `public/ayah/` from scratch: a verse whose summaries move away loses its page, and the
  Worker 301-redirects that URL to its surah page. That is expected, not a bug.

## Content data — do NOT edit here
`public/s*.json` (verses, summaries `summ`, quotations `nuq`, records) come from a separate content pipeline
(another Claude session) that verifies every summary verbatim against the books. A website session must not
change quoted text, summaries, or their attribution. Layout, SEO, UX, translations of the UI = fine.

## Rules
- Imams' words are shown verbatim in Arabic; never translate or paraphrase them (risk of distortion).
- QuranEnc translations: show unmodified with title + version credit.
- Usage terms: sharing for knowledge allowed, selling forbidden (2:41).
