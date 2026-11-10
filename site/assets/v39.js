/* V39: the header hides while reading down and comes back as soon as you scroll up a little.
   V40: on the division pages a section bar appears below the hero, stays at the top while you read and marks where you are. */
(function () {
  var root = document.documentElement, hd = null, app = false, H = 0, hidden = false, last = 0, bar = null, SB = 0, barOn = false, hero = null;
  function find() {
    hd = document.querySelector('#app #nav') || document.querySelector('header#nav') || document.querySelector('header.top');
    app = !!(hd && hd.id === 'nav');
  }
  function apply() {
    var sb = barOn ? SB : 0;
    root.style.setProperty('--hd-h', H + 'px');
    root.style.setProperty('--hd', hidden ? '0px' : H + 'px');
    root.style.setProperty('--sb', sb + 'px');
    if (app) root.style.setProperty('--stick', ((hidden ? 0 : H) + sb) + 'px');
  }
  function measure() { if (!hd) return; H = Math.ceil(hd.getBoundingClientRect().height); if (bar) SB = Math.ceil(bar.getBoundingClientRect().height); apply(); }
  function busy() {
    if (!hd) return true;
    if (hd.querySelector('[aria-expanded="true"]')) return true;           // a menu is open
    var m = document.getElementById('menu'); if (m && !m.hidden) return true;
    var mn = document.getElementById('mnav'); if (mn && !mn.hidden) return true;
    return false;
  }
  function set(h) {
    if (!hd || h === hidden) return;
    hidden = h;
    hd.classList.toggle(app ? 'nav-hide' : 'tuck', h);
    apply();
  }
  // ---- section bar (division pages)
  var SECS = [['dip', 'How it works'], ['kettle', 'Kettles'], ['hdg-machines', 'Equipment'], ['wire', 'The line'], ['wire-machines', 'Machines'],
    ['rein-loop', 'Environment'], ['rein-machines', 'Equipment'], ['rein-lines', 'Wire lines'], ['plants', 'Complete plant'], ['rein-plants', 'Complete plants'],
    ['hall', '3D models'], ['rein-3d', '3D models'], ['range', 'Products'], ['rein-range', 'Products'], ['tools', 'Calculators'], ['standards', 'Standards'], ['enquire', 'Get a quote']];
  var links = [];
  function buildBar() {
    if (!app || !document.getElementById('app')) return;
    var vis = SECS.filter(function (s) { var e = document.getElementById(s[0]); return e && e.offsetHeight > 0; });
    if (vis.length < 3) return;
    hero = document.getElementById('top'); if (!hero || !hero.offsetHeight) hero = document.getElementById('reinplast');
    bar = document.createElement('nav'); bar.className = 'v40-sb'; bar.setAttribute('aria-label', 'On this page');
    bar.innerHTML = '<div class="v40-sb-in">' + vis.map(function (s) { return '<a href="#' + s[0] + '" data-s="' + s[0] + '"' + (s[0] === 'enquire' ? ' class="q"' : '') + '>' + s[1] + '</a>'; }).join('') + '</div>';
    document.body.appendChild(bar);
    links = [].slice.call(bar.querySelectorAll('a'));
    SB = Math.ceil(bar.getBoundingClientRect().height) || 46;
  }
  var cur = '';
  function mark() {
    if (!bar) return;
    var on = hero ? hero.getBoundingClientRect().bottom < 0 : (window.scrollY > 500);
    if (on !== barOn) { barOn = on; bar.classList.toggle('on', on); apply(); }
    var off = (hidden ? 0 : H) + SB + 60, id = '';
    for (var i = 0; i < links.length; i++) { var e = document.getElementById(links[i].dataset.s); if (e && e.getBoundingClientRect().top <= off) id = links[i].dataset.s; }
    if (id !== cur) {
      cur = id;
      links.forEach(function (a) { var o = a.dataset.s === id; a.classList.toggle('cur', o); if (o) { a.setAttribute('aria-current', 'location'); var w = a.parentElement; if (w.scrollWidth > w.clientWidth) w.scrollTo({ left: a.offsetLeft - 24, behavior: 'smooth' }); } else a.removeAttribute('aria-current'); });
    }
  }
  function onScroll() {
    if (!hd) return;
    var y = window.scrollY || 0, d = y - last;
    if (y <= Math.max(H, 40)) { set(false); last = y; mark(); return; }
    if (Math.abs(d) >= 8) { if (d > 0) { if (!busy()) set(true); } else set(false); last = y; }
    mark();
  }
  function init() {
    find(); if (!hd) return; buildBar(); measure(); last = window.scrollY || 0;
    addEventListener('scroll', onScroll, { passive: true });
    addEventListener('resize', function () { measure(); mark(); });
    if (window.ResizeObserver) new ResizeObserver(measure).observe(hd);
    hd.addEventListener('focusin', function () { set(false); });
    mark();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();

/* V42: menus lock the page while open, close on Escape or a tap outside, and glide to the section you pick */
(function () {
  var root = document.documentElement;
  function menus() { return [document.getElementById('menu'), document.getElementById('mnav'), document.getElementById('v42menu')].filter(Boolean); }
  function btnFor(m) { return document.querySelector('[aria-controls="' + m.id + '"]'); }
  function close(m) { if (!m || m.hidden) return; var b = btnFor(m); if (b) b.click(); if (!m.hidden) { m.hidden = true; if (b) { b.setAttribute('aria-expanded', 'false'); if (b.id === 'menuBtn') b.textContent = 'Menu'; } } }
  function sync() { root.classList.toggle('v42-lock', menus().some(function (m) { return !m.hidden; })); }
  function init() {
    var sb = document.getElementById('v42mb'), sm = document.getElementById('v42menu');
    if (sb && sm) sb.addEventListener('click', function () { var o = sm.hidden; sm.hidden = !o; sb.setAttribute('aria-expanded', String(o)); sb.textContent = o ? 'Close' : 'Menu'; });
    menus().forEach(function (m) {
      new MutationObserver(sync).observe(m, { attributes: true, attributeFilter: ['hidden'] });
      m.addEventListener('click', function (e) {
        var a = e.target.closest('a[href]'); if (!a) return;
        var u = new URL(a.getAttribute('href'), location.href);
        if (u.pathname === location.pathname && u.hash && u.hash.length > 1) {
          var t = document.getElementById(u.hash.slice(1)); if (!t) return;
          e.preventDefault();
          setTimeout(function () { close(m); sync(); requestAnimationFrame(function () { var cs = getComputedStyle(root), hh = parseFloat(cs.getPropertyValue('--hd-h')) || 64, sb = document.querySelector('.v40-sb') ? (document.querySelector('.v40-sb').offsetHeight || 46) : 0, r = t.getBoundingClientRect().top, off = (r > 0 ? 0 : hh) + sb + 10; window.scrollTo({ top: Math.max(0, r + window.scrollY - off), behavior: 'smooth' }); try { history.replaceState(null, '', u.hash); } catch (_) {} }); }, 0);
        }
      });
    });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') menus().forEach(close); });
    document.addEventListener('pointerdown', function (e) { menus().forEach(function (m) { if (!m.hidden && !m.contains(e.target)) { var b = btnFor(m); if (!b || !b.contains(e.target)) close(m); } }); });
    sync();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();

/* V46: email buttons open the mail app; if this browser or preview cannot open one, offer Gmail / Outlook compose links with every SHIVAS address filled in */
(function () {
  var sheet = null, tm = 0;
  function parse(h) {
    var q = h.slice(7).split('?'), o = { to: decodeURIComponent(q[0] || ''), cc: '', subject: '', body: '' };
    (q[1] || '').split('&').forEach(function (kv) { var k = kv.split('=')[0].toLowerCase(), v = kv.slice(k.length + 1); try { v = decodeURIComponent(v); } catch (e) {} if (k in o) o[k] = v; });
    return o;
  }
  function E(x) { return encodeURIComponent(x); }
  function offer(h) {
    var m = parse(h);
    var gm = 'https://mail.google.com/mail/?view=cm&fs=1&to=' + E(m.to) + '&cc=' + E(m.cc) + '&su=' + E(m.subject) + '&body=' + E(m.body);
    var ol = 'https://outlook.live.com/mail/0/deeplink/compose?to=' + E(m.to) + '&cc=' + E(m.cc) + '&subject=' + E(m.subject) + '&body=' + E(m.body);
    if (!sheet) { sheet = document.createElement('div'); sheet.className = 'v46-ms'; document.body.appendChild(sheet); }
    sheet.innerHTML = '<p>Send the email with</p><div><a class="v46-g" target="_blank" rel="noopener">Gmail</a><a class="v46-o" target="_blank" rel="noopener">Outlook</a><a class="v46-m" target="_blank" rel="noopener">Mail app</a><button type="button" aria-label="Close">✕</button></div>';
    sheet.querySelector('.v46-g').href = gm; sheet.querySelector('.v46-o').href = ol; sheet.querySelector('.v46-m').href = h;
    sheet.querySelector('button').onclick = function () { sheet.classList.remove('on'); };
    sheet.querySelectorAll('a').forEach(function (a) { a.addEventListener('click', function () { setTimeout(function () { sheet.classList.remove('on'); }, 300); }); });
    requestAnimationFrame(function () { sheet.classList.add('on'); });
    clearTimeout(tm); tm = setTimeout(function () { sheet.classList.remove('on'); }, 15000);
  }
  function watch(h) {
    var left = false; function gone() { left = true; }
    window.addEventListener('blur', gone, { once: true }); document.addEventListener('visibilitychange', gone, { once: true });
    setTimeout(function () { window.removeEventListener('blur', gone); document.removeEventListener('visibilitychange', gone); if (!left) offer(h); }, 1300);
  }
  function go(h) { var a = document.createElement('a'); a.href = h; a.target = '_blank'; a.rel = 'noopener'; a.style.display = 'none'; document.body.appendChild(a); a.click(); a.remove(); }
  window.shivasMail = go;
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href^="mailto:"]'); if (!a || (sheet && sheet.contains(a))) return;
    watch(a.getAttribute('href'));
  }, true);
})();
