# -*- coding: utf-8 -*-
"""用頁面上方的網址審查框（不用組 URL），逐一測三頁並請求索引。"""
import asyncio, os
from playwright.async_api import async_playwright

PROFILE = os.path.expanduser('~/.config/gsc-playwright')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, '_預覽', 'inspect')
os.makedirs(OUT, exist_ok=True)
SITE = 'https://ruru02044567.github.io/lin-brothers-taekwondo/'
ENC = SITE.replace(':', '%3A').replace('/', '%2F')
HOME = 'https://search.google.com/search-console?resource_id=' + ENC
URLS = [SITE, SITE + 'lin-sheng-xiang.html', SITE + 'lin-sheng-chen.html']
REPORT = []


async def inspect_one(pg, url, tag):
    print('\n>>> 審查:', url, flush=True)
    await pg.goto(HOME, wait_until='domcontentloaded')
    await pg.wait_for_timeout(11000)
    for _ in range(2):
        await pg.keyboard.press('Escape'); await pg.wait_for_timeout(700)

    # 上方審查框
    box = None
    for getter in [
        lambda: pg.get_by_placeholder('檢查'),
        lambda: pg.locator('input[aria-label*="檢查"]'),
        lambda: pg.locator('input[type=text]'),
    ]:
        try:
            loc = getter()
            for i in range(await loc.count()):
                el = loc.nth(i)
                if await el.is_visible():
                    box = el; break
            if box: break
        except Exception: pass
    if not box:
        print('   找不到審查框', flush=True)
        REPORT.append((tag, 'NO_BOX', ''))
        return

    await box.click(); await pg.wait_for_timeout(600)
    await box.fill('')
    await box.type(url, delay=25)
    await box.press('Enter')
    print('   已送出審查，等待結果…', flush=True)

    # 等結果（最多 90 秒）
    verdict = ''
    for i in range(18):
        await pg.wait_for_timeout(5000)
        b = await pg.inner_text('body')
        for k in ['網址在 Google 上', '網址不在 Google 上', '已建立索引',
                  '尚未建立索引', '正在擷取', '正在測試']:
            if k in b:
                verdict = k; break
        if verdict and '正在' not in verdict:
            break
    await pg.screenshot(path=os.path.join(OUT, tag + '_result.png'))
    print('   判定:', verdict or '(讀不到)', flush=True)

    # 按要求建立索引
    hit = None
    for lab in ['要求建立索引', '要求編入索引', 'REQUEST INDEXING']:
        try:
            loc = pg.get_by_text(lab, exact=False)
            for i in range(min(await loc.count(), 4)):
                el = loc.nth(i)
                if await el.is_visible():
                    bb = await el.bounding_box()
                    if bb and bb['width'] > 4:
                        await pg.mouse.click(bb['x']+bb['width']/2, bb['y']+bb['height']/2)
                        hit = lab; break
            if hit: break
        except Exception as e:
            print('   點 %s 失敗 %s' % (lab, str(e)[:60]), flush=True)
    if hit:
        print('   已按「%s」，等待處理…' % hit, flush=True)
        for i in range(12):
            await pg.wait_for_timeout(5000)
            b = await pg.inner_text('body')
            if any(k in b for k in ['已要求建立索引', '已加入優先檢索佇列',
                                    '編入索引的要求', 'Indexing requested']):
                print('   ✅ 索引請求已受理', flush=True)
                break
        await pg.screenshot(path=os.path.join(OUT, tag + '_requested.png'))
    REPORT.append((tag, verdict or '?', hit or 'no-button'))


async def main():
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            PROFILE, headless=True, channel='msedge',
            viewport={'width': 1400, 'height': 1000})
        pg = ctx.pages[0] if ctx.pages else await ctx.new_page()
        pg.set_default_timeout(50000)
        for i, u in enumerate(URLS):
            try:
                await inspect_one(pg, u, 'p%d' % i)
            except Exception as e:
                print('   例外:', str(e)[:150], flush=True)
                REPORT.append(('p%d' % i, 'ERROR', str(e)[:80]))
        print('\n' + '='*50, flush=True)
        for r in REPORT:
            print('  %-4s %-16s %s' % r, flush=True)
        print('='*50, flush=True)
        await ctx.close()

asyncio.run(main())
