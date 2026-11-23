/* SHIVAS Products India: the pultrusion line, animated (pultrusion.html).
   Creel → resin bath → preformer → heated die → two reciprocating pullers → flying cut-off saw.
   Pick a profile to change what comes out of the die. Pauses off screen; starts paused for reduced motion. */
(function () {
  var box = document.getElementById('pu-anim'); if (!box) return;
  var cv = box.querySelector('canvas'), ctx = cv.getContext('2d');
  var W = 1100, H = 330, K = 1, dpr = 1, run = !matchMedia('(prefers-reduced-motion: reduce)').matches, vis = true, t = 0, last = 0;
  var playB = box.querySelector('.pa-play'), nameEl = box.querySelector('.pa-now');
  var SH = [
    ['angle', 'Equal angle'], ['channel', 'Channel'], ['ibeam', 'I-beam'], ['sq', 'Square tube'],
    ['rect', 'Rectangular tube'], ['round', 'Round tube'], ['rod', 'Solid rod'], ['flat', 'Flat strip'], ['grating', 'Grating bar']
  ];
  var cur = 2, pieces = [], made = 0;
  var segs = box.querySelector('.pa-shapes');
  segs.innerHTML = SH.map(function (s, i) { return '<button type="button" data-i="' + i + '" aria-pressed="' + (i === cur) + '">' + s[1] + '</button>'; }).join('');
  segs.addEventListener('click', function (e) {
    var b = e.target.closest('button'); if (!b) return; cur = +b.getAttribute('data-i');
    [].forEach.call(segs.children, function (x) { x.setAttribute('aria-pressed', String(x === b)); });
    nameEl.textContent = SH[cur][1]; if (!run) draw();
  });
  nameEl.textContent = SH[cur][1];
  playB.addEventListener('click', function () { run = !run; sync(); if (run) { last = performance.now(); requestAnimationFrame(loop); } });
  function sync() { playB.textContent = run ? 'Pause' : 'Play'; playB.setAttribute('aria-pressed', String(!run)); }
  sync();
  function size() {
    var r = cv.getBoundingClientRect(); dpr = Math.min(2, window.devicePixelRatio || 1); K = Math.max(1, Math.min(2.2, 700 / (r.width || 1100)));
    cv.width = Math.round(r.width * dpr); cv.height = Math.round(r.width * H / W * dpr); cv.style.height = (r.width * H / W) + 'px';
    if (!run) draw();
  }
  addEventListener('resize', size);
  if (window.ResizeObserver) new ResizeObserver(function () { var w = cv.getBoundingClientRect().width; if (w && Math.abs(w * dpr - cv.width) > 2) size(); }).observe(cv);
  if ('IntersectionObserver' in window) new IntersectionObserver(function (es) { vis = es[0].isIntersecting; if (vis && run) { last = performance.now(); requestAnimationFrame(loop); } }, { threshold: 0 }).observe(cv);

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
    else if (k === 'ibeam') { ctx.rect(-a, -a, s, t2); ctx.rect(-a, a - t2, s, t2); ctx.rect(-t2 / 2, -a, t2, s); }
    else if (k === 'sq') { ctx.rect(-a, -a, s, s); ctx.rect(a - t2, -a + t2, -(s - 2 * t2), s - 2 * t2); }
    else if (k === 'rect') { ctx.rect(-a, -a * .6, s, s * .6); ctx.rect(a - t2, -a * .6 + t2, -(s - 2 * t2), s * .6 - 2 * t2); }
    else if (k === 'round') { ctx.arc(0, 0, a, 0, 6.283); ctx.moveTo(a - t2, 0); ctx.arc(0, 0, a - t2, 0, 6.283, true); }
    else if (k === 'rod') { ctx.arc(0, 0, a * .8, 0, 6.283); }
    else if (k === 'flat') { ctx.rect(-a, -t2 / 2, s, t2); }
    else if (k === 'grating') { ctx.rect(-s * .32, -a, s * .64, t2); ctx.rect(-t2 / 2, -a, t2, s * .8); ctx.rect(-s * .32, a - s * .2 - t2, s * .64, t2); }
    ctx.fill('evenodd'); ctx.stroke(); ctx.restore();
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
  function vignette() { var v = ctx.createRadialGradient(W / 2, H * .45, W * .3, W / 2, H * .5, W * .75); v.addColorStop(0, 'rgba(4,10,18,0)'); v.addColorStop(1, 'rgba(4,10,18,.36)'); ctx.fillStyle = v; ctx.fillRect(0, 0, W, H); }
  function draw() {
    if (!cv.width) { var w0 = cv.getBoundingClientRect().width; if (!w0) return; size(); }
    var sx = cv.width / W; ctx.setTransform(sx, 0, 0, sx, 0, 0);
    room();
    // floor
    ctx.fillStyle = '#13263a'; ctx.fillRect(0, 238, W, 2);
    var flow = t * SPEED;
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
    ctx.fillStyle = '#2d4860'; ctx.fillRect(228, 226, 8, 12); ctx.fillRect(334, 226, 8, 12);
    // 3 preformer plates
    ctx.fillStyle = '#5d7590'; ctx.fillRect(386, Y - 34, 8, 68); ctx.fillRect(410, Y - 26, 8, 52);
    ctx.fillStyle = '#e9e2c8'; ctx.fillRect(394, Y - 5, 76, 10);
    // 4 heated die, heater bands glowing
    var g = ctx.createLinearGradient(470, 0, 650, 0); g.addColorStop(0, '#3a2a1a'); g.addColorStop(.5, '#8a3d17'); g.addColorStop(1, '#4a2a1a');
    side(470, Y - 46, 180, 92, '#5a2a12', 12); rr(470, Y - 46, 180, 92, 6); ctx.fillStyle = g; ctx.fill(); ctx.strokeStyle = '#e66a2c'; ctx.lineWidth = 2; ctx.stroke();
    for (i = 0; i < 5; i++) { var hb = .5 + .3 * Math.sin(t * 2.2 + i * .9), bg = ctx.createLinearGradient(484 + i * 34, 0, 498 + i * 34, 0); bg.addColorStop(0, 'rgba(120,40,12,.9)'); bg.addColorStop(.5, 'rgba(255,' + Math.round(100 + 60 * hb) + ',44,' + (.55 + .35 * hb).toFixed(3) + ')'); bg.addColorStop(1, 'rgba(120,40,12,.9)'); ctx.fillStyle = bg; ctx.fillRect(484 + i * 34, Y - 52, 14, 104);
      ctx.save(); ctx.globalCompositeOperation = 'lighter'; var gl = ctx.createRadialGradient(491 + i * 34, Y, 2, 491 + i * 34, Y, 46); gl.addColorStop(0, 'rgba(255,120,50,' + (.16 * hb).toFixed(3) + ')'); gl.addColorStop(1, 'rgba(255,120,50,0)'); ctx.fillStyle = gl; ctx.fillRect(445 + i * 34, Y - 60, 92, 120); ctx.restore(); }
    ctx.fillStyle = '#2d4860'; ctx.fillRect(500, Y + 46, 10, 238 - Y - 46); ctx.fillRect(610, Y + 46, 10, 238 - Y - 46);
    // the cured profile, moving
    var p0 = 650, p1 = 960;
    side(p0, Y - 10, p1 - p0, 20, '#5f8f85', 7); ctx.fillStyle = '#7fb3a8'; ctx.fillRect(p0, Y - 10, p1 - p0, 20);
    ctx.strokeStyle = 'rgba(11,22,34,.35)'; ctx.lineWidth = 1;
    for (x = p0 + (flow % 30); x < p1; x += 30) { ctx.beginPath(); ctx.moveTo(x, Y - 10); ctx.lineTo(x, Y + 10); ctx.stroke(); }
    // 5 two reciprocating pullers: one grips and pulls while the other returns open
    var cyc = 4, ph = (t % cyc) / cyc;
    [0, 1].forEach(function (k) {
      var q = (ph + k * .5) % 1, pulling = q < .5, u = pulling ? q / .5 : 1 - (q - .5) / .5;
      var bx = 690 + k * 120 + u * 70, gap = pulling ? 0 : 7;
      var pc = '#55687c'; [Y - 30 - gap, Y + 12 + gap].forEach(function (yy, top) { side(bx, yy, 44, 18, pc, 6); var mg = ctx.createLinearGradient(0, yy, 0, yy + 18); mg.addColorStop(0, '#9fb2c4'); mg.addColorStop(.5, '#6b7f93'); mg.addColorStop(1, '#45576a'); ctx.fillStyle = mg; rr(bx, yy, 44, 18, 3); ctx.fill(); ctx.strokeStyle = 'rgba(255,255,255,.25)'; ctx.lineWidth = 1; ctx.stroke();
        ctx.fillStyle = pulling ? '#e8a317' : '#3a4a5a'; ctx.fillRect(bx + 3, top ? yy - 3 : yy + 18, 38, 3); });
      ctx.fillStyle = '#2d4860'; ctx.fillRect(bx + 18, Y + 30 + gap, 8, 238 - (Y + 30 + gap));
    });
    ctx.fillStyle = '#2d4860'; ctx.fillRect(680, 236, 250, 4);
    // 6 flying saw: rides with the profile, drops, cuts, returns; cut pieces roll away on the table
    var sc = 7, sp = (t % sc) / sc, sxp = 900 + (sp < .6 ? sp / .6 * 40 : 40 - (sp - .6) / .4 * 40), down = sp > .25 && sp < .6;
    var bladeY = down ? Y : Y - 44;
    ctx.save(); ctx.translate(sxp, bladeY); var bd = ctx.createRadialGradient(0, 0, 4, 0, 0, 24); bd.addColorStop(0, 'rgba(200,215,228,.35)'); bd.addColorStop(1, 'rgba(200,215,228,.08)'); ctx.fillStyle = bd; ctx.beginPath(); ctx.arc(0, 0, 22, 0, 6.283); ctx.fill(); ctx.fillStyle = '#1a2a3c'; ctx.beginPath(); ctx.arc(0, 0, 5, 0, 6.283); ctx.fill(); ctx.rotate(t * 12);
    ctx.strokeStyle = '#dfe7ee'; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(0, 0, 22, 0, 6.283); ctx.stroke();
    for (i = 0; i < 12; i++) { ctx.rotate(.5236); ctx.beginPath(); ctx.moveTo(22, 0); ctx.lineTo(26, 3); ctx.stroke(); }
    ctx.restore();
    ctx.fillStyle = '#5d7590'; ctx.fillRect(sxp - 3, 60, 6, bladeY - 60 - 22);
    if (down && Math.abs(sp - .58) < .02 && (!pieces.length || t - pieces[pieces.length - 1].t > 3)) { pieces.push({ t: t, k: SH[cur][0] }); made++; }
    pieces = pieces.filter(function (pc) { return t - pc.t < 9; });
    pieces.forEach(function (pc) {
      var age = t - pc.t, x0 = 960 + age * SPEED * .9;
      side(x0, Y - 10, 110, 20, '#79a79d', 7); ctx.fillStyle = '#9cc7bd'; ctx.fillRect(x0, Y - 10, 110, 20);
      section(Math.min(x0 + 120, W - 22), Y, 22, pc.k);
    });
    ctx.fillStyle = '#2d4860'; ctx.fillRect(950, 236, 150, 4);
    // section inset
    var iw = 134 * Math.min(K, 1.6), ih = 104 * Math.min(K, 1.6);
    rr(W - iw - 16, 16, iw, ih, 10); ctx.fillStyle = 'rgba(19,38,58,.95)'; ctx.fill(); ctx.strokeStyle = '#2d4860'; ctx.lineWidth = 1; ctx.stroke();
    ctx.fillStyle = '#8fa6bb'; ctx.font = '500 ' + (12 * Math.min(K, 1.6)).toFixed(0) + 'px "Noto Sans", "Segoe UI", Arial, sans-serif'; ctx.textAlign = 'left'; ctx.fillText('SECTION', W - iw - 6, 34 * Math.min(K, 1.3));
    section(W - 16 - iw / 2, 16 + ih * .58, 48 * Math.min(K, 1.6), SH[cur][0]);
    vignette();
    // stations
    label(74, 1, 'Creel'); label(285, 2, 'Resin bath'); label(402, 3, 'Preformer'); label(560, 4, 'Heated die'); label(790, 5, 'Pullers'); label(930, 6, 'Saw');
  }
  function loop(now) {
    if (!run || !vis) return;
    var dt = Math.min(.05, (now - last) / 1000); last = now; t += dt; draw(); requestAnimationFrame(loop);
  }
  size(); draw(); if (run) { last = performance.now(); requestAnimationFrame(loop); }
})();
