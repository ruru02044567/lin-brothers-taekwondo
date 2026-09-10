# 爬 tkdgms.weebly.com（競技比賽資訊網）：走遍所有內頁，收集 uploads 檔案（pdf/xls/doc），下載後全文搜名字。
import requests, re, os, sys, json, time
from urllib.parse import urljoin, unquote
from bs4 import BeautifulSoup
sys.stdout.reconfigure(encoding='utf-8')
OUT = r"C:\Users\TUF Gaming\Desktop\我的專案\林家兄弟跆拳道\紀錄\其他縣市\tkdgms"
os.makedirs(OUT, exist_ok=True)
BASE = "https://tkdgms.weebly.com/"
S = requests.Session(); S.headers["User-Agent"]="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/128 Safari/537.36"
seen=set(); pages={}; files={}
queue=[BASE]
while queue and len(seen)<120:
    u=queue.pop(0)
    if u in seen: continue
    seen.add(u)
    try: r=S.get(u,timeout=20)
    except Exception as e: print("ERR",u,e); continue
    soup=BeautifulSoup(r.text,"html.parser")
    title=soup.title.string.strip() if soup.title else ""
    pages[u]=title
    for a in soup.find_all("a",href=True):
        h=urljoin(u,a["href"]); t=a.get_text(" ",strip=True)
        if "tkdgms.weebly.com" in h and h.endswith(".html") and h not in seen: queue.append(h)
        if "/uploads/" in h or re.search(r'\.(pdf|xlsx?|docx?)(\?|$)',h,re.I) or "drive.google" in h or "docs.google" in h:
            files.setdefault(h,{"text":t,"page":title,"page_url":u})
print("pages",len(pages),"files",len(files))
json.dump({"pages":pages,"files":files},open(os.path.join(OUT,"_index.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
for u,t in pages.items(): print("PAGE",t,"|",u)
