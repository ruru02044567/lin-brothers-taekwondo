# -*- coding: utf-8 -*-
"""唯讀診斷：測每個 profile 對 Search Console 的登入狀態。不做任何變更。"""
import asyncio, os, sys
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, '_預覽', 'probe')
os.makedirs(OUT, exist_ok=True)

CANDIDATES = ['gemini-bot-profile', 'chrome-bot-profile', 'gsc-playwright']


async def probe(p, name):
    prof = os.path.expanduser('~/.config/' + name)
    if not os.path.isdir(prof):
        return name, 'NO_PROFILE', ''
    ctx = None
    try:
        ctx = await p.chromium.launch_persistent_context(
            prof, headless=True, channel='msedge',
            viewport={'width': 1280, 'height': 900})
        pg = ctx.pages[0] if ctx.pages else await ctx.new_page()
        pg.set_default_timeout(30000)
        await pg.goto('https://search.google.com/search-console/welcome',
                      wait_until='domcontentloaded')
        await pg.wait_for_timeout(7000)
        url = pg.url
        try:
            body = (await pg.inner_text('body'))[:300].replace('\n', ' ')
        except Exception:
            body = ''
        await pg.screenshot(path=os.path.join(OUT, name + '.png'))
        if 'accounts.google.com' in url or 'ServiceLogin' in url:
            state = 'LOGGED_OUT'
        elif 'search-console' in url:
            state = 'LOGGED_IN'
        else:
            state = 'UNKNOWN'
        return name, state, url[:90] + ' || ' + body[:160]
    except Exception as e:
        return name, 'ERROR', str(e)[:150]
    finally:
        if ctx:
            try:
                await ctx.close()
            except Exception:
                pass


async def main():
    async with async_playwright() as p:
        for name in CANDIDATES:
            n, state, detail = await probe(p, name)
            print('[%-12s] %-11s %s' % (n, state, detail), flush=True)

asyncio.run(main())
