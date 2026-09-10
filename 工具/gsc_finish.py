# -*- coding: utf-8 -*-
"""從 not-verified 頁按「驗證擁有權」→ 完成驗證 → 送 sitemap → 請求索引。
每步截圖 + 印 body，失敗自動換備援策略。
"""
import asyncio, os, json
from playwright.async_api import async_playwright

PROFILE = os.path.expanduser('~/.config/gsc-playwright')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, '_預覽', 'finish')
os.makedirs(OUT, exist_ok=True)

SITE = 'https://ruru02044567.github.io/lin-brothers-taekwondo/'
ENC = SITE.replace(':', '%3A').replace('/', '%2F')
URLS = [SITE, SITE + 'lin-sheng-xiang.html', SITE + 'lin-sheng-chen.html']
REPORT = []


def note(step, ok, detail=''):
    REPORT.append({'step': step, 'ok': bool(ok), 'detail': str(detail)[:200]})
    print('[%s] %-22s %s' % ('OK  ' if ok else 'FAIL', step, str(detail)[:150]), flush=True)


async def shot(pg, n):
    try:
        await pg.screenshot(path=os.path.join(OUT, n + '.png'))
    except Exception:
        pass


async def btext(pg, n=900):
    try:
        return (await pg.inner_text('body'))[:n]
    except Exception:
        return ''


async def click_any(pg, labels, timeout=6000):
    """多重策略點擊：role=button → get_by_text → 座標。回傳點到的 label。"""
    for lab in labels:
        try:
            b = pg.get_by_role('button', name=lab)
            if await b.count() and await b.first.is_visible():
                await b.first.click(timeout=timeout)
                print('   ↳ role-button 點到「%s」' % lab, flush=True)
                return lab
        except Exception:
            pass
        try:
            loc = pg.get_by_text(lab, exact=False)
            for i in range(min(await loc.count(), 6)):
                el = loc.nth(i)
                if not await el.is_visible():
                    continue
                bb = await el.bounding_box()
                if not bb or bb['width'] < 4:
                    continue
                await pg.mouse.click(bb['x'] + bb['width'] / 2, bb['y'] + bb['height'] / 2)
                print('   ↳ 座標點到「%s」at (%.0f,%.0f)' % (lab, bb['x'], bb['y']), flush=True)
                return lab
        except Exception as e:
            print('   ↳ 點「%s」失敗 %s' % (lab, str(e)[:70]), flush=True)
    return None


async def main():
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            PROFILE, headless=True, channel='msedge',
            viewport={'width': 1360, 'height': 980})
        pg = ctx.pages[0] if ctx.pages else await ctx.new_page()
        pg.set_default_timeout(35000)

        # ── 1. 驗證擁有權 ──────────────────────────────
        await pg.goto('https://search.google.com/search-console/sitemaps?resource_id=' + ENC,
                      wait_until='domcontentloaded')
        await pg.wait_for_timeout(8000)
        await shot(pg, '01_landing')
        b = await btext(pg)
        verified = '沒有存取這項資源的權限' not in b and 'not-verified' not in pg.url

        if not verified:
            hit = await click_any(pg, ['驗證擁有權', 'VERIFY OWNERSHIP', '驗證'])
            note('點驗證擁有權', hit, hit or '沒找到按鈕')
            await pg.wait_for_timeout(9000)
            await shot(pg, '02_verify_dialog')
            b2 = await btext(pg, 1400)
            print('--- 驗證對話框 ---\n%s\n' % b2[:600], flush=True)

            # 對話框裡可能還要再按一次「驗證」
            hit2 = await click_any(pg, ['驗證', 'VERIFY'])
            await pg.wait_for_timeout(15000)
            await shot(pg, '03_after_verify')
            b3 = await btext(pg, 1200)
            print('--- 驗證結果 ---\n%s\n' % b3[:600], flush=True)
            ok = any(k in b3 for k in ['已驗證擁有權', '驗證成功', '恭喜',
                                       'Ownership verified', '所有權已驗證'])
            note('驗證擁有權', ok, b3[:160])
            await click_any(pg, ['前往資源', 'GO TO PROPERTY', '完成', 'DONE'])
            await pg.wait_for_timeout(7000)
        else:
            note('驗證擁有權', True, '已是驗證狀態，跳過')

        # ── 2. 送 sitemap ─────────────────────────────
        await pg.goto('https://search.google.com/search-console/sitemaps?resource_id=' + ENC,
                      wait_until='domcontentloaded')
        await pg.wait_for_timeout(9000)
        await shot(pg, '04_sitemap_page')
        b4 = await btext(pg, 900)
        print('--- sitemap 頁 ---\n%s\n' % b4[:500], flush=True)

        if '沒有存取這項資源的權限' in b4:
            note('送 sitemap', False, '仍未驗證，無法進入 sitemap 頁')
        else:
            filled = False
            try:
                inputs = pg.locator('input[type=text], input:not([type]), input[aria-label]')
                for i in range(await inputs.count()):
                    el = inputs.nth(i)
                    if await el.is_visible():
                        await el.click()
                        await el.fill('sitemap.xml')
                        if 'sitemap' in (await el.input_value() or ''):
                            filled = True
                            break
            except Exception as e:
                print('   填欄位例外 %s' % str(e)[:100], flush=True)
            if filled:
                await click_any(pg, ['提交', 'SUBMIT'])
                await pg.wait_for_timeout(12000)
            await shot(pg, '05_sitemap_done')
            b5 = await btext(pg, 700)
            print('--- 送出後 ---\n%s\n' % b5[:400], flush=True)
            ok5 = any(k in b5 for k in ['成功', 'Success', '已提交', 'sitemap.xml'])
            note('送 sitemap', ok5, b5[:150])

            # ── 3. 請求索引 ───────────────────────────
            for i, u in enumerate(URLS):
                try:
                    insp = ('https://search.google.com/search-console/inspect?resource_id='
                            + ENC + '&id=' + u.replace(':', '%3A').replace('/', '%2F'))
                    await pg.goto(insp, wait_until='domcontentloaded')
                    await pg.wait_for_timeout(20000)
                    await shot(pg, '06_inspect_%d' % i)
                    hit = await click_any(pg, ['要求建立索引', 'REQUEST INDEXING', '要求編入索引'])
                    await pg.wait_for_timeout(22000)
                    await shot(pg, '07_indexed_%d' % i)
                    bt = await btext(pg, 400)
                    note('請求索引 %d' % (i + 1), hit, (u.split('/')[-1] or 'index') + ' | ' + bt[:90])
                except Exception as e:
                    note('請求索引 %d' % (i + 1), False, str(e)[:120])

        print('\n' + '=' * 50, flush=True)
        print(json.dumps(REPORT, ensure_ascii=False, indent=2), flush=True)
        print('=' * 50, flush=True)
        await ctx.close()

asyncio.run(main())
