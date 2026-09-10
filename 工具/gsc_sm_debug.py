# -*- coding: utf-8 -*-
"""送出後立刻連續抓畫面，找出 Google 回的錯誤訊息。"""
import asyncio, os, re
from playwright.async_api import async_playwright

PROFILE = os.path.expanduser('~/.config/gsc-playwright')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, '_預覽', 'smdbg')
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
        pg.set_default_timeout(40000)

        # 攔 API 回應
        seen = []
        def on_resp(r):
            u = r.url
            if 'sitemap' in u.lower() or 'batchexecute' in u.lower():
                seen.append('%d %s' % (r.status, u[:150]))
        pg.on('response', on_resp)

        await pg.goto(SM_URL, wait_until='domcontentloaded')
        await pg.wait_for_timeout(11000)
        for lab in ['我知道了', 'GOT IT']:
            try:
                loc = pg.get_by_text(lab, exact=True)
                if await loc.count() and await loc.first.is_visible():
                    await loc.first.click(); await pg.wait_for_timeout(2000); break
            except Exception: pass

        el = pg.get_by_label('輸入 Sitemap 網址').first
        await el.click(); await pg.wait_for_timeout(500)
        await el.fill(''); await el.type('sitemap.xml', delay=100)
        print('欄位值:', await el.input_value(), flush=True)
        await pg.screenshot(path=os.path.join(OUT, 'a_filled.png'))

        # 按提交
        clicked = False
        try:
            b = pg.get_by_role('button', name='提交')
            if await b.count() and await b.first.is_visible():
                await b.first.click(); clicked = True
        except Exception: pass
        if not clicked:
            loc = pg.get_by_text('提交', exact=True)
            bb = await loc.first.bounding_box()
            await pg.mouse.click(bb['x']+bb['width']/2, bb['y']+bb['height']/2)
        print('已按提交', flush=True)

        # 連續抓 6 次畫面找訊息
        for i in range(6):
            await pg.wait_for_timeout(4000)
            await pg.screenshot(path=os.path.join(OUT, 'b_%d.png' % i))
            b = await pg.inner_text('body')
            # 找關鍵訊息
            keys = ['無法', '錯誤', '失敗', '找不到', '成功', '已提交', 'Couldn',
                    'error', '請稍後', '不支援', '格式']
            hits = [k for k in keys if k in b]
            m = re.search(r'共\s*(\d+)\s*列', b)
            print('第%d次 t=%ds 列數=%s 命中=%s' % (i, (i+1)*4, m.group(1) if m else '?', hits), flush=True)
            # 印出對話框區域
            for sel in ['[role=alertdialog]', '[role=dialog]', '[role=alert]', '.snackbar', '[aria-live]']:
                try:
                    d = pg.locator(sel)
                    for j in range(min(await d.count(), 3)):
                        if await d.nth(j).is_visible():
                            t = (await d.nth(j).inner_text())[:300].replace('\n', ' | ')
                            if t.strip():
                                print('   [%s] %s' % (sel, t), flush=True)
                except Exception: pass

        print('\n--- 相關網路請求 ---', flush=True)
        for s in seen[-12:]:
            print('  ', s, flush=True)
        await ctx.close()

asyncio.run(main())
