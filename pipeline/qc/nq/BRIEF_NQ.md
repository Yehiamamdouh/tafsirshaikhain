# «تمام المعنى» review of the «نقل» items on tafsirshaikhain.com

Under each Quran verse the site shows (a) verbatim excerpts of Ibn Taymiyya (IT) / Ibn al-Qayyim (IQ), and (b) «نقل»
items: the words of SOMEONE ELSE that the imam quotes (a Companion, a mufassir, a grammarian, an opponent…), shown with
WHO said it, the imam's stance ST toward it, and — when he disagrees — his rejoinder RT. Earlier rounds checked speaker
and stance; nobody yet checked whether each نقل is COMPLETE and correctly bounded. That is your job.

Paths: SC = /tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad
Packet `SC/qc/nq/pk/<NAME>.txt` → write `SC/qc/nq/out/<NAME>.txt`.
Item: `### N#### — SU:V — imam — w=WORK (vol/page)`, VERSE, WHO | ST, NUQ TEXT, RT (if any), and a window of the stored
passage. More context: `python3 SC/spec/nb.py WORK "key words" [before] [after]` prints the book paragraphs around.
Exact cutting: `python3 SC/qc/nq/cut.py N#### "first words" "last words"` (cuts from the item's full stored passage) —
copy its output by script; never retype Arabic.

## A نقل passes only if ALL hold
1. **Right boundaries** — the text is the quoted party's words: it does not start mid-quote, does not stop before the
   quoted statement ends, and does not run on into the imam's own commentary (that belongs in RT or nowhere).
2. **Complete meaning** — no dangling reference («هذا، ذلك، هو، القول الثاني…») to something absent; the verse shown
   above counts as visible.
3. **About this verse.**
4. **WHO** names the speaker as the passage does (the closest attribution: «قال ابن عباس», «قال الزجاج», «قالت
   طائفة», «قالوا» → describe the party as the imam does). A wrong or missing name fails. WHO is a short label
   (≤ 60 chars): a name, optionally with a few words naming the topic in parentheses, e.g. «قيل (في الضمير في يتلونه)».
   Never put anyone's quoted words or a paraphrase of them in WHO; if the quote needs its referent, extend TEXT instead.
5. **ST** fits what the imam does with it, one of: أقرّه / أقرّه وزاد عليه / أقرّه وشرحه / استشهد به / حكاه / رجّح غيره / ردّه.
6. **RT** — when ST is ردّه or رجّح غيره and the imam's answer is in the passage, a short verbatim RT (≤ 400 chars, his
   own words, his verdict) must be shown; an RT already shown must be his words and complete. When the imam lists
   several views and then says the right meaning COMBINES them («والصحيح أنه يتناول الأمرين…»), each view's item gets
   ST «أقرّه وزاد عليه» with that combining verdict as RT.

## Output — one line per item, packet order
`N#### | OK | -`
`N#### | FIX | <fixes joined by " ;; "> | reason` where each fix is one of
   `TEXT «exact new span from the passage»` · `WHO «name as the imam gives it»` · `ST «one of the 7 values»` ·
   `RT «exact imam rejoinder from the passage»`
   When the needed text lies OUTSIDE the stored passage (quote runs past a page break, the imam's verdict comes later),
   take it from the book paragraphs: find them with `python3 SC/spec/nb.py WORK "key"` or
   `python3 SC/bp/pp.py WORK i [before] [after]`, cut with `python3 SC/bp/cut.py WORK i "first" "last"` (span starts in
   paragraph #i, may run into #i+1/#i+2), and write the fix as `TEXT@WORK#i «…»` or `RT@WORK#i «…»`.
`N#### | DROP | reason` (not about this verse / not a quotation at all / unfixable)
`N#### | HUMAN | Arabic question for a scholar (book/page, what to decide)` — sparingly.
Be decisive; a reviewer's doubt the text already answers is OK. Validate:
`python3 SC/qc/nq/chk.py SC/qc/nq/out/<NAME>.txt SC/qc/nq/pk/<NAME>.txt` must say `bad 0`.
Finish with counts and anything systematic. Helper scripts only as `SC/qc/nq/h_<NAME>_*.py`. Edit nothing else.
