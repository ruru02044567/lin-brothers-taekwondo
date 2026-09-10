# -*- coding: utf-8 -*-
"""產生 SEO 需要的檔案，並把結構化資料注入三頁 HTML。
- sitemap.xml：告訴 Google 有哪些頁
- robots.txt：允許收錄，並指向 sitemap
- JSON-LD：讓 Google 認得這是運動員檔案與獲獎清單
"""
import json, io, os, collections, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, 'docs')
REC = json.load(io.open(os.path.join(ROOT, '獎狀資料.json'), encoding='utf-8'))['獎狀']

BASE = 'https://ruru02044567.github.io/lin-brothers-taekwondo'
TODAY = datetime.date.today().isoformat()

PAGES = [
    ('index.html', '1.0'),
    ('lin-sheng-xiang.html', '0.9'),
    ('lin-sheng-chen.html', '0.9'),
]


def sitemap():
    x = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for f, pri in PAGES:
        x.append('  <url><loc>%s/%s</loc><lastmod>%s</lastmod>'
                 '<changefreq>monthly</changefreq><priority>%s</priority></url>'
                 % (BASE, f, TODAY, pri))
    x.append('</urlset>')
    return '\n'.join(x)


def robots():
    return ('User-agent: *\n'
            'Allow: /\n\n'
            'Sitemap: %s/sitemap.xml\n' % BASE)


def person_ld(who, name, page):
    """schema.org Person，附上獲獎清單。Google 用這個判斷頁面在講誰。"""
    rs = sorted([r for r in REC if r['選手'] == who], key=lambda r: r['日期'], reverse=True)
    awards = ['%s %s %s %s' % (r['賽事'], r['項目'], r['組別'], r['名次文字']) for r in rs]
    golds = sum(1 for r in rs if r['名次'] == 1)
    obj = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": name,
        "url": "%s/%s" % (BASE, page),
        "nationality": {"@type": "Country", "name": "臺灣"},
        "jobTitle": "跆拳道選手",
        "affiliation": [
            {"@type": "SportsOrganization", "name": "民逸跆訓",
             "alternateName": "逸心聯隊", "sport": "跆拳道",
             "areaServed": {"@type": "City", "name": "高雄市"}},
            {"@type": "SportsTeam", "name": "高雄市福山國小跆拳道隊", "sport": "跆拳道"},
        ],
        "memberOf": {"@type": "EducationalOrganization", "name": "高雄市立福山國民小學"},
        "knowsAbout": ["跆拳道", "對打", "品勢", "競技對打", "Taekwondo"],
        "alternateName": ["民逸跆訓 " + name],
        "award": awards,
        "description": "民逸跆訓 %s，高雄市福山國小跆拳道隊選手。共 %d 場獲獎紀錄，其中 %d 次第一名。"
                       % (name, len(rs), golds),
    }
    return json.dumps(obj, ensure_ascii=False, indent=None)


def site_ld():
    obj = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "林聖翔 林聖宸 跆拳道比賽紀錄",
        "url": BASE + '/',
        "inLanguage": "zh-Hant-TW",
        "about": [
            {"@type": "Person", "name": "林聖翔"},
            {"@type": "Person", "name": "林聖宸"},
            {"@type": "SportsOrganization", "name": "民逸跆訓",
             "alternateName": "逸心聯隊", "sport": "跆拳道",
             "areaServed": {"@type": "City", "name": "高雄市"}},
        ],
        "keywords": "民逸跆訓, 逸心聯隊, 林聖翔, 林聖宸, 福山國小, 高雄跆拳道, 跆拳道比賽紀錄",
        "description": "高雄市福山國小、民逸跆訓，林聖翔與林聖宸兩兄弟民國 112 至 115 年跆拳道比賽獲獎紀錄，"
                       "共 36 場，橫跨 7 個縣市，每一場都附獎狀原圖。",
    }
    return json.dumps(obj, ensure_ascii=False, indent=None)


def inject(fname, ld, canonical):
    p = os.path.join(DOCS, fname)
    h = io.open(p, encoding='utf-8').read()
    if 'application/ld+json' in h:
        return False
    block = ('<link rel="canonical" href="%s/%s">\n'
             '<script type="application/ld+json">%s</script>\n'
             % (BASE, canonical, ld))
    h = h.replace('<link rel="stylesheet" href="style.css">',
                  block + '<link rel="stylesheet" href="style.css">')
    io.open(p, 'w', encoding='utf-8').write(h)
    return True


if __name__ == '__main__':
    io.open(os.path.join(DOCS, 'sitemap.xml'), 'w', encoding='utf-8').write(sitemap())
    io.open(os.path.join(DOCS, 'robots.txt'), 'w', encoding='utf-8').write(robots())
    io.open(os.path.join(DOCS, '.nojekyll'), 'w', encoding='utf-8').write('')
    print('sitemap.xml / robots.txt / .nojekyll 完成')
    print('index.html      ', inject('index.html', site_ld(), 'index.html'))
    print('lin-sheng-xiang ', inject('lin-sheng-xiang.html',
                                     person_ld('聖翔', '林聖翔', 'lin-sheng-xiang.html'),
                                     'lin-sheng-xiang.html'))
    print('lin-sheng-chen  ', inject('lin-sheng-chen.html',
                                     person_ld('聖宸', '林聖宸', 'lin-sheng-chen.html'),
                                     'lin-sheng-chen.html'))
