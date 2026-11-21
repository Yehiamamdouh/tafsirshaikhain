"""Tell Bing (and the other IndexNow engines: Yandex, Seznam, Naver…) which pages changed.
Run after a build has been pushed AND deployed (the key file must be live):
    python3 src/indexnow.py            # URLs whose sitemap <lastmod> is today
    python3 src/indexnow.py 2026-11-20 # URLs changed on/after that date
    python3 src/indexnow.py all        # every URL in the indexed sitemaps
Only the sitemaps listed in public/sitemap.xml are used, so noindexed language pages are never sent."""
import glob, json, os, re, sys, urllib.request, datetime, subprocess
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); P = R + '/public'
HOST = 'tafsirshaikhain.com'
KEY = [os.path.basename(f)[:-4] for f in glob.glob(R + '/src/*.txt') if re.fullmatch(r'[0-9a-f]{32}\.txt', os.path.basename(f))][0]
arg = sys.argv[1] if len(sys.argv) > 1 else datetime.date.today().isoformat()
urls = []
for sm in re.findall(r'<loc>https://' + HOST + r'/([^<]+)</loc>', open(P + '/sitemap.xml').read()):
    for loc, lm in re.findall(r'<url><loc>([^<]+)</loc>(?:<lastmod>([^<]+)</lastmod>)?', open(P + '/' + sm).read()):
        if arg == 'all' or (lm or '') >= arg: urls.append(loc)
print(len(urls), 'URLs', '(all)' if arg == 'all' else 'changed since ' + arg)
for i in range(0, len(urls), 10000):
    body = json.dumps({'host': HOST, 'key': KEY, 'keyLocation': f'https://{HOST}/{KEY}.txt', 'urlList': urls[i:i + 10000]}).encode()
    # curl goes through the session proxy reliably; urllib is a fallback
    try:
        out = subprocess.run(['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', '-H', 'Content-Type: application/json; charset=utf-8',
                              '--data-binary', '@-', 'https://api.indexnow.org/indexnow'], input=body, capture_output=True, timeout=120).stdout.decode()
    except FileNotFoundError:
        req = urllib.request.Request('https://api.indexnow.org/indexnow', body, {'Content-Type': 'application/json; charset=utf-8'})
        out = str(urllib.request.urlopen(req, timeout=120).status)
    print('batch', i // 10000 + 1, 'HTTP', out, '(200/202 = accepted)')
