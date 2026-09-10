# -*- coding: utf-8 -*-
"""檢查線上網站三頁是否正常顯示。"""
import asyncio, os
from playwright.async_api import async_playwright

B = 'https://ruru02044567.github.io/lin-brothers-taekwondo'
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '_預覽')
os.makedirs(OUT, exist_ok=True)

PAGES = [('/', 'live_index'), ('/lin-sheng-xiang.html', 'live_xiang'),
         ('/lin-sheng-chen.html', 'live_chen')]


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width': 1280, 'height': 900})
        errs = []
        pg.on('console', lambda m: errs.append('console ' + m.type + ': ' + m.text)
              if m.type == 'error' else None)
        pg.on('pageerror', lambda e: errs.append('pageerror: ' + str(e)))
        pg.on('requestfailed', lambda r: errs.append('failed: ' + r.url))

        for path, name in PAGES:
            errs.clear()
            await pg.goto(B + path, wait_until='networkidle')
            await pg.wait_for_timeout(1200)
            items = await pg.eval_on_selector_all('.item', 'els => els.length')
            visible = await pg.eval_on_selector_all(
                '.item', 'els => els.filter(e => !e.hidden).length')
            cnt = await pg.text_content('#count')
            h1 = (await pg.text_content('h1') or '').strip().replace('\n', ' ')
            imgs = await pg.eval_on_selector_all(
                'img', 'els => els.filter(e => e.naturalWidth === 0).length')
            await pg.screenshot(path=os.path.join(OUT, name + '.png'))
            print('%-24s h1=%-22s 列數=%-3d 顯示=%-3d 計數文字=%-16s 壞圖=%d'
                  % (path, h1[:20], items, visible, cnt, imgs))
            if errs:
                print('    錯誤:', errs[:4])

        # 實際點一列，看燈箱有沒有出圖
        await pg.goto(B + '/lin-sheng-xiang.html', wait_until='networkidle')
        await pg.wait_for_timeout(1500)
        await pg.click('.item')
        await pg.wait_for_timeout(1500)
        vis = await pg.is_visible('#lb')
        src = await pg.get_attribute('#lbImg', 'src')
        nw = await pg.eval_on_selector('#lbImg', 'e => e.naturalWidth')
        print('\n燈箱：開啟=%s 圖片=%s 實際載入寬度=%s' % (vis, src, nw))
        await pg.screenshot(path=os.path.join(OUT, 'live_lightbox.png'))
        await b.close()

asyncio.run(main())
