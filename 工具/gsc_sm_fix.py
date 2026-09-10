# -*- coding: utf-8 -*-
"""避開「提交意見」面板，只在「新增 Sitemap」卡片內操作。"""
import asyncio, os, re
from playwright.async_api import async_playwright

PROFILE = os.path.expanduser('~/.config/gsc-playwright')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, '_預覽', 'smfix')
os.makedirs(OUT, exist_ok=True)
SITE = 'https://ruru02044567.github.io/lin-brothers-taekwondo/'
ENC = SITE.replace(':', '%3A').replace('/', '%2F')
SM_URL = 'https://search.google.com/search-console/sitemaps?resource_id=' + ENC


async def rows(pg):
    b = await pg.inner_text('body')
    m = re.search(r'共\s*(\d+)\s*列', b)
    return int(m.group(1)) if m else -1


async def main():
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            PROFILE, headless=True, channel='msedge',
            viewport={'width': 1400, 'height': 1000})
        pg = ctx.pages[0] if ctx.pages else await ctx.new_page()
        pg.set_default_timeout(40000)

        ok_rpc = {'hit': False}
        def on_resp(r):
            if 'batchexecute' in r.url and 'rpcids=' in r.url:
                rid = r.url.split('rpcids=')[1].split('&')[0]
                print('   RPC %s -> %d' % (rid, r.status), flush=True)
                ok_rpc['hit'] = True
        pg.on('response', on_resp)

        await pg.goto(SM_URL, wait_until='domcontentloaded')
        await pg.wait_for_timeout(12000)

        # 關掉任何側邊面板 / 彈窗
        for _ in range(3):
            await pg.keyboard.press('Escape')
            await pg.wait_for_timeout(900)
        for lab in ['我知道了', 'GOT IT', '關閉']:
            try:
                loc = pg.get_by_role('button', name=lab)
                if await loc.count() and await loc.first.is_visible():
                    await loc.first.click(); await pg.wait_for_timeout(1800)
            except Exception: pass
        await pg.screenshot(path=os.path.join(OUT, '01_clean.png'))
        print('清場後列數:', await rows(pg), flush=True)

        # 只在「新增 Sitemap」卡片範圍內操作
        el = pg.get_by_label('輸入 Sitemap 網址').first
        await el.scroll_into_view_if_needed()
        await el.click(); await pg.wait_for_timeout(700)
        await el.fill('')
        await el.type('sitemap.xml', delay=110)
        val = await el.input_value()
        box = await el.bounding_box()
        print('欄位值=「%s」 位置 x=%.0f y=%.0f' % (val, box['x'], box['y']), flush=True)
        await pg.screenshot(path=os.path.join(OUT, '02_typed.png'))

        # 送出：Enter
        await el.press('Enter')
        await pg.wait_for_timeout(10000)
        await pg.screenshot(path=os.path.join(OUT, '03_after_enter.png'))
        n1 = await rows(pg)
        print('Enter 後列數:', n1, flush=True)

        if n1 < 1:
            # 找跟輸入框同一列、在它右邊的按鈕
            print('--- Enter 無效，找卡片內按鈕 ---', flush=True)
            btns = pg.locator('button, [role=button]')
            cnt = await btns.count()
            for i in range(cnt):
                b = btns.nth(i)
                try:
                    if not await b.is_visible():
                        continue
                    bb = await b.bounding_box()
                    if not bb:
                        continue
                    t = ((await b.inner_text()) or '').strip()[:20]
                    same_row = abs(bb['y'] - box['y']) < 70
                    right_of = bb['x'] > box['x']
                    if same_row and right_of:
                        print('   候選按鈕「%s」 x=%.0f y=%.0f' % (t, bb['x'], bb['y']), flush=True)
                        await b.click()
                        await pg.wait_for_timeout(10000)
                        break
                except Exception:
                    pass
            await pg.screenshot(path=os.path.join(OUT, '04_after_btn.png'))

        # 重整驗收
        await pg.goto(SM_URL, wait_until='domcontentloaded')
        await pg.wait_for_timeout(12000)
        final = await rows(pg)
        await pg.screenshot(path=os.path.join(OUT, '05_final.png'), full_page=True)
        body = await pg.inner_text('body')
        idx = body.find('已提交的 Sitemap')
        print('\n=== 最終列數:', final, '===', flush=True)
        print(body[idx:idx+600] if idx > 0 else body[:600], flush=True)
        print('\n>>> RESULT:', 'SUCCESS' if final >= 1 else 'STILL_ZERO', flush=True)
        await ctx.close()

asyncio.run(main())
