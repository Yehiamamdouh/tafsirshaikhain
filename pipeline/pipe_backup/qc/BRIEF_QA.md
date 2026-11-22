# Blind second review — new excerpts on tafsirshaikhain.com

The site shows, under each Quran verse, short **verbatim** excerpts («مختصر») from Ibn Taymiyya (IT) or Ibn al-Qayyim
(IQ). The excerpts in your packet were added recently by ONE reviewer. You are the independent second check. You have
not seen their reasoning — judge each excerpt fresh and strictly. A wrong excerpt under a Quran verse is far worse than
none: when in real doubt, do not pass it.

Paths: SC = /tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad
Packet `SC/qc/pk/<NAME>.txt` → write `SC/qc/out/<NAME>.txt`.
Item: `### A### — SU:V — imam — WORK#i (vol/page)`, the VERSE, the EXCERPT, and the book paragraphs around it.
More context: `python3 SC/bp/pp.py WORK i [before] [after]` prints whole paragraphs (use it whenever the speaker or the
verdict is not clear from what is shown).

## Pass (OK) only if ALL hold
1. **The imam's own voice** — not an objector («فإن قيل»، «قالوا»), not a reported view («وقيل»، «قال فلان»), not
   hadith/athar text, not another author he copies, not one party's argument in a debate he reports, not a view he
   rejects or only entertains («وقد يقال» without adopting it).
2. **About THIS verse** — its meaning, a word, its ruling or the imam's lesson from it; not a neighbouring verse, not a
   verse only quoted as one item in a list, not a verse cited only as a parallel.
3. **Complete for a researcher** — contains his conclusion; no dangling reference («هذا، ذلك، هو، القولين، الوجه
   الثاني…») to something the reader cannot see (the verse shown above the excerpt counts as visible); not cut before a
   restriction or a rejection that follows; if he lists views, his choice is visible.
4. **Text sound** — the edition text inside the excerpt is not garbled in a way that changes or blocks the meaning.

## Output — one line per item, packet order
`A### | OK | -`
`A### | DROP | reason (one line)` — fails 1, 2 or 4, or 3 can't be fixed inside the shown paragraphs.
`A### | TRIM | «exact shorter text» | reason` — only removing words fixes it (start later / end earlier). Build the text
   with `python3 SC/bp/cut.py WORK i "first words" "last words"` and copy its output by script, never retype Arabic.
`A### | HUMAN | Arabic question for a scholar (book/page, what to decide)` — genuinely unsettlable from the texts.
Be decisive; give the reason in English or Arabic. Finish with counts and anything systematic.
Helper scripts only as `SC/qc/h_<NAME>_*.py`. Edit nothing else.
