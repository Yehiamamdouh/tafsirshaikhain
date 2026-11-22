# New excerpts from book paragraphs — verses that still have nothing on the site

Site: tafsirshaikhain.com shows, per Quran verse, short **verbatim** excerpts («مختصر») of Ibn Taymiyya (IT) and
Ibn al-Qayyim (IQ) explaining that verse, with the full passage under «اقرأ الفقرة كاملة». The verses in your packet
have NO excerpt yet. The imams' books quote them somewhere; your packet shows, per verse, up to 3 book paragraphs that
quote it (the best-scoring ones). Decide whether a paragraph holds a REAL explanation of THIS verse by the imam himself,
and if so cut the excerpt. **Most verses are only cited in passing** (a proof-text in a list, an example, a verse quoted
inside a longer chain) → `NONE` is the normal, correct answer. Never force an excerpt. A wrong excerpt on a Quran
verse is far worse than a missing one.

Paths: SC = /tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad
Your packet: `SC/bp/pk/<NAME>.txt` → write `SC/bp/out/<NAME>.txt`.
Block: `### SU:V — VERSE: …  (N paragraphs quote it)`, then per paragraph `-- IT|IQ WORK#i (vol/page) [section header]`
and its text (a window if long, marked …), sometimes `[#i+1 التالية]` = the start of the next paragraph.

## Tools
- `python3 SC/bp/pp.py WORK i [before] [after]` prints whole paragraphs around #i (index, page, header, full text).
  Use it whenever you need: what comes before (whose voice? an objection? «قالوا»?), what comes after (the imam's
  verdict, a restriction, a rejection), or the full text of a windowed paragraph.
- `python3 SC/bp/cut.py WORK i "first words" "last words"` prints the exact span (it starts in paragraph #i and may run
  into #i+1/#i+2). **Build every excerpt with it and copy its output by script — never retype Arabic** (typing can
  reorder diacritics/letters and the line fails validation).
- Other paragraphs that quote the verse (the header says N): you may look at them only if a shown paragraph points
  there; you are not required to hunt.

## An excerpt is accepted only if ALL hold
1. **Verbatim & contiguous**: exact text starting in paragraph #i (may continue into #i+1/#i+2); no joining of
   non-adjacent text, no added words, no «…».
2. **The imam's own voice**: not an objector («فإن قيل», «قالوا», «احتجوا»), not a reported view («وقيل», «قال
   فلان»), not a hadith/athar text, a poem, or another author he copies; not one side's argument in a debate the imam
   reports (e.g. Hadi al-Arwah ch. 6 sets out the two parties' arguments about the garden of Adam — those are the
   parties' words, not his verdict) unless the imam explicitly adopts it.
3. **Explains THIS verse**: its meaning, a word's sense, its ruling, or the lesson the imam draws from it — not just
   quoting it as one item of a list, and not the meaning of a neighbouring verse.
4. **Complete meaning for a researcher** (the 5 conditions of the site's last review):
   a. contains the imam's conclusion on the verse, not only his introduction or the first step of a proof;
   b. no dangling reference («هذا، ذلك، كما تقدم، القول الثاني، الوجه الأول، هو…») to something the reader cannot see —
      the verse is shown right above the excerpt, so a reference to this verse or its words is fine;
   c. not cut before a restriction that changes the meaning («لكن، إلا أن، بشرط، ما لم، غير أن…») — and not
      immediately rejected/qualified by the imam right after;
   d. if he lists several meanings, all appear or his chosen one appears with his own words showing it is his choice
      («والصحيح، والأظهر، وهذا أصح…»);
   e. nothing unrelated; short: start at the sentence carrying the verse's meaning (often the verse citation itself),
      end right after the verdict/restriction. Aim 40–400 chars; hard max 700. If longer is unavoidable, split into
      **two** excerpts (two lines, each contiguous). Max 2 excerpts per imam per verse.
5. If both IT and IQ explain the verse, give both (separate lines).

Editor context lines (CTX) — only the two owner-approved forms, written in the reason field:
`CTX «وهذا اختيار الإمام»` (his choice among meanings is clear but not in his own short words) and
`CTX «ينقل كلام <name> ويقرّه»` (he copies and endorses another author named far back). Nothing else.
If a real explanation exists but cannot meet the conditions verbatim (needs a referent from far away, the verdict is
pages later, attribution unclear, edition text looks corrupt), write `NONE` with reason starting `HUMAN:` + one Arabic
line saying what a specialist must decide (book/page). Use HUMAN sparingly.

## Output — `SC/bp/out/<NAME>.txt`, packet order, one or more lines per verse, append as you go
- `SU:V | IT|IQ | WORK#i | «exact excerpt» | reason (short; + CTX if any)`
- `SU:V | NONE | reason (short: e.g. "list of proof-texts", "objector's words", "explains 2:31 not 2:32")`
If the output file already exists (you are resuming), continue after the last verse in it.
Validate before finishing: `python3 SC/bp/chk.py SC/bp/out/<NAME>.txt SC/bp/pk/<NAME>.txt` must say `bad 0`.
Final reply (short): counts (verses with excerpts / NONE / HUMAN), anything systematic, items you were unsure about.
Helper scripts only as `SC/bp/h_<NAME>_*.py`. Edit nothing else.
