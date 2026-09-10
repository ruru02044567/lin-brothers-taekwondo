# v2：捲到 2022、展開「查看更多」、每篇單獨開存全文＋截圖
import asyncio, json, sys, re, os
from playwright.async_api import async_playwright
sys.stdout.reconfigure(encoding='utf-8')
OUT = r"C:\Users\TUF Gaming\Desktop\我的專案\林家兄弟跆拳道\紀錄\民逸跆訓粉專"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
KEYS = ["聖翔","聖宸","聖辰","福山","金牌","冠軍","成績"]
LOG=[]
def log(*a):
    s=" ".join(str(x) for x in a); print(s,flush=True); LOG.append(s)
async def dismiss(pg):
    for sel in ['div[role="dialog"] div[aria-label="關閉"]','div[role="dialog"] div[aria-label="Close"]']:
        try:
            el=await pg.query_selector(sel)
            if el: await el.click(timeout=1500); await pg.wait_for_timeout(500); return
        except: pass
    try: await pg.evaluate("""()=>{document.querySelectorAll('div[role="dialog"]').forEach(d=>d.remove());document.body.style.overflow='auto';}""")
    except: pass
async def expand(pg):
    n=await pg.evaluate("""()=>{let n=0;for(const el of document.querySelectorAll('div[role="button"],span[role="button"]')){const t=(el.innerText||'').trim();if(t==='查看更多'||t==='See more'){el.click();n++;}}return n;}""")
    if n: await pg.wait_for_timeout(1200)
    return n
async def extract(pg):
    return await pg.evaluate("""()=>{
      const out=[];
      for(const a of document.querySelectorAll('div[role="article"]')){
        if(a.closest('div[role="article"]')!==a) {}
        if(a.parentElement && a.parentElement.closest('div[role="article"]')) continue; // 跳過留言（巢狀 article）
        const t=a.innerText||''; if(t.length<20) continue;
        const links=[...a.querySelectorAll('a[href*="/posts/"]')].map(x=>x.href.split('?')[0]);
        const imgs=[...a.querySelectorAll('img')].map(i=>i.src).filter(s=>s.includes('scontent'));
        const times=[...a.querySelectorAll('a[aria-label]')].map(x=>x.getAttribute('aria-label')).filter(Boolean);
        out.push({text:t.slice(0,6000),links:[...new Set(links)].slice(0,3),imgs:[...new Set(imgs)].slice(0,20),times:times.slice(0,4)});
      } return out; }""")
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(headless=False,args=["--disable-blink-features=AutomationControlled","--lang=zh-TW"])
        ctx=await b.new_context(user_agent=UA,locale="zh-TW",viewport={'width':1280,'height':900})
        pg=await ctx.new_page()
        await pg.goto("https://www.facebook.com/MINYITKD/",wait_until="domcontentloaded",timeout=45000)
        await pg.wait_for_timeout(4000); await dismiss(pg)
        allposts={}; stale=0; last=0
        for i in range(120):
            await pg.mouse.wheel(0,2500); await pg.wait_for_timeout(1500)
            if i%3==0: await dismiss(pg); await expand(pg)
            posts=await extract(pg)
            for po in posts:
                k=(po['links'][0] if po['links'] else po['text'][:100])
                if k not in allposts or len(po['text'])>len(allposts[k]['text']): allposts[k]=po
            yrs=re.findall(r'(20\d\d)年',"\n".join(p['text'][:200] for p in posts))
            oldest=min(yrs) if yrs else None
            if len(allposts)==last: stale+=1
            else: stale=0; log(f"  scroll {i}: posts={len(allposts)} oldest={oldest}")
            last=len(allposts)
            if oldest and int(oldest)<=2021: log("reached 2021, stop"); break
            if stale>=12: log("stale 12 rounds, stop at",i); break
        with open(os.path.join(OUT,"feed_full.html"),"w",encoding="utf-8") as f: f.write(await pg.content())
        await pg.screenshot(path=os.path.join(OUT,"feed_bottom.png"))
        log("feed posts:",len(allposts))
        # 每篇單獨開
        result=[]
        for k,po in list(allposts.items()):
            url=po['links'][0] if po['links'] else None
            text=po['text']; imgs=po['imgs']
            if url:
                pid=re.search(r'posts/([^/?]+)',url); pid=pid.group(1)[:40] if pid else re.sub(r'\W','',url)[-30:]
                try:
                    await pg.goto(url,wait_until="domcontentloaded",timeout=45000); await pg.wait_for_timeout(3000); await dismiss(pg); await expand(pg); await pg.wait_for_timeout(800)
                    posts=await extract(pg)
                    if posts:
                        main=max(posts,key=lambda x:len(x['text'])); text=main['text']; imgs=main['imgs'] or imgs
                    hit=[x for x in KEYS if x in text]
                    tag="hit" if hit else "post"
                    await pg.screenshot(path=os.path.join(OUT,f"{tag}_{pid}.png"),full_page=True)
                    with open(os.path.join(OUT,f"{tag}_{pid}.html"),"w",encoding="utf-8") as f: f.write(await pg.content())
                    log("  opened",pid,hit)
                except Exception as e: log("  err",pid,str(e)[:80])
            m=re.search(r'(20\d\d年\d{1,2}月\d{1,2}日|\d{1,2}月\d{1,2}日)',text)
            result.append({"date":m.group(0) if m else None,"keywords":[x for x in KEYS if x in text],"post_url":url,"text":text,"images":imgs})
        json.dump(result,open(os.path.join(OUT,"posts.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
        log("TOTAL",len(result),"hits",sum(1 for r in result if r['keywords']))
        open(os.path.join(OUT,"_抓取紀錄.txt"),"a",encoding="utf-8").write("\n== v2 ==\n"+"\n".join(LOG))
        await b.close()
asyncio.run(main())
