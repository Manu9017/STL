/* Runs site/setup/visitor-log/Code.gs in Node against stand-ins for the Google services (a Sheet that keeps its rows,
   MailApp, properties, triggers) and prints what it would write and email. Nothing leaves this machine.
     node tools/test_visitor_log.cjs                 (run from the repo root)
     node tools/test_visitor_log.cjs report.html     (also saves the sample weekly report, to look at in a browser)
   The sample week uses made-up visitors and companies ("Example ...", "Sample ..."), never real data. */
const fs = require('fs'), vm = require('vm');
const SRC = fs.readFileSync('site/setup/visitor-log/Code.gs', 'utf8');
const MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], WD = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
const formatDate = (d, tz, f) => {   // India time, the patterns Code.gs uses
  const x = new Date(new Date(d).getTime() + 330 * 60000), p = n => String(n).padStart(2, '0');
  return f.replace(/yyyy|MMM|MM|dd|d|HH|mm|EEE/g, t => ({ yyyy: x.getUTCFullYear(), MMM: MON[x.getUTCMonth()], MM: p(x.getUTCMonth() + 1), dd: p(x.getUTCDate()),
    d: x.getUTCDate(), HH: p(x.getUTCHours()), mm: p(x.getUTCMinutes()), EEE: WD[x.getUTCDay()] })[t]);
};
let failed = 0;
const check = (ok, what) => { console.log((ok ? '  ok    ' : '  FAIL  ') + what); if (!ok) failed++; };

function run(opts = {}) {
  const mails = [], props = Object.assign({ SHEET: 'SHEET-ID' }, opts.props || {}), tabs = { Visits: [], Leads: [] }, triggers = [];
  const sheet = n => ({
    appendRow: r => tabs[n].push(r.slice()),
    getLastRow: () => tabs[n].length + 1,
    getRange: (row, col, nr, nc) => ({
      getValues: () => tabs[n].slice(row - 2, row - 2 + (nr || 1)).map(r => r.slice(col - 1, col - 1 + (nc || 1))),
      setValue: v => { tabs[n][row - 2][col - 1] = v; }
    }),
    deleteRows: (row, k) => tabs[n].splice(row - 2, k)
  });
  const book = { getId: () => 'SHEET-ID', getUrl: () => 'https://docs.google.com/spreadsheets/d/SHEET-ID', getSheetByName: n => tabs[n] ? sheet(n) : null };
  const ctx = {
    console, JSON, Date, Math, String, Number, Object, isNaN,
    LockService: { getScriptLock: () => ({ waitLock() {}, releaseLock() {} }) },
    CacheService: { getScriptCache: () => ({ get: () => null, put() {} }) },
    ContentService: { createTextOutput: t => t },
    PropertiesService: { getScriptProperties: () => ({ getProperty: k => k in props ? props[k] : null, setProperty: (k, v) => { props[k] = v; }, deleteProperty: k => { delete props[k]; } }) },
    SpreadsheetApp: { getActiveSpreadsheet: () => book, openById: () => book, create: () => book },
    ScriptApp: { getProjectTriggers: () => [], deleteTrigger() {}, newTrigger: () => ({}), WeekDay: { MONDAY: 1 } },
    MailApp: { sendEmail: m => { if (opts.mailFails) throw new Error('quota'); mails.push(m); }, getRemainingDailyQuota: () => 100 },
    Session: { getEffectiveUser: () => ({ getEmail: () => 'owner@example.com' }) },
    Utilities: { formatDate }
  };
  vm.createContext(ctx); vm.runInContext(SRC, ctx);
  const base = { page: 'index.html', title: 'SHIVAS home', device: 'Phone', os: 'Android', browser: 'Chrome', lang: 'en-IN', tz: 'Asia/Kolkata' };
  const post = d => ctx.doPost({ postData: { contents: JSON.stringify(Object.assign({ at: new Date().toISOString() }, base, d)) } });
  return { ctx, post, mails, tabs, props };
}
const C = {}; { const c = {}; vm.createContext(c); vm.runInContext(SRC, c); c.VISIT_COLS.forEach((x, i) => { C[x[0]] = i; }); }

console.log('Posting from the website');
let t = run();
check(t.post({ type: 'view', landing: 1 }) === 'ok' && t.mails.length === 0, 'first page of a visit: logged, no email (visit alerts off by default)');
check(t.tabs.Visits[0][C.detail] === 'Start of visit', 'that row is marked "Start of visit"');
t.post({ type: 'view' }); check(t.tabs.Visits[1][C.detail] === '', 'second page: not marked');
t = run({ props: { VISIT_ALERTS: 'on' } });
t.post({ type: 'view', landing: 1, city: 'Ghaziabad', region: 'Uttar Pradesh', country: 'India', org: 'Example Steel Pvt Ltd', visit: 3 });
check(t.mails.length === 1 && /someone opened SHIVAS home · Ghaziabad/.test(t.mails[0].subject) && /Example Steel Pvt Ltd \(Company network\)/.test(t.mails[0].htmlBody), 'script property VISIT_ALERTS = on: the visit email comes back');
for (let i = 0; i < 30; i++) t.post({ type: 'view', landing: 1 });
check(t.mails.length === 25 && t.tabs.Visits.length === 31, 'and is capped at 25 a day, every visit still logged');
t = run({ mailFails: true, props: { VISIT_ALERTS: 'on' } });
check(t.post({ type: 'view', landing: 1 }) === 'ok' && t.tabs.Visits.length === 1, 'a failing MailApp never loses the row');
t = run(); t.post({ type: 'lead', source: 'Enquiry form', name: 'Test', contact: '+91 0000000000', product: 'Kettle' });
check(t.mails.length === 1 && t.mails[0].subject === 'Website enquiry: Test (Kettle)' && t.mails[0].to === 'info@shivastechnology.com', 'enquiry: emailed at once, subject "' + (t.mails[0] || {}).subject + '"');
check(t.tabs.Leads.length === 1 && t.tabs.Visits.length === 1, 'enquiry: a Leads row and a Visits row');
t = run(); t.post({ type: 'lead', source: 'Enquiry form', name: 'Test', contact: '+91 0000000000', div: 'rein', product: 'SHIVAS Reinplast · Scrubber' });
check(t.mails[0].to === 'info@shivasasia.com' && t.mails[0].cc === 'shivasasia@gmail.com', 'Reinplast enquiry goes to info@shivasasia.com');
t = run(); t.post({ type: 'view', pv: 'p1', landing: 1 }); t.post({ type: 'view', pv: 'p2' }); t.post({ type: 'time', pv: 'p1', secs: 31, scroll: 64 });
t.post({ type: 'update', pv: 'p2', visitor: 'V-abc', city: 'Pune', country: 'India', org: 'Reliance Jio Infocomm' });
check(t.tabs.Visits[0][C.secs] === 31 && t.tabs.Visits[0][C.scroll] === 64 && t.tabs.Visits.length === 2, 'time on page fills the right row, no new row');
check(t.tabs.Visits[1][C.city] === 'Pune' && t.tabs.Visits[1][C.nettype] === 'Home / mobile', 'the visitor\'s OK fills city and network type');
t = run(); t.post({ type: 'lead', source: 'Enquiry form', name: '=HYPERLINK(1)', contact: '+91 1' });
check(t.tabs.Leads[0][2] === "'=HYPERLINK(1)" && t.tabs.Leads[0][4] === "'+91 1", 'text that looks like a formula is stored as text');

console.log('\nMorning run (dailyDigest)');
t = run(); t.post({ type: 'view', landing: 1, at: new Date(Date.now() - 864e5).toISOString() });
t.ctx.dailyDigest(); check(t.mails.length === 0, 'no morning report by default (it still tidies old rows)');
t = run({ props: { DAILY_REPORT: 'on' } }); t.post({ type: 'view', landing: 1, at: new Date(Date.now() - 864e5).toISOString() });
t.ctx.dailyDigest(); check(t.mails.length === 1 && /^SHIVAS website, \d+ \w+: 0 enquiries, 1 visit$/.test(t.mails[0].subject), 'DAILY_REPORT = on: "' + (t.mails[0] || {}).subject + '"');
t = run(); t.post({ type: 'view', at: new Date(Date.now() - 800 * 864e5).toISOString() }); t.post({ type: 'view' }); t.post({ type: 'view' });
t.ctx.dailyDigest(); check(t.tabs.Visits.length === 2, 'rows older than 730 days are deleted');

// ---------------- a sample fortnight: made-up visitors, the week before for comparison ----------------
console.log('\nWeekly report on a sample fortnight (made-up data)');
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
// this week (the 7 days to today)
visit(ist(5, 10, 12), { dev: phone, ref: 'www.google.com (search)' }, [['index.html', 22], ['items/kettle.html', 95], ['calculator.html', 260, PLANT, 'WhatsApp: https://wa.me/919810920468 · WhatsApp it']]);
visit(ist(4, 15, 40), { dev: pc, ref: 'https://www.linkedin.com/', ok: { visitor: 'V-sample1', visit: 2, city: 'Ludhiana', region: 'Punjab', country: 'India', org: 'Sample Wires Ltd', ip: '203.0.113.10' } },
  [['wire-drawing.html', 70], ['items/oto.html', 180], ['items/slm.html', 240], ['calculators/wire-drawing.html', 150, WIRE]]);
visit(ist(3, 11, 5), { dev: phone, ok: { visitor: 'V-sample2', visit: 3, city: 'Pune', region: 'Maharashtra', country: 'India', org: 'Reliance Jio Infocomm', ip: '203.0.113.20' } },
  [['reinplast.html', 60], ['calculators/etp-zld.html', 320, ZLD], ['contact.html', 90, '', '', { source: 'Enquiry form', name: 'Sample buyer', company: 'Example Chemicals (sample)', contact: '+91 00000 00000', email: 'buyer@example.com', div: 'rein', product: 'SHIVAS Reinplast · ETP and ZLD plant', place: 'Pune', message: 'Sample enquiry: effluent about 120 m3 a day from a dyeing unit, we need ZLD. Please send a proposal and call us.' }]]);
visit(ist(2, 19, 30), { dev: Object.assign({}, phone, { tz: 'Asia/Dhaka', lang: 'bn-BD' }), ref: 'www.google.com (search)' }, [['galvanizing.html', 85], ['v/hdg-plant.html', 140], ['blog/burners-and-kettle-life.html', 210]]);
visit(ist(2, 9, 45), { dev: pc, ok: { visitor: 'V-sample3', visit: 1, city: 'Dubai', country: 'United Arab Emirates', org: 'Example Steel LLC (sample)', ip: '203.0.113.30' }, ref: 'https://www.bing.com/' }, [['galvanizing.html', 50], ['items/furnace.html', 300], ['items/kettle.html', 120, '', 'Phone: +919810280104 · +91 98102 80104']]);
visit(ist(1, 12, 0), { dev: pc }, [['index.html', 30], ['about.html', 45], ['contact.html', 25, '', 'Email: info@shivastechnology.com · info@shivastechnology.com']]);
for (let i = 0; i < 6; i++) visit(ist(1 + (i % 4), 8 + i, 10), { dev: phone }, [['careers.html', 4 + i % 3]]);
visit(ist(0, 9, 20), { dev: phone, ref: 'android-app://com.google.android.gm/' }, [['index.html', 18], ['items/kettle.html', 75]]);
// the week before
visit(ist(10, 11, 0), { dev: phone, ref: 'www.google.com (search)' }, [['index.html', 20], ['items/kettle.html', 60]]);
visit(ist(9, 16, 0), { dev: pc }, [['galvanizing.html', 40]]);
visit(ist(8, 10, 30), { dev: phone }, [['wire-drawing.html', 35], ['contact.html', 30, '', 'WhatsApp: https://wa.me/919810920468 · WhatsApp']]);
t.mails.length = 0;
t.ctx.sendTestWeekly();
const m = t.mails[0] || {}, h = m.htmlBody || '';
check(t.mails.length === 1 && m.to === 'info@shivastechnology.com,owner@example.com', 'one report to info@ and the owner\'s account');
console.log('        subject: ' + m.subject);
check(/^Test: SHIVAS website, Last 7 days, .*: 1 enquiry, 13 visits, 2 companies$/.test(m.subject), 'subject counts: 1 enquiry, 13 visits (6 short careers visits included), 2 companies');
check(/Sample buyer/.test(h) && /Example Chemicals \(sample\)/.test(h) && /buyer@example.com/.test(h), 'the enquiry is at the top, with contact details');
check(/Sample Wires Ltd/.test(h) && /Example Steel LLC \(sample\)/.test(h) && !/Reliance Jio/.test(h.split('Most interested')[0].split('Companies that')[1] || ''), 'companies: office networks only, not Jio');
check(/Galvanizing plant calculator<\/b>: Product mix: ISMC 150/.test(h) && /ETP and ZLD plant<\/b>: Effluent: 120/.test(h), 'calculators: what visitors entered');
check(/Google search/.test(h) && /LinkedIn/.test(h) && /Gmail/.test(h) && /Other search engines/.test(h), 'sources: Google, LinkedIn, Gmail app, Bing');
check(/Bangladesh/.test(h) && /United Arab Emirates/.test(h), 'countries: Bangladesh from the time zone, UAE from the location');
check(/Worth improving/.test(h) && /Careers/.test(h.split('Worth improving')[1] || ''), 'worth improving: the page people leave within seconds');
check(/3 the week before/.test(h), 'compared with the week before (3 visits)');
check(!/—/.test(h) && !/—/.test(m.subject), 'no em dashes');
check(h.length < 60000, 'size ' + Math.round(h.length / 1024) + ' KB (Gmail clips above 102 KB)');
t.mails.length = 0; t.ctx.weeklyDigest();
check(t.mails.length === 1 && /^SHIVAS website, Week of /.test(t.mails[0].subject), 'Monday run: "' + (t.mails[0] || {}).subject + '"');
// rows from before Version 4 (no "Start of visit" marks): visits found from a gap of 30 minutes
const old = run();
['10:00', '10:05', '10:20', '14:00'].forEach(hm => old.post({ type: 'view', at: ist(2, +hm.slice(0, 2), +hm.slice(3)).toISOString() }));
old.ctx.sendTestWeekly(); check(/0 enquiries, 2 visits$/.test(old.mails[0].subject), 'older rows without marks: 4 views at 10:00, 10:05, 10:20, 14:00 = 2 visits');
const empty = run(); empty.ctx.weeklyDigest();
check(/0 enquiries, 0 visits/.test(empty.mails[0].subject) && /No visits were recorded this week/.test(empty.mails[0].htmlBody), 'a quiet week still sends a short report');
if (process.argv[2]) { fs.writeFileSync(process.argv[2], '<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Sample weekly report</title><body style="margin:0;padding:16px;background:#f6f8fb">' + h + '</body>'); console.log('        saved ' + process.argv[2]); }

// doGet: first open runs setup and emails a confirmation; later opens only report "running"
console.log('\nFirst open of the web app (doGet)');
(function () {
  const mails = [], props = {}, created = {}, triggers = [];
  const sheet = n => ({ getRange: () => ({ setValues() { return this; }, setFontWeight() { return this; }, setBackground() { return this; }, setFontColor() { return this; }, setNumberFormat() { return this; }, setFormula() { return this; } }),
    setFrozenRows() {}, hideColumns() {}, getLastRow: () => 0 });
  const book = { getId: () => 'SHEET-ID', getUrl: () => 'https://docs.google.com/spreadsheets/d/SHEET-ID', getSheetByName: n => created[n] || null,
    insertSheet: n => (created[n] = sheet(n)), getSheets: () => Object.keys(created), deleteSheet() {} };
  const trig = { timeBased: () => trig, atHour: () => trig, everyDays: () => trig, inTimezone: () => trig, onWeekDay: () => trig, nearMinute: () => trig, create: () => triggers.push(1) };
  const ctx = { console, JSON, Date, Math, String, Number, Object, isNaN,
    ContentService: { createTextOutput: t => t },
    PropertiesService: { getScriptProperties: () => ({ getProperty: k => k in props ? props[k] : null, setProperty: (k, v) => { props[k] = v; } }) },
    SpreadsheetApp: { getActiveSpreadsheet: () => book, openById: () => book, create: () => book },
    ScriptApp: { getProjectTriggers: () => [], deleteTrigger() {}, newTrigger: () => trig, WeekDay: { MONDAY: 1 } },
    MailApp: { sendEmail: m => mails.push(m), getRemainingDailyQuota: () => 100 },
    Session: { getEffectiveUser: () => ({ getEmail: () => 'owner@example.com' }) },
    Utilities: { formatDate } };
  vm.createContext(ctx); vm.runInContext(SRC, ctx);
  check(/is set up/.test(ctx.doGet()) && Object.keys(created).join(',') === 'Visits,Leads,Companies,Pages,Daily,Viewers' && triggers.length === 2 && props.SHEET === 'SHEET-ID', 'tabs, 2 triggers and the confirmation email "' + (mails[0] && mails[0].subject) + '"');
  check(/every Monday at 8:30/.test(mails[0].htmlBody) && !/opens the website/.test(mails[0].htmlBody), 'the confirmation describes Version 4 (enquiries and the Monday report)');
  check(ctx.doGet() === 'SHIVAS visitor log is running.' && mails.length === 1, 'opening it again only says it is running');
})();
console.log(failed ? '\n' + failed + ' FAILED' : '\nall passed');
process.exit(failed ? 1 : 0);
