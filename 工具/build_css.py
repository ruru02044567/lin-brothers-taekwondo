import io, os
CSS = r"""/* 林家兄弟跆拳道 - 共用樣式
   設計方向：道場的夜。深墨底、紙白字、腰帶色作為唯一亮點。
   用細線與留白分隔，不用圓角卡片堆疊。 */

:root{
  --bg:#12100e;
  --bg2:#1a1714;
  --surface:#211d19;
  --surface2:#292420;
  --ink:#f2eee6;
  --ink2:#a89f92;
  --ink3:#6d665c;
  --line:#2f2a24;
  --line2:#403a32;

  --hong:#d4574b;
  --chung:#5b8fd0;
  --gold:#d4a935;
  --silver:#a8a49c;
  --bronze:#b07a45;

  --belt-yellow:#e8b22a;
  --belt-green:#4a9d6b;
  --belt-red:#c8453a;
  --belt-black:#f2eee6;

  --serif:"Noto Serif TC",Georgia,serif;
  --sans:"Noto Sans TC",system-ui,-apple-system,"PingFang TC","Microsoft JhengHei",sans-serif;
}

*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{
  margin:0;background:var(--bg);color:var(--ink);
  font-family:var(--sans);font-size:15.5px;line-height:1.75;
  -webkit-font-smoothing:antialiased;
}
a{color:inherit;text-decoration:none}
a:focus-visible,button:focus-visible,input:focus-visible,select:focus-visible{
  outline:2px solid var(--gold);outline-offset:3px;
}
img{max-width:100%;display:block}

.wrap{max-width:1120px;margin:0 auto;padding:0 24px}

.topbar{
  border-bottom:1px solid var(--line);
  position:sticky;top:0;z-index:50;
  background:rgba(18,16,14,.93);backdrop-filter:blur(10px);
}
.topbar .wrap{display:flex;align-items:center;justify-content:space-between;height:58px;gap:20px}
.brand{font-family:var(--serif);font-weight:700;font-size:1.02rem;letter-spacing:.06em;white-space:nowrap}
.brand span{color:var(--gold)}
.navlinks{display:flex;gap:4px;font-size:.88rem}
.navlinks a{padding:6px 13px;border-radius:2px;color:var(--ink2);transition:.16s}
.navlinks a:hover{color:var(--ink);background:var(--surface)}
.navlinks a.on{color:var(--ink);border-bottom:2px solid var(--gold)}

.hero{padding:60px 0 38px;border-bottom:1px solid var(--line)}
.hero .eyebrow{
  font-size:.75rem;letter-spacing:.24em;color:var(--ink3);
  text-transform:uppercase;margin-bottom:18px;
}
.hero h1{
  font-family:var(--serif);font-weight:900;
  font-size:clamp(2.1rem,5.6vw,3.4rem);line-height:1.14;
  margin:0;letter-spacing:.02em;text-wrap:balance;
}
.hero h1 .sep{color:var(--ink3);font-weight:400;margin:0 .1em}
.hero .sub{color:var(--ink2);max-width:40em;margin-top:20px;font-size:1.02rem}

.stats{display:flex;flex-wrap:wrap;gap:0;margin-top:36px;border-top:1px solid var(--line)}
.stat{
  flex:1 1 128px;padding:19px 22px 17px;
  border-right:1px solid var(--line);border-bottom:1px solid var(--line);
}
.stat:last-child{border-right:none}
.stat .n{
  font-family:var(--serif);font-weight:900;line-height:1;
  font-size:2.4rem;font-variant-numeric:tabular-nums;
}
.stat .k{font-size:.8rem;color:var(--ink2);margin-top:7px;letter-spacing:.05em}
.stat.g .n{color:var(--gold)}
.stat.s .n{color:var(--silver)}
.stat.b .n{color:var(--bronze)}
.stat.h .n{color:var(--hong)}
.stat.c .n{color:var(--chung)}

section{padding:52px 0}
.sec-head{
  display:flex;align-items:baseline;gap:16px;flex-wrap:wrap;
  border-bottom:1px solid var(--line2);padding-bottom:11px;margin-bottom:24px;
}
.sec-head h2{
  font-family:var(--serif);font-size:1.3rem;font-weight:700;margin:0;letter-spacing:.03em;
}
.sec-head .hint{font-size:.85rem;color:var(--ink3);margin-left:auto}

.tools{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-bottom:20px}
.search{flex:1 1 250px;position:relative}
.search input{
  width:100%;background:var(--surface);border:1px solid var(--line2);
  color:var(--ink);font-family:var(--sans);font-size:.95rem;
  padding:11px 14px 11px 38px;border-radius:2px;
}
.search input::placeholder{color:var(--ink3)}
.search svg{
  position:absolute;left:13px;top:50%;transform:translateY(-50%);
  width:15px;height:15px;stroke:var(--ink3);fill:none;stroke-width:2;
}
select{
  background:var(--surface);border:1px solid var(--line2);color:var(--ink);
  font-family:var(--sans);font-size:.9rem;padding:11px 12px;border-radius:2px;
}
.count{font-size:.85rem;color:var(--ink3);white-space:nowrap;padding-left:4px}

.year-head{
  display:flex;align-items:baseline;gap:14px;
  padding:22px 0 10px;border-bottom:1px solid var(--line);
}
.year-head .y{font-family:var(--serif);font-size:1.5rem;font-weight:900;letter-spacing:.02em}
.year-head .ce{font-size:.85rem;color:var(--ink3)}
.year-head .cnt{margin-left:auto;font-size:.82rem;color:var(--ink3)}

.item{
  display:grid;grid-template-columns:86px 1fr auto;
  gap:0 20px;align-items:start;
  padding:15px 0;border-bottom:1px solid var(--line);
  cursor:pointer;transition:.14s;width:100%;text-align:left;
  background:none;border-left:none;border-right:none;border-top:none;
  color:inherit;font-family:inherit;font-size:inherit;
}
.item:hover{background:var(--bg2)}
.item .date{font-size:.84rem;color:var(--ink3);font-variant-numeric:tabular-nums;padding-top:3px}
.item .body{min-width:0}
.item .ev{font-size:.99rem;font-weight:500;line-height:1.5;text-wrap:balance}
.item .meta{
  font-size:.85rem;color:var(--ink2);margin-top:5px;
  display:flex;gap:8px;flex-wrap:wrap;align-items:center;
}
.item .meta .dot{color:var(--ink3)}
.item .rank{
  font-family:var(--serif);font-weight:700;font-size:1.02rem;white-space:nowrap;
  padding-top:2px;text-align:right;
}
.r1{color:var(--gold)} .r2{color:var(--silver)} .r3{color:var(--bronze)} .r4{color:var(--ink3)}

.chip{
  font-size:.74rem;letter-spacing:.05em;padding:2px 8px;
  border:1px solid var(--line2);border-radius:2px;color:var(--ink2);white-space:nowrap;
}
.chip.natl{border-color:var(--gold);color:var(--gold)}
.belt{display:inline-flex;align-items:center;gap:6px;white-space:nowrap;font-size:.85rem}
.belt i{width:16px;height:5px;border-radius:1px;display:inline-block;flex:0 0 auto}
.belt.yellow i{background:var(--belt-yellow)}
.belt.color i{background:var(--belt-green)}
.belt.red i{background:var(--belt-red)}
.belt.black i{background:var(--belt-black)}

.empty{padding:50px 0;text-align:center;color:var(--ink3)}

.lightbox{
  position:fixed;inset:0;z-index:100;
  background:rgba(8,7,6,.95);backdrop-filter:blur(6px);
  display:flex;align-items:center;justify-content:center;padding:24px;
}
.lightbox[hidden]{display:none!important}
.lb-inner{max-width:840px;width:100%;max-height:100%;display:flex;flex-direction:column;gap:14px}
.lb-img{flex:1 1 auto;min-height:0;display:flex;align-items:center;justify-content:center}
.lb-img img{max-height:72vh;width:auto;border:1px solid var(--line2)}
.lb-cap{flex:0 0 auto}
.lb-cap .t{font-family:var(--serif);font-size:1.04rem;font-weight:700;line-height:1.45}
.lb-cap .d{font-size:.87rem;color:var(--ink2);margin-top:5px}
.lb-close{
  position:fixed;top:14px;right:18px;z-index:110;
  background:var(--surface);border:1px solid var(--line2);color:var(--ink2);
  width:38px;height:38px;border-radius:2px;font-size:1.2rem;cursor:pointer;
}
.lb-close:hover{color:var(--ink);border-color:var(--ink3)}
.lb-nav{
  position:fixed;z-index:110;top:50%;transform:translateY(-50%);
  background:var(--surface);border:1px solid var(--line2);color:var(--ink2);
  width:40px;height:56px;border-radius:2px;font-size:1.3rem;cursor:pointer;
}
.lb-nav:hover{color:var(--ink)}
.lb-prev{left:16px} .lb-next{right:16px}
@media(max-width:640px){.lb-nav{display:none}}

.people{display:grid;grid-template-columns:1fr 1fr;gap:20px}
@media(max-width:720px){.people{grid-template-columns:1fr}}
.person{
  border:1px solid var(--line);padding:28px 26px 26px;
  background:var(--bg2);transition:.18s;position:relative;overflow:hidden;display:block;
}
.person:hover{border-color:var(--line2);background:var(--surface)}
.person::before{content:"";position:absolute;top:0;left:0;right:0;height:4px}
.person.h::before{background:var(--hong)}
.person.c::before{background:var(--chung)}
.person .role{font-size:.78rem;letter-spacing:.16em;color:var(--ink3)}
.person .nm{
  font-family:var(--serif);font-size:1.95rem;font-weight:900;
  line-height:1.15;margin:5px 0 3px;letter-spacing:.04em;
}
.person .cur{font-size:.88rem;color:var(--ink2)}
.person .med{display:flex;gap:22px;margin-top:20px}
.person .med div{display:flex;flex-direction:column}
.person .med .v{font-family:var(--serif);font-size:1.65rem;font-weight:900;line-height:1}
.person .med .l{font-size:.75rem;color:var(--ink3);margin-top:3px}
.person .go{margin-top:22px;font-size:.88rem;color:var(--ink2);display:inline-flex;align-items:center;gap:7px}
.person:hover .go{color:var(--gold)}

.fig{border:1px solid var(--line);background:var(--bg2);padding:22px 18px 14px;overflow-x:auto}
.fig svg{display:block;width:100%;height:auto;min-width:660px}
.fig text{font-family:var(--sans);fill:var(--ink2);font-size:12px}
.fig text.lbl{fill:var(--ink);font-size:12.5px;font-weight:500}
.fig text.sm{fill:var(--ink3);font-size:11px}
.fig .gl{stroke:var(--line);stroke-width:1}
.fig .ax{stroke:var(--line2);stroke-width:1}
.fig .ring{fill:none;stroke:var(--bg2);stroke-width:2}
.figcap{font-size:.82rem;color:var(--ink3);margin-top:12px;padding:0 2px}
.legend{display:flex;gap:18px;flex-wrap:wrap;font-size:.84rem;color:var(--ink2);margin-top:14px;padding:0 2px}
.legend span{display:inline-flex;align-items:center;gap:7px}
.legend i{width:11px;height:11px;border-radius:2px;display:inline-block}

footer{border-top:1px solid var(--line);margin-top:36px;padding:30px 0 58px;font-size:.84rem;color:var(--ink3)}
footer p{margin:0 0 8px;max-width:52em}

.note{
  border-left:3px solid var(--gold);background:var(--bg2);
  padding:16px 20px;margin:20px 0;font-size:.92rem;color:var(--ink2);
}
.note b{color:var(--ink);font-weight:700}
"""
os.makedirs('docs', exist_ok=True)
io.open('docs/style.css', 'w', encoding='utf-8').write(CSS)
print('style.css OK', len(CSS))
