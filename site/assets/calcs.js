/* SHIVAS engineering calculators (calculators.html).
   Each calculator: inputs -> run(v) -> {key:[[label,value,sub]], rows:[[label,value]], table:{head,rows}, warn:[], note}.
   Planning estimates only; every input is editable. No SHIVAS prices are used anywhere. */
(function () {
  'use strict';
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var fx = function (v, d) { if (!isFinite(v)) return 'n/a'; return (+v).toLocaleString('en-IN', { minimumFractionDigits: d || 0, maximumFractionDigits: d || 0 }); };
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
    ss:  { n: 'Stainless steel 304', uts: 650, k: 900, rho: 7900, red: 18, v: 6 }
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

  /* ---------------- 8. Hot-dip galvanized coating against ISO 1461 ---------------- */
  // ISO 1461 minimum [local, mean] in µm, and the standard's own g/m² for each (nominal 7.2 g/m² per µm)
  var ISO_G = { 20: 145, 25: 180, 35: 250, 40: 285, 45: 325, 50: 360, 55: 395, 60: 430, 70: 505, 80: 575, 85: 610 };
  var ART = {
    st: ['Steel sections and plate', function (t) { return t > 6 ? [70, 85, 'over 6 mm thick'] : t > 3 ? [55, 70, 'over 3 mm up to 6 mm'] : t >= 1.5 ? [45, 55, '1.5 mm up to 3 mm'] : [35, 45, 'under 1.5 mm']; }],
    ca: ['Castings', function (t) { return t >= 6 ? [70, 80, '6 mm and over'] : [60, 70, 'under 6 mm']; }],
    thr: ['Centrifuged: bolts, studs and nuts', function (t) { return t > 6 ? [40, 50, 'thread over 6 mm Ø'] : [20, 25, 'thread 6 mm Ø and under']; }],
    oth: ['Centrifuged: other small parts', function (t) { return t >= 3 ? [45, 55, '3 mm and over'] : [35, 45, 'under 3 mm']; }]
  };
  CALCS.push({
    id: 'coating', div: 'hdg', t: 'Coating thickness check', s: 'ISO 1461 minimums, g/m², zinc per tonne',
    lead: 'Check a hot-dip galvanized coating against the ISO 1461 minimums for your steel. Enter the mean of your gauge readings and the lowest local value: see whether each one passes, the coating mass in g/m² and the zinc the coating puts on each tonne of steel.',
    inputs: [
      { k: 'kind', l: 'Article', type: 'sel', opts: Object.keys(ART).map(function (k) { return [k, ART[k][0]]; }), v: 'st' },
      { k: 'tk', l: 'Steel thickness (thread Ø for bolts)', u: 'mm', v: 8, step: 0.5, min: 0.3 },
      { k: 'mean', l: 'Mean of all readings', u: 'µm', v: 95, step: 1, min: 0 },
      { k: 'low', l: 'Lowest local value', u: 'µm', v: 78, step: 1, min: 0, hint: 'the average in one reference area' },
      { k: 'area', adv: 1, l: 'Surface per tonne, if you know it', u: 'm²/t', v: 0, step: 1, min: 0, hint: '0 = worked out from the thickness', auto: 'from the thickness' }
    ],
    run: function (v) {
      if (!(v.tk > 0)) return { warn: ['Enter the steel thickness.'] };
      var A = ART[v.kind], m = A[1](v.tk), loc = m[0], mean = m[1];
      var area = v.area > 0 ? v.area : (v.kind === 'thr' ? 4000 : 2000) / (7.85 * v.tk);   // m² per tonne: flat steel (both faces) or a round bar
      var mass = v.mean * 7.2, kgt = mass * area / 1000, extra = Math.max(0, v.mean - mean) * 7.2 * area / 1000;
      var okM = v.mean >= mean, okL = v.low >= loc, warn = [];
      if (v.low > v.mean) warn.push('The lowest local value cannot be higher than the mean of all readings. Check the two entries.');
      if (!okM || !okL) warn.push('Below the ISO 1461 minimum. Before you decide, check the gauge on bare steel of the same thickness and measure away from edges, corners, holes and flame-cut faces.');
      if (v.mean > 200) warn.push('A mean over 200 µm usually comes from reactive steel (silicon or phosphorus) or a long dip. Such coatings use more zinc and flake more easily on impact. See <a href="blog/silicon-and-the-sandelin-effect.html">silicon and the Sandelin effect</a>.');
      return {
        key: [['Mean', fx(v.mean) + ' µm', okM ? 'passes: minimum ' + mean + ' µm' : 'below the ' + mean + ' µm minimum'],
          ['Lowest local', fx(v.low) + ' µm', okL ? 'passes: minimum ' + loc + ' µm' : 'below the ' + loc + ' µm minimum'],
          ['Coating mass', fx(mass) + ' g/m²', 'from the mean'],
          ['Zinc on the steel', fx(kgt, 1) + ' kg/t', fx(area, 1) + ' m² per tonne']],
        rows: [['ISO 1461 class', A[0] + ', ' + m[2]], ['Minimum local', loc + ' µm (' + ISO_G[loc] + ' g/m²)'], ['Minimum mean', mean + ' µm (' + ISO_G[mean] + ' g/m²)'],
          ['Zinc at the minimum mean', fx(mean * 7.2 * area / 1000, 1) + ' kg per tonne of steel'], ['Zinc above the minimum', fx(extra, 1) + ' kg per tonne of steel']],
        warn: warn,
        note: 'Minimums from ISO 1461 for articles that are not centrifuged and for centrifuged ones, with coating mass at the standard\'s nominal 7.2 g/m² per µm. A local value is the average of the gauge readings in one reference area; the mean is the average over all the reference areas on the article or sample. Surface per tonne is estimated from the thickness (flat steel 254.8 ÷ t, bolts 509.6 ÷ Ø); zinc lost to dross and ash comes on top. If your order names ASTM A123 or IS 4759, check against that standard\'s own table.'
      };
    }
  });

  /* ---------------- 9. Wire weight, length, coil and zinc on galvanized wire ---------------- */
  CALCS.push({
    id: 'wireweight', div: 'wire', t: 'Wire weight and length', s: 'kg per km, metres per coil, output, zinc',
    lead: 'From the wire size: the weight per metre and per kilometre, how many metres a coil or spool holds and how long it takes to fill, what the machine makes in an hour and a day, and the zinc a galvanized coating puts on each tonne of wire.',
    inputs: [
      { k: 'd', l: 'Wire Ø', u: 'mm', v: 2.5, step: 0.01, min: 0.05 },
      { k: 'coil', l: 'Coil or spool weight', u: 'kg', v: 1000, step: 10, min: 1 },
      { k: 'v', l: 'Line speed', u: 'm/s', v: 10, step: 0.5, min: 0.05, max: 40 },
      { k: 'g', l: 'Zinc coating, if galvanized', u: 'g/m²', v: 0, step: 5, min: 0, hint: '0 = black wire' },
      { k: 'n', adv: 1, l: 'Strands or machines running', u: 'no.', v: 1, step: 1, min: 1 },
      { k: 'hrs', adv: 1, l: 'Running hours', u: 'h/day', v: 20, step: 0.5, min: 1, max: 24 },
      { k: 'util', adv: 1, l: 'Utilisation (stops, coil changes)', u: '%', v: 80, step: 1, min: 10, max: 100 },
      { k: 'rho', adv: 1, l: 'Steel density', u: 'kg/m³', v: 7850, step: 10, min: 7000, max: 8100 }
    ],
    run: function (v) {
      if (!(v.d > 0) || !(v.v > 0)) return { warn: ['Enter the wire size and the line speed.'] };
      var kgm = v.rho * Math.PI / 4 * v.d * v.d * 1e-6, len = v.coil / kgm, fill = len / v.v / 60;
      var kgh = kgm * v.v * 3600 * v.n, tday = kgh * v.hrs * v.util / 100 / 1000;
      var perM = Math.PI * v.d / 1000, sa = perM / kgm * 1000, zt = v.g * sa / 1000, warn = [];   // m² of surface per metre and per tonne; zinc kg/t
      if (fill < 5) warn.push('A coil of ' + fx(v.coil) + ' kg fills in under 5 minutes at this speed. A bigger package or a twin take-up saves stops.');
      var rows = [['Metres per kg', fx(1 / kgm, 2) + ' m'], ['Cross-section', fx(Math.PI / 4 * v.d * v.d, 3) + ' mm²'], ['Output a day', fx(tday, 1) + ' t at ' + v.hrs + ' h and ' + v.util + ' %'], ['Surface per tonne', fx(sa, 1) + ' m²']];
      if (v.g > 0) rows = rows.concat([['Coating thickness', fx(v.g / 7.14, 1) + ' µm'], ['Zinc per tonne of wire', fx(zt, 1) + ' kg'], ['Zinc in one coil', fx(v.g * perM * len / 1000, 1) + ' kg'], ['Galvanized wire weight', fx((kgm + v.g * perM / 1000) * 1000, 1) + ' kg/km']]);
      return {
        key: [['Weight', fx(kgm * 1000, 1) + ' kg/km', fx(kgm, 4) + ' kg per metre'], ['One coil holds', fx(len) + ' m', fx(len / 1000, 2) + ' km in ' + fx(v.coil) + ' kg'],
          ['Output', fx(kgh / 1000, 2) + ' t/h', (v.n > 1 ? v.n + ' strands' : 'one strand') + ' at ' + v.v + ' m/s'], ['Coil fills in', fx(fill, fill < 10 ? 1 : 0) + ' min', 'at ' + v.v + ' m/s']],
        rows: rows,
        warn: warn,
        note: 'Weight from the nominal size at ' + fx(v.rho) + ' kg/m³. Surface per tonne = 4,000 ÷ (7.85 × Ø in mm). Coating thickness at 7.14 g/m² per µm of zinc; zinc lost to dross, ash and wiping comes on top. Check the coating mass against the standard on your order, for example IS 4826 or ISO 7989-2.'
      };
    }
  });

  /* ---------------- 10. Spent acid neutralisation: lime, sludge and salt ---------------- */
  CALCS.push({
    id: 'neutralise', div: 'rein', t: 'Spent acid neutralisation', s: 'Lime, filter cake and dissolved salt',
    lead: 'What it takes to neutralise spent hydrochloric pickling acid with hydrated lime: the lime a month, the iron hydroxide sludge and filter cake to dispose of, and the calcium chloride left dissolved in the water, which is the load a ZLD plant has to remove.',
    inputs: [
      { k: 'vol', l: 'Spent acid', u: 'm³/month', v: 60, step: 1, min: 0.1 },
      { k: 'fe', l: 'Iron in the spent acid', u: 'g/L', v: 130, step: 5, min: 0, max: 220 },
      { k: 'hcl', l: 'Free acid left', u: '% HCl', v: 3, step: 0.5, min: 0, max: 20, hint: 'from a titration' },
      { k: 'zn', adv: 1, l: 'Zinc, if you strip in the same acid', u: 'g/L', v: 0, step: 5, min: 0, max: 250 },
      { k: 'sg', adv: 1, l: 'Density of the spent acid', u: 'kg/L', v: 1.25, step: 0.01, min: 1, max: 1.6 },
      { k: 'pur', adv: 1, l: 'Lime purity', u: '% Ca(OH)₂', v: 90, step: 1, min: 50, max: 100 },
      { k: 'ex', adv: 1, l: 'Lime excess', u: '%', v: 10, step: 1, min: 0, max: 50 },
      { k: 'cake', adv: 1, l: 'Solids in the filter cake', u: '%', v: 35, step: 1, min: 10, max: 80 },
      { k: 'days', adv: 1, l: 'Working days', u: 'per month', v: 26, step: 1, min: 1, max: 31 }
    ],
    run: function (v) {
      var hcl = v.vol * 1000 * v.sg * v.hcl / 100, fe = v.vol * v.fe, zn = v.vol * v.zn;               // kg a month
      var need = hcl * 1.0161 + fe * 1.3268 + zn * 1.1333;                                                 // kg Ca(OH)₂ that reacts
      if (!(need > 0)) return { warn: ['Enter the iron or the free acid in the spent acid.'] };
      var lime = need * (1 + v.ex / 100) / (v.pur / 100), dry = fe * 1.9136 + zn * 1.5202 + (lime - need), cake = dry / (v.cake / 100);
      var cacl = hcl * 1.5219 + fe * 1.9873 + zn * 1.6975, warn = [];
      if (v.vol > 300) warn.push('At over 300 m³ a month an acid regeneration plant usually suits better than neutralising: it returns hydrochloric acid to the line and turns the iron into iron oxide you can sell.');
      if (v.zn > 0 && v.fe > 0) warn.push('Acid that carries both iron and zinc is hard to regenerate. A separate tank for stripping keeps the pickling acid clean and the zinc recoverable.');
      var rows = [['Iron in the acid', fx(fe / 1000, 2) + ' t / month'], ['Free HCl', fx(hcl / 1000, 2) + ' t / month']];
      if (zn > 0) rows.push(['Zinc in the acid', fx(zn / 1000, 2) + ' t / month']);
      rows = rows.concat([['Pure Ca(OH)₂ that reacts', fx(need / 1000, 2) + ' t / month'], ['Lime per m³ of spent acid', fx(lime / v.vol) + ' kg'], ['Filter cake per m³ of spent acid', fx(cake / v.vol) + ' kg'], ['Oxygen to turn Fe(II) into Fe(III)', fx(fe * 0.1433) + ' kg / month, in theory, from air']]);
      return {
        key: [['Hydrated lime', fx(lime / 1000, 1) + ' t / month', fx(lime / v.days) + ' kg per working day'], ['Filter cake', fx(cake / 1000, 1) + ' t / month', 'at ' + v.cake + ' % solids'],
          ['Dry sludge', fx(dry / 1000, 1) + ' t / month', 'iron hydroxide' + (zn > 0 ? ', zinc hydroxide' : '') + ' and lime residue'], ['Dissolved CaCl₂', fx(cacl / 1000, 1) + ' t / month', '≈ ' + fx(cacl / v.vol) + ' g/L before dilution']],
        rows: rows,
        warn: warn,
        note: '2HCl + Ca(OH)₂ → CaCl₂ + 2H₂O; FeCl₂ + Ca(OH)₂ → Fe(OH)₂ + CaCl₂, and aeration turns Fe(OH)₂ into Fe(OH)₃ (1.91 kg per kg of iron); ZnCl₂ + Ca(OH)₂ → Zn(OH)₂ + CaCl₂. Lime is dosed to about pH 9 in practice, so set the real dose with a jar test. The calcium chloride stays in the water: neutralising, settling and filtering do not remove it; only a ZLD plant (RO, then evaporation) does. SHIVAS Reinplast builds neutralisation and filter press plants, ETP, ZLD and acid regeneration.'
      };
    }
  });

  /* ---------------- 11. FRP pultruded profile: weight and deflection beside steel ---------------- */
  var SHP = { ib: 'I-beam', ch: 'Channel', rt: 'Square or rectangular tube', ct: 'Round tube', ang: 'Equal angle', rod: 'Round rod', flat: 'Flat strip' };
  CALCS.push({
    id: 'frp', div: 'frp', t: 'FRP profile weight and deflection', s: 'kg per metre, steel comparison, beam check',
    lead: 'For a pultruded FRP section: its weight per metre and per piece, what the same section weighs in steel, and how far it bends as a simply supported beam under your load, beside steel of the same size.',
    inputs: [
      { k: 'shp', l: 'Section', type: 'sel', opts: Object.keys(SHP).map(function (k) { return [k, SHP[k]]; }), v: 'ib' },
      { k: 'H', l: 'Height H, or outside Ø', u: 'mm', v: 150, step: 1, min: 3 },
      { k: 'B', l: 'Width B (flange, tube or strip)', u: 'mm', v: 75, step: 1, min: 3 },
      { k: 't', l: 'Wall or web thickness t', u: 'mm', v: 8, step: 0.5, min: 0.5 },
      { k: 'L', l: 'Span, and the piece length', u: 'm', v: 3, step: 0.1, min: 0.1 },
      { k: 'w', l: 'Load spread along the span', u: 'kN/m', v: 1, step: 0.1, min: 0 },
      { k: 'tf', adv: 1, l: 'Flange thickness, I-beam and channel', u: 'mm', v: 0, step: 0.5, min: 0, hint: '0 = same as t', auto: 'same as t' },
      { k: 'rho', adv: 1, l: 'FRP density', u: 'g/cm³', v: 1.9, step: 0.05, min: 1.2, max: 2.4 },
      { k: 'E', adv: 1, l: 'FRP modulus along the length', u: 'GPa', v: 23, step: 0.5, min: 5, max: 60, hint: 'use the value your supplier guarantees' },
      { k: 'G', adv: 1, l: 'FRP shear modulus', u: 'GPa', v: 3, step: 0.1, min: 0.5, max: 10 }
    ],
    run: function (v) {
      var H = v.H, B = v.B, t = v.t, tf = v.tf > 0 ? v.tf : t, s = v.shp, c = H / 2, A, I = 0, Aw = 0, dims, bad = 'Check the sizes: the wall is too thick for this section.';
      if (s === 'ib' || s === 'ch') {
        if (2 * tf >= H || t >= B) return { warn: [bad] };
        A = 2 * B * tf + (H - 2 * tf) * t; I = (B * Math.pow(H, 3) - (B - t) * Math.pow(H - 2 * tf, 3)) / 12; Aw = H * t; dims = H + ' × ' + B + ' × ' + t + (tf !== t ? ' / ' + tf : '');
      } else if (s === 'rt') {
        if (2 * t >= H || 2 * t >= B) return { warn: [bad] };
        A = H * B - (H - 2 * t) * (B - 2 * t); I = (B * Math.pow(H, 3) - (B - 2 * t) * Math.pow(H - 2 * t, 3)) / 12; Aw = 2 * H * t; dims = H + ' × ' + B + ' × ' + t;
      } else if (s === 'ct') {
        if (2 * t >= H) return { warn: [bad] };
        var di = H - 2 * t; A = Math.PI / 4 * (H * H - di * di); I = Math.PI / 64 * (Math.pow(H, 4) - Math.pow(di, 4)); Aw = A / 2; dims = 'Ø' + H + ' × ' + t;
      } else if (s === 'rod') {
        A = Math.PI / 4 * H * H; I = Math.PI / 64 * Math.pow(H, 4); Aw = 0.9 * A; dims = 'Ø' + H;
      } else if (s === 'flat') {
        A = B * t; I = B * Math.pow(t, 3) / 12; Aw = A * 5 / 6; c = t / 2; dims = B + ' × ' + t;
      } else {
        if (t >= H) return { warn: [bad] };
        A = t * (2 * H - t); dims = H + ' × ' + H + ' × ' + t;
      }
      var kgm = A * v.rho / 1000, st = A * 7.85 / 1000, Lm = v.L * 1000, warn = [];
      var key = [['FRP weight', fx(kgm, 2) + ' kg/m', fx(kgm * v.L, 1) + ' kg per ' + v.L + ' m piece'], ['Same section in steel', fx(st, 2) + ' kg/m', 'FRP is ' + fx((1 - kgm / st) * 100) + ' % lighter']];
      var rows = [['Section', SHP[s] + ', ' + dims + ' mm'], ['Area', fx(A) + ' mm²'], ['Pieces per tonne', fx(1000 / (kgm * v.L)) + ' of ' + v.L + ' m']];
      if (I > 0) {
        var wF = v.w + kgm * 9.81 / 1000, wS = v.w + st * 9.81 / 1000, E = v.E * 1000, G = v.G * 1000;    // N/mm, N/mm²
        var bF = 5 * wF * Math.pow(Lm, 4) / (384 * E * I), sF = wF * Lm * Lm / (8 * Aw * G), dF = bF + sF;
        var dS = 5 * wS * Math.pow(Lm, 4) / (384 * 200000 * I) + wS * Lm * Lm / (8 * Aw * 77000);
        var sig = wF * Lm * Lm / 8 * c / I, ratio = function (d) { var r = Lm / d; return 'span ÷ ' + fx(r, r < 10 ? 1 : 0); };
        key.push(['Deflection, FRP', fx(dF, 1) + ' mm', ratio(dF)], ['Deflection, steel', fx(dS, 2) + ' mm', ratio(dS)]);
        if (Lm / dF < 50) warn.push('This section is far too small for this load and span, and simple beam sums no longer describe it. Choose a deeper section or a shorter span.');
        else if (sig > 100) warn.push('The bending stress in the FRP (' + fx(sig) + ' MPa) is high for a pultruded profile. Check it against the allowable stress your supplier guarantees, with its safety factor.');
        rows = rows.concat([['Second moment of area', fx(I / 1e4, 1) + ' cm⁴'], ['Bending stress at mid-span', fx(sig, 1) + ' MPa in FRP'], ['Shear part of the FRP deflection', fx(sF / dF * 100) + ' %'], ['FRP bends', fx(dF / dS, 1) + ' times as much as steel'], ['Load used', fx(v.w, 2) + ' kN/m plus self-weight ' + fx(kgm * 9.81 / 1000, 3) + ' kN/m']]);
      } else {
        key.push(['Deflection', 'n/a', 'not worked out for angles']);
        warn.push('An angle bends about an inclined axis, so its deflection is not worked out here. Ask SHIVAS to check the span.');
      }
      return {
        key: key, rows: rows, warn: warn,
        note: 'Section properties for sharp corners, about the strong axis. Deflection = bending (5wL⁴ ÷ 384EI) plus shear (wL² ÷ 8A<sub>w</sub>G); the shear part matters in FRP because its shear modulus is low. Steel at 200 GPa and 77 GPa. FRP is usually sized for deflection before strength: use the modulus and allowable stresses your supplier guarantees for the profile. SHIVAS Products India pultrudes FRP profiles and can check your section and span.'
      };
    }
  });

  /* ---------------- 12. ETP + ZLD: neutralisation, sludge, RO, MEE or MVR, crystallizer, ATFD ---------------- */
  var NEUT = { lime: 'Hydrated lime', naoh: 'Caustic soda', soda: 'Lime, then soda ash' };
  var TRAIN = { mee: 'MEE, then ATFD', meec: 'MEE with crystallizer, then ATFD', mvr: 'MVR, then ATFD', mvrc: 'MVR with crystallizer, then ATFD', atfd: 'No evaporator: ATFD takes the RO reject' };
  var ECON = { 3: 2.5, 4: 3.2, 5: 3.9 };   // typical kg of water evaporated per kg of steam for 3, 4 and 5 effects
  function zldSvg(top, bot) {   // two rows of boxes: top left to right, bottom right to left, joined at the right end
    var W = 140, H = 66, G = 22, X = function (i) { return 10 + i * (W + G); }, y1 = 22, y2 = 196, s = '';
    var box = function (x, y, b) {
      return '<g class="' + (b.c || '') + '"><rect x="' + x + '" y="' + y + '" width="' + W + '" height="' + H + '" rx="9"/>' +
        '<text x="' + (x + 10) + '" y="' + (y + 22) + '" class="t">' + b.t + '</text>' +
        '<text x="' + (x + 10) + '" y="' + (y + 41) + '" class="v">' + b.s + '</text>' + (b.s2 ? '<text x="' + (x + 10) + '" y="' + (y + 57) + '" class="v">' + b.s2 + '</text>' : '') + '</g>' +
        (b.o ? '<path class="ar ' + (b.oc || '') + '" d="M' + (x + W / 2) + ' ' + (y + H) + 'v20"/><text x="' + (x + W / 2) + '" y="' + (y + H + 34) + '" class="o ' + (b.oc || '') + '" text-anchor="middle">' + b.o + '</text>' : '');
    };
    top.forEach(function (b, i) { s += box(X(i), y1, b); if (i) s += '<path class="ar" d="M' + (X(i) - G + 2) + ' ' + (y1 + H / 2) + 'h' + (G - 6) + '"/>'; });
    var r = top.length - 1;
    s += '<path class="ar" d="M' + (X(r) + W / 2) + ' ' + (y1 + H + 44) + 'V' + (y2 - 4) + '"/>';
    bot.forEach(function (b, i) { var x = X(r - i); s += box(x, y2, b); if (i) s += '<path class="ar" d="M' + (x + W + G - 2) + ' ' + (y2 + H / 2) + 'h-' + (G - 6) + '"/>'; });
    return '<svg viewBox="0 0 ' + (X(r) + W + 10) + ' ' + (y2 + H + 44) + '" role="img" aria-label="Process flow of the ETP and ZLD plant, with the flows worked out above">' +
      '<defs>' + ['', 'w', 's'].map(function (k) { return '<marker id="zar' + k + '" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto"><path class="mk' + k + '" d="M0 0L8 4L0 8z"/></marker>'; }).join('') + '</defs>' + s + '</svg>';
  }
  CALCS.push({
    id: 'zld', div: 'rein', t: 'ETP and ZLD plant', s: 'Neutraliser, sludge, RO, MEE or MVR, ATFD, steam and power',
    lead: 'Size the whole effluent plant for a pickling, galvanizing or wire shop, from the acidic effluent to dry salt: the neutraliser and the filter cake, the tanks and clarifier, how much water reverse osmosis gives back, the evaporator (multiple-effect or MVR) with its steam or power, the crystallizer if you want one, and the agitated thin film dryer (ATFD) that turns the last brine into dry salt.',
    inputs: [
      { k: 'q', l: 'Dilute effluent: rinses, scrubber bleed, floor wash', u: 'm³/day', v: 88, step: 1, min: 0 },
      { k: 'hq', l: 'Free acid in it', u: 'g/L HCl', v: 1.5, step: 0.1, min: 0, max: 50, hint: 'from a composite sample' },
      { k: 'fq', l: 'Iron in it', u: 'g/L', v: 0.8, step: 0.1, min: 0, max: 50 },
      { k: 'sa', l: 'Spent acid neutralised in the ETP', u: 'm³/day', v: 2, step: 0.1, min: 0, hint: '0 if it is regenerated or sold' },
      { k: 'neut', l: 'Neutraliser', type: 'sel', opts: Object.keys(NEUT).map(function (k) { return [k, NEUT[k]]; }), v: 'lime' },
      { k: 'train', l: 'Evaporation and drying', type: 'sel', opts: Object.keys(TRAIN).map(function (k) { return [k, TRAIN[k]]; }), v: 'mee' },
      { k: 'nef', l: 'Effects in the MEE', type: 'sel', opts: [['3', '3 effects'], ['4', '4 effects'], ['5', '5 effects']], v: '4' },
      { k: 'safe', adv: 1, l: 'Iron in the spent acid', u: 'g/L', v: 130, step: 5, min: 0, max: 220 },
      { k: 'sahcl', adv: 1, l: 'Free acid in the spent acid', u: '% HCl', v: 3, step: 0.5, min: 0, max: 20 },
      { k: 'sasg', adv: 1, l: 'Density of the spent acid', u: 'kg/L', v: 1.25, step: 0.01, min: 1, max: 1.6 },
      { k: 'zn', adv: 1, l: 'Zinc in the spent acid', u: 'g/L', v: 0, step: 5, min: 0, max: 250 },
      { k: 'tds0', adv: 1, l: 'Other dissolved salts in the dilute effluent', u: 'mg/L', v: 1500, step: 100, min: 0 },
      { k: 'hrs', adv: 1, l: 'ETP running hours', u: 'h/day', v: 20, step: 1, min: 4, max: 24 },
      { k: 'pur', adv: 1, l: 'Lime purity', u: '% Ca(OH)₂', v: 90, step: 1, min: 50, max: 100 },
      { k: 'ex', adv: 1, l: 'Reagent excess', u: '%', v: 10, step: 1, min: 0, max: 50 },
      { k: 'cake', adv: 1, l: 'Solids in the filter cake', u: '%', v: 35, step: 1, min: 15, max: 70 },
      { k: 'eqh', adv: 1, l: 'Equalisation, hours of average flow', u: 'h', v: 12, step: 1, min: 2, max: 48 },
      { k: 'sor', adv: 1, l: 'Clarifier surface loading', u: 'm³/m²·h', v: 1, step: 0.1, min: 0.3, max: 3 },
      { k: 'ote', adv: 1, l: 'Oxygen transfer of the aeration', u: '%', v: 10, step: 1, min: 3, max: 40, hint: 'coarse bubble, shallow tank ≈ 5 to 10' },
      { k: 'rorec', adv: 1, l: 'RO recovery wanted', u: '%', v: 75, step: 1, min: 0, max: 95 },
      { k: 'rotds', adv: 1, l: 'Highest salt in the RO reject', u: 'mg/L', v: 60000, step: 1000, min: 10000, max: 90000, hint: 'sets the highest recovery' },
      { k: 'rorej', adv: 1, l: 'RO salt rejection', u: '%', v: 98, step: 0.5, min: 80, max: 99.8 },
      { k: 'econ', adv: 1, l: 'MEE steam economy, if your supplier gives one', u: 'kg/kg', v: 0, step: 0.1, min: 0, max: 8, hint: '0 = typical for the effects', auto: 'typical for the effects' },
      { k: 'mvrk', adv: 1, l: 'MVR power per m³ evaporated', u: 'kWh', v: 30, step: 1, min: 8, max: 80, hint: 'typically about 20 to 50' },
      { k: 'evx', adv: 1, l: 'Solids in the evaporator concentrate', u: '%', v: 0, step: 1, min: 0, max: 70, hint: '0 = near saturation for the salt', auto: 'near saturation' },
      { k: 'cry', adv: 1, l: 'Salt the crystallizer takes out', u: '%', v: 85, step: 1, min: 0, max: 98, hint: 'of the salt it can crystallize' },
      { k: 'adry', adv: 1, l: 'Dryness of the ATFD product', u: '% solids', v: 95, step: 1, min: 70, max: 99 },
      { k: 'asteam', adv: 1, l: 'ATFD steam per kg of water', u: 'kg/kg', v: 1.25, step: 0.05, min: 1, max: 2 },
      { k: 'zh', adv: 1, l: 'Evaporator and ATFD running hours', u: 'h/day', v: 24, step: 1, min: 8, max: 24 },
      { k: 'ps', adv: 1, l: 'Steam price (yours)', u: '₹/t', v: 2500, step: 100, min: 0 },
      { k: 'pe', adv: 1, l: 'Power price (yours)', u: '₹/kWh', v: 8, step: 0.5, min: 0 }
    ],
    run: function (v) {
      var Fin = v.q + v.sa, warn = [], n = +v.nef || 4;
      if (!(Fin > 0)) return { warn: ['Enter the effluent flow.'] };
      /* acid load, kg a day */
      var hcl = v.q * v.hq + v.sa * 1000 * v.sasg * v.sahcl / 100, fe = v.q * v.fq + v.sa * v.safe, zn = v.sa * v.zn;
      var eq = hcl / 36.461 + 2 * fe / 55.845 + 2 * zn / 65.38;                                   // kmol of acid to neutralise (chloride equivalents)
      /* neutraliser, salt left in the water, sludge, reagent water */
      var X = 1 + v.ex / 100, caoh = eq / 2 * 74.093, lime = 0, naoh = 0, soda = 0, salt, saltN, resid = 0, caco3 = 0, rw = 0, extraDS = 0;
      if (v.neut === 'naoh') { naoh = eq * 39.997 * X; salt = eq * 58.443; saltN = 'sodium chloride'; extraDS = eq * 39.997 * (X - 1); rw = naoh * 0.52 / 0.48; }
      else {
        lime = caoh * X / (v.pur / 100); resid = lime - caoh; rw = lime * 9;                      // dosed as a 10 % slurry
        if (v.neut === 'soda') { soda = eq / 2 * 105.988 * X; caco3 = eq / 2 * 100.087; salt = eq * 58.443; saltN = 'sodium chloride'; extraDS = eq / 2 * 105.988 * (X - 1); rw += soda * 9; }
        else { salt = eq / 2 * 110.98; saltN = 'calcium chloride'; }
      }
      var dry = fe * 1.9136 + zn * 1.5202 + resid + caco3, cake = dry / (v.cake / 100), cakeW = cake - dry;
      var Wtot = Fin + rw / 1000, Ft = Wtot - cakeW / 1000, bg = v.q * v.tds0 / 1000, DS = salt + bg + extraDS, tdsF = DS / Ft * 1000;   // m³/day, kg/day, mg/L
      /* reverse osmosis */
      var r = 0, tdsP = 0, tdsR = tdsF, P = 0, roKwh = 0;
      if (v.rorec > 0 && tdsF < 0.9 * v.rotds) {
        r = Math.min(v.rorec / 100, 1 - tdsF / v.rotds);
        if (r < 0.2) r = 0;
      }
      if (r > 0) {
        var avg = tdsF * Math.log(1 / (1 - r)) / r; tdsP = (1 - v.rorej / 100) * avg; tdsR = (tdsF - r * tdsP) / (1 - r);
        P = Math.max(8, 0.78 * tdsR / 1000 + 5); roKwh = Ft * P * 0.037;
      } else warn.push('The treated water carries ' + fx(tdsF) + ' mg/L of salt, too much for reverse osmosis at the reject limit you set, so all of it goes to the evaporator. Less spent acid in the ETP, or acid regeneration, changes that.');
      var perm = r * Ft, Qe = Ft - perm, Se = DS - perm * tdsP / 1000, We = Qe * (1000 - 0.3 * tdsR / 1000);   // evaporator feed: m³, kg solids, kg water a day
      /* evaporator, crystallizer, ATFD */
      var hasEv = v.train !== 'atfd', hasCr = v.train === 'meec' || v.train === 'mvrc', mvr = v.train === 'mvr' || v.train === 'mvrc';
      var evx = v.evx > 0 ? v.evx : (saltN === 'calcium chloride' ? 40 : 26);
      var cryst = 0, crW = 0;
      if (hasCr) { cryst = (saltN === 'sodium chloride' ? salt + bg : bg) * v.cry / 100; crW = cryst * 5 / 95; }
      var Sml = Se - cryst, Mml = Sml / (evx / 100), Wml = Mml - Sml, Ev = 0;
      if (hasEv) { Ev = We - Wml - crW; if (Ev < 0) { Ev = 0; Wml = We; } } else Wml = We;
      Mml = Sml + Wml;                                                                    // brine the ATFD receives
      var prod = Sml / (v.adry / 100), Ea = Math.max(0, Wml - (prod - Sml));
      var econ = v.econ > 0 ? v.econ : ECON[n], stEv = hasEv && !mvr ? Ev / econ : 0, kwEv = hasEv && mvr ? Ev / 1000 * v.mvrk : 0, stA = Ea * v.asteam;
      var steam = (stEv + stA) / 1000, power = kwEv + roKwh, cost = steam * v.ps + power * v.pe;
      var cool = ((hasEv && !mvr ? Ev / n : 0) + Ea) * 2350 / (v.zh * 3600);        // kW to the cooling tower from the last effect and the ATFD condenser
      var rec = perm + Ev / 1000 + Ea / 1000, recP = rec / Wtot * 100;
      /* ETP sizes */
      var qh = Fin / v.hrs, eqV = Fin / 24 * v.eqh, cA = qh / v.sor, cD = Math.sqrt(4 * cA / Math.PI);
      var air = fe * 0.14325 / (0.232 * 1.293) / (v.ote / 100) / v.hrs, press = cake / 1300 / 2 * 1000;
      if (tdsF > 0 && r > 0 && fe > 0) warn.push('Iron fouls RO membranes: the clarified water must be filtered (sand, then carbon or cartridge) and the iron kept very low before the RO.');
      if (mvr && saltN === 'calcium chloride' && evx > 30) warn.push('Calcium chloride raises the boiling point steeply as it concentrates, which an MVR fan or compressor cannot follow far. With lime, an MVR usually takes the brine part of the way, and steam-heated effects or the ATFD finish it.');
      if (hasCr && saltN === 'calcium chloride') warn.push('With lime the salt is calcium chloride. It stays dissolved to very high strength, so a crystallizer takes out only the other salts and most of the solids still go to the ATFD. Caustic soda, or lime followed by soda ash, gives sodium chloride, which crystallizes.');
      if (saltN === 'calcium chloride') warn.push('The dry product is mainly calcium chloride, which draws moisture from the air. Bag it hot in lined bags and store it dry.');
      if (hasEv && Ev / 1000 < 3 && v.train !== 'atfd') warn.push('Less than 3 m³ a day reaches the evaporator. At this size an ATFD alone, without an evaporator, is often the simpler plant.');
      var NL = v.neut === 'naoh' ? 'Caustic soda' : v.neut === 'soda' ? 'Lime + soda ash' : 'Hydrated lime';
      var dose = v.neut === 'naoh' ? naoh : lime + soda;
      var evName = !hasEv ? 'No evaporator' : mvr ? 'MVR' : n + '-effect MEE';
      var rows = [['Acid load', fx(hcl) + ' kg HCl, ' + fx(fe) + ' kg iron' + (zn > 0 ? ', ' + fx(zn) + ' kg zinc' : '') + ' a day'],
        [v.neut === 'naoh' ? 'Caustic soda' : 'Hydrated lime', v.neut === 'naoh' ? fx(naoh) + ' kg/day (100 %), about ' + fx(naoh / 0.48 / 1.51) + ' L of 48 % lye' : fx(lime) + ' kg/day, ' + fx(lime * 10 / 1000, 1) + ' m³ of 10 % slurry'],
      ].concat(soda ? [['Soda ash', fx(soda) + ' kg/day, swaps the calcium for sodium']] : []).concat([
        ['Equalisation tank', fx(eqV) + ' m³'], ['Neutralisation tanks', '2 × ' + fx(qh * 0.5, 1) + ' m³ (30 minutes each)'], ['Oxidation tank and air', fx(qh, 1) + ' m³, about ' + fx(air) + ' Nm³/h of air'],
        ['Clarifier', fx(cA, 1) + ' m², Ø ' + fx(cD, 1) + ' m'], ['Filter press', fx(cake / 1300, 2) + ' m³ of cake a day, about ' + fx(press) + ' L of chambers at two cycles'],
        ['Salt left in the treated water', fx(DS) + ' kg/day, ' + fx(tdsF) + ' mg/L, mainly ' + saltN],
        ['RO', r > 0 ? fx(r * 100) + ' % recovery, reject ' + fx(tdsR) + ' mg/L, feed ≈ ' + fx(P) + ' bar, ' + fx(roKwh) + ' kWh/day' : 'bypassed'],
        ['Evaporator', hasEv ? evName + ', ' + fx(Ev / v.zh) + ' kg/h of water' + (mvr ? ', ' + fx(kwEv) + ' kWh/day' : ', steam ' + fx(stEv / 1000, 2) + ' t/day at economy ' + fx(econ, 1)) : 'none']]).concat(hasCr ? [['Crystallizer and centrifuge', fx(cryst / 1000, 2) + ' t/day of salt crystals']] : []).concat([
        ['ATFD', fx(Wml / v.zh) + ' kg/h of water in, ' + fx(Ea / v.zh) + ' kg/h evaporated, steam ' + fx(stA / 1000, 2) + ' t/day'],
        ['Cooling tower load', fx(cool) + ' kW (' + (mvr || !hasEv ? 'ATFD condenser' : 'last effect and ATFD condenser') + ')'],
        ['Energy cost', '₹' + fx(cost) + ' a day, ₹' + fx(cost / Fin) + ' per m³ of effluent']]);
      var trows = [['Dilute effluent', fx(v.q, 1), fx(v.hq, 1) + ' g/L HCl, ' + fx(v.fq, 1) + ' g/L Fe', 'Equalisation'], ['Spent acid', fx(v.sa, 1), fx(v.safe) + ' g/L Fe', 'Neutralisation'],
        ['Reagent water', fx(rw / 1000, 1), NL, 'Neutralisation'], ['Filter cake', fx(cake / 1000, 2) + ' t', v.cake + ' % solids', 'Disposal'], ['Treated water', fx(Ft, 1), fx(tdsF) + ' mg/L', r > 0 ? 'RO' : hasEv ? 'Evaporator' : 'ATFD']
      ].concat(r > 0 ? [['RO permeate', fx(perm, 1), fx(tdsP) + ' mg/L', 'Reuse'], ['RO reject', fx(Qe, 1), fx(tdsR) + ' mg/L', hasEv ? 'Evaporator' : 'ATFD']] : [])
        .concat(hasEv ? [['Evaporator condensate', fx(Ev / 1000, 1), 'low salt', 'Reuse']] : []).concat(hasCr ? [['Salt crystals', fx(cryst / 1000, 2) + ' t', '95 % solids', 'Bagging']] : [])
        .concat([['Brine to the ATFD', fx(Mml / 1000, 2) + ' t', fx(Sml / Mml * 100) + ' % solids', 'ATFD'], ['ATFD condensate', fx(Ea / 1000, 2), 'low salt', 'Reuse'], ['Dry salt', fx(prod / 1000, 2) + ' t', v.adry + ' % solids', 'Bagging']]);
      var top = [{ t: 'Effluent', s: fx(Fin) + ' m³/day', s2: fx(hcl) + ' kg HCl/day' }, { t: 'Equalisation', s: fx(eqV) + ' m³' },
        { t: 'Neutralise, aerate', s: NL.toLowerCase(), s2: fx(dose) + ' kg/day' }, { t: 'Clarifier', s: 'Ø ' + fx(cD, 1) + ' m', o: 'cake ' + fx(cake / 1000, 1) + ' t/day', oc: 's' },
        { t: 'Filters', s: 'sand, carbon', s2: fx(Ft, 1) + ' m³/day' }, { t: 'RO', s: r > 0 ? fx(r * 100) + ' % recovery' : 'bypassed', s2: r > 0 ? fx(P) + ' bar' : '', o: r > 0 ? fx(perm, 1) + ' m³/day water' : '', oc: 'w', c: r > 0 ? '' : 'off' }];
      var bot = [{ t: hasEv ? evName : 'Evaporator', s: hasEv ? fx(Ev / 1000, 1) + ' m³/day off' : 'not used', s2: hasEv ? (mvr ? fx(kwEv) + ' kWh/day' : fx(stEv / 1000, 1) + ' t steam/day') : '', o: hasEv ? 'condensate to reuse' : '', oc: 'w', c: hasEv ? '' : 'off' }]
        .concat(hasCr ? [{ t: 'Crystallizer', s: 'and centrifuge', s2: fx(cryst / 1000, 2) + ' t/day salt', o: 'crystals', oc: 's' }] : [])
        .concat([{ t: 'ATFD', s: fx(Ea / 1000, 1) + ' m³/day off', s2: fx(stA / 1000, 1) + ' t steam/day', o: 'condensate to reuse', oc: 'w' }, { t: 'Dry salt', s: fx(prod / 1000, 2) + ' t/day', s2: saltN, c: 'sl' }]);
      return {
        key: [['ETP design flow', fx(qh, 1) + ' m³/h', fx(Fin) + ' m³/day in ' + v.hrs + ' h'], [NL, fx(dose) + ' kg/day', 'filter cake ' + fx(cake / 1000, 1) + ' t/day'],
          ['RO water back', r > 0 ? fx(perm, 1) + ' m³/day' : 'bypassed', r > 0 ? fx(r * 100) + ' % recovery' : 'feed too salty for RO'], ['Evaporator', hasEv ? fx(Ev / 1000, 1) + ' m³/day' : 'none', hasEv ? evName + (mvr ? ', ' + fx(kwEv) + ' kWh/day' : ', ' + fx(stEv / 1000, 1) + ' t steam/day') : 'ATFD only'],
          ['ATFD dry salt', fx(prod / 1000, 2) + ' t/day', 'steam ' + fx(stA / 1000, 1) + ' t/day'], ['Water recovered', fx(recP, 1) + ' %', fx(rec, 1) + ' m³/day for reuse']],
        rows: rows,
        table: { title: 'Stream table', head: ['Stream', 'm³ or t a day', 'Strength', 'Goes to'], rows: trows },
        svg: zldSvg(top, bot),
        warn: warn,
        note: 'Neutraliser from the chloride the acid carries: 1.02 kg of lime per kg of HCl and 1.33 kg per kg of iron, or 1.10 and 1.43 kg of caustic soda; aeration turns the iron into Fe(OH)₃. RO recovery is the lower of what you ask and what keeps the reject under your limit; feed pressure is estimated from the reject strength. Evaporation uses typical steam economies of 2.5, 3.2 and 3.9 for 3, 4 and 5 effects, or the MVR power you set, and the ATFD dries the last brine to a powder. ETP pumps, agitators and blowers are not included. A first sizing for budgets and layouts: SHIVAS Reinplast confirms it on your effluent analysis, with jar and pilot tests.'
      };
    }
  });

  /* Most used and most important first; the plant calculator (its own page) leads the list */
  var ORDER = ['wire', 'burner', 'zld', 'coating', 'wireweight', 'scrubber', 'acid', 'neutralise', 'bagfilter', 'fan', 'rectifier', 'frp'];
  CALCS.sort(function (a, b) { return ORDER.indexOf(a.id) - ORDER.indexOf(b.id); });

  window.SHIVAS_CALCS = CALCS;

  /* ---------------- UI ----------------
     One panel, three ways to show it:
     1. calculators.html: <div class="cx" id="calcs"> with .cx-nav and .cx-pane. Every calculator, picked from the
        list; the address carries #id and the page colour follows the calculator's company.
     2. A division page: <div class="cx cx-app" data-calcs="wire,wireweight" data-h="3"> (data-ext="1" puts the
        plant calculator first). The same list with only these; the address does not change.
     3. One calculator: <div class="cx-one" data-calc="zld" data-h="3"> on a product page, or data-h="0" on the
        calculator's own page, calculators/<PAGE[id]>.html, where the page carries the title. data-div="hdg|wire|rein"
        names the company for the label and the enquiry when the page belongs to another one.
     Pages that do not load this file themselves get it from site.js when a calculator comes near the screen.
     Links in the calculators are written from the site root; rel() makes them work from any folder. */
  var PAGE = { wire: 'wire-drawing', burner: 'burner-kw', zld: 'etp-zld', coating: 'coating-thickness', wireweight: 'wire-weight', scrubber: 'fume-scrubber', acid: 'pickling-acid', neutralise: 'acid-neutralisation', bagfilter: 'bag-filter', fan: 'fan-motor', rectifier: 'eg-rectifier', frp: 'frp-profile' };
  window.SHIVAS_CALC_PAGES = PAGE;
  var DIVN = { hdg: 'Galvanizing', wire: 'Wire', rein: 'Reinplast', frp: 'FRP profiles' }, DCL = { frp: 'hdg' };
  var ME = document.currentScript || document.querySelector('script[src*="calcs.js"]');
  var BASE = ME ? (ME.getAttribute('src') || '').replace(/assets\/calcs\.js(\?.*)?$/, '') : '';
  if (/calcs\.js/.test(BASE)) BASE = '';
  var rel = function (h) { return BASE ? String(h).replace(/href="(?![a-z]+:|#|\/|\.\.\/)/g, 'href="' + BASE) : h; };
  var pageOf = function (id) { return BASE + 'calculators/' + PAGE[id] + '.html'; };
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
  var MOUNTS = [], N = 0;
  function setMG(m) { MG = m; try { localStorage.setItem('shivas.mg', String(MG)); } catch (e) {} MOUNTS.forEach(function (x) { x.mg(); }); }

  function mount(root, ids, opt) {
    var list = CALCS.filter(function (c) { return ids.indexOf(c.id) >= 0; }); if (!list.length) return;
    var P = opt.hub ? 'cx' : 'cx' + (++N), H = opt.h, nav = $('.cx-nav', root), pane = $('.cx-pane', root), cur = null, div = '', st = {}, lastSum = '', timer = 0;
    if (!pane) {   // replaces the placeholder the page carries until the script runs
      root.innerHTML = (opt.one ? '' : '<nav class="cx-nav" aria-label="' + (opt.label || 'Calculators') + '"></nav>') + '<div class="cx-pane"></div>';
      nav = $('.cx-nav', root); pane = $('.cx-pane', root);
    }
    root.classList.add('cx-on');
    if (nav) {
      nav.innerHTML = rel((opt.ext ? '<a href="calculator.html" class="d-hdg ext"><small>Galvanizing</small><b>Plant size and running cost</b><span>Full plant planner, cost per tonne ↗</span></a>' : '') +
        list.map(function (c) { return '<a href="' + (opt.hub ? '#' + c.id : pageOf(c.id)) + '" data-id="' + c.id + '" class="d-' + (DCL[c.div] || c.div) + '"><small>' + DIVN[c.div] + '</small><b>' + c.t + '</b><span>' + c.s + '</span></a>'; }).join(''));
      nav.addEventListener('click', function (e) { var a = e.target.closest('a[data-id]'); if (!a) return; e.preventDefault(); open(a.getAttribute('data-id'), true); if (innerWidth < 900) pane.scrollIntoView({ behavior: 'smooth', block: 'start' }); });
    }
    function field(c, f) {
      var val = st[c.id][f.k], id = P + '-' + c.id + '-' + f.k;
      if (f.type === 'sel') return '<label class="fld fsel" for="' + id + '"><span>' + f.l + '</span><select id="' + id + '" data-k="' + f.k + '">' + f.opts.map(function (o) { return '<option value="' + o[0] + '"' + (o[0] === val ? ' selected' : '') + '>' + o[1] + '</option>'; }).join('') + '</select></label>';
      return '<label class="fld" for="' + id + '"><span>' + f.l + (f.hint ? ' <em>' + f.hint + '</em>' : '') + '</span><span class="u"><input id="' + id + '" type="number" inputmode="decimal" step="' + (f.step || 'any') + '"' + (f.min != null ? ' min="' + f.min + '"' : '') + (f.max != null ? ' max="' + f.max + '"' : '') + ' value="' + val + '" data-k="' + f.k + '">' + (f.u || '') + '</span></label>';
    }
    function open(id, push) {
      var c = list.filter(function (x) { return x.id === id; })[0] || list[0]; cur = c; div = opt.div || c.div;
      if (!st[c.id]) { st[c.id] = {}; c.inputs.forEach(function (f) { st[c.id][f.k] = f.v; }); }
      var nAdv = c.inputs.filter(function (f) { return f.adv; }).length, adv = P + 'Adv';
      if (nav) {
        [].forEach.call(nav.children, function (a) { a.setAttribute('aria-current', String(a.getAttribute('data-id') === c.id)); });
        var ca = nav.querySelector('[aria-current="true"]'); if (ca && nav.scrollWidth > nav.clientWidth + 4) { if (push) nav.scrollTo({ left: ca.offsetLeft - 16, behavior: 'smooth' }); else nav.scrollLeft = ca.offsetLeft - 16; }   // no smooth scroll on page load: it would end the browser's largest-paint measurement
      }
      if (opt.hub) document.documentElement.setAttribute('data-brand', c.div === 'rein' ? 'rein' : 'tech');
      pane.innerHTML = rel((H ? '<div class="cx-h"><span class="k">' + DIVN[div] + ' · calculator</span><h' + H + '>' + c.t + '</h' + H + '><p>' + c.lead + '</p>' +
          '<p class="cx-own"><a href="' + pageOf(c.id) + '">' + (opt.hub ? 'This calculator on its own page' : 'Open it on its own page') + ' →</a></p></div>' : '') +
        '<div class="cx-grid"><form class="cx-in" onsubmit="return false">' + (c.mg ? '<div class="cx-mg" role="group" aria-label="Extra margin on the selected size"><span class="cx-mg-l" title="Added to the calculated need before the next standard size is chosen. None gives the exact need.">Extra margin</span><div class="seg">' + [0, 10, 20, 30].map(function (m) { return '<button type="button" data-mg="' + m + '" aria-pressed="' + (m === MG) + '">' + (m ? '+' + m + ' %' : 'None') + '</button>'; }).join('') + '</div></div>' : '') + c.inputs.filter(function (f) { return !f.adv; }).map(function (f) { return field(c, f); }).join('') +
        (nAdv ? '<button type="button" class="cx-adv-t" aria-expanded="' + !!st[c.id]._adv + '" aria-controls="' + adv + '"><span><b>Advanced</b> · ' + nAdv + ' more inputs for a closer answer</span><em aria-hidden="true">↓</em></button>' +
          '<p class="cx-assume"' + (st[c.id]._adv ? ' hidden' : '') + '></p>' +
          '<div class="cx-adv" id="' + adv + '"' + (st[c.id]._adv ? '' : ' hidden') + '>' + c.inputs.filter(function (f) { return f.adv; }).map(function (f) { return field(c, f); }).join('') + '</div>' : '') +
        '<button type="button" class="btn line sm cx-reset">Reset to typical values</button></form>' +
        '<div class="cx-out"><div class="cx-res" aria-live="polite"></div>' + ASK + '</div></div><div class="cx-wide"></div>');
      $('.cx-in', pane).addEventListener('input', change); $('.cx-in', pane).addEventListener('change', change);
      [].forEach.call(pane.querySelectorAll('[data-mg]'), function (b) { b.addEventListener('click', function () { setMG(+b.getAttribute('data-mg')); }); });
      $('.cx-reset', pane).addEventListener('click', function () { var a = st[c.id]._adv; delete st[c.id]; open(c.id); if (a) toggleAdv(true); });
      var at = $('.cx-adv-t', pane); if (at) at.addEventListener('click', function () { toggleAdv(at.getAttribute('aria-expanded') !== 'true'); });
      askInit();
      calc();
      if (push && opt.hub) { try { history.replaceState(null, '', '#' + c.id); } catch (e) {} }
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
        return '<i>' + f.l.replace(/ \(.*\)$/, '').replace(/, if (you already have one|you know it|your supplier gives one)$/, '') + ' ' + (auto ? (f.auto || (f.k === 'nb' ? 'auto' : 'from the article')) : v) + (f.u && f.type !== 'sel' && !auto ? ' ' + f.u : '') + '</i>';
      }).join(' ');
    }
    function askInit() {
      var t = $('.cx-ask-t', pane), f = $('.cx-ask-f', pane), ok = $('.cx-ask-ok', pane);
      t.addEventListener('click', function () { var o = f.hidden; f.hidden = !o; t.setAttribute('aria-expanded', String(o)); if (o) f.querySelector('input').focus(); });
      $('.cx-ask-mail', f).addEventListener('click', function (e) {
        var ALL = ['info@shivastechnology.com', 'shivastechnology@gmail.com', 'info@shivasasia.com', 'shivasasia@gmail.com', 'shivas1470@gmail.com'], to = div === 'rein' ? 'info@shivasasia.com' : 'info@shivastechnology.com', cc = ALL.filter(function (x) { return x !== to; }).join(',');
        this.href = 'mailto:' + to + '?cc=' + cc + '&subject=' + encodeURIComponent('Calculator: ' + cur.t) + '&body=' + encodeURIComponent(who() + '\n\n' + lastSum + '\n\nPlease check this and send a proposal.');
      });
      function who() { var d = new FormData(f); return ['Name: ' + d.get('name'), 'Company: ' + d.get('company'), 'Phone: ' + d.get('phone'), 'Email: ' + d.get('email')].join('\n'); }
      f.addEventListener('submit', function (e) {
        e.preventDefault(); var d = new FormData(f), name = (d.get('name') || '').trim(), phone = (d.get('phone') || '').trim();
        $('.cx-ask-e', f).hidden = !!(name && phone); if (!name || !phone) return;
        var T = window.SHIVAS_TRACK, sent = T && T.lead({ source: 'Calculator · ' + cur.t, div: div, name: name, company: (d.get('company') || '').trim(), contact: phone, email: (d.get('email') || '').trim(), product: cur.t, message: lastSum });
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
      clearTimeout(timer); timer = setTimeout(function () { var T = window.SHIVAS_TRACK; if (T) T.event('calc', { calc: cur.t, detail: lastSum.slice(0, 900) }); }, 15000);
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
      o.innerHTML = rel(h); $('.cx-wide', pane).innerHTML = (r.svg ? '<p class="k cx-tt">Process flow</p><div class="zfd" tabindex="0" role="region" aria-label="Process flow diagram">' + r.svg + '</div>' : '') + tw;
      $('.cx-copy', o).addEventListener('click', function () { try { navigator.clipboard.writeText(sum); this.textContent = 'Copied'; } catch (e) {} });
    }
    MOUNTS.push({ mg: function () { [].forEach.call(pane.querySelectorAll('[data-mg]'), function (x) { x.setAttribute('aria-pressed', String(+x.getAttribute('data-mg') === MG)); }); if (cur) calc(); } });
    if (opt.hub) {
      var fromHash = function () { var h = (location.hash || '').slice(1); open(list.some(function (c) { return c.id === h; }) ? h : list[0].id); };
      addEventListener('hashchange', fromHash); fromHash();
    } else open(list[0].id);
  }

  /* calculators.html, then every visible set or single calculator on the page; site.js calls it again when a hidden
     one (another company's section on a division page) comes into view */
  function mountAll() {
    var hub = document.getElementById('calcs');
    if (hub && !hub.hasAttribute('data-on')) { hub.setAttribute('data-on', ''); mount(hub, ORDER, { hub: true, ext: true, h: 2, label: 'Calculators' }); }
    [].forEach.call(document.querySelectorAll('div[data-calc],div[data-calcs]'), function (el) {   // <body data-calcs> on the hub is a page flag, not a calculator
      if (el === hub || el.hasAttribute('data-on') || !el.getClientRects().length) return;
      el.setAttribute('data-on', '');
      var one = el.hasAttribute('data-calc'), ids = (el.getAttribute(one ? 'data-calc' : 'data-calcs') || '').split(',').map(function (x) { return x.trim(); });
      mount(el, ids, { one: one, h: el.hasAttribute('data-h') ? +el.getAttribute('data-h') : 3, ext: el.getAttribute('data-ext') === '1', div: el.getAttribute('data-div') || '', label: el.getAttribute('data-label') || '' });
    });
  }
  window.SHIVAS_CALCS_MOUNT = mountAll;
  if (typeof document.querySelectorAll === 'function') mountAll();   // not when the formulas are tested outside a browser
})();
