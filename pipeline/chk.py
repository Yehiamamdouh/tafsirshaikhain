import asyncio,subprocess,time
from playwright.async_api import async_playwright
async def main():
    srv=subprocess.Popen(['python3','-m','http.server','8765','-d','/home/claude/tafsirshaikhain/public'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1)
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':390,'height':844})
        errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)))
        await pg.goto('http://localhost:8765/index.html#s2a247'); await pg.wait_for_timeout(2500)
        c=pg.locator('.pt .cite').first; await c.click(); await pg.wait_for_timeout(500)
        n=await pg.locator('.ctxbtn').count(); print('ctxbtn',n)
        if n: await pg.locator('.ctxbtn').first.click(); await pg.wait_for_timeout(1500); print('ctx spans',await pg.locator('.full .ctx').count())
        sw=await pg.evaluate('document.documentElement.scrollWidth'); print('scrollWidth',sw,'errs',errs[:2])
        await pg.screenshot(path='/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad/m.png')
        await pg.goto('http://localhost:8765/about.html'); sw=await pg.evaluate('document.documentElement.scrollWidth'); print('about sw',sw)
        await b.close()
    srv.kill()
asyncio.run(main())
