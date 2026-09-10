import asyncio, json, sys, re
from playwright.async_api import async_playwright
sys.stdout.reconfigure(encoding='utf-8')
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        pg = await b.new_page(viewport={'width':1280,'height':900})
        url = "https://www.tpetkd.org.tw/di-fang-xiao-xi/【競賽組】賽事資訊📣-114年第32屆全國少年跆拳道錦標賽"
        await pg.goto(url, wait_until='domcontentloaded', timeout=60000)
        await pg.wait_for_timeout(6000)
        links = await pg.eval_on_selector_all('a[href]', 'els=>els.map(e=>[e.href,e.innerText.trim().slice(0,80)])')
        pdfs = [l for l in links if '.pdf' in l[0].lower() or 'filesusr' in l[0] or 'ugd' in l[0]]
        print("POST PDFS:", json.dumps(pdfs, ensure_ascii=False, indent=1))
        # listing
        await pg.goto("https://www.tpetkd.org.tw/di-fang-xiao-xi", wait_until='domcontentloaded', timeout=60000)
        await pg.wait_for_timeout(6000)
        print("TITLE:", await pg.title())
        links = await pg.eval_on_selector_all('a[href]', 'els=>els.map(e=>[e.href,e.innerText.trim().slice(0,80)])')
        posts = [l for l in links if '/di-fang-xiao-xi/' in l[0]]
        print("N posts on page:", len(set(x[0] for x in posts)))
        for l in posts[:60]: print(l)
        # pagination / category links
        cats = [l for l in links if 'categories' in l[0] or 'page' in l[0].lower() or 'blog' in l[0]]
        print("CATS:", json.dumps(cats[:40], ensure_ascii=False))
        await b.close()
asyncio.run(main())
