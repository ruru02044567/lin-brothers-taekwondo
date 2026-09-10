# 林家兄弟跆拳道 專案筆記

最後更新：2026-09-10 20:15 台北

## 網站已上線

**https://ruru02044567.github.io/lin-brothers-taekwondo/**

公開網址，任何人拿到連結都打得開，手機可看。三頁：

- 總覽 `/`
- 林聖翔 `/lin-sheng-xiang.html`
- 林聖宸 `/lin-sheng-chen.html`

GitHub repo：https://github.com/ruru02044567/lin-brothers-taekwondo （公開）

**Google 收錄還沒完成**，要賢賢本人到 Search Console 送 sitemap，
步驟寫在 `讓Google搜得到.md`。

## 這是什麼

林聖翔（哥哥）、林聖宸（弟弟）兩位福山國小跆拳道隊選手的比賽紀錄網站。
教練鄭逸有是民逸跆訓負責人，部分獎狀的指導教練寫張玄諺。

## 資料來源與數字

**36 張獎狀正本照片**，逐張讀出，比網路能查到的多 23 筆。

| | 場次 | 第一 | 第二 | 第三 | 第四 |
|---|---|---|---|---|---|
| 林聖翔 | 20 | 8 | 8 | 4 | 0 |
| 林聖宸 | 16 | 7 | 5 | 2 | 2 |

- 年份：民國 112 到 115 年
- 縣市：高雄 20、屏東 4、全國協會 4、台中 2、新竹 2、苗栗 2、嘉義 1、新北 1
- 全國級賽事 25 場
- 腰帶：聖翔 黃→色→黑（115 年 1 月升黑帶）；聖宸 黃→色（115 年 6 月一張寫紅帶）

**重要**：網路查到的只有 13 筆，全在高雄。獎狀顯示實際跨 7 個縣市。
原因是市級成績多半不上網，只發到現場、報名系統和道館群組。

## 資料夾結構

```
林家兄弟跆拳道/
├─ 獎狀資料.json        ← 主資料源，36 筆
├─ 原始照片/            ← 36 張原圖（不進 git）
├─ docs/                ← 網站本體，GitHub Pages 根目錄
│  ├─ index.html / lin-sheng-xiang.html / lin-sheng-chen.html
│  ├─ style.css / app.js / data.json
│  ├─ images/           ← 36 張壓縮過的獎狀圖，約 5 MB
│  ├─ sitemap.xml / robots.txt / .nojekyll
│  └─ _charts.py        ← 產生的圖表 SVG（不進 git）
├─ 工具/                ← 所有腳本
├─ 紀錄/                ← 之前爬網路查到的資料（不進 git）
└─ 讓Google搜得到.md    ← 給賢賢的 Search Console 操作指南
```

## 重建網站的四個指令

改完 `獎狀資料.json` 之後依序跑：

```
python -X utf8 工具/build_css.py      # 樣式
python -X utf8 工具/build_charts.py   # 圖表 SVG
python -X utf8 工具/build_site.py     # 三頁 HTML
python -X utf8 工具/build_seo.py      # sitemap + 結構化資料
```

然後 commit + push，Pages 會自動重新發布，網址不變。

驗證用 `python -X utf8 工具/check_live.py`，會用真瀏覽器開線上三頁截圖。

## 網站功能

- 搜尋框：打「屏東」「黑帶」「115」都能篩
- 兩個下拉：賽事層級、名次
- 點任一列開燈箱看獎狀原圖，左右鍵可翻頁，Esc 關閉
- 兩張圖表：獎牌堆疊配腰帶進程、各縣市場次長條
- 手機版測過，390px 寬不會橫向捲動

## 設計決定

深墨底配紙白字，腰帶色當唯一亮點。不用圓角卡片堆疊，改用細線與留白，
因為獎狀本身就是這種版式。紅藍分兩兄弟，跑過 dataviz 的色盲驗證。

## 已知空白

- 113 年道館 FB 有兩則得獎貼文抓不到全文（議長盃、理事長盃）
- 112 年全國少年盃成績是掃描圖檔，本機沒 tesseract 沒 OCR
- 中正盃、學總盃、全國國小盃在學生體總系統，沒查

這些現在意義不大，因為獎狀正本比網路紀錄完整。

## 技術備忘

- GitHub Pages 只認根目錄或 `docs`，所以資料夾叫 docs 不叫 site
- Google 和 Bing 的 sitemap ping 端點都已停用（404 / 410），只能手動送
- 跆協 tpetkd.org.tw 是 Wix，PDF 要用 `[data-hook="file-upload-name"]` 加 expect_download
- Innosoft PlayerInfo API 會回顯關鍵字，判命中要看 `Value.QueryList` 長度
- FB 粉專 headed Playwright 加真實 UA 可讀 DOM，不登入只餵到 2024/09
- 用 heredoc 寫含引號的 CSS/JS 會被 bash 吃掉，改寫成 Python 腳本檔

## 隱私

網站公開了兩個小學生的全名、學校、年級、體重量級和 36 張獎狀照片。
賢賢 9/10 明確要求「開 Google，陌生人也可以找到」。

收回的方式寫在 `讓Google搜得到.md` 最後一段。
Google 收錄後即使刪站，快取和轉載可能仍在。
