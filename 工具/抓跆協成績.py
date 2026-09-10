# 抓跆協成績.py — 用 playwright 掃 tpetkd.org.tw 國內消息（含月份封存頁），找賽事貼文，點擊下載檔名含「成績」的 PDF
import asyncio, json, sys, os, re, time
from urllib.parse import unquote
from playwright.async_api import async_playwright
sys.stdout.reconfigure(encoding='utf-8')
OUT = r"C:\Users\TUF Gaming\Desktop\我的專案\林家兄弟跆拳道\紀錄\跆協全國賽"
LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "下載紀錄.json")
START = "https://www.tpetkd.org.tw/副本-國內消息-113九月份"
KEY = re.compile(r'少年|國小|總統盃|中正盃|青年盃|菁英盃|學總盃|品勢錦標賽|全國.*品勢')
YEAR = re.compile(r'(11[1-5])年')
DEADLINE = time.time() + float(sys.argv[1]) * 60 if len(sys.argv) > 1 else time.time() + 13*60
def sname(s): return re.sub(r'[\/:*?"<>|\s]+', '', s)
def event_name(title):
    for k,v in [('少年','全國少年盃'),('國小','全國國小盃'),('總統盃','總統盃'),('中正盃','中正盃'),('青年盃','青年盃'),('菁英','全國菁英盃'),('學總','學總盃'),('品勢','全國品勢錦標賽')]:
        if k in title: return v
    return sname(title)[:20]
async def main():
    rec = json.load(open(LOG,encoding='utf-8')) if os.path.exists(LOG) else {"posts":{}, "files":[], "fail":[]}
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        ctx = await b.new_context(accept_downloads=True, viewport={'width':1280,'height':900})
        pg = await ctx.new_page()
        async def load(u, scroll=True):
            await pg.goto(u, wait_until='domcontentloaded', timeout=60000)
            await pg.wait_for_timeout(5000)
            if scroll:
                for _ in range(10):
                    await pg.mouse.wheel(0, 5000); await pg.wait_for_timeout(700)
            return await pg.eval_on_selector_all('a[href]', 'els=>els.map(e=>[e.href,e.innerText.trim()])')
        # 1. 收集封存頁
        links = await load(START)
        archives = sorted(set(l[0] for l in links if '%E5%89%AF%E6%9C%AC-%E5%9C%8B%E5%85%A7' in l[0] or '副本-國內消息' in unquote(l[0])))
        archives = [START] + [a for a in archives if a != START]
        print("封存頁數:", len(archives)); [print("  ", unquote(a)) for a in archives]
        posts = {}
        for a in archives:
            if time.time() > DEADLINE: print("TIMEOUT at archives"); break
            try: links = await load(a) if a != START else links
            except Exception as e: print("archive fail", a, e); continue
            for href, txt in links:
                if '/di-fang-xiao-xi/' in href and href not in posts:
                    posts[href] = txt
        print("貼文總數:", len(posts))
        targets = {h:t for h,t in posts.items() if KEY.search(t) or KEY.search(unquote(h))}
        print("目標貼文:", len(targets))
        for h,t in targets.items(): print("  ", t[:60], '|', unquote(h)[-60:])
        # 2. 逐篇下載成績
        for h,t in targets.items():
            if time.time() > DEADLINE: print("TIMEOUT at posts"); rec["fail"].append({"post":unquote(h),"why":"時間到未處理"}); continue
            if h in rec["posts"]: continue
            try: await load(h, scroll=False)
            except Exception as e: rec["fail"].append({"post":unquote(h),"why":f"開頁失敗 {e}"}); continue
            title = (await pg.title()).strip()
            names = await pg.eval_on_selector_all('[data-hook="file-upload-name"]', 'els=>els.map(e=>e.textContent)')
            m = YEAR.search(title) or YEAR.search(unquote(h)); year = m.group(1) if m else 'xxx'
            ev = event_name(title)
            print(f"[{year}] {title[:50]} 檔案{len(names)}: {names}")
            got=[]
            for i,n in enumerate(names):
                if '成績' not in n and '名次' not in n and '排名' not in n: continue
                fn = f"{year}_{ev}_{sname(n)}.pdf"
                dest = os.path.join(OUT, fn)
                if os.path.exists(dest): got.append(fn); continue
                try:
                    async with pg.expect_download(timeout=30000) as di:
                        await pg.locator('[data-hook="file-upload-name"]').nth(i).click()
                    dl = await di.value; await dl.save_as(dest)
                    got.append(fn); rec["files"].append({"file":fn,"size":os.path.getsize(dest),"post":title,"url":dl.url})
                    print("   ✓", fn, os.path.getsize(dest))
                except Exception as e:
                    rec["fail"].append({"post":title,"file":n,"why":str(e)[:100]}); print("   ✗", n, e)
            rec["posts"][h] = {"title":title,"year":year,"files":names,"got":got}
            json.dump(rec, open(LOG,'w',encoding='utf-8'), ensure_ascii=False, indent=1)
        await b.close()
    json.dump(rec, open(LOG,'w',encoding='utf-8'), ensure_ascii=False, indent=1)
    print("DONE files:", len(rec["files"]), "fail:", len(rec["fail"]))
asyncio.run(main())
