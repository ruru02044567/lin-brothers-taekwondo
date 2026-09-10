import asyncio, sys, os
from playwright.async_api import async_playwright
sys.stdout.reconfigure(encoding='utf-8')
OUT = r"C:\Users\TUF Gaming\Desktop\我的專案\林家兄弟跆拳道\紀錄\跆協全國賽"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        ctx = await b.new_context(accept_downloads=True, viewport={'width':1280,'height':900})
        pg = await ctx.new_page()
        url = "https://www.tpetkd.org.tw/di-fang-xiao-xi/【競賽組】賽事資訊📣-114年第32屆全國少年跆拳道錦標賽"
        # capture any network responses with pdf
        pdf_urls=[]
        pg.on('response', lambda r: pdf_urls.append(r.url) if ('pdf' in r.url.lower() or 'ugd' in r.url) else None)
        await pg.goto(url, wait_until='domcontentloaded', timeout=60000)
        await pg.wait_for_timeout(6000)
        names = await pg.eval_on_selector_all('[data-hook="file-upload-name"]', 'els=>els.map(e=>e.textContent)')
        print("FILES:", names)
        el = pg.locator('[data-hook="file-upload-name"]').first
        try:
            async with pg.expect_download(timeout=20000) as dl_info:
                await el.click()
            dl = await dl_info.value
            print("DOWNLOAD URL:", dl.url, "suggested:", dl.suggested_filename)
            path = os.path.join(OUT, "test_" + dl.suggested_filename)
            await dl.save_as(path); print("saved", path, os.path.getsize(path))
        except Exception as e:
            print("no download event:", e)
        await pg.wait_for_timeout(3000)
        print("PDF-ish responses:", pdf_urls[:10])
        print("PAGES:", [q.url for q in ctx.pages])
        await b.close()
asyncio.run(main())
