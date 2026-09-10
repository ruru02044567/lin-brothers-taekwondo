# -*- coding: utf-8 -*-
"""產生林家兄弟跆拳道網站的三個 HTML 頁面。
資料來源：獎狀資料.json（由 36 張獎狀照片逐張讀出）
輸出：site/index.html、site/lin-sheng-xiang.html、site/lin-sheng-chen.html
"""
import json, io, os, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'docs'))
import _charts
D = json.load(io.open(os.path.join(ROOT, '獎狀資料.json'), encoding='utf-8'))
REC = D['獎狀']

BELT_CLASS = {'黃帶': 'yellow', '色帶': 'color', '紅帶': 'red', '黑帶': 'black'}
FONT = ('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
        'family=Noto+Serif+TC:wght@700;900&family=Noto+Sans+TC:wght@400;500;700&display=swap">')


def esc(s):
    return (str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            .replace('"', '&quot;'))


def head(title, desc, page):
    """頁首。title 已含全名，讓搜尋引擎抓得到。"""
    nav = [('index.html', '總覽'), ('lin-sheng-xiang.html', '林聖翔'),
           ('lin-sheng-chen.html', '林聖宸')]
    links = ''.join(
        '<a href="{}"{}>{}</a>'.format(h, ' class="on"' if h == page else '', t)
        for h, t in nav)
    return '''<!doctype html>
<html lang="zh-Hant-TW">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="profile">
<meta name="robots" content="index,follow">
{font}
<link rel="stylesheet" href="style.css">
</head>
<body>
<header class="topbar"><div class="wrap">
<div class="brand">林家兄弟 <span>跆拳道</span></div>
<nav class="navlinks">{links}</nav>
</div></header>
'''.format(title=esc(title), desc=esc(desc), font=FONT, links=links)


TAIL = '''<footer><div class="wrap">
<p>本頁紀錄整理自獎狀正本，共 36 張，逐張核對。
參賽單位為<b>高雄市福山國小</b>與<b>民逸跆訓</b>（道館比賽隊名為逸心聯隊）。</p>
<p><b>姓名正確寫法</b>：哥哥為<b>林聖翔</b>，弟弟為<b>林聖宸</b>。
弟弟的名字在部分學校公告中曾誤植為「林聖辰」，獎狀正本一律為「林聖宸」，請以獎狀為準。</p>
<p>最後更新 2026 年 9 月。若有遺漏或誤植，以獎狀正本為準。</p>
</div></footer>
<script src="app.js"></script>
</body></html>'''


def stat_block(rs, extra=None):
    c = collections.Counter(r['名次'] for r in rs)
    cells = [('g', c[1], '第一名'), ('s', c[2], '第二名'), ('b', c[3], '第三名')]
    if c[4]:
        cells.append(('', c[4], '第四名'))
    html = '<div class="stats">'
    html += '<div class="stat"><div class="n">{}</div><div class="k">總場次</div></div>'.format(len(rs))
    for cls, n, k in cells:
        html += '<div class="stat {}"><div class="n">{}</div><div class="k">{}</div></div>'.format(cls, n, k)
    if extra:
        for n, k in extra:
            html += '<div class="stat"><div class="n">{}</div><div class="k">{}</div></div>'.format(n, k)
    return html + '</div>'


def render_items(rs):
    """依年份分組輸出獎狀清單。每筆是 button，點了開燈箱。"""
    out = []
    by_year = collections.defaultdict(list)
    for r in rs:
        by_year[r['年']].append(r)
    for y in sorted(by_year, reverse=True):
        items = sorted(by_year[y], key=lambda r: r['日期'], reverse=True)
        out.append('<div class="year-block" data-year="{}">'.format(y))
        out.append('<div class="year-head"><span class="y">民國 {} 年</span>'
                   '<span class="ce">{}</span><span class="cnt">{} 場</span></div>'
                   .format(y, items[0]['西元'], len(items)))
        for r in items:
            belt = r.get('腰帶') or ''
            bcls = BELT_CLASS.get(belt, 'color')
            chips = []
            if r['層級'] == '全國賽':
                chips.append('<span class="chip natl">全國賽</span>')
            if r['縣市']:
                chips.append('<span class="chip">{}</span>'.format(esc(r['縣市'])))
            blob = ' '.join(str(v) for v in [r['賽事'], r['組別'], r['主辦'], r['縣市'],
                                             r['單位'], r['項目'], belt, r['名次文字'],
                                             r['年'], r['西元'], r['日期']] if v)
            out.append(
                '<button class="item" data-id="{id}" data-search="{blob}" '
                'data-level="{lv}" data-rank="{rk}">'
                '<span class="date">{date}</span>'
                '<span class="body"><span class="ev">{ev}</span>'
                '<span class="meta">{belt}<span class="dot">·</span>{proj} {grp}</span>'
                '<span class="meta">{chips}</span></span>'
                '<span class="rank r{rk}">{rt}</span></button>'.format(
                    id=r['id'], blob=esc(blob), lv=esc(r['層級']), rk=r['名次'],
                    date=r['日期'][5:].replace('-', '/'), ev=esc(r['賽事']),
                    belt='<span class="belt {}"><i></i>{}</span>'.format(bcls, esc(belt)) if belt else '',
                    proj=esc(r['項目']), grp=esc(r['組別']),
                    chips=''.join(chips), rt=esc(r['名次文字'])))
        out.append('</div>')
    return '\n'.join(out)


def tools_bar(scope):
    return ('<div class="tools">'
            '<label class="search"><svg viewBox="0 0 24 24" aria-hidden="true">'
            '<circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg>'
            '<input type="search" id="q" placeholder="搜尋賽事、縣市、組別、年份…" '
            'aria-label="搜尋{scope}的比賽紀錄"></label>'
            '<select id="fLevel" aria-label="賽事層級">'
            '<option value="">所有層級</option><option>全國賽</option>'
            '<option>市級</option><option>縣級</option><option>鎮級</option></select>'
            '<select id="fRank" aria-label="名次">'
            '<option value="">所有名次</option><option value="1">第一名</option>'
            '<option value="2">第二名</option><option value="3">第三名</option>'
            '<option value="4">第四名</option></select>'
            '<span class="count" id="count"></span></div>').format(scope=scope)


LIGHTBOX = '''<div class="lightbox" id="lb" hidden role="dialog" aria-modal="true" aria-label="獎狀原圖">
<button class="lb-close" id="lbClose" aria-label="關閉">&times;</button>
<button class="lb-nav lb-prev" id="lbPrev" aria-label="上一張">&#8249;</button>
<button class="lb-nav lb-next" id="lbNext" aria-label="下一張">&#8250;</button>
<div class="lb-inner"><div class="lb-img"><img id="lbImg" src="" alt=""></div>
<div class="lb-cap"><div class="t" id="lbTitle"></div><div class="d" id="lbDesc"></div></div>
</div></div>'''


def timeline_svg():
    """兩兄弟得獎時間軸。x 軸依日期線性換算，避免點擠在一起。"""
    W, L, R = 960, 108, 936
    import datetime
    d0 = datetime.date(2023, 1, 1)
    d1 = datetime.date(2026, 12, 31)
    span = (d1 - d0).days

    def x(ds):
        d = datetime.date(*map(int, ds.split('-')))
        return L + (R - L) * ((d - d0).days / span)

    RANK_FILL = {1: 'var(--gold)', 2: 'var(--silver)', 3: 'var(--bronze)', 4: 'var(--ink3)'}
    s = ['<svg viewBox="0 0 960 250" role="img" aria-label="兩兄弟 112 至 115 年得獎時間軸">']
    for yr, ce in [(112, 2023), (113, 2024), (114, 2025), (115, 2026)]:
        gx = x('%d-01-01' % ce)
        s.append('<line class="gl" x1="%.1f" y1="26" x2="%.1f" y2="196"/>' % (gx, gx))
        s.append('<text class="sm" x="%.1f" y="216">民國 %d 年</text>' % (gx + 6, yr))
        s.append('<text class="sm" x="%.1f" y="232">%d</text>' % (gx + 6, ce))
    for who, cy, color in [('聖翔', 84, 'var(--hong)'), ('聖宸', 158, 'var(--chung)')]:
        s.append('<line class="ax" x1="%d" y1="%d" x2="%d" y2="%d"/>' % (L, cy, R, cy))
        s.append('<text class="lbl" x="%d" y="%d" text-anchor="end" fill="%s">林%s</text>'
                 % (L - 12, cy + 4, color, who))
        rs = sorted([r for r in REC if r['選手'] == who], key=lambda r: r['日期'])
        for i, r in enumerate(rs):
            px = x(r['日期'])
            rad = 7 if r['名次'] == 1 else 5.5
            up = (i % 2 == 0)
            s.append('<g><title>%s %s %s</title>'
                     '<circle cx="%.1f" cy="%d" r="%.1f" fill="%s"/>'
                     '<circle class="ring" cx="%.1f" cy="%d" r="%.1f"/></g>'
                     % (esc(r['日期']), esc(r['賽事']), esc(r['名次文字']),
                        px, cy, rad, RANK_FILL[r['名次']], px, cy, rad))
    s.append('</svg>')
    return '\n'.join(s)


def build_index():
    xiang = [r for r in REC if r['選手'] == '聖翔']
    chen = [r for r in REC if r['選手'] == '聖宸']
    cities = {r['縣市'] for r in REC if r['縣市']}
    natl = sum(1 for r in REC if r['層級'] == '全國賽')
    golds = sum(1 for r in REC if r['名次'] == 1)

    def card(cls, role, name, href, rs, cur):
        c = collections.Counter(r['名次'] for r in rs)
        return ('<a class="person {cls}" href="{href}">'
                '<div class="role">{role}</div><div class="nm">{name}</div>'
                '<div class="cur">{cur}</div>'
                '<div class="med">'
                '<div><span class="v r1">{g}</span><span class="l">第一名</span></div>'
                '<div><span class="v r2">{s}</span><span class="l">第二名</span></div>'
                '<div><span class="v r3">{b}</span><span class="l">第三名</span></div>'
                '<div><span class="v">{t}</span><span class="l">總場次</span></div>'
                '</div><div class="go">看完整紀錄 &rarr;</div></a>').format(
            cls=cls, href=href, role=role, name=name, cur=cur,
            g=c[1], s=c[2], b=c[3], t=len(rs))

    h = head('民逸跆訓 林聖翔 林聖宸 跆拳道比賽紀錄',
             '高雄市福山國小、民逸跆訓，林聖翔與林聖宸兩兄弟民國 112 至 115 年跆拳道比賽獲獎紀錄，'
             '共 36 場，橫跨 7 個縣市。每一場都附獎狀原圖。', 'index.html')
    h += '''<div class="hero"><div class="wrap">
<div class="eyebrow">高雄市福山國小 · 民逸跆訓</div>
<h1>林聖翔<span class="sep">·</span>林聖宸<br>跆拳道比賽紀錄</h1>
<p class="sub"><b>民逸跆訓</b>選手林聖翔、林聖宸兩兄弟，就讀高雄市福山國小。
從民國 112 年打到現在，累積 {t} 張獎狀，跑遍 {c} 個縣市。
這裡收錄每一場的賽事名稱、組別、名次，點任何一列都能看獎狀原圖。</p>
{stats}
</div></div>

<section><div class="wrap">
<div class="sec-head"><h2>兩位選手</h2></div>
<div class="people">{cards}</div>
</div></section>

<section><div class="wrap">
<div class="sec-head"><h2>越打越強</h2><span class="hint">一個方塊代表一面獎牌</span></div>
<div class="fig">{ladder}</div>
<div class="legend">
<span><i style="background:var(--gold)"></i>第一名</span>
<span><i style="background:var(--silver)"></i>第二名</span>
<span><i style="background:var(--bronze)"></i>第三名</span>
<span><i style="background:var(--ink3)"></i>第四名</span>
</div>
<p class="figcap">哥哥前兩年七戰無金，114 年四場全拿第一，隔年升上黑帶。
弟弟 115 年九場比賽拿下六個第一。下方色帶是腰帶進程。</p>
</div></section>

<section><div class="wrap">
<div class="sec-head"><h2>跑了七個縣市</h2><span class="hint">由北到南排列</span></div>
<div class="fig">{citymap}</div>
<div class="legend">
<span><i style="background:var(--hong)"></i>林聖翔</span>
<span><i style="background:var(--chung)"></i>林聖宸</span>
</div>
<p class="figcap">主場在高雄，但為了比賽從屏東潮州一路跑到新北、新竹竹東、苗栗。
最下面那列是中華民國跆拳道協會與 9 段協會主辦的全國賽，沒有固定縣市。</p>
</div></section>

<section><div class="wrap">
<div class="sec-head"><h2>全部 {t} 場</h2><span class="hint">可搜尋、可篩選</span></div>
{tools}
<div id="list">{items}</div>
<div class="empty" id="empty" hidden>沒有符合的紀錄</div>
</div></section>
{lb}
'''.format(t=len(REC), c=len(cities),
           stats=stat_block(REC, extra=[(natl, '全國級賽事'), (len(cities), '個縣市')]),
           cards=card('h', '哥哥', '林聖翔', 'lin-sheng-xiang.html', xiang, '黑帶 · 37 公斤級')
                 + card('c', '弟弟', '林聖宸', 'lin-sheng-chen.html', chen, '色帶 · 34 公斤級'),
           ladder=_charts.LADDER, citymap=_charts.CITYMAP, tools=tools_bar('兩兄弟'),
           items=render_items(REC), lb=LIGHTBOX)
    return h + TAIL


def build_person(who, name, en, role, cur, desc_extra):
    rs = [r for r in REC if r['選手'] == who]
    cities = {r['縣市'] for r in rs if r['縣市']}
    natl = sum(1 for r in rs if r['層級'] == '全國賽')
    first = min(rs, key=lambda r: r['日期'])
    last = max(rs, key=lambda r: r['日期'])
    page = en + '.html'
    title = '民逸跆訓 {name} | 跆拳道比賽紀錄 · 高雄福山國小'.format(name=name)
    desc = ('民逸跆訓 {name}，高雄市福山國小跆拳道隊選手。民國 {y1} 至 {y2} 年共 {t} 場獲獎紀錄，'
            '含 {n} 場全國級賽事，橫跨 {c} 個縣市，每場皆附獎狀原圖。{extra}').format(
        name=name, y1=first['年'], y2=last['年'], t=len(rs), n=natl,
        c=len(cities), extra=desc_extra)

    h = head(title, desc, page)
    h += '''<div class="hero"><div class="wrap">
<div class="eyebrow">{role} · 高雄市福山國小 · 民逸跆訓</div>
<h1>{name}</h1>
<p class="sub"><b>民逸跆訓</b>選手 {name}，就讀高雄市福山國小，{cur}。
民國 {y1} 年 {m1} 月第一次站上頒獎台，到民國 {y2} 年為止累積 {t} 張獎狀，
其中 {n} 場是全國級賽事，比賽足跡遍及 {c} 個縣市。</p>
{stats}
</div></div>

<section><div class="wrap">
<div class="sec-head"><h2>比賽紀錄</h2><span class="hint">點任一列看獎狀原圖</span></div>
{tools}
<div id="list">{items}</div>
<div class="empty" id="empty" hidden>沒有符合的紀錄</div>
</div></section>
{lb}
'''.format(role=role, name=name, cur=cur, y1=first['年'], m1=int(first['日期'][5:7]),
           y2=last['年'], t=len(rs), n=natl, c=len(cities),
           stats=stat_block(rs, extra=[(natl, '全國級賽事'), (len(cities), '個縣市')]),
           tools=tools_bar(name), items=render_items(rs), lb=LIGHTBOX)
    return h + TAIL


APP_JS = r'''// 搜尋、篩選、燈箱
(function () {
  var data = null;
  fetch('data.json').then(function (r) { return r.json(); })
    .then(function (d) { data = d; });

  var q = document.getElementById('q');
  var fl = document.getElementById('fLevel');
  var fr = document.getElementById('fRank');
  var cnt = document.getElementById('count');
  var empty = document.getElementById('empty');
  var items = [].slice.call(document.querySelectorAll('.item'));
  var blocks = [].slice.call(document.querySelectorAll('.year-block'));

  function apply() {
    var kw = (q.value || '').trim().toLowerCase();
    var lv = fl.value, rk = fr.value, shown = 0;
    items.forEach(function (el) {
      var ok = true;
      if (kw && el.dataset.search.toLowerCase().indexOf(kw) === -1) ok = false;
      if (ok && lv && el.dataset.level !== lv) ok = false;
      if (ok && rk && el.dataset.rank !== rk) ok = false;
      el.hidden = !ok;
      if (ok) shown++;
    });
    blocks.forEach(function (b) {
      var any = b.querySelector('.item:not([hidden])');
      b.hidden = !any;
    });
    cnt.textContent = shown === items.length
      ? ('共 ' + items.length + ' 場')
      : ('顯示 ' + shown + ' / ' + items.length + ' 場');
    empty.hidden = shown > 0;
  }
  [q, fl, fr].forEach(function (el) { el.addEventListener('input', apply); });
  apply();

  // 燈箱
  var lb = document.getElementById('lb'),
      lbImg = document.getElementById('lbImg'),
      lbT = document.getElementById('lbTitle'),
      lbD = document.getElementById('lbDesc');
  var cur = -1;

  function visible() { return items.filter(function (e) { return !e.hidden; }); }

  function open(el) {
    if (!data) return;
    var id = el.dataset.id;
    var r = data['獎狀'].filter(function (x) { return x.id === id; })[0];
    if (!r) return;
    cur = visible().indexOf(el);
    lbImg.src = 'images/' + id + '.jpg';
    lbImg.alt = r['賽事'] + ' ' + r['名次文字'] + ' 獎狀';
    lbT.textContent = r['賽事'];
    var bits = [r['日期'], r['項目'], r['組別'], r['名次文字'], '單位：' + r['單位']];
    if (r['主辦']) bits.push('主辦：' + r['主辦']);
    lbD.textContent = bits.join('　');
    lb.hidden = false;
    document.body.style.overflow = 'hidden';
  }
  function close() {
    lb.hidden = true; lbImg.src = ''; document.body.style.overflow = '';
  }
  function step(n) {
    var v = visible();
    if (!v.length) return;
    cur = (cur + n + v.length) % v.length;
    open(v[cur]);
  }
  items.forEach(function (el) {
    el.addEventListener('click', function () { open(el); });
  });
  document.getElementById('lbClose').addEventListener('click', close);
  document.getElementById('lbPrev').addEventListener('click', function () { step(-1); });
  document.getElementById('lbNext').addEventListener('click', function () { step(1); });
  lb.addEventListener('click', function (e) { if (e.target === lb) close(); });
  document.addEventListener('keydown', function (e) {
    if (lb.hidden) return;
    if (e.key === 'Escape') close();
    if (e.key === 'ArrowLeft') step(-1);
    if (e.key === 'ArrowRight') step(1);
  });
})();
'''

if __name__ == '__main__':
    site = os.path.join(ROOT, 'docs')
    os.makedirs(site, exist_ok=True)
    io.open(os.path.join(site, 'index.html'), 'w', encoding='utf-8').write(build_index())
    io.open(os.path.join(site, 'lin-sheng-xiang.html'), 'w', encoding='utf-8').write(
        build_person('聖翔', '林聖翔', 'lin-sheng-xiang', '哥哥', '目前黑帶，37 公斤級',
                     '民國 115 年第三屆全國理事長盃跆拳道錦標賽國小男子黑帶組第一名。'))
    io.open(os.path.join(site, 'lin-sheng-chen.html'), 'w', encoding='utf-8').write(
        build_person('聖宸', '林聖宸', 'lin-sheng-chen', '弟弟', '目前色帶，34 公斤級',
                     '民國 115 年第三屆全國理事長盃跆拳道錦標賽國小男子色帶組第一名。'))
    io.open(os.path.join(site, 'app.js'), 'w', encoding='utf-8').write(APP_JS)
    print('三頁 + app.js 產生完成')
    for f in ['index.html', 'lin-sheng-xiang.html', 'lin-sheng-chen.html', 'app.js']:
        p = os.path.join(site, f)
        print('  %-24s %6.1f KB' % (f, os.path.getsize(p) / 1024))
