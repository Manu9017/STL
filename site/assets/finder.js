/* SHIVAS product finder: three drop-downs (what you make, what you need, how much) lead to the SHIVAS products
   that fit, drawn as line drawings with a link to each product page, and to the plant calculator where it applies.
   <section data-finder="hdg|wire|rein"> holds the UI; product names come from assets/library.js. */
(function () {
  'use strict';
  var L = window.SHIVAS_LIBRARY; if (!L) return;
  var MAKE = {
    structural: { n: 'Structural steel, sheds and fabrications', g: 'galv', fam: 'isa', cap: 's' },
    solar: { n: 'Solar module mounting structures', g: 'galv', fam: 'cpur', cap: 's' },
    tower: { n: 'Transmission, telecom and lighting towers and poles', g: 'galv', fam: 'tower', cap: 's' },
    barrier: { n: 'Crash barriers and highway steel', g: 'galv', fam: 'cb', cap: 's' },
    pipe: { n: 'Pipes, tubes and hollow sections', g: 'galv', fam: 'chs', cap: 's' },
    fastener: { n: 'Fasteners, bolts and small parts', g: 'spin', fam: 'fast', cap: 's' },
    wiredraw: { n: 'Wire drawn from rod (MS, HB, high-carbon, spring)', g: 'draw', cap: 'w' },
    wiregalv: { n: 'Galvanized wire, barbed wire, strand', g: 'wgalv', cap: 'w' },
    mig: { n: 'CO₂ / MIG welding wire', g: 'mig', cap: 'w' },
    alwire: { n: 'Aluminium wire and conductor', g: 'al', cap: 'w' },
    strip: { n: 'Steel strip and coil', g: 'strip', cap: 's' },
    chem: { n: 'Chemical, plating and process plants', g: 'chem', cap: 'p' },
    effluent: { n: 'An effluent, acid or fume problem to solve', g: 'env', cap: 'p' }
  };
  var NEED = { new: 'A complete new plant or line', upgrade: 'More output or lower cost from my plant', equipment: 'A particular machine or equipment', env: 'Fume, acid and effluent compliance' };
  var CAP = {
    s: [['s1', 'Up to 500 t a month', 400], ['s2', '500 to 2,000 t a month', 1200], ['s3', 'More than 2,000 t a month', 3000]],
    w: [['w1', 'Up to 30 t a day', 20], ['w2', '30 to 100 t a day', 60], ['w3', 'More than 100 t a day', 150]],
    p: [['p1', 'A single unit', 1], ['p2', 'A complete plant', 2], ['p3', 'Several sites or lines', 3]]
  };
  var MAP = {
    galv: { new: ['turnkey', 'kettle', 'furnace', 'burner', 'pretreat', 'acidroom', 'flux', 'dryer', 'enclosure', 'zfe', 'afe', 'eot', 'jig', 'quench', 'auto', 'env'],
            upgrade: ['kettle', 'furnace', 'burner', 'gastrain', 'efurnace', 'flux', 'fluxheat', 'dross', 'ash', 'zfe', 'auto', 'jig'],
            equipment: ['kettle', 'furnace', 'burner', 'gastrain', 'pretreat', 'flux', 'dryer', 'fluxheat', 'eot', 'jig', 'dross', 'corner'],
            env: ['afe', 'zfe', 'enclosure', 'acidroom', 'r-scrub', 'r-acid', 'env', 'r-etp', 'ash'] },
    spin: { new: ['spin', 'kettle', 'furnace', 'burner', 'pretreat', 'acidroom', 'dryer', 'zfe', 'afe', 'quench', 'auto'],
            upgrade: ['spin', 'furnace', 'burner', 'zfe', 'ash', 'auto'], equipment: ['spin', 'kettle', 'burner', 'dross', 'quench'],
            env: ['zfe', 'afe', 'acidroom', 'r-scrub', 'r-etp', 'ash'] },
    draw: { new: ['wdline', 'payoff', 'descaler', 'pointing', 'butt', 'slm', 'oto', 'diebox', 'dbc', 'spooler'],
            upgrade: ['slm', 'oto', 'diebox', 'dbc', 'spooler', 'acc'],
            equipment: ['slm', 'oto', 'bull', 'wet', 'dbc', 'vcoiler', 'ivcoiler', 'payoff', 'descaler', 'pointing', 'butt', 'spooler', 'diebox', 'coildryer', 'acc', 'special'],
            env: ['r-wirepick', 'line-fpl', 'r-scrub', 'r-acid', 'r-etp'] },
    wgalv: { new: ['hdgwire', 'line-cgl', 'line-fpl', 'payoff', 'anneal', 'wirezinc', 'htakeup', 'r-scrub', 'r-acid'],
             upgrade: ['wirezinc', 'line-fpl', 'htakeup', 'anneal', 'r-acid'], equipment: ['wirezinc', 'htakeup', 'payoff', 'anneal', 'egline', 'line-egl'],
             env: ['line-fpl', 'r-scrub', 'r-acid', 'r-etp', 'r-zld'] },
    mig: { new: ['mig', 'payoff', 'descaler', 'slm', 'spooler', 'line-egl'], upgrade: ['mig', 'slm', 'spooler', 'diebox'], equipment: ['mig', 'slm', 'spooler', 'diebox', 'acc'], env: ['line-fpl', 'r-scrub', 'r-etp'] },
    al: { new: ['alwdm', 'payoff', 'spooler', 'acc'], upgrade: ['alwdm', 'spooler', 'acc', 'special'], equipment: ['alwdm', 'spooler', 'acc', 'special'], env: ['r-scrub', 'r-etp'] },
    strip: { new: ['r-strip', 'r-pick', 'r-airdryer', 'r-scrub', 'r-acid', 'r-etp'], upgrade: ['r-strip', 'r-airdryer', 'r-hx', 'r-acid', 'r-recovery'],
             equipment: ['r-tanks', 'r-pump', 'r-hx', 'r-airdryer', 'r-hood', 'r-duct', 'r-blower'], env: ['r-scrub', 'r-acid', 'r-recovery', 'r-etp', 'r-zld'] },
    chem: { new: ['r-tanks', 'r-storage', 'r-mix', 'r-plating', 'r-structure', 'r-pump', 'r-hx', 'r-pipe', 'r-duct', 'r-frpfab'],
            upgrade: ['r-tanks', 'r-hood', 'r-scrub', 'r-blower', 'r-pump'], equipment: ['r-tanks', 'r-storage', 'r-mix', 'r-plating', 'r-pump', 'r-hx', 'r-pipe', 'r-duct', 'r-frp', 'r-frpfab'],
            env: ['r-scrub', 'r-odour', 'r-apc', 'r-etp', 'r-zld'] },
    env: { new: ['r-etp', 'r-zld', 'env', 'r-acid', 'r-scrub', 'r-msscrub', 'r-apc', 'r-odour'], upgrade: ['r-acid', 'r-recovery', 'r-zld', 'r-scrub', 'r-blower'],
           equipment: ['r-scrub', 'r-msscrub', 'r-blower', 'r-duct', 'r-hood', 'r-recovery'], env: ['r-etp', 'r-zld', 'r-acid', 'r-scrub', 'r-msscrub', 'r-apc', 'r-odour', 'afe', 'zfe'] }
  };
  var NOTE = {
    galv: 'Kettle length is your longest member plus about 0.8 m; the zinc bill depends on surface per tonne and steel silicon. Size it in the calculator with your own profiles.',
    spin: 'Fasteners are dipped in perforated baskets and spun above a small kettle so threads stay clean. Throughput sets the number of spinners.',
    draw: 'Rod size, finished size and speed set the number of blocks; we design the die sequence with you.',
    wgalv: 'Strand count and line speed set the bath length; fumeless pickling keeps acid fume inside the tanks.',
    mig: 'Copper coating and precision layer winding decide CO₂ wire quality.',
    al: 'Aluminium needs lower reductions per pass and careful surface handling.',
    strip: 'Strip width, gauge and speed set tank length and the scrubber size.',
    chem: 'PP-H, FRP and PP-FRP built to the chemical, temperature and load.',
    env: 'We start from your waste streams: acid, rinse water, fume and sludge.'
  };
  var esc = function (s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;'); };
  var first = function (s) { var m = String(s || '').match(/^(.+?[.!?])(\s|$)/); return m ? m[1] : String(s || ''); };
  function opts(o, sel) { return Object.keys(o).map(function (k) { return '<option value="' + k + '"' + (k === sel ? ' selected' : '') + '>' + esc(o[k].n || o[k]) + '</option>'; }).join(''); }
  [].forEach.call(document.querySelectorAll('[data-finder]'), function (sec) {
    var dv = sec.getAttribute('data-finder'), box = sec.querySelector('.fd');
    var def = { hdg: 'structural', wire: 'wiredraw', rein: 'chem' }[dv] || 'structural';
    box.innerHTML = '<div class="fd-q"><label><span><i>1</i>What do you make?</span><select data-q="make">' + opts(MAKE, def) + '</select></label>' +
      '<label><span><i>2</i>What do you need?</span><select data-q="need">' + opts(NEED, 'new') + '</select></label>' +
      '<label><span><i>3</i>How much?</span><select data-q="cap"></select></label></div><div class="fd-r" aria-live="polite"></div>';
    var mk = box.querySelector('[data-q=make]'), nd = box.querySelector('[data-q=need]'), cp = box.querySelector('[data-q=cap]'), out = box.querySelector('.fd-r');
    function caps() { var c = CAP[MAKE[mk.value].cap]; cp.innerHTML = c.map(function (x, i) { return '<option value="' + x[0] + '"' + (i === 1 ? ' selected' : '') + '>' + x[1] + '</option>'; }).join(''); }
    function run() {
      var m = MAKE[mk.value], ids = (MAP[m.g][nd.value] || []).filter(function (id) { return L.items[id]; }), capRow = CAP[m.cap].filter(function (x) { return x[0] === cp.value; })[0] || CAP[m.cap][1];
      var calc = (m.g === 'galv' || m.g === 'spin') ? '<a class="pill-cta" href="calculator.html?fam=' + m.fam + '&t=' + capRow[2] + (m.g === 'spin' ? '&mode=spin' : '') + '">Size it and see the cost per tonne →</a>' : '';
      var ask = '<a class="ghost" href="#enquire" data-fd-ask="' + esc(m.n + ' · ' + NEED[nd.value] + ' · ' + capRow[1]) + '">Ask SHIVAS about this</a>';
      out.innerHTML = '<div class="fd-h"><p><b>' + ids.length + ' SHIVAS products fit.</b> ' + esc(NOTE[m.g]) + '</p><div class="fd-a">' + calc + ask + '</div></div>' +
        '<div class="fd-g' + (ids.length > 8 ? ' fd-more' : '') + '">' + ids.map(function (id, k) { var it = L.items[id], a = L.assets[it.fallbackImage] || {};
          return '<a class="fd-c" href="items/' + id + '.html"><span class="fd-f"><img src="' + esc(a.preview || '') + '" alt="" loading="lazy" decoding="async">' + (k === 0 ? '<em>Start here</em>' : '') + (it.photos ? '<i class="ph-badge">' + it.photos + ' photo' + (it.photos > 1 ? 's' : '') + '</i>' : '') + '</span><b>' + esc(it.name) + '</b><span>' + esc(first(it.description)) + '</span></a>'; }).join('') + '</div>' +
        (ids.length > 8 ? '<button type="button" class="ghost fd-all">Show all ' + ids.length + ' products</button>' : '');
    }
    mk.addEventListener('change', function () { caps(); run(); }); nd.addEventListener('change', run); cp.addEventListener('change', run);
    out.addEventListener('click', function (e) { var m = e.target.closest('.fd-all'); if (m) { out.querySelector('.fd-g').classList.remove('fd-more'); m.remove(); return; } var a = e.target.closest('[data-fd-ask]'); if (!a) return; var t = document.querySelector('#enquire textarea'); if (t && !t.value) t.value = 'Product finder: ' + a.getAttribute('data-fd-ask') + '. '; });
    caps(); run();
  });
})();
