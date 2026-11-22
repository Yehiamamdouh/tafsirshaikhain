# Restriction check — Mustadrak al-Fatawa excerpts on tafsirshaikhain.com

The site shows verbatim excerpts («مختصر») of Ibn Taymiyya under Quran verses. Your packet holds every excerpt taken from
«المستدرك على مجموع الفتاوى» — a compilation of short rulings. A second reviewer found one excerpt (70:24-25) that ended
right before a restriction that changes the ruling («وإن سأل مطلقا بغير معين لم يجب أيضا»). Check every item for that
and for the usual conditions.

Paths: SC = /tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad
Packet `SC/qc/pk/QM1.txt` → write `SC/qc/out/QM1.txt`. More context: `python3 SC/bp/pp.py MustadrakCalaMajmucFatawa i [before] [after]`.
Exact cutting: `python3 SC/bp/cut.py MustadrakCalaMajmucFatawa i "first words" "last words"` — copy its output by script,
never retype Arabic.

Per item decide:
- `OK` — the excerpt is Ibn Taymiyya's own statement (not the compiler's or another scholar's: watch for «قال أبو العباس»,
  «قاله ابن عقيل», «ذكره…», «نقله…»), about this verse, and NOT followed (in the same ruling) by a restriction, exception,
  condition or reversal that changes what the excerpt says (لكن، إلا، إن/إذا…، بشرط، ما لم، وإن…لم يجب، والصحيح خلافه…).
- `EXT «exact longer text»` — the fix is to extend the excerpt to include the restriction (contiguous, starting where the
  current excerpt starts, ≤ 700 chars).
- `TRIM «exact shorter text»` — the excerpt carries something it shouldn't (another voice, unrelated ruling).
- `DROP` — not his words, or not about this verse, or not fixable.
Output one line per item, packet order: `M## | OK|EXT|TRIM|DROP | «text» or - | reason`. Finish with counts.
Helper scripts only as `SC/qc/h_QM1_*.py`. Edit nothing else.
