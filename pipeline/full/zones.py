"""zones.py : list existing site summ items whose record lies in book zones that forks flagged as someone else's text."""
import json, os, re
SC = '/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad'
ws = lambda s: re.sub(r'\s+', ' ', s).strip()
Z = [  # work, vol, page_from, page_to, note
    ('CuddatSabirin', 1, 1, 9999, 'debate قالت الفقراء/الأغنياء?'),
    ('MajmucFatawa', 5, 402, 405, 'Ibn Qutayba'), ('MinhajSunna', 8, 466, 470, 'Ibn Hazm'),
    ('MajmucFatawa', 7, 318, 322, 'al-Marwazi'), ('TariqHijratayn', 1, 190, 197, 'قالوا'),
    ('AclamMuwaqqicin', 2, 205, 208, 'al-Shafii Risala'), ('MustadrakCalaMajmucFatawa', 3, 60, 64, 'IQ text?'),
    ('MustadrakCalaMajmucFatawa', 1, 188, 190, 'IQ text?'), ('MajmucFatawa', 7, 332, 334, 'Abu Talib al-Makki'),
    ('SawaciqMursala', 4, 1540, 1544, 'Shahrastani'), ('BayanTalbisJahmiyya', 1, 238, 240, 'Ibn Rushd'),
    ('BayanTalbisJahmiyya', 1, 494, 497, 'Ibn Rushd'), ('DarTacarud', 9, 325, 327, 'Ibn Rushd?'),
    ('BayanTalbisJahmiyya', 1, 108, 110, 'Ashari Ibana'), ('MajmucFatawa', 2, 198, 200, 'Fusus'),
    ('MajmucFatawa', 2, 250, 253, 'Fusus'), ('MajmucFatawa', 13, 193, 195, 'Fusus'), ('DarTacarud', 6, 165, 167, 'Fusus'),
    ('RasailWaFatawa', 1, 165, 167, 'Fusus'), ('BughyatMurtad', 1, 378, 381, 'Fusus/Ghazali'),
    ('Hamawiyya', 1, 459, 462, 'Sufi creed'), ('MajmucFatawa', 5, 81, 83, 'Sufi creed'),
    ('ZadMacad', 1, 468, 470, 'al-Tabari'), ('ZadMacad', 3, 106, 108, 'قالوا'), ('ZadMacad', 5, 585, 587, 'quote?'),
    ('BadaicFawaid', 4, 40, 42, 'Hanbali other'), ('BadaicFawaid', 4, 168, 171, 'Suhayli'),
    ('BadaicFawaid', 1, 158, 160, 'Suhayli?'), ('BadaicFawaid', 1, 194, 196, 'Suhayli?'),
    ('MinhajSunna', 7, 4, 6, 'Rafidi'), ('Imama', 1, 9, 11, 'Rafidi'), ('MinhajSunna', 5, 286, 289, 'قالوا'),
    ('RawdatMuhibbin', 1, 111, 113, 'opponent'), ('TuhfatMawdud', 1, 168, 170, 'قالوا'),
    ('BayanTalbisJahmiyya', 1, 267, 270, 'opponents'), ('MiftahDarSacada', 1, 238, 240, 'Jahiz?'),
    ('MajmucFatawa', 6, 372, 376, 'objector (cf 4047)'), ('MinhajSunna', 4, 565, 567, 'Rafidi story'),
]
n = 0
for su in range(1, 115):
    d = json.load(open(f'{SC}/site/s{su}.json')); p = f'{SC}/site/s{su}i.json'
    inc = json.load(open(p)) if os.path.exists(p) else []
    R = {r['id']: r for r in d['recs'] + inc}; B = d['books']
    for kind in ('summ',):
        for a, vs in d.get(kind, {}).items():
            for v, xs in vs.items():
                for x in xs:
                    r = R[x['r']]; w = B[r['b']]['w']
                    for zw, zv, p0, p1, note in Z:
                        if w == zw and r['v'] == zv and p0 <= r['p'] <= p1:
                            n += 1
                            print(f'{su}:{v} {a} rec{r["id"]} {w} {r["v"]}/{r["p"]} [{note}] «{ws(x["t"])[:110]}»')
print('total', n)
