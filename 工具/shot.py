# -*- coding: utf-8 -*-
import asyncio, sys, os
from playwright.async_api import async_playwright

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '_預覽')
os.makedirs(OUT, exist_ok=True)

PAGES = [
    ('index.html', 'index'),
    ('lin-sheng-xiang.html', 'xiang'),
]

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width': 1280, 'height': 1000},
                              device_scale_factor=1)
        errs = []
        pg.on('console', lambda m: errs.append(m.type + ': ' + m.text) if m.type == 'error' else None)
        pg.on('pageerror', lambda e: errs.append('pageerror: ' + str(e)))
        for f, name in PAGES:
            await pg.goto('http://127.0.0.1:8931/' + f, wait_until='networkidle')
            await pg.wait_for_timeout(700)
            await pg.screenshot(path=os.path.join(OUT, name + '_top.png'))
            await pg.screenshot(path=os.path.join(OUT, name + '_full.png'), full_page=True)
            print(name, 'shot ok')
        # 測搜尋
        await pg.goto('http://127.0.0.1:8931/index.html', wait_until='networkidle')
        await pg.fill('#q', '屏東')
        await pg.wait_for_timeout(400)
        print('搜尋「屏東」→', await pg.text_content('#count'))
        await pg.screenshot(path=os.path.join(OUT, 'search.png'))
        await pg.fill('#q', '')
        # 測燈箱
        await pg.click('.item')
        await pg.wait_for_timeout(900)
        vis = await pg.is_visible('#lb')
        src = await pg.get_attribute('#lbImg', 'src')
        print('燈箱開啟：', vis, '圖片：', src)
        await pg.screenshot(path=os.path.join(OUT, 'lightbox.png'))
        # 手機寬
        await pg.set_viewport_size({'width': 390, 'height': 844})
        await pg.goto('http://127.0.0.1:8931/index.html', wait_until='networkidle')
        await pg.wait_for_timeout(500)
        await pg.screenshot(path=os.path.join(OUT, 'mobile.png'), full_page=False)
        w = await pg.evaluate('document.documentElement.scrollWidth')
        print('手機版 scrollWidth =', w, '(390 以內才沒有橫向捲動)')
        print('console 錯誤：', errs if errs else '無')
        await b.close()

asyncio.run(main())
