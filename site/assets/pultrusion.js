/* SHIVAS Products India: the pultrusion line, animated (pultrusion.html).
   Creel → resin bath → preformer → heated die → two reciprocating pullers → flying cut-off saw.
   It makes each profile in turn, changing after every cut (owner, 25 Nov 2026: animations play by themselves); a profile
   a visitor picks stays for 30 s. The line shows the profile being made: its side view from the die to the saw, the cut
   pieces, the pullers gripping it and its section (owner, 25 Nov 2026: picking a profile must change the look). Pauses off screen. It plays whatever the device's reduce-motion setting, like every
   animation on the site (owner); the Pause button stops it. */
(function () {
  var box = document.getElementById('pu-anim'); if (!box) return;
  var cv = box.querySelector('canvas'), ctx = cv.getContext('2d');
  var W = 1100, H = 330, K = 1, dpr = 1, run = true, vis = true, t = 0, last = 0, looping = false, hold = 0;
  var playB = box.querySelector('.pa-play'), nameEl = box.querySelector('.pa-now');
  var SH = [
    ['ibeam', 'I-beam'], ['hbeam', 'Wide-flange H-beam'], ['fandeck', 'Fan deck plank'], ['channel', 'Channel'], ['angle', 'Equal angle'],
    ['uangle', 'Unequal angle'], ['sq', 'Square tube'], ['rect', 'Rectangular tube'], ['round', 'Round tube'], ['rod', 'Solid rod'],
    ['flat', 'Flat strip'], ['grating', 'Grating bar'], ['ctray', 'Cable tray rail']
  ];
  var cur = 2, pieces = [], made = 0;
  /* the side view of each profile on the line: height and depth of the top face in px, light (+) and dark (-) bands as
     fractions of the height, round = shaded like a cylinder, ribs = grooves along a wide top face, lips = turned-in edges */
  var PV = {
    ibeam: { h: 34, d: 8, b: [[0, .15, .26], [.85, 1, .26], [.15, .85, -.2]] },
    hbeam: { h: 34, d: 16, b: [[0, .14, .28], [.86, 1, .28], [.14, .86, -.24]] },
    fandeck: { h: 14, d: 26, b: [[0, .22, .2], [.78, 1, -.12]], ribs: 1 },
    channel: { h: 30, d: 10, b: [[0, .14, .22], [.86, 1, .22], [.14, .86, -.08]] },
    angle: { h: 26, d: 13, b: [[0, .18, .24]] },
    uangle: { h: 30, d: 8, b: [[0, .14, .24]] },
    sq: { h: 28, d: 11, b: [[0, .1, .16]] },
    rect: { h: 20, d: 15, b: [[0, .12, .16]] },
    round: { h: 26, d: 0, round: 1 },
    rod: { h: 13, d: 0, round: 1 },
    flat: { h: 6, d: 17, b: [] },
    grating: { h: 30, d: 5, b: [[0, .13, .26], [.13, 1, -.12]] },
    ctray: { h: 30, d: 9, b: [[0, .1, .22], [.9, 1, .22], [.1, .22, -.18], [.78, .9, -.18]] }
  };
  var segs = box.querySelector('.pa-shapes');
  segs.innerHTML = SH.map(function (s, i) { return '<button type="button" data-i="' + i + '" aria-pressed="' + (i === cur) + '">' + s[1] + '</button>'; }).join('');
  function shape(i) {
    cur = i; nameEl.textContent = SH[cur][1];
    [].forEach.call(segs.children, function (x, k) { x.setAttribute('aria-pressed', String(k === cur)); });
  }
  segs.addEventListener('click', function (e) {
    var b = e.target.closest('button'); if (!b) return; shape(+b.getAttribute('data-i')); hold = t + 30;
    if (!run) draw();
  });
  shape(cur);
  // one drawing loop at a time (the observer and the start-up used to start two)
  function kick() { if (looping || !run || !vis) return; looping = true; last = performance.now(); requestAnimationFrame(loop); }
  playB.addEventListener('click', function () { run = !run; sync(); kick(); });
  function sync() { playB.textContent = run ? 'Pause' : 'Play'; playB.setAttribute('aria-pressed', String(!run)); }
  sync();
  function size() {
    var r = cv.getBoundingClientRect(); dpr = Math.min(2, window.devicePixelRatio || 1); K = Math.max(1, Math.min(2.2, 700 / (r.width || 1100)));
    cv.width = Math.round(r.width * dpr); cv.height = Math.round(r.width * H / W * dpr); cv.style.height = (r.width * H / W) + 'px';
    if (!run) draw();
  }
  addEventListener('resize', size);
  if (window.ResizeObserver) new ResizeObserver(function () { var w = cv.getBoundingClientRect().width; if (w && Math.abs(w * dpr - cv.width) > 2) size(); }).observe(cv);
  if ('IntersectionObserver' in window) new IntersectionObserver(function (es) { vis = es[0].isIntersecting; kick(); }, { threshold: 0 }).observe(cv);

  var Y = 168, SPEED = 46;               // profile centre line; px per second along the line
  function rr(x, y, w, h, r) { ctx.beginPath(); if (ctx.roundRect) ctx.roundRect(x, y, w, h, r); else ctx.rect(x, y, w, h); }
  function label(x, n, txt) {
    var yb = K > 1.4 ? 290 : 300;
    ctx.fillStyle = 'rgba(9,20,33,.9)'; ctx.beginPath(); ctx.arc(x, yb, 11 * K, 0, 6.283); ctx.fill(); ctx.strokeStyle = '#3fc1ca'; ctx.lineWidth = 1.3 * K; ctx.stroke();
    ctx.fillStyle = '#7fd8de'; ctx.font = '700 ' + (12 * K).toFixed(0) + 'px "Noto Sans", Arial, sans-serif'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(n, x, yb + 1);
    ctx.textBaseline = 'alphabetic';
    if (K <= 1.4) { ctx.fillStyle = '#cfe0ee'; ctx.font = '500 14px "Noto Sans", "Segoe UI", Arial, sans-serif'; ctx.fillText(txt, x, 272); }
  }
  function section(x, y, s, k) {         // cross-section of the current profile, centred at x,y, size s
    ctx.save(); ctx.translate(x, y); ctx.fillStyle = '#9cc7bd'; ctx.strokeStyle = '#e8f3f0'; ctx.lineWidth = 1.5;
    var a = s / 2, t2 = s * .14;
    ctx.beginPath();
    if (k === 'angle') { ctx.rect(-a, -a, t2, s); ctx.rect(-a, a - t2, s, t2); }
    else if (k === 'channel') { ctx.rect(-a, -a, t2, s); ctx.rect(-a, -a, s * .8, t2); ctx.rect(-a, a - t2, s * .8, t2); }
    else if (k === 'ibeam') { ctx.rect(-a * .62, -a, s * .62, t2); ctx.rect(-a * .62, a - t2, s * .62, t2); ctx.rect(-t2 / 2, -a + t2, t2, s - 2 * t2); }
    else if (k === 'hbeam') { ctx.rect(-a, -a, s, t2); ctx.rect(-a, a - t2, s, t2); ctx.rect(-t2 / 2, -a + t2, t2, s - 2 * t2); }
    else if (k === 'uangle') { ctx.rect(-a, -a, t2, s); ctx.rect(-a, a - t2, s * .62, t2); }
    else if (k === 'ctray') { ctx.rect(-a * .5, -a, t2, s); ctx.rect(-a * .5, -a, s * .55, t2); ctx.rect(-a * .5, a - t2, s * .55, t2); ctx.rect(a * .6 - t2, -a + t2, t2, s * .2); ctx.rect(a * .6 - t2, a - t2 - s * .2, t2, s * .2); }
    else if (k === 'fandeck') {             // hollow plank: three cells, a tongue on the right and a groove on the left, so planks lock side by side
      var hh = s * .17, gh = hh * .9, gd = s * .07, w2 = a * 1.25, tw = s * .05;
      ctx.moveTo(-w2, -hh); ctx.lineTo(w2, -hh); ctx.lineTo(w2, -gh / 2); ctx.lineTo(w2 + gd, -gh / 2); ctx.lineTo(w2 + gd, gh / 2); ctx.lineTo(w2, gh / 2); ctx.lineTo(w2, hh);
      ctx.lineTo(-w2, hh); ctx.lineTo(-w2, gh / 2); ctx.lineTo(-w2 + gd, gh / 2); ctx.lineTo(-w2 + gd, -gh / 2); ctx.lineTo(-w2, -gh / 2); ctx.closePath();
      var cw = (2 * w2 - gd - 4 * tw) / 3;
      for (var ci = 0; ci < 3; ci++) { var cx0 = -w2 + gd + tw + ci * (cw + tw); ctx.rect(cx0, -hh + tw, cw, 2 * hh - 2 * tw); } }
    else if (k === 'sq') { ctx.rect(-a, -a, s, s); ctx.rect(a - t2, -a + t2, -(s - 2 * t2), s - 2 * t2); }
    else if (k === 'rect') { ctx.rect(-a, -a * .6, s, s * .6); ctx.rect(a - t2, -a * .6 + t2, -(s - 2 * t2), s * .6 - 2 * t2); }
    else if (k === 'round') { ctx.arc(0, 0, a, 0, 6.283); ctx.moveTo(a - t2, 0); ctx.arc(0, 0, a - t2, Math.PI * 2, 0, true); }
    else if (k === 'rod') { ctx.arc(0, 0, a * .8, 0, 6.283); }
    else if (k === 'flat') { ctx.rect(-a, -t2 / 2, s, t2); }
    else if (k === 'grating') { ctx.rect(-s * .32, -a, s * .64, t2); ctx.rect(-t2 / 2, -a, t2, s * .8); ctx.rect(-s * .32, a - s * .2 - t2, s * .64, t2); }
    ctx.fill('evenodd'); ctx.stroke(); ctx.restore();
  }
  function shadeBand(v) { return v > 0 ? 'rgba(255,255,255,' + v + ')' : 'rgba(0,0,0,' + (-v) + ')'; }
  function bar(x0, x1, k, base, top, flow) {
    var p = PV[k], h = p.h, y = Y - h / 2, w = x1 - x0, x;
    if (p.round) {
      var gr = ctx.createLinearGradient(0, y, 0, y + h); gr.addColorStop(0, top); gr.addColorStop(.32, '#d6efe9'); gr.addColorStop(.55, base); gr.addColorStop(1, '#3f665e');
      ctx.fillStyle = gr; ctx.fillRect(x0, y, w, h);
    } else {
      if (p.d) side(x0, y, w, h, top, p.d);
      ctx.fillStyle = base; ctx.fillRect(x0, y, w, h);
      p.b.forEach(function (b) { ctx.fillStyle = shadeBand(b[2]); ctx.fillRect(x0, y + b[0] * h, w, (b[1] - b[0]) * h); });
      if (p.ribs) {                     // grooves along the wide top face of a fan deck plank
        ctx.strokeStyle = 'rgba(20,40,38,.45)'; ctx.lineWidth = 1;
        for (var r = 1; r < 4; r++) { var f = r / 4, ox = p.d * f, oy = -p.d * .75 * f; ctx.beginPath(); ctx.moveTo(x0 + ox, y + oy); ctx.lineTo(x1 + ox, y + oy); ctx.stroke(); }
      }
    }
    if (flow !== undefined) {           // marks moving with the profile, so the pull shows
      ctx.strokeStyle = 'rgba(11,22,34,.3)'; ctx.lineWidth = 1;
      for (x = x0 + (flow % 30); x < x1; x += 30) { ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x, y + h); ctx.stroke(); }
    }
  }
  // V40: depth: a top and a side face behind a box, and a room with a floor in perspective
  function side(x, y, w, h, col, d) { d = d || 8; var dy = -d * .75;
    ctx.fillStyle = col; ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x + d, y + dy); ctx.lineTo(x + w + d, y + dy); ctx.lineTo(x + w, y); ctx.closePath(); ctx.fill(); ctx.fillStyle = 'rgba(255,255,255,.18)'; ctx.fill();
    ctx.fillStyle = col; ctx.beginPath(); ctx.moveTo(x + w, y); ctx.lineTo(x + w + d, y + dy); ctx.lineTo(x + w + d, y + h + dy); ctx.lineTo(x + w, y + h); ctx.closePath(); ctx.fill(); ctx.fillStyle = 'rgba(0,0,0,.35)'; ctx.fill(); }
  function room() {
    var gb = ctx.createLinearGradient(0, 0, 0, H); gb.addColorStop(0, '#10263d'); gb.addColorStop(.7, '#0d2134'); gb.addColorStop(1, '#0a1a2a');
    ctx.fillStyle = gb; ctx.fillRect(0, 0, W, H);
    var sp = ctx.createRadialGradient(W * .45, 90, 20, W * .45, 120, 620); sp.addColorStop(0, 'rgba(110,160,215,.16)'); sp.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = sp; ctx.fillRect(0, 0, W, 238);
    ctx.lineWidth = .6; ctx.strokeStyle = 'rgba(150,190,230,.05)'; ctx.beginPath();
    for (var gx = 0; gx <= W; gx += 20) { ctx.moveTo(gx, 0); ctx.lineTo(gx, 238); } for (var gy = 238; gy >= 0; gy -= 20) { ctx.moveTo(0, gy); ctx.lineTo(W, gy); } ctx.stroke();
    ctx.strokeStyle = 'rgba(150,190,230,.085)'; ctx.beginPath(); for (gx = 0; gx <= W; gx += 100) { ctx.moveTo(gx, 0); ctx.lineTo(gx, 238); } ctx.stroke();
    var fg = ctx.createLinearGradient(0, 238, 0, H); fg.addColorStop(0, 'rgba(130,170,210,.13)'); fg.addColorStop(1, 'rgba(10,24,40,0)'); ctx.fillStyle = fg; ctx.fillRect(0, 238, W, H - 238);
    for (var x = -600; x <= W + 600; x += 60) { var lg = ctx.createLinearGradient(0, 238, 0, H); lg.addColorStop(0, 'rgba(160,195,225,.12)'); lg.addColorStop(1, 'rgba(160,195,225,0)'); ctx.strokeStyle = lg; ctx.lineWidth = .8; ctx.beginPath(); ctx.moveTo(W / 2 + (x - W / 2) * .55, 238); ctx.lineTo(x, H); ctx.stroke(); }
    ctx.fillStyle = 'rgba(190,220,245,.25)'; ctx.fillRect(0, 238, W, 1.2); }
  /* V81 pultrusion: contact shadow on the floor and a steel stand */
  function shadow(x, w) { ctx.save(); ctx.translate(x + w / 2, 239); ctx.scale(1, .12); var g2 = ctx.createRadialGradient(0, 0, 0, 0, 0, w * .6 + 8); g2.addColorStop(0, 'rgba(0,0,0,.45)'); g2.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = g2; ctx.beginPath(); ctx.arc(0, 0, w * .6 + 8, 0, 6.283); ctx.fill(); ctx.restore(); }
  function stand(x, y, w) { var sg = ctx.createLinearGradient(0, y, 0, 238); sg.addColorStop(0, '#3b5672'); sg.addColorStop(1, '#22364b'); ctx.fillStyle = sg; ctx.fillRect(x, y, 8, 238 - y); ctx.fillRect(x + w - 8, y, 8, 238 - y); ctx.fillRect(x, 226, w, 6); ctx.fillStyle = 'rgba(255,255,255,.12)'; ctx.fillRect(x, y, 2, 238 - y); }
  function vignette() { var v = ctx.createRadialGradient(W / 2, H * .45, W * .3, W / 2, H * .5, W * .75); v.addColorStop(0, 'rgba(4,10,18,0)'); v.addColorStop(1, 'rgba(4,10,18,.36)'); ctx.fillStyle = v; ctx.fillRect(0, 0, W, H); }
  function draw() {
    if (!cv.width) { var w0 = cv.getBoundingClientRect().width; if (!w0) return; size(); }
    var sx = cv.width / W; ctx.setTransform(sx, 0, 0, sx, 0, 0);
    room();
    // floor
    ctx.fillStyle = '#13263a'; ctx.fillRect(0, 238, W, 2);
    var flow = t * SPEED;
    shadow(20, 116); shadow(220, 130); shadow(470, 180); shadow(680, 250); shadow(950, 150);
    ctx.strokeStyle = '#3b5672'; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(22, 214); ctx.lineTo(22, 60); ctx.moveTo(134, 214); ctx.lineTo(134, 60); ctx.moveTo(22, 60); ctx.lineTo(134, 60); for (var cyy = 99; cyy < 214; cyy += 34) { ctx.moveTo(22, cyy); ctx.lineTo(134, cyy); } ctx.stroke();
    // 1 creel: spools turning
    for (var i = 0; i < 3; i++) for (var j = 0; j < 4; j++) {
      var cx = 38 + i * 34, cy = 82 + j * 34;
      for (var q = 3; q >= 1; q--) { ctx.fillStyle = 'rgba(70,74,70,' + (.5 - q * .1) + ')'; ctx.beginPath(); ctx.arc(cx + q * 1.5, cy - q * 1.1, 13, 0, 6.283); ctx.fill(); }
      var sg = ctx.createRadialGradient(cx - 4, cy - 5, 1, cx, cy, 13); sg.addColorStop(0, '#f4f1e6'); sg.addColorStop(.75, '#d6d0bb'); sg.addColorStop(1, '#a59d84');
      ctx.fillStyle = sg; ctx.beginPath(); ctx.arc(cx, cy, 13, 0, 6.283); ctx.fill();
      ctx.strokeStyle = 'rgba(120,110,85,.35)'; ctx.lineWidth = .6; for (var rq = 11; rq > 5; rq -= 2) { ctx.beginPath(); ctx.arc(cx, cy, rq, 0, 6.283); ctx.stroke(); }
      ctx.fillStyle = '#1a2a3c'; ctx.beginPath(); ctx.arc(cx, cy, 4.2, 0, 6.283); ctx.fill(); ctx.strokeStyle = '#7f93a6'; ctx.lineWidth = 1; ctx.stroke();
      ctx.save(); ctx.translate(cx, cy); ctx.rotate(t * 2 + i + j); ctx.fillStyle = 'rgba(80,70,50,.55)'; ctx.fillRect(7, -1, 5, 2); ctx.restore();
    }
    ctx.fillStyle = '#2d4860'; ctx.fillRect(20, 214, 116, 6);
    // fibres: spools → guide → down into the bath → up to the preformer
    ctx.lineWidth = .9; ctx.setLineDash([2, 9]); ctx.lineDashOffset = -flow;
    for (i = 0; i < 3; i++) for (j = 0; j < 4; j++) {
      ctx.setLineDash([]); ctx.strokeStyle = 'rgba(233,226,200,.28)'; ctx.beginPath(); ctx.moveTo(52 + i * 34, 82 + j * 34);
      ctx.lineTo(170, 150 + j * 3); ctx.lineTo(240, 190 + j * 2); ctx.lineTo(330, 190 + j * 2); ctx.lineTo(392, Y - 4 + j * 2.5); ctx.stroke();
      ctx.setLineDash([2, 9]); ctx.strokeStyle = 'rgba(255,250,232,.85)'; ctx.beginPath(); ctx.moveTo(52 + i * 34, 82 + j * 34);
      ctx.lineTo(170, 150 + j * 3); ctx.lineTo(240, 190 + j * 2); ctx.lineTo(330, 190 + j * 2); ctx.lineTo(392, Y - 4 + j * 2.5); ctx.stroke();
    }
    ctx.setLineDash([]);
    ctx.fillStyle = '#5d7590'; ctx.fillRect(164, 140, 8, 28);
    // 2 resin bath with a moving surface
    side(220, 168, 130, 58, '#6b5a34', 10); rr(220, 168, 130, 58, 6); ctx.fillStyle = 'rgba(217,164,65,.38)'; ctx.fill(); ctx.strokeStyle = '#d9a441'; ctx.lineWidth = 2; ctx.stroke();
    ctx.beginPath(); ctx.moveTo(222, 178);
    for (var x = 222; x <= 348; x += 6) ctx.lineTo(x, 178 + Math.sin(x * .12 + t * 3) * 2);
    ctx.strokeStyle = '#f0c46a'; ctx.lineWidth = 1.5; ctx.stroke();
    stand(226, 226, 118);
    var dr = ctx.createRadialGradient(282, 200, 2, 285, 204, 12); dr.addColorStop(0, '#dfe7ee'); dr.addColorStop(1, '#5d7590'); ctx.fillStyle = dr; ctx.beginPath(); ctx.arc(285, 204, 11, 0, 6.283); ctx.fill();
    ctx.save(); ctx.translate(285, 204); ctx.rotate(t * 2); ctx.strokeStyle = 'rgba(30,45,60,.6)'; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.moveTo(-8, 0); ctx.lineTo(8, 0); ctx.stroke(); ctx.restore();
    // 3 preformer plates
    ctx.fillStyle = '#5d7590'; ctx.fillRect(386, Y - 34, 8, 68); ctx.fillRect(410, Y - 26, 8, 52);
    var hP = PV[SH[cur][0]].h; ctx.fillStyle = '#e9e2c8'; ctx.fillRect(394, Y - Math.max(3, hP * .3), 76, Math.max(6, hP * .6));
    // 4 heated die, heater bands glowing
    var g = ctx.createLinearGradient(470, 0, 650, 0); g.addColorStop(0, '#3a2a1a'); g.addColorStop(.5, '#8a3d17'); g.addColorStop(1, '#4a2a1a');
    side(470, Y - 46, 180, 92, '#5a2a12', 12); rr(470, Y - 46, 180, 92, 6); ctx.fillStyle = g; ctx.fill(); ctx.strokeStyle = '#e66a2c'; ctx.lineWidth = 2; ctx.stroke();
    for (i = 0; i < 5; i++) { var hb = .5 + .3 * Math.sin(t * 2.2 + i * .9), bg = ctx.createLinearGradient(484 + i * 34, 0, 498 + i * 34, 0); bg.addColorStop(0, 'rgba(120,40,12,.9)'); bg.addColorStop(.5, 'rgba(255,' + Math.round(100 + 60 * hb) + ',44,' + (.55 + .35 * hb).toFixed(3) + ')'); bg.addColorStop(1, 'rgba(120,40,12,.9)'); ctx.fillStyle = bg; ctx.fillRect(484 + i * 34, Y - 52, 14, 104);
      ctx.save(); ctx.globalCompositeOperation = 'lighter'; var gl = ctx.createRadialGradient(491 + i * 34, Y, 2, 491 + i * 34, Y, 46); gl.addColorStop(0, 'rgba(255,120,50,' + (.16 * hb).toFixed(3) + ')'); gl.addColorStop(1, 'rgba(255,120,50,0)'); ctx.fillStyle = gl; ctx.fillRect(445 + i * 34, Y - 60, 92, 120); ctx.restore(); }
    stand(494, Y + 46, 132);
    for (i = 0; i < 5; i++) { ctx.strokeStyle = '#c9d4de'; ctx.lineWidth = 1.2; ctx.beginPath(); ctx.moveTo(491 + i * 34, Y - 52); ctx.quadraticCurveTo(491 + i * 34, Y - 72, 500 + i * 34, Y - 80); ctx.stroke(); ctx.fillStyle = '#e8a317'; ctx.fillRect(498 + i * 34, Y - 84, 6, 6); }
    // the cured profile, moving
    var p0 = 650, p1 = 960, hh2 = hP / 2;
    bar(p0, p1, SH[cur][0], '#7fb3a8', '#5f8f85', flow);
    // 5 two reciprocating pullers: one grips and pulls while the other returns open
    var cyc = 4, ph = (t % cyc) / cyc;
    [0, 1].forEach(function (k) {
      var q = (ph + k * .5) % 1, pulling = q < .5, u = pulling ? q / .5 : 1 - (q - .5) / .5;
      var bx = 690 + k * 120 + u * 70, gap = pulling ? 0 : 7;
      var pc = '#55687c'; [Y - hh2 - 20 - gap, Y + hh2 + 2 + gap].forEach(function (yy, top) { side(bx, yy, 44, 18, pc, 6); var mg = ctx.createLinearGradient(0, yy, 0, yy + 18); mg.addColorStop(0, '#9fb2c4'); mg.addColorStop(.5, '#6b7f93'); mg.addColorStop(1, '#45576a'); ctx.fillStyle = mg; rr(bx, yy, 44, 18, 3); ctx.fill(); ctx.strokeStyle = 'rgba(255,255,255,.25)'; ctx.lineWidth = 1; ctx.stroke();
        ctx.fillStyle = pulling ? '#e8a317' : '#3a4a5a'; ctx.fillRect(bx + 3, top ? yy - 3 : yy + 18, 38, 3); });
      ctx.fillStyle = '#2d4860'; ctx.fillRect(bx + 18, Y + hh2 + 20 + gap, 8, 238 - (Y + hh2 + 20 + gap));
    });
    ctx.fillStyle = '#2d4860'; ctx.fillRect(680, 236, 250, 4);
    [0, 1].forEach(function (k) { var q = (ph + k * .5) % 1, pulling = q < .5, u = pulling ? q / .5 : 1 - (q - .5) / .5, bx = 690 + k * 120 + u * 70, cy0 = 214 + k * 8;
      var cg = ctx.createLinearGradient(0, cy0 - 6, 0, cy0 + 6); cg.addColorStop(0, '#6f8faf'); cg.addColorStop(.5, '#3f6082'); cg.addColorStop(1, '#1f3550'); ctx.fillStyle = cg; ctx.fillRect(bx + 44, cy0 - 6, 6, 12);
      var rg2 = ctx.createLinearGradient(0, cy0 - 3, 0, cy0 + 3); rg2.addColorStop(0, '#f1f5f8'); rg2.addColorStop(1, '#8fa3b6'); ctx.fillStyle = rg2; ctx.fillRect(bx + 50, cy0 - 3, Math.max(4, 800 + k * 120 - bx - 50), 6);
      ctx.fillStyle = cg; ctx.fillRect(800 + k * 120, cy0 - 7, 34, 14); });
    // 6 flying saw: rides with the profile, drops, cuts, returns; cut pieces roll away on the table
    var sc = 7, sp = (t % sc) / sc, sxp = 900 + (sp < .6 ? sp / .6 * 40 : 40 - (sp - .6) / .4 * 40), down = sp > .25 && sp < .6;
    var bladeY = down ? Y : Y - 44;
    ctx.save(); ctx.translate(sxp, bladeY); var bd = ctx.createRadialGradient(0, 0, 4, 0, 0, 24); bd.addColorStop(0, 'rgba(200,215,228,.35)'); bd.addColorStop(1, 'rgba(200,215,228,.08)'); ctx.fillStyle = bd; ctx.beginPath(); ctx.arc(0, 0, 22, 0, 6.283); ctx.fill(); ctx.fillStyle = '#1a2a3c'; ctx.beginPath(); ctx.arc(0, 0, 5, 0, 6.283); ctx.fill(); ctx.rotate(t * 12);
    ctx.strokeStyle = '#dfe7ee'; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(0, 0, 22, 0, 6.283); ctx.stroke();
    for (i = 0; i < 12; i++) { ctx.rotate(.5236); ctx.beginPath(); ctx.moveTo(22, 0); ctx.lineTo(26, 3); ctx.stroke(); }
    ctx.restore();
    ctx.fillStyle = '#5d7590'; ctx.fillRect(sxp - 3, 60, 6, bladeY - 60 - 22);
    ctx.fillStyle = '#3b5672'; ctx.fillRect(sxp - 30, 50, 60, 14); ctx.fillStyle = '#2d4860'; ctx.fillRect(sxp - 8, 0, 16, 50);
    if (down) { for (var di = 0; di < 18; di++) { var dph = ((t * 1.8) + di / 18) % 1, da = -1.2 + (di % 7) * .35; ctx.fillStyle = 'rgba(214,236,230,' + (.6 * (1 - dph)).toFixed(3) + ')'; ctx.beginPath(); ctx.arc(sxp + Math.cos(da) * dph * 46, Y + Math.sin(da) * dph * 30 - dph * 10, 1.6 + dph * 2.4, 0, 6.283); ctx.fill(); } }
    if (down && Math.abs(sp - .58) < .02 && (!pieces.length || t - pieces[pieces.length - 1].t > 3)) { pieces.push({ t: t, k: SH[cur][0] }); made++; if (t >= hold) shape((cur + 1) % SH.length); }
    pieces = pieces.filter(function (pc) { return t - pc.t < 9; });
    pieces.forEach(function (pc) {
      var age = t - pc.t, x0 = 960 + age * SPEED * .9;
      bar(x0, x0 + 110, pc.k, '#9cc7bd', '#79a79d');
      section(Math.min(x0 + 124, W - 24), Y, 26, pc.k);
    });
    ctx.fillStyle = '#2d4860'; ctx.fillRect(950, 236, 150, 4); stand(952, Y + 24, 146); ctx.fillStyle = '#3b5672'; ctx.fillRect(952, Y + 22, 146, 5);
    for (var ri = 0; ri < 6; ri++) { var rx2 = 962 + ri * 24, rg3 = ctx.createRadialGradient(rx2 - 2, Y + 20, 1, rx2, Y + 22, 6); rg3.addColorStop(0, '#dfe7ee'); rg3.addColorStop(1, '#4d6278'); ctx.fillStyle = rg3; ctx.beginPath(); ctx.arc(rx2, Y + 22, 5, 0, 6.283); ctx.fill(); }
    // section inset
    var kk = Math.min(K, 1.15), small = K > 1.4, iw = 164 * kk, ih = 124 * kk, ix = 186;   // above the resin bath, clear of the saw; on phones the name shows under the drawing
    rr(ix, 12, iw, ih, 10); ctx.fillStyle = 'rgba(19,38,58,.95)'; ctx.fill(); ctx.strokeStyle = '#3fc1ca'; ctx.lineWidth = 1.2; ctx.stroke();
    ctx.fillStyle = '#8fa6bb'; ctx.font = '600 ' + (11 * kk).toFixed(0) + 'px "Noto Sans", "Segoe UI", Arial, sans-serif'; ctx.textAlign = 'left'; ctx.fillText('SECTION', ix + 10, 12 + 18 * kk);
    ctx.fillStyle = '#e8f3f0'; ctx.font = '700 ' + (12 * kk).toFixed(0) + 'px "Noto Sans", "Segoe UI", Arial, sans-serif'; ctx.textAlign = 'center'; if (!small) ctx.fillText(SH[cur][1], ix + iw / 2, 12 + ih - 10 * kk);
    section(ix + iw / 2, 12 + ih * (small ? .56 : .5), (small ? 64 : 52) * kk, SH[cur][0]);
    vignette();
    // stations
    label(74, 1, 'Creel'); label(285, 2, 'Resin bath'); label(402, 3, 'Preformer'); label(560, 4, 'Heated die'); label(790, 5, 'Pullers'); label(930, 6, 'Saw');
  }
  function loop(now) {
    if (!run || !vis) { looping = false; return; }
    var dt = Math.min(.05, (now - last) / 1000); last = now; t += dt; draw(); requestAnimationFrame(loop);
  }
  size(); draw(); kick();
})();
