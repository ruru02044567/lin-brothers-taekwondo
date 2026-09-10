# -*- coding: utf-8 -*-
"""Search Console 全自動：新增網站 → 驗證 → 送 sitemap → 請求索引。
中途不問人。每一步截圖。遇到需要放驗證檔就自動處理再回頭驗證。
"""
import asyncio, os, json, re, subprocess, io

PROFILE = os.path.expanduser('~/.config/gsc-playwright')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, 'docs')
OUT = os.path.join(ROOT, '_預覽', 'gsc')
os.makedirs(OUT, exist_ok=True)

SITE = 'https://ruru02044567.github.io/lin-brothers-taekwondo/'
URLS = [
    'https://ruru02044567.github.io/lin-brothers-taekwondo/',
    'https://ruru02044567.github.io/lin-brothers-taekwondo/lin-sheng-xiang.html',
    'https://ruru02044567.github.io/lin-brothers-taekwondo/lin-sheng-chen.html',
]
REPORT = []


def note(step, ok, detail=''):
    REPORT.append({'step': step, 'ok': ok, 'detail': str(detail)[:200]})
    print('[%s] %s | %s' % ('OK  ' if ok else 'FAIL', step, str(detail)[:150]), flush=True)


def sh(cmd):
    r = subprocess.run(cmd, cwd=ROOT, shell=True, capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()


def put_verify_file(fname):
    """把驗證檔寫進 docs 並推上線。"""
    target = os.path.join(DOCS, fname)
    io.open(target, 'w', encoding='utf-8').write('google-site-verification: ' + fname)
    sh('git add "docs/%s"' % fname)
    sh('git commit -q -m "加上 Google Search Console 驗證檔"')
    code, out = sh('git push -q origin main')
    return code == 0, out


async def shot(pg, name):
    try:
        await pg.screenshot(path=os.path.join(OUT, name + '.png'))
    except Exception:
        pass


async def body_text(pg, n=1500):
    try:
        return (await pg.inner_text('body'))[:n]
    except Exception:
        return ''


async def click_text(pg, patterns, timeout=8000):
    """依可見文字點擊元素。"""
    for pat in patterns:
        rx = re.compile(pat)
        for sel in ['button', '[role=button]', 'a', 'span', 'div']:
            try:
                loc = pg.locator(sel).filter(has_text=rx)
                for i in range(min(await loc.count(), 5)):
                    el = loc.nth(i)
                    if await el.is_visible():
                        await el.click(timeout=timeout)
                        return True, pat
            except Exception:
                continue
    return False, None


async def main():
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            PROFILE, headless=False, channel='msedge',
            viewport={'width': 1360, 'height': 960},
            args=['--window-position=40,20'])
        pg = ctx.pages[0] if ctx.pages else await ctx.new_page()
        pg.set_default_timeout(25000)

        # ── 1. 開歡迎頁 ─────────────────────────────────────────
        await pg.goto('https://search.google.com/search-console/welcome',
                      wait_until='domcontentloaded')
        await pg.wait_for_timeout(5000)
        await shot(pg, '01_welcome')
        b = await body_text(pg, 400)
        if 'accounts.google' in pg.url:
            note('登入', False, '未登入')
            print(json.dumps(REPORT, ensure_ascii=False)); await ctx.close(); return
        note('登入', True, pg.url[:60])

        # ── 2. 按「新增網站」叫出輸入框 ─────────────────────────
        ok, which = await click_text(pg, [r'^新增網站$', r'新增網站', r'Add site', r'新增資源'])
        await pg.wait_for_timeout(4000)
        await shot(pg, '02_after_addsite')
        note('按新增網站', ok, which or await body_text(pg, 150))

        # ── 3. 填網址（網址前置字元那欄）────────────────────────
        filled = False
        filled_idx = 0
        try:
            inputs = pg.locator('input[type=text], input:not([type]), input[type=url]')
            n = await inputs.count()
            print('  可見輸入框掃描: 共 %d' % n, flush=True)
            cands = []
            for i in range(n):
                el = inputs.nth(i)
                try:
                    if await el.is_visible():
                        ph = (await el.get_attribute('placeholder')) or ''
                        al = (await el.get_attribute('aria-label')) or ''
                        cands.append((i, ph, al))
                except Exception:
                    pass
            print('  可見的:', cands, flush=True)
            # 優先找 placeholder/aria 含 https 或 網址 的
            order = [i for i, ph, al in cands
                     if 'http' in (ph + al).lower() or '網址' in (ph + al)]
            order += [i for i, _, _ in cands if i not in order]
            for i in order:
                el = inputs.nth(i)
                try:
                    await el.click(timeout=5000)
                    await el.fill(SITE)
                    if SITE[:32] in (await el.input_value()):
                        filled = True
                        filled_idx = i
                        print('  填入 index=%d' % i, flush=True)
                        break
                except Exception:
                    continue
        except Exception as e:
            print('  填入例外:', str(e)[:120], flush=True)
        await shot(pg, '03_filled')
        note('填入網址', filled, SITE if filled else '')
        if not filled:
            print(json.dumps(REPORT, ensure_ascii=False, indent=2))
            await pg.wait_for_timeout(300000); await ctx.close(); return

        # ── 4. 按繼續：用座標點右側卡片裡的按鈕（最可靠）──────────
        ok = False
        try:
            box_in = await inputs.nth(filled_idx).bounding_box()
            print('  輸入框位置 x=%.0f y=%.0f' % (box_in['x'], box_in['y']), flush=True)
            # 找所有寫著「繼續」的元素，挑 x 座標跟輸入框同側（右邊）那顆
            cont = pg.get_by_text('繼續', exact=True)
            cnt = await cont.count()
            print('  找到 %d 個「繼續」' % cnt, flush=True)
            best, bestdx = None, 99999
            for i in range(cnt):
                el = cont.nth(i)
                try:
                    if not await el.is_visible():
                        continue
                    bb = await el.bounding_box()
                    if not bb:
                        continue
                    dx = abs(bb['x'] - box_in['x'])
                    print('    第%d個 x=%.0f y=%.0f dx=%.0f' % (i, bb['x'], bb['y'], dx), flush=True)
                    if bb['y'] > box_in['y'] and dx < bestdx:
                        best, bestdx = bb, dx
                except Exception:
                    continue
            if best:
                cx = best['x'] + best['width'] / 2
                cy = best['y'] + best['height'] / 2
                print('  點擊座標 (%.0f, %.0f)' % (cx, cy), flush=True)
                await pg.mouse.click(cx, cy)
                ok = True
        except Exception as e:
            print('  座標點擊例外:', str(e)[:150], flush=True)
        if not ok:
            try:
                await inputs.nth(filled_idx).press('Enter')
                ok = True
                print('  改用 Enter 送出', flush=True)
            except Exception:
                pass
        await pg.wait_for_timeout(10000)
        await shot(pg, '04_after_continue')
        b = await body_text(pg, 1600)
        note('按繼續', ok, b[:120])
        print('\n--- 驗證畫面全文 ---\n' + b[:900] + '\n', flush=True)

        # ── 5. 驗證 ─────────────────────────────────────────────
        verified = any(k in b for k in ['已驗證擁有權', '驗證成功', 'Ownership verified',
                                        '已驗證所有權', '恭喜'])
        if not verified:
            m = re.search(r'google[0-9a-f]{16}\.html', b)
            if not m:
                await click_text(pg, [r'HTML 檔案', r'HTML file', r'其他驗證方法',
                                      r'MORE WAYS', r'其他驗證選項'])
                await pg.wait_for_timeout(4000)
                b2 = await body_text(pg, 2500)
                await shot(pg, '05_verify_methods')
                m = re.search(r'google[0-9a-f]{16}\.html', b2)
                print('\n--- 驗證方法畫面 ---\n' + b2[:700] + '\n', flush=True)
            if m:
                fname = m.group(0)
                print('>>> 驗證檔名: %s' % fname, flush=True)
                pushed, out = put_verify_file(fname)
                note('放驗證檔', pushed, fname + ' | ' + out[:80])
                if pushed:
                    # 等 Pages 生效
                    for _ in range(20):
                        await pg.wait_for_timeout(15000)
                        code, o = sh('curl -s -o /dev/null -w "%%{http_code}" '
                                     '"https://ruru02044567.github.io/'
                                     'lin-brothers-taekwondo/%s"' % fname)
                        if '200' in o:
                            note('驗證檔上線', True, fname)
                            break
                    else:
                        note('驗證檔上線', False, '等待逾時')
                    ok2, _ = await click_text(pg, [r'^驗證$', r'驗證', r'VERIFY', r'Verify'])
                    await pg.wait_for_timeout(12000)
                    await shot(pg, '06_after_verify')
                    b3 = await body_text(pg, 900)
                    verified = any(k in b3 for k in ['已驗證擁有權', '驗證成功',
                                                     'Ownership verified', '恭喜'])
                    note('按驗證', verified, b3[:150])
            else:
                note('取得驗證檔名', False, '畫面上找不到 googleXXXX.html')
        else:
            note('驗證', True, '自動通過')

        # 關掉可能的成功彈窗
        await click_text(pg, [r'前往資源', r'完成', r'GO TO PROPERTY', r'DONE'])
        await pg.wait_for_timeout(5000)
        await shot(pg, '07_property')

        # ── 6. 送 sitemap ───────────────────────────────────────
        enc = SITE.replace(':', '%3A').replace('/', '%2F')
        try:
            await pg.goto('https://search.google.com/search-console/sitemaps?resource_id=' + enc,
                          wait_until='domcontentloaded')
            await pg.wait_for_timeout(7000)
            await shot(pg, '08_sitemap_page')
            done = False
            inputs = pg.locator('input[type=text], input:not([type])')
            for i in range(await inputs.count()):
                el = inputs.nth(i)
                try:
                    if await el.is_visible():
                        await el.click(); await el.fill('sitemap.xml')
                        done = True; break
                except Exception:
                    continue
            if done:
                await click_text(pg, [r'提交', r'SUBMIT', r'Submit'])
                await pg.wait_for_timeout(8000)
            await shot(pg, '09_sitemap_done')
            note('送 sitemap', done, (await body_text(pg, 250)))
        except Exception as e:
            note('送 sitemap', False, str(e)[:120])

        # ── 7. 請求索引 ─────────────────────────────────────────
        for i, u in enumerate(URLS):
            try:
                insp = ('https://search.google.com/search-console/inspect?resource_id=' + enc
                        + '&id=' + u.replace(':', '%3A').replace('/', '%2F'))
                await pg.goto(insp, wait_until='domcontentloaded')
                await pg.wait_for_timeout(14000)
                await shot(pg, '10_inspect_%d' % i)
                ok3, _ = await click_text(pg, [r'要求建立索引', r'REQUEST INDEXING',
                                               r'Request indexing'])
                await pg.wait_for_timeout(15000)
                await shot(pg, '11_indexed_%d' % i)
                note('請求索引 %d' % (i + 1), ok3, u.split('/')[-1] or 'index')
            except Exception as e:
                note('請求索引 %d' % (i + 1), False, str(e)[:100])

        print('\n' + '=' * 46, flush=True)
        print(json.dumps(REPORT, ensure_ascii=False, indent=2), flush=True)
        print('=' * 46, flush=True)
        await pg.wait_for_timeout(180000)
        await ctx.close()

asyncio.run(main())
