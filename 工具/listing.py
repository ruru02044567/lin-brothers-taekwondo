import asyncio, json, sys, re
from playwright.async_api import async_playwright
sys.stdout.reconfigure(encoding='utf-8')
PAGES = ["https://www.tpetkd.org.tw/地方訊息","https://www.tpetkd.org.tw/副本-國內消息-113九月份","https://www.tpetkd.org.tw/blog","https://www.tpetkd.org.tw/di-fang-xiao-xi/categories/競賽組"]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        pg = await b.new_page(viewport={'width':1280,'height':900})
        for u in PAGES:
            try:
                await pg.goto(u, wait_until='domcontentloaded', timeout=60000)
            except Exception as e: print("ERR", u, e); continue
            await pg.wait_for_timeout(6000)
            for _ in range(8):
                await pg.mouse.wheel(0, 4000); await pg.wait_for_timeout(1200)
            print("=== ", u, "| title:", await pg.title())
            links = await pg.eval_on_selector_all('a[href]', 'els=>els.map(e=>[e.href,e.innerText.trim().slice(0,70)])')
            posts = sorted(set((l[0],l[1]) for l in links if '/di-fang-xiao-xi/' in l[0] or '/post/' in l[0]))
            print("posts:", len(posts))
            for l in posts: print(l[1], '|', l[0][:120])
            other = sorted(set(l[0] for l in links if 'tpetkd' in l[0] and 'di-fang' not in l[0]))
            print("other:", [o[24:80] for o in other][:40])
        await b.close()
asyncio.run(main())
