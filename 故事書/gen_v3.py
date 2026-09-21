# -*- coding: utf-8 -*-
# 產生 兄弟故事書腳本圖 v3：哥哥頁＋弟弟頁（漫畫版，六參考圖融合＋テコンダー朴式扉頁）
import json, base64, io, pathlib, re, html
from PIL import Image

SCR = pathlib.Path('.')
P = pathlib.Path(r'C:\Users\TUF Gaming\Desktop\我的專案\林家兄弟跆拳道')
D = pathlib.Path(r'C:\Users\TUF Gaming\Desktop\林家兄弟貼圖-傳給爸爸\林家兄弟照片')
data = json.load(open(P / 'docs' / 'data.json', encoding='utf-8'))['獎狀']
inv = json.load(open('inventory.json', encoding='utf-8'))

def b64(path, w, fmt='JPEG', q=76):
    im = Image.open(path)
    if fmt == 'JPEG': im = im.convert('RGB')
    r = w / im.width
    if r < 1: im = im.resize((w, int(im.height * r)), Image.LANCZOS)
    b = io.BytesIO()
    im.save(b, fmt, quality=q, optimize=True) if fmt == 'JPEG' else im.save(b, fmt, optimize=True)
    return 'data:image/%s;base64,' % ('jpeg' if fmt == 'JPEG' else 'png') + base64.b64encode(b.getvalue()).decode()

def short(ev):
    ev = re.sub(r'^(中華民國)?(\d{3}年度?|\d{4}年?)', '', ev)
    ev = re.sub(r'跆拳道錦標賽|全國跆拳道錦標賽|錦標賽', '', ev)
    for a, b in [('暨全國運動會高雄市代表隊選拔賽', ''), ('暨代表隊選拔賽', ''), ('暨原住民選拔賽', ''), ('全國賽暨選拔賽', '全國賽'), ('全國武術功夫暨跆拳道經典賽', '武術功夫經典賽')]:
        ev = ev.replace(a, b)
    return ev.strip(' ・·')

RK = {1: ('1st', 'g'), 2: ('2nd', 's'), 3: ('3rd', 'b'), 4: ('4th', '')}

def recs(who):
    return sorted([r for r in data if r['選手'] == who], key=lambda r: r['日期'])

def stats(rs):
    c = {k: sum(1 for r in rs if r['名次'] == k) for k in (1, 2, 3, 4)}
    nat = sum(1 for r in rs if '全國' in (r['層級'] or ''))
    cities = len(set(r['縣市'] for r in rs if r['縣市'] and '全國' not in r['縣市']))
    return c, nat, cities

def strip8(rs, start):
    out = ''
    for i, r in enumerate(rs[-8:], start=start):
        lab, cls = RK[r['名次']]
        out += f'<figure><img src="{b64(P / "docs" / "images" / (r["id"] + ".jpg"), 300, q=60)}" alt=""><span class="r">{lab}</span><figcaption>第 {i} 話<br>{html.escape(short(r["賽事"])[:12])}<br>{r["日期"][2:].replace("-", "/")}</figcaption></figure>'
    return out

def toc_cards(rs):
    out = ''
    for i, r in enumerate(rs, start=1):
        lab, cls = RK[r['名次']]
        d = r['日期'][2:].split('-')
        out += (f'<div class="ec"><div class="ed"><b>{d[1]}.{d[2]}</b><small>民國 {r["年"]}</small></div>'
                f'<div class="et"><span class="en">第{i}話</span>{html.escape(short(r["賽事"]))}<small>{html.escape(r["項目"])} · {html.escape(r["腰帶"])}{(" · " + r["量級"]) if r["量級"] else ""} · {html.escape(r["層級"] or "")}</small></div>'
                f'<div class="er {cls}">{lab}</div></div>')
    return out

def manga(cfg):
    rs = recs(cfg['who']); c, nat, cities = stats(rs); n = len(rs)
    medals = f"{c[1]} 金 {c[2]} 銀 {c[3]} 銅" + (f" · 第四名 {c[4]}" if c[4] else '')
    ph = {k: b64(v[0], v[1]) for k, v in cfg['photos'].items()}
    st = {k: b64(f'stickers/{cfg["who"]}/{v}.png', 340, 'PNG') for k, v in cfg['stickers'].items()}
    pos = cfg['pos']
    evo = ''
    for i, e in enumerate(cfg['evo']):
        arrow = '<span class="arrow">▶</span>' if i < 2 else ''
        gray = ' style="filter:grayscale(1);opacity:.45"' if e.get('soon') else ''
        evo += f'<div><span class="lv">{e["lv"]}</span><img src="{st[e["stk"]]}" alt=""{gray}><div class="belt {e["belt"]}"></div><b>{e["name"]}</b><small>{e["desc"]}</small>{arrow}</div>'
    rail = ''.join(f'<div class="rl"><b>{a}</b><small>{b}</small></div>' for a, b in [('TOP', 'トップ'), ('PROFILE', 'プロフィール'), ('EPISODES', 'エピソード'), ('FILE', '戦績ファイル'), ('POWER UP', 'パワーアップ'), ('NEXT', '次回予告')])
    return f'''
<div class="manga" style="--c:{cfg['c']};--cd:{cfg['cd']};--cl:{cfg['cl']}">
  <aside class="rail"><div class="rlogo">{cfg['name']}</div>{rail}<div class="rfoot">民逸跆訓<br>逸心聯隊</div></aside>
  <div class="main">
    <div class="tobira">
      <div class="burst"></div><div class="tone"></div>
      <div class="col"><img src="{ph['col1']}" style="object-position:{pos['col1']}" alt=""><img src="{ph['col2']}" style="object-position:{pos['col2']}" alt=""><img src="{ph['col3']}" style="object-position:{pos['col3']}" alt=""></div>
      <img class="hero-stk" src="{st['hero']}" alt="">
      <div class="ttl">
        <div class="kana">{cfg['kana']}</div>
        <div class="cn">{cfg['name']}</div>
        <div class="en">{cfg['en']}</div>
        <div class="tag">{cfg['tagjp']}<small>{cfg['tagcn']}</small></div>
        <div class="credit">原作 <b>林家爸爸</b> ／ 資料 <b>{n} 張獎狀正本</b></div>
      </div>
      <div class="vol">第 1 巻<small>全 {n} 話</small></div>
      <div class="sfx big">{cfg['sfx1']}</div>
    </div>
    <div class="bar"><span>EPISODE 01 – {n:02d}</span><span>{rs[0]['年']} → {rs[-1]['年']}</span><span>{cfg['belts']}</span><span>{medals}</span><span>全國賽 {nat} 場 · {cities} 個縣市</span></div>

    <div class="mp">
      <div class="pn pA"><img class="ph" src="{ph['pA']}" style="object-position:{pos['pA']}" alt=""><div class="bub" style="left:5%;top:6%">{cfg['bubA']}</div><img class="stk" src="{st['pA']}" style="right:-2%;bottom:-3%;width:40%" alt=""><div class="cap">{cfg['capA']}</div></div>
      <div class="pn pB"><img class="ph" src="{ph['pB']}" style="object-position:{pos['pB']}" alt=""><div class="nar" style="right:4%;top:6%"><small>{cfg['narB_jp']}</small>{cfg['narB']}</div><div class="cap">{cfg['capB']}</div></div>
      <div class="pn pC color"><img class="ph" src="{ph['pC']}" style="object-position:{pos['pC']}" alt=""><div class="tone"></div>
        <div class="date"><b>{cfg['bigdate']}</b><small>{cfg['bigdate_sub']}</small></div>
        <div class="sfx" style="left:30%;top:6%;font-size:52px;transform:rotate(-5deg)">{cfg['sfx2']}</div>
        <div class="stamp" style="right:3%;top:6%">{cfg['stampC']}</div>
        <div class="nar" style="left:3%;bottom:11%;max-width:58%"><small>{cfg['narC_jp']}</small>{cfg['narC']}<br><span class="by">── 爸爸的部落格 9/12</span></div>
        <div class="cap">{cfg['capC']}</div></div>
      <div class="pn pD"><img class="stk" src="{st['pD']}" alt=""><div class="bub l" style="right:6%;top:6%;font-size:15px">{cfg['bubD']}</div></div>
      <div class="pn pE"><img class="ph" src="{ph['pE']}" style="object-position:{pos['pE']}" alt=""><div class="sfx" style="right:4%;top:6%;font-size:30px">{cfg['sfx3']}</div><div class="cap">{cfg['capE']}</div></div>
      <div class="pn pF color"><img class="ph" src="{ph['pF']}" style="object-position:{pos['pF']}" alt=""><div class="tone"></div><div class="cap">{cfg['capF']}</div></div>
    </div>

    <div class="file"><span class="h"><i>FILE</i>戰績檔案<small>戦績ファイル · 最近 8 話</small></span><div class="strip8">{strip8(rs, n - 7)}</div></div>
    <div class="evo"><span class="h"><i>POWER UP</i>進化<small>パワーアップ</small></span><div class="evo3">{evo}</div></div>
    <div class="toc"><span class="h"><i>EPISODES</i>全 {n} 話<small>エピソード一覧</small></span><div class="ecs">{toc_cards(rs)}</div></div>
    <div class="next"><div><small>NEXT EPISODE · 次回予告</small><b>下一場，爸爸發文就出現</b></div><div class="go">{cfg['next']}</div></div>
  </div>
</div>'''

XIANG = dict(who='聖翔', name='林聖翔', kana='リン・セイショウ', en='LIN SHENG-XIANG', c='#1e63e9', cd='#0f3f9e', cl='#ffd23f',
    tagjp='黒帯への道', tagcn='黑帶之路', belts='黄帯 → 色帯 → 黒帯', sfx1='ドンッ', sfx2='ドドドド', sfx3='バキッ',
    photos={'col1': (D / '林聖翔' / '808058_0.jpg', 700), 'col2': (D / '林聖翔' / '807995_0.jpg', 700), 'col3': (D / '林聖翔' / '807988_0.jpg', 700),
            'pA': (D / '林聖翔' / '808696.jpg', 700), 'pB': (D / '林聖翔' / '807990_0.jpg', 700), 'pC': ('blogimg/2026-09-12_8.jpg', 900),
            'pE': (D / '林聖翔' / '807982_0.jpg', 600), 'pF': ('blogimg/2026-09-19_5.jpg', 700)},
    pos={'col1': '50% 8%', 'col2': '55% 10%', 'col3': '50% 12%', 'pA': '50% 15%', 'pB': '50% 8%', 'pC': '50% 40%', 'pE': '50% 12%', 'pF': '50% 20%'},
    stickers={'hero': '16', 'pA': '03', 'pD': '09', 'e1': '01', 'e2': '11', 'e3': '16'},
    bubA='出發！', capA='比賽日的早上', narB_jp='112年4月・高雄', narB='第一次站上墊子。<br>黃帶，品勢，第二名。', capB='道服・等待上場',
    bigdate='8.24', bigdate_sub='115 年 · 高雄海青工商 · 大雨', stampC='第一名',
    narC_jp='EPISODE 20', narC='「在高手如雲、容錯率極低的黑帶組，每一場都是意志力與技術的硬仗。」', capC='第 20 話 · 全國理事長盃 · 黑帶組 37 公斤級',
    bubD='讓我來', sfx3_='', capE='獎牌・獎盃・獎狀', capF='115.9.19 台中 · 兄弟一起捧回團體第二',
    evo=[dict(lv='LV.1 · 112 年', stk='e1', belt='y', name='黃帶', desc='1 場 · 市長盃品勢第二名<br>第一次站上墊子'),
         dict(lv='LV.2 · 112～114 年', stk='e2', belt='r', name='色帶', desc='8 場 · 開始打對打<br>議長盃、主委盃、師聖盃連拿第一'),
         dict(lv='LV.3 · 115 年～', stk='e3', belt='k', name='黑帶', desc='11 場 · 全國理事長盃冠軍<br>115 年 1 月升黑帶')],
    next='弟弟 <span>聖宸</span> の物語へ →')

CHEN = dict(who='聖宸', name='林聖宸', kana='リン・セイシン', en='LIN SHENG-CHEN', c='#e63946', cd='#a8202b', cl='#ffd23f',
    tagjp='昇段への道', tagcn='升段之路', belts='黄帯 → 色帯 → ？', sfx1='ズドン', sfx2='ババババ', sfx3='ドガッ',
    photos={'col1': (D / '林聖宸' / '807993_0.jpg', 700), 'col2': (D / '林聖宸' / '807991_0.jpg', 700), 'col3': (D / '林聖宸' / '807994_0.jpg', 700),
            'pA': (D / '林聖宸' / '808794.jpg', 700), 'pB': (D / '林聖宸' / '807989_0.jpg', 700), 'pC': ('blogimg/2026-09-12_9.jpg', 900),
            'pE': (D / '林聖宸' / '808049_0.jpg', 600), 'pF': ('blogimg/2026-09-11_10.jpg', 700)},
    pos={'col1': '50% 10%', 'col2': '50% 10%', 'col3': '50% 8%', 'pA': '50% 15%', 'pB': '50% 12%', 'pC': '50% 40%', 'pE': '50% 10%', 'pF': '50% 15%'},
    stickers={'hero': '15', 'pA': '02', 'pD': '08', 'e1': '03', 'e2': '06', 'e3': '14'},
    bubA='我來了！', capA='比賽日的早上', narB_jp='113年3月・高雄', narB='第一次站上墊子。<br>黃帶，品勢，第四名。<br>從這裡開始。', capB='道服・等待上場',
    bigdate='8.24', bigdate_sub='115 年 · 高雄海青工商 · 大雨', stampC='第一名',
    narC_jp='EPISODE 16', narC='「色帶組的競爭同樣激烈，考驗的是基本功的紮實度與臨場應變。聖宸全場氣勢如虹，以壓倒性的攻勢一路領先。」', capC='第 16 話 · 全國理事長盃 · 色帶組 34 公斤級',
    bubD='第一名！', capE='獎牌・獎狀', capF='兄弟 · 黑帶與紅帶',
    evo=[dict(lv='LV.1 · 113 年', stk='e1', belt='y', name='黃帶', desc='2 場 · 品勢第四名兩次<br>從這裡開始'),
         dict(lv='LV.2 · 113～115 年', stk='e2', belt='r', name='色帶', desc='14 場 · 全國理事長盃色帶組冠軍<br>最新一張獎狀寫紅帶'),
         dict(lv='LV.3 · ？', stk='e3', belt='k', name='黑帶', desc='還沒到<br>升了這格就亮', soon=True)],
    next='哥哥 <span>聖翔</span> の物語へ →')

# 入口橫幅（小樣）
BANNER = f'''
<div class="banner">
  <div class="bh2">☰ &nbsp; 民逸跆訓/林聖翔/林聖宸 跆拳道的生涯 <span>Blogger · Contempo 版型原樣</span></div>
  <div class="bn"><img class="two" src="{b64(D / '兩人合照' / '807985_0.jpg', 700)}" alt="">
    <img class="s1" src="{b64('stickers/聖翔/main.png', 260, 'PNG')}" alt=""><img class="s2" src="{b64('stickers/聖宸/main.png', 260, 'PNG')}" alt="">
    <div class="bt"><small>兄弟の物語</small><b>兩兄弟的故事</b><div class="bb"><span style="background:#1e63e9">聖翔の物語 →</span><span style="background:#e63946">聖宸の物語 →</span></div></div></div>
  <div class="bh2" style="border-top:1px solid #ddd;border-bottom:0">↓ 下面照舊是爸爸的文章列表</div>
</div>'''

t = open('v3_template.html', encoding='utf-8').read()
t = t.replace('{{BOARD_X}}', manga(XIANG)).replace('{{BOARD_C}}', manga(CHEN)).replace('{{BANNER}}', BANNER)
open('兄弟故事書腳本圖.html', 'w', encoding='utf-8').write(t)
open('_mob.html', 'w', encoding='utf-8').write('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">' + t)
print('最終', len(t.encode()) // 1024, 'KB；殘留', re.findall(r'\{\{\w+\}\}', t))
for w in ('聖翔', '聖宸'):
    rs = recs(w); c, nat, ci = stats(rs); print(w, len(rs), c, '全國', nat, '縣市(不含全國協會)', ci)
