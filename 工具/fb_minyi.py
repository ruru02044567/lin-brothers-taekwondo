# 民逸跆訓 FB 粉專公開貼文抓取（不登入）。headed + 真實 UA，關掉登入牆，捲動，讀 DOM。
import asyncio, json, sys, re, os, time
from datetime import datetime
from playwright.async_api import async_playwright
sys.stdout.reconfigure(encoding='utf-8')
OUT = r"C:\Users\TUF Gaming\Desktop\我的專案\林家兄弟跆拳道\紀錄\民逸跆訓粉專"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
KEYS = ["聖翔","聖宸","聖辰","福山","金牌","冠軍","成績"]
URLS = ["https://www.facebook.com/MINYITKD/","https://www.facebook.com/MINYITKD/posts/","https://www.facebook.com/pg/MINYITKD/posts/"]
LOG = []
def log(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); LOG.append(s)

async def dismiss(pg):
    # 關閉登入牆
    for sel in ['div[role="dialog"] div[aria-label="關閉"]','div[role="dialog"] div[aria-label="Close"]','[aria-label="關閉"]','[aria-label="Close"]']:
        try:
            el = await pg.query_selector(sel)
            if el:
                await el.click(timeout=2000); log("  closed dialog via", sel); await pg.wait_for_timeout(800); return True
        except Exception as e: pass
    # 強制移除 dialog 與 scroll lock
    try:
        await pg.evaluate("""()=>{document.querySelectorAll('div[role="dialog"]').forEach(d=>d.remove());document.querySelectorAll('[data-nosnippet]').forEach(d=>d.remove());document.body.style.overflow='auto';}""")
    except: pass
    return False

async def extract(pg):
    return await pg.evaluate("""()=>{
      const out=[];
      const arts=[...document.querySelectorAll('div[role="article"]')];
      for(const a of arts){
        const t=a.innerText||'';
        if(t.length<20) continue;
        const links=[...a.querySelectorAll('a[href*="/posts/"],a[href*="story_fbid"],a[href*="/photos/"],a[href*="pfbid"]')].map(x=>x.href);
        const imgs=[...a.querySelectorAll('img')].map(i=>i.src).filter(s=>s.includes('scontent'));
        const times=[...a.querySelectorAll('abbr,a[aria-label]')].map(x=>x.getAttribute('aria-label')||x.title||'').filter(Boolean);
        out.push({text:t.slice(0,4000),links:[...new Set(links)].slice(0,5),imgs:[...new Set(imgs)].slice(0,20),times:times.slice(0,5)});
      }
      return out;
    }""")

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled","--lang=zh-TW"])
        ctx = await b.new_context(user_agent=UA, locale="zh-TW", viewport={'width':1280,'height':900})
        pg = await ctx.new_page()
        allposts = {}
        for url in URLS:
            log("== GOTO", url)
            try:
                await pg.goto(url, wait_until="domcontentloaded", timeout=45000)
            except Exception as e:
                log("  goto err", str(e)[:100])
            await pg.wait_for_timeout(4000)
            log("  title:", await pg.title(), "| url:", pg.url)
            await dismiss(pg)
            name = re.sub(r'\W+','_',url)[-40:]
            await pg.screenshot(path=os.path.join(OUT, f"page_{name}.png"))
            n0 = -1
            for i in range(25):
                await pg.mouse.wheel(0, 3000)
                await pg.wait_for_timeout(1800)
                if i % 4 == 0: await dismiss(pg)
                posts = await extract(pg)
                for po in posts:
                    k = po['text'][:120]
                    if k not in allposts: allposts[k] = po
                if len(posts) == n0 and i > 5: 
                    log("  no growth, stop at scroll", i); break
                n0 = len(posts)
            log("  articles so far:", len(allposts))
            html = await pg.content()
            with open(os.path.join(OUT, f"page_{name}.html"), "w", encoding="utf-8") as f: f.write(html)
            # 若整頁含登入字樣且 0 篇，記錄
            if len(allposts) == 0:
                body = await pg.evaluate("()=>document.body.innerText.slice(0,1500)")
                log("  BODY:", body.replace("\n"," | ")[:800])
        # 已知貼文
        known = "https://www.facebook.com/MINYITKD/posts/297365912208789"
        log("== GOTO known", known)
        await pg.goto(known, wait_until="domcontentloaded", timeout=45000); await pg.wait_for_timeout(4000); await dismiss(pg)
        await pg.screenshot(path=os.path.join(OUT, "post_297365912208789.png"), full_page=True)
        with open(os.path.join(OUT, "post_297365912208789.html"), "w", encoding="utf-8") as f: f.write(await pg.content())
        posts = await extract(pg)
        for po in posts:
            po['links'] = po['links'] or [known]
            allposts.setdefault(po['text'][:120], po)
        log("  known post articles:", len(posts), (posts[0]['text'][:200].replace("\n"," / ") if posts else "NONE"))
        # 整理
        result = []
        for po in allposts.values():
            hit = [k for k in KEYS if k in po['text']]
            m = re.search(r'(20\d\d)年(\d{1,2})月(\d{1,2})日', po['text']) or re.search(r'(\d{1,2})月(\d{1,2})日', po['text'])
            result.append({"date_guess": m.group(0) if m else None, "times": po['times'], "keywords": hit, "text": po['text'], "images": po['imgs'], "post_urls": po['links']})
        with open(os.path.join(OUT, "posts.json"), "w", encoding="utf-8") as f: json.dump(result, f, ensure_ascii=False, indent=1)
        log("TOTAL posts:", len(result), "with keywords:", sum(1 for r in result if r['keywords']))
        # 命中的貼文逐篇開、截圖
        for r in result:
            if r['keywords'] and r['post_urls']:
                u = r['post_urls'][0]
                pid = re.sub(r'\W+','_',u.split('facebook.com/')[-1])[:60]
                try:
                    await pg.goto(u, wait_until="domcontentloaded", timeout=45000); await pg.wait_for_timeout(3500); await dismiss(pg)
                    await pg.screenshot(path=os.path.join(OUT, f"hit_{pid}.png"), full_page=True)
                    with open(os.path.join(OUT, f"hit_{pid}.html"), "w", encoding="utf-8") as f: f.write(await pg.content())
                    log("  saved hit", pid, r['keywords'])
                except Exception as e: log("  hit err", pid, str(e)[:80])
        with open(os.path.join(OUT, "_抓取紀錄.txt"), "w", encoding="utf-8") as f: f.write("\n".join(LOG))
        await b.close()
asyncio.run(main())
