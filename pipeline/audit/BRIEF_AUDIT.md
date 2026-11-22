# Independent audit — brief for each reviewer

## The project
tafsirshaikhain.com shows, per Quran verse, short excerpts of the **verbatim** words of Ibn Taymiyya (IT) and Ibn
al-Qayyim (IQ) (= "summ" items, shown as the imam's own words), plus "nuq" items: words of OTHER people that the imam
quotes, each with the quoted person (WHO) and the imam's stance (STANCE). Every excerpt is already machine-verified to
be an exact substring of the book, so you never need to check spelling/verbatim. Your job is **judgement**: is each
item correctly attributed, correctly labelled, about the right verse, and not misleading? You are an independent
second reviewer: assume nothing was checked before. Be strict but fair.

Work dir: `/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad`
Your packet `audit/pk/<NAME>.txt` has one block per item (`### ID [flags] IMAM WORK vol/page recID verse SU:V`)
with the context you need. For more context read the book: `out/cache/{WORK}.pkl` (pickle; key `paras` = list of
{header,text,vol,p_start,p_end}); find the paragraph by searching a distinctive piece of the excerpt (whitespace-
normalized). Records: `site/s{SU}.json` → `recs` (+ `site/s{SU}i.json`), match `id`. Write helpers as
`audit/h_<NAME>_*.py`. Never edit anything except your output file.

## What to decide

### summ items (packets S*, R*) — "this is the imam's own explanation of this verse"
- **Speaker**: the words must be the imam's own voice. NOT his: a quotation of another scholar/book (even long,
  multi-paragraph, e.g. al-Shahrastani, Ibn Rushd, al-Ash'ari, al-Darimi, al-Muhasibi, Ibn Hazm, al-Suhayli in Bada'i'
  al-Fawa'id, al-Harawi's Manazil in Madarij, al-Shafi'i's Risala), an opponent/objector («قالوا», «فإن قيل», «قال
  الرافضي», the Christians' letter in al-Jawab al-Sahih), one party's argument in a debate the imam lays out (even the
  side he favours), a reported view («وقيل», «قال بعضهم»), Salaf reports/hadith/poetry, the questioner's question
  (before «فأجاب»), a compiler's wording (al-Ba'li's al-Ikhtiyarat, Ibn Qasim's Mustadrak notes), or IQ reproducing IT
  (or IT quoting IQ) without saying so. A quote that is short and clearly closed before the excerpt is fine.
  The flag OPENQ only means an opener was seen up to 20 paragraphs earlier — most are false alarms; judge the real flow
  (closing signs: «قلت», «انتهى», «والجواب», «فيقال», «هذا كلامه», «والمقصود», «والصواب», a new «فصل», the imam
  answering or judging).
- **Verse**: it comments on THIS verse (not just lists it, not really about a neighbouring verse).
- **Not misleading**: read the words right after the excerpt (AFTER). If the imam immediately qualifies, restricts or
  rejects what the excerpt says («لكن», «إلا أن», «وهذا ضعيف», «والصحيح خلافه»), the excerpt alone misrepresents him.
- **Format**: footnote digits glued to words, broken brackets.

### nuq items (packets N*) — "the imam quotes WHO, with STANCE"
- WHO correct (the person/group actually quoted; precise enough; not the imam himself)?
- STANCE correct given what the imam says around it: أقرّه (endorses/accepts) · استشهد به (cites as evidence/support)
  · حكاه (just reports, no judgement) · ردّه (rejects/refutes) · رجّح غيره (prefers another view). Also «أقرّه وشرحه»,
  «أقرّه وزاد عليه» exist.
- Is it really someone else's words? If the QUOTE is in fact the imam's own words → SUMM.
- REJOINDER (rt), when present, must be the imam's own reply to that quote.

## Output — one line per item, in packet order, to `audit/out/<NAME>.txt` (append as you go; the machine can
restart; if the file exists, continue after the last ID in it)
- `ID | KEEP`
- `ID | DROP | reason`                      (not the imam's words and not worth a nuq; or not about the verse; or misleading)
- `ID | NUQ | WHO | STANCE | reason`        (summ that is really a quotation → turn into a quote of WHO)
- `ID | MOVE | SU:V | reason`               (right text, wrong verse)
- `ID | TRIM | «exact substring» | reason`  (keep only this verbatim part of the excerpt — or of the record, e.g. to
                                             include the imam's qualification — must be copied exactly)
- nuq only: `ID | WHO | new who | reason` · `ID | ST | new stance | reason` · `ID | SUMM | reason` · `ID | DROP | reason`
When unsure about the speaker → DROP (for summ) — a misattribution is worse than a missing line; for other doubts
KEEP and add `?` in a reason: `ID | KEEP | ? reason`.

Final reply (short): counts per decision, and any systematic problem (a book section that is someone else's text,
a wrong pattern) with WORK vol/page.

## Sweep packets (W*, X*) — section-level re-check
Each block also shows `SECTION FINDING` (what earlier reviewers found about that book section: someone else's text,
a party's argument in a debate, IQ copying IT unnamed, etc.) and `EARLIER DECISION` lines. Your decision is FINAL for
the item and replaces the earlier ones, so write the full decision even if it agrees (e.g. repeat the earlier TRIM).
- First verify the section finding yourself in the book (search the pkl; for IQ-copies-IT, compare with the IT book in
  out/cache when present — near-verbatim = IT's text). Do not take it on faith; if it is wrong, say so in your reason.
- Then apply it consistently: inside such a section only the imam's own replies/judgements («قلت», «والجواب»,
  «والصواب», «والتحقيق», a new «فصل», his verdict) are his voice. Party/quoted text → NUQ (WHO = the party or the
  person; stance = how the imam treats it) or DROP if not worth a quote. IQ reproducing IT nearly verbatim without
  naming him → `NUQ | شيخه ابن تيمية (<IT work if known>) | أقرّه | reason`. IQ's own rewording → KEEP.
- nuq items in these ranges: re-check WHO/STANCE in light of the finding.

## Owner rule DEC2 — debates Ibn al-Qayyim composed himself (applies wherever a SECTION FINDING says "DEC2")
Where IQ lays out a debate/argument he composed and speaks through HIS OWN favoured side («قالوا» of the side he
holds, «قال السني», «قال صاحب القرآن», «قال الموقعون», the amthal section of A'lam 1/101-146, …) the words count as
IQ's own, but the reader must be told the frame. Decision for such a summ item:
- `ID | CTX | «short Arabic context line» | reason`  = KEEP as IQ's words + show the context line under it. Write the
  line in neutral Arabic, ≤ 12 words, naming the frame and the book, e.g. «من سياق احتجاج مثبتي القياس في إعلام
  الموقعين» · «على لسان السني في مناظرته مع القدري (شفاء العليل)» · «على لسان صاحب القرآن في مناظرة السماع».
  (CTX may be combined with MOVE/TRIM on separate lines for the same ID.)
- The side IQ rejects or does not adopt, or a named person quoted inside the frame → NUQ (WHO, STANCE) as usual.
- Not about the verse / misleading → MOVE / TRIM / DROP as usual. A nuq item that is really IQ's favoured side → SUMM.
