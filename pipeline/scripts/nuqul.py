"""List candidate quotations of earlier authorities in passages tied to given verses.

usage: nuqul.py SITEFILE AUTHOR VERSES [maxper]
"""
import json, sys, re
S = '/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
f, a, vs = sys.argv[1], sys.argv[2], [int(x) for x in sys.argv[3].split(',')]
maxper = int(sys.argv[4]) if len(sys.argv) > 4 else 12
d = json.load(open(S + '/site/' + f, encoding='utf-8'))
recs = list(d['recs'])
B = d['books']
NAMES = ['ابن عباس', 'ابن مسعود', 'عبد الله بن مسعود', 'أبي بن كعب', 'علي', 'عمر', 'عائشة', 'أبو هريرة', 'أبي هريرة', 'ابن عمر',
 'مجاهد', 'قتادة', 'الحسن', 'عكرمة', 'سعيد بن جبير', 'السدي', 'الضحاك', 'أبو العالية', 'أبي العالية', 'الربيع', 'عطاء', 'ابن زيد', 'زيد بن أسلم',
 'سفيان', 'ابن عيينة', 'الثوري', 'أحمد', 'الشافعي', 'مالك', 'أبو حنيفة', 'ابن جرير', 'الطبري', 'البغوي', 'الواحدي', 'الثعلبي', 'ابن عطية',
 'الزمخشري', 'الرازي', 'السهيلي', 'الفراء', 'الزجاج', 'سيبويه', 'الأخفش', 'أبو عبيدة', 'ابن قتيبة', 'ابن الأنباري', 'الخليل', 'الكسائي',
 'شيخنا', 'شيخ الإسلام', 'ابن أبي حاتم', 'أبو عبيد', 'المفسرين', 'السلف', 'جماعة', 'طائفة', 'بعضهم', 'بعض الناس', 'بعض السلف',
 'سهل بن عبد الله', 'الجنيد', 'صاحب المنازل', 'الهروي', 'محمد بن كعب', 'الكلبي', 'مقاتل', 'ابن الأعرابي', 'الجوهري', 'ابن فارس']
PAT = re.compile(r'(?:قال|وقال|فقال|وعن|عن|قاله|قول|وقول|ذكر|وذكر|روى|وروى|حكى|وحكى|وقيل|قيل|يقول)\s+(?:ه?م?\s*)?(' + '|'.join(sorted(map(re.escape, NAMES), key=len, reverse=True)) + r')\b|(?:وقيل|قيل)\s*:')
for v in vs:
    print('=' * 10, a, 'آية', v, d['verses'][v - 1][:60] if 'verses' in d else '')
    xs = [r for r in recs if B[r['b']]['a'] == a and v in r['ay'] and not r.get('inc')]
    xs.sort(key=lambda r: (-(r['c'] == 1), len(r['ay']) > 3, r['id']))
    n = 0
    for r in xs:
        t = r['t']
        for m in PAT.finditer(t):
            after = t[m.end():m.end() + 60]
            if re.search(r'النبي|رسول الله|صلى الله عليه', after): continue
            if m.group(1) in ('علي', 'عمر', 'مالك', 'أحمد', 'الحسن', 'الربيع', 'عطاء', 'سفيان', 'الخليل') and not re.match(r'\s*(البصري|بن|-|رضي|رحمه)?[^.]{0,25}?(:|في قوله|في تفسير|يعني|معناه|هو )', after): continue
            if m.group(1) is None and not re.search(r'[:،]', t[m.end()-2:m.end()+3]): continue
            s = max(0, m.start() - 120); e = min(len(t), m.end() + 330)
            print('#%d %s %s/%s | ...%s...' % (r['id'], B[r['b']]['t'][:16], r['v'], r['p'], t[s:e].replace('\n', ' ')))
            n += 1
            if n >= maxper: break
        if n >= maxper: break
    print()
