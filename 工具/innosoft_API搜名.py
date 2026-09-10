# 用公開 API 直接搜名字：PlayerInfo(keyword) + RankPlayerList(整場名次)，37 場全跑
import json, sys, re, urllib.request, urllib.parse, concurrent.futures as cf
S, OUT = sys.argv[1], sys.argv[2]
NAMES = ["林聖翔", "林聖宸", "林聖辰"]
rows = json.load(open(f"{S}/meetings.json", encoding="utf-8"))
def post(url, data):
    try:
        req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode(), headers={"User-Agent": "Mozilla/5.0", "X-Requested-With": "XMLHttpRequest"})
        with urllib.request.urlopen(req, timeout=40) as r: return r.read().decode("utf-8", "replace")
    except Exception as e: return f"<err {e}>"
def one(m):
    mid = re.search(r'meeting_id=([0-9A-F]{32})', m.get("final") or "")
    if not mid: return {"meeting": m["text"][:60], "note": "no mid"}
    mid = mid.group(1); res = {"meeting": m["text"][:60], "mid": mid, "playerinfo": {}, "rank_hits": [], "rank_len": 0}
    for n in NAMES:
        b = post(f"https://act.innosoft.com.tw/api/Tkd/PlayerInfo?meeting_id={mid}&keyword={urllib.parse.quote(n)}&muid=", {"meeting_id": mid, "keyword": n})
        res["playerinfo"][n] = {"len": len(b), "hit": n in b, "err": b.startswith("<err")}
        if n in b: open(f"{OUT}/PlayerInfo_{mid[:8]}_{n}.json", "w", encoding="utf-8").write(b)
    b = post("https://act.innosoft.com.tw/api/Tkd/RankPlayerList", {"meeting_id": mid, "group": "weight", "fight_day": "", "org": "", "weight": "", "mode": "", "need_reload": "true"})
    res["rank_len"] = len(b); res["rank_err"] = b.startswith("<err")
    for n in NAMES:
        if n in b:
            res["rank_hits"].append(n); open(f"{OUT}/RankList_{mid[:8]}_{n}.json", "w", encoding="utf-8").write(b)
    return res
out = []
with cf.ThreadPoolExecutor(6) as ex:
    for r in ex.map(one, rows):
        out.append(r); pi = r.get("playerinfo", {})
        print(f"{r['meeting'][:45]} | PI lens={[v['len'] for v in pi.values()]} hits={[k for k,v in pi.items() if v['hit']]} | rank len={r.get('rank_len')} hits={r.get('rank_hits')}", flush=True)
json.dump(out, open(f"{S}/api_search.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
