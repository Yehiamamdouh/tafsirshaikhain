# Quotations ("نقول") — completeness review (tafsirshaikhain.com)
Each item is a QUOTE of someone else (WHO) that Ibn Taymiyya (IT) / Ibn al-Qayyim (IQ) brings under a verse, with his STANCE
(أقرّه · استشهد به · حكاه · ردّه · رجّح غيره · أقرّه وشرحه · أقرّه وزاد عليه) and sometimes a REJOINDER (rt) = the imam's own
words answering/judging the quote. Text is machine-verified verbatim — never judge spelling. WHO/STANCE were already
reviewed once; this pass is about COMPLETENESS, but fix a clearly wrong WHO/STANCE if you see one.
Check for every item:
1. QUOTE COMPLETE — the quoted view is a self-standing meaningful sentence: not cut mid-phrase, no dangling referent, it
   contains what makes it a view on THIS verse, and it does not swallow the imam's own words (his framing «قال فلان» is ok
   to leave out; his verdict must NOT be inside the quote). Fix with TRIM «exact substring of the passage».
2. REJOINDER — if present: is it really the imam's own reply to this quote, and complete? Fix with RT «exact substring
   of the passage» or `RT | -` to remove it. If missing but the imam judges the quote right after (e.g. «وهذا ضعيف»,
   «والصواب…»), you may add one with RT «…».
3. FULL PASSAGE — the passage (shown under «اقرأ الفقرة كاملة») should include the imam's judgement on the quote. If it
   is in a neighbouring paragraph → FULL prev=N next=M (0-3). Plain sentence splits are fixed automatically — skip those.
4. VERSE — the quote is about THIS verse; else MOVE SU:V (same rule as before).
If the "quote" is really the imam's own words → SUMM. Not worth showing → DROP.
Work dir: /tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad . Book text: out/cache/{WORK}.pkl
(key 'paras'); records site/s{SU}.json 'recs' (+ s{SU}i.json). Tafsir Ayat Ashkalat: books/ashkalat_pages.json. Fast search:
audit/h_S07_nx.py. Helpers only as audit4/h_<NAME>_*.py. Edit nothing but your output file. Most items are KEEP.
## Output — audit4/out/<NAME>.txt, one line per item in packet order (several lines per ID allowed), append as you go;
if the file exists, continue after the last ID in it:
`ID | KEEP` (`| ? reason` for a human) · `ID | TRIM | «…» | reason` · `ID | RT | «…» | reason` · `ID | RT | - | reason` ·
`ID | FULL | prev=N next=M | reason` · `ID | WHO | new | reason` · `ID | ST | new | reason` · `ID | MOVE | SU:V | reason` ·
`ID | SUMM | reason` · `ID | DROP | reason`
Final reply (short): counts per decision and any systematic problem (WORK vol/page).
