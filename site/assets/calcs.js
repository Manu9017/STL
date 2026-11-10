/* SHIVAS engineering calculators (calculators.html).
   Each calculator: inputs -> run(v) -> {key:[[label,value,sub]], rows:[[label,value]], table:{head,rows}, warn:[], note}.
   Planning estimates only; every input is editable. No SHIVAS prices are used anywhere. */
(function () {
  'use strict';
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var fx = function (v, d) { if (!isFinite(v)) return '—'; return (+v).toLocaleString('en-IN', { minimumFractionDigits: d || 0, maximumFractionDigits: d || 0 }); };
  var up = function (v, list) { for (var i = 0; i < list.length; i++) if (list[i] >= v - 1e-9) return list[i]; return list[list.length - 1]; };
  var KW = [0.37, 0.55, 0.75, 1.1, 1.5, 2.2, 3.7, 5.5, 7.5, 11, 15, 18.5, 22, 30, 37, 45, 55, 75, 90, 110, 132, 160, 200, 250, 315, 355, 400];
  var HP = [0.5, 0.75, 1, 1.5, 2, 3, 5, 7.5, 10, 12.5, 15, 20, 25, 30, 40, 50, 60, 75, 100, 125, 150, 180, 200, 250, 300, 350, 400, 500];
  /* V42: one extra margin for every final selection, chosen by the visitor: none (default), +10, +20 or +30 %.
     Each selection is the next standard size above (calculated need × (1 + margin)); nothing else is added. */
  var MG = 0; try { MG = +localStorage.getItem('shivas.mg') || 0; } catch (e) {}
  if ([0, 10, 20, 30].indexOf(MG) < 0) MG = 0;
  var MF = function () { return 1 + MG / 100; };
  var mgT = function () { return MG ? ', +' + MG + ' % margin' : ', no extra margin'; };
  var HPOF = [0.5, 0.75, 1, 1.5, 2, 3, 5, 7.5, 10, 15, 20, 25, 30, 40, 50, 60, 75, 100, 125, 150, 180, 215, 270, 340, 430, 480, 545];   // nameplate HP of each standard kW rating
  var motor = function (kwShaft) { var need = kwShaft * MF(); var k = up(need, KW); return { kw: k, hp: HPOF[KW.indexOf(k)], need: need }; };
  var round = function (v, step) { return Math.ceil(v / step - 1e-9) * step; };
  var CALCS = [];

  /* ---------------- 1. Wire drawing: passes, die sequence, speeds, power, output ---------------- */
  var MAT = {
    ms:  { n: 'Low carbon steel (MS, ≤ 0.1 % C)', uts: 380, k: 330, rho: 7850, red: 25, v: 12 },
    mc:  { n: 'Medium carbon (0.3–0.45 % C)', uts: 600, k: 380, rho: 7850, red: 22, v: 10 },
    hc:  { n: 'High carbon (0.6–0.85 % C, spring, LRPC)', uts: 1050, k: 450, rho: 7850, red: 20, v: 8 },
    ss:  { n: 'Stainless steel 304', uts: 650, k: 900, rho: 7900, red: 18, v: 6 },
    al:  { n: 'Aluminium (EC grade)', uts: 90, k: 70, rho: 2700, red: 22, v: 20 },
    cu:  { n: 'Copper (ETP)', uts: 230, k: 170, rho: 8900, red: 25, v: 20 }
  };
  CALCS.push({
    id: 'wire', mg: 1, div: 'wire', t: 'Wire drawing', s: 'Passes, die sequence, block speeds, kW and output',
    lead: 'Rod size to finished size: how many dies, the diameter after each die, the speed of every block, the drawing force and motor power per block, and what the machine makes in a day.',
    inputs: [
      { k: 'mat', l: 'Material', type: 'sel', opts: Object.keys(MAT).map(function (k) { return [k, MAT[k].n]; }), v: 'ms', set: function (v, st) { st.red = MAT[v].red; st.vf = MAT[v].v; } },
      { k: 'd0', l: 'Rod / entry Ø', u: 'mm', v: 5.5, step: 0.05, min: 0.5 },
      { k: 'df', l: 'Finished Ø', u: 'mm', v: 2.0, step: 0.01, min: 0.1 },
      { k: 'red', adv: 1, l: 'Largest area reduction per die', u: '%', v: 25, step: 0.5, min: 8, max: 40 },
      { k: 'vf', l: 'Finishing speed', u: 'm/s', v: 12, step: 0.5, min: 0.5, max: 40 },
      { k: 'alpha', adv: 1, l: 'Die half-angle', u: '°', v: 6, step: 0.5, min: 3, max: 15 },
      { k: 'mu', adv: 1, l: 'Friction in the die', u: 'μ', v: 0.05, step: 0.005, min: 0.01, max: 0.2 },
      { k: 'eff', adv: 1, l: 'Drive efficiency', u: '%', v: 88, step: 1, min: 60, max: 98 },
      { k: 'hrs', l: 'Running hours', u: 'h/day', v: 20, step: 0.5, min: 1, max: 24 },
      { k: 'util', adv: 1, l: 'Utilisation (stops, coil changes)', u: '%', v: 80, step: 1, min: 30, max: 100 }
    ],
    run: function (v) {
      var M = MAT[v.mat], A0 = Math.PI / 4 * v.d0 * v.d0, Af = Math.PI / 4 * v.df * v.df, warn = [];
      if (v.df >= v.d0) return { warn: ['The finished size must be smaller than the rod.'] };
      var rmax = v.red / 100, tot = Math.log(A0 / Af), n = Math.max(1, Math.ceil(tot / -Math.log(1 - rmax)));
      // taper: the last die takes about two-thirds of the average reduction, the rest share the remainder
      var eq = tot / n, last = n > 2 ? eq * 0.7 : eq, rest = n > 1 ? (tot - last) / (n - 1) : tot, a = v.alpha * Math.PI / 180;
      var d = v.d0, eps = 0, rows = [], sumKW = 0, maxRatio = 0, vf = v.vf;
      for (var i = 1; i <= n; i++) {
        var e = (i === n) ? last : rest, dIn = d, Ain = Math.PI / 4 * dIn * dIn, Aout = Ain / Math.exp(e), dOut = Math.sqrt(4 * Aout / Math.PI);
        var utsIn = M.uts + M.k * eps; eps += e; var utsOut = M.uts + M.k * eps;
        var sm = (utsIn + utsOut) / 2, sd = sm * ((1 + v.mu / a) * e + (2 / 3) * a), F = sd * Aout / 1000;   // kN (MPa × mm² = N)
        var vel = vf * Af / Aout, P = F * vel / (v.eff / 100), ratio = sd / utsOut; maxRatio = Math.max(maxRatio, ratio); sumKW += P;
        var mt = motor(P);
        rows.push([i, fx(dOut, 2), fx((1 - Aout / Ain) * 100, 1) + ' %', fx(vel, 2), fx(utsOut), fx(F, 2), fx(P, 1), mt.kw + ' kW · ' + mt.hp + ' HP', fx(ratio * 100) + ' %']);
        d = dOut;
      }
      if (maxRatio > 0.65) warn.push('Drawing stress reaches ' + fx(maxRatio * 100) + ' % of the wire strength in at least one die. Above about 60–65 % breaks become likely: lower the reduction per die or the die angle, or improve lubrication.');
      if (v.mat === 'hc' && eps > 2.2) warn.push('High carbon wire above a true strain of about 2.2 (≈ 89 % total reduction) usually needs patenting in between.');
      var kgh = M.rho * Af * 1e-6 * vf * 3600 * v.util / 100, tday = kgh * v.hrs / 1000;
      return {
        key: [['Dies', n, 'blocks on the machine'], ['Total reduction', fx((1 - Af / A0) * 100, 1) + ' %', 'true strain ' + fx(tot, 2)], ['Output', fx(tday, 1) + ' t/day', fx(kgh) + ' kg/h at ' + v.util + ' %'], ['Drawing power', fx(sumKW, 0) + ' kW', 'sum of all blocks']],
        table: { title: 'Die by die: diameter, speed, pull and motor', head: ['Die', 'Ø out mm', 'Reduction', 'Speed m/s', 'UTS MPa', 'Pull kN', 'Power kW', 'Motor', 'Stress / UTS'], rows: rows },
        rows: [['Finished wire tensile (estimate)', fx(M.uts + M.k * tot) + ' MPa'], ['Wire weight', fx(M.rho * Af * 1e-6, 4) + ' kg/m'], ['Rod speed into the first die', fx(vf * Af / A0, 2) + ' m/s'], ['Installed motors (sum)', fx(rows.reduce(function (s, r) { return s + parseFloat(r[7]); }, 0)) + ' kW']],
        warn: warn,
        note: 'Siebel drawing stress with work hardening per die; back tension, die wear and speed effects are not included. The last die takes a lighter reduction for size and finish. SHIVAS designs the actual die sequence with your rod and wire specification.'
      };
    }
  });

  /* ---------------- 2. Electro-galvanizing: rectifier selection ---------------- */
  CALCS.push({
    id: 'rectifier', mg: 1, div: 'wire', t: 'Electro-galvanizing rectifier', s: 'Current, current density and rectifier size',
    lead: 'From wire size, strands, line speed and zinc coating: the plating current, the current density on the wire, the rectifier rating and the zinc used.',
    inputs: [
      { k: 'd', l: 'Wire Ø', u: 'mm', v: 2.5, step: 0.05, min: 0.2 },
      { k: 'n', l: 'Strands', u: 'no.', v: 24, step: 1, min: 1 },
      { k: 'vl', l: 'Line speed', u: 'm/min', v: 40, step: 1, min: 1 },
      { k: 'g', l: 'Zinc coating', u: 'g/m²', v: 30, step: 1, min: 5, hint: '1 µm of zinc ≈ 7.14 g/m²' },
      { k: 'eff', adv: 1, l: 'Current efficiency', u: '%', v: 95, step: 1, min: 50, max: 100 },
      { k: 'L', adv: 1, l: 'Plating length (wire in the solution)', u: 'm', v: 30, step: 1, min: 1 },
      { k: 'cells', adv: 1, l: 'Plating cells', u: 'no.', v: 4, step: 1, min: 1 },
      { k: 'V', adv: 1, l: 'Cell voltage', u: 'V', v: 9, step: 0.5, min: 3, max: 24 },
      { k: 'hrs', adv: 1, l: 'Running hours', u: 'h/day', v: 20, step: 0.5, min: 1, max: 24 }
    ],
    run: function (v) {
      var dm = v.d / 1000, area = Math.PI * dm * v.vl * 60 * v.n;           // m² of wire surface plated per hour
      var zn = v.g * area, I = zn / (1.2195 * v.eff / 100);                  // g/h ; 1.2195 g of zinc per A·h
      var wet = Math.PI * dm * v.L * v.n, J = I / (wet * 100);               // A/dm²
      var perCell = I / v.cells, rated = up(perCell * MF(), [250, 500, 750, 1000, 1500, 2000, 2500, 3000, 4000, 5000, 6000, 8000, 10000, 12000, 15000]);
      var Vr = v.V <= 10 ? 12 : v.V <= 13 ? 15 : v.V <= 16 ? 18 : 24, kwdc = I * v.V / 1000, kva = rated * Vr * v.cells / 1000 / 0.85 / 0.9;
      var wireKgH = 7850 * Math.PI / 4 * dm * dm * v.vl * 60 * v.n, warn = [];
      if (J > 80) warn.push('Current density ' + fx(J, 0) + ' A/dm² is high for an acid zinc bath: lengthen the plating zone or slow the line.');
      if (J < 10) warn.push('Current density ' + fx(J, 0) + ' A/dm² is low: the line could run faster or the plating zone could be shorter.');
      return {
        key: [['Plating current', fx(I) + ' A', fx(I / 1000, 1) + ' kA in total'], ['Current density', fx(J, 0) + ' A/dm²', 'on the wire in the bath'], ['Rectifiers', v.cells + ' × ' + fx(rated) + ' A / ' + Vr + ' V', 'one per cell' + mgT()], ['Zinc', fx(zn * v.hrs / 1000, 0) + ' kg/day', fx(zn / 1000, 1) + ' kg/h']],
        rows: [['Coating thickness', fx(v.g / 7.14, 1) + ' µm'], ['Wire plated', fx(wireKgH * v.hrs / 1000, 1) + ' t/day (' + fx(wireKgH) + ' kg/h)'], ['Zinc per tonne of wire', fx(zn / wireKgH, 1) + ' kg/t'], ['Current per cell', fx(perCell) + ' A'], ['DC power', fx(kwdc, 0) + ' kW at ' + v.V + ' V'], ['Supply needed (all rectifiers)', '≈ ' + fx(kva, 0) + ' kVA'], ['Wire area in the bath', fx(wet, 2) + ' m²']],
        warn: warn,
        note: 'Faraday’s law with 1.2195 g of zinc per ampere-hour. Rectifier voltage must cover the bath, contacts and busbars; choose the anode-to-wire gap and contact rolls with SHIVAS. Water-cooled thyristor or switch-mode rectifiers in standard ratings.'
      };
    }
  });

  /* ---------------- 3. High-velocity burner rating for a galvanizing furnace ---------------- */
  var FUEL = { ng: ['Natural gas', 34, 'Sm³/h', .75], lpg: ['LPG', 46, 'kg/h', 1], ldo: ['LDO', 36.5, 'L/h', .85], fo: ['Furnace oil', 41, 'kg/h', 1] }; // [name, MJ per unit, unit, kg per unit]
  CALCS.push({
    id: 'burner', mg: 1, div: 'hdg', t: 'High-velocity burner kW', s: 'Firing rate, burners, wall heat flux, fuel',
    lead: 'From your largest article and the tonnage: the kettle it needs, the heat the furnace has to put into the zinc, the firing rate, how many high-velocity burners of what size, the heat flux on the kettle wall and the fuel per hour.',
    inputs: [
      { k: 'aL', l: 'Largest article: length (L)', u: 'm', v: 6.9, step: 0.1, min: 0.3 },
      { k: 'aB', l: 'Largest article: width (B)', u: 'm', v: 1.3, step: 0.05, min: 0.1 },
      { k: 'aH', l: 'Largest article: height as dipped (H)', u: 'm', v: 2.0, step: 0.05, min: 0.1 },
      { k: 'tph', l: 'Steel galvanized', u: 't/h', v: 6, step: 0.1, min: 0.1 },
      { k: 'kL', adv: 1, l: 'Kettle length, if you already have one', u: 'm', v: 0, step: 0.1, min: 0, hint: '0 = article + 100 mm' },
      { k: 'kW', adv: 1, l: 'Kettle width, if you already have one', u: 'm', v: 0, step: 0.05, min: 0, hint: '0 = article + 100 mm' },
      { k: 'kD', adv: 1, l: 'Kettle depth, if you already have one', u: 'm', v: 0, step: 0.05, min: 0, hint: '0 = article + 200 mm' },
      { k: 'tin', adv: 1, l: 'Steel temperature into the zinc', u: '°C', v: 60, step: 5, min: 0, max: 200, hint: 'dried work 60–120 °C' },
      { k: 'pick', adv: 1, l: 'Zinc picked up', u: 'kg/t', v: 60, step: 1, min: 10, max: 200 },
      { k: 'qs', adv: 1, l: 'Bath surface loss while dipping', u: 'kW/m²', v: 9, step: 0.5, min: 2, max: 20 },
      { k: 'eta', adv: 1, l: 'Furnace available heat', u: '%', v: 45, step: 1, min: 25, max: 75, hint: 'HV burners, cold air ≈ 45 %' },
      { k: 'nb', adv: 1, l: 'Burners', u: 'no.', v: 0, step: 1, min: 0, max: 12, hint: '0 = let the calculator choose' },
      { k: 'fuel', l: 'Fuel', type: 'sel', opts: Object.keys(FUEL).map(function (k) { return [k, FUEL[k][0]]; }), v: 'ng' }
    ],
    run: function (v) {
      /* SHIVAS kettle rule: inside length and width = article + 100 mm; depth = article height + 100 mm of zinc below + 100 mm empty at the top */
      v = Object.assign({}, v, { L: v.kL > 0 ? v.kL : v.aL + 0.1, W: v.kW > 0 ? v.kW : v.aB + 0.1, D: v.kD > 0 ? v.kD : v.aH + 0.2 });
      var zd = v.D - 0.1, area = v.L * v.W, wall = 2 * (v.L + v.W) * zd;
      var qSteel = v.tph * 1000 * 0.49 * (450 - v.tin) / 3600, qZn = v.tph * v.pick * (0.39 * 425 + 112) / 3600, qSurf = area * v.qs;
      var shell = 2 * (v.L + 1.4 + v.W + 1.4) * (v.D + 0.8) + (v.L + 1.4) * (v.W + 1.4) * 0.3, qCase = shell * 0.45;
      var net = qSteel + qZn + qSurf + qCase, fire = net / (v.eta / 100);
      var nb = v.nb > 0 ? v.nb : (v.L <= 8.5 ? 2 : v.L <= 13 ? 4 : 6), per = fire * MF() / nb;
      var sizes = [50, 80, 100, 150, 200, 250, 300, 350, 400, 500, 600, 750, 900, 1000, 1250, 1500], bk = up(per, sizes);
      var flux = (net - qSurf) / wall, hold = (area * 3 + qCase) / (v.eta / 100), zinc = v.L * v.W * zd * 6.6;
      var melt = zinc * 1000 * (0.39 * 425 + 112) / 3600 / (bk * nb * v.eta / 100 * 0.7), F = FUEL[v.fuel], warn = [];
      if (flux > 20) warn.push('Wall heat flux ' + fx(flux, 1) + ' kW/m² is above the usual 18–20 kW/m² limit for a steel kettle: a longer or deeper kettle, or lower throughput, protects the kettle.');
      if (zinc < v.tph * 10) warn.push('The zinc mass (' + fx(zinc, 0) + ' t) is less than ten times the hourly throughput; the bath will drop in temperature on heavy dips.');
      return {
        key: [['Firing rate', fx(fire) + ' kW', 'at full production'], ['Burners', nb + ' × ' + bk + ' kW', 'high-velocity' + mgT()], ['Wall heat flux', fx(flux, 1) + ' kW/m²', 'limit ≈ 18–20'], ['Fuel', fx(fire * 3.6 / F[1], 0) + ' ' + F[2], F[0] + ', full production' + (F[2].indexOf('kg') ? ' · ≈ ' + fx(fire * 3.6 / F[1] * F[3], 0) + ' kg/h' : '')]],
        rows: [['Kettle, inside (L × W × D)', fx(v.L, 2) + ' × ' + fx(v.W, 2) + ' × ' + fx(v.D, 2) + ' m' + (v.kL > 0 || v.kW > 0 || v.kD > 0 ? '' : ' (article + 100 / 100 / 200 mm)')], ['Heat into the steel', fx(qSteel) + ' kW'], ['Heat into new zinc', fx(qZn) + ' kW'], ['Bath surface loss', fx(qSurf) + ' kW'], ['Furnace casing loss', fx(qCase) + ' kW'], ['Net heat into the kettle', fx(net) + ' kW'], ['Holding (covered, idle) firing', fx(hold) + ' kW · ' + fx(hold * 3.6 / F[1], 1) + ' ' + F[2]], ['Zinc in the kettle', fx(zinc, 1) + ' t'], ['First melt with all burners', '≈ ' + fx(melt, 0) + ' h'], ['Fuel per tonne', fx(fire * 3.6 / F[1] / v.tph, 1) + ' ' + F[2].split('/')[0] + ' / t' + (F[2].indexOf('kg') ? ' (≈ ' + fx(fire * 3.6 / F[1] / v.tph * F[3], 1) + ' kg / t)' : '')]],
        warn: warn,
        note: 'Steel cp 0.49 kJ/kg·K; zinc heated from ingot and melted (112 kJ/kg). Furnace casing loss ≈ 0.45 kW/m². Available heat depends on excess air and flue temperature; a recuperator raises it. SHIVAS sets burner positions and firing so the wall is heated evenly.'
      };
    }
  });

  /* ---------------- 4. Wet scrubber + FRP blower ---------------- */
  var GAS = {
    hcl: { n: 'HCl fume (pickling)', lg: 2.5, htu: 0.5, v: 2.0, med: 'Water, NaOH polish' },
    h2so4: { n: 'H₂SO₄ mist', lg: 2.0, htu: 0.6, v: 2.0, med: 'Water + mesh demister' },
    hfno3: { n: 'HF / HNO₃ / NOx (stainless pickling)', lg: 3.0, htu: 0.8, v: 1.8, med: 'NaOH, two stages for NOx' },
    nh3: { n: 'Ammonia / flux fume', lg: 2.5, htu: 0.6, v: 2.0, med: 'Dilute acid dosing' },
    cr: { n: 'Chromic acid mist (plating)', lg: 2.0, htu: 0.6, v: 2.0, med: 'Water + mesh demister' }
  };
  CALCS.push({
    id: 'scrubber', mg: 1, div: 'rein', t: 'Fume scrubber + blower', s: 'Air flow, tower size, packing, pump, blower kW and HP',
    lead: 'Size a packed-bed fume scrubber from your tanks: the extraction air, tower diameter and packing height, recirculation pump, pressure drop, and the blower motor in kW and HP.',
    inputs: [
      { k: 'gas', l: 'Fume', type: 'sel', opts: Object.keys(GAS).map(function (k) { return [k, GAS[k].n]; }), v: 'hcl', set: function (v, st) { st.vs = GAS[v].v; st.lg = GAS[v].lg; } },
      { k: 'nt', l: 'Tanks extracted', u: 'no.', v: 3, step: 1, min: 0 },
      { k: 'tl', l: 'Tank length', u: 'm', v: 6, step: 0.1, min: 0.3 },
      { k: 'tw', l: 'Tank width', u: 'm', v: 1.2, step: 0.05, min: 0.3 },
      { k: 'cap', adv: 1, l: 'Capture rate', u: 'm³/s·m²', v: 0.38, step: 0.01, min: 0.1, max: 1.5, hint: 'push-pull ≈ 0.25, lateral slot ≈ 0.4' },
      { k: 'qx', adv: 1, l: 'Extra air (room, hoods)', u: 'm³/h', v: 0, step: 500, min: 0 },
      { k: 'vs', adv: 1, l: 'Tower air velocity', u: 'm/s', v: 2.0, step: 0.1, min: 0.8, max: 3 },
      { k: 'eff', adv: 1, l: 'Removal wanted', u: '%', v: 95, step: 0.5, min: 50, max: 99.9 },
      { k: 'lg', adv: 1, l: 'Liquid / gas ratio', u: 'L/m³', v: 2.5, step: 0.1, min: 0.5, max: 8 },
      { k: 'duct', adv: 1, l: 'Duct run', u: 'm', v: 40, step: 5, min: 0 },
      { k: 'feta', adv: 1, l: 'Fan efficiency', u: '%', v: 62, step: 1, min: 35, max: 85, hint: 'FRP centrifugal ≈ 60–65 %' }
    ],
    run: function (v) {
      var G = GAS[v.gas], Qh = v.nt * v.tl * v.tw * v.cap * 3600 + v.qx, Q = Qh / 3600;
      if (Q <= 0) return { warn: ['Enter tanks or extra air.'] };
      var D = round(Math.sqrt(4 * Q / (Math.PI * v.vs)), 0.05), vAct = Q / (Math.PI / 4 * D * D);
      var ntu = Math.log(1 / (1 - v.eff / 100)), H = Math.max(1.0, round(ntu * G.htu, 0.25));
      var Lr = Qh * v.lg / 1000, dpPack = 300 * H * Math.pow(vAct / 2, 2), dp = Math.round(dpPack + 150 + 150 + v.duct * 4 + 350 + 60);
      var kwShaft = Q * dp / (v.feta / 100) / 1000, m = motor(kwShaft), pump = Lr / 3600 * 1000 * 9.81 * 18 / 0.5 / 1000, pm = motor(pump);
      var dd = round(Math.sqrt(4 * Q / (Math.PI * 12)), 0.05), hcl = v.gas === 'hcl' ? v.nt * v.tl * v.tw * 0.05 : 0;
      var warn = []; if (D > 3.2) warn.push('A tower over 3.2 m across: two scrubbers in parallel are easier to make, ship and maintain.');
      return {
        key: [['Air flow', fx(Qh) + ' m³/h', fx(Q, 2) + ' m³/s'], ['Tower', 'Ø ' + fx(D * 1000) + ' mm', fx(H, 2) + ' m packing · ' + fx(vAct, 2) + ' m/s'], ['Blower motor', m.kw + ' kW · ' + m.hp + ' HP', fx(kwShaft, 1) + ' kW at the shaft'], ['Recirculation', fx(Lr, 1) + ' m³/h', 'pump ' + pm.kw + ' kW']],
        rows: [['System pressure drop', fx(dp) + ' Pa (packing ' + fx(dpPack) + ', demister, hoods, ' + v.duct + ' m duct, stack)'], ['Transfer units needed', fx(ntu, 2) + ' NTU for ' + v.eff + ' %'], ['Main duct at 12 m/s', 'Ø ' + fx(dd * 1000) + ' mm'], ['Scrubbing liquid', G.med], ['Recommended blower', 'FRP centrifugal, ' + m.kw + ' kW (' + m.hp + ' HP) motor, VFD']].concat(hcl ? [['HCl evaporated (≈ 50 g/m²·h)', fx(hcl, 2) + ' kg/h → NaOH ' + fx(hcl * 40 / 36.46, 2) + ' kg/h if neutralised']] : []),
        warn: warn,
        note: 'Capture air from tank surface area × capture rate; packing height = transfer units × height of a transfer unit for random PP packing. Pressure drop scales with the square of tower velocity. SHIVAS Reinplast builds the hoods, ducts, scrubber, FRP blower and stack in PP / FRP.'
      };
    }
  });

  /* ---------------- 5. Pulse-jet bag filter ---------------- */
  var DUST = { zn: ['Zinc / flux fume (galvanizing)', 0.9], gen: ['General process dust', 1.3], fdy: ['Foundry, metal dust', 1.1], cem: ['Cement, lime', 1.0], wood: ['Wood, light dust', 1.8] };
  CALCS.push({
    id: 'bagfilter', mg: 1, div: 'hdg', t: 'Bag filter', s: 'Cloth area, bags, housing, fan kW and HP',
    lead: 'Size a pulse-jet bag filter from the air flow and the dust: cloth area, number of bags, housing, can velocity, bag material for the temperature, fan power and compressed air.',
    inputs: [
      { k: 'Q', l: 'Air flow', u: 'm³/h', v: 30000, step: 500, min: 500 },
      { k: 'T', l: 'Gas temperature', u: '°C', v: 60, step: 5, min: 0, max: 300 },
      { k: 'dust', l: 'Dust', type: 'sel', opts: Object.keys(DUST).map(function (k) { return [k, DUST[k][0]]; }), v: 'zn', set: function (v, st) { st.ac = DUST[v][1]; } },
      { k: 'ac', adv: 1, l: 'Air-to-cloth ratio', u: 'm/min', v: 0.9, step: 0.05, min: 0.4, max: 3 },
      { k: 'bd', adv: 1, l: 'Bag Ø', u: 'mm', v: 160, step: 5, min: 100, max: 200 },
      { k: 'bl', adv: 1, l: 'Bag length', u: 'm', v: 3.0, step: 0.25, min: 1, max: 8 },
      { k: 'comp', adv: 1, l: 'Compartments', u: 'no.', v: 2, step: 1, min: 1, max: 8 },
      { k: 'dp', adv: 1, l: 'System pressure drop', u: 'Pa', v: 2500, step: 100, min: 500, max: 6000 },
      { k: 'feta', adv: 1, l: 'Fan efficiency', u: '%', v: 72, step: 1, min: 40, max: 85 },
      { k: 'load', adv: 1, l: 'Dust at the inlet', u: 'g/m³', v: 0.5, step: 0.1, min: 0 }
    ],
    run: function (v) {
      var cloth = v.Q / 60 / v.ac, ab = Math.PI * v.bd / 1000 * v.bl, perRow = 8;
      var nb = Math.ceil(cloth / ab / (perRow * v.comp)) * perRow * v.comp, acA = v.Q / 60 / (nb * ab), acC = v.comp > 1 ? v.Q / 60 / ((nb - nb / v.comp) * ab) : acA;
      var pitch = (v.bd + 70) / 1000, cols = nb / perRow, hw = perRow * pitch + 0.2, hl = cols * pitch + 0.2 * v.comp, net = hw * hl - nb * Math.PI / 4 * Math.pow(v.bd / 1000, 2), can = v.Q / 3600 / net;
      var kw = v.Q / 3600 * v.dp / (v.feta / 100) / 1000, m = motor(kw), air = nb * 0.18, dust = v.Q * v.load / 1000;
      var mat = v.T <= 120 ? 'Polyester needle felt (PTFE membrane for sticky fume)' : v.T <= 190 ? 'Aramid (Nomex) or PPS' : v.T <= 240 ? 'P84 / PTFE' : 'Fibreglass with PTFE finish (or cool the gas first)';
      var warn = []; if (can > 1.5) warn.push('Can velocity ' + fx(can, 2) + ' m/s is high; dust re-entrains after pulsing. Use longer bags or a larger housing.');
      if (v.dust === 'zn') warn.push('Flux fume (NH₄Cl / ZnCl₂) is sticky and absorbs water: lime pre-coat, PTFE membrane bags and heated hoppers in humid weather.');
      return {
        key: [['Bags', fx(nb) + ' × Ø' + v.bd + ' × ' + v.bl + ' m', v.comp + ' compartments'], ['Cloth area', fx(nb * ab, 0) + ' m²', 'air-to-cloth ' + fx(acA, 2) + ' m/min'], ['Fan motor', m.kw + ' kW · ' + m.hp + ' HP', fx(kw, 1) + ' kW at the shaft'], ['Can velocity', fx(can, 2) + ' m/s', 'keep below ≈ 1.5']],
        rows: [['Air-to-cloth, one compartment cleaning', fx(acC, 2) + ' m/min'], ['Housing (approx.)', fx(hw, 1) + ' × ' + fx(hl, 1) + ' m in plan'], ['Bag material for ' + v.T + ' °C', mat], ['Compressed air', '≈ ' + fx(air, 0) + ' Nm³/h dry, 5–6 bar'], ['Dust collected', fx(dust, 1) + ' kg/h'], ['Pulse valves', fx(cols) + ' rows of ' + perRow + ' bags']],
        warn: warn,
        note: 'Bags in rows of eight, one diaphragm valve per row. Housing size is a first estimate for layout. SHIVAS builds zinc fume extraction (ZFE) with the hoods, ducting, spark arrestor, filter, fan and stack.'
      };
    }
  });

  /* ---------------- 6. Fan / blower motor ---------------- */
  CALCS.push({
    id: 'fan', mg: 1, div: 'rein', t: 'Fan / blower motor', s: 'Air power, shaft kW, motor kW and HP',
    lead: 'Any fan or blower: from the air flow and the total pressure, the air power, the shaft power and the motor to install, in kW and HP.',
    inputs: [
      { k: 'Q', l: 'Air flow', u: 'm³/h', v: 20000, step: 500, min: 100 },
      { k: 'dp', l: 'Total pressure', u: 'Pa', v: 1500, step: 50, min: 50, hint: '1 mm WG ≈ 9.81 Pa' },
      { k: 'T', adv: 1, l: 'Air temperature', u: '°C', v: 35, step: 5, min: -10, max: 400 },
      { k: 'eta', adv: 1, l: 'Fan efficiency', u: '%', v: 65, step: 1, min: 30, max: 88 }
    ],
    run: function (v) {
      var Q = v.Q / 3600, air = Q * v.dp / 1000, shaft = air / (v.eta / 100), m = motor(shaft), rho = 1.2 * 293 / (273 + v.T);
      return {
        key: [['Motor', m.kw + ' kW', m.hp + ' HP'], ['Shaft power', fx(shaft, 2) + ' kW', fx(shaft / 0.746, 2) + ' HP'], ['Air power', fx(air, 2) + ' kW', ''], ['Pressure', fx(v.dp) + ' Pa', fx(v.dp / 9.81, 0) + ' mm WG']],
        rows: [['Air density at ' + v.T + ' °C', fx(rho, 3) + ' kg/m³'], ['Mass flow', fx(Q * rho * 3600) + ' kg/h'], ['Power at the same speed if the air were at 20 °C', fx(shaft * 1.2 / rho, 2) + ' kW (cold start)']],
        warn: v.T > 60 ? ['Hot air: start the fan against a closed damper or size the motor for cold air (' + fx(shaft * 1.2 / rho, 1) + ' kW).'] : [],
        note: 'Shaft power = flow × total pressure ÷ efficiency; the motor is the next standard rating above the shaft power, plus the extra margin you choose. SHIVAS Reinplast makes FRP and PP blowers for corrosive fume.'
      };
    }
  });

  /* ---------------- 7. Pickling acid consumption and spent acid ---------------- */
  CALCS.push({
    id: 'acid', div: 'rein', t: 'Pickling acid', s: 'Acid use, spent acid, tank charge',
    lead: 'How much hydrochloric acid your pickling uses, how much spent acid you have to dispose of or regenerate each month, and what one tank charge holds.',
    inputs: [
      { k: 't', l: 'Steel pickled', u: 't/mo', v: 1500, step: 50, min: 10 },
      { k: 'loss', adv: 1, l: 'Iron + scale removed', u: '% of steel', v: 0.8, step: 0.1, min: 0.1, max: 4, hint: 'light rust ≈ 0.5, mill scale ≈ 1–1.5' },
      { k: 'fe', adv: 1, l: 'Iron at which the bath is spent', u: 'g/L', v: 130, step: 5, min: 60, max: 180 },
      { k: 'nt', l: 'Pickling tanks', u: 'no.', v: 3, step: 1, min: 1 },
      { k: 'vol', l: 'Working volume per tank', u: 'm³', v: 22, step: 1, min: 0.5 },
      { k: 'conc', adv: 1, l: 'Bath strength when made up', u: '% HCl', v: 15, step: 1, min: 5, max: 20 }
    ],
    run: function (v) {
      var fe = v.t * 1000 * v.loss / 100 * 0.75, hcl = fe * 2 * 36.46 / 55.85 / 0.85, a33 = hcl / 0.33;   // 75 % of the loss is iron; 85 % of the acid is used
      var spent = fe / (v.fe / 1000) / 1000, perT = a33 / v.t, charge = v.vol * 1000 * 1.075 * v.conc / 100 / 0.33 / 1000;
      return {
        key: [['Acid 33 %', fx(a33 / 1000, 1) + ' t / month', fx(perT, 1) + ' kg per tonne of steel'], ['Spent acid', fx(spent, 0) + ' m³ / month', 'to regenerate or neutralise'], ['Iron dissolved', fx(fe / 1000, 1) + ' t / month', ''], ['One tank charge', fx(charge, 1) + ' t of 33 % acid', v.vol + ' m³ at ' + v.conc + ' %']],
        rows: [['Tank volume, all tanks', fx(v.nt * v.vol) + ' m³'], ['Bath life (all tanks)', '≈ ' + fx(v.nt * v.vol / Math.max(spent, 0.01) * 30, 0) + ' days'], ['Pure HCl consumed', fx(hcl / 1000, 1) + ' t / month'], ['Regeneration', 'Spent acid at this rate suits ' + (spent > 300 ? 'an acid regeneration plant (spray roaster)' : spent > 60 ? 'acid recovery / iron removal on site' : 'neutralisation in an ETP')]],
        warn: [],
        note: 'Fe + 2HCl → FeCl₂ + H₂; about 85 % of the acid charged is used before the bath is spent. Real use depends on the scale, inhibitor, temperature and drag-out. SHIVAS Reinplast builds pickling lines, fume scrubbers, acid recovery and effluent plants.'
      };
    }
  });

  window.SHIVAS_CALCS = CALCS;

  /* ---------------- UI ---------------- */
  var root = document.getElementById('calcs'); if (!root) return;
  var nav = $('.cx-nav', root), pane = $('.cx-pane', root), cur = null, st = {};
  var DIVN = { hdg: 'Galvanizing', wire: 'Wire', rein: 'Reinplast' };
  nav.innerHTML = CALCS.map(function (c) { return '<a href="#' + c.id + '" data-id="' + c.id + '" class="d-' + c.div + '"><small>' + DIVN[c.div] + '</small><b>' + c.t + '</b><span>' + c.s + '</span></a>'; }).join('') +
    '<a href="calculator.html" class="d-hdg ext"><small>Galvanizing</small><b>Plant size and running cost</b><span>Full plant planner, cost per tonne ↗</span></a>';
  function field(c, f) {
    var val = st[c.id][f.k], id = 'cx-' + c.id + '-' + f.k;
    if (f.type === 'sel') return '<label class="fld" for="' + id + '"><span>' + f.l + '</span><select id="' + id + '" data-k="' + f.k + '">' + f.opts.map(function (o) { return '<option value="' + o[0] + '"' + (o[0] === val ? ' selected' : '') + '>' + o[1] + '</option>'; }).join('') + '</select></label>';
    return '<label class="fld" for="' + id + '"><span>' + f.l + (f.hint ? ' <em>' + f.hint + '</em>' : '') + '</span><span class="u"><input id="' + id + '" type="number" inputmode="decimal" step="' + (f.step || 'any') + '"' + (f.min != null ? ' min="' + f.min + '"' : '') + (f.max != null ? ' max="' + f.max + '"' : '') + ' value="' + val + '" data-k="' + f.k + '">' + (f.u || '') + '</span></label>';
  }
  function open(id, push) {
    var c = CALCS.filter(function (x) { return x.id === id; })[0] || CALCS[0]; cur = c;
    if (!st[c.id]) { st[c.id] = {}; c.inputs.forEach(function (f) { st[c.id][f.k] = f.v; }); }
    var nAdv = c.inputs.filter(function (f) { return f.adv; }).length;
    [].forEach.call(nav.children, function (a) { a.setAttribute('aria-current', String(a.getAttribute('data-id') === c.id)); });
    var ca = nav.querySelector('[aria-current="true"]'); if (ca && nav.scrollWidth > nav.clientWidth + 4) nav.scrollTo({ left: ca.offsetLeft - 16, behavior: 'smooth' });
    document.documentElement.setAttribute('data-brand', c.div === 'rein' ? 'rein' : 'tech');
    pane.innerHTML = '<div class="cx-h"><span class="k">' + DIVN[c.div] + ' · calculator</span><h2>' + c.t + '</h2><p>' + c.lead + '</p></div>' +
      '<div class="cx-grid"><form class="cx-in" onsubmit="return false">' + (c.mg ? '<div class="cx-mg" role="group" aria-label="Extra margin on the selected size"><span class="cx-mg-l" title="Added to the calculated need before the next standard size is chosen. None gives the exact need.">Extra margin</span><div class="seg">' + [0, 10, 20, 30].map(function (m) { return '<button type="button" data-mg="' + m + '" aria-pressed="' + (m === MG) + '">' + (m ? '+' + m + ' %' : 'None') + '</button>'; }).join('') + '</div></div>' : '') + c.inputs.filter(function (f) { return !f.adv; }).map(function (f) { return field(c, f); }).join('') +
      (nAdv ? '<button type="button" class="cx-adv-t" aria-expanded="' + !!st[c.id]._adv + '" aria-controls="cxAdv"><span><b>Advanced</b> · ' + nAdv + ' more inputs for a closer answer</span><em aria-hidden="true">↓</em></button>' +
        '<p class="cx-assume"' + (st[c.id]._adv ? ' hidden' : '') + '></p>' +
        '<div class="cx-adv" id="cxAdv"' + (st[c.id]._adv ? '' : ' hidden') + '>' + c.inputs.filter(function (f) { return f.adv; }).map(function (f) { return field(c, f); }).join('') + '</div>' : '') +
      '<button type="button" class="btn line sm cx-reset">Reset to typical values</button></form>' +
      '<div class="cx-out"><div class="cx-res" aria-live="polite"></div>' + ASK + '</div></div><div class="cx-wide"></div>';
    $('.cx-in', pane).addEventListener('input', change); $('.cx-in', pane).addEventListener('change', change);
    [].forEach.call(pane.querySelectorAll('[data-mg]'), function (b) { b.addEventListener('click', function () { MG = +b.getAttribute('data-mg'); try { localStorage.setItem('shivas.mg', String(MG)); } catch (e) {} [].forEach.call(pane.querySelectorAll('[data-mg]'), function (x) { x.setAttribute('aria-pressed', String(x === b)); }); calc(); }); });
    $('.cx-reset', pane).addEventListener('click', function () { var a = st[c.id]._adv; delete st[c.id]; open(c.id); if (a) toggleAdv(true); });
    var at = $('.cx-adv-t', pane); if (at) at.addEventListener('click', function () { toggleAdv(at.getAttribute('aria-expanded') !== 'true'); });
    askInit();
    calc();
    if (push) { try { history.replaceState(null, '', '#' + c.id); } catch (e) {} }
  }
  function toggleAdv(on) {
    var at = $('.cx-adv-t', pane); if (!at) return; st[cur.id]._adv = on;
    at.setAttribute('aria-expanded', String(on)); $('.cx-adv', pane).hidden = !on; $('.cx-assume', pane).hidden = on;
    if (on) { var f = $('.cx-adv input,.cx-adv select', pane); if (f) f.focus({ preventScroll: true }); }
  }
  function assumed() {
    var p = $('.cx-assume', pane); if (!p) return;
    p.innerHTML = '<span>Typical values used:</span> ' + cur.inputs.filter(function (f) { return f.adv; }).map(function (f) {
      var v = st[cur.id][f.k]; if (f.type === 'sel') v = f.opts.filter(function (o) { return o[0] === v; })[0][1];
      var auto = !v && f.hint && f.hint.indexOf('0 =') === 0;
      return '<i>' + f.l.replace(/ \(.*\)$/, '').replace(/, if you already have one$/, '') + ' ' + (auto ? (f.k === 'nb' ? 'auto' : 'from the article') : v) + (f.u && f.type !== 'sel' && !auto ? '\u00a0' + f.u : '') + '</i>';
    }).join(' ');
  }
  /* "Ask our engineer": the visitor's own details and this calculation, sent to SHIVAS (visitor log when set up, else WhatsApp) */
  var ASK = '<div class="cx-ask"><button type="button" class="btn amber cx-ask-t" aria-expanded="false">Ask our engineer to check this</button>' +
    '<form class="cx-ask-f" hidden novalidate><p class="cx-ask-h">We reply with a checked sizing and a proposal.</p>' +
    '<label class="fld"><span>Name</span><input name="name" autocomplete="name" required></label>' +
    '<label class="fld"><span>Company</span><input name="company" autocomplete="organization"></label>' +
    '<label class="fld"><span>Phone / WhatsApp</span><input name="phone" type="tel" autocomplete="tel" inputmode="tel" required></label>' +
    '<label class="fld"><span>Email</span><input name="email" type="email" autocomplete="email"></label>' +
    '<p class="cx-ask-e" hidden>Add your name and a phone number.</p>' +
    '<div class="cx-act"><button type="submit" class="btn amber">Send to SHIVAS</button><a class="btn line cx-ask-mail" href="#" target="_blank" rel="noopener">Email instead</a></div>' +
    '<p class="cx-ask-n">Used only to reply to you. <a href="privacy.html">Privacy</a></p></form><p class="cx-ask-ok" hidden></p></div>';
  var lastSum = '';
  function askInit() {
    var t = $('.cx-ask-t', pane), f = $('.cx-ask-f', pane), ok = $('.cx-ask-ok', pane);
    t.addEventListener('click', function () { var o = f.hidden; f.hidden = !o; t.setAttribute('aria-expanded', String(o)); if (o) f.querySelector('input').focus(); });
    $('.cx-ask-mail', f).addEventListener('click', function (e) {
      var ALL = ['info@shivastechnology.com', 'shivastechnology@gmail.com', 'info@shivasasia.com', 'shivasasia@gmail.com', 'shivas1470@gmail.com'], to = cur.div === 'rein' ? 'info@shivasasia.com' : 'info@shivastechnology.com', cc = ALL.filter(function (x) { return x !== to; }).join(',');
      this.href = 'mailto:' + to + '?cc=' + cc + '&subject=' + encodeURIComponent('Calculator: ' + cur.t) + '&body=' + encodeURIComponent(who() + '\n\n' + lastSum + '\n\nPlease check this and send a proposal.');
    });
    function who() { var d = new FormData(f); return ['Name: ' + d.get('name'), 'Company: ' + d.get('company'), 'Phone: ' + d.get('phone'), 'Email: ' + d.get('email')].join('\n'); }
    f.addEventListener('submit', function (e) {
      e.preventDefault(); var d = new FormData(f), name = (d.get('name') || '').trim(), phone = (d.get('phone') || '').trim();
      $('.cx-ask-e', f).hidden = !!(name && phone); if (!name || !phone) return;
      var T = window.SHIVAS_TRACK, sent = T && T.lead({ source: 'Calculator · ' + cur.t, div: cur.div, name: name, company: (d.get('company') || '').trim(), contact: phone, email: (d.get('email') || '').trim(), product: cur.t, message: lastSum });
      if (!sent) window.open('https://wa.me/919810920468?text=' + encodeURIComponent(who() + '\n\n' + lastSum + '\n\nPlease check this and send a proposal.'), '_blank', 'noopener');
      f.hidden = true; t.hidden = true; ok.hidden = false;
      ok.textContent = sent ? 'Sent. A SHIVAS engineer will call or WhatsApp you on ' + phone + '.' : 'WhatsApp opened with your details and this calculation. Press send there.';
    });
  }
  function change(e) {
    var el = e.target, k = el.getAttribute('data-k'); if (!k) return; var f = cur.inputs.filter(function (x) { return x.k === k; })[0];
    var val = f.type === 'sel' ? el.value : parseFloat(el.value); if (f.type !== 'sel' && !isFinite(val)) return;
    st[cur.id][k] = val;
    if (f.set && e.type === 'change') { f.set(val, st[cur.id]); cur.inputs.forEach(function (g) { var i = $('[data-k="' + g.k + '"]', pane); if (i && g.k !== k) i.value = st[cur.id][g.k]; }); }
    calc();
    clearTimeout(change.t); change.t = setTimeout(function () { var T = window.SHIVAS_TRACK; if (T) T.event('calc', { calc: cur.t, detail: lastSum.slice(0, 900) }); }, 15000);
  }
  function calc() {
    var r; try { r = cur.run(st[cur.id]); } catch (err) { r = { warn: ['Check the inputs.'] }; console.error(err); }
    var o = $('.cx-res', pane), h = ''; assumed();
    if (r.key) h += '<div class="cx-key">' + r.key.map(function (k) { return '<div><span>' + k[0] + '</span><b' + (String(k[1]).length > 11 ? ' class="l"' : '') + '>' + k[1] + '</b><small>' + (k[2] || '') + '</small></div>'; }).join('') + '</div>';
    if (r.warn && r.warn.length) h += r.warn.map(function (w) { return '<p class="cx-warn">' + w + '</p>'; }).join('');
    var tw = r.table ? '<p class="k cx-tt">' + (r.table.title || 'Step by step') + '</p><div class="cx-tw" tabindex="0" role="region" aria-label="Step by step table"><table class="cx-t"><thead><tr>' + r.table.head.map(function (x) { return '<th>' + x + '</th>'; }).join('') + '</tr></thead><tbody>' + r.table.rows.map(function (row) { return '<tr>' + row.map(function (x) { return '<td>' + x + '</td>'; }).join('') + '</tr>'; }).join('') + '</tbody></table></div>' : '';
    if (r.rows) h += '<dl class="cx-dl">' + r.rows.map(function (x) { return '<div><dt>' + x[0] + '</dt><dd>' + x[1] + '</dd></div>'; }).join('') + '</dl>';
    if (r.note) h += '<p class="cx-note">' + r.note + '</p>';
    var sum = cur.t + '\n' + cur.inputs.map(function (f) { var v = st[cur.id][f.k]; if (f.type === 'sel') v = f.opts.filter(function (o) { return o[0] === v; })[0][1]; return f.l + ': ' + v + (f.u && f.type !== 'sel' ? ' ' + f.u : ''); }).join('\n') +
      (cur.mg ? '\nExtra margin on the selected size: ' + (MG ? '+' + MG + ' %' : 'none') : '') + '\n\nResults\n' + (r.key || []).map(function (k) { return k[0] + ': ' + k[1] + (k[2] ? ' (' + k[2] + ')' : ''); }).join('\n');
    lastSum = sum;
    h += '<div class="cx-act"><a class="btn line" target="_blank" rel="noopener" href="https://wa.me/919810920468?text=' + encodeURIComponent(sum) + '">WhatsApp it</a><button type="button" class="btn line cx-copy">Copy</button></div>';
    o.innerHTML = h; $('.cx-wide', pane).innerHTML = tw;
    $('.cx-copy', o).addEventListener('click', function () { try { navigator.clipboard.writeText(sum); this.textContent = 'Copied'; } catch (e) {} });
  }
  nav.addEventListener('click', function (e) { var a = e.target.closest('a[data-id]'); if (!a) return; e.preventDefault(); open(a.getAttribute('data-id'), true); if (innerWidth < 900) pane.scrollIntoView({ behavior: 'smooth', block: 'start' }); });
  function fromHash() { var h = (location.hash || '').slice(1); open(CALCS.some(function (c) { return c.id === h; }) ? h : CALCS[0].id); }
  addEventListener('hashchange', fromHash); fromHash();
})();
