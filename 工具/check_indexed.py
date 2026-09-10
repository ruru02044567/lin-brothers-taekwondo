# -*- coding: utf-8 -*-
"""用真瀏覽器實際搜尋，確認是否已被 Google 收錄。"""
import asyncio, os

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   '_預覽', 'search')
os.makedirs(OUT, exist_ok=True)

QUERIES = [
    ('site:ruru02044567.github.io/lin-brothers-taekwondo', 'site_query'),
    ('民逸跆訓 林聖翔', 'name_xiang'),
    ('民逸跆訓', 'dojo'),
]


async def main():
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        pg = await b.new_page(
            viewport={'width': 1280, 'height': 1000},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36',
            locale='zh-TW')
        for q, name in QUERIES:
            url = 'https://www.google.com/search?hl=zh-TW&q=' + q.replace(' ', '+').replace(':', '%3A')
            try:
                await pg.goto(url, wait_until='domcontentloaded')
                await pg.wait_for_timeout(3500)
                await pg.screenshot(path=os.path.join(OUT, name + '.png'))
                txt = await pg.inner_text('body')
                hit = 'lin-brothers-taekwondo' in txt or 'ruru02044567.github.io' in txt
                # 找「找不到」訊息
                none = any(k in txt for k in ['找不到和您查詢的字詞相符的資料',
                                              '沒有找到', 'did not match any documents'])
                print('查詢「%s」' % q)
                print('  網站有出現: %s' % ('是' if hit else '否'))
                print('  Google 說找不到: %s' % ('是' if none else '否'))
                # 抓前幾筆結果標題
                try:
                    titles = await pg.eval_on_selector_all(
                        'h3', 'els => els.slice(0,5).map(e => e.innerText)')
                    for t in titles:
                        print('    結果:', t[:60])
                except Exception:
                    pass
                print()
            except Exception as e:
                print('查詢「%s」失敗: %s\n' % (q, str(e)[:100]))
        await b.close()

asyncio.run(main())
