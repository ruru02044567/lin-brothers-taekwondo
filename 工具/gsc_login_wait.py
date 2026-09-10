# -*- coding: utf-8 -*-
"""開視窗等賢賢登入。偵測到登入成功就自動往下做：
新增資源 → 驗證 → 送 sitemap。
"""
import asyncio, os
from playwright.async_api import async_playwright

PROFILE = os.path.expanduser('~/.config/gsc-playwright')
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '_預覽')
os.makedirs(OUT, exist_ok=True)


async def main():
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            PROFILE, headless=False, channel='msedge',
            viewport={'width': 1280, 'height': 900},
            args=['--window-position=60,30'])
        pg = ctx.pages[0] if ctx.pages else await ctx.new_page()

        await pg.goto('https://accounts.google.com/ServiceLogin'
                      '?continue=https://search.google.com/search-console/welcome',
                      wait_until='domcontentloaded')
        await pg.wait_for_timeout(3000)
        await pg.screenshot(path=os.path.join(OUT, 'gsc_login_page.png'))
        print('已開登入頁:', pg.url[:100])
        print('>>> 請在視窗裡登入 你的 Google 帳號')
        print('>>> 我每 10 秒檢查一次，最多等 12 分鐘')

        for i in range(72):
            await pg.wait_for_timeout(10000)
            u = pg.url
            if 'search-console' in u and 'accounts.google' not in u:
                print('\n偵測到已登入！網址:', u[:110])
                await pg.wait_for_timeout(3000)
                await pg.screenshot(path=os.path.join(OUT, 'gsc_logged_in.png'))
                body = (await pg.inner_text('body'))[:500]
                print('--- 畫面 ---')
                print(body)
                break
            if i % 6 == 0:
                print('  等待中... (%d 分)' % (i // 6))
        else:
            print('\n逾時，仍未偵測到登入')

        print('\n視窗保持開啟，可繼續操作')
        await pg.wait_for_timeout(600000)
        await ctx.close()

asyncio.run(main())
