"""Display-only clean-up of edition artifacts in the imams' texts (the data in public/s*.json is never changed).
1. a verse reference repeated right after itself ([البقرة: 125] [البقرة 125]) -> keep the first
2. a footnote number glued to the end of an Arabic word, outside [...] (الشام3،) -> dropped
3. editor additions in [...] with no digits ([من]) -> kept, shown faint with a tooltip
4. a 1-2 digit footnote number right after ] or } (with or without a space) -> dropped
5. manuscript page marks like /54ب/ -> dropped
Numbers in parentheses inside verses, e.g. (49), are verse numbers and are left alone.
Verse references like [البقرة: 5] or [يس2 , 1] are left as they are. Works on escaped HTML or plain text.
Mirrored in src/patch.js (edfix) for the interactive app."""
import re
DUP=re.compile(r'(\[([^\]\[\d:<>]+?):?\s*(\d+)\])\s*\[\s*\2:?\s*\3\]')
BR=re.compile(r'(\[[^\[\]]*\])')
FN=re.compile(r'([ء-ي])(\d{1,2})(?=[\s،,.؛:!؟?»"\'&<]|$)')
AFT=re.compile(r'([\]}])((?:</[a-z]+>)*)\s?\d{1,2}(?![\d/])')
MS=re.compile(r'\s?/\s*\d{1,4}\s*[أاب]\s*/')
ED=re.compile(r'\[([^\[\]\d<>{}]+)\]')
def fx(t, span=True):
    t=DUP.sub(r'\1',t)
    t=MS.sub('',t)
    t=AFT.sub(r'\1\2',t)
    t=''.join(p if i%2 else FN.sub(r'\1',p) for i,p in enumerate(BR.split(t)))
    if span: t=ED.sub(lambda m:f'<span class="tz" title="زيادة من المحقق">[{m.group(1)}]</span>',t)
    return t
