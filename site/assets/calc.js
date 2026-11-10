/* SHIVAS galvanizing plant sizing and running-cost calculator.
   Pick the profiles you galvanize (a mix), set your monthly black-steel target and largest article, and the page works out
   surface per tonne, coating to ISO 1461 / IS 4759, zinc with dross and ash, kettle and furnace size, pretreatment line,
   fuel, acid, flux, power and labour, and the running cost per tonne and per month. Every rate and assumption is editable.
   Planning estimates only: real figures depend on steel chemistry, surface condition and plant practice. */
(function () {
  'use strict';
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var root = document.getElementById('calc'); if (!root) return;
  var RHO = 7.85e-3; // kg per mm2 per m
  // ---------- profile library (nominal dimensions, mm) ----------
  var F = {
    isa: { n: 'Equal angles (ISA)', k: 'angle', unit: 'a × a × t', list: [[20,20,3],[25,25,3],[30,30,3],[35,35,5],[40,40,5],[45,45,5],[50,50,5],[50,50,6],[60,60,6],[65,65,6],[70,70,6],[75,75,6],[75,75,8],[80,80,8],[90,90,8],[100,100,8],[100,100,10],[110,110,10],[130,130,10],[150,150,12],[200,200,16]], use: 'Structures, sheds, towers, frames' },
    isau: { n: 'Unequal angles (ISA)', k: 'angle', unit: 'a × b × t', list: [[75,50,6],[100,65,8],[100,75,8],[125,75,8],[150,75,10],[150,115,10]], use: 'Structures and bracing' },
    ismc: { n: 'Channels (ISMC)', k: 'channel', unit: 'h × b × tw × tf', list: [[75,40,4.4,7.3],[100,50,4.7,7.5],[125,65,5,8.1],[150,75,5.4,9],[175,75,5.7,10.2],[200,75,6.1,11.4],[250,80,7.1,14.1],[300,90,7.6,13.6],[400,100,8.6,15.3]], use: 'Frames, purlins, crash-barrier posts' },
    ismb: { n: 'I-beams (ISMB)', k: 'ibeam', unit: 'h × b × tw × tf', list: [[100,75,4,7.2],[125,75,4.4,7.6],[150,80,4.8,7.6],[175,90,5.5,8.6],[200,100,5.7,10.8],[250,125,6.9,12.5],[300,140,7.5,12.4],[350,140,8.1,14.2],[400,140,8.9,16],[450,150,9.4,17.4],[500,180,10.2,17.2],[600,210,12,20.8]], use: 'Building and bridge steel' },
    ishb: { n: 'H-beams (ISHB)', k: 'hbeam', unit: 'h × b × tw × tf', list: [[150,150,5.4,9],[200,200,6.1,9],[225,225,6.5,9.1],[250,250,6.9,9.7],[300,250,7.6,10.6],[350,250,8.3,11.6],[400,250,9.1,12.7],[450,250,9.8,13.7]], use: 'Columns, heavy structures' },
    euro: { n: 'European IPE / HEA', k: 'ibeam', unit: 'h × b × tw × tf', list: [[160,82,5,7.4],[200,100,5.6,8.5],[240,120,6.2,9.8],[300,150,7.1,10.7],[190,200,6.5,10],[230,240,7.5,12],[290,300,8.5,14]], label: ['IPE 160','IPE 200','IPE 240','IPE 300','HEA 200','HEA 240','HEA 300'], use: 'Export structures' },
    cpur: { n: 'Solar: lipped C purlins / channels', k: 'lipc', unit: 'h × b × lip × t', list: [[41,41,9,2.5],[60,40,15,2],[75,40,15,2],[100,50,15,2],[100,50,20,2.5],[120,60,20,2.5],[150,65,20,2.5],[150,65,20,3],[200,75,20,3]], use: 'Solar module rafters, purlins, posts' },
    zpur: { n: 'Solar: Z purlins', k: 'zed', unit: 'h × b × lip × t', list: [[100,50,15,2],[150,60,20,2.5],[200,70,20,3]], use: 'Solar and roof purlins' },
    hat: { n: 'Solar: hat / omega sections', k: 'hat', unit: 'h × top × flange × t', list: [[40,30,15,2],[40,40,20,2],[50,60,20,2.5],[60,80,25,3]], use: 'Module rails, bracing' },
    chs: { n: 'Round pipes (CHS)', k: 'chs', unit: 'OD × t', list: [[21.3,2],[26.9,2.3],[33.7,2.6],[42.4,2.6],[48.3,2.9],[60.3,2.9],[76.1,3.2],[88.9,3.2],[114.3,3.6],[139.7,4.5],[168.3,4.5],[219.1,5]], use: 'Solar piles, poles, scaffolding, fencing (galvanized inside and out)' },
    shs: { n: 'Square / rectangular tubes (SHS / RHS)', k: 'shs', unit: 'B × H × t', list: [[25,25,2],[40,40,2.6],[50,50,3],[72,72,3.2],[100,100,4],[120,120,3],[150,150,5],[60,40,2.6],[80,40,3],[100,50,3.2],[122,61,3.6],[145,82,4.8]], use: 'Solar torque tubes, frames, gates (inside and out)' },
    cb: { n: 'Crash barriers', k: 'wbeam', unit: 'developed width × t', list: [[483,2.5],[483,3],[749,3]], label: ['W-beam 2.5 mm','W-beam 3 mm','Thrie-beam 3 mm'], use: 'Highway safety barriers' },
    tower: { n: 'Transmission / telecom tower angles', k: 'angle', unit: 'a × a × t', list: [[45,45,5],[50,50,6],[65,65,6],[75,75,6],[90,90,7],[100,100,8],[110,110,10],[130,130,10],[150,150,12],[200,200,16]], use: 'Lattice towers, bolted' },
    plate: { n: 'Plates and fabrications', k: 'plate', unit: 'thickness t', list: [[3],[5],[6],[8],[10],[12],[16],[20],[25]], use: 'Base plates, brackets, tanks, gratings' },
    fast: { n: 'Fasteners (spin galvanized)', k: 'bolt', unit: 'thread size', list: [[10],[12],[16],[20],[24],[30],[36]], label: ['M10','M12','M16','M20','M24','M30','M36'], use: 'Bolts, nuts, washers for towers and structures' }
  };
  function geo(fk, d) { // returns {A mm2, P mm, t mm, spun}
    var k = F[fk].k, a, b, t, h, tw, tf, c;
    switch (k) {
      case 'angle': a = d[0]; b = d[1]; t = d[2]; return { A: (a + b - t) * t, P: 2 * (a + b), t: t };
      case 'channel': case 'ibeam': case 'hbeam': h = d[0]; b = d[1]; tw = d[2]; tf = d[3];
        return { A: (k === 'channel' ? 2 : 2) * b * tf + (h - 2 * tf) * tw, P: k === 'channel' ? 2 * h + 4 * b - 2 * tw : 2 * h + 4 * b - 2 * tw, t: tf };
      case 'lipc': case 'zed': h = d[0]; b = d[1]; c = d[2]; t = d[3]; return { A: (h + 2 * b + 2 * c - 4 * t) * t, P: 2 * (h + 2 * b + 2 * c) - 4 * t, t: t };
      case 'hat': h = d[0]; b = d[1]; c = d[2]; t = d[3]; var w = b + 2 * h + 2 * c; return { A: w * t, P: 2 * w, t: t };
      case 'chs': return { A: Math.PI * (d[0] - d[1]) * d[1], P: Math.PI * (2 * d[0] - 2 * d[1]), t: d[1] };
      case 'shs': b = d[0]; h = d[1]; t = d[2]; return { A: 2 * t * (b + h - 2 * t), P: 4 * (b + h) - 8 * t, t: t };
      case 'wbeam': return { A: d[0] * d[1], P: 2 * d[0], t: d[1] };
      case 'plate': return { A: 1000 * d[0], P: 2000, t: d[0] };
      case 'bolt': var dd = d[0]; // cylinder with thread, head, nut and washer allowance
        return { A: Math.PI * dd * dd / 4, P: Math.PI * dd * 1.3, t: dd, spun: true };
    }
  }
  function coatMin(g) { // ISO 1461 / IS 4759 minimum mean coating thickness, micrometres
    if (g.spun) return g.t > 20 ? 55 : 45;
    return g.t > 6 ? 85 : g.t > 3 ? 70 : g.t >= 1.5 ? 55 : 45;
  }
  function sizeLabel(fk, i) { var f = F[fk]; return f.label ? f.label[i] : f.list[i].map(function (v) { return String(v); }).join(' × '); }
  // ---------- cross-section drawing ----------
  function section(fk, d) {
    var k = F[fk].k, s = '', W = 80, H = 80, sc, x0, y0;
    function poly(pts) { return '<path class="sx" d="M' + pts.map(function (p) { return p[0].toFixed(1) + ' ' + p[1].toFixed(1); }).join('L') + 'Z"/>'; }
    if (k === 'angle') { var a = d[0], b = d[1], t = d[2]; sc = 64 / Math.max(a, b); x0 = 8; y0 = 72;
      s = poly([[x0, y0], [x0 + b * sc, y0], [x0 + b * sc, y0 - t * sc], [x0 + t * sc, y0 - t * sc], [x0 + t * sc, y0 - a * sc], [x0, y0 - a * sc]]); }
    else if (k === 'channel' || k === 'ibeam' || k === 'hbeam') { var h = d[0], bb = d[1], tw = d[2], tf = d[3]; sc = 64 / Math.max(h, bb); var w = bb * sc, hh = h * sc; x0 = 40 - w / 2; y0 = 40 - hh / 2; var TW = Math.max(tw * sc, 1.4), TF = Math.max(tf * sc, 1.6);
      if (k === 'channel') s = poly([[x0, y0], [x0 + w, y0], [x0 + w, y0 + TF], [x0 + TW, y0 + TF], [x0 + TW, y0 + hh - TF], [x0 + w, y0 + hh - TF], [x0 + w, y0 + hh], [x0, y0 + hh]]);
      else { var cx = 40; s = poly([[x0, y0], [x0 + w, y0], [x0 + w, y0 + TF], [cx + TW / 2, y0 + TF], [cx + TW / 2, y0 + hh - TF], [x0 + w, y0 + hh - TF], [x0 + w, y0 + hh], [x0, y0 + hh], [x0, y0 + hh - TF], [cx - TW / 2, y0 + hh - TF], [cx - TW / 2, y0 + TF], [x0, y0 + TF]]); } }
    else if (k === 'lipc' || k === 'zed') { var h2 = d[0], b2 = d[1], c2 = d[2], t2 = d[3]; sc = 64 / Math.max(h2, b2 * 1.6); var hh2 = h2 * sc, w2 = b2 * sc, cc = c2 * sc, T = Math.max(t2 * sc, 1.3); x0 = 40 - w2 / 2; y0 = 40 - hh2 / 2;
      if (k === 'lipc') s = '<path class="sx2" d="M' + (x0 + w2) + ' ' + (y0 + cc) + 'V' + y0 + 'H' + x0 + 'V' + (y0 + hh2) + 'H' + (x0 + w2) + 'V' + (y0 + hh2 - cc) + '" stroke-width="' + T.toFixed(1) + '"/>';
      else s = '<path class="sx2" d="M' + (40 + w2) + ' ' + (y0 + cc) + 'V' + y0 + 'H40V' + (y0 + hh2) + 'H' + (40 - w2) + 'V' + (y0 + hh2 - cc) + '" stroke-width="' + T.toFixed(1) + '"/>'; }
    else if (k === 'hat') { var h3 = d[0], b3 = d[1], c3 = d[2], t3 = d[3]; sc = 64 / (b3 + 2 * c3 + 10); var hh3 = h3 * sc, bw = b3 * sc, cw = c3 * sc, T3 = Math.max(t3 * sc, 1.3); y0 = 40 - hh3 / 2;
      s = '<path class="sx2" d="M' + (40 - bw / 2 - cw) + ' ' + (y0 + hh3) + 'H' + (40 - bw / 2) + 'V' + y0 + 'H' + (40 + bw / 2) + 'V' + (y0 + hh3) + 'H' + (40 + bw / 2 + cw) + '" stroke-width="' + T3.toFixed(1) + '"/>'; }
    else if (k === 'chs') { var r = 32, ri = Math.max(r - d[1] * 32 / (d[0] / 2), r - 9); s = '<path class="sx" fill-rule="evenodd" d="M8 40a32 32 0 1 0 64 0a32 32 0 1 0-64 0ZM' + (40 - ri) + ' 40a' + ri + ' ' + ri + ' 0 1 0 ' + 2 * ri + ' 0a' + ri + ' ' + ri + ' 0 1 0 ' + (-2 * ri) + ' 0Z"/>'; }
    else if (k === 'shs') { var B = d[0], Hh = d[1], tt = d[2]; sc = 64 / Math.max(B, Hh); var bw2 = B * sc, hw = Hh * sc, T4 = Math.max(tt * sc, 1.6); x0 = 40 - bw2 / 2; y0 = 40 - hw / 2;
      s = '<path class="sx" fill-rule="evenodd" d="M' + x0 + ' ' + y0 + 'h' + bw2 + 'v' + hw + 'h' + (-bw2) + 'ZM' + (x0 + T4) + ' ' + (y0 + T4) + 'v' + (hw - 2 * T4) + 'h' + (bw2 - 2 * T4) + 'v' + (-(hw - 2 * T4)) + 'Z"/>'; }
    else if (k === 'wbeam') { s = d[0] > 600 ? '<path class="sx2" d="M6 30q6-14 12 0t12 0t12 0t12 0t12 0t12 0" stroke-width="2.2"/>' : '<path class="sx2" d="M8 40q8-18 16 0t16 0t16 0t16 0" stroke-width="2.2"/>'; }
    else if (k === 'plate') { var th = Math.max(Math.min(d[0] * 1.6, 30), 3); s = poly([[8, 40 - th / 2], [72, 40 - th / 2], [72, 40 + th / 2], [8, 40 + th / 2]]); }
    else if (k === 'bolt') { s = '<path class="sx" d="M10 30h10v20H10Z"/><path class="sx2" d="M20 36h46v8H20" stroke-width="1.6"/><path d="M28 36l2 8M34 36l2 8M40 36l2 8M46 36l2 8M52 36l2 8M58 36l2 8" stroke="currentColor" stroke-width=".6"/><path class="sx" d="M48 31h8v18h-8Z"/>'; }
    return '<svg viewBox="0 0 ' + W + ' ' + H + '" aria-hidden="true">' + s + '</svg>';
  }
  // ---------- defaults ----------
  var FUEL = { ng: { n: 'Natural gas (PNG)', u: 'Sm³', cv: 34, eff: .5, price: 48, kg: .75 }, lpg: { n: 'LPG', u: 'kg', cv: 46, eff: .5, price: 72, kg: 1 }, ldo: { n: 'LDO', u: 'litre', cv: 36.5, eff: .45, price: 82, kg: .85 },
               fo: { n: 'Furnace oil', u: 'kg', cv: 41, eff: .45, price: 58, kg: 1 }, el: { n: 'Electric', u: 'kWh', cv: 3.6, eff: .88, price: 8.5 } };
  var SI = { low: { n: 'Low silicon, Al-killed (Si ≤ 0.03 %)', f: 1.15 }, sand: { n: 'Sandelin range (Si 0.03–0.12 %)', f: 1.8 }, seb: { n: 'Sebisty range (Si 0.15–0.25 %)', f: 1.35 }, high: { n: 'High silicon (Si > 0.25 %)', f: 2.0 } };
  var st = { rows: [{ f: 'cpur', i: 4, s: 50 }, { f: 'chs', i: 6, s: 30 }, { f: 'isa', i: 6, s: 20 }], mode: 'batch',
    t: 1000, days: 26, shifts: 2, hours: 8, avail: 85, L: 6.5, W: 0.6, H: 1.2, fuel: 'ng', si: 'low',
    r: { zinc: 450, dross: 82.2, ash: 20, fuel: 48, power: 8.5, hcl: 4, chem: 500, wage: 20000, cons: 150, maint: 250, acidDisp: 4, water: 80 },
    x: { dross: 10, ash: 15, other: 3, hclkg: 25, kwh: 35, cycle: 12, crane: 5, lossP: 7, lossI: 3, lossW: .6, staff: 6 } };
  // ---------- state from the URL (so results can be shared) ----------
  try { var q = new URLSearchParams(location.search); if (q.get('mix')) { st.rows = q.get('mix').split(',').map(function (x) { var p = x.split(':'); return { f: p[0], i: +p[1], s: +p[2] }; }).filter(function (r) { return F[r.f] && F[r.f].list[r.i]; }); }
    ['t','days','shifts','hours','L','W','H'].forEach(function (k) { if (q.get(k)) st[k] = +q.get(k); }); if (q.get('fuel') && FUEL[q.get('fuel')]) st.fuel = q.get('fuel'); if (q.get('si') && SI[q.get('si')]) st.si = q.get('si'); if (q.get('mode')) st.mode = q.get('mode');
    if (q.get('fam') && F[q.get('fam')]) { st.rows = [{ f: q.get('fam'), i: Math.floor(F[q.get('fam')].list.length / 2), s: 100 }]; if (q.get('fam') === 'fast') st.mode = 'spin'; }
  } catch (e) {}
  if (!st.rows.length) st.rows = [{ f: 'isa', i: 6, s: 100 }];
  var fmt = function (v, d) { return (isFinite(v) ? v : 0).toLocaleString('en-IN', { maximumFractionDigits: d == null ? 0 : d, minimumFractionDigits: d == null ? 0 : d }); };
  var rs = function (v) { return '₹ ' + fmt(v); };
  var lakh = function (v) { return v >= 1e7 ? '₹ ' + fmt(v / 1e7, 2) + ' crore' : v >= 1e5 ? '₹ ' + fmt(v / 1e5, 2) + ' lakh' : rs(v); };
  // ---------- compute ----------
  function compute() {
    var tot = st.rows.reduce(function (a, r) { return a + (+r.s || 0); }, 0) || 1, m2t = 0, coatKg = 0, thin = 99, rowsOut = [];
    var siF = SI[st.si].f;
    st.rows.forEach(function (r) {
      var d = F[r.f].list[r.i], g = geo(r.f, d), kgm = g.A * RHO, m2m = g.P / 1000, a = m2m / kgm * 1000, cmin = coatMin(g), um = cmin * (g.spun ? 1.3 : siF), gm2 = um * 7.14 * .95, sh = (+r.s || 0) / tot;
      m2t += sh * a; coatKg += sh * a * gm2 / 1000; thin = Math.min(thin, g.t);
      rowsOut.push({ r: r, g: g, kgm: kgm, m2m: m2m, a: a, cmin: cmin, um: um, gm2: gm2, sh: sh });
    });
    var x = st.x, R = st.r, loss = (x.dross + x.ash + x.other) / 100, zTot = coatKg / (1 - loss), drossKg = zTot * x.dross / 100, ashKg = zTot * x.ash / 100;
    var hoursProd = st.days * st.shifts * st.hours * st.avail / 100, tph = st.t / Math.max(hoursProd, 1);
    // kettle
    var Lk, Wk, Dk, spinUnits = 0;
    if (st.mode === 'spin') { Lk = 2.5; Wk = 1.2; Dk = 1.5; spinUnits = Math.ceil(tph / 3.6); }
    /* SHIVAS kettle rule: inside length and width = largest article + 100 mm; depth = article height + 100 mm of zinc below it + 100 mm left empty at the top */
    else { Lk = +(st.L + .1).toFixed(2); Wk = +(st.W + .1).toFixed(2); Dk = +(st.H + .2).toFixed(2); }
    var zincT = Lk * Wk * (Dk - .1) * 6.6, ruleOk = zincT >= 10 * tph;
    if (!ruleOk && st.mode === 'spin') { while (Lk * Wk * (Dk - .1) * 6.6 < 10 * tph && Lk < 4) { Lk += .5; } }
    var zincT2 = Lk * Wk * (Dk - .1) * 6.6;
    var dips = 60 / x.cycle, perDip = tph / dips, craneNeed = (perDip * (1 + coatKg / 1000) + .8) * (1 + (st.mg || 0) / 100), crane = [3, 5, 7.5, 10, 12.5, 16, 20].find(function (c) { return c >= craneNeed; }) || 25;   // steel + zinc picked up + jig, then the chosen margin
    // heat and fuel
    var surf = Lk * Wk, wall = 2 * (Lk + Wk) * Dk + surf, lossP = surf * x.lossP + wall * x.lossW, lossI = surf * x.lossI + wall * x.lossW;
    var hoursIdle = Math.max(730 - hoursProd, 0), heatT = 215 + zTot * .28; // MJ per tonne of steel
    var fu = FUEL[st.fuel], netMJ = heatT * st.t + (lossP * hoursProd + lossI * hoursIdle) * 3.6, fuelUnits = netMJ / fu.eff / fu.cv;
    var kwFurnace = ((heatT * tph * 1000 / 3600) + lossP) / fu.eff * (1 + (st.mg || 0) / 100);   // V42: margin chosen by the visitor (none by default)
    // pretreatment line
    var pickTanks = Math.max(2, Math.ceil(45 / x.cycle)), tankL = Math.ceil((Lk + .3) * 2) / 2, tankW = Math.round((Wk + .3) * 10) / 10, tankD = Math.round((Dk + .1) * 10) / 10;
    var line = [['Degreasing', 1], ['Rinse', 1], ['Pickling (HCl)', pickTanks], ['Rinse', 2], ['Flux', 1], ['Drying pit', 1], ['Zinc kettle', 1], ['Quench', 1], ['Passivation', 1]];
    // people
    var perShift = Math.round(10 + 3 * tph), heads = perShift * st.shifts + x.staff;
    // costs per month
    var c = {}, M = st.t;
    c.zinc = zTot * M * R.zinc - drossKg * M * R.zinc * R.dross / 100 - ashKg * M * R.zinc * R.ash / 100;
    c.fuel = fuelUnits * (st.fuel === 'el' ? R.power : R.fuel);
    c.chem = M * (R.chem + x.hclkg * R.hcl); // SHIVAS recommended: degreaser, acid, flux and dichromate ₹500/t + additional HCl 25 kg/t × ₹4/kg
    c.waste = M * (x.hclkg * 1.1 * R.acidDisp + R.water);
    c.power = M * x.kwh * R.power;
    c.labour = heads * R.wage;
    c.other = M * (R.cons + R.maint);
    var sum = 0; Object.keys(c).forEach(function (k) { sum += c[k]; });
    return { rows: rowsOut, m2t: m2t, coatKg: coatKg, zTot: zTot, drossKg: drossKg, ashKg: ashKg, tph: tph, hoursProd: hoursProd, Lk: Lk, Wk: Wk, Dk: Dk, zincT: zincT2, ruleOk: ruleOk,
      dips: dips, perDip: perDip, drop: perDip * 215e3 / (zincT2 * 1000 * .5), crane: crane, craneNeed: craneNeed, fuelUnits: fuelUnits, fuelPerT: fuelUnits / M, kwFurnace: kwFurnace, line: line, tank: [tankL, tankW, tankD], heads: heads, perShift: perShift,
      cost: c, sum: sum, perT: sum / M, spinUnits: spinUnits, thin: thin };
  }
  // ---------- render ----------
  var LABEL = { zinc: 'Zinc (net of dross and ash sold)', fuel: 'Fuel / heating', chem: 'Acid, flux and chemicals', waste: 'Spent acid, water and effluent', power: 'Electricity (cranes, fans, pumps)', labour: 'Labour', other: 'Consumables and maintenance' };
  var COL = { zinc: '#1f4e79', fuel: '#e8a317', chem: '#0e7c86', waste: '#6b8aa6', power: '#9aa8b5', labour: '#c45c2a', other: '#4f6b3a' };
  function famOptions(sel) { return Object.keys(F).map(function (k) { return '<option value="' + k + '"' + (k === sel ? ' selected' : '') + '>' + F[k].n + '</option>'; }).join(''); }
  function sizeOptions(fk, sel) { return F[fk].list.map(function (d, i) { return '<option value="' + i + '"' + (i === +sel ? ' selected' : '') + '>' + sizeLabel(fk, i) + '</option>'; }).join(''); }
  function rowsHTML() {
    return st.rows.map(function (r, k) {
      return '<div class="mx" data-k="' + k + '"><label><span>Profile</span><select data-f>' + famOptions(r.f) + '</select></label>' +
        '<label><span>Size <i>' + F[r.f].unit + '</i></span><select data-i>' + sizeOptions(r.f, r.i) + '</select></label>' +
        '<label class="sh"><span>Share of tonnage</span><span class="u"><input type="number" min="0" max="100" step="5" value="' + r.s + '" data-s>%</span></label>' +
        (st.rows.length > 1 ? '<button type="button" class="mx-x" aria-label="Remove this profile">✕</button>' : '') + '<div class="mx-o"></div></div>';
    }).join('');
  }
  var mix = $('#cMix');
  function drawRows() { mix.innerHTML = rowsHTML(); }
  mix.addEventListener('change', function (e) {
    var row = e.target.closest('.mx'); if (!row) return; var r = st.rows[+row.dataset.k];
    if (e.target.hasAttribute('data-f')) { r.f = e.target.value; r.i = Math.floor(F[r.f].list.length / 2); if (r.f === 'fast') setMode('spin'); drawRows(); }
    else if (e.target.hasAttribute('data-i')) r.i = +e.target.value;
    else if (e.target.hasAttribute('data-s')) r.s = Math.max(0, +e.target.value || 0);
    run();
  });
  mix.addEventListener('input', function (e) { if (e.target.hasAttribute('data-s')) { st.rows[+e.target.closest('.mx').dataset.k].s = Math.max(0, +e.target.value || 0); run(); } });
  mix.addEventListener('click', function (e) { var b = e.target.closest('.mx-x'); if (!b) return; st.rows.splice(+b.closest('.mx').dataset.k, 1); drawRows(); run(); });
  $('#cAdd').addEventListener('click', function () { if (st.rows.length >= 6) return; st.rows.push({ f: 'ismc', i: 3, s: 10 }); drawRows(); run(); });
  // simple inputs bound by data-bind="path"
  function getP(p) { return p.split('.').reduce(function (o, k) { return o[k]; }, st); }
  function setP(p, v) { var ks = p.split('.'), o = st; for (var i = 0; i < ks.length - 1; i++) o = o[ks[i]]; o[ks[ks.length - 1]] = v; }
  [].forEach.call(root.querySelectorAll('[data-bind]'), function (el) {
    var p = el.getAttribute('data-bind'); el.value = getP(p);
    el.addEventListener('input', function () { var v = el.type === 'number' || el.type === 'range' ? +el.value : el.value; setP(p, v);
      if (p === 'fuel') { st.r.fuel = FUEL[v].price; var fe = root.querySelector('[data-bind="r.fuel"]'); if (fe) fe.value = st.r.fuel; $('#fuelU').textContent = '₹ / ' + FUEL[v].u; }
      var twin = root.querySelectorAll('[data-bind="' + p + '"]'); [].forEach.call(twin, function (t) { if (t !== el) t.value = el.value; });
      run(); });
  });
  var LOSS = { batch: { dross: 10, ash: 15, other: 3 }, spin: { dross: 12, ash: 22, other: 5 } };
  function setMode(m) { if (st.mode !== m) { var o = LOSS[st.mode], nw = LOSS[m]; ['dross', 'ash', 'other'].forEach(function (k) { if (st.x[k] === o[k]) { st.x[k] = nw[k]; var el = root.querySelector('[data-bind="x.' + k + '"]'); if (el) el.value = nw[k]; } }); }
    st.mode = m; [].forEach.call(root.querySelectorAll('[data-mode]'), function (b) { b.setAttribute('aria-pressed', String(b.dataset.mode === m)); }); $('#cArt').hidden = m === 'spin'; $('#cSpin').hidden = m !== 'spin'; }
  [].forEach.call(root.querySelectorAll('[data-mode]'), function (b) { b.addEventListener('click', function () { setMode(b.dataset.mode); run(); }); });
  /* V42: extra margin on equipment sizes (furnace rating, crane): none by default; the visitor can add 10, 20 or 30 % */
  try { st.mg = +localStorage.getItem('shivas.mg') || 0; } catch (e) { st.mg = 0; }
  if ([0, 10, 20, 30].indexOf(st.mg) < 0) st.mg = 0;
  (function () {
    var secs = root.querySelectorAll('.c-in > .cs'), after = secs[3] || secs[secs.length - 1]; if (!after) return;
    var box = document.createElement('div'); box.className = 'v42-mg';
    box.innerHTML = '<span class="v42-mg-l" title="Added to the furnace rating and the crane only; the kettle always follows the SHIVAS size rule. None gives the exact calculated need.">Extra margin on furnace and crane</span><div class="seg" role="group" aria-label="Extra margin on furnace and crane">' + [0, 10, 20, 30].map(function (m) { return '<button type="button" data-mg="' + m + '" aria-pressed="' + (m === st.mg) + '">' + (m ? '+' + m + ' %' : 'None') + '</button>'; }).join('') + '</div>';
    after.parentNode.insertBefore(box, after.nextSibling);
    box.addEventListener('click', function (e) { var b = e.target.closest('[data-mg]'); if (!b) return; st.mg = +b.getAttribute('data-mg'); try { localStorage.setItem('shivas.mg', String(st.mg)); } catch (_) {} [].forEach.call(box.querySelectorAll('[data-mg]'), function (x) { x.setAttribute('aria-pressed', String(x === b)); }); run(); });
  })();
  function run() {
    var o = compute(), x = st.x;
    // per-row facts
    o.rows.forEach(function (ro, k) { var el = mix.children[k] && mix.children[k].querySelector('.mx-o'); if (!el) return;
      el.innerHTML = section(ro.r.f, F[ro.r.f].list[ro.r.i]) + '<dl><div><dt>Weight</dt><dd>' + fmt(ro.kgm, 2) + ' kg/m</dd></div><div><dt>Surface</dt><dd>' + fmt(ro.m2m, 3) + ' m²/m</dd></div>' +
        '<div><dt>Surface per tonne</dt><dd><b>' + fmt(ro.a, 1) + ' m²/t</b></dd></div><div><dt>Coating</dt><dd>' + ro.cmin + ' µm min · ≈ ' + fmt(ro.um) + ' µm</dd></div></dl><p class="use">' + F[ro.r.f].use + '</p>'; });
    var tot = st.rows.reduce(function (a, r) { return a + (+r.s || 0); }, 0); $('#cShare').textContent = tot === 100 ? '' : 'Shares add up to ' + tot + ' %; the calculator scales them to 100 %.';
    var fu = FUEL[st.fuel], c = o.cost;
    $('#oHead').innerHTML = '<div class="kbig"><span>Running cost</span><b>' + rs(o.perT) + '</b><i>per tonne of black steel</i></div><div class="kbig"><span>Per month</span><b>' + lakh(o.sum) + '</b><i>at ' + fmt(st.t) + ' t a month</i></div>' +
      '<div class="kbig"><span>Zinc</span><b>' + fmt(o.zTot, 1) + ' kg</b><i>per tonne, before dross and ash credit</i></div>';
    $('#cMini').innerHTML = '<b>' + rs(o.perT) + ' / t</b><span>' + (st.mode === 'spin' ? 'spin kettle ' : 'kettle ') + o.Lk + ' × ' + o.Wk + ' × ' + o.Dk + ' m · ' + fmt(o.zTot, 1) + ' kg zinc/t</span><i>Results ↓</i>';
    $('#oBar').innerHTML = Object.keys(c).map(function (k) { return '<i style="flex:' + Math.max(c[k], 0) + ';background:' + COL[k] + '" title="' + LABEL[k] + '"></i>'; }).join('');
    $('#oCost').innerHTML = '<tr><th>Cost head</th><th>₹ / t</th><th>₹ / month</th><th>Share</th></tr>' + Object.keys(c).map(function (k) { return '<tr><td><i class="sw" style="background:' + COL[k] + '"></i>' + LABEL[k] + '</td><td>' + fmt(c[k] / st.t) + '</td><td>' + fmt(c[k]) + '</td><td>' + fmt(c[k] / o.sum * 100, 1) + ' %</td></tr>'; }).join('') +
      '<tr class="tot"><td>Total running cost</td><td>' + fmt(o.perT) + '</td><td>' + fmt(o.sum) + '</td><td>100 %</td></tr>';
    var kettleTxt = st.mode === 'spin' ? 'Spin kettle ' + o.Lk + ' × ' + o.Wk + ' × ' + o.Dk + ' m with ' + o.spinUnits + ' spinner' + (o.spinUnits > 1 ? 's' : '') : o.Lk + ' × ' + o.Wk + ' × ' + o.Dk + ' m (inside, L × W × D): your article + 100 mm in length and width, + 200 mm in depth';
    $('#oSize').innerHTML = [
      ['Throughput needed', fmt(o.tph, 2) + ' t/h over ' + fmt(o.hoursProd) + ' production hours a month' + (o.tph > 5 && st.mode !== 'spin' ? '; above about 5 t/h most plants run two lines or a third shift' : '')],
      ['Zinc kettle', kettleTxt],
      ['Zinc in the kettle', '≈ ' + fmt(o.zincT, 0) + ' t (' + fmt(o.zincT / Math.max(o.tph, .01), 0) + ' × hourly throughput' + (o.ruleOk || st.mode === 'spin' ? '' : '; below 10 ×, so the bath cools more on each dip: lighter loads or a deeper kettle help') + ')'],
      ['Dips per hour', fmt(o.dips, 1) + ' dips at ' + x.cycle + ' min a dip, ' + fmt(o.perDip, 2) + ' t of steel per dip'],
      ['Bath drop per dip', '≈ ' + fmt(o.drop, 1) + ' °C' + (o.drop > 10 ? ' (high: lighter loads, a deeper kettle or a second line)' : ' (fine below about 10 °C)')],
      ['Cranes', fmt(o.crane, 1) + ' t SWL over the kettle' + (o.tph > 2 ? ', plus a pretreatment crane' : '')],
      ['Furnace rating', '≈ ' + fmt(o.kwFurnace / 10, 0) * 10 + ' kW installed (' + fu.n + ')'],
      ['Pretreatment tanks', fmt(o.tank[0], 1) + ' × ' + fmt(o.tank[1], 1) + ' × ' + fmt(o.tank[2], 1) + ' m each'],
      ['People', o.perShift + ' a shift × ' + st.shifts + ' shifts + ' + x.staff + ' staff = ' + o.heads]
    ].map(function (r) { return '<div><dt>' + r[0] + '</dt><dd>' + r[1] + '</dd></div>'; }).join('');
    $('#oLine').innerHTML = o.line.map(function (l) { return '<li><b>' + (l[1] > 1 ? l[1] + ' × ' : '') + '</b>' + l[0] + '</li>'; }).join('');
    $('#oUse').innerHTML = [
      ['Surface per tonne (your mix)', fmt(o.m2t, 1) + ' m²/t'],
      ['Zinc in the coating', fmt(o.coatKg, 1) + ' kg/t'],
      ['Dross formed', fmt(o.drossKg, 1) + ' kg/t'],
      ['Zinc ash formed', fmt(o.ashKg, 1) + ' kg/t'],
      ['Total zinc bought', fmt(o.zTot, 1) + ' kg/t · ' + fmt(o.zTot * st.t / 1000, 1) + ' t a month'],
      ['Fuel', fmt(o.fuelPerT, 1) + ' ' + fu.u + '/t' + (fu.kg && fu.u !== 'kg' ? ' (≈ ' + fmt(o.fuelPerT * fu.kg, 1) + ' kg/t)' : '') + ' · ' + fmt(o.fuelUnits) + ' ' + fu.u + ' a month' + (fu.kg && fu.u !== 'kg' ? ' (≈ ' + fmt(o.fuelUnits * fu.kg / 1000, 1) + ' t)' : '')],
      ['Additional HCl (33 %)', fmt(x.hclkg, 1) + ' kg/t · ' + fmt(x.hclkg * st.t / 1000, 1) + ' t a month'],
      ['Degreaser, acid, flux and dichromate', rs(st.r.chem) + ' / t'],
      ['Electricity', fmt(x.kwh) + ' kWh/t' + (st.fuel === 'el' ? ' + furnace ' + fmt(o.fuelPerT) + ' kWh/t' : '')]
    ].map(function (r) { return '<div><dt>' + r[0] + '</dt><dd>' + r[1] + '</dd></div>'; }).join('');
    // share link and enquiry text
    var mixq = st.rows.map(function (r) { return r.f + ':' + r.i + ':' + r.s; }).join(',');
    var qs = '?mix=' + mixq + '&t=' + st.t + '&days=' + st.days + '&shifts=' + st.shifts + '&hours=' + st.hours + '&L=' + st.L + '&W=' + st.W + '&H=' + st.H + '&fuel=' + st.fuel + '&si=' + st.si + '&mode=' + st.mode;
    try { history.replaceState(null, '', qs); } catch (e) {}
    var summary = 'Galvanizing plant enquiry from the SHIVAS calculator\n\nProduct mix: ' + st.rows.map(function (r) { return F[r.f].n + ' ' + sizeLabel(r.f, r.i) + ' (' + r.s + ' %)'; }).join('; ') +
      '\nTarget: ' + st.t + ' t of black steel a month, ' + st.days + ' days, ' + st.shifts + ' shifts of ' + st.hours + ' h\nLargest article: ' + st.L + ' × ' + st.W + ' × ' + st.H + ' m\nFuel: ' + fu.n +
      '\n\nCalculator estimate: kettle ' + o.Lk + ' × ' + o.Wk + ' × ' + o.Dk + ' m, ' + fmt(o.tph, 2) + ' t/h, zinc ' + fmt(o.zTot, 1) + ' kg/t, running cost ' + rs(o.perT) + ' per tonne.\n\nLink: ' + location.href.split('?')[0] + qs;
    $('#oMail').target = '_blank'; $('#oMail').href = 'mailto:info@shivastechnology.com?cc=shivastechnology@gmail.com,info@shivasasia.com,shivasasia@gmail.com,shivas1470@gmail.com&subject=' + encodeURIComponent('Galvanizing plant: ' + st.t + ' t/month') + '&body=' + encodeURIComponent(summary);
    $('#oWa').href = 'https://wa.me/919810920468?text=' + encodeURIComponent(summary);
    $('#oCopy').onclick = function () { try { navigator.clipboard.writeText(summary); this.textContent = 'Copied'; var b = this; setTimeout(function () { b.textContent = 'Copy the summary'; }, 1600); } catch (e) {} };
  }
  drawRows(); if (st.mode === 'spin') { st.mode = 'batch'; setMode('spin'); } else setMode(st.mode); $('#fuelU').textContent = '₹ / ' + FUEL[st.fuel].u;
  // fill selects that come from data
  var fsel = root.querySelector('[data-bind="fuel"]'); fsel.innerHTML = Object.keys(FUEL).map(function (k) { return '<option value="' + k + '">' + FUEL[k].n + '</option>'; }).join(''); fsel.value = st.fuel;
  var ssel = root.querySelector('[data-bind="si"]'); ssel.innerHTML = Object.keys(SI).map(function (k) { return '<option value="' + k + '">' + SI[k].n + '</option>'; }).join(''); ssel.value = st.si;
  if (FUEL[st.fuel]) { st.r.fuel = FUEL[st.fuel].price; var fe = root.querySelector('[data-bind="r.fuel"]'); if (fe) fe.value = st.r.fuel; }
  run();
  window.SHIVAS_CALC = { compute: compute, state: st, F: F };
})();
