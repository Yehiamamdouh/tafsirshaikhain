# Specialist triage — settle every open «?» that can be settled from the books; leave the rest for a human scholar

Site: tafsirshaikhain.com shows, under each Quran verse, verbatim excerpts («مختصر») from Ibn Taymiyya (IT) and Ibn
al-Qayyim (IQ), and «نقل» items (another person's words quoted by the imam, with who said it and the imam's stance).
Several review rounds left ~570 items with an open question («?»). Many were later fixed by other rounds, so the
question may already be moot. Your job: for each item, look at the CURRENT text on the site and decide whether the
question is settled, fixable, or really needs a human specialist (عالم متخصص).

Paths: SC = /tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad
Your packet: `SC/spec/pk/<NAME>.txt` → write `SC/spec/out/<NAME>.txt`.
Item block: `### ID — surah verse — imam — مختصر|نقل`, the verse, the current site sentences `[i] recN (book v/p) w=WORK: «…»`
(for نقل also who/st/rt), the open questions from earlier rounds, then the full stored passage(s) `النص الكامل recN … w=WORK:`.

## Tools
- Book paragraphs beyond the stored passage: `python3 SC/spec/nb.py WORK "key words" [before] [after]` prints the book
  paragraphs around the first paragraph containing the key (WORK = the `w=` code). Use it whenever the question is
  "what comes before/after", "whose voice is this", "does the imam give a verdict later", "is this al-Suhayli".
  Some works (e.g. Ashkalat) have no cache: then say so.
- Exact cutting: build any proposed text by copying from the printed passage/paragraphs with a script, never retype Arabic.

## Decide, per item, ONE of
- `KEEP` — the question is moot or answered: the current text is the imam's own voice, on this verse, meaning complete
  enough, nothing misleading. Give the reason in one line (Arabic or English).
- `FIX` — settle it with a verbatim change you can justify from the book: `TRIM «exact shorter text»`,
  `EXT «exact longer text from same passage/next paragraphs»`, `DROP` (not the imam's voice / not this verse / misleading),
  `NUQ WHO ST` (it is someone else's words: convert to a نقل with speaker and stance), `CTX «short Arabic context line»`
  (only when the words are the imam's but need one framing line, e.g. «من حجة الخصم التي يرد عليها ابن القيم»),
  `RT «exact imam rejoinder text»` for a نقل missing its rejoinder.
- `HUMAN` — cannot be settled from the texts available: attribution genuinely unclear (e.g. Bada'i' grammar sections that
  may be al-Suhayli's), edition corruption that changes meaning, pages missing from the cache, sensitive doctrinal
  passages (فناء النار) the owner wants a scholar to judge, or the imam's verdict lies beyond what is stored and cannot be
  cut verbatim. Then write the question for the scholar **in clear Arabic, one or two lines**, naming the book/page and
  what exactly he must decide (e.g. «هل هذه الفقرة في بدائع الفوائد ٢/٦٠ من كلام السهيلي أم من كلام ابن القيم؟»).

Be decisive: a reviewer's earlier «?» that the current text already answers is KEEP. A verse cited only as one example
in a list, where the sentence shown is still the imam's own statement bearing on the verse, is KEEP (the owner accepted
this class). «هذا/ذلك» pointing at the verse shown above is fine. Don't send to HUMAN what a careful reader of the
paragraphs can decide.

## Output — one line per item, in packet order
`ID | KEEP|FIX|HUMAN | detail | reason`
- KEEP: detail `-`.  FIX: detail = the FIX form above (texts exact, from the stored passage or nb.py paragraphs; say which
  paragraph index if from nb.py).  HUMAN: detail = the Arabic question for the scholar.
Validate: every ID of the packet present, in order. Finish with counts and 2–3 lines on anything systematic.
Helper scripts go in SC/spec/ named h_<NAME>_*.py. Edit nothing else.
