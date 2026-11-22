# Full pass — brief for each reviewer (tafsirshaikhain.com)
The site shows per Quran verse short excerpts of the VERBATIM words of Ibn Taymiyya (IT) / Ibn al-Qayyim (IQ) ("summ"),
and under each a button «اقرأ الفقرة كاملة» that opens the FULL PASSAGE (the record the excerpt comes from). All text is
already machine-verified as exact book text — never judge spelling. Your job is judgement on 4 points for every item:
1. VERSE — the excerpt explains THIS verse (not merely lists it, not really about a neighbouring verse / another verse
   with the same wording). Wrong verse → MOVE.
2. EXCERPT COMPLETE — a self-standing meaningful sentence: no dangling referent («هذا», «ذلك», «بهذا كله» with nothing
   before it), not cut mid-phrase, and the imam does not immediately qualify/restrict/reject it right after («لكن»,
   «إلا أن», «وهذا ضعيف»…). Fix with TRIM (a verbatim substring of the PASSAGE, may be longer or shorter than the excerpt).
3. FULL PASSAGE COMPLETE — PASSAGE START/END must begin and end at sensible points: not mid-sentence, not mid-argument,
   not cut before the imam's conclusion on this verse. Use BOOK BEFORE/AFTER PASSAGE to judge. If whole neighbouring
   paragraphs would fix it → FULL with how many paragraphs to add before/after (0-3). NOTE: passages that merely start/
   end mid-sentence at a paragraph split are fixed AUTOMATICALLY for the whole site — do NOT write FULL for that. Write
   FULL only when the passage is cut before the imam's conclusion/answer on this verse, or starts inside a quotation or
   argument so that the reader cannot tell who speaks.
4. SPEAKER — the imam's own voice, not a quotation of another scholar, an objector («قالوا», «فإن قيل»), a reported
   view («وقيل»), a party's argument in a debate, a questioner, a compiler (Mustadrak/al-Ikhtiyarat), or one imam
   copying the other unnamed. Few problems are expected here, but check. Unsure speaker → DROP.
Known section: Bada'i' al-Fawa'id vol 2 pp.58-105 is al-Suhayli's Nata'ij al-Fikr quoted verbatim (opens «قال السهيلي:» 2/58, closes «هذا نص كلام السهيلي بحروفه» 2/105) — only «قلت:» passages there are IQ's.
Owner rules: (DEC2) where IQ composes a debate and speaks through the side HE holds, keep it as his words with a context
line: `CTX | «short Arabic line naming the frame and book»`. (DEC1) Majmu' al-Fatawa 15/10-28 and Bada'i' al-Fawa'id
3/2-18 are kept under both imams — do not drop for authorship.

Work dir: /tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad . Book text: out/cache/{WORK}.pkl
(pickle, key 'paras' = list of {header,text,vol,p_start,p_end}); records: site/s{SU}.json 'recs' (+ site/s{SU}i.json).
Tafsir Ayat Ashkalat (not in out/cache) is in books/ashkalat_pages.json. Fast normalized search over all books: audit/h_S07_nx.py (read it for usage). Write helpers only as audit2/h_<NAME>_*.py.
Never edit anything except your output file. Be efficient: most items are KEEP — read deeper only when something looks off.

## Output — audit2/out/<NAME>.txt, one line per item in packet order (several lines allowed for one ID), append as you
go; if the file exists, continue after the last ID in it:
- `ID | KEEP`   (add `| ? reason` when a human should look)
- `ID | MOVE | SU:V | reason`
- `ID | TRIM | «exact substring of the passage» | reason`
- `ID | FULL | prev=N next=M | reason`
- `ID | NUQ | WHO | STANCE | reason`   (stances: أقرّه · استشهد به · حكاه · ردّه · رجّح غيره · أقرّه وشرحه · أقرّه وزاد عليه)
- `ID | CTX | «…» | reason`
- `ID | DROP | reason`
Final reply (short): counts per decision, and any book section that is systematically someone else's text (WORK vol/page).
