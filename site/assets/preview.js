/* SHIVAS previews for production-line diagrams.
   Point at, keyboard-focus or tap a machine and a small card shows its picture, name, verified
   configuration (if any), one line of description and a link to the machine's page.
   Pictures come only from window.SHIVAS_LIBRARY (assets/library.js): each segment id maps to one
   asset id there. If a picture fails to load, the machine's line drawing is shown instead.
   Card modes: tip  (mouse over a list item or button: the pointer can move into the card)
               peek (mouse over a machine in a drawing: look-only, never blocks the drawing)
               pin  (mouse click on a machine in a drawing: stays until closed, link usable)
               sheet (touch, or keyboard on a small screen: panel at the bottom of the screen)
   <script src="assets/preview.js" data-root=""> on root pages, data-root="../" on item pages. */
(function () {
  'use strict';
  var LIB = window.SHIVAS_LIBRARY;
  if (!LIB) return;
  var me = document.currentScript;
  var ROOT = (me && me.getAttribute('data-root')) || '';
  var DRAW = !!(me && me.hasAttribute('data-drawings'));   // main pages: line drawings only, photos wait on the product page
  var SHOW = 90, HIDE = 170;
  var small = window.matchMedia('(max-width: 640px)');
  var card, fig, img, tag, nm, cf, ds, lk, b2, xb;
  var tShow = 0, tHide = 0, curEl = null, curSeg = null, mode = '', lastType = 'mouse', onSecondary = null, onHide = null;

  function build() {
    card = document.createElement('div');
    card.className = 'spv'; card.id = 'spv'; card.hidden = true;
    card.innerHTML = '<button type="button" class="spv-x" aria-label="Close preview">✕</button>' +
      '<figure class="spv-fig"><img alt="" decoding="async"><span class="spv-tag"></span></figure>' +
      '<div class="spv-body"><b class="spv-n" id="spvN"></b><span class="spv-c"></span><p class="spv-d" id="spvD"></p>' +
      '<div class="spv-acts"><a class="spv-a" href="#">Details and photos →</a><button type="button" class="spv-2" hidden></button></div></div>';
    document.body.appendChild(card);
    fig = card.querySelector('.spv-fig'); img = fig.querySelector('img'); tag = card.querySelector('.spv-tag');
    nm = card.querySelector('.spv-n'); cf = card.querySelector('.spv-c'); ds = card.querySelector('.spv-d');
    lk = card.querySelector('.spv-a'); b2 = card.querySelector('.spv-2'); xb = card.querySelector('.spv-x');
    card.addEventListener('pointerenter', function () { if (mode === 'tip') clearTimeout(tHide); });
    card.addEventListener('pointerleave', function (e) { if (mode === 'tip' && e.pointerType !== 'touch') hideSoon(); });
    card.addEventListener('focusout', function (e) { if (mode === 'tip' && !card.contains(e.relatedTarget) && !(curEl && curEl.contains(e.relatedTarget))) hideSoon(60); });
    xb.addEventListener('click', function () { var el = curEl; hide(); if (el && el.focus) try { el.focus({ preventScroll: true }); } catch (_) {} });
    b2.addEventListener('click', function () { var f = onSecondary; hide(); if (f) f(); });
    img.addEventListener('load', function () { fig.classList.remove('spv-load'); });
    img.addEventListener('error', function () {
      var seg = LIB.segments[curSeg] || {}, fb = LIB.assets[seg.fallbackImage];
      var tried = img.getAttribute('data-tried') || '';
      if (fb && tried.indexOf('fb') < 0) { img.setAttribute('data-tried', tried + 'fb'); useAsset(fb, seg.fallbackImage); return; }
      if (tried.indexOf('lib') < 0) { img.setAttribute('data-tried', tried + 'lib'); fig.classList.add('spv-drw'); img.src = ROOT + LIB.fallback; return; }
      fig.classList.remove('spv-load'); fig.hidden = true;
    });
    document.addEventListener('keydown', function (e) {
      if (e.key !== 'Escape' || card.hidden) return;
      var el = curEl, m = mode; hide();
      if (el && el.focus && m !== 'tip') try { el.focus({ preventScroll: true }); } catch (_) {}
    });
    document.addEventListener('pointerdown', function (e) {
      lastType = e.pointerType || 'mouse';
      if (!card.hidden && (mode === 'sheet' || mode === 'pin') && !card.contains(e.target) && !(curEl && curEl.contains(e.target))) hide();
    }, true);
    window.addEventListener('scroll', function () { if (mode && mode !== 'sheet') hide(); }, { passive: true });
    window.addEventListener('resize', function () { if (mode && mode !== 'sheet') hide(); });
  }

  function useAsset(a, id) {
    fig.hidden = false;
    fig.classList.toggle('spv-drw', a.type === 'drawing');
    fig.classList.add('spv-load');
    tag.textContent = a.tag;
    img.alt = a.alt;
    card.setAttribute('data-asset', id);
    img.src = ROOT + a.preview;
    if (img.complete && img.naturalWidth) fig.classList.remove('spv-load');
  }

  function fill(sid) {
    var s = LIB.segments[sid], it = LIB.items[s.item];
    var id = DRAW ? s.fallbackImage : s.image, a = LIB.assets[id];
    if (!a) { a = LIB.assets[s.fallbackImage]; id = s.fallbackImage; }
    img.removeAttribute('data-tried');
    useAsset(a, id);
    nm.textContent = it.name;
    cf.textContent = DRAW ? (it.photos ? it.photos + (it.photos > 1 ? ' photos' : ' photo') + ' on the product page' : '') : (a.verified && a.config ? a.config : '');
    cf.hidden = !cf.textContent;
    ds.textContent = it.description;
    lk.href = ROOT + it.href;
    lk.setAttribute('aria-label', 'Details and photos: ' + it.name);
    card.setAttribute('data-seg', sid);
  }

  /* the card never goes under a fixed or sticky page header */
  function topBound() {
    var h = document.getElementById('nav') || document.querySelector('header.top');
    if (!h) return 8;
    var p = getComputedStyle(h).position;
    if (p !== 'fixed' && p !== 'sticky') return 8;
    var r = h.getBoundingClientRect();
    return r.bottom > 0 && r.top <= 1 ? r.bottom + 8 : 8;
  }

  /* pref 'side' (vertical lists): beside the item so the card never covers its neighbours;
     otherwise above the item, or below it when there is no room above. Always inside the viewport. */
  function place(r, pref) {
    card.style.left = ''; card.style.top = '';
    card.classList.toggle('spv-sheet', mode === 'sheet');
    card.classList.toggle('spv-peek', mode === 'peek');
    card.classList.toggle('spv-pin', mode === 'pin');
    if (mode === 'sheet') return;
    var w = card.offsetWidth, h = card.offsetHeight, vw = document.documentElement.clientWidth, vh = window.innerHeight, m = 8, top = topBound(), x = null, y;
    if (pref === 'side') {
      if (r.right + 12 + w <= vw - m) x = r.right + 12;
      else if (r.left - 12 - w >= m) x = r.left - 12 - w;
    }
    if (x !== null) {
      y = Math.max(top, Math.min(vh - h - m, r.top + r.height / 2 - h / 2));
    } else {
      x = Math.max(m, Math.min(vw - w - m, r.left + r.width / 2 - w / 2));
      y = r.top - h - 10;
      if (y < top) { y = r.bottom + 10; if (y + h > vh - m) y = Math.max(top, vh - h - m); }
    }
    card.style.left = Math.round(x) + 'px'; card.style.top = Math.round(y) + 'px';
  }

  function mark(el, sid) {
    if (curEl && curEl !== el) { curEl.classList.remove('spv-on'); curEl.removeAttribute('aria-describedby'); }
    curEl = el; curSeg = sid;
    if (el) { el.classList.add('spv-on'); el.setAttribute('aria-describedby', 'spvD'); }
  }

  function modeFor(how) {
    if (how === 'tap') return 'sheet';
    if (how === 'focus') return small.matches ? 'sheet' : 'tip';
    if (how === 'peek' || how === 'pin') return how;
    return 'tip';
  }

  function show(sid, rect, el, how, secondary, hideCb, pref) {
    if (!LIB.segments[sid] || !rect) return;
    clearTimeout(tShow); clearTimeout(tHide);
    if (onHide && hideCb !== onHide) { var f = onHide; onHide = null; f(); }
    onHide = hideCb || null;
    mode = modeFor(how);
    mark(el, sid);
    onSecondary = secondary ? secondary.run : null;
    b2.hidden = !(mode === 'sheet' && secondary);
    if (secondary) b2.textContent = secondary.label;
    var dialog = mode === 'sheet' || mode === 'pin';
    card.setAttribute('role', dialog ? 'dialog' : 'tooltip');
    if (dialog) card.setAttribute('aria-labelledby', 'spvN'); else card.removeAttribute('aria-labelledby');
    fill(sid);
    var was = !card.hidden;
    card.hidden = false;
    place(rect, pref);
    if (!was) { card.classList.remove('spv-in'); requestAnimationFrame(function () { card.classList.add('spv-in'); }); }
  }

  function hide() {
    clearTimeout(tShow); clearTimeout(tHide);
    if (!card || card.hidden) return;
    card.classList.remove('spv-in', 'spv-sheet', 'spv-peek', 'spv-pin'); card.hidden = true;
    mark(null, null);
    if (onHide) { var f = onHide; onHide = null; f(); }
    mode = '';
  }
  function hideSoon(d) {
    if (mode === 'sheet' || mode === 'pin') return;            // those stay until closed
    clearTimeout(tShow); clearTimeout(tHide); tHide = setTimeout(hide, d == null ? HIDE : d);
  }
  function later(sid, getRect, el, how, sec, cb, pref) {
    clearTimeout(tShow); clearTimeout(tHide);
    if (!card.hidden && (mode === 'pin' || mode === 'sheet')) return;                                                     // a pinned card stays
    if (!card.hidden && (mode === 'tip' || mode === 'peek')) { show(sid, getRect(), el, how, sec, cb, pref); return; }   // moving on: no delay
    tShow = setTimeout(function () { show(sid, getRect(), el, how, sec, cb, pref); }, SHOW);
  }

  /* Delegated wiring for DOM segments inside root.
     opt.touch: 'both' = keep the element's own tap action and also open the panel,
                'intercept' = the panel replaces the tap action (offered again as opt.secondary),
                'none' = taps do their own thing only (e.g. links that open the machine's page).
     opt.place: 'side' for vertical lists. */
  function attach(root, selector, getSeg, opt) {
    if (!root) return;
    opt = opt || {};
    var segOf = function (t) { var s = getSeg(t); return s && LIB.segments[s] ? s : null; };
    root.addEventListener('pointerover', function (e) {
      if (e.pointerType === 'touch') return;
      var t = e.target.closest(selector); if (!t || !root.contains(t)) return;
      var sid = segOf(t); if (!sid) return;
      if (t === curEl && !card.hidden) { clearTimeout(tHide); return; }
      later(sid, function () { return t.getBoundingClientRect(); }, t, 'hover', null, null, opt.place);
    });
    root.addEventListener('pointerout', function (e) {
      if (e.pointerType === 'touch') return;
      var t = e.target.closest(selector); if (!t) return;
      var to = e.relatedTarget;
      if (to && (t.contains(to) || card.contains(to))) return;
      hideSoon();
    });
    root.addEventListener('focusin', function (e) {
      var t = e.target.closest(selector); if (!t || !root.contains(t) || lastType === 'touch') return;
      var vis = true; try { vis = t.matches(':focus-visible'); } catch (_) {}
      if (!vis) return;
      var sid = segOf(t); if (!sid) return;
      show(sid, t.getBoundingClientRect(), t, 'focus', null, null, opt.place);
    });
    root.addEventListener('focusout', function (e) {
      var t = e.target.closest(selector);
      if (!t || t !== curEl || mode !== 'tip') return;
      if (e.relatedTarget && card.contains(e.relatedTarget)) return;
      hideSoon(60);
    });
    if (opt.touch !== 'none') root.addEventListener('click', function (e) {
      if (lastType !== 'touch') return;
      var t = e.target.closest(selector); if (!t || !root.contains(t)) return;
      var sid = segOf(t); if (!sid) return;
      if (opt.touch === 'intercept') { e.preventDefault(); e.stopPropagation(); }
      var sec = opt.secondary ? { label: opt.secondary.label, run: function () { opt.secondary.run(t); } } : null;
      show(sid, t.getBoundingClientRect(), t, 'tap', sec);
    }, true);
  }

  build();
  window.SHIVAS_PREVIEW = {
    attach: attach,
    /* machines drawn on a canvas: rect in viewport coordinates.
       how: 'peek' (mouse over), 'pin' (mouse click), 'tap' (touch). onHideCb clears the drawing's highlight. */
    show: function (sid, rect, how, onHideCb) {
      if (how === 'peek') later(sid, function () { return rect; }, null, 'peek', null, onHideCb);
      else show(sid, rect, null, how, null, onHideCb);
    },
    hide: hide, hideSoon: hideSoon,
    has: function (sid) { return !!LIB.segments[sid]; },
    seg: function (sid) { return LIB.segments[sid] || null; },
    pointer: function () { return lastType; },
    mode: function () { return mode; },
    slug: function (s) { return String(s).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, ''); }
  };
})();
