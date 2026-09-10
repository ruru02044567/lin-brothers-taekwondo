# -*- coding: utf-8 -*-
"""唯讀：查資源目前狀態，決定下一步要走哪條路。"""
import asyncio, os
from playwright.async_api import async_playwright

PROFILE = os.path.expanduser('~/.config/gsc-playwright')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, '_預覽', 'state')
os.makedirs(OUT, exist_ok=True)
SITE = 'https://ruru02044567.github.io/lin-brothers-taekwondo/'
ENC = SITE.replace(':', '%3A').replace('/', '%2F')


async def main():
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            PROFILE, headless=True, channel='msedge',
            viewport={'width': 1360, 'height': 960})
        pg = ctx.pages[0] if ctx.pages else await ctx.new_page()
        pg.set_default_timeout(35000)

        for tag, url in [
            ('sitemaps', 'https://search.google.com/search-console/sitemaps?resource_id=' + ENC),
            ('overview', 'https://search.google.com/search-console?resource_id=' + ENC),
        ]:
            try:
                await pg.goto(url, wait_until='domcontentloaded')
                await pg.wait_for_timeout(9000)
                await pg.screenshot(path=os.path.join(OUT, tag + '.png'), full_page=False)
                body = (await pg.inner_text('body'))[:900].replace('\n', ' | ')
                print('=== %s ===' % tag, flush=True)
                print('URL :', pg.url[:120], flush=True)
                print('TEXT:', body, flush=True)
                print('', flush=True)
            except Exception as e:
                print('=== %s === ERROR %s' % (tag, str(e)[:150]), flush=True)
        await ctx.close()

asyncio.run(main())
