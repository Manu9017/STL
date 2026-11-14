/* SHIVAS button and viewer controls for the 3D viewers in v/.
   One column, placed per viewer where it does not cover the viewer's own controls:
   zoom in, zoom out, full screen, and the round SHIVAS button. The SHIVAS button opens a menu:
   ask about this plant on WhatsApp, call, the product page, switch to another 3D model, all 3D models and home.
   A short hint ("Drag to turn · + / − or scroll to zoom") shows once the model is up, and hides on the first touch.

   <script defer src="shivas-bar.js" data-name="Zinc ash recovery plant" data-item="ash"
           data-d="top:70px;right:24px" data-p="top:160px;right:12px"></script>
     data-name  what the model shows (goes into the WhatsApp message)
     data-item  items/<id>.html for the product page (optional)
     data-d     position on screens 760 px and wider; data-p below 760 px (CSS, fixed to the viewport)
   The zoom buttons send wheel events to the viewer's canvas, so they work in every viewer without touching it.
   Also hides the viewer's loading screen (#shv-load) once the model is on screen, and loads the visitor log
   (../assets/config.js + track.js, without the consent bar). Needs ../apple-touch-icon.png for the logo. Keys typed inside the menu
   do not reach the viewer, so its shortcuts (F, X, Esc, arrows) keep working outside it. */
(function () {
  'use strict';
  var me = document.currentScript; if (!me) return;
  var D = me.dataset, NAME = D.name || document.title.replace(/\s*[·|].*$/, ''), PHONE = '919810920468';
  var base = me.src.replace(/v\/shivas-bar\.js.*$/, '');
  var MODELS = [
    ['hdg-plant', 'Hot-dip galvanizing plant'],
    ['spin-galvanizing', 'Spin galvanizing plant'],
    ['acid-room-2line', 'Enclosed acid room, two lines'],
    ['electric-furnace', 'Electric kettle furnace'],
    ['zinc-ash-plant', 'Zinc ash recovery plant'],
    ['zinc-ash-hoist', 'Zinc ash unit, hoist tilt'],
    ['zinc-ash-hydraulic', 'Zinc ash unit, hydraulic tilt'],
    ['dross-grab', 'Pneumatic dross grab'],
    ['etp-zld-compact', 'ETP and ZLD, compact site'],
    ['etp-zld-spread', 'ETP and ZLD, open site'],
    ['arp-10', 'Acid regeneration plant ARP-10']
  ];
  var HERE = (location.pathname.split('/').pop() || '').replace(/\.html$/, '');
  var css = '' +
    '.shv{position:fixed;z-index:2147483000;display:flex;flex-direction:column;align-items:center;gap:8px;' +
      'font:500 14px/1.35 "Noto Sans","Segoe UI",Arial,sans-serif;color:#13202c}' +
    '.shv *{box-sizing:border-box}' +
    '.shv-b{display:block;width:44px;height:44px;padding:0;border:2px solid #fff;border-radius:50%;cursor:pointer;' +
      'background:#0a4b8d url(' + base + 'apple-touch-icon.png) center/cover no-repeat;box-shadow:0 2px 10px rgba(0,0,0,.35)}' +
    '.shv-t{display:flex;flex-direction:column;gap:8px}' +
    '.shv-t button{display:grid;place-items:center;width:44px;height:44px;padding:0;border:2px solid #fff;border-radius:50%;' +
      'cursor:pointer;background:rgba(10,75,141,.92);color:#fff;box-shadow:0 2px 10px rgba(0,0,0,.35)}' +
    '.shv-t button:hover{background:#0a4b8d}' +
    '.shv-t svg{width:20px;height:20px}' +
    '.shv-b:focus-visible,.shv-t button:focus-visible{outline:3px solid #ffc35a;outline-offset:2px}' +
    '.shv-m{position:absolute;width:276px;max-width:calc(100vw - 24px);max-height:calc(100vh - 110px);overflow:auto;' +
      'background:#fff;border:1px solid #dde5ee;border-radius:12px;' +
      'box-shadow:0 12px 32px rgba(0,0,0,.28);padding:10px;display:grid;gap:6px;overscroll-behavior:contain}' +
    '.shv-m[hidden]{display:none}' +
    '.shv-h{padding:4px 6px 6px;border-bottom:1px solid #dde5ee;margin-bottom:2px}' +
    '.shv-h b{display:block;font-size:12px;letter-spacing:.08em;color:#1f4e79}' +
    '.shv-h span{display:block;font-size:13px;color:#4f6275}' +
    '.shv-g{font:600 11px/1 "Noto Sans","Segoe UI",Arial,sans-serif;letter-spacing:.08em;text-transform:uppercase;color:#4f6275;padding:8px 6px 2px}' +
    '.shv-m a{display:flex;align-items:center;gap:10px;min-height:44px;padding:8px 10px;border-radius:8px;text-decoration:none;color:#13202c}' +
    '.shv-m a.shv-s{min-height:38px;padding:6px 10px;font-size:13.5px}' +
    '.shv-m a:hover,.shv-m a:focus-visible{background:#eef3f8;outline:none}' +
    '.shv-m a.wa{background:#15803d;color:#fff;font-weight:600}.shv-m a.wa:hover,.shv-m a.wa:focus-visible{background:#116b33}' +
    '.shv-m svg{flex:none;width:18px;height:18px}' +
    '.shv-hint{position:fixed;left:50%;bottom:calc(14px + env(safe-area-inset-bottom,0px));transform:translateX(-50%);z-index:2147482999;' +
      'max-width:calc(100vw - 20px);padding:9px 16px;border-radius:999px;background:rgba(8,18,30,.82);color:#fff;' +
      'font:500 13.5px/1.35 "Noto Sans","Segoe UI",Arial,sans-serif;text-align:center;white-space:nowrap;pointer-events:none;' +
      'opacity:0;transition:opacity .45s}' +
    '.shv-hint.on{opacity:1}' +
    '@media (prefers-color-scheme:dark){.shv-m{background:#0f1d2c;border-color:#24394f;color:#e7edf3}.shv-h{border-color:#24394f}' +
      '.shv-h b{color:#8fb3d6}.shv-h span,.shv-g{color:#a3b5c7}.shv-m a{color:#e7edf3}.shv-m a:hover,.shv-m a:focus-visible{background:#132539}}';
  var ic = {
    wa: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm4.5 12.1c-.2-.1-1.5-.7-1.7-.8s-.4-.1-.6.1-.7.8-.8 1-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4.2-.4.7-1.4a.5.5 0 0 0 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.7 11.8 11.8 0 0 0 4.5 4c1.7.7 2.3.8 3.2.6a2.7 2.7 0 0 0 1.8-1.2 2.2 2.2 0 0 0 .1-1.2c0-.1-.2-.2-.4-.3z"/></svg>',
    tel: '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M5 3h4l2 5-2.5 1.5a11 11 0 0 0 6 6L16 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 5a2 2 0 0 1 2-2z"/></svg>',
    doc: '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M6 3h8l4 4v14H6z"/><path d="M14 3v4h4M9 12h6M9 16h6"/></svg>',
    cube: '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M12 3l8 4.5v9L12 21l-8-4.5v-9z"/><path d="M4 7.5l8 4.5 8-4.5M12 12v9"/></svg>',
    home: '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M3 11l9-7 9 7v9h-6v-6H9v6H3z"/></svg>',
    plus: '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg>',
    minus: '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M5 12h14"/></svg>',
    full: '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 4H4v5M15 4h5v5M9 20H4v-5M15 20h5v-5"/></svg>'
  };
  var esc = function (t) { return String(t).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
  var msg = encodeURIComponent('Enquiry from the SHIVAS website: ' + NAME + ' (3D model). ');

  // zoom: send a wheel event to the viewer's canvas, where its own controls listen
  function canvas() {
    var best = null, ba = 0;
    [].forEach.call(document.querySelectorAll('canvas'), function (x) {
      var r = x.getBoundingClientRect(), a = r.width * r.height;
      if (a > ba) { ba = a; best = x; }
    });
    return best;
  }
  function zoom(dir) {
    var c = canvas(); if (!c) return;
    var r = c.getBoundingClientRect();
    c.dispatchEvent(new WheelEvent('wheel', {
      bubbles: true, cancelable: true, view: window,
      clientX: r.left + r.width / 2, clientY: r.top + r.height / 2,
      deltaY: dir * -100, deltaMode: 0
    }));
  }

  function build() {
    var st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);
    var others = MODELS.filter(function (m) { return m[0] !== HERE; });
    var w = document.createElement('div'); w.className = 'shv';
    w.innerHTML =
      '<nav class="shv-m" id="shvMenu" aria-label="SHIVAS" hidden>' +
        '<div class="shv-h"><b>SHIVAS</b><span>' + esc(NAME) + '</span></div>' +
        '<a class="wa" href="https://wa.me/' + PHONE + '?text=' + msg + '" target="_blank" rel="noopener">' + ic.wa + 'Ask about this plant</a>' +
        '<a href="tel:+' + PHONE + '">' + ic.tel + 'Call +91 98109 20468</a>' +
        (D.item ? '<a href="' + base + 'items/' + esc(D.item) + '.html">' + ic.doc + 'Details and photos</a>' : '') +
        '<div class="shv-g">Switch 3D model</div>' +
        others.map(function (m) {
          return '<a class="shv-s" href="' + base + 'v/' + m[0] + '.html">' + ic.cube + esc(m[1]) + '</a>';
        }).join('') +
        '<a href="' + base + '3d-models.html">' + ic.cube + 'All 3D models</a>' +
        '<a href="' + base + '">' + ic.home + 'SHIVAS home</a>' +
      '</nav>' +
      '<div class="shv-t">' +
        '<button type="button" data-z="1" aria-label="Zoom in" title="Zoom in">' + ic.plus + '</button>' +
        '<button type="button" data-z="-1" aria-label="Zoom out" title="Zoom out">' + ic.minus + '</button>' +
        '<button type="button" data-fs aria-label="Full screen" title="Full screen">' + ic.full + '</button>' +
      '</div>' +
      '<button type="button" class="shv-b" aria-expanded="false" aria-controls="shvMenu" aria-label="SHIVAS menu: ask about this plant" title="SHIVAS: ask about this plant"></button>';
    document.body.appendChild(w);
    var btn = w.querySelector('.shv-b'), menu = w.querySelector('.shv-m'), tools = w.querySelector('.shv-t');

    function place() {
      var spec = (innerWidth < 760 ? D.p : D.d) || 'bottom:16px;right:16px';
      w.style.cssText = '';
      spec.split(';').forEach(function (kv) { var p = kv.split(':'); if (p.length === 2) w.style.setProperty(p[0].trim(), p[1].trim()); });
      if (/left:\s*50%/.test(spec)) w.style.transform = 'translateX(-50%)';
      // anchored to the top edge: SHIVAS button first, tools below it, so the stack grows away from the edge
      w.style.flexDirection = /(^|;)\s*top\s*:/.test(spec) ? 'column-reverse' : 'column';
    }
    function aim() {   // open the menu away from the nearest screen edge
      var r = w.getBoundingClientRect();
      menu.style.top = menu.style.bottom = menu.style.left = menu.style.right = '';
      if (r.top + r.height / 2 > innerHeight / 2) menu.style.bottom = 'calc(100% + 8px)'; else menu.style.top = 'calc(100% + 8px)';
      if (r.left + r.width / 2 > innerWidth / 2) menu.style.right = '0'; else menu.style.left = '0';
    }
    function open(v) {
      menu.hidden = !v; btn.setAttribute('aria-expanded', String(v));
      if (v) { aim(); var a = menu.querySelector('a'); a && a.focus(); }
    }
    btn.addEventListener('click', function (e) { e.stopPropagation(); open(menu.hidden); });
    document.addEventListener('pointerdown', function (e) { if (!menu.hidden && !w.contains(e.target)) open(false); }, true);
    w.addEventListener('keydown', function (e) {
      e.stopPropagation();   // the viewer's keyboard shortcuts must not fire while using the menu
      if (e.key === 'Escape') { open(false); btn.focus(); }
    });
    ['pointerdown', 'wheel', 'touchstart', 'mousedown'].forEach(function (t) { w.addEventListener(t, function (e) { e.stopPropagation(); }, { passive: true }); });

    // zoom buttons: one step per tap, repeat while held
    var rep = 0;
    tools.addEventListener('pointerdown', function (e) {
      var b = e.target.closest('button[data-z]'); if (!b) return;
      var d = +b.dataset.z; zoom(d);
      clearInterval(rep); rep = setInterval(function () { zoom(d); }, 130);
    });
    ['pointerup', 'pointercancel', 'pointerleave'].forEach(function (t) { tools.addEventListener(t, function () { clearInterval(rep); }); });
    // full screen (hidden where the browser does not allow it, e.g. iPhone)
    var fsb = tools.querySelector('[data-fs]'), root = document.documentElement;
    if (!root.requestFullscreen) { fsb.style.display = 'none'; }
    else {
      fsb.addEventListener('click', function () {
        if (document.fullscreenElement) document.exitFullscreen();
        else root.requestFullscreen().catch(function () {});
      });
      document.addEventListener('fullscreenchange', function () {
        var on = !!document.fullscreenElement;
        fsb.setAttribute('aria-label', on ? 'Exit full screen' : 'Full screen');
        fsb.title = on ? 'Exit full screen' : 'Full screen';
      });
    }
    addEventListener('resize', place);
    place();

    // one short hint, once the model is up; goes away on the first touch of the model or after 7 s
    var hint = document.createElement('div');
    hint.className = 'shv-hint'; hint.setAttribute('aria-hidden', 'true');
    hint.textContent = 'Drag to turn · + / − or scroll to zoom';
    document.body.appendChild(hint);
    var hided = 0, unhint = function () { if (hided) return; hided = 1; hint.classList.remove('on'); setTimeout(function () { hint.remove(); }, 600); };
    setTimeout(function () {
      if (hided) return; hint.classList.add('on');
      setTimeout(unhint, 7000);
    }, 1500);
    ['pointerdown', 'wheel', 'touchstart'].forEach(function (t) { document.addEventListener(t, function (e) { if (!w.contains(e.target)) unhint(); }, { passive: true, capture: true }); });
  }
  if (document.body) build(); else document.addEventListener('DOMContentLoaded', build);

  // loading screen (#shv-load, inline at the top of <body> so it shows at once): hide it when a 3D canvas is on screen
  var load = document.getElementById('shv-load');
  if (load) {
    var t0 = Date.now();
    var hide = function () { load.style.transition = 'opacity .3s'; load.style.opacity = '0'; setTimeout(function () { load.remove(); }, 320); };
    (function wait() {
      var c = [].some.call(document.querySelectorAll('canvas'), function (x) { var r = x.getBoundingClientRect(); return r.width > 200 && r.height > 120; });
      if (c) requestAnimationFrame(function () { requestAnimationFrame(function () { setTimeout(hide, 250); }); });
      else if (Date.now() - t0 > 20000) hide();
      else setTimeout(wait, 150);
    })();
  }

  // visitor log: does nothing until assets/config.js is filled in. No consent bar on the viewers (SHIVAS_NOBAR).
  if (!window.SHIVAS_TRACK) {
    window.SHIVAS_NOBAR = true;
    var cf = document.createElement('script'); cf.src = base + 'assets/config.js';
    cf.onload = cf.onerror = function () { var t = document.createElement('script'); t.src = base + 'assets/track.js'; t.async = true; document.head.appendChild(t); };
    document.head.appendChild(cf);
  }
})();
