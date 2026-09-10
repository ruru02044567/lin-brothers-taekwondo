# 讓 Google 搜得到 林家兄弟跆拳道

網站已上線，網址是
**https://ruru02044567.github.io/lin-brothers-taekwondo/**

現在任何人拿到這個連結都打得開。但 Google 還不知道它存在，所以搜尋名字還找不到。
下面這幾步要你本人登入 Google 帳號做，我沒有你的密碼，代替不了。

做完之後兩週到一個月會被收錄。這是推的，不是保證。

---

## 我已經做好的部分

- `robots.txt` 明確允許所有搜尋引擎收錄
- `sitemap.xml` 列出三個頁面，附更新日期
- 每頁都有 `canonical` 標記，避免重複網址
- 兩兄弟的頁面各嵌了 schema.org 的 Person 結構化資料，
  裡面寫明姓名、學校、道館、跆拳道選手身分，還有完整獲獎清單
- 頁面標題含全名加「跆拳道」加「福山國小」加「民逸跆訓」

自動通知 Google 的舊管道（ping 端點）在 2023 年已被 Google 停用，
所以下面第二步必須手動送。

---

## 你要做的四步

### 第一步：開啟 Search Console

用電腦瀏覽器開 https://search.google.com/search-console

用你的 Google 帳號登入，就是 ruru02044567@gmail.com 那個。

### 第二步：新增資源

左上角有個下拉選單，點開，選「新增資源」。

會跳出兩個方框，左邊是「網域」，右邊是「網址前置字元」。
**選右邊那個**，左邊那個需要改網域設定，我們用不到。

在右邊的輸入框貼上這一整串，一個字都不要改：

```
https://ruru02044567.github.io/lin-brothers-taekwondo/
```

按「繼續」。

### 第三步：驗證擁有權

因為網址是 github.io 底下的路徑，Google 通常會直接通過，
或是要求你用 Google Analytics、HTML 檔案等方式驗證。

如果它要你下載一個 HTML 檔案放到網站上，把那個檔案存下來，
告訴我檔名，我幫你放進網站再推上去，然後你回去按「驗證」。

### 第四步：送出 sitemap

驗證通過後，左邊選單找到「Sitemap」，
在「新增 Sitemap」的輸入框填：

```
sitemap.xml
```

按「提交」。狀態顯示「成功」就完成了。

### 補一步：手動送出網址（可加快）

左上角有個搜尋框寫著「檢查任何網址」，貼上下面三個網址，
每貼一個，按「要求建立索引」：

```
https://ruru02044567.github.io/lin-brothers-taekwondo/
https://ruru02044567.github.io/lin-brothers-taekwondo/lin-sheng-xiang.html
https://ruru02044567.github.io/lin-brothers-taekwondo/lin-sheng-chen.html
```

每個要等一分鐘左右。這步不是必要，但通常會快一點。

---

## 之後怎麼確認有沒有成功

過一兩週，在 Google 搜尋框打這個：

```
site:ruru02044567.github.io/lin-brothers-taekwondo
```

有結果就代表被收錄了。沒結果就是還在等。

收錄之後，搜「林聖翔 跆拳道」或「林聖宸 民逸跆訓」這種完整關鍵字，
機會不低，因為這組字幾乎只有這個網站有。

但只打「林聖翔」三個字，我不保證排得上第一頁。
同名的有醫師、教授、球員，那些網頁存在很久、被連結很多次，Google 會排前面。

---

## 以後要加新獎狀

拍照傳給我，跟我說要更新林家兄弟的網站，我會：

1. 讀出獎狀內容，加進 `獎狀資料.json`
2. 跑 `python 工具/build_charts.py` 更新圖表
3. 跑 `python 工具/build_site.py` 重新產生三頁
4. 跑 `python 工具/build_seo.py` 更新 sitemap
5. commit 後 push，Pages 會自動重新發布

網址不會變，你朋友那邊重新整理就看得到。

**只有你能更新。** 你朋友點連結只能看，改不了，因為網站在你的 GitHub 帳號底下。

---

## 想收回怎麼辦

跟我說一聲，我可以：

- **改成私人**：網址立刻失效，誰都打不開
- **擋掉 Google**：網址還能傳，但不讓搜尋引擎收錄
- **整個刪掉**：repo 連同網站一起消失

但要注意，Google 收錄之後就算刪掉網站，
快取和第三方轉載可能還留著一段時間，這部分收不回來。
