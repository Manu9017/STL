/* Runs site/setup/visitor-log/Code.gs (Version 6.1, reports on Monday and Thursday) in Node against stand-ins for the Google services (a Sheet that keeps
   its rows, MailApp, properties, triggers, Utilities.zip) and checks what it would write and email. The weekly Excel file
   is really built: its parts are zipped and opened with Python's openpyxl. Nothing leaves this machine.
     node tools/test_visitor_log.cjs                       (run from the repo root; needs python3 with openpyxl)
     node tools/test_visitor_log.cjs report.html out.xlsx  (also saves the sample weekly email and its Excel file)
   The sample fortnight uses made-up visitors and companies ("Example ...", "Sample ..."), never real data. */
const fs = require('fs'), os = require('os'), path = require('path'), vm = require('vm'), cp = require('child_process');
const SRC = fs.readFileSync('site/setup/visitor-log/Code.gs', 'utf8');
const MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], WD = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
const formatDate = (d, tz, f) => {   // India time, the patterns Code.gs uses
  const x = new Date(new Date(d).getTime() + 330 * 60000), p = n => String(n).padStart(2, '0');
  return f.replace(/yyyy|MMM|MM|dd|d|HH|mm|EEE|u/g, t => ({ yyyy: x.getUTCFullYear(), MMM: MON[x.getUTCMonth()], MM: p(x.getUTCMonth() + 1), dd: p(x.getUTCDate()),
    d: x.getUTCDate(), HH: p(x.getUTCHours()), mm: p(x.getUTCMinutes()), EEE: WD[x.getUTCDay()], u: String((x.getUTCDay() + 6) % 7 + 1) })[t]);
};
let failed = 0;
const check = (ok, what) => { console.log((ok ? '  ok    ' : '  FAIL  ') + what); if (!ok) failed++; };
// a clock fixed at 'now' (ms) for the script, to run it as on a given Monday or Thursday
const fakeDate = now => class D extends Date { constructor(...a) { if (a.length) super(...a); else super(now); } static now() { return now; } };
const blob = (data, type, name) => ({ data: String(data), type, name, setContentType(t) { this.type = t; return this; }, setName(n) { this.name = n; return this; }, getName() { return this.name; } });

function run(opts = {}) {
  const mails = [], props = Object.assign({ SHEET: 'SHEET-ID' }, opts.props || {}), tabs = { Visits: [], Leads: [] };
  const triggers = (opts.triggers || []).map(h => ({ h })), made = [], deleted = [];
  const sheet = n => ({
    appendRow: r => tabs[n].push(r.slice()), getLastRow: () => tabs[n].length + 1,
    getRange: (row, col, nr, nc) => ({ getValues: () => tabs[n].slice(row - 2, row - 2 + (nr || 1)).map(r => r.slice(col - 1, col - 1 + (nc || 1))), setValue: v => { tabs[n][row - 2][col - 1] = v; } }),
    deleteRows: (row, k) => tabs[n].splice(row - 2, k)
  });
  const book = { getId: () => 'SHEET-ID', getUrl: () => 'https://docs.google.com/spreadsheets/d/SHEET-ID', getSheetByName: n => tabs[n] ? sheet(n) : null };
  const trig = h => { const o = { timeBased: () => o, onWeekDay: d => { o.day = d; return o; }, atHour: x => { o.hour = x; return o; }, nearMinute: m => { o.min = m; return o; }, everyDays: () => { o.daily = true; return o; }, inTimezone: z => { o.tz = z; return o; }, create: () => { made.push(Object.assign({ h }, o)); triggers.push({ h }); } }; return o; };
  const ctx = {
    console: { log() {} }, JSON, Date: opts.now ? fakeDate(opts.now) : Date, Math, String, Number, Object, isNaN, isFinite, encodeURIComponent,
    LockService: { getScriptLock: () => ({ waitLock() {}, releaseLock() {} }) },
    CacheService: { getScriptCache: () => ({ get: () => null, put() {} }) },
    ContentService: { createTextOutput: t => t },
    PropertiesService: { getScriptProperties: () => ({ getProperty: k => k in props ? props[k] : null, setProperty: (k, v) => { props[k] = v; }, deleteProperty: k => { delete props[k]; }, getKeys: () => Object.keys(props) }) },
    SpreadsheetApp: { getActiveSpreadsheet: () => book, openById: () => book, create: () => book },
    ScriptApp: { getProjectTriggers: () => triggers.map(t => ({ getHandlerFunction: () => t.h, _t: t })), deleteTrigger: t => { deleted.push(t._t.h); triggers.splice(triggers.indexOf(t._t), 1); }, newTrigger: trig, WeekDay: { MONDAY: 'MONDAY', THURSDAY: 'THURSDAY' } },
    MailApp: { sendEmail: m => { if (opts.mailFails) throw new Error('quota'); mails.push(m); }, getRemainingDailyQuota: () => 100 },
    Session: { getEffectiveUser: () => ({ getEmail: () => 'owner@example.com' }) },
    Utilities: { formatDate, newBlob: blob, zip: (parts, name) => Object.assign(blob('', 'application/zip', name), { parts }) }
  };
  vm.createContext(ctx); vm.runInContext(SRC, ctx);
  const base = { page: 'index.html', title: 'SHIVAS home', device: 'Phone', os: 'Android', browser: 'Chrome', lang: 'en-IN', tz: 'Asia/Kolkata' };
  const post = d => ctx.doPost({ postData: { contents: JSON.stringify(Object.assign({ at: new Date().toISOString() }, base, d)) } });
  return { ctx, post, mails, tabs, props, made, deleted, triggers };
}
// open a built .xlsx with openpyxl and return what is in it
function openXlsx(file, save) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'xl-'));
  file.parts.forEach(b => { const f = path.join(dir, b.name); fs.mkdirSync(path.dirname(f), { recursive: true }); fs.writeFileSync(f, b.data); });
  const out = save || path.join(dir, 'out.xlsx');
  const py = `import sys,os,zipfile,json
from openpyxl import load_workbook
d,out=sys.argv[1],sys.argv[2]
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
    for root,_,files in os.walk(d):
        for f in files:
            p=os.path.join(root,f)
            if p!=out: z.write(p,os.path.relpath(p,d))
wb=load_workbook(out)
print(json.dumps({ws.title:[[c.value for c in r] for r in ws.iter_rows()] for ws in wb.worksheets}))`;
  return JSON.parse(cp.execFileSync('python3', ['-c', py, dir, out], { encoding: 'utf8' }));
}
const C = {}; { const c = {}; vm.createContext(c); vm.runInContext(SRC, c); c.VISIT_COLS.forEach((x, i) => { C[x[0]] = i; }); }

console.log('Posting from the website');
let t = run();
check(t.post({ type: 'view', landing: 1 }) === 'ok' && t.mails.length === 0, 'a visit: logged, never an email');
check(t.tabs.Visits[0][C.detail] === 'Start of visit', 'the first page of a visit is marked "Start of visit"');
t.post({ type: 'view' }); check(t.tabs.Visits[1][C.detail] === '', 'the second page is not marked');
t = run(); t.post({ type: 'lead', source: 'Enquiry form', name: 'Test', contact: '+91 0000000000', product: 'Kettle' });
check(t.mails.length === 1 && t.mails[0].subject === 'Website enquiry: Test (Kettle)' && t.mails[0].to === 'info@shivastechnology.com', 'an enquiry: emailed at once (the default), "' + (t.mails[0] || {}).subject + '"');
check(t.tabs.Leads.length === 1 && t.tabs.Visits.length === 1, 'an enquiry: a Leads row and a Visits row');
t = run({ props: { ENQUIRY_EMAILS: 'off' } }); t.post({ type: 'lead', source: 'Enquiry form', name: 'Quiet', contact: '1' });
check(t.mails.length === 0 && t.tabs.Leads.length === 1, 'ENQUIRY_EMAILS = off: no email, the enquiry is still saved');
t.ctx.sendTestWeekly(); check(/Enquiry emails are switched off/.test(t.mails[0].htmlBody) && /Quiet/.test(t.mails[0].htmlBody), 'and the weekly email then says enquiries arrive there, and lists it');
t = run(); t.post({ type: 'lead', source: 'Enquiry form', name: 'Test', contact: '1', div: 'rein', product: 'SHIVAS Reinplast · Scrubber' });
check(t.mails[0].to === 'info@shivasasia.com' && t.mails[0].cc === 'shivasasia@gmail.com', 'a Reinplast enquiry goes to info@shivasasia.com');
t = run({ mailFails: true });
check(t.post({ type: 'lead', source: 'Enquiry form', name: 'Fail', contact: '1' }) === 'ok' && t.tabs.Leads.length === 1 && t.tabs.Visits.length === 1, 'the email failing never loses the enquiry or its Visits row');
t = run(); t.post({ type: 'view', pv: 'p1', landing: 1 }); t.post({ type: 'view', pv: 'p2' }); t.post({ type: 'time', pv: 'p1', secs: 31, scroll: 64 });
t.post({ type: 'update', pv: 'p2', visitor: 'V-abc', city: 'Pune', country: 'India', org: 'Reliance Jio Infocomm' });
check(t.tabs.Visits[0][C.secs] === 31 && t.tabs.Visits[0][C.scroll] === 64 && t.tabs.Visits.length === 2, 'time on page fills the right row, no new row');
check(t.tabs.Visits[1][C.city] === 'Pune' && t.tabs.Visits[1][C.nettype] === 'Home / mobile', 'the visitor\'s OK fills city and network type');
t = run(); t.post({ type: 'lead', source: 'Enquiry form', name: '=HYPERLINK(1)', contact: '+91 1' });
check(t.tabs.Leads[0][2] === "'=HYPERLINK(1)" && t.tabs.Leads[0][4] === "'+91 1", 'text that looks like a formula is stored as text');

console.log('\nSchedule');
t = run({ triggers: ['dailyDigest', 'weeklyDigest'] }); t.ctx.setupWeekly();
check(t.deleted.join(',') === 'dailyDigest,weeklyDigest' && t.made.length === 2 && t.made.every(x => x.h === 'weeklyDigest' && x.hour === 8 && x.min === 30 && x.tz === 'Asia/Kolkata') && t.made.map(x => x.day).join(',') === 'MONDAY,THURSDAY', 'setupWeekly: the old triggers go, two remain, Monday and Thursday at 8:30 India time');
{ const IST = (ymd, hm) => new Date(ymd + 'T' + hm + ':00+05:30');
  const mk = now => { const r = run({ now: +now }); for (let d = 19; d <= 29; d++) r.post({ type: 'view', landing: 1, title: 'Day ' + d, at: IST('2026-11-' + d, '12:00').toISOString() }); return r; };
  const thu = mk(IST('2026-11-26', '08:30')); thu.ctx.weeklyDigest();
  check(thu.mails[0].subject === 'SHIVAS website, 23 Nov to 25 Nov: 0 enquiries, 3 visits' && /3 in the same number of days before/.test(thu.mails[0].htmlBody), 'Thursday 26 Nov: Monday to Wednesday, "' + thu.mails[0].subject + '"');
  const mon = mk(IST('2026-11-30', '08:30')); mon.ctx.weeklyDigest();
  check(mon.mails[0].subject === 'SHIVAS website, 26 Nov to 29 Nov: 0 enquiries, 4 visits' && /4 in the same number of days before/.test(mon.mails[0].htmlBody), 'Monday 30 Nov: Thursday to Sunday, "' + mon.mails[0].subject + '" (every day in exactly one report)');
  check(/Since the last report:/.test(mon.mails[0].htmlBody) && mon.mails[0].attachments[0].name === 'SHIVAS website 2026-11-26 to 2026-11-29.xlsx', 'the report says "Since the last report" and its file covers the same days'); }
t = run(); t.post({ type: 'view', landing: 1, at: new Date(Date.now() - 864e5).toISOString() }); t.ctx.dailyDigest();
check(t.mails.length === 0, 'an old daily trigger still firing sends nothing');
t = run(); t.post({ type: 'view', at: new Date(Date.now() - 800 * 864e5).toISOString() }); t.post({ type: 'view' }); t.post({ type: 'view' });
t.ctx.dailyDigest(); check(t.tabs.Visits.length === 2, 'rows older than 730 days are deleted');

// ---------------- a sample fortnight: made-up visitors, the week before for comparison ----------------
console.log('\nThe weekly email on a sample fortnight (made-up data)');
t = run();
const title = f => { try { return (fs.readFileSync('site/' + f, 'utf8').match(/<title>([^<]*)/) || [])[1].replace(/\s*\|\s*SHIVAS.*$/, ''); } catch (e) { return f; } };
const ist = (daysAgo, hh, mm) => new Date(formatDate(Date.now() - daysAgo * 864e5, '', 'yyyy-MM-dd') + 'T' + String(hh).padStart(2, '0') + ':' + String(mm).padStart(2, '0') + ':00+05:30');
let pvN = 0;
function visit(when, who, pages) {
  let tm = when.getTime();
  pages.forEach((pg, i) => {
    const pv = 'pv' + (++pvN), at = new Date(tm).toISOString(), extra = Object.assign({}, who.ok || {});
    t.post(Object.assign({ type: 'view', pv, page: pg[0], title: title(pg[0]), at }, who.dev, extra, i === 0 ? { landing: 1, ref: who.ref || '', utm: who.utm || '' } : {}));
    if (pg[1]) t.post({ type: 'time', pv, secs: pg[1], scroll: 70 });
    if (pg[2]) t.post(Object.assign({ type: 'calc', pv, page: pg[0], title: title(pg[0]), detail: pg[2], at: new Date(tm + 20000).toISOString() }, who.dev, extra));
    if (pg[3]) t.post(Object.assign({ type: 'click', pv, page: pg[0], title: title(pg[0]), detail: pg[3], at: new Date(tm + 30000).toISOString() }, who.dev, extra));
    if (pg[4]) t.post(Object.assign({ type: 'lead', page: pg[0], title: title(pg[0]), at: new Date(tm + 40000).toISOString() }, who.dev, extra, pg[4]));
    tm += ((pg[1] || 20) + 8) * 1000;
  });
}
const phone = { device: 'Phone', os: 'Android', browser: 'Chrome', model: 'SM-A546E', screen: '412×915', lang: 'en-IN', tz: 'Asia/Kolkata' };
const pc = { device: 'Computer', os: 'Windows', browser: 'Chrome', model: '', screen: '1920×1080', lang: 'en-GB', tz: 'Asia/Kolkata' };
const PLANT = 'Galvanizing plant calculator\nProduct mix: ISMC 150 (40 %); ISA 50 × 50 × 5 (40 %); MS pipe 2" (20 %)\nTarget: 800 t of black steel a month, 26 days, 2 shifts of 8 h\nLargest article: 6.5 × 1.2 × 1.4 m\nFuel: Natural gas\n\nCalculator estimate: kettle 7 × 1.5 × 2.5 m, 1.92 t/h, zinc 68.4 kg/t';
const WIRE = 'Wire drawing\nInlet wire: 5.5 mm\nFinal wire: 2.5 mm\nCarbon: 0.08 %\nFinal speed: 10 m/s\n\nResults\nPasses: 8\nMotor power: 75 kW';
const ZLD = 'ETP and ZLD plant\nEffluent: 120 m³/day\nTDS: 18,000 mg/l\nEvaporator: MVR\n\nResults\nRO permeate: 78 m³/day\nEvaporator: 36 m³/day';
visit(ist(2, 10, 12), { dev: phone, ref: 'www.google.com (search)' }, [['index.html', 22], ['items/kettle.html', 95], ['calculator.html', 260, PLANT, 'WhatsApp: https://wa.me/919810920468 · WhatsApp it']]);
visit(ist(3, 15, 40), { dev: pc, ref: 'https://www.linkedin.com/', ok: { visitor: 'V-sample1', visit: 2, first: '2026-11-02', city: 'Ludhiana', region: 'Punjab', country: 'India', org: 'Sample Wires Ltd', ip: '203.0.113.10' } },
  [['wire-drawing.html', 70], ['items/oto.html', 180], ['items/slm.html', 240], ['calculators/wire-drawing.html', 150, WIRE]]);
visit(ist(3, 11, 5), { dev: phone, ok: { visitor: 'V-sample2', visit: 3, city: 'Pune', region: 'Maharashtra', country: 'India', org: 'Reliance Jio Infocomm', ip: '203.0.113.20' } },
  [['reinplast.html', 60], ['calculators/etp-zld.html', 320, ZLD], ['contact.html', 90, '', '', { source: 'Enquiry form', name: 'Sample buyer', company: 'Example Chemicals (sample)', contact: '+91 00000 00000', email: 'buyer@example.com', div: 'rein', product: 'SHIVAS Reinplast · ETP and ZLD plant', place: 'Pune', message: 'Sample enquiry: effluent about 120 m3 a day from a dyeing unit, we need ZLD. Please send a proposal and call us.' }]]);
visit(ist(2, 19, 30), { dev: Object.assign({}, phone, { tz: 'Asia/Dhaka', lang: 'bn-BD' }), ref: 'www.google.com (search)' }, [['galvanizing.html', 85], ['v/hdg-plant.html', 140], ['blog/burners-and-kettle-life.html', 210]]);
visit(ist(2, 9, 45), { dev: pc, ok: { visitor: 'V-sample3', visit: 1, city: 'Dubai', country: 'United Arab Emirates', org: 'Example Steel LLC (sample)', ip: '203.0.113.30' }, ref: 'https://www.bing.com/' }, [['galvanizing.html', 50], ['items/furnace.html', 300], ['items/kettle.html', 120, '', 'Phone: +919810280104 · +91 98102 80104']]);
visit(ist(1, 12, 0), { dev: pc }, [['index.html', 30], ['about.html', 45], ['contact.html', 25, '', 'Email: info@shivastechnology.com · info@shivastechnology.com']]);
for (let i = 0; i < 6; i++) visit(ist(1 + (i % 4), 8 + i, 10), { dev: phone }, [['careers.html', 4 + i % 3]]);
visit(ist(0, 9, 20), { dev: phone, ref: 'android-app://com.google.android.gm/', utm: 'linkedin / social / kettle-post' }, [['index.html', 18], ['items/kettle.html', 75]]);
visit(ist(7, 11, 0), { dev: phone, ref: 'www.google.com (search)' }, [['index.html', 20], ['items/kettle.html', 60]]);
visit(ist(6, 16, 0), { dev: pc }, [['galvanizing.html', 40]]);
visit(ist(5, 10, 30), { dev: phone }, [['wire-drawing.html', 35], ['contact.html', 30, '', 'WhatsApp: https://wa.me/919810920468 · WhatsApp']]);
t.mails.length = 0;
t.ctx.sendTestWeekly();
const m = t.mails[0] || {}, h = m.htmlBody || '', file = (m.attachments || [])[0];
check(t.mails.length === 1 && m.to === 'info@shivastechnology.com,owner@example.com', 'ONE email, to info@ and the owner\'s Google account');
console.log('        subject: ' + m.subject);
check(/^Test: SHIVAS website, \d+ \w+ to \d+ \w+ \(today included\): 1 enquiry, 12 visits, 2 companies$/.test(m.subject), 'subject: the last 4 days with today, 1 enquiry, 12 visits, 2 companies');
check(file && /^SHIVAS website \d{4}-\d\d-\d\d to \d{4}-\d\d-\d\d\.xlsx$/.test(file.name) && file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'ONE file attached: "' + (file || {}).name + '"');
check(/Sample buyer/.test(h) && /look up the company/.test(h) && /Sample Wires Ltd/.test(h) && /linkedin\.com\/search\/results\/companies\/\?keywords=Sample%20Wires%20Ltd/.test(h) && /google\.com\/search\?q=Sample%20Wires%20Ltd%20Ludhiana/.test(h), 'the email: the enquiry first, and Google and LinkedIn links for each company');
check(/<b>Attached<\/b>: one Excel file/.test(h) && !/WhatsApp messages|WA_|DAILY_REPORT|VISIT_ALERTS/.test(h), 'the email says what is attached and mentions no WhatsApp or daily options');
check(!/—/.test(h + m.subject), 'no em dashes');
const X = openXlsx(file, process.argv[3]);
const names = Object.keys(X);
check(names.join(',') === 'Summary,Enquiries,Companies,Visitors who pressed OK,Pages,Calculators,Taps,Came from,Countries,Devices,Days,Every visit', 'Excel opens with openpyxl, 12 tabs: ' + names.join(', '));
const row = (tab, label) => (X[tab] || []).find(r => r[0] === label) || [];
check((X.Summary || []).some(r => r[1] === 'These days' && r[2] === 'Same number of days before') && row('Summary', 'Visits')[1] === 12 && row('Summary', 'Visits')[2] === 4 && row('Summary', 'Enquiries')[1] === 1, 'Summary: these days against the same number of days before, visits 12 against 4, enquiries 1');
const E = X.Enquiries || [];
check(E.length === 2 && E[1][2] === 'Sample buyer' && E[1][4] === '+91 00000 00000' && /HYPERLINK\("https:\/\/www\.google\.com\/search\?q=Example%20Chemicals/.test(E[1][E[0].length - 1]), 'Enquiries: name, number, the pages seen before, a link to look up the company');
const F = X.Companies || [];
check(F.length === 3 && F.slice(1).map(r => r[0]).sort().join('|') === 'Example Steel LLC (sample)|Sample Wires Ltd' && F[1][2] >= F[2][2] && /linkedin/.test(F[1][14]), 'Companies: the two office networks (not Jio), highest interest first, Google and LinkedIn links');
const P = X['Visitors who pressed OK'] || [];
check(P.length === 4 && P.some(r => r[0] === 'V-sample2' && r[2] === 'Yes' && r[6] === 'Reliance Jio Infocomm') && P.some(r => r[0] === 'V-sample1' && r[4] === '2026-11-02'), 'Visitors who pressed OK: 3 people, the one who sent the enquiry marked, first seen as a date');
check((X.Calculators || []).length === 4 && X.Calculators.some(r => /Galvanizing plant calculator/.test(r[1]) && /Target: 800 t/.test(r[2])), 'Calculators: every use with what was entered');
check((X.Taps || []).length === 4 && X.Taps.some(r => r[1] === 'Phone' && /98102 80104/.test(r[2])), 'Taps: the 3 WhatsApp, phone and email taps of the week, with the number tapped');
check(row('Came from', 'Google search')[1] === 2 && row('Came from', 'linkedin / social / kettle-post')[1] === 1 && row('Countries', 'Bangladesh')[1] === 1 && row('Countries', 'Dubai, United Arab Emirates')[1] === 1, 'Came from and Countries: sources, campaigns, countries and cities');
const EV = X['Every visit'] || [];
check(EV.length > 30 && !EV[0].includes('IP address') && !EV[0].includes('pv') && !JSON.stringify(X).includes('203.0.113'), 'Every visit: every row of the week, and no IP address anywhere in the file');
check((X.Days || []).length === 5 && (X.Pages || []).some(r => r[1] === 'items/kettle.html' && r[2] === 3), 'Days and Pages: 4 days with visits, views per page (Zinc kettle 3)');
if (process.argv[2]) { fs.writeFileSync(process.argv[2], '<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Sample weekly report</title><body style="margin:0;padding:16px;background:#f6f8fb">' + h + '</body>'); console.log('        saved ' + process.argv[2] + (process.argv[3] ? ' and ' + process.argv[3] : '')); }
t.mails.length = 0; t.ctx.weeklyDigest();
check(t.mails.length === 1 && /^SHIVAS website, \d+ \w+ to \d+ \w+: /.test(t.mails[0].subject) && t.mails[0].attachments.length === 1, 'the scheduled run today: "' + (t.mails[0] || {}).subject + '", with the file');
const old = run();
['10:00', '10:05', '10:20', '14:00'].forEach(hm => old.post({ type: 'view', at: ist(2, +hm.slice(0, 2), +hm.slice(3)).toISOString() }));
old.ctx.sendTestWeekly(); check(/0 enquiries, 2 visits$/.test(old.mails[0].subject), 'older rows without marks: 4 views at 10:00, 10:05, 10:20, 14:00 = 2 visits');
const empty = run(); empty.ctx.weeklyDigest(); const ef = openXlsx(empty.mails[0].attachments[0]);
check(/0 enquiries, 0 visits/.test(empty.mails[0].subject) && /No visits were recorded in these days/.test(empty.mails[0].htmlBody) && Object.keys(ef).length === 12, 'quiet days: still one short email, with the file (headers only)');
check(!/UrlFetchApp|DriveApp|graph\.facebook|WA_TOKEN/.test(SRC), 'no WhatsApp and no extra Google permissions in the script (no UrlFetchApp, no DriveApp)');

console.log('\nFirst open of the web app (doGet)');
(function () {
  const mails = [], props = {}, created = {}, made = [];
  const sheet = n => ({ getRange: () => ({ setValues() { return this; }, setFontWeight() { return this; }, setBackground() { return this; }, setFontColor() { return this; }, setNumberFormat() { return this; }, setFormula() { return this; } }),
    setFrozenRows() {}, hideColumns() {}, getLastRow: () => 0 });
  const book = { getId: () => 'SHEET-ID', getUrl: () => 'https://docs.google.com/spreadsheets/d/SHEET-ID', getSheetByName: n => created[n] || null,
    insertSheet: n => (created[n] = sheet(n)), getSheets: () => Object.keys(created), deleteSheet() {} };
  const trig = { timeBased: () => trig, atHour: () => trig, everyDays: () => trig, inTimezone: () => trig, onWeekDay: () => trig, nearMinute: () => trig, create: () => made.push(1) };
  const ctx = { console: { log() {} }, JSON, Date, Math, String, Number, Object, isNaN,
    ContentService: { createTextOutput: t => t },
    PropertiesService: { getScriptProperties: () => ({ getProperty: k => k in props ? props[k] : null, setProperty: (k, v) => { props[k] = v; } }) },
    SpreadsheetApp: { getActiveSpreadsheet: () => book, openById: () => book, create: () => book },
    ScriptApp: { getProjectTriggers: () => [], deleteTrigger() {}, newTrigger: () => trig, WeekDay: { MONDAY: 1, THURSDAY: 4 } },
    MailApp: { sendEmail: m => mails.push(m), getRemainingDailyQuota: () => 100 },
    Session: { getEffectiveUser: () => ({ getEmail: () => 'owner@example.com' }) },
    Utilities: { formatDate } };
  vm.createContext(ctx); vm.runInContext(SRC, ctx);
  check(/is set up/.test(ctx.doGet()) && Object.keys(created).join(',') === 'Visits,Leads,Companies,Pages,Daily,Viewers' && made.length === 2 && props.SHEET === 'SHEET-ID', 'tabs, two triggers (Monday and Thursday) and the confirmation email');
  check(/every Monday and Thursday at 8:30/.test(mails[0].htmlBody), 'the confirmation describes Version 6.1');
  check(ctx.doGet() === 'SHIVAS visitor log is running.' && mails.length === 1, 'opening it again only says it is running');
})();
console.log(failed ? '\n' + failed + ' FAILED' : '\nall passed');
process.exit(failed ? 1 : 0);
