# 林家兄弟 LINE 貼圖 — 交接給 Codex

寫於 2026-09-16 13:05 台北。主腦 Claude 做完照片分類與規劃，生圖與後製交給 Codex（你那邊有 image_gen）。
專案根目錄：`C:\Users\TUF Gaming\Desktop\我的專案\林家兄弟跆拳道`，下面路徑都相對於它。

## 目標

哥哥林聖翔、弟弟林聖宸各 16 張 LINE 貼圖。畫風沿用 9/14 你做的小嘴版（大頭身小、半寫實臉、粗描邊平塗），加跆拳道動漫味。
兩個硬要求：看得出是本人；不看文字也分得出誰是哥哥誰是弟弟。

## 先讀（照順序）

1. `貼圖\貼圖規劃.html` — 畫風規格、兩人區分、16 句文字、技術規格、身分證據。用瀏覽器開。
2. `照片\_分類對照.png` — 25 張照片分類結果。
3. `C:\Users\TUF Gaming\Desktop\小嘴 LINE 貼圖成品\32張總覽.png` — 畫風基準，照這個畫。同資料夾 `製作與檢查紀錄.json` 有切格座標與字級。
4. `C:\Users\TUF Gaming\Desktop\MiniMouth-Intro\LINE貼圖\CODEX接手說明.md` — 你 9/14 自己寫的接手說明；同資料夾 `貼圖劇本_32張.md`、`貼圖文案_32張.json` 是小嘴版的劇本與文案格式，這次照同樣格式寫兩份。
5. 後製腳本：`C:\Users\TUF Gaming\Desktop\MiniMouth-Intro\LINE貼圖\build_full_pack.py`。9/14 的呼叫範例在 `C:\Users\TUF Gaming\Documents\Codex\2026-09-14\c-users-tuf-gaming-desktop-minimouth-2\work\build_final.py`（切格用連通區塊＋邊界中性色 flood fill，八格先依 y 再依 x 排序）。字型 `MiniMouth-Intro\LINE貼圖\fonts\NotoSansCJKtc-Bold.otf`。

## 參考照（上傳給 image_gen 用）

| 誰 | 檔案 | 用途 |
|---|---|---|
| 哥哥 林聖翔 | `照片\林聖翔\808058_0.jpg` | 正面最清楚，主參考 |
| | `照片\林聖翔\807994_0.jpg` | 特寫（自拍，左右相反） |
| | `照片\林聖翔\807982_0.jpg` | 全身＋獎盃，身形比例 |
| | `照片\林聖翔\807989_0.jpg` | 吃便當，#14 原型 |
| 弟弟 林聖宸 | `照片\林聖宸\808051_0.jpg` | 正面笑臉，主參考 |
| | `照片\林聖宸\807988_0.jpg` | 比讚大笑，#16 原型 |
| | `照片\林聖宸\807996_0.jpg` | 護具坐姿 |
| | `照片\林聖宸\808049_0.jpg` | 拿獎狀，#08 原型 |

證件照 `808053`（哥）、`808052`（弟）是照臉型推的，信心低，不要當主參考。

## 兩人區分（提示詞一定要寫進去）

**林聖翔（哥哥）**：長橢圓臉、下巴有稜角、眉毛直而粗、表情偏冷靜；右臉頰一顆小痣（正面照在畫面左邊）；**黑領道服＋紅黑品勢帶**；畫略高；個性帥、酷、話少。個人色藍。
**林聖宸（弟弟）**：圓臉、臉頰肉肉、笑起來有酒窩、眼睛笑成彎月；沒有痣、瀏海蓬一點；**白領道服＋紅帶**（腰帶色待賢賢確認，先畫紅）；畫略矮；個性活潑愛笑、動作誇張。個人色紅。
兩人都是黑色鍋蓋頭。

身分證據：獎狀放大讀名字，807982／808057 寫林聖翔、808051 寫林聖宸；807994 腰上紅黑品勢帶（黑帶專用）；長臉有痣那位在 807989／807991／807995／808058 都是同一人。賢賢原本說道服特寫是弟弟，Claude 判定是哥哥，已請賢賢確認。

## 生成方式

- 一次生一張「8 格姿勢表」：4×2、每格全身、中性淺底、格與格留白（方便切）。每人 2 張表 = 16 格。
- 同一個人的 2 張表在**同一段對話**連續生，提示詞只換姿勢區塊，其餘一字不改。
- **先只生哥哥第 1 張表就停**，讓賢賢看像不像、畫風對不對，過了再生其餘 3 張。這一步不要跳。
- 圖上**不畫任何文字**（中文一定亂碼），文字後製疊。道服胸口用素色方塊代替字樣。
- 禁止任何現有動漫角色、招牌服裝、logo。

### 提示詞骨架（英文給 image_gen，姿勢區塊照規劃表 16 句換）

```
Sticker character sheet, 8 panels in a 4x2 grid on plain light grey background, wide gaps between panels, each panel one full-body pose of the SAME boy.
STYLE: chibi caricature, big head small body, about 2.3 heads tall, head is 45% of total height; semi-realistic face based on the reference photos (keep real facial structure, eyes only slightly enlarged); bold clean black outlines, flat cel shading with one shadow tone, no gradients, no realistic lighting; Taiwanese sports-anime energy: speed lines, impact bursts, sweat drops, fire aura where the pose calls for it. No text anywhere. No existing anime characters or logos.
IDENTITY (哥哥): 11-year-old Taiwanese boy, black bowl-cut hair, long oval face, angular chin, thick straight eyebrows, calm cool expression by default, a small mole on his right cheek; white taekwondo dobok with BLACK collar and a red-and-black poom belt; slightly tall.
POSES: 1) ... 2) ... 3) ... 4) ... 5) ... 6) ... 7) ... 8) ...
```
弟弟把 IDENTITY 換成：round face, chubby cheeks, dimples when smiling, crescent smiling eyes, no mole, fluffier fringe; white dobok with WHITE collar and a red belt; slightly shorter; cheerful exaggerated poses.

## 後製與輸出

1. `build_full_pack.py` 切格 → 去背 → 縮到 370×320 內、四邊留 10 px → 疊字（規劃表的 16 句，Noto Sans CJK TC Bold）→ 每張 ≤ 1 MB。
2. 每人一個 `main.png`（240×240）、`tab.png`（96×74）、16 張 PNG、一個 zip、16 格總覽、深底／淺底預覽。
3. 輸出到 `貼圖\林聖翔\` 與 `貼圖\林聖宸\`；兩人並排一張 `貼圖\兩人總覽.png`。
4. 總覽圖各複製一份到桌面，純英文檔名：`lin-xiang-stickers.png`、`lin-chen-stickers.png`（賢賢要能直接點）。

## 完成條件（可驗）

- `貼圖\林聖翔\PNG\01.png` … `16.png` 與 `貼圖\林聖宸\PNG\01.png` … `16.png`，各 16 張，尺寸 ≤ 370×320、透明底、≤ 1 MB。
- `貼圖\兩人總覽.png` 存在，32 格並排。
- 賢賢看總覽，不看文字能分出誰是誰；像不像由他拍板（visual 型：看過、操作過、比過三勾）。
- 回報：動了哪些檔、生成幾輪、哪幾格重生過、哪幾格自己覺得不像。

## 禁區

- 不動 `docs\`（上線網站）、`獎狀資料.json`、`工具\`、`.git`。
- 照片不進 git（`.gitignore` 已擋 `照片/`）；照片只上傳給 image_gen，不傳到其他服務；不對外發布。
- 不刪任何檔；不花錢。
- 全部 32 張做完前不要 commit 貼圖成品；只 commit 文件。

## 待賢賢回答（沒回覆就照預設做）

1. 分類對照圖有沒有分錯 — 預設沒錯。
2. 弟弟腰帶顏色 — 預設紅帶。
3. 自家用還是上架賣 — 預設自家用（上架要家長同意）。
4. 16 句文字 — 預設規劃表。

## 已驗／未驗

- 已驗：兩人身分（獎狀名字）、25 張分類、規劃頁能開。
- 未驗：畫風提示詞一張都還沒生過；小嘴版 `build_full_pack.py` 對新圖的切格是否直接可用。
- 環境：2026-09-16 12:50 RAM 剩 1.96 GB，生圖前先確認 > 3 GB（Steam 700 MB、ChatGPT 桌面版 1.76 GB 可關）。
