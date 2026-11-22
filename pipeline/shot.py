from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':390,'height':844})
    for u,n in [('/ayah/2-255.html','a'),('/book/AclamMuwaqqicin.html','bk'),('/surah/2.html','su'),('/books.html','bks')]:
        pg.goto('http://localhost:8765'+u); pg.wait_for_timeout(800)
        print(n,pg.evaluate('document.documentElement.scrollWidth'),pg.title()); pg.screenshot(path=f'{n}.png')
    b.close()
