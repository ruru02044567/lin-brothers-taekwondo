# -*- coding: utf-8 -*-
"""刪掉錯誤那列 /sitemap.xml（根目錄，404），只保留正確路徑。"""
import asyncio, os, re
from playwright.async_api import async_playwright

PROFILE = os.path.expanduser('~/.config/gsc-playwright')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, '_預覽', 'del')
os.makedirs(OUT, exist_ok=True)
SITE = 'https://ruru02044567.github.io/lin-brothers-taekwondo/'
ENC = SITE.replace(':', '%3A').replace('/', '%2F')
SM_URL = 'https://search.google.com/search-console/sitemaps?resource_id=' + ENC


async def main():
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            PROFILE, headless=True, channel='msedge',
            viewport={'width': 1400, 'height': 1000})
        pg = ctx.pages[0] if ctx.pages else await ctx.new_page()
        pg.set_default_timeout(45000)
        await pg.goto(SM_URL, wait_until='domcontentloaded')
        await pg.wait_for_timeout(13000)
        for _ in range(2):
            await pg.keyboard.press('Escape'); await pg.wait_for_timeout(700)

        # 點「/sitemap.xml」那一列（精準比對，不能命中長路徑那列）
        rows = pg.get_by_text('/sitemap.xml', exact=True)
        cnt = await rows.count()
        print('精準命中 /sitemap.xml 列數:', cnt, flush=True)
        done = False
        for i in range(cnt):
            el = rows.nth(i)
            if not await el.is_visible():
                continue
            bb = await el.bounding_box()
            await pg.mouse.click(bb['x']+bb['width']/2, bb['y']+bb['height']/2)
            await pg.wait_for_timeout(9000)
            await pg.screenshot(path=os.path.join(OUT, 'detail.png'))
            b = await pg.inner_text('body')
            print('詳情頁含 sitemap 路徑:', '/sitemap.xml' in b, flush=True)
            # 找刪除入口
            for lab in ['移除 Sitemap', '刪除 Sitemap', '移除', '刪除']:
                try:
                    l2 = pg.get_by_text(lab, exact=False)
                    for j in range(min(await l2.count(), 4)):
                        e2 = l2.nth(j)
                        if await e2.is_visible():
                            b2 = await e2.bounding_box()
                            if b2 and b2['width'] > 4:
                                await pg.mouse.click(b2['x']+b2['width']/2, b2['y']+b2['height']/2)
                                print('點了「%s」' % lab, flush=True)
                                await pg.wait_for_timeout(5000)
                                # 確認對話框
                                for c in ['移除', '刪除', 'REMOVE', '確定']:
                                    try:
                                        bt = pg.get_by_role('button', name=c)
                                        if await bt.count() and await bt.first.is_visible():
                                            await bt.first.click()
                                            print('確認:', c, flush=True)
                                            break
                                    except Exception: pass
                                await pg.wait_for_timeout(8000)
                                done = True
                                break
                    if done: break
                except Exception: pass
            break

        await pg.goto(SM_URL, wait_until='domcontentloaded')
        await pg.wait_for_timeout(12000)
        await pg.screenshot(path=os.path.join(OUT, 'after.png'), full_page=True)
        b = await pg.inner_text('body')
        for line in b.split('\n'):
            if 'sitemap.xml' in line or '列，共' in line:
                print('  ', line.strip(), flush=True)
        await ctx.close()

asyncio.run(main())
