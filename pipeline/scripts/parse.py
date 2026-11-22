"""Parse OpenITI mARkdown files into paragraphs with printed volume/page refs,
and detect references to the verses of al-Fatiha."""
import re, json, sys, glob, os

PAGE = re.compile(r'PageV(\d+)P(\d+)')
MS = re.compile(r'\s*ms\d+\s*')

def norm(s):
    s = re.sub(r'[ً-ْٰـ]', '', s)          # harakat, tatweel
    s = re.sub(r'[إأآٱ]', 'ا', s)
    s = s.replace('ى', 'ي').replace('ة', 'ه').replace('ؤ', 'و').replace('ئ', 'ي')
    return s

def meta(path):
    m = {}
    with open(path, encoding='utf-8') as f:
        for line in f:
            if line.startswith('#META#Header#End#'):
                break
            mm = re.match(r'#META#\s*(\S+)\s*::\s*(.*)', line)
            if mm:
                m[mm.group(1)] = mm.group(2).strip()
    return m

def paragraphs(path):
    """Yield dicts: text, vol, p_start, p_end, header. Page tags mark the END of a page."""
    with open(path, encoding='utf-8') as f:
        lines = f.read().split('\n')
    i = 0
    while i < len(lines) and not lines[i].startswith('#META#Header#End#'):
        i += 1
    lines = lines[i + 1:]

    # Pass 1: build a token stream of (kind, value)
    paras = []          # list of [header, list_of_segments]
    header = ''
    cur = None
    for line in lines:
        if line.startswith('### '):
            header = re.sub(r'^###\s*\|+\s*', '', line).strip()
            header = MS.sub(' ', header).strip()
            cur = None
            continue
        if line.startswith('# '):
            body = line[2:]
            if PAGE.fullmatch(body.strip()):
                paras.append(('PAGE', body.strip()))
                cur = None
                continue
            cur = [header, body]
            paras.append(('P', cur))
        elif line.startswith('~~') and cur is not None:
            cur[1] += ' ' + line[2:]
        elif line.strip() and cur is not None:
            cur[1] += ' ' + line.strip()

    # Pass 2: resolve pages. Each paragraph's text may contain inline page tags.
    # A paragraph's starting page = page of the next tag after its start.
    out = []
    pending = []        # paragraphs waiting for their page tag
    for kind, val in paras:
        if kind == 'PAGE':
            m = PAGE.fullmatch(val)
            v, p = int(m.group(1)), int(m.group(2))
            for para in pending:
                para.setdefault('vol', v); para.setdefault('p_start', p)
                para['p_end'] = p
            pending = []
            continue
        hdr, text = val
        para = {'header': hdr}
        parts = PAGE.split(text)
        # parts: text0, v, p, text1, v, p, text2 ...
        clean = parts[0]
        for k in range(1, len(parts), 3):
            v, p = int(parts[k]), int(parts[k + 1])
            # text before this tag ends on page p
            for q in pending:
                q.setdefault('vol', v); q.setdefault('p_start', p); q['p_end'] = p
            pending = []
            para.setdefault('vol', v); para.setdefault('p_start', p); para['p_end'] = p
            clean += ' ' + parts[k + 2]
        clean = re.sub(r'\s?\(¬?\d{1,3}\)', '', MS.sub(' ', clean).replace('@QB@', '{').replace('@QE@', '}').replace(' # ', ' '))
        clean = re.sub(r'\s+', ' ', clean).strip()
        para['text'] = clean
        if 'p_start' in para and parts[-1].strip():
            # paragraph continues onto the following page
            para['_open'] = True
            pending.append(para)
        elif 'p_start' not in para:
            pending.append(para)
        out.append(para)
    for para in out:
        para.pop('_open', None)
        para.setdefault('vol', 0); para.setdefault('p_start', 0); para.setdefault('p_end', para['p_start'])
    return [p for p in out if p['text']]

# ---- Verse detection -------------------------------------------------------
# Normalised phrases.  'strong' phrases count even without Quranic braces.
VERSES = {
    1: {'braced': ['بسم الله الرحمن الرحيم'], 'strong': []},
    2: {'braced': ['الحمد لله رب العالمين'], 'strong': []},
    3: {'braced': ['الرحمن الرحيم'], 'strong': []},
    4: {'braced': ['مالك يوم الدين', 'ملك يوم الدين'], 'strong': ['مالك يوم الدين', 'ملك يوم الدين']},
    5: {'braced': ['اياك نعبد', 'اياك نستعين'], 'strong': ['اياك نعبد', 'اياك نستعين']},
    6: {'braced': ['اهدنا الصراط المستقيم'], 'strong': ['اهدنا الصراط المستقيم', 'اهدنا الصراط']},
    7: {'braced': ['صراط الذين انعمت عليهم', 'غير المغضوب عليهم', 'ولا الضالين', 'انعمت عليهم'],
        'strong': ['صراط الذين انعمت عليهم', 'غير المغضوب عليهم', 'المغضوب عليهم ولا الضالين']},
}
SURAH = ['سوره الفاتحه', 'فاتحه الكتاب', 'ام القران', 'السبع المثاني', 'الفاتحه']
SURAH_RE = re.compile(r'(?<![\w])(?:' + '|'.join(SURAH) + r')(?![\w])')
def has_surah(n):
    return bool(SURAH_RE.search(n))
CITE = re.compile(r'\[\s*الفاتحه\s*:\s*([٠-٩\d]+)\s*(?:[-–]\s*([٠-٩\d]+))?\s*\]')
AR_DIG = str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789')
BRACE = re.compile(r'\{([^{}]*)\}')

def detect(text):
    n = norm(text)
    verses, how = set(), set()
    for m in CITE.finditer(n):
        a = int(m.group(1).translate(AR_DIG)); b = int((m.group(2) or m.group(1)).translate(AR_DIG))
        for v in range(a, b + 1):
            if 1 <= v <= 7:
                verses.add(v); how.add('cite')
    braces = ' | '.join(BRACE.findall(n))
    for v, d in VERSES.items():
        if any(ph in braces for ph in d['braced']):
            # basmala / hamdala / rahman-rahim in braces only count when the paragraph is about the Fatiha
            if v in (1, 2, 3) and not (CITE.search(n) or has_surah(n)):
                continue
            verses.add(v); how.add('brace')
        elif any(ph in n for ph in d['strong']):
            verses.add(v); how.add('phrase')
    surah = has_surah(n)
    return sorted(verses), surah, sorted(how)

if __name__ == '__main__':
    out = []
    for path in sys.argv[1:]:
        m = meta(path)
        paras = paragraphs(path)
        hits = 0
        for idx, p in enumerate(paras):
            v, s, how = detect(p['text'])
            p['idx'] = idx
            p['verses'] = v; p['surah'] = s; p['how'] = how
            if v or s:
                hits += 1
        print(f"{hits:5d} / {len(paras):6d}  {m.get('020.BookTITLE','?')[:60]}", file=sys.stderr)
