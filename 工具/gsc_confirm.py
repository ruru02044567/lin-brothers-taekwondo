# -*- coding: utf-8 -*-
"""唯讀確認：驗證狀態 + sitemap 是否真的收到。"""
import asyncio, os
from playwright.async_api import async_playwright

PROFILE = os.path.expanduser('~/.config/gsc-playwright')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, '_預覽', 'confirm')
os.makedirs(OUT, exist_ok=True)
SITE = 'https://ruru02044567.github.io/lin-brothers-taekwondo/'
ENC = SITE.replace(':', '%3A').replace('/', '%2F')


async def main():
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            PROFILE, headless=True, channel='msedge',
            viewport={'width': 1360, 'height': 980})
        pg = ctx.pages[0] if ctx.pages else await ctx.new_page()
        pg.set_default_timeout(40000)

        await pg.goto('https://search.google.com/search-console/sitemaps?resource_id=' + ENC,
                      wait_until='domcontentloaded')
        await pg.wait_for_timeout(12000)
        await pg.screenshot(path=os.path.join(OUT, 'sitemaps.png'), full_page=True)
        body = await pg.inner_text('body')
        print('URL:', pg.url[:110], flush=True)
        print('--- 有無權限問題:', '沒有存取這項資源的權限' in body, flush=True)
        print('--- 全文 ---', flush=True)
        print(body[:2200], flush=True)
        await ctx.close()

asyncio.run(main())
