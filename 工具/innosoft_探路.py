# 探路：開 Innosoft 賽事列表頁，攔所有 API 回應，存到 scratch
import asyncio, json, sys
from playwright.async_api import async_playwright
OUT = sys.argv[1]
URLS = [
 "https://act.innosoft.com.tw/tkd/pages/TkdS.html",
 "https://act.innosoft.com.tw/tkd/pages/b.aspx?page=tkd.html&method=In_Dashboard_MeetingList_light",
]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        ctx = await b.new_context()
        log = []
        async def on_resp(r):
            u = r.url
            if any(k in u for k in ("api","Api","aspx","json")) and "innosoft" in u:
                try:
                    body = await r.text()
                except Exception as e:
                    body = f"<err {e}>"
                log.append({"url":u,"status":r.status,"ct":r.headers.get("content-type",""),"len":len(body),"head":body[:3000]})
        ctx.on("response", on_resp)
        for i,u in enumerate(URLS):
            pg = await ctx.new_page()
            try:
                await pg.goto(u, wait_until="networkidle", timeout=45000)
            except Exception as e:
                print("goto err", u, e)
            await pg.wait_for_timeout(3000)
            html = await pg.content()
            open(f"{OUT}/page{i}.html","w",encoding="utf-8").write(html)
            print(u, "html len", len(html))
        json.dump(log, open(f"{OUT}/api_log.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
        for l in log: print(l["status"], l["len"], l["url"])
        await b.close()
asyncio.run(main())
