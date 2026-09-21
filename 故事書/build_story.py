# -*- coding: utf-8 -*-
"""
從 gen_v3.py 的定稿設定（XIANG／CHEN 兩個 dict）產出正式頁：
  docs/story/xiang.html、chen.html      獨立頁（無 rail、無 board）
  docs/story/img/*                       只放用到的照片／貼圖／獎狀
  docs/story/banner.html                 入口橫幅片段（貼 Blogger 首頁 HTML 小工具）
  docs/story/blogger-xiang.html、-chen   貼 Blogger「網頁」HTML 檢視的片段
用法：在 scratchpad（有 stickers/、blogimg/）跑 python build_story.py
"""
import json, re, html, pathlib, shutil, sys
from PIL import Image, ImageOps

P = pathlib.Path(r'C:\Users\TUF Gaming\Desktop\我的專案\林家兄弟跆拳道')
D = pathlib.Path(r'C:\Users\TUF Gaming\Desktop\林家兄弟貼圖-傳給爸爸\林家兄弟照片')
STORY = P / 'docs' / 'story'
IMG = STORY / 'img'
SITE = 'https://ruru02044567.github.io/lin-brothers-taekwondo/'
BLOG = 'https://linsheng-xiang.blogspot.com/'
FORBID = {'808053_0.jpg', '808052_0.jpg'}          # 證件照絕對不放
FONTS = 'https://fonts.googleapis.com/css2?family=Dela+Gothic+One&family=Noto+Sans+TC:wght@400;500;700;900&family=Noto+Serif+TC:wght@700;900&display=swap'

data = json.load(open(P / 'docs' / 'data.json', encoding='utf-8'))['獎狀']

# ---- 從 gen_v3.py 抽 XIANG / CHEN 兩個 dict（唯一來源，不另抄一份）----
src = open(P / '故事書' / 'gen_v3.py', encoding='utf-8').read()
m = re.search(r'^(XIANG = dict\(.*?)\n\n(CHEN = dict\(.*?)\n\n# 入口橫幅', src, re.S | re.M)
ns = {'D': D, 'pathlib': pathlib}
exec(m.group(1) + '\n' + m.group(2), ns)
XIANG, CHEN = ns['XIANG'], ns['CHEN']
# 大格 pC 哥哥那張原本是 325px 縮圖，換成 s0 原尺寸（同一張、blog 9/12 第 8 張）
XIANG['photos']['pC'] = ('blogimg/2026-09-12_8_s0.jpg', 900)

# ---- 跟 gen_v3.py 一樣的輔助 ----
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

# ---- 圖片輸出 ----
USED = []   # (分類, 來源, 輸出)

def photo(srcpath, name, long=1200, q=82):
    srcpath = pathlib.Path(srcpath)
    assert srcpath.name not in FORBID, f'證件照不准放：{srcpath}'
    im = ImageOps.exif_transpose(Image.open(srcpath)).convert('RGB')
    r = long / max(im.size)
    if r < 1:
        im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    out = IMG / name
    im.save(out, 'JPEG', quality=q, optimize=True, progressive=True)
    USED.append(('照片' if 'cert' not in name else '獎狀', str(srcpath), name))
    return 'img/' + name

def sticker(who, num, name):
    srcpath = pathlib.Path('stickers') / who / f'{num}.png'
    shutil.copyfile(srcpath, IMG / name)
    USED.append(('貼圖', str(srcpath), name))
    return 'img/' + name

def strip8(rs, start, pfx):
    out = ''
    for i, r in enumerate(rs[-8:], start=start):
        lab, cls = RK[r['名次']]
        s = photo(P / 'docs' / 'images' / (r['id'] + '.jpg'), f'{pfx}-cert-{r["id"]}.jpg')
        out += f'<figure><img src="{s}" alt="第 {i} 話獎狀" loading="lazy"><span class="r">{lab}</span><figcaption>第 {i} 話<br>{html.escape(short(r["賽事"])[:12])}<br>{r["日期"][2:].replace("-", "/")}</figcaption></figure>'
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

def manga(cfg, pfx, next_href):
    rs = recs(cfg['who']); c, nat, cities = stats(rs); n = len(rs)
    medals = f"{c[1]} 金 {c[2]} 銀 {c[3]} 銅" + (f" · 第四名 {c[4]}" if c[4] else '')
    names = {'col1': 'hero-1', 'col2': 'hero-2', 'col3': 'hero-3', 'pA': 'panel-a', 'pB': 'panel-b', 'pC': 'panel-c', 'pE': 'panel-e', 'pF': 'panel-f'}
    ph = {k: photo(v[0], f'{pfx}-{names[k]}.jpg') for k, v in cfg['photos'].items()}
    st = {k: sticker(cfg['who'], v, f'{pfx}-stk-{v}.png') for k, v in cfg['stickers'].items()}
    pos = cfg['pos']; nm = cfg['name']
    evo = ''
    for i, e in enumerate(cfg['evo']):
        arrow = '<span class="arrow">▶</span>' if i < 2 else ''
        gray = ' style="filter:grayscale(1);opacity:.45"' if e.get('soon') else ''
        evo += f'<div><span class="lv">{e["lv"]}</span><img src="{st[e["stk"]]}" alt="{nm} 貼圖" loading="lazy"{gray}><div class="belt {e["belt"]}"></div><b>{e["name"]}</b><small>{e["desc"]}</small>{arrow}</div>'
    body = f'''<div class="manga" style="--c:{cfg['c']};--cd:{cfg['cd']};--cl:{cfg['cl']}">
<div class="main">
<div class="tobira">
<div class="burst"></div><div class="tone"></div>
<div class="col"><img src="{ph['col1']}" style="object-position:{pos['col1']}" alt="{nm}"><img src="{ph['col2']}" style="object-position:{pos['col2']}" alt="{nm}"><img src="{ph['col3']}" style="object-position:{pos['col3']}" alt="{nm}"></div>
<img class="hero-stk" src="{st['hero']}" alt="{nm} 貼圖">
<div class="ttl">
<div class="kana">{cfg['kana']}</div>
<div class="cn">{nm}</div>
<div class="en">{cfg['en']}</div>
<div class="tag">{cfg['tagjp']}<small>{cfg['tagcn']}</small></div>
<div class="credit">原作 <b>林家爸爸</b> ／ 資料 <b>{n} 張獎狀正本</b></div>
</div>
<div class="vol">第 1 巻<small>全 {n} 話</small></div>
<div class="sfx big">{cfg['sfx1']}</div>
</div>
<div class="bar"><span>EPISODE 01 – {n:02d}</span><span>{rs[0]['年']} → {rs[-1]['年']}</span><span>{cfg['belts']}</span><span>{medals}</span><span>全國賽 {nat} 場 · {cities} 個縣市</span></div>
<div class="mp">
<div class="pn pA"><img class="ph" src="{ph['pA']}" style="object-position:{pos['pA']}" alt="{nm}・{cfg['capA']}"><div class="bub" style="left:5%;top:6%">{cfg['bubA']}</div><img class="stk" src="{st['pA']}" style="right:-2%;bottom:-3%;width:40%" alt=""><div class="cap">{cfg['capA']}</div></div>
<div class="pn pB"><img class="ph" src="{ph['pB']}" style="object-position:{pos['pB']}" alt="{nm}・{cfg['capB']}"><div class="nar" style="right:4%;top:6%"><small>{cfg['narB_jp']}</small>{cfg['narB']}</div><div class="cap">{cfg['capB']}</div></div>
<div class="pn pC color"><img class="ph" src="{ph['pC']}" style="object-position:{pos['pC']}" alt="{nm}・{cfg['capC']}" loading="lazy"><div class="tone"></div>
<div class="date"><b>{cfg['bigdate']}</b><small>{cfg['bigdate_sub']}</small></div>
<div class="sfx" style="left:30%;top:6%;font-size:52px;transform:rotate(-5deg)">{cfg['sfx2']}</div>
<div class="stamp" style="right:3%;top:6%">{cfg['stampC']}</div>
<div class="nar" style="left:3%;bottom:11%;max-width:58%"><small>{cfg['narC_jp']}</small>{cfg['narC']}<br><span class="by">── 爸爸的部落格 9/12</span></div>
<div class="cap">{cfg['capC']}</div></div>
<div class="pn pD"><img class="stk" src="{st['pD']}" alt="{nm} 貼圖" loading="lazy"><div class="bub l" style="right:6%;top:6%;font-size:15px">{cfg['bubD']}</div></div>
<div class="pn pE"><img class="ph" src="{ph['pE']}" style="object-position:{pos['pE']}" alt="{cfg['capE']}" loading="lazy"><div class="sfx" style="right:4%;top:6%;font-size:30px">{cfg['sfx3']}</div><div class="cap">{cfg['capE']}</div></div>
<div class="pn pF color"><img class="ph" src="{ph['pF']}" style="object-position:{pos['pF']}" alt="{cfg['capF']}" loading="lazy"><div class="tone"></div><div class="cap">{cfg['capF']}</div></div>
</div>
<div class="file"><span class="h"><i>FILE</i>戰績檔案<small>戦績ファイル · 最近 8 話</small></span><div class="strip8">{strip8(rs, n - 7, pfx)}</div></div>
<div class="evo"><span class="h"><i>POWER UP</i>進化<small>パワーアップ</small></span><div class="evo3">{evo}</div></div>
<div class="toc"><span class="h"><i>EPISODES</i>全 {n} 話<small>エピソード一覧</small></span><div class="ecs">{toc_cards(rs)}</div></div>
<div class="next"><div><small>NEXT EPISODE · 次回予告</small><b>下一場，爸爸發文就出現</b></div><a class="go" href="{next_href}">{cfg['next']}</a></div>
</div>
</div>
<footer class="lb-foot">原文出處：<a href="{BLOG}" target="_blank" rel="noopener">爸爸的部落格</a><span class="sep">·</span><a href="../index.html">回總覽</a></footer>'''
    meta = dict(n=n, c=c, nat=nat, cities=cities, y0=rs[0]['年'], y1=rs[-1]['年'], hero='img/' + f'{pfx}-hero-1.jpg')
    return body, meta

# ---- CSS：模板的漫畫段（去 rail，manga 改 block）＋頁面殼 ----
tpl = open(P / '故事書' / 'v3_template.html', encoding='utf-8').read()
css_all = re.search(r'<style>(.*?)</style>', tpl, re.S).group(1)
manga_css = css_all[css_all.index('/* ===== 漫畫頁'):]
manga_css = manga_css.replace('.manga{display:grid;grid-template-columns:150px 1fr;', '.manga{display:block;')
manga_css = re.sub(r'\n\.rail\{.*?\}\n\.rlogo\{.*?\}\n\.rl b\{.*?\}\n\.rl small\{.*?\}\n\.rfoot\{.*?\}', '', manga_css, flags=re.S)
manga_css = manga_css.replace('  .manga{grid-template-columns:1fr}.rail{display:none}\n', '')
manga_css = manga_css.replace('.next .go{', '.next .go{text-decoration:none;display:inline-block;')
manga_css = manga_css.replace('.next .go span{color:var(--cl)}', '.next .go span{color:var(--cl)}\n.next .go:hover{background:#fff;color:#111}.next .go:hover span{color:var(--cd)}')
manga_css = manga_css.replace('  .bn{height:240px}.bn .s1,.bn .s2{width:90px}.bt b{font-size:24px}\n', '  .next{grid-template-columns:1fr}\n')
assert '.rail' not in manga_css and '.bn{' not in manga_css, '殘留 rail/banner 規則'
banner_css = css_all[css_all.index('/* ===== 入口橫幅'):css_all.index('/* ===== 漫畫頁')]

shell_css = '''*{box-sizing:border-box}
html{background:#1b1b1b}
body{margin:0;padding:0 0 32px;background:#1b1b1b;color:#111;font-family:"Noto Sans TC","PingFang TC","Microsoft JhengHei",system-ui,sans-serif;font-size:16px;line-height:1.5;-webkit-text-size-adjust:100%}
.lb-story{max-width:960px;margin:0 auto}
.lb-foot{color:#bbb;font-size:13px;padding:14px 16px;text-align:center;line-height:1.8}
.lb-foot a{color:#fff;text-decoration:underline;text-underline-offset:3px}
.lb-foot .sep{margin:0 10px;color:#666}
@media (min-width:961px){.lb-story{margin-top:24px}}
'''

def page(cfg, pfx, fname, next_href, title, desc):
    body, mt = manga(cfg, pfx, next_href)
    head = f'''<!doctype html>
<html lang="zh-Hant-TW">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="article">
<meta property="og:image" content="{SITE}story/{mt['hero']}">
<meta property="og:url" content="{SITE}story/{fname}">
<meta name="robots" content="index,follow">
<link rel="canonical" href="{SITE}story/{fname}">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<style>
{shell_css}{manga_css}</style>
</head>
<body>
<main class="lb-story" id="lb-story">
'''
    full = head + body + '\n</main>\n</body>\n</html>\n'
    (STORY / fname).write_text(full, encoding='utf-8')
    return body, mt

# ---- Blogger 片段：CSS 全部加 #lb-story 前綴、圖片與連結改完整網址、壓成單行（Blogger 會把換行變 <br>）----
def prefix_css(css, pfx):
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    out = []
    i = 0
    def rules(block):
        res = ''
        for mm in re.finditer(r'([^{}]+)\{([^{}]*)\}', block):
            sels = [s.strip() for s in mm.group(1).split(',') if s.strip()]
            res += ','.join(f'{pfx} {s}' for s in sels) + '{' + mm.group(2).strip() + '}'
        return res
    pos = 0
    while True:
        j = css.find('@media', pos)
        if j < 0:
            out.append(rules(css[pos:])); break
        out.append(rules(css[pos:j]))
        k = css.index('{', j)
        depth, e = 1, k + 1
        while depth:
            depth += {'{': 1, '}': -1}.get(css[e], 0); e += 1
        out.append(css[j:k].strip() + '{' + rules(css[k + 1:e - 1]) + '}')
        pos = e
    return ''.join(out)

def blogger_fragment(body, fname):
    css = prefix_css(shell_css.split('\n', 2)[2] + manga_css, '#lb-story')   # 丟掉 * 與 html 兩條，換成容器規則
    css = ('#lb-story *{box-sizing:border-box}#lb-story{max-width:960px;margin:0 auto;background:#1b1b1b;color:#111;font-family:"Noto Sans TC","PingFang TC","Microsoft JhengHei",system-ui,sans-serif;font-size:16px;line-height:1.5;padding:0 0 8px}'
           '#lb-story div,#lb-story figure,#lb-story figcaption,#lb-story span,#lb-story small,#lb-story b,#lb-story i,#lb-story img,#lb-story a,#lb-story main,#lb-story footer{margin:0;padding:0;border:0;background:none;box-shadow:none;text-align:left;font-size:inherit;line-height:inherit;font-weight:inherit}'
           '#lb-story img{max-width:none;display:inline-block;vertical-align:middle;width:auto;height:auto}#lb-story b{font-weight:900}#lb-story a{border:0;background:none}' + css)
    b = body.replace('src="img/', f'src="{SITE}story/img/').replace('href="../index.html"', f'href="{SITE}index.html"')
    b = re.sub(r'href="(xiang|chen)\.html"', lambda m: f'href="{SITE}story/{m.group(1)}.html"', b)
    b = re.sub(r'\n\s*', '', b)
    frag = (f'<!-- 林家兄弟故事頁（漫畫版）：整段貼進 Blogger「網頁」的 HTML 檢視。圖片放在 GitHub Pages。來源 {SITE}story/{fname} -->'
            f'<style>@import url("{FONTS}");{css}</style>'
            f'<div id="lb-story">{b}</div>')
    (STORY / ('blogger-' + fname)).write_text(frag, encoding='utf-8')

# ---- 入口橫幅片段 ----
def banner():
    two = photo(D / '兩人合照' / '807985_0.jpg', 'b-two.jpg')
    s1 = sticker('聖翔', 'main', 'x-stk-main.png'); s2 = sticker('聖宸', 'main', 'c-stk-main.png')
    css = prefix_css(banner_css, '#lb-banner')
    css = ('#lb-banner *{box-sizing:border-box}#lb-banner{font-family:"Noto Sans TC","PingFang TC","Microsoft JhengHei",system-ui,sans-serif;line-height:1.4}'
           '#lb-banner div,#lb-banner span,#lb-banner small,#lb-banner b,#lb-banner img,#lb-banner a{margin:0;padding:0;border:0;background:none;box-shadow:none;font-size:inherit;line-height:inherit;font-weight:inherit}'
           '#lb-banner img{max-width:none;width:auto;height:auto;display:inline-block}#lb-banner b{font-weight:900}#lb-banner a{text-decoration:none}'
           '#lb-banner .bb a{display:inline-block;color:#fff;font-weight:900;padding:6px 14px;transform:skew(-10deg);font-size:14px;box-shadow:3px 3px 0 #111;text-shadow:none}'
           '#lb-banner .bb a:hover{filter:brightness(1.12)}'
           '@media (max-width:820px){#lb-banner .bn{height:240px}#lb-banner .bn .s1,#lb-banner .bn .s2{width:90px}#lb-banner .bt b{font-size:24px}}' + css)
    b = (f'<div class="banner"><div class="bn"><img class="two" src="{SITE}story/{two}" alt="林聖翔 林聖宸 兩兄弟">'
         f'<img class="s1" src="{SITE}story/{s1}" alt=""><img class="s2" src="{SITE}story/{s2}" alt="">'
         f'<div class="bt"><small>兄弟の物語</small><b>兩兄弟的故事</b><div class="bb">'
         f'<a href="{SITE}story/xiang.html" style="background:#1e63e9">聖翔の物語 →</a>'
         f'<a href="{SITE}story/chen.html" style="background:#e63946">聖宸の物語 →</a></div></div></div></div>')
    frag = (f'<!-- 林家兄弟故事入口橫幅：貼進 Blogger 版面「HTML/JavaScript」小工具，放標題下方。圖片在 GitHub Pages。-->'
            f'<style>@import url("{FONTS}");{css}</style><div id="lb-banner">{b}</div>')
    (STORY / 'banner.html').write_text(frag, encoding='utf-8')

# ---- 跑 ----
if __name__ == '__main__':
    if IMG.exists(): shutil.rmtree(IMG)
    IMG.mkdir(parents=True)
    rx = recs('聖翔'); cx, natx, cix = stats(rx)
    rc = recs('聖宸'); cc, natc, cic = stats(rc)
    bx, mx = page(XIANG, 'x', 'xiang.html', 'chen.html',
                  '林聖翔の物語：黑帶之路｜林家兄弟跆拳道',
                  f'哥哥林聖翔的跆拳道故事，漫畫版。從民國 {rx[0]["年"]} 年黃帶第一次站上墊子，到 {rx[-1]["年"]} 年升黑帶、拿下全國理事長盃冠軍：{len(rx)} 張獎狀正本、全 {len(rx)} 話，{cx[1]} 金 {cx[2]} 銀 {cx[3]} 銅。')
    bc, mc = page(CHEN, 'c', 'chen.html', 'xiang.html',
                  '林聖宸の物語：升段之路｜林家兄弟跆拳道',
                  f'弟弟林聖宸的跆拳道故事，漫畫版。從民國 {rc[0]["年"]} 年黃帶品勢第四名起步，到 {rc[-1]["年"]} 年全國理事長盃色帶組冠軍：{len(rc)} 張獎狀正本、全 {len(rc)} 話，{cc[1]} 金 {cc[2]} 銀 {cc[3]} 銅。')
    blogger_fragment(bx, 'xiang.html'); blogger_fragment(bc, 'chen.html')
    banner()
    # 統計
    from collections import Counter
    cnt = Counter(k for k, _, _ in USED)
    total = sum(p.stat().st_size for p in IMG.iterdir())
    print('圖片', dict(cnt), '共', len(list(IMG.iterdir())), '檔', total // 1024, 'KB')
    for k, s, o in USED: print(f'  {k} {o:22s} <- {s}')
    for f in ('xiang.html', 'chen.html', 'blogger-xiang.html', 'blogger-chen.html', 'banner.html'):
        t = (STORY / f).read_text(encoding='utf-8'); print(f, len(t.encode()) // 1024, 'KB', 'lines', t.count('\n') + 1, '殘留 base64' if 'data:image' in t else '')
    print('哥哥', len(rx), cx, '弟弟', len(rc), cc)
