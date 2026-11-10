/* SHIVAS visitor log. Loaded by site.js on every page; does nothing until assets/config.js is filled in.
   Records each page view (page, device, browser, language, time zone, where the visitor came from) and, after the
   visitor presses OK, their approximate location, network / company name (looked up from the IP address) and a
   random visitor number, so repeat visits and a later enquiry can be tied together. Enquiries and "ask our engineer"
   requests are always sent, because the visitor sends them. Writes to the SHIVAS Google Sheet (sheetUrl). */
(function () {
  'use strict';
  var C = window.SHIVAS_CONFIG || {};
  var ON = !!(C.sheetUrl || C.ga4 || C.companyScript);
  var UA = navigator.userAgent || '';
  var BOT = /bot|crawl|spider|slurp|preview|headless|lighthouse|pingdom|monitor/i.test(UA) || navigator.webdriver === true;
  var me = (document.currentScript && document.currentScript.src) || '';
  var ROOT = me.replace(/assets\/track\.js(\?.*)?$/, '');
  function store(kind, k, v) {
    try { var s = window[kind]; if (v === undefined) return s.getItem(k); if (v === null) s.removeItem(k); else s.setItem(k, v); } catch (e) {}
    return null;
  }
  var ls = function (k, v) { return store('localStorage', k, v); }, ss = function (k, v) { return store('sessionStorage', k, v); };
  var rid = function () { return Math.random().toString(36).slice(2, 9) + Date.now().toString(36).slice(-5); };
  var consent = ls('shivas.consent');                          // 'yes' | 'no' | null (not asked yet)
  if (!consent && navigator.globalPrivacyControl === true) consent = 'no';

  /* ---------- what every row carries (nothing here identifies a person) ---------- */
  function device() {
    var os = /Android/i.test(UA) ? 'Android' : /iPhone|iPad|iPod/.test(UA) || (/Macintosh/.test(UA) && navigator.maxTouchPoints > 1) ? 'iOS' : /Windows/.test(UA) ? 'Windows' : /Mac OS X/.test(UA) ? 'macOS' : /CrOS/.test(UA) ? 'ChromeOS' : /Linux/.test(UA) ? 'Linux' : 'Other';
    var br = /Edg\//.test(UA) ? 'Edge' : /OPR\/|Opera/.test(UA) ? 'Opera' : /SamsungBrowser/.test(UA) ? 'Samsung Internet' : /CriOS|Chrome\//.test(UA) ? 'Chrome' : /FxiOS|Firefox\//.test(UA) ? 'Firefox' : /Safari\//.test(UA) ? 'Safari' : 'Other';
    var tab = /iPad|Tablet/.test(UA) || (/Android/.test(UA) && !/Mobile/.test(UA)) || (os === 'iOS' && !/iPhone|iPod/.test(UA));
    var model = (UA.match(/Android [\d.]+; ([^;)]+)\)/) || [])[1] || (/iPhone/.test(UA) ? 'iPhone' : /iPad/.test(UA) ? 'iPad' : '');
    if (model === 'K') model = '';
    return { device: tab ? 'Tablet' : /Mobi|iPhone|Android/.test(UA) ? 'Phone' : 'Computer', os: os, browser: br, model: model, screen: screen.width + '×' + screen.height };
  }
  function page() {
    var p = location.pathname, r = ROOT.replace(/^https?:\/\/[^/]+/, '');
    if (r && p.indexOf(r) === 0) p = p.slice(r.length);
    return (p.replace(/^\//, '') || 'index.html') + (location.hash && location.hash.length < 40 ? location.hash : '');
  }
  function ref() {
    var r = document.referrer; if (!r) return '';
    try { var u = new URL(r); if (u.host === location.host) return ''; return /google\.|bing\.|duckduckgo|yahoo\.|yandex/.test(u.host) ? u.host + ' (search)' : r.slice(0, 200); } catch (e) { return ''; }
  }
  var Q = new URLSearchParams(location.search), D = device(), PV = rid(), T0 = Date.now(), maxScroll = 0;
  var tz = ''; try { tz = Intl.DateTimeFormat().resolvedOptions().timeZone || ''; } catch (e) {}
  var BASE = {
    pv: PV, page: page(), title: (document.title || '').replace(/\s*\|\s*SHIVAS.*$/, ''), ref: ref(),
    utm: ['utm_source', 'utm_medium', 'utm_campaign'].map(function (k) { return Q.get(k); }).filter(Boolean).join(' / '),
    lang: navigator.language || '', tz: tz, device: D.device, os: D.os, browser: D.browser, model: D.model, screen: D.screen
  };

  /* ---------- with the visitor's OK: visitor number, visit count, location and network ---------- */
  var geo = null, ids = null;
  try { geo = JSON.parse(ss('shivas.geo') || 'null'); } catch (e) {}
  function makeIds() {
    var vid = ls('shivas.vid'); if (!vid) { vid = 'V-' + rid(); ls('shivas.vid', vid); ls('shivas.first', new Date().toISOString().slice(0, 10)); }
    var sid = ss('shivas.sid'); if (!sid) { sid = rid(); ss('shivas.sid', sid); ls('shivas.vn', String(+(ls('shivas.vn') || 0) + 1)); }
    ids = { visitor: vid, visit: +(ls('shivas.vn') || 1), first: ls('shivas.first') || '', session: sid };
  }
  function timeout(p, ms) { return Promise.race([p, new Promise(function (_, no) { setTimeout(no, ms); })]); }
  function lookup() {
    if (geo) return Promise.resolve(geo);
    var a = function () { return timeout(fetch('https://ipapi.co/json/'), 3500).then(function (r) { return r.json(); }).then(function (j) { if (j.error) throw 0; return { ip: j.ip, city: j.city, region: j.region, country: j.country_name, org: j.org, asn: j.asn }; }); };
    var b = function () { return timeout(fetch('https://ipwho.is/'), 3500).then(function (r) { return r.json(); }).then(function (j) { if (j.success === false) throw 0; var c = j.connection || {}; return { ip: j.ip, city: j.city, region: j.region, country: j.country, org: c.org || c.isp, asn: c.asn ? 'AS' + c.asn : '' }; }); };
    return a().catch(b).then(function (g) { geo = g; ss('shivas.geo', JSON.stringify(g)); return g; }).catch(function () { return null; });
  }

  /* ---------- sending ---------- */
  function body(type, data) {
    var p = { type: type, at: new Date().toISOString() }, k;
    for (k in BASE) p[k] = BASE[k];
    if (consent === 'yes') { if (!ids) makeIds(); for (k in ids) p[k] = ids[k]; if (geo) for (k in geo) p[k] = geo[k]; }
    for (k in (data || {})) p[k] = data[k];
    return JSON.stringify(p);
  }
  function post(b) {
    if (!C.sheetUrl) return false;
    try {
      if (navigator.sendBeacon && navigator.sendBeacon(C.sheetUrl, new Blob([b], { type: 'text/plain;charset=utf-8' }))) return true;
      fetch(C.sheetUrl, { method: 'POST', mode: 'no-cors', keepalive: true, headers: { 'Content-Type': 'text/plain;charset=utf-8' }, body: b });
      return true;
    } catch (e) { return false; }
  }
  var ready = Promise.resolve();
  function send(type, data) { ready.then(function () { post(body(type, data)); }); }

  /* ---------- optional Google Analytics and company-identification service (only after OK) ---------- */
  var extrasOn = false;
  function extras() {
    if (extrasOn || consent !== 'yes') return; extrasOn = true;
    var add = function (src) { var s = document.createElement('script'); s.async = true; s.src = src; document.head.appendChild(s); };
    if (C.ga4) {
      add('https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(C.ga4));
      window.dataLayer = window.dataLayer || []; window.gtag = function () { window.dataLayer.push(arguments); };
      window.gtag('js', new Date()); window.gtag('config', C.ga4);
    }
    if (C.companyScript) add(C.companyScript);
  }

  /* ---------- the one-time question ---------- */
  function ask() {
    var st = document.createElement('style');
    st.textContent = '.sv-bar{position:fixed;left:50%;transform:translateX(-50%);bottom:calc(var(--spv-bottom,0px) + 12px + env(safe-area-inset-bottom,0px));z-index:9999;width:min(680px,calc(100% - 24px));display:flex;flex-wrap:wrap;gap:10px 14px;align-items:center;padding:12px 14px;border-radius:12px;background:#0b1622;color:#e7edf3;border:1px solid #2d4860;box-shadow:0 12px 40px rgba(0,0,0,.35);font:14px/1.45 "Archivo","Helvetica Neue",Arial,sans-serif}' +
      '.sv-bar p{margin:0;flex:1 1 300px}.sv-bar a{color:#ffc35a}.sv-bar .sv-b{display:flex;gap:8px;margin-left:auto}' +
      '.sv-bar button{font:600 13px/1 inherit;font-family:inherit;min-height:38px;padding:0 16px;border-radius:999px;cursor:pointer;border:1px solid #2d4860;background:transparent;color:#e7edf3}' +
      '.sv-bar button.y{background:#e8a317;border-color:#e8a317;color:#111}';
    document.head.appendChild(st);
    var bar = document.createElement('div'); bar.className = 'sv-bar'; bar.setAttribute('role', 'region'); bar.setAttribute('aria-label', 'Visit records');
    bar.innerHTML = '<p>SHIVAS records which pages are visited, from what device, country and company network, so we can follow up enquiries. <a href="' + ROOT + 'privacy.html">Privacy</a></p><div class="sv-b"><button type="button" class="n">No thanks</button><button type="button" class="y">OK</button></div>';
    bar.addEventListener('click', function (e) { var b = e.target.closest('button'); if (!b) return; choose(b.className === 'y' ? 'yes' : 'no'); bar.remove(); });
    (document.body || document.documentElement).appendChild(bar);
  }
  function choose(v) {
    var was = consent; consent = v; ls('shivas.consent', v);
    if (v === 'yes' && was !== 'yes') { ready = lookup().then(function () { send('update', {}); extras(); }); }
    if (v === 'no') { ls('shivas.vid', null); ls('shivas.vn', null); ls('shivas.first', null); ss('shivas.geo', null); ss('shivas.sid', null); ids = null; geo = null; }
  }

  /* ---------- public: calculators and forms report through this ---------- */
  var sentLeads = {};
  window.SHIVAS_TRACK = {
    on: ON && !!C.sheetUrl,
    event: function (type, data) { if (!ON || BOT) return false; send(type, data); return !!C.sheetUrl; },
    lead: function (d) {
      if (!C.sheetUrl) return false;
      var key = JSON.stringify(d).slice(0, 400); if (sentLeads[key]) return true; sentLeads[key] = 1;
      send('lead', d); return true;
    },
    consent: function (v) { if (v === 'yes' || v === 'no') choose(v); return consent; }
  };
  if (!ON || BOT) return;

  /* ---------- page view, time on page, clicks that matter, enquiry form ---------- */
  if (consent === 'yes') { ready = lookup(); extras(); }
  send('view', {});
  // SHIVAS_NOBAR (set by the 3D viewers): no consent bar, it would cover the viewer's controls. A visitor's earlier
  // choice on the main site still applies; without one only the plain page view is sent (no location, no visitor number).
  if (!consent && !window.SHIVAS_NOBAR) { if (document.body) ask(); else document.addEventListener('DOMContentLoaded', ask); }
  addEventListener('scroll', function () {
    var h = document.documentElement, m = Math.round(100 * (scrollY + innerHeight) / Math.max(h.scrollHeight, 1)); if (m > maxScroll) maxScroll = Math.min(m, 100);
  }, { passive: true });
  var timed = false;
  function leave() { if (timed) return; timed = true; post(body('time', { secs: Math.round((Date.now() - T0) / 1000), scroll: maxScroll })); }
  document.addEventListener('visibilitychange', function () { if (document.visibilityState === 'hidden') leave(); });
  addEventListener('pagehide', leave);
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href]'); if (!a) return;
    var h = a.getAttribute('href') || '', kind = /wa\.me|whatsapp/i.test(h) ? 'WhatsApp' : /^mailto:/i.test(h) ? 'Email' : /^tel:/i.test(h) ? 'Phone' : /(^|\/)v\/[^/]+\.html/.test(h) ? '3D viewer' : /^https?:/i.test(h) && h.indexOf(location.host) < 0 ? 'Other site' : '';
    if (kind) send('click', { detail: kind + ': ' + (h.replace(/^(mailto:|tel:)/, '').split('?')[0] + ' · ' + (a.textContent || '').trim().slice(0, 60)) });
  }, true);
  document.addEventListener('submit', function (e) {
    var f = e.target; if (!f || f.id !== 'qForm') return;
    var v = function (id) { var el = document.getElementById(id); return el ? (el.value || '').trim() : ''; };
    var opt = function (id) { var el = document.getElementById(id); return el && el.selectedOptions && el.selectedOptions[0] ? el.selectedOptions[0].textContent : ''; };
    if (!v('qName') || !v('qContact')) return;
    var ok = window.SHIVAS_TRACK.lead({ source: 'Enquiry form', div: v('qDiv'), name: v('qName'), company: v('qCo'), contact: v('qContact'), place: v('qCountry'), product: [opt('qDiv'), opt('qProd')].filter(Boolean).join(' · '), message: v('qMsg'), to: opt('qTo') });
    if (ok) setTimeout(function () { var p = document.querySelector('#qOut p'); if (p) p.textContent = 'Sent to SHIVAS. We will get back to you. For a faster reply, also send it on WhatsApp:'; }, 0);
  }, true);
})();
