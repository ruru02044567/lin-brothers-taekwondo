# Innosoft 跆拳道公開對戰表全掃：讀 meetings.json（賽事總表）→ 每場取組別 → 抓每組對戰表 → 搜名字
# 用法：python innosoft_全掃.py <scratch目錄> <輸出目錄>
import re, json, sys, html as H, urllib.request, urllib.parse, concurrent.futures as cf, os, time
S, OUT = sys.argv[1], sys.argv[2]
NAMES = ["林聖翔", "林聖宸", "林聖辰"]
BASE = "https://act.innosoft.com.tw/tkd/pages/"
def get(u, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=40) as r:
                b = r.read(); fu = r.geturl()
            try: return fu, b.decode("utf-8")
            except: return fu, b.decode("big5", "replace")
        except Exception as e:
            time.sleep(1.5)
    return None, ""
def strip(t):
    t = re.sub(r'<script.*?</script>', '', t, flags=re.S); t = re.sub(r'<style.*?</style>', '', t, flags=re.S)
    t = re.sub(r'<[^>]+>', ' ', t); return re.sub(r'\s+', ' ', H.unescape(t))
meetings = json.load(open(f"{S}/meetings.json", encoding="utf-8"))
report = []; hits = []
def do_meeting(m):
    fu = m.get("final"); page = open(m["func_html"], encoding="utf-8").read() if m.get("func_html") else ""
    rec = {"meeting": m["text"], "short": m["link"], "final": fu, "meeting_id": None, "programs": 0, "public": False, "note": ""}
    if not fu: rec["note"] = "打不開"; return rec, []
    mid = re.search(r'meeting_id=([0-9A-F]{32})', fu or "")
    if not mid: rec["note"] = "沒轉到 meeting_id"; return rec, []
    rec["meeting_id"] = mid.group(1)
    if "系統出現錯誤" in page: rec["note"] = "系統出現錯誤"; return rec, []
    progs = []
    for a in re.finditer(r'<a[^>]+href="([^"]*program_id=([0-9A-F]{32})[^"]*)"[^>]*>(.*?)</a>', page, re.S):
        pid = a.group(2); name = strip(a.group(3)).strip()
        if pid not in [p[0] for p in progs]: progs.append((pid, name))
    rec["programs"] = len(progs)
    rec["public"] = len(progs) > 0
    if not progs: rec["note"] = "功能頁沒有組別連結（可能未公開或需登入）"
    found = []
    def do_prog(p):
        pid, pname = p
        u = f"{BASE}b.aspx?page=PublicCompetition.html&method=in_meeting_program_preview&meeting_id={rec['meeting_id']}&program_id={pid}"
        _, ph = get(u)
        if not ph: return None
        txt = strip(ph)
        # 組別全名：頁面標題附近
        title = re.search(r'<title>(.*?)</title>', ph, re.S)
        hh = [n for n in NAMES if n in txt]
        if hh:
            ctxs = {n: [txt[max(0, i-80): i+80] for i in [mm.start() for mm in re.finditer(n, txt)]][:6] for n in hh}
            return {"meeting": m["text"], "meeting_id": rec["meeting_id"], "program_id": pid, "program_anchor": pname, "url": u, "names": hh, "context": ctxs, "html": ph}
        return None
    with cf.ThreadPoolExecutor(6) as ex:
        for r in ex.map(do_prog, progs):
            if r: found.append(r)
    return rec, found
os.makedirs(OUT, exist_ok=True)
with cf.ThreadPoolExecutor(4) as ex:
    for rec, found in ex.map(do_meeting, meetings):
        report.append(rec)
        print(f"[{len(report)}/{len(meetings)}] progs={rec['programs']} hits={len(found)} {rec['note']} {rec['meeting'][:50]}", flush=True)
        for f in found:
            safe = re.sub(r'[\/:*?"<>| ]', '_', f["meeting"][12:60]) + "_" + re.sub(r'[\/:*?"<>| ]', '_', f["program_anchor"])[:30] + "_" + f["program_id"][:8]
            path = os.path.join(OUT, safe + ".html")
            open(path, "w", encoding="utf-8").write(f["html"])
            f["file"] = path; del f["html"]; hits.append(f)
json.dump(report, open(f"{S}/report.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(hits, open(f"{S}/hits.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(hits, open(os.path.join(OUT, "命中清單.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("DONE hits", len(hits))
