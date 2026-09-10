// 搜尋、篩選、燈箱
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
