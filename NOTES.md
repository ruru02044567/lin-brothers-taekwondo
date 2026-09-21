# 林家兄弟跆拳道 專案筆記

最後更新：2026-09-20 10:10 台北

## 2026-09-20 故事書（漫畫版）規劃中，等賢賢定樣子

- **目標**：在爸爸的 Blogger（https://linsheng-xiang.blogspot.com/ ，Contempo 版型，側欄有「網頁」功能但目前零頁）裡開兩個網頁：哥哥、弟弟各一頁，日本熱血運動漫畫風（賢賢丟《テコンダー朴》封面當參考）。
- **腳本圖**：https://claude.ai/artifact/N1Xvnx6ZmgMhnwvgm7FF1z （第 4 版：全彩、無黑白、照片對齊臉；哥哥頁、弟弟頁、入口橫幅）。產生器 `故事書\gen_v3.py`＋`故事書\v3_template.html`，在 scratchpad 跑（要 `inventory.json`、`stickers\`、`blogimg\`，後兩者可由 gen 流程重建）。
- **已定案**：哥哥藍、弟弟紅（跟 9/16 貼圖）；故事文字由 Claude 寫；生活照可上網，但兩張證件照（翔 808053、宸 808052）不放；**黑白照片一律不用**（賢賢：不吉利）；先看樣子再做技術；架上去後可再改。
- **9/20 10:40 賢賢：「其他都交給你」**。四題用預設：扉頁照第 5 版、弟弟黑帶格留「？」、主圖照現版、參考圖維持混搭。他唯一要做的是請爸爸把 ruru02044567@gmail.com 加成 Blogger 管理員（步驟已驗：設定→權限→邀請更多作者→傳送；接受後在名字旁選「管理員」；support.google.com/blogger/answer/42673）。給爸爸的訊息在桌面 `blogger-permission.txt`。
- **2026-09-21 22:xx 已進 Blogger**：賢賢 9/21 20:17 接受邀請（自己的 Edge 按的），爸爸 21:xx 升為管理員。用機器人 Edge（profile `~/.config/blogger-bot-profile`，偵錯埠 9555，`connect_over_cdp`）在 Blogger 開兩個「網頁」並發布：哥哥 https://linsheng-xiang.blogspot.com/p/blog-page.html ，弟弟 https://linsheng-xiang.blogspot.com/p/blog-page_21.html （各 22 張圖全載得到、手機 390 無橫捲，headless 截圖驗過）。「網頁」小工具（PageList1，區塊 page_list_top）加了首頁／聖翔の物語／聖宸の物語三項並開啟顯示，首頁標題下方已出現分頁標籤（桌機截圖看到）。**坑**：Blogger HTML 檢視是 CodeMirror，對可見的 textarea 用 fill 會成功寫進編輯器但 value 讀回是 0，要驗隱藏的 `textarea.Fdco1c`；版面配置的儲存是 `[aria-label="儲存"]` 圖示鈕；Google 拒絕 Playwright 內建 Chromium 登入，要用正版 Edge 開獨立 profile 讓賢賢登入一次。
- **權限到手前 Claude 可先做**：① 樣張改正式頁（去左側欄與 BOARD 框）② 圖片上 GitHub Pages `docs/story/`（生活照公開已授權，兩張證件照不放）③ 橫幅小工具 HTML。權限到手後：Blogger 開兩個網頁貼入、側欄勾選、手機驗收。
- **生圖**：人臉的圖走 GPT。9/20 10:00 Codex image_gen 撞用量上限（9/21 07:45 重置）；本機 ComfyUI check-heavy=HOLD（可用 RAM 1.7 GB）且沒 insightface 做不了像本人。已給賢賢桌面 `manga-prompts.txt` 讓他用 ChatGPT 手動生 3 張，存到桌面 `林家兄弟貼圖-傳給爸爸\生圖樣張\`。
- **貼圖最終版**：桌面 `林家兄弟貼圖-傳給爸爸\林家兄弟貼圖-各16張-解壓後上傳LINE.zip`（9/17 13:50，道具放大＋表情修正版，38 張雜湊全異於 9/16 交付包）。賢賢 9/20 指定只用這版，`貼圖\爸爸交付包` 那套是舊的不要用。編號與文字兩版相同。
- **素材位置**：生活照 36 張在桌面 `林家兄弟貼圖-傳給爸爸\林家兄弟照片\`（翔 17／宸 16／合照 3）；獎狀 `docs\images`；貼圖 `貼圖\爸爸交付包`；爸爸部落格 3 篇＋11 張原圖（feed 可抓 s0 原尺寸）。
- **未驗**：Blogger 網頁貼自訂 HTML 這步沒用爸爸帳號實測；9/19 台中大肚國小理事長盃還沒有獎狀資料。
- **規則**：網站案固定流程（需求→樣子→素材→技術→驗收）寫在記憶 rules/website-workflow-see-before-build.md。
- **2026-09-21 17:38 故事頁上線**（commit 12d2a22，連同 9/14、9/16 兩個未推的本機 commit 一起 push）。
  - 線上：哥哥 https://ruru02044567.github.io/lin-brothers-taekwondo/story/xiang.html 、弟弟 https://ruru02044567.github.io/lin-brothers-taekwondo/story/chen.html （17:4x 兩頁 curl 都 200）；總覽導覽列多了「聖翔の物語」「聖宸の物語」。
  - 產生器：`故事書\build_story.py`（在 scratchpad 跑，讀 gen_v3.py 的 XIANG／CHEN dict 當唯一來源；哥哥大格 pC 換成 s0 原尺寸）。圖片 `docs\story\img\` 46 檔 5.9 MB：照片 17（生活照 13＋合照 1＋部落格原圖 4，長邊 1200、JPEG 82）、貼圖 13（最終版 zip 原尺寸）、獎狀 16。證件照沒放、沒有 base64、沒有灰階照片（17 張 HSV 飽和度最低 0.089）。
  - 給 Blogger 用（權限到手後）：入口橫幅 `docs\story\banner.html`（版面「HTML/JavaScript」小工具）、兩頁片段 `docs\story\blogger-xiang.html`、`blogger-chen.html`（「網頁」HTML 檢視；CSS 全帶 `#lb-story` 前綴、壓成單行、圖片走 GitHub Pages 完整網址）。線上網址同上路徑。
  - 已驗：本機與線上 Playwright 手機 390 寬 scrollWidth＝390、22 張圖無壞連；桌機 1100／手機 390 截圖在 `故事書\_驗收\`（xiang-*、chen-*、live-*）；cv2 臉部偵測主角臉全在可見區；Blogger 片段在模擬干擾 CSS（img 加框、div 加 margin、b 取消粗體）下版面正常。
  - 未驗：真正的 Blogger Contempo 版型沒貼過（沒權限）；Blogger 存檔時「Enter 換行」設定是否會動到片段（已預先壓成單行避開）；弟弟進化格「黑帶」貼圖仍是灰化＋「？」（9/20 賢賢用預設留的，不是照片）；獎狀縮圖也照規格縮到 1200，每頁約 3 MB 圖，手機第一次載會慢一點。


## 2026-09-16 LINE 貼圖（交接給 Codex）

賢賢 9/16 放了 25 張兩兄弟的生活／比賽照，要做兩人各 16 張 LINE 貼圖，畫風沿用 9/14 小嘴版＋跆拳道動漫風。

- **照片**：`照片\林聖翔\`14 張、`照片\林聖宸\`8 張、`照片\兩人合照\`3 張；分類依據獎狀名字＋品勢帶＋臉頰痣，對照圖 `照片\_分類對照.png`。
  賢賢原說道服特寫（807994）是弟弟，證據判定是哥哥，待他確認。**照片不進 git**（.gitignore 已擋）。
- **規劃**：`貼圖\貼圖規劃.html`（畫風、兩人區分、16 句、規格、流程、風險）。
- **交接**：`貼圖\交接給Codex.md`，白板任務 WB-008，負責 codex。生圖走 Codex 的 image_gen，後製沿用 `Desktop\MiniMouth-Intro\LINE貼圖\build_full_pack.py`。
- **待賢賢答**：分類有無錯、弟弟腰帶色（預設紅）、自家用或上架（預設自家用）、16 句要不要換、部落格是哪個。
- **未驗**：提示詞一張沒生過；RAM 12:50 剩 1.96 GB。
- 桌面 `林家兄弟照片` 是 `照片\` 的 junction 分身，給賢賢丟檔用。

## 網站已上線

**https://ruru02044567.github.io/lin-brothers-taekwondo/**

公開網址，任何人拿到連結都打得開，手機可看。三頁：

- 總覽 `/`
- 林聖翔 `/lin-sheng-xiang.html`
- 林聖宸 `/lin-sheng-chen.html`

GitHub repo：https://github.com/ruru02044567/lin-brothers-taekwondo （公開）

**Search Console 已設定完成**（驗證＋sitemap＋三頁索引請求都做完了），
剩下等 Google 實際收錄，見下方進度區。

## Search Console 進度（2026-09-10 21:5x 台北）

**驗證擁有權：已完成 ✅**  帳號 ruru02044567@gmail.com，HTML 檔案驗證通過。

**sitemap：已提交 ✅**  `/lin-brothers-taekwondo/sitemap.xml`
狀態欄顯示「無法擷取」但「上次讀取時間」是空的 —— 這是 Google 還沒去抓的預設值，
不是失敗。sitemap 本身實測 HTTP 200、三個網址格式正確。

**索引請求：三頁全部受理 ✅**
- index（總覽）
- lin-sheng-xiang.html
- lin-sheng-chen.html

### 這輪踩到的四個坑（自動化 Search Console 必看）

1. **`get_by_text('提交')` 會點到左下角的「提交意見」**，不是 sitemap 的提交鈕。
   側邊會滑出「提供意見給 Google」面板蓋住畫面。
   正解：抓輸入框座標，只點「同一列、在它右邊」的按鈕。

2. **驗收不能用關鍵字**：頁面本來就有「sitemap.xml」這幾個字，
   拿它當成功條件等於沒測。正解：讀表格的「共 N 列」。

3. **只填 `sitemap.xml` 會被接到網域根目錄** → `github.io/sitemap.xml`（404）。
   要填含資源路徑的 `lin-brothers-taekwondo/sitemap.xml`。
   兩列都送了，錯的那列刪不掉但不影響。

4. **索引請求會隨機跳「請稍後再試」**，重跑一次就過。要寫重試。

### 相關腳本

- `工具/probe_profiles.py` — 唯讀測各瀏覽器 profile 的登入狀態
- `工具/gsc_confirm.py` — 唯讀查驗證與 sitemap 現況
- `工具/gsc_sm_full.py` — 送 sitemap（已避開提交意見陷阱）
- `工具/gsc_inspect.py` — 三頁網址審查＋請求索引
- `工具/gsc_retry.py` — 單頁索引請求重試

登入用的 profile 是 `~/.config/gsc-playwright`（已登入，headless 可直接用）。

### 還沒完成的部分

Google 實際收錄要等，**2 天到 4 週**，這是 Google 端的時間，本機沒有加速手段。
驗收方式：Google 搜 `site:ruru02044567.github.io/lin-brothers-taekwondo`
或跑 `python -X utf8 工具/check_indexed.py`。

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
├─ 照片/                ← 9/16 生活照 25 張，分聖翔／聖宸／合照（不進 git）
├─ 貼圖/                ← LINE 貼圖規劃與 Codex 交接
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
