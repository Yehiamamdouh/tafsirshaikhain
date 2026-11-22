# Verse-placement check — is each item shown under the right verse?

tafsirshaikhain.com shows, under each Quran verse, verbatim excerpts («مختصر», kind `summ`) and «نقل» items (kind `nuq`)
from Ibn Taymiyya (IT) / Ibn al-Qayyim (IQ). Items were tied to verses through the verse references printed in the book
editions, and some editions print WRONG references (we have seen e.g. a quote of 4:92 labelled النساء 91, of 36:29
labelled يس 53, of 28:63 labelled القصص 13). A script found the items in your packet whose stored passage does NOT seem
to quote the words of the verse they are shown under. Many will still be correct (the verse is the section heading, the
passage paraphrases it, the verse was quoted just before the stored window, it is the opening of a surah, etc.). Your job:
decide for each item whether it is placed under the right verse.

Paths: SC = /tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad
Packet `SC/qc/pk/<NAME>.txt` → write `SC/qc/out/<NAME>.txt`.
Item: `### V### — SU:V — imam — summ|nuq — w=WORK (vol/page) header: …`, the VERSE it is shown under, the SITE TEXT, and
the FULL STORED PASSAGE (may be cut at 3500 chars).
More context: `python3 SC/spec/nb.py WORK "key words from the passage" [before] [after]` prints the book paragraphs
around the first paragraph containing the key words — use it to see which verse the imam is actually discussing
(what he quotes just before, the section header). The Quran text of any verse: `SC/site/s<SU>.json` → `verses[V-1]`.

## Output — one line per item, packet order
`V### | OK | short reason` — the item does explain/concern this verse (say how: heading, paraphrase, quoted earlier…).
`V### | MOVE | SU:V | reason` — it clearly concerns ANOTHER verse; give that verse (check its Quran text matches).
`V### | DROP | reason` — it is not about this verse and there is no single right verse (general remark, list item…).
`V### | HUMAN | Arabic question for a scholar` — genuinely cannot tell.
Be decisive; OK needs a concrete reason, not "probably". Finish with counts and anything systematic (e.g. an edition
whose labels are shifted). Helper scripts only as `SC/qc/h_<NAME>_*.py`. Edit nothing else.
