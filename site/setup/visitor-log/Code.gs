/**
 * SHIVAS website visitor log — Google Apps Script for a Google Sheet.
 * Receives what the website sends (assets/track.js) and writes it to two tabs:
 *   Visits  – one row per page view: page, device, browser, country, city, network / company, time on page …
 *   Leads   – every enquiry form and "ask our engineer" request, with what that visitor looked at before.
 * Also: an email for every lead at once, a report of yesterday's visitors every morning at 8:00 (India time) and of the
 * last 7 days every Monday, sent to DIGEST_TO and to the Google account that set this up. Tabs Pages, Daily and Viewers
 * summarise the Visits tab.
 * Set up: see README.txt in this folder. Run setup() once, then Deploy → New deployment → Web app.
 */

// ---------------- settings ----------------
var ALERT_TECH = { to: 'info@shivastechnology.com', cc: 'shivastechnology@gmail.com' };   // galvanizing and wire drawing
var ALERT_REIN = { to: 'info@shivasasia.com', cc: 'shivasasia@gmail.com' };               // SHIVAS Reinplast
var DIGEST_TO = 'info@shivastechnology.com';                                              // morning summary
var KEEP_DAYS = 730;                                                                      // visit rows older than this are deleted (privacy notice says 24 months)

// ---------------- columns ----------------
var VISIT_COLS = [
  ['at', 'Time'], ['type', 'Type'], ['page', 'Page'], ['title', 'Title'], ['visitor', 'Visitor'], ['visit', 'Visit no.'], ['first', 'First seen'],
  ['device', 'Device'], ['model', 'Model'], ['os', 'OS'], ['browser', 'Browser'], ['screen', 'Screen'], ['lang', 'Language'], ['tz', 'Time zone'],
  ['ref', 'Came from'], ['utm', 'Campaign'], ['country', 'Country'], ['region', 'Region'], ['city', 'City'], ['org', 'Network / company'],
  ['nettype', 'Network type'], ['ip', 'IP address'], ['secs', 'Seconds on page'], ['scroll', 'Scrolled %'], ['detail', 'Detail'], ['pv', 'pv']
];
var LEAD_COLS = [
  ['at', 'Time'], ['source', 'Source'], ['name', 'Name'], ['company', 'Company'], ['contact', 'Phone / email'], ['email', 'Email'], ['place', 'Place given'],
  ['product', 'Product'], ['message', 'Message'], ['to', 'Sent to'], ['page', 'Page'], ['visitor', 'Visitor'], ['org', 'Network / company'],
  ['city', 'City'], ['country', 'Country'], ['device', 'Device'], ['seen', 'Pages seen before']
];

// ---------------- network type from the IP owner's name ----------------
var CLOUD = /\b(google|amazon|aws|microsoft|azure|cloudflare|akamai|fastly|digitalocean|ovh|hetzner|linode|vultr|oracle cloud|alibaba|tencent|contabo|leaseweb|m247|datacamp|nordvpn|expressvpn|proton|zscaler)\b/i;
var ISP = /\b(jio|reliance jio|airtel|bharti|vodafone|idea|bsnl|mtnl|act fibernet|atria convergence|beam telecom|hathway|tata (teleservices|play|sky)|you broadband|excitel|spectra|tikona|alliance broadband|gtpl|den networks|asianet|railtel|sify|netplus|fastway|siti broadband|ortel|broadband|internet service|telecom|tata communications|comcast|charter|spectrum|verizon|at&t|t-mobile|sprint|cox|virgin media|british telecom|sky uk|orange|telefonica|deutsche telekom|vodafone|etisalat|emirates integrated|omantel|ooredoo|saudi telecom|stc|zain|mobily|batelco|ptcl|grameenphone|robi|telstra|optus|singtel|starhub|maxis|telkom|turk telekom)\b/i;
function netType(org) {
  if (!org) return '';
  if (CLOUD.test(org)) return 'Cloud / VPN';
  if (ISP.test(org)) return 'Home / mobile';
  return 'Company network';
}

// ---------------- web app ----------------
function doGet() { return ContentService.createTextOutput('SHIVAS visitor log is running.'); }

function doPost(e) {
  var lock = LockService.getScriptLock();
  try { lock.waitLock(10000); } catch (err) { /* write anyway */ }
  try {
    var d = JSON.parse((e && e.postData && e.postData.contents) || '{}');
    if (!d || !d.type || String(d.type).length > 20) return reply('bad');
    var cache = CacheService.getScriptCache(), n = +(cache.get('rate') || 0);          // flood guard: 300 rows a minute at most
    if (n > 300) return reply('busy');
    cache.put('rate', String(n + 1), 60);
    clean(d);
    d.nettype = netType(d.org);
    var book = book_(), visits = book.getSheetByName('Visits');
    if (d.type === 'time' || d.type === 'update') { update_(visits, d); return reply('ok'); }
    if (d.type === 'lead') {
      d.seen = history_(visits, d.visitor);
      book.getSheetByName('Leads').appendRow(row_(LEAD_COLS, d));
      d.detail = d.source + ': ' + [d.name, d.company, d.contact].filter(Boolean).join(' · ');
      alert_(d);
    }
    visits.appendRow(row_(VISIT_COLS, d));
    return reply('ok');
  } finally { try { lock.releaseLock(); } catch (err) {} }
}
function reply(t) { return ContentService.createTextOutput(t); }
function clean(d) {
  for (var k in d) {
    if (typeof d[k] === 'string') d[k] = d[k].slice(0, k === 'message' || k === 'detail' || k === 'seen' ? 3000 : 300);
  }
  var t = new Date(d.at); d.at = isNaN(t) ? new Date() : t;
}
function book_() {
  var id = PropertiesService.getScriptProperties().getProperty('SHEET');
  return id ? SpreadsheetApp.openById(id) : SpreadsheetApp.getActiveSpreadsheet();
}
function row_(cols, d) {   // text from the web is never run as a formula (+91… stays text too)
  return cols.map(function (c) { var v = d[c[0]]; if (v === undefined || v === null) return ''; return typeof v === 'string' && /^[=+\-@]/.test(v) ? "'" + v : v; });
}
function col_(cols, key) { for (var i = 0; i < cols.length; i++) if (cols[i][0] === key) return i + 1; return 0; }

// time on page and the visitor's OK arrive after the page view: fill them into that row
function update_(sh, d) {
  var last = sh.getLastRow(); if (last < 2 || !d.pv) return;
  var from = Math.max(2, last - 799), pvCol = col_(VISIT_COLS, 'pv');
  var pvs = sh.getRange(from, pvCol, last - from + 1, 1).getValues();
  for (var i = pvs.length - 1; i >= 0; i--) {
    if (pvs[i][0] !== d.pv) continue;
    var r = from + i, keys = d.type === 'time' ? ['secs', 'scroll'] : ['visitor', 'visit', 'first', 'country', 'region', 'city', 'org', 'nettype', 'ip'];
    keys.forEach(function (k) { if (d[k] !== undefined && d[k] !== '') sh.getRange(r, col_(VISIT_COLS, k)).setValue(d[k]); });
    return;
  }
}

// pages a visitor looked at before getting in touch
function history_(sh, visitor) {
  if (!visitor) return '';
  var last = sh.getLastRow(); if (last < 2) return '';
  var from = Math.max(2, last - 4999), v = sh.getRange(from, 1, last - from + 1, VISIT_COLS.length).getValues();
  var cV = col_(VISIT_COLS, 'visitor') - 1, cT = col_(VISIT_COLS, 'title') - 1, cA = 0, cY = col_(VISIT_COLS, 'type') - 1, cD = col_(VISIT_COLS, 'detail') - 1, out = [];
  v.forEach(function (r) {
    if (r[cV] !== visitor) return;
    var when = Utilities.formatDate(new Date(r[cA]), 'Asia/Kolkata', 'd MMM HH:mm');
    if (r[cY] === 'view') out.push(when + '  ' + r[cT]);
    else if (r[cY] === 'calc' || r[cY] === 'click') out.push(when + '  ' + (r[cY] === 'calc' ? 'Calculator: ' : 'Clicked ') + String(r[cD]).split('\n')[0]);
  });
  return out.slice(-40).join('\n');
}

// an email for every lead
function alert_(d) {
  var who = (d.div === 'rein' || /reinplast/i.test(d.product || '')) ? ALERT_REIN : ALERT_TECH;
  var line = function (k, v) { return v ? '<tr><td style="padding:3px 12px 3px 0;color:#566778">' + k + '</td><td style="padding:3px 0"><b>' + esc(v) + '</b></td></tr>' : ''; };
  var html = '<div style="font:14px/1.5 Arial,sans-serif;color:#13202c">' +
    '<p style="font-size:16px"><b>New website enquiry</b> · ' + esc(d.source) + '</p><table>' +
    line('Name', d.name) + line('Company', d.company) + line('Phone / email', d.contact) + line('Email', d.email) + line('Place given', d.place) +
    line('Product', d.product) + line('Sent to', d.to) + line('Network / company', d.org ? d.org + ' (' + d.nettype + ')' : '') +
    line('Location', [d.city, d.region, d.country].filter(Boolean).join(', ')) + line('Device', [d.device, d.model, d.os, d.browser].filter(Boolean).join(' · ')) + '</table>' +
    (d.message ? '<p><b>Message / calculation</b></p><pre style="white-space:pre-wrap;font:13px/1.45 monospace;background:#f3f5f7;padding:10px">' + esc(d.message) + '</pre>' : '') +
    (d.seen ? '<p><b>What this visitor looked at</b></p><pre style="white-space:pre-wrap;font:13px/1.45 monospace">' + esc(d.seen) + '</pre>' : '') +
    '<p style="color:#566778">Reply directly to the customer. All enquiries are in the Leads tab of the visitor log.</p></div>';
  MailApp.sendEmail({ to: who.to, cc: who.cc, subject: 'Website enquiry: ' + [d.name, d.company].filter(Boolean).join(' · ') + ' — ' + (d.product || d.source), htmlBody: html, name: 'SHIVAS website' });
}
function esc(s) { return String(s).replace(/[&<>]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]; }); }

// ---------------- every morning: yesterday's visitors ----------------
// ---------------- reports ----------------
// Who gets them: DIGEST_TO, the Google account that set this script up (so the owner always gets the report, without
// putting a personal address in this public file) and any extra addresses in the script property REPORT_TO
// (Apps Script: Project settings → Script properties → REPORT_TO, comma-separated).
function recipients_() {
  var list = [DIGEST_TO];
  try { var me = Session.getEffectiveUser().getEmail(); if (me) list.push(me); } catch (e) {}
  var extra = PropertiesService.getScriptProperties().getProperty('REPORT_TO');
  if (extra) list = list.concat(extra.split(/[,;\s]+/));
  var seen = {};
  return list.map(function (x) { return String(x || '').trim(); }).filter(function (x) {
    var k = x.toLowerCase(); if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(k) || seen[k]) return false; seen[k] = 1; return true;
  }).join(',');
}

// everything that happened between two days (yyyy-MM-dd, India time; 'from' included, 'to' not)
function summary_(from, to) {
  var sh = book_().getSheetByName('Visits'), last = sh.getLastRow(), tz = 'Asia/Kolkata';
  var s = { views: 0, people: {}, anon: 0, countries: {}, devices: {}, firms: {}, leads: [], calcs: [], clicks: [], pages: {}, visitors: {} };
  if (last < 2) return s;
  var start = Math.max(2, last - 29999), rows = sh.getRange(start, 1, last - start + 1, VISIT_COLS.length).getValues();
  var c = {}; VISIT_COLS.forEach(function (x, i) { c[x[0]] = i; });
  var where = function (r) { return [r[c.city], r[c.country]].filter(Boolean).join(', '); };
  rows.forEach(function (r) {
    var day = Utilities.formatDate(new Date(r[c.at]), tz, 'yyyy-MM-dd');
    if (day < from || day >= to) return;
    var t = r[c.type], title = String(r[c.title] || r[c.page] || ''), page = String(r[c.page] || '');
    if (t === 'view') {
      s.views++;
      var vid = r[c.visitor]; if (vid) s.people[vid] = 1; else s.anon++;
      var co = r[c.country] || (r[c.tz] ? 'Time zone ' + r[c.tz] : 'Unknown'); s.countries[co] = (s.countries[co] || 0) + 1;
      s.devices[r[c.device] || 'Unknown'] = (s.devices[r[c.device] || 'Unknown'] || 0) + 1;
      var key = page.split('#')[0] || title, pg = s.pages[key] = s.pages[key] || { title: title, page: key, n: 0, secs: 0, timed: 0, who: {} };
      pg.n++; if (+r[c.secs]) { pg.secs += +r[c.secs]; pg.timed++; } pg.who[vid || 'anon' + s.anon] = 1;
      if (vid) {
        var v = s.visitors[vid] = s.visitors[vid] || { id: vid, n: 0, secs: 0, pages: [], where: where(r), org: r[c.org] || '', net: r[c.nettype] || '', device: [r[c.device], r[c.model], r[c.os]].filter(Boolean).join(' · '), visit: r[c.visit], ref: r[c.ref] || '' };
        v.n++; v.secs += +r[c.secs] || 0; if (v.pages.indexOf(title) < 0) v.pages.push(title);
      }
      if (r[c.nettype] === 'Company network') {
        var f = s.firms[r[c.org]] = s.firms[r[c.org]] || { n: 0, secs: 0, where: where(r), pages: {} };
        f.n++; f.secs += +r[c.secs] || 0; f.pages[title] = 1;
      }
    } else if (t === 'lead') s.leads.push(r[c.detail]);
    else if (t === 'calc') s.calcs.push(String(r[c.detail]).split('\n')[0] + (r[c.org] ? ' — ' + r[c.org] : '') + (r[c.city] ? ', ' + r[c.city] : ''));
    else if (t === 'click' && /^(WhatsApp|Email|Phone|3D viewer)/.test(r[c.detail])) s.clicks.push(r[c.detail] + (r[c.org] ? ' — ' + r[c.org] : '') + (r[c.city] ? ', ' + r[c.city] : ''));
  });
  return s;
}

function report_(s, label) {
  var grey = 'color:#566778', th = 'text-align:left;padding:4px 10px 4px 0;border-bottom:1px solid #dde5ee;font-weight:600', td = 'padding:4px 10px 4px 0;border-bottom:1px solid #eef3f8;vertical-align:top';
  var mins = function (secs) { return secs ? (secs < 90 ? Math.round(secs) + ' s' : Math.round(secs / 60) + ' min') : ''; };
  var top = function (o, n) { return Object.keys(o).sort(function (a, b) { return o[b] - o[a]; }).slice(0, n).map(function (k) { return esc(k) + ' <b>' + o[k] + '</b>'; }).join(' · '); };
  var li = function (a) { return a.length ? '<ul>' + a.slice(0, 40).map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ul>' : '<p style="' + grey + '">None</p>'; };
  var table = function (head, rows) { return rows.length ? '<table style="border-collapse:collapse;font-size:13px"><tr>' + head.map(function (h) { return '<th style="' + th + '">' + h + '</th>'; }).join('') + '</tr>' + rows.join('') + '</table>' : '<p style="' + grey + '">None</p>'; };
  var pages = Object.keys(s.pages).map(function (k) { return s.pages[k]; }).sort(function (a, b) { return b.n - a.n; });
  var pageRow = function (p) { return '<tr><td style="' + td + '">' + esc(p.title) + '<br><span style="' + grey + ';font-size:12px">' + esc(p.page) + '</span></td><td style="' + td + '"><b>' + p.n + '</b></td><td style="' + td + '">' + Object.keys(p.who).length + '</td><td style="' + td + '">' + mins(p.timed ? p.secs / p.timed : 0) + '</td></tr>'; };
  var models = pages.filter(function (p) { return /^v\//.test(p.page); });
  var vis = Object.keys(s.visitors).map(function (k) { return s.visitors[k]; }).sort(function (a, b) { return b.n - a.n; });
  var firmList = Object.keys(s.firms).sort(function (a, b) { return s.firms[b].n - s.firms[a].n; }).slice(0, 40).map(function (k) {
    var f = s.firms[k]; return '<li><b>' + esc(k) + '</b> · ' + esc(f.where) + ' · ' + f.n + ' pages, ' + Math.round(f.secs / 60) + ' min<br><span style="' + grey + '">' + esc(Object.keys(f.pages).slice(0, 8).join(' · ')) + '</span></li>';
  }).join('');
  var url = ''; try { url = book_().getUrl(); } catch (e) {}
  return '<div style="font:14px/1.5 Arial,sans-serif;color:#13202c;max-width:760px">' +
    '<p style="font-size:17px;margin:0 0 4px"><b>SHIVAS website · ' + esc(label) + '</b></p>' +
    '<p style="margin:0 0 14px">' + s.views + ' page views · ' + Object.keys(s.people).length + ' visitors who pressed OK · ' + s.anon + ' views from visitors who did not · ' + s.leads.length + ' enquiries</p>' +
    (url ? '<p><a href="' + url + '" style="color:#1f4e79;font-weight:600">Open the visitor log (Google Sheet)</a> <span style="' + grey + '">· tabs Visits, Pages, Daily, Viewers, Companies, Leads</span></p>' : '') +
    '<h3 style="margin:18px 0 6px">Enquiries</h3>' + li(s.leads) +
    '<h3 style="margin:18px 0 6px">Pages viewed</h3>' + table(['Page', 'Views', 'Visitors', 'Avg time'], pages.slice(0, 60).map(pageRow)) +
    '<h3 style="margin:18px 0 6px">3D models opened</h3>' + table(['Model', 'Views', 'Visitors', 'Avg time'], models.map(pageRow)) +
    '<h3 style="margin:18px 0 6px">Visitors and what they looked at</h3><p style="' + grey + ';margin:0 0 6px">Visitors who pressed OK on the bar. Others are counted above but not listed. Home and mobile connections cannot be named.</p>' +
    table(['Visitor', 'From', 'Network', 'Pages they viewed'], vis.slice(0, 60).map(function (v) {
      return '<tr><td style="' + td + '">' + esc(v.id) + '<br><span style="' + grey + ';font-size:12px">visit ' + esc(v.visit || 1) + ' · ' + v.n + ' views · ' + mins(v.secs) + '</span></td><td style="' + td + '">' + esc(v.where) + '<br><span style="' + grey + ';font-size:12px">' + esc(v.device) + '</span></td><td style="' + td + '">' + esc(v.org) + (v.net ? '<br><span style="' + grey + ';font-size:12px">' + esc(v.net) + '</span>' : '') + '</td><td style="' + td + '">' + esc(v.pages.slice(0, 12).join(' · ')) + (v.ref ? '<br><span style="' + grey + ';font-size:12px">came from ' + esc(v.ref) + '</span>' : '') + '</td></tr>';
    })) +
    '<h3 style="margin:18px 0 6px">Companies</h3><p style="' + grey + ';margin:0">Visits from office networks</p>' + (firmList ? '<ol>' + firmList + '</ol>' : '<p style="' + grey + '">None identified</p>') +
    '<h3 style="margin:18px 0 6px">WhatsApp, email, phone and 3D taps</h3>' + li(s.clicks) +
    '<h3 style="margin:18px 0 6px">Calculators used</h3>' + li(s.calcs) +
    '<p><b>Countries</b><br>' + (top(s.countries, 12) || 'None') + '</p><p><b>Devices</b><br>' + (top(s.devices, 5) || 'None') + '</p>' +
    '<p style="' + grey + '">Every row is in the Visits tab. Visit rows older than ' + KEEP_DAYS + ' days are deleted; enquiries are kept.</p></div>';
}

function day_(offset) { return Utilities.formatDate(new Date(Date.now() + offset * 864e5), 'Asia/Kolkata', 'yyyy-MM-dd'); }

// every morning at 8:00: yesterday
function dailyDigest() {
  var y = day_(-1), s = summary_(y, day_(0));
  if (s.views || s.leads.length) MailApp.sendEmail({ to: recipients_(), subject: 'SHIVAS website ' + y + ': ' + s.views + ' views · ' + Object.keys(s.people).length + ' visitors · ' + Object.keys(s.firms).length + ' companies · ' + s.leads.length + ' enquiries', htmlBody: report_(s, y), name: 'SHIVAS website' });
  cleanup();
}

// every Monday at 8:30: the last 7 days
function weeklyDigest() {
  var from = day_(-7), to = day_(0), s = summary_(from, to), label = 'week ' + from + ' to ' + day_(-1);
  MailApp.sendEmail({ to: recipients_(), subject: 'SHIVAS website ' + label + ': ' + s.views + ' views · ' + Object.keys(s.people).length + ' visitors · ' + s.leads.length + ' enquiries', htmlBody: report_(s, label), name: 'SHIVAS website' });
}

// run this once by hand after setup: sends today's report so far, to check the emails arrive
function sendTestReport() {
  var t = day_(0), s = summary_(t, day_(1));
  MailApp.sendEmail({ to: recipients_(), subject: 'SHIVAS website test report ' + t + ': ' + s.views + ' views so far', htmlBody: report_(s, t + ' so far (test)'), name: 'SHIVAS website' });
}

// visit rows older than KEEP_DAYS are deleted (enquiries in Leads are kept)
function cleanup() {
  var sh = book_().getSheetByName('Visits'), last = sh.getLastRow(); if (last < 3) return;
  var cut = new Date(Date.now() - KEEP_DAYS * 864e5), t = sh.getRange(2, 1, last - 1, 1).getValues(), n = 0;
  while (n < t.length && new Date(t[n][0]) < cut) n++;
  if (n) sh.deleteRows(2, Math.min(n, last - 2));
}

// ---------------- run once ----------------
function setup() {
  var book = SpreadsheetApp.getActiveSpreadsheet();
  PropertiesService.getScriptProperties().setProperty('SHEET', book.getId());
  [['Visits', VISIT_COLS], ['Leads', LEAD_COLS]].forEach(function (x) {
    var sh = book.getSheetByName(x[0]) || book.insertSheet(x[0]);
    sh.getRange(1, 1, 1, x[1].length).setValues([x[1].map(function (c) { return c[1]; })]).setFontWeight('bold').setBackground('#1F4E79').setFontColor('#ffffff');
    sh.setFrozenRows(1);
    sh.getRange('A:A').setNumberFormat('dd mmm yyyy hh:mm');
  });
  book.getSheetByName('Visits').hideColumns(col_(VISIT_COLS, 'pv'));
  // Companies tab: every office network seen, newest first
  var cs = book.getSheetByName('Companies') || book.insertSheet('Companies');
  var L = function (k) { var n = col_(VISIT_COLS, k), s = ''; while (n) { var m = (n - 1) % 26; s = String.fromCharCode(65 + m) + s; n = (n - 1 - m) / 26; } return s; };
  cs.getRange('A1').setFormula('=IFERROR(QUERY(Visits!A:' + L('pv') + ',"select ' + L('org') + ', ' + L('city') + ', ' + L('country') + ', count(' + L('page') + '), max(A) where ' + L('nettype') + " = 'Company network' and " + L('type') + " = 'view' group by " + L('org') + ', ' + L('city') + ', ' + L('country') + ' order by max(A) desc label ' + L('org') + " 'Company network', " + L('city') + " 'City', " + L('country') + " 'Country', count(" + L('page') + ") 'Page views', max(A) 'Last visit'\",1),\"No company visits yet\")");
  // Pages, Daily and Viewers tabs: live summaries of the Visits tab
  var tab = function (name, formula) { var t = book.getSheetByName(name) || book.insertSheet(name); t.getRange('A1').setFormula(formula); t.setFrozenRows(1); return t; };
  var V = 'Visits!A:' + L('pv'), q = function (sel) { return '=IFERROR(QUERY(' + V + ',"' + sel + '",1),"No page views yet")'; };
  tab('Pages', q('select ' + L('title') + ', ' + L('page') + ', count(' + L('type') + '), avg(' + L('secs') + '), max(A) where ' + L('type') + " = 'view' group by " + L('title') + ', ' + L('page') + ' order by count(' + L('type') + ') desc label ' + L('title') + " 'Page', " + L('page') + " 'Address', count(" + L('type') + ") 'Views', avg(" + L('secs') + ") 'Avg seconds', max(A) 'Last view'"));
  tab('Daily', q('select toDate(A), count(' + L('type') + ') where ' + L('type') + " = 'view' group by toDate(A) order by toDate(A) desc label toDate(A) 'Day', count(" + L('type') + ") 'Page views'")).getRange('A:A').setNumberFormat('ddd dd mmm yyyy');
  tab('Viewers', q('select ' + L('visitor') + ', max(A), count(' + L('type') + '), ' + L('org') + ', ' + L('city') + ', ' + L('country') + ', ' + L('device') + ' where ' + L('type') + " = 'view' and " + L('visitor') + " <> '' group by " + L('visitor') + ', ' + L('org') + ', ' + L('city') + ', ' + L('country') + ', ' + L('device') + ' order by max(A) desc label ' + L('visitor') + " 'Visitor', max(A) 'Last seen', count(" + L('type') + ") 'Page views', " + L('org') + " 'Network / company', " + L('city') + " 'City', " + L('country') + " 'Country', " + L('device') + " 'Device'"));
  var old = book.getSheetByName('Sheet1'); if (old && old.getLastRow() === 0 && book.getSheets().length > 1) book.deleteSheet(old);
  ScriptApp.getProjectTriggers().forEach(function (t) { if (/^(dailyDigest|weeklyDigest)$/.test(t.getHandlerFunction())) ScriptApp.deleteTrigger(t); });
  ScriptApp.newTrigger('dailyDigest').timeBased().atHour(8).everyDays(1).inTimezone('Asia/Kolkata').create();
  ScriptApp.newTrigger('weeklyDigest').timeBased().onWeekDay(ScriptApp.WeekDay.MONDAY).atHour(8).nearMinute(30).inTimezone('Asia/Kolkata').create();
  MailApp.getRemainingDailyQuota();   // asks for the email permission now, not on the first enquiry
}
