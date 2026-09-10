# -*- coding: utf-8 -*-
"""重試單一網址的索引請求，最多 4 次，讀真實回饋。"""
import asyncio, os, sys
from playwright.async_api import async_playwright

PROFILE = os.path.expanduser('~/.config/gsc-playwright')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, '_預覽', 'retry')
os.makedirs(OUT, exist_ok=True)
SITE = 'https://ruru02044567.github.io/lin-brothers-taekwondo/'
ENC = SITE.replace(':', '%3A').replace('/', '%2F')
HOME = 'https://search.google.com/search-console?resource_id=' + ENC
TARGET = SITE + 'lin-sheng-xiang.html'


async def attempt(pg, n):
    await pg.goto(HOME, wait_until='domcontentloaded')
    await pg.wait_for_timeout(11000)
    for _ in range(2):
        await pg.keyboard.press('Escape'); await pg.wait_for_timeout(700)

    box = None
    loc = pg.locator('input[type=text]')
    for i in range(await loc.count()):
        if await loc.nth(i).is_visible():
            box = loc.nth(i); break
    if not box:
        return 'NO_BOX'
    await box.click(); await box.fill(''); await box.type(TARGET, delay=20)
    await box.press('Enter')

    for _ in range(18):
        await pg.wait_for_timeout(5000)
        b = await pg.inner_text('body')
        if '網址不在 Google' in b or '網址在 Google' in b:
            break

    hit = False
    loc2 = pg.get_by_text('要求建立索引', exact=False)
    for i in range(min(await loc2.count(), 4)):
        el = loc2.nth(i)
        if await el.is_visible():
            bb = await el.bounding_box()
            if bb and bb['width'] > 4:
                await pg.mouse.click(bb['x']+bb['width']/2, bb['y']+bb['height']/2)
                hit = True; break
    if not hit:
        return 'NO_BUTTON'

    for _ in range(14):
        await pg.wait_for_timeout(5000)
        b = await pg.inner_text('body')
        if any(k in b for k in ['已要求建立索引', '已加入優先檢索佇列', '編入索引的要求']):
            await pg.screenshot(path=os.path.join(OUT, 'ok_%d.png' % n))
            return 'SUCCESS'
        if '發生錯誤' in b or '請稍後再試' in b:
            await pg.screenshot(path=os.path.join(OUT, 'err_%d.png' % n))
            return 'RETRY_LATER'
    return 'TIMEOUT'


async def main():
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            PROFILE, headless=True, channel='msedge',
            viewport={'width': 1400, 'height': 1000})
        pg = ctx.pages[0] if ctx.pages else await ctx.new_page()
        pg.set_default_timeout(50000)
        for n in range(4):
            r = await attempt(pg, n)
            print('第%d次 → %s' % (n+1, r), flush=True)
            if r == 'SUCCESS':
                break
            await pg.wait_for_timeout(20000)
        await ctx.close()

asyncio.run(main())
