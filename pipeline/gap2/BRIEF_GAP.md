# New summaries for verses that have none yet (tafsirshaikhain.com)
The site shows, per Quran verse, short VERBATIM excerpts of Ibn Taymiyya (IT) / Ibn al-Qayyim (IQ) explaining that verse.
These verses have NO excerpt yet, but the imams' books mention them. Each block shows the verse and up to 3 passages
(windows around where the verse is cited; the full passage text is in site/s{SU}.json 'recs' or site/s{SU}i.json, match
'id'). Your job: decide whether a passage contains a REAL explanation of THIS verse by the imam himself, and if so pick the
excerpt. Most verses here are only cited in passing (a list of proof-verses, an example, a quotation) → NONE is the
normal, correct answer; do not force an excerpt.
An excerpt is accepted only if ALL hold:
1. verbatim — an exact substring of the record text (copy it exactly; never edit, never join non-adjacent text);
2. the imam's own voice — not a quotation of someone else, an objector («فإن قيل», «قالوا»), a reported view («وقيل»), a
   party's argument in a debate, a hadith/athar text, a compiler's wording; (Ibn al-Qayyim speaking through the side he
   holds in a debate he composed is OK — add `CTX «short Arabic frame»` in the reason);
3. explains THIS verse (meaning, ruling, lesson drawn from it) — not just lists it;
4. not immediately qualified/rejected by the imam right after;
5. self-standing: a complete sentence that names or quotes the verse words it explains (start at the verse citation
   when needed), roughly 15–420 characters.
You may read the whole record and the neighbouring book paragraphs (out/cache/{WORK}.pkl, key 'paras') to judge; fast
search: audit/h_S07_nx.py. Helpers only as gap2/h_<NAME>_*.py. Edit nothing but your output file.
## Output — gap2/out/<NAME>.txt, in packet order, at least one line per verse, append as you go (if the file exists,
continue after the last verse in it):
- `SU:V | IT|IQ | recID | «verbatim excerpt» | reason`   (at most 2 excerpts per imam per verse)
- `SU:V | NONE | reason`
Final reply (short): verses with new excerpts / NONE counts, and anything systematic.
