# -*- coding: utf-8 -*-
"""連上已開啟的 Edge（CDP 9222），確認 Google 登入狀態並打開 Search Console。"""
import asyncio, os
from playwright.async_api import async_playwright

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '_預覽')
os.makedirs(OUT, exist_ok=True)


async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        ctx = b.contexts[0]
        print('現有分頁數:', len(ctx.pages))
        for i, pg in enumerate(ctx.pages):
            try:
                print('  [%d] %s' % (i, (await pg.title())[:50]), '|', pg.url[:70])
            except Exception:
                pass

        pg = await ctx.new_page()
        await pg.goto('https://search.google.com/search-console',
                      wait_until='domcontentloaded')
        await pg.wait_for_timeout(4000)
        print('\nSearch Console 網址:', pg.url[:110])
        print('標題:', await pg.title())
        await pg.screenshot(path=os.path.join(OUT, 'gsc_01.png'))
        txt = (await pg.inner_text('body'))[:900]
        print('\n--- 頁面文字 ---')
        print(txt)
        await b.close()

asyncio.run(main())
