# -*- coding: utf-8 -*-
"""產生網站用的三張圖表 SVG。
1. 成長階梯：每年獎牌堆疊 + 腰帶進程
2. 比賽地圖：跑過哪些縣市
3. 對照條：兩兄弟逐年金銀銅
輸出成 python 字串，由 build_site.py 引用。
"""
import json, io, os, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REC = json.load(io.open(os.path.join(ROOT, '獎狀資料.json'), encoding='utf-8'))['獎狀']

GOLD, SILVER, BRONZE, FOURTH = 'var(--gold)', 'var(--silver)', 'var(--bronze)', 'var(--ink3)'
HONG, CHUNG = 'var(--hong)', 'var(--chung)'


def esc(s):
    return (str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))


def chart_ladder():
    """成長階梯：橫軸年份，每年一疊獎牌方塊，越高越多。
    下方一條腰帶進程色帶。這是主圖，講『越打越強』。"""
    YEARS = [112, 113, 114, 115]
    CE = {112: 2023, 113: 2024, 114: 2025, 115: 2026}
    W, H = 900, 470
    L, B = 92, 286           # 左邊界、基線
    colw = (W - L - 40) / 4  # 每年欄寬
    unit = 21                # 每面獎牌高度
    gap = 3

    s = ['<svg viewBox="0 0 %d %d" role="img" aria-label="兩兄弟逐年獎牌數與腰帶進程">' % (W, H)]

    # 基線
    s.append('<line class="ax" x1="%d" y1="%d" x2="%d" y2="%d"/>' % (L - 14, B, W - 24, B))

    for i, y in enumerate(YEARS):
        cx = L + colw * i + colw / 2
        # 年份標籤
        s.append('<text class="lbl" x="%.1f" y="%d" text-anchor="middle">民國 %d 年</text>'
                 % (cx, B + 30, y))
        s.append('<text class="sm" x="%.1f" y="%d" text-anchor="middle">%d</text>'
                 % (cx, B + 47, CE[y]))

        for j, (who, color, off) in enumerate([('聖翔', HONG, -1), ('聖宸', CHUNG, 1)]):
            rs = [r for r in REC if r['選手'] == who and r['年'] == y]
            if not rs:
                continue
            bw = colw * 0.30
            bx = cx + off * (bw / 2 + 5) - bw / 2
            c = collections.Counter(r['名次'] for r in rs)
            stack = [(4, c[4], FOURTH), (3, c[3], BRONZE), (2, c[2], SILVER), (1, c[1], GOLD)]
            ytop = B
            for rank, n, col in stack:
                for k in range(n):
                    ytop -= unit
                    s.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%d" fill="%s" rx="1"/>'
                             % (bx, ytop, bw, unit - gap, col))
                    ytop -= 0
            # 總數
            s.append('<text class="sm" x="%.1f" y="%.1f" text-anchor="middle">%d</text>'
                     % (bx + bw / 2, ytop - 8, len(rs)))
            # 誰
            s.append('<text x="%.1f" y="%d" text-anchor="middle" font-size="11" fill="%s">%s</text>'
                     % (bx + bw / 2, B + 14, color, who))

    # 腰帶進程帶
    by = 372
    s.append('<text class="sm" x="%d" y="%d" text-anchor="end">腰帶進程</text>' % (W - 24, by - 22))
    # 哥哥
    segs_x = [('黃帶', 112.3, 112.75, '#e8b22a'), ('色帶', 112.75, 115.03, '#4a9d6b'),
              ('黑帶', 115.03, 116.0, '#f2eee6')]

    def xof(v):
        return L + colw * (v - 112)

    for label, a, b, col in segs_x:
        x1, x2 = xof(a), min(xof(b), W - 24)
        s.append('<rect x="%.1f" y="%d" width="%.1f" height="9" fill="%s" rx="1"/>'
                 % (x1, by, x2 - x1, col))
        s.append('<text class="sm" x="%.1f" y="%d" text-anchor="middle">%s</text>'
                 % ((x1 + x2) / 2, by - 7, label))
    s.append('<text x="%d" y="%d" text-anchor="end" font-size="11.5" fill="%s">聖翔</text>'
             % (L - 20, by + 9, HONG))

    by2 = 424
    segs_c = [('黃帶', 113.2, 113.7, '#e8b22a'), ('色帶', 113.7, 116.0, '#4a9d6b')]
    for label, a, b, col in segs_c:
        x1, x2 = xof(a), min(xof(b), W - 24)
        s.append('<rect x="%.1f" y="%d" width="%.1f" height="9" fill="%s" rx="1"/>'
                 % (x1, by2, x2 - x1, col))
        s.append('<text class="sm" x="%.1f" y="%d" text-anchor="middle">%s</text>'
                 % ((x1 + x2) / 2, by2 - 7, label))
    s.append('<text x="%d" y="%d" text-anchor="end" font-size="11.5" fill="%s">聖宸</text>'
             % (L - 20, by2 + 9, CHUNG))

    s.append('</svg>')
    return '\n'.join(s)


def chart_map():
    """比賽地圖：台灣由北到南排列的縣市長條，看得出跑多遠。"""
    ORDER = ['新北市', '新竹縣', '苗栗縣', '臺中市', '嘉義市', '高雄市', '屏東縣', '全國協會']
    NOTE = {'全國協會': '中華民國跆拳道協會、9段協會'}
    cnt = collections.Counter(r['縣市'] or '全國協會' for r in REC)
    W = 900
    rowh = 40
    H = 40 + rowh * len(ORDER)
    L = 108
    maxv = max(cnt.values())
    barmax = W - L - 130

    s = ['<svg viewBox="0 0 %d %d" role="img" aria-label="各縣市比賽場次">' % (W, H)]
    for i, city in enumerate(ORDER):
        v = cnt.get(city, 0)
        if not v:
            continue
        y = 30 + rowh * i
        xs = sum(1 for r in REC if (r['縣市'] or '全國協會') == city and r['選手'] == '聖翔')
        cs = v - xs
        s.append('<text class="lbl" x="%d" y="%d" text-anchor="end">%s</text>' % (L - 16, y + 15, city))
        w1 = barmax * xs / maxv
        w2 = barmax * cs / maxv
        if w1:
            s.append('<rect x="%d" y="%d" width="%.1f" height="20" fill="%s" rx="1"/>'
                     % (L, y, w1, HONG))
        if w2:
            s.append('<rect x="%.1f" y="%d" width="%.1f" height="20" fill="%s" rx="1"/>'
                     % (L + w1 + 2, y, w2, CHUNG))
        s.append('<text class="sm" x="%.1f" y="%d">%d 場</text>' % (L + w1 + w2 + 12, y + 15, v))
    s.append('</svg>')
    return '\n'.join(s)


if __name__ == '__main__':
    out = io.open(os.path.join(ROOT, 'docs', '_charts.py'), 'w', encoding='utf-8')
    out.write('# -*- coding: utf-8 -*-\n')
    out.write('LADDER = """%s"""\n\n' % chart_ladder())
    out.write('CITYMAP = """%s"""\n' % chart_map())
    out.close()
    print('圖表 SVG 產生完成')
