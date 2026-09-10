# -*- coding: utf-8 -*-
"""在既有的 gsc-playwright profile 上操作 Search Console。
只讀畫面、截圖、回報，不做破壞性動作。
"""
import asyncio, os, sys
from playwright.async_api import async_playwright

PROFILE = os.path.expanduser('~/.config/gsc-playwright')
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '_預覽')
SITE = 'https://ruru02044567.github.io/lin-brothers-taekwondo/'
os.makedirs(OUT, exist_ok=True)

STEP = sys.argv[1] if len(sys.argv) > 1 else 'status'


async def shot(pg, name):
    await pg.screenshot(path=os.path.join(OUT, name + '.png'))


async def main():
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            PROFILE, headless=False, channel='msedge',
            viewport={'width': 1280, 'height': 900},
            args=['--window-position=80,40'])
        pg = ctx.pages[0] if ctx.pages else await ctx.new_page()

        if STEP == 'status':
            await pg.goto('https://search.google.com/search-console',
                          wait_until='domcontentloaded')
            await pg.wait_for_timeout(5000)
            print('網址:', pg.url[:130])
            print('標題:', await pg.title())
            await shot(pg, 'gsc_status')
            body = (await pg.inner_text('body'))[:700]
            print('--- 畫面文字 ---')
            print(body)
            # 判斷是否已登入
            logged = 'accounts.google.com' not in pg.url
            print('\n看起來已登入:', logged)

        await ctx.close()

asyncio.run(main())
