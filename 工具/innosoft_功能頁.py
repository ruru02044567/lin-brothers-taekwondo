# 用 playwright 把每場賽事的功能頁（含組別連結）載完存到 scratch/func_<n>.html
import asyncio, json, sys
from playwright.async_api import async_playwright
S=sys.argv[1]
rows=json.load(open(f"{S}/meetings.json",encoding="utf-8"))
async def one(ctx,i,r):
    pg=await ctx.new_page()
    try:
        await pg.goto(r["link"],wait_until="networkidle",timeout=45000); await pg.wait_for_timeout(1500)
        r["final"]=pg.url; r["func_html"]=f"{S}/func_{i}.html"
        open(r["func_html"],"w",encoding="utf-8").write(await pg.content())
        print(i,"ok",pg.url[-60:],flush=True)
    except Exception as e: print(i,"ERR",e,flush=True); r["final"]=None
    await pg.close()
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(headless=True); ctx=await b.new_context()
        sem=asyncio.Semaphore(5)
        async def g(i,r):
            async with sem: await one(ctx,i,r)
        await asyncio.gather(*[g(i,r) for i,r in enumerate(rows)])
        await b.close()
    json.dump(rows,open(f"{S}/meetings.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
asyncio.run(main())
