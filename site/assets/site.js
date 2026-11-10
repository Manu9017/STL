/* SHIVAS site-wide helpers, loaded on every page.
   1. Every page opens at the top. A link that opens another page must never land the reader at the bottom:
      scroll restoration is off, the page is put at the top on load (or at its #anchor), and when the site is shown
      inside a frame that grows with its content (phones, embedded viewers) the frame itself is brought into view.
   2. A back-to-top button on long sub-pages.
   3. Gentle auto-scroll for horizontal rails marked data-auto (pauses on touch, hover or focus). */
(function () {
  'use strict';
  var H = document.documentElement, MAIN = !!document.getElementById('app'), ME = (document.currentScript && document.currentScript.src) || '';
  try { history.scrollRestoration = 'manual'; } catch (e) {}
  var fromLink = false;
  try { fromLink = sessionStorage.getItem('shivas.nav') === '1'; sessionStorage.removeItem('shivas.nav'); } catch (e) {}
  var moved = false;
  ['wheel', 'touchmove', 'keydown'].forEach(function (t) { addEventListener(t, function () { moved = true; }, { passive: true, once: true }); });
  function top() {
    if (moved) return;
    var h = (location.hash || '').slice(1);
    if (h) {
      if (MAIN) return;                                   // the main pages open their own sections (and brand) from the hash
      var el = document.getElementById(decodeURIComponent(h));
      if (el) { el.scrollIntoView({ block: 'start' }); return; }
    }
    if (scrollY !== 0) scrollTo(0, 0);
    H.scrollTop = 0; if (document.body) document.body.scrollTop = 0;
    if (fromLink) { try { (document.body || H).scrollIntoView({ block: 'start' }); } catch (e) {} }
  }
  top();
  document.addEventListener('DOMContentLoaded', top);
  addEventListener('load', function () { top(); setTimeout(top, 90); setTimeout(top, 450); });
  addEventListener('pageshow', function (e) { if (e.persisted) { moved = false; top(); } });
  // remember that the next page was opened from a link on this site
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href]'); if (!a || a.target === '_blank') return;
    var h = a.getAttribute('href'); if (/^(#|mailto:|tel:|https?:|javascript:)/.test(h)) return;
    try { sessionStorage.setItem('shivas.nav', '1'); } catch (_) {}
  }, true);

  // back to top on sub-pages (the main pages have their own)
  if (!MAIN) {
    var bt = document.createElement('button'); bt.type = 'button'; bt.className = 'to-top'; bt.setAttribute('aria-label', 'Back to top'); bt.textContent = '↑';
    bt.addEventListener('click', function () { scrollTo({ top: 0, behavior: 'smooth' }); });
    document.addEventListener('DOMContentLoaded', function () { document.body.appendChild(bt); });
    var on = false; addEventListener('scroll', function () { var s = scrollY > 900; if (s !== on) { on = s; bt.classList.toggle('on', s); } }, { passive: true });
    // the header tucks away while reading down and comes back on the first scroll up (more room on phones)
    var ly = scrollY, hd = null;
    addEventListener('scroll', function () {
      hd = hd || document.querySelector('header.top'); if (!hd) return;
      var y = scrollY, d = y - ly; if (Math.abs(d) < 6) return; ly = y;
      /* V39: hiding and showing the header is done in assets/v39.js */
    }, { passive: true });
    // the site bar marks the page you are on
    document.addEventListener('DOMContentLoaded', function () {
      var here = location.pathname.replace(/\/index\.html$/, '/').replace(/\/$/, '/index.html').split('/').slice(-2).join('/');
      [].forEach.call(document.querySelectorAll('.snav a'), function (a) {
        var p = (a.getAttribute('href') || '').replace(/^(\.\.\/|\.\/)/, '');
        if (p && p.indexOf('#') < 0 && here.slice(-p.length) === p) a.setAttribute('aria-current', 'page');
      });
    });
  }

  // auto-scrolling rails: <div data-auto> with overflow-x; one card every few seconds, back to the start at the end
  function autoRail(el) {
    var hold = 0, vis = false, step = +el.getAttribute('data-auto') || 4200;
    var stop = function () { hold = Date.now() + 9000; };
    ['pointerdown', 'touchstart', 'wheel', 'focusin', 'mouseenter'].forEach(function (t) { el.addEventListener(t, stop, { passive: true }); });
    el.addEventListener('mousemove', stop, { passive: true });
    new IntersectionObserver(function (es) { vis = es[0].isIntersecting; }, { threshold: .3 }).observe(el);
    setInterval(function () {
      if (!vis || Date.now() < hold || document.hidden || el.scrollWidth <= el.clientWidth + 4) return;
      var c = el.firstElementChild; var w = c ? c.getBoundingClientRect().width + 12 : el.clientWidth * .8;
      var end = el.scrollLeft + el.clientWidth >= el.scrollWidth - 6;
      el.scrollTo({ left: end ? 0 : el.scrollLeft + w, behavior: 'smooth' });
    }, step);
  }
  function initRails() { [].forEach.call(document.querySelectorAll('[data-auto]'), autoRail); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initRails); else initRails();
  window.SHIVAS_SITE = { autoRail: autoRail, top: top };

  // settings, then the visitor log (it does nothing until assets/config.js is filled in)
  if (ME && !window.SHIVAS_TRACK) {
    var base = ME.replace(/site\.js(\?.*)?$/, ''), c = document.createElement('script');
    c.src = base + 'config.js';
    c.onload = c.onerror = function () { var t = document.createElement('script'); t.src = base + 'track.js'; t.async = true; document.head.appendChild(t); };
    document.head.appendChild(c);
  }
})();
