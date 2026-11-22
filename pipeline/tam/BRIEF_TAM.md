# Review: «تمام المعنى للباحث» — is each headline excerpt enough on its own?

Site: tafsirshaikhain.com shows, under each Quran verse, short **verbatim** excerpts ("المختصر") from Ibn Taymiyya (IT)
and Ibn al-Qayyim (IQ), with the full passage under «اقرأ الفقرة كاملة». Earlier reviews already checked that each
excerpt is the imam's own voice, on the right verse, and a complete sentence. **This review asks a higher question:
does the excerpt alone let a researcher understand what the imam means by this verse?**

Paths: SC = /tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad
Your packet: `SC/tam/pk/<NAME>.txt` → write `SC/tam/out/<NAME>.txt`.
Each item: `### ID — surah verse — imam`, the verse, the excerpt sentences `[n] recN (book v/p): «…»` (optional
`[سطر سياق: …]` = an editor context line already shown), then the full passage(s) `النص الكامل recN …`.
One item = all excerpt sentences of one imam on one verse (judge them together).

## The 5 conditions (all must hold for «كاف»)
1. **Contains the imam's verdict / conclusion on the verse** — not only his introduction, premise, or the start of his proof.
2. **No dangling reference** to something absent from the excerpt: «هذا، ذلك، كما تقدم، القول الثاني، الوجه الأول، هو، هي…»
   whose referent the reader cannot see. (The site shows the verse right above the excerpt, so a pronoun/«هذا» that clearly refers to this verse or a word of it counts as visible — do NOT extend only to add the verse quote. Extend when the referent is something else: another verse, a hadith, a person, an earlier premise.)
3. **Not cut before a restriction that changes the meaning**: «لكن، إلا أن، بشرط، إذا، ما لم، غير أن…» that follow in the passage.
4. **Several meanings**: if the imam lists several meanings/views, either all appear, or the one he chose appears **with
   his own words showing it is his choice** («والصحيح…، والأظهر…، وهذا أصح…»). If his choice is clear in the passage but
   no short wording of his shows it, propose the excerpt of the chosen meaning and put `CTX «وهذا اختيار الإمام»` in the
   reason (owner-approved editor context line, shown under the excerpt).
5. **Nothing unrelated to the verse** is included; the excerpt stays short.

A short excerpt can be «كاف»: a precise gloss («أي باعوه») of an obscure word IS the imam's meaning of the verse, if
it stands on its own. Do not demand more than the imam himself said about this verse.

## Editor context lines (CTX) — only these two owner-approved cases
- the imam's choice among meanings is clear but not stated in his own short words → `CTX «وهذا اختيار الإمام»`;
- the excerpt is the imam carrying over and endorsing another author's words, named only far back in the passage →
  `CTX «ينقل كلام <name> ويقرّه»`.
Put the CTX in the reason field. If the text itself needs no change and only the CTX is needed, use verdict `كاف` with PROPOSAL `-` and the CTX in the reason. Any other missing referent that cannot be fixed verbatim → `لا يمكن`.
An existing `[سطر سياق]` already counts.

## Verdicts
- `كاف` — all 5 hold.
- `إكمال` — extend: give the WHOLE new excerpt (it replaces all current sentences), taken from the same full passage.
- `استبدال` — the chosen sentence is the wrong part; pick a different part of the same full passage.
- `لا يمكن` — the meaning cannot be completed inside the full passage, or only with a very long text (> ~700 chars
  even after splitting). These go to a human specialist.

## Hard constraints
- Proposed text = **exact, contiguous** text of the full passage shown in the item (whitespace may differ). No
  rewording, no summarising, no joining non-adjacent pieces inside one point, no added words, no «…».
- Build every proposed text with the helper, never retype Arabic (the Write tool can reorder diacritics):
  `python3 SC/tam/cut.py ID recN "first words" "last words"` prints the exact span.
- If the new excerpt would exceed ~400 chars, split it into **two points** (each a contiguous span, max 2 points;
  points may come from different records of the item).
- Keep it short: start at the sentence that carries the verse meaning; end right after the verdict/restriction.
  Do not pull in long proofs, hadith chains, or other verses' discussion.
- A point must be the imam's own words. Do not add a point that is someone else's voice (a narrator, a poet, a quoted scholar, a hadith text) — if the imam's meaning cannot stand without it, use `لا يمكن`. A short verse quote inside the imam's sentence is fine.
- An existing `[سطر سياق]` stays; don't count it as missing context.
- If you notice the excerpt is not the imam's voice or not about this verse, say so in the reason (prefix `OTHER:`),
  verdict per the best available fix (often `استبدال` or `لا يمكن`).

## Output — one line per item, in packet order
`ID | VERDICT | PROPOSAL | reason (one short line, English or Arabic)`
- PROPOSAL is `-` for `كاف` / `لا يمكن`; otherwise `recN «exact text»` or `recN «text1» ++ recM «text2»`.
- Example: `t2:7:IQ | إكمال | rec3961 «ومن هذا إخباره … عنه» | adds the restriction «…» that follows (cond. 3)`
  (in real output the text is complete, no «…»).

Validate before finishing: `python3 SC/tam/chk.py SC/tam/out/<NAME>.txt SC/tam/pk/<NAME>.txt` must say `bad 0`.
Finish with a short report: counts per verdict, recurring patterns, any item you were unsure about.
Do not edit any other file (your own helper scripts may go in SC/tam/ named h_<NAME>_*.py).
