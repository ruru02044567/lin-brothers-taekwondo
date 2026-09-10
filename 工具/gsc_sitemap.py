# -*- coding: utf-8 -*-
"""專攻送 sitemap：先關說明彈窗，精準填欄位，用「已提交列數」驗收。"""
import asyncio, os, re
from playwright.async_api import async_playwright

PROFILE = os.path.expanduser('~/.config/gsc-playwright')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, '_預覽', 'sm')
os.makedirs(OUT, exist_ok=True)
SITE = 'https://ruru02044567.github.io/lin-brothers-taekwondo/'
ENC = SITE.replace(':', '%3A').replace('/', '%2F')
SM_URL = 'https://search.google.com/search-console/sitemaps?resource_id=' + ENC


async def rows(pg):
    """讀『0-0 列，共 N 列』的 N。"""
    try:
        b = await pg.inner_text('body')
        m = re.search(r'共\s*(\d+)\s*列', b)
        return int(m.group(1)) if m else -1
    except Exception:
        return -1


async def main():
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            PROFILE, headless=True, channel='msedge',
            viewport={'width': 1400, 'height': 1000})
        pg = ctx.pages[0] if ctx.pages else await ctx.new_page()
        pg.set_default_timeout(40000)

        await pg.goto(SM_URL, wait_until='domcontentloaded')
        await pg.wait_for_timeout(11000)
        print('進站前列數:', await rows(pg), flush=True)

        # 關掉「我知道了」說明彈窗
        for lab in ['我知道了', 'GOT IT', '關閉', 'Dismiss']:
            try:
                loc = pg.get_by_text(lab, exact=True)
                if await loc.count() and await loc.first.is_visible():
                    await loc.first.click()
                    print('關掉彈窗:', lab, flush=True)
                    await pg.wait_for_timeout(2500)
                    break
            except Exception:
                pass
        await pg.screenshot(path=os.path.join(OUT, '01_after_dismiss.png'))

        # 精準找「輸入 Sitemap 網址」欄位
        filled = False
        strategies = [
            ('placeholder', lambda: pg.get_by_placeholder('輸入 Sitemap 網址')),
            ('placeholder_en', lambda: pg.get_by_placeholder('Enter sitemap URL')),
            ('label', lambda: pg.get_by_label('輸入 Sitemap 網址')),
            ('any_text_input', lambda: pg.locator('input[type=text]')),
        ]
        for name, get in strategies:
            try:
                loc = get()
                cnt = await loc.count()
                for i in range(cnt):
                    el = loc.nth(i)
                    if not await el.is_visible():
                        continue
                    await el.click()
                    await pg.wait_for_timeout(600)
                    await el.fill('')
                    await el.type('sitemap.xml', delay=90)
                    val = await el.input_value()
                    print('策略 %-14s 第%d個 → 值=「%s」' % (name, i, val), flush=True)
                    if 'sitemap' in val:
                        filled = True
                        break
                if filled:
                    break
            except Exception as e:
                print('策略 %s 例外 %s' % (name, str(e)[:90]), flush=True)

        await pg.screenshot(path=os.path.join(OUT, '02_filled.png'))
        if not filled:
            print('!! 找不到輸入框，中止', flush=True)
            await ctx.close()
            return

        # 送出：先試 Enter，再試提交按鈕
        before = await rows(pg)
        await pg.keyboard.press('Enter')
        await pg.wait_for_timeout(9000)
        after = await rows(pg)
        print('Enter 送出後 列數 %d → %d' % (before, after), flush=True)

        if after <= 0:
            for lab in ['提交', 'SUBMIT']:
                try:
                    b = pg.get_by_role('button', name=lab)
                    if await b.count() and await b.first.is_visible():
                        await b.first.click()
                        print('按了按鈕:', lab, flush=True)
                        break
                    loc = pg.get_by_text(lab, exact=True)
                    if await loc.count() and await loc.first.is_visible():
                        bb = await loc.first.bounding_box()
                        await pg.mouse.click(bb['x'] + bb['width'] / 2, bb['y'] + bb['height'] / 2)
                        print('座標按了:', lab, flush=True)
                        break
                except Exception as e:
                    print('按 %s 失敗 %s' % (lab, str(e)[:80]), flush=True)
            await pg.wait_for_timeout(11000)

        await pg.screenshot(path=os.path.join(OUT, '03_submitted.png'))
        # 重新整理確認
        await pg.goto(SM_URL, wait_until='domcontentloaded')
        await pg.wait_for_timeout(11000)
        final = await rows(pg)
        await pg.screenshot(path=os.path.join(OUT, '04_reload.png'), full_page=True)
        body = await pg.inner_text('body')
        print('\n=== 重整後列數:', final, '===', flush=True)
        idx = body.find('已提交的 Sitemap')
        print(body[idx:idx + 700] if idx > 0 else body[:700], flush=True)
        print('\n>>> 結果:', 'SUCCESS sitemap 已登錄' if final >= 1 else 'STILL_ZERO 尚未登錄', flush=True)
        await ctx.close()

asyncio.run(main())
