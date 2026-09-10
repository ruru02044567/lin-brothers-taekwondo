# -*- coding: utf-8 -*-
"""驗證檔已上線，回頭按驗證 → 送 sitemap → 請求索引。"""
import asyncio, os, json, re

PROFILE = os.path.expanduser('~/.config/gsc-playwright')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, '_預覽', 'gsc2')
os.makedirs(OUT, exist_ok=True)

SITE = 'https://ruru02044567.github.io/lin-brothers-taekwondo/'
ENC = SITE.replace(':', '%3A').replace('/', '%2F')
URLS = [
    SITE,
    SITE + 'lin-sheng-xiang.html',
    SITE + 'lin-sheng-chen.html',
]
REPORT = []


def note(step, ok, detail=''):
    REPORT.append({'step': step, 'ok': ok, 'detail': str(detail)[:180]})
    print('[%s] %s | %s' % ('OK  ' if ok else 'FAIL', step, str(detail)[:140]), flush=True)


async def shot(pg, n):
    try:
        await pg.screenshot(path=os.path.join(OUT, n + '.png'))
    except Exception:
        pass


async def btext(pg, n=1200):
    try:
        return (await pg.inner_text('body'))[:n]
    except Exception:
        return ''


async def click_exact(pg, label, after_y=None):
    """用座標點擊寫著 label 的可見元素。"""
    try:
        loc = pg.get_by_text(label, exact=True)
        for i in range(await loc.count()):
            el = loc.nth(i)
            if not await el.is_visible():
                continue
            bb = await el.bounding_box()
            if not bb:
                continue
            if after_y and bb['y'] < after_y:
                continue
            await pg.mouse.click(bb['x'] + bb['width'] / 2, bb['y'] + bb['height'] / 2)
            print('  點了「%s」at (%.0f,%.0f)' % (label, bb['x'], bb['y']), flush=True)
            return True
    except Exception as e:
        print('  點擊失敗 %s: %s' % (label, str(e)[:80]), flush=True)
    return False


async def main():
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            PROFILE, headless=False, channel='msedge',
            viewport={'width': 1360, 'height': 960},
            args=['--window-position=40,20'])
        pg = ctx.pages[0] if ctx.pages else await ctx.new_page()
        pg.set_default_timeout(25000)

        # ── 1. 開歡迎頁，點「已經開始驗證了嗎？請繼續完成驗證」 ──
        await pg.goto('https://search.google.com/search-console/welcome',
                      wait_until='domcontentloaded')
        await pg.wait_for_timeout(6000)
        await shot(pg, '01_welcome')

        # 先試試資源是否已存在（直接開 sitemap 頁，若已驗證會正常顯示）
        await pg.goto('https://search.google.com/search-console/sitemaps?resource_id=' + ENC,
                      wait_until='domcontentloaded')
        await pg.wait_for_timeout(7000)
        await shot(pg, '02_sitemap_try')
        b = await btext(pg, 800)
        already = 'Sitemap' in b or 'sitemap' in b.lower()
        print('--- sitemap 頁畫面 ---\n' + b[:400] + '\n', flush=True)

        if not already or '沒有權限' in b or '找不到' in b:
            # 回歡迎頁走驗證流程
            await pg.goto('https://search.google.com/search-console/welcome',
                          wait_until='domcontentloaded')
            await pg.wait_for_timeout(5000)
            got = await click_exact(pg, '已經開始驗證了嗎？請繼續完成驗證')
            if not got:
                for t in ['請繼續完成驗證', '繼續完成驗證']:
                    if await click_exact(pg, t):
                        got = True
                        break
            await pg.wait_for_timeout(6000)
            await shot(pg, '03_resume_verify')
            b2 = await btext(pg, 1200)
            print('--- 續驗畫面 ---\n' + b2[:500] + '\n', flush=True)
            ok = await click_exact(pg, '驗證')
            await pg.wait_for_timeout(14000)
            await shot(pg, '04_after_verify')
            b3 = await btext(pg, 900)
            verified = any(k in b3 for k in ['已驗證擁有權', '驗證成功', '恭喜',
                                             'Ownership verified'])
            note('按驗證', verified, b3[:150])
            print('--- 驗證後畫面 ---\n' + b3[:500] + '\n', flush=True)
            await click_exact(pg, '前往資源')
            await pg.wait_for_timeout(6000)
        else:
            note('資源已存在', True, '直接進行 sitemap')

        # ── 2. 送 sitemap ───────────────────────────────────────
        await pg.goto('https://search.google.com/search-console/sitemaps?resource_id=' + ENC,
                      wait_until='domcontentloaded')
        await pg.wait_for_timeout(8000)
        await shot(pg, '05_sitemap_page')
        b4 = await btext(pg, 700)
        print('--- sitemap 頁 ---\n' + b4[:400] + '\n', flush=True)
        sent = False
        try:
            inputs = pg.locator('input[type=text], input:not([type])')
            for i in range(await inputs.count()):
                el = inputs.nth(i)
                if await el.is_visible():
                    await el.click()
                    await el.fill('sitemap.xml')
                    if 'sitemap' in (await el.input_value()):
                        sent = True
                        break
            if sent:
                if not await click_exact(pg, '提交'):
                    await click_exact(pg, 'SUBMIT')
                await pg.wait_for_timeout(10000)
        except Exception as e:
            print('  sitemap 例外:', str(e)[:120], flush=True)
        await shot(pg, '06_sitemap_done')
        note('送 sitemap', sent, (await btext(pg, 200)))

        # ── 3. 請求索引 ─────────────────────────────────────────
        for i, u in enumerate(URLS):
            try:
                insp = ('https://search.google.com/search-console/inspect?resource_id='
                        + ENC + '&id=' + u.replace(':', '%3A').replace('/', '%2F'))
                await pg.goto(insp, wait_until='domcontentloaded')
                await pg.wait_for_timeout(16000)
                await shot(pg, '07_inspect_%d' % i)
                ok = await click_exact(pg, '要求建立索引')
                if not ok:
                    ok = await click_exact(pg, 'REQUEST INDEXING')
                await pg.wait_for_timeout(18000)
                await shot(pg, '08_indexed_%d' % i)
                note('請求索引 %d' % (i + 1), ok, u.split('/')[-1] or 'index')
            except Exception as e:
                note('請求索引 %d' % (i + 1), False, str(e)[:100])

        print('\n' + '=' * 46, flush=True)
        print(json.dumps(REPORT, ensure_ascii=False, indent=2), flush=True)
        print('=' * 46, flush=True)
        await ctx.close()

asyncio.run(main())
