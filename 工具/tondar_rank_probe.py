# 掃 tondar-cn.com 成績查詢頁 EventNo 1..70，存 HTML，搜名字
import requests, os, sys, re, json
from bs4 import BeautifulSoup
sys.stdout.reconfigure(encoding='utf-8')
OUT=r"C:\Users\TUF Gaming\Desktop\我的專案\林家兄弟跆拳道\紀錄\其他縣市\tondar成績"
os.makedirs(OUT,exist_ok=True)
NAMES=["林聖翔","林聖宸","林聖辰","民逸","福山"]
S=requests.Session(); S.headers["User-Agent"]="Mozilla/5.0"
rep=[]
for n in range(1,71):
    u=f"https://www.tondar-cn.com/Competition/Rank.php?EventNo={n}"
    try: r=S.get(u,timeout=20); r.encoding=r.apparent_encoding or "utf-8"
    except Exception as e: print(n,"ERR",e); continue
    soup=BeautifulSoup(r.text,"html.parser"); t=soup.get_text(" ",strip=True)
    title=(soup.title.string.strip() if soup.title and soup.title.string else "")
    h=re.search(r'(1\d\d\s*年[^ ]{0,40}(錦標賽|選拔賽|盃))',t)
    hits={k:t.count(k) for k in NAMES if k in t}
    forms=[(f.get("action"),[i.get("name") for i in f.find_all(["input","select"])]) for f in soup.find_all("form")]
    sel={s.get("name"):[o.get_text(strip=True) for o in s.find_all("option")][:15] for s in soup.find_all("select")}
    print(n,"|",title[:40],"|",h.group(1) if h else "-","| len",len(t),"| hits",hits,"| selects",list(sel.keys())[:5])
    open(os.path.join(OUT,f"rank_{n}.html"),"w",encoding="utf-8").write(r.text)
    rep.append({"EventNo":n,"title":title,"event":h.group(1) if h else None,"len":len(t),"hits":hits,"forms":forms,"selects":sel})
json.dump(rep,open(os.path.join(OUT,"_probe.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
