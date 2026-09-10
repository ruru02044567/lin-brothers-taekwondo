# -*- coding: utf-8 -*-
"""改填完整網址重送 sitemap，並讀回每列狀態。"""
import asyncio, os, re
from playwright.async_api import async_playwright

PROFILE = os.path.expanduser('~/.config/gsc-playwright')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, '_預覽', 'smfull')
os.makedirs(OUT, exist_ok=True)
SITE = 'https://ruru02044567.github.io/lin-brothers-taekwondo/'
ENC = SITE.replace(':', '%3A').replace('/', '%2F')
SM_URL = 'https://search.google.com/search-console/sitemaps?resource_id=' + ENC

# 兩種寫法都送，看哪個被接受
CANDS = ['lin-brothers-taekwondo/sitemap.xml', 'sitemap.xml']


async def table(pg):
    b = await pg.inner_text('body')
    idx = b.find('已提交的 Sitemap')
    seg = b[idx:idx + 700] if idx > 0 else ''
    m = re.search(r'共\s*(\d+)\s*列', b)
    return (int(m.group(1)) if m else -1), seg


async def submit(pg, value):
    for _ in range(2):
        await pg.keyboard.press('Escape'); await pg.wait_for_timeout(800)
    el = pg.get_by_label('輸入 Sitemap 網址').first
    await el.scroll_into_view_if_needed()
    await el.click(); await pg.wait_for_timeout(600)
    await el.fill('')
    await el.type(value, delay=70)
    box = await el.bounding_box()
    print('   填入「%s」' % (await el.input_value()), flush=True)
    # 找同列右方按鈕
    btns = pg.locator('button, [role=button]')
    for i in range(await btns.count()):
        b = btns.nth(i)
        try:
            if not await b.is_visible():
                continue
            bb = await b.bounding_box()
            if not bb:
                continue
            if abs(bb['y'] - box['y']) < 70 and bb['x'] > box['x']:
                t = ((await b.inner_text()) or '').strip()[:12]
                await b.click()
                print('   按了「%s」' % t, flush=True)
                await pg.wait_for_timeout(11000)
                return True
        except Exception:
            pass
    return False


async def main():
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            PROFILE, headless=True, channel='msedge',
            viewport={'width': 1400, 'height': 1000})
        pg = ctx.pages[0] if ctx.pages else await ctx.new_page()
        pg.set_default_timeout(40000)

        for v in CANDS:
            print('\n>>> 嘗試送出:', v, flush=True)
            await pg.goto(SM_URL, wait_until='domcontentloaded')
            await pg.wait_for_timeout(12000)
            await submit(pg, v)
            await pg.wait_for_timeout(4000)

        # 最後重整看全表
        await pg.goto(SM_URL, wait_until='domcontentloaded')
        await pg.wait_for_timeout(14000)
        await pg.screenshot(path=os.path.join(OUT, 'final.png'), full_page=True)
        n, seg = await table(pg)
        print('\n=== 共 %d 列 ===' % n, flush=True)
        print(seg, flush=True)
        await ctx.close()

asyncio.run(main())
