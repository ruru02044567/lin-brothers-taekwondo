# v3：補開 v1 看到但 v2 沒展開的貼文，合併進 posts.json
import asyncio, json, sys, re, os
from playwright.async_api import async_playwright
sys.stdout.reconfigure(encoding='utf-8')
OUT=r"C:\Users\TUF Gaming\Desktop\我的專案\林家兄弟跆拳道\紀錄\民逸跆訓粉專"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
KEYS=["聖翔","聖宸","聖辰","福山","金牌","冠軍","成績"]
ids=[l.strip() for l in open(os.path.join(OUT,"_todo_ids.txt")) if l.strip()]
async def dismiss(pg):
    try:
        el=await pg.query_selector('div[role="dialog"] div[aria-label="關閉"]')
        if el: await el.click(timeout=1500); await pg.wait_for_timeout(500)
    except: pass
    try: await pg.evaluate("""()=>{document.querySelectorAll('div[role="dialog"]').forEach(d=>d.remove());document.body.style.overflow='auto';}""")
    except: pass
async def main():
    res=json.load(open(os.path.join(OUT,"posts.json"),encoding="utf-8"))
    async with async_playwright() as p:
        b=await p.chromium.launch(headless=False,args=["--disable-blink-features=AutomationControlled","--lang=zh-TW"])
        ctx=await b.new_context(user_agent=UA,locale="zh-TW",viewport={'width':1280,'height':900}); pg=await ctx.new_page()
        for pid in ids:
            url=f"https://www.facebook.com/MINYITKD/posts/{pid}"
            try:
                await pg.goto(url,wait_until="domcontentloaded",timeout=45000); await pg.wait_for_timeout(3000); await dismiss(pg)
                await pg.evaluate("""()=>{for(const el of document.querySelectorAll('div[role="button"],span[role="button"]')){const t=(el.innerText||'').trim();if(t==='查看更多'||t==='See more')el.click();}}"""); await pg.wait_for_timeout(1000)
                posts=await pg.evaluate("""()=>[...document.querySelectorAll('div[role="article"]')].filter(a=>!(a.parentElement&&a.parentElement.closest('div[role="article"]'))).map(a=>({text:a.innerText.slice(0,6000),imgs:[...a.querySelectorAll('img')].map(i=>i.src).filter(s=>s.includes('scontent'))}))""")
                if not posts: print("no article",pid); continue
                m=max(posts,key=lambda x:len(x['text'])); text=m['text']; hit=[k for k in KEYS if k in text]
                tag="hit" if hit else "post"
                await pg.screenshot(path=os.path.join(OUT,f"{tag}_{pid[:40]}.png"),full_page=True)
                open(os.path.join(OUT,f"{tag}_{pid[:40]}.html"),"w",encoding="utf-8").write(await pg.content())
                d=re.search(r'(20\d\d年\d{1,2}月\d{1,2}日|\d{1,2}月\d{1,2}日)',text)
                res.append({"date":d.group(0) if d else None,"keywords":hit,"post_url":url,"text":text,"images":m['imgs'][:20]})
                print("opened",pid[:20],d.group(0) if d else None,hit)
            except Exception as e: print("err",pid[:20],str(e)[:80])
        json.dump(res,open(os.path.join(OUT,"posts.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
        print("TOTAL",len(res))
        await b.close()
asyncio.run(main())
