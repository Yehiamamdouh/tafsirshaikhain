# Collation wave — picking verbatim headlines (brief for each worker)

## The project
tafsirshaikhain.com shows, for every Quran verse, short excerpts of the **verbatim** words of Ibn Taymiyya (IT) and
Ibn al-Qayyim (IQ), each linked to its source book/page; "اقرأ الفقرة كاملة" opens the full paragraph.
The site's about page promises the work was collated against the printed compilations (دقائق التفسير للجليند،
تفسير شيخ الإسلام للقيسي (IT); بدائع التفسير ليسري السيد محمد، تفسير ابن القيم/دار الهلال (IQ)) and that what
they had and we missed was added. You are doing that "added" step.

A script already found **candidate verses**: verses where a compilation contains a passage of imam X (matched to
our own copy of the source book) linked to the verse, but the site has nothing from imam X on that verse.
Many candidates are false leads (the verse is only cited in passing, inside a list, etc.). Skipping is normal —
expect to fill maybe 30–50%.

## Tool
Work dir: `/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad`
`python3 coll/cshow.py IMAM SU [verse-range]` prints, per candidate verse, up to 5 records:
`--- IMAM recID WORK vol/page (verses cited in record: N; in: <compilation>)`, then a window of the record around
the quoted verse (⟦…⟧), then `+1:`, `+2:`, `+3:` = the next book paragraphs (the comment often follows the verse).
Full record text: `site/s{SU}.json` → `recs` (+ `site/s{SU}i.json`), match `id`. Book paragraphs:
`out/cache/{WORK}.pkl` (pickle; key `paras`, list of {header,text,vol,p_start,p_end}) — read more context there
when needed (preceding paragraphs to check who is speaking).

## Output — one line per filled verse
`SU:V IMAM RECID «text»`      text is inside the record
`SU:V IMAM RECID+K «text»`    text is inside paragraph +K (K=1..3) shown by cshow (record paragraph … +K are joined)
At most ONE line per verse. Validate with `python3 coll/capply.py --check <your file>` → must end `bad 0`.

## What qualifies (all must hold)
1. **Verbatim**: an exact substring (whitespace-normalized) — copy, don't retype; keep source spelling, brackets,
   typos. No footnote digits glued to words (e.g. «شهداءكم6»): cut around them or skip.
2. **A short, useful, complete sentence** (not half a sentence), roughly 40–300 characters (hard max 420). It must
   make sense alone as a headline about THIS verse: an explanation, meaning, ruling, lesson, wording point.
   It may start with «أي» or «فأخبر/فبين…» when that reads complete. Don't start mid-word.
3. **The imam's OWN words.** Not: quotes of others (scholars, Salaf reports «قال ابن عباس/قتادة…», hadith/athar,
   poetry), an opponent's/objector's argument («قالوا», «فإن قيل», «قالت طائفة», «قالت الفقراء/الأغنياء»,
   the Rafidi in منهاج السنة, Ibn Arabi's Fusus, Ibn Rushd/al-Ash'ari/al-Darimi/al-Muhasibi/Ibn Qutayba texts IT quotes,
   al-Harawi's Manazil text in مدارج السالكين, al-Suhayli in بدائع الفوائد, al-Shafi'i's Risala in إعلام الموقعين),
   or a view he reports in order to reject. Check the preceding paragraphs when a quotation might still be open.
   If unsure who is speaking → skip.
4. **About this verse**: the passage really comments on it, not just lists it among other verses.
5. **Not fana' al-nar** material: skip ShifaCalil paragraphs 513–530, HadiArwah 1311–1374, and the book
   RaddCalaManQalaBiFanaJanna entirely.

## Rules
- **Write incrementally**: append your lines to your output file after finishing EACH surah (the machine can restart;
  unsaved work is lost). If your output file already has lines when you start, continue after the last surah in it.
- Write only your own output file (name given in your task). Helper scripts: `coll/w<slice>_*.py`. Don't edit
  anything else; don't run apply/build/git.
- Final reply (short): lines written / verses skipped, and any attribution problem you noticed in existing data
  (e.g. a record whose words are someone else's) with SU/rec/work/page.
