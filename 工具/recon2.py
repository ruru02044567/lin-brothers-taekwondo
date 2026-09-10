import asyncio, json, sys, re
from playwright.async_api import async_playwright
sys.stdout.reconfigure(encoding='utf-8')
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        pg = await b.new_page(viewport={'width':1280,'height':900})
        url = "https://www.tpetkd.org.tw/di-fang-xiao-xi/【競賽組】賽事資訊📣-114年第32屆全國少年跆拳道錦標賽"
        await pg.goto(url, wait_until='domcontentloaded', timeout=60000)
        await pg.wait_for_timeout(8000)
        print("TITLE:", await pg.title())
        html = await pg.content()
        open('post_dump.html','w',encoding='utf-8').write(html)
        for m in sorted(set(re.findall(r'https?://[^"\'\s<>]+?(?:\.pdf|filesusr[^"\'\s<>]*)', html))): print("PDFISH:", m[:200])
        links = await pg.eval_on_selector_all('a[href]', 'els=>els.map(e=>[e.href,e.innerText.trim().slice(0,60)])')
        print("N links", len(links))
        for l in links: print(l)
        print("IFRAMES:", await pg.eval_on_selector_all('iframe', 'els=>els.map(e=>e.src)'))
        txt = await pg.inner_text('body')
        print("BODY TEXT (head):", txt[:1500])
        # home nav
        await pg.goto("https://www.tpetkd.org.tw/", wait_until='domcontentloaded', timeout=60000)
        await pg.wait_for_timeout(6000)
        links = await pg.eval_on_selector_all('a[href]', 'els=>els.map(e=>[e.href,e.innerText.trim().slice(0,60)])')
        print("HOME LINKS:")
        for l in sorted(set(map(tuple,links))): print(l)
        await b.close()
asyncio.run(main())
