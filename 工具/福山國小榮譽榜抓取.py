# -*- coding: utf-8 -*-
"""抓福山國小榮譽榜，找含林聖翔／林聖宸／林聖辰的公告，存 HTML＋附件＋raw.json
用法：python 福山國小榮譽榜抓取.py  (輸出到 紀錄/福山國小榮譽榜/)"""
import re, sys, os, json, html, urllib.parse, time, io
import urllib.request
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = "https://www.fsps.kh.edu.tw"
LIST = BASE + "/view/index.php?WebID=214&MainType=0&SubType=101&MainMenuId=12681&SubMenuId=21164&page={}"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "紀錄", "福山國小榮譽榜")
NAMES = ["林聖翔", "林聖宸", "林聖辰"]
SINCE = "2022/01/01"
UA = {"User-Agent": "Mozilla/5.0"}

def get(url, binary=False):
    for i in range(3):
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30)
            d = r.read()
            return d if binary else d.decode("utf-8", "replace")
        except Exception as e:
            print("  retry", i, url, e); time.sleep(2)
    return None

def strip_tags(s):
    s = re.sub(r"<script.*?</script>|<style.*?</style>", "", s, flags=re.S)
    s = re.sub(r"<br\s*/?>|</p>|</div>|</tr>|</li>", "\n", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    return html.unescape(s)

# 1. 列表
items = []
for p in range(1, 20):
    h = get(LIST.format(p))
    if not h: break
    found = re.findall(r'(\d{4}/\d{2}/\d{2})&nbsp;&nbsp;<a title="[^"]*" href="([^"]*DataId=(\d+)[^"]*)">(.*?)</a>', h, flags=re.S)
    if not found: break
    stop = False
    for date, href, did, title in found:
        title = html.unescape(re.sub(r"\s+", " ", title)).strip()
        if date < SINCE: stop = True; continue
        items.append({"DataId": did, "date": date, "title": title, "url": BASE + html.unescape(href)})
    print(f"page {p}: {len(found)} 則, 累計 {len(items)}, 最舊 {found[-1][0]}")
    if stop: break
print("2022 以後共", len(items), "則")

# 2. 逐則
hits = []
os.makedirs(OUT, exist_ok=True)
for it in items:
    h = get(it["url"])
    if not h: continue
    txt = strip_tags(h)
    matched = [n for n in NAMES if n in txt]
    # 也檢查附件檔名
    if not matched: continue
    it["names"] = matched
    safe = re.sub(r'[\/:*?"<>|]', "_", it["title"])[:60]
    fname = f'{it["DataId"]}_{it["date"].replace("/","")}_{safe}'
    d = os.path.join(OUT, fname); os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "page.html"), "w", encoding="utf-8").write(h)
    # 內文區：抓有名字的段落附近
    # 本文區（ContentMain）與附件：只抓本文區內的連結
    mm = re.search(r'<div class="ContentMain">(.*?)<div class="ContentSign">', h, flags=re.S)
    main = mm.group(1) if mm else ""
    body = strip_tags(main)
    open(os.path.join(d, "page.txt"), "w", encoding="utf-8").write(body)
    it["body"] = body.strip()
    atts = []
    for a in dict.fromkeys(re.findall(r'(?:href|src)="([^"]+)"', main)):
        u = urllib.parse.urljoin(it["url"], html.unescape(a))
        if not re.search(r"\.(jpe?g|png|gif|pdf|docx?|xlsx?|odt|ods|zip)(\?|$)", u, re.I) and "/upload/" not in u and "download" not in u.lower(): continue
        u2 = urllib.parse.quote(u, safe=":/?=&%")
        b = get(u2, binary=True)
        if not b: continue
        an = urllib.parse.unquote(u.split("/")[-1].split("?")[0]) or "attachment"
        an = re.sub(r'[\/:*?"<>|]', "_", an)
        open(os.path.join(d, an), "wb").write(b)
        atts.append({"url": u, "file": os.path.join(d, an), "bytes": len(b)})
    it["dir"] = d; it["attachments"] = atts
    # 文字內容片段（含名字的行）
    it["lines"] = [l.strip() for l in body.splitlines() if any(n in l for n in NAMES)]
    hits.append(it)
    print("HIT", it["DataId"], it["date"], matched, it["title"][:50], "附件", len(atts))

json.dump({"scanned": len(items), "items": items, "hits": hits}, open(os.path.join(OUT, "raw.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("done, hits:", len(hits))
