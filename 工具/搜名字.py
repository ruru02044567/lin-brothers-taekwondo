# 搜名字.py — 用 pypdf 抽文字，找林聖翔／林聖宸／林聖辰，輸出命中（含頁碼、該行上下文）
import os, re, sys, json
from pypdf import PdfReader
sys.stdout.reconfigure(encoding='utf-8')
D = r"C:\Users\TUF Gaming\Desktop\我的專案\林家兄弟跆拳道\紀錄\跆協全國賽"
NAMES = re.compile(r'林\s*聖\s*[翔宸辰]')
hits, noText = [], []
for fn in sorted(os.listdir(D)):
    if not fn.lower().endswith('.pdf'): continue
    path = os.path.join(D, fn)
    try: r = PdfReader(path)
    except Exception as e: noText.append((fn, f"讀不到 {e}")); continue
    total = 0
    for i, page in enumerate(r.pages, 1):
        try: t = page.extract_text() or ''
        except Exception as e: t = ''
        total += len(t.strip())
        for m in NAMES.finditer(t):
            s = t[max(0,m.start()-120):m.end()+120].replace('\n',' ⏎ ')
            hits.append({"file":fn,"page":i,"name":m.group(0),"ctx":s})
    if total < 50: noText.append((fn, f"無文字層（{len(r.pages)} 頁，抽出 {total} 字）"))
print("=== 命中", len(hits))
for h in hits: print(json.dumps(h, ensure_ascii=False))
print("=== 無文字層／讀不到", len(noText))
for n in noText: print(n)
json.dump({"hits":hits,"noText":noText}, open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"命中結果.json"),'w',encoding='utf-8'), ensure_ascii=False, indent=1)
