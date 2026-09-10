# -*- coding: utf-8 -*-
"""用 Playwright 開一個持久化瀏覽器視窗到 Search Console。
賢賢在這個視窗登入一次，之後同一個 profile 就一直有效。
"""
import asyncio, os, sys
from playwright.async_api import async_playwright

PROFILE = os.path.expanduser('~/.config/gsc-playwright')
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '_預覽')
os.makedirs(OUT, exist_ok=True)
os.makedirs(PROFILE, exist_ok=True)

URL = sys.argv[1] if len(sys.argv) > 1 else 'https://search.google.com/search-console'


async def main():
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            PROFILE,
            headless=False,
            channel='msedge',
            viewport={'width': 1280, 'height': 900},
            args=['--window-position=80,40'],
        )
        pg = ctx.pages[0] if ctx.pages else await ctx.new_page()
        await pg.goto(URL, wait_until='domcontentloaded')
        await pg.wait_for_timeout(5000)
        print('網址:', pg.url[:120])
        print('標題:', await pg.title())
        await pg.screenshot(path=os.path.join(OUT, 'gsc_open.png'))
        body = (await pg.inner_text('body'))[:600]
        print('--- 畫面文字 ---')
        print(body)
        print('\n>>> 視窗保持開啟 15 分鐘，請在裡面登入 Google。')
        await pg.wait_for_timeout(900000)
        await ctx.close()

asyncio.run(main())
