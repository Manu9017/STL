# Builds a single-file, phone-friendly preview of the site from the artboards.
# Private preview only: not the production site described in CLAUDE.md.
import re, base64, os
HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(HERE, "..", "design", "artboards")
LOGO = os.path.join(HERE, "..", "assets", "logo")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shivas-site.html")

ROUTES = [  # key, file, hash route, page title
    ("main", "Main.dc.html", "home", "SHIVAS Technology"),
    ("wire", "WireDrawing.dc.html", "wire-drawing", "Wire drawing machines | SHIVAS"),
    ("galv", "Galvanizing.dc.html", "galvanizing", "Hot dip galvanizing plants | SHIVAS"),
    ("furnace", "Furnace.dc.html", "pulse-fired-furnaces", "Pulse-fired furnaces | SHIVAS"),
    ("about", "About.dc.html", "company", "Company and group | SHIVAS"),
    ("contact", "Contact.dc.html", "contact", "Request a quote | SHIVAS"),
]
FILE2ROUTE = {f: r for _, f, r, _ in ROUTES}

def data_uri(p):
    return "data:image/png;base64," + base64.b64encode(open(p, "rb").read()).decode()
LOGO_DARK = data_uri(os.path.join(LOGO, "shivas-logo-compact.png"))
LOGO_LIGHT = data_uri(os.path.join(LOGO, "shivas-logo-compact-light.png"))

def rewrite_links(s, route):
    def fix(m):
        href = m.group(1)
        if href.startswith(("http", "tel:", "mailto:")):
            return m.group(0)
        if href.startswith("#"):
            return f'href="#{route}.{href[1:]}"'
        f, _, sec = href.partition("#")
        r = FILE2ROUTE.get(f)
        if r is None:
            return m.group(0)
        return f'href="#{r}.{sec}"' if sec else f'href="#{r}"'
    s = re.sub(r'href="([^"]*)"', fix, s)
    s = s.replace("/_blob/7e388a42bbaaacc40b2c9ce5143a1fdf", LOGO_DARK).replace("/_blob/3dcd77c2428396d3e29bd9a804dd88f3", LOGO_LIGHT)
    return s

def is_placeholder(st):
    return "dashed" in st or ("justify-content: center" in st and "align-items: center" in st and "[" not in st and "font-size" in st)

def fluid(s):
    """Turn fixed artboard geometry into flowing layout."""
    def fix_style(m):
        st = m.group(1)
        st = st.replace("height: 100%;", "padding-block: 72px;")
        section = "padding: 0 80px" in st or "flex-shrink: 0" in st
        def h(mm):
            px = int(mm.group(1))
            return mm.group(0) if (px < 100 and not section) or is_placeholder(st) else ""
        st = re.sub(r'(?<![\w-])height: (\d+)px;\s?', h, st)
        st = st.replace("overflow: hidden; ", "")
        return f'style="{st}"'
    return re.sub(r'style="([^"]*)"', fix_style, s)

def body_of(s):
    start = s.index(">", s.index('<div style="width: ')) + 1
    end = s.rindex("</div>", 0, s.index("</x-dc>"))
    return s[start:end]

def page_parts(f):
    s = open(os.path.join(ART, f)).read()
    helmet = re.search(r"<style>(.*?)</style>", s, re.S).group(1)
    script = re.search(r'<script type="text/x-dc"[^>]*>(.*?)</script>', s, re.S).group(1)
    return s, helmet, script

main_src, HELMET_CSS, _ = page_parts("Main.dc.html")
FOOTER = re.search(r"<footer.*?</footer>", main_src, re.S).group(0)
FOOTER = fluid(rewrite_links(FOOTER, "home")).replace("<footer ", '<footer class="site-foot" ', 1)

templates, scripts = [], []
for key, f, route, title in ROUTES:
    s, _, script = page_parts(f)
    b = body_of(s)
    b = re.sub(r"<header.*?</header>\s*", "", b, count=1, flags=re.S)
    b = re.sub(r'<div aria-hidden="true" style="height: 4px.*?</div>\s*', "", b, count=1, flags=re.S)
    b = re.sub(r"<footer.*?</footer>\s*", "", b, count=1, flags=re.S)
    # sections without an inner full-height block need their own bottom padding once heights go
    def mark(m):
        sec = m.group(0)
        head = sec[: sec.index(">") + 200]
        if "height: 100%" in head:
            return sec
        return sec.replace("<section ", '<section class="pb" ', 1)
    b = re.sub(r"<section\b.*?</section>", mark, b, flags=re.S)
    if key == "galv":
        b = b.replace('<div style="display: flex; align-items: flex-end; gap: 8px; height: 200px;', '<div data-stages style="display: flex; align-items: flex-end; gap: 8px; height: 200px;', 1)
        b = b.replace('<svg viewBox="0 0 1280 30"', '<svg data-crane viewBox="0 0 1280 30"', 1)
    if key == "contact":
        b = b.replace(">Enquiry sent<", ">Preview only: not sent<")
        b = re.sub(r"An engineer from the \{\{divName\}\} division will reply within \[one working day\]\. A copy has gone to your email\.",
                   "This form is not connected yet. On the live site your enquiry will go to info@shivastechnology.com and an engineer from the {{divName}} division will reply.", b)
    b = fluid(rewrite_links(b, route))
    b = b.replace('style="padding-block: 72px; display: flex; align-items: center; justify-content: space-between; border-bottom', 'style="padding-block: 22px; display: flex; flex-wrap: wrap; gap: 8px 24px; align-items: center; justify-content: space-between; border-bottom')
    templates.append(f'<template id="t-{key}" data-route="{route}" data-title="{title}"><div class="pg">{b}</div></template>')
    scripts.append(f"COMPONENTS[{key!r}] = (function () {{\n{script.strip()}\nreturn Component;\n}})();")

NAV = [("Wire drawing", "wire-drawing"), ("Galvanizing", "galvanizing"), ("Knowledge", "galvanizing.knowledge"), ("Company", "company"), ("Contact", "contact")]
nav_links = "".join(f'<a href="#{r}" data-nav="{r.split(".")[0]}">{t}</a>' for t, r in NAV)
MENU = [("Home", "home", "Choose a division", "#0A1F4D"), ("Wire drawing", "wire-drawing", "Straight line, OTO, line equipment", "#0070AD"),
        ("Die sequence calculator", "wire-drawing.calculator", "Passes, reductions and speeds", "#0070AD"),
        ("Hot dip galvanizing", "galvanizing", "Turnkey plants and 12 systems", "#A85F00"),
        ("Pulse-fired furnaces", "pulse-fired-furnaces", "Galvanizing product page", "#A85F00"),
        ("Knowledge", "galvanizing.knowledge", "Guides for galvanizers", "#A85F00"),
        ("Company and group", "company", "Leadership, projects, group sites", "#0A1F4D")]
menu_items = "".join(f'<a href="#{r}"><i style="background:{c}"></i><span><b>{t}</b><small>{sub}</small></span></a>' for t, r, sub, c in MENU)

HTML = f"""<title>SHIVAS Technology Site</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&amp;display=swap" rel="stylesheet">
<style>
{HELMET_CSS.replace("body{margin:0;background:#F5F8FF}", "")}
:root{{--red:#E3000F;--gold:#FFB400;--blue:#0070AD;--ink:#0A1F4D;--text:#14213D;--muted:#475A78;--rule:#D3DDEE;--paper:#F5F8FF}}
html{{background:#FFFFFF}}
body{{margin:0;background:var(--paper);color:var(--text);font-family:'Archivo','Helvetica Neue',system-ui,sans-serif;font-size:16px;-webkit-text-size-adjust:100%}}
*{{box-sizing:border-box}}
h1,h2,h3{{text-wrap:balance}}
.pg{{overflow-x:hidden}}
.pg svg{{max-width:100%;height:auto}}
.pg section > div,.pg section > div > div{{min-width:0;max-width:100%}}
.pg [data-stages]{{max-width:100%}}
.pg section.pb{{padding-bottom:88px !important}}
.site-head{{position:sticky;top:env(safe-area-inset-top,0px);z-index:20;background:#FFFFFF;border-bottom:1px solid var(--rule)}}
.head-row{{height:80px;display:flex;align-items:center;justify-content:space-between;gap:24px;padding:0 80px}}
.head-row .logo img{{height:46px;width:auto;display:block}}
.desk-nav{{display:flex;align-items:center;gap:32px}}
.desk-nav a{{font-size:16px;font-weight:500;color:var(--text);padding:10px 0;border-bottom:2px solid transparent}}
.desk-nav a.on{{font-weight:600;border-bottom-color:var(--red)}}
.btn-quote{{display:inline-flex;align-items:center;min-height:48px;padding:0 22px;font-size:16px;font-weight:600;color:#FFFFFF !important;background:var(--red);border-radius:2px}}
.btn-quote:hover{{background:#C8000D}}
.stripe{{height:4px;display:flex}}.stripe span{{flex:1}}
.menu-btn{{display:none;width:48px;height:48px;border:0;background:transparent;align-items:center;justify-content:center;cursor:pointer;color:var(--ink)}}
.m-menu{{display:none}}
@media (max-width: 1100px){{.head-row{{padding:0 32px}}.desk-nav{{gap:20px}}}}
@media (max-width: 900px){{
  .head-row{{height:64px;padding:0 16px}}
  .head-row .logo img{{height:34px}}
  .desk-nav{{display:none}}
  .menu-btn{{display:flex}}
  .m-menu.open{{display:flex;flex-direction:column;position:fixed;left:0;right:0;bottom:0;top:calc(68px + env(safe-area-inset-top,0px));background:#FFFFFF;overflow-y:auto;z-index:19;padding-bottom:env(safe-area-inset-bottom,0px)}}
  .m-menu a{{display:flex;align-items:center;gap:14px;min-height:60px;padding:0 20px;border-bottom:1px solid var(--rule);color:var(--ink)}}
  .m-menu i{{width:10px;height:10px;border-radius:5px;flex-shrink:0}}
  .m-menu span{{display:flex;flex-direction:column;gap:2px}}.m-menu b{{font-size:18px}}.m-menu small{{font-size:14px;color:var(--muted)}}
  .m-menu .m-cta{{padding:20px;display:flex;flex-direction:column;gap:10px}}
  .m-menu .m-cta a{{justify-content:center;min-height:52px;border:0;font-weight:600;font-size:16px;border-radius:2px}}
  .m-menu .m-cta .q{{background:var(--red);color:#FFFFFF}}
  .m-menu .m-cta .w{{box-shadow:inset 0 0 0 1.5px var(--ink);color:var(--ink)}}
  .m-menu .m-cta .num{{justify-content:center;min-height:0;border:0;font-size:15px;color:var(--muted);user-select:all}}

  .pg section,.pg nav[aria-label="Breadcrumb"],.site-foot{{padding-left:20px !important;padding-right:20px !important}}
  .pg section.pb{{padding-bottom:56px !important}}
  .pg [style*="padding-top: 8"],.pg [style*="padding-top: 9"],.pg [style*="padding-top: 7"]{{padding-top:48px !important}}
  .pg [style*="padding-block: 72px"]{{padding-block:48px !important}}
  .pg [style*="grid-template-columns"],.site-foot [style*="grid-template-columns"]{{grid-template-columns:minmax(0,1fr) !important}}
  .pg [style*="display: flex"]{{flex-wrap:wrap}}
  .pg [style*="flex: 1;"]{{flex:1 1 100% !important}}
  .pg [style*="padding: 72px 64px 48px 80px"],.pg [style*="padding: 72px 80px 48px 64px"]{{padding:40px 20px 24px !important;gap:24px}}
  .pg [style*="margin-right: -64px"],.pg [style*="margin-left: -24px"]{{margin:0 !important}}
  .pg [style*="gap: 80px"],.pg [style*="gap: 72px"],.pg [style*="gap: 64px"],.pg [style*="gap: 56px"]{{gap:32px !important}}
  .pg h1{{font-size:36px !important;line-height:1.08 !important}}
  .pg h2{{font-size:30px !important;line-height:1.12 !important}}
  .pg h3{{font-size:21px !important}}
  .pg p{{font-size:17px !important}}
  .pg nav[aria-label="Breadcrumb"]{{height:auto !important;flex-wrap:wrap;gap:6px 20px;padding-block:12px !important}}
  .pg nav[aria-label="Breadcrumb"] > div{{flex-wrap:wrap;gap:6px 16px !important}}
  .pg nav[aria-label="Breadcrumb"] > div:last-child > span{{display:none}}
  .pg [data-stages]{{overflow-x:auto;justify-content:flex-start;flex-wrap:nowrap !important;-webkit-overflow-scrolling:touch}}
  .pg [data-stages] button{{flex:0 0 96px !important}}
  .pg [data-crane]{{display:none}}
  .pg [style*="min-height: 150px"]{{min-height:0 !important}}
  .site-foot{{height:auto !important;gap:32px;padding-top:48px !important}}
  .site-foot > div:last-child{{flex-direction:column;align-items:flex-start !important;gap:12px}}
}}
@media (prefers-reduced-motion: reduce){{html{{scroll-behavior:auto}}}}
</style>

<header class="site-head">
<div class="head-row">
<a class="logo" href="#home" aria-label="SHIVAS Technology home"><img src="{LOGO_DARK}" alt="Shivas: SHIVAS Technology Ltd" width="282" height="48"></a>
<nav class="desk-nav" aria-label="Main">{nav_links}<a class="btn-quote" href="#contact">Request a quote</a></nav>
<button class="menu-btn" type="button" aria-label="Open menu" aria-expanded="false" aria-controls="m-menu"><svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true"><path class="ln" stroke="currentColor" d="M3 7 H21 M3 12 H21 M3 17 H21"></path></svg></button>
</div>
<div class="stripe" aria-hidden="true"><span style="background:#E3000F"></span><span style="background:#FFB400"></span><span style="background:#0070AD"></span></div>
</header>
<nav id="m-menu" class="m-menu" aria-label="Menu">{menu_items}<div class="m-cta"><a class="q" href="#contact">Request a quote</a><a class="w" href="https://wa.me/919810280104">WhatsApp us</a><a class="num">+91 98102 80104 · info@shivastechnology.com</a></div></nav>

<main id="app"></main>
{FOOTER}

{''.join(templates)}

<script>
class DCLogic {{
  constructor(props) {{ this.props = props || {{}}; this.state = {{}}; }}
  setState(patch) {{ this.state = Object.assign({{}}, this.state, typeof patch === 'function' ? patch(this.state) : patch); if (this._r) this._r(); }}
  forceUpdate() {{ if (this._r) this._r(); }}
}}
const COMPONENTS = {{}};
{chr(10).join(scripts)}

(function () {{
  const app = document.getElementById('app');
  const tpls = {{}};
  document.querySelectorAll('template[data-route]').forEach(t => {{ tpls[t.dataset.route] = t; }});
  const keyOf = {{}};
  document.querySelectorAll('template[data-route]').forEach(t => {{ keyOf[t.dataset.route] = t.id.slice(2); }});
  const inst = {{}};
  let current = null;

  function lookup(path, scope) {{
    path = path.trim();
    if (path === 'true') return true; if (path === 'false') return false;
    if (/^-?\\d+(\\.\\d+)?$/.test(path)) return Number(path);
    return path.split('.').reduce((o, k) => (o == null ? undefined : o[k]), scope);
  }}
  const HOLE = /\\{{\\{{([^}}]*)\\}}\\}}/g;
  const interp = (str, scope) => str.replace(HOLE, (_, p) => {{ const v = lookup(p, scope); return v == null ? '' : String(v); }});

  function proc(node, scope) {{
    Array.from(node.childNodes).forEach(ch => {{
      if (ch.nodeType === 3) {{ if (ch.nodeValue.indexOf('{{{{') >= 0) ch.nodeValue = interp(ch.nodeValue, scope); return; }}
      if (ch.nodeType !== 1) return;
      const tag = ch.localName;
      if (tag === 'sc-for') {{
        const list = lookup(ch.getAttribute('list').replace(/[{{}}]/g, ''), scope) || [];
        const as = ch.getAttribute('as') || 'item';
        const frag = document.createDocumentFragment();
        list.forEach((it, i) => {{
          const box = document.createElement('div');
          Array.from(ch.childNodes).forEach(c => box.appendChild(c.cloneNode(true)));
          proc(box, Object.assign({{}}, scope, {{ [as]: it, $index: i }}));
          while (box.firstChild) frag.appendChild(box.firstChild);
        }});
        ch.replaceWith(frag); return;
      }}
      if (tag === 'sc-if') {{
        const v = lookup(ch.getAttribute('value').replace(/[{{}}]/g, ''), scope);
        if (!v) {{ ch.remove(); return; }}
        proc(ch, scope);
        ch.replaceWith(...Array.from(ch.childNodes)); return;
      }}
      Array.from(ch.attributes).forEach(a => {{
        if (a.value.indexOf('{{{{') < 0) return;
        const whole = a.value.match(/^\\s*\\{{\\{{([^}}]*)\\}}\\}}\\s*$/);
        if (a.name.startsWith('on') && whole) {{
          const fn = lookup(whole[1], scope);
          ch.removeAttribute(a.name);
          let ev = a.name.slice(2);
          if (ev === 'change' && (tag === 'input' || tag === 'textarea')) ev = 'input';
          if (typeof fn === 'function') ch.addEventListener(ev, fn);
          return;
        }}
        const val = interp(a.value, scope);
        ch.setAttribute(a.name, val);
        if (a.name === 'value' && 'value' in ch) ch.value = val;
      }});
      proc(ch, scope);
    }});
  }}

  function draw(route) {{
    const c = inst[route];
    const a = document.activeElement, id = a && a.id, s1 = a && a.selectionStart, s2 = a && a.selectionEnd;
    const tree = tpls[route].content.cloneNode(true);
    proc(tree, c.renderVals());
    app.replaceChildren(tree);
    if (id) {{ const el = document.getElementById(id); if (el) {{ el.focus({{ preventScroll: true }}); try {{ if (s1 != null) el.setSelectionRange(s1, s2); }} catch (e) {{}} }} }}
  }}

  function go() {{
    const h = decodeURIComponent(location.hash.slice(1));
    let [route, sec] = h.split('.');
    if (!tpls[route]) route = 'home';
    if (route !== current) {{
      if (!inst[route]) {{ const C = COMPONENTS[keyOf[route]]; inst[route] = new C({{}}); inst[route]._r = () => {{ if (current === route) draw(route); }}; }}
      current = route;
      draw(route);
      document.title = tpls[route].dataset.title;
      document.querySelectorAll('.desk-nav a[data-nav]').forEach(l => l.classList.toggle('on', l.dataset.nav === route && !(l.getAttribute('href').indexOf('.') > 0)));
    }}
    closeMenu();
    const target = sec && document.getElementById(sec);
    if (target) {{
      const off = document.querySelector('.site-head').offsetHeight + 8;
      window.scrollTo(0, target.getBoundingClientRect().top + window.scrollY - off);
    }} else window.scrollTo(0, 0);
  }}

  const btn = document.querySelector('.menu-btn'), menu = document.getElementById('m-menu');
  function closeMenu() {{ menu.classList.remove('open'); btn.setAttribute('aria-expanded', 'false'); btn.setAttribute('aria-label', 'Open menu'); }}
  btn.addEventListener('click', () => {{
    const open = !menu.classList.contains('open');
    menu.classList.toggle('open', open);
    btn.setAttribute('aria-expanded', String(open));
    btn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
  }});
  // same-hash taps (e.g. tapping "Wire drawing" while on it) still scroll to the top or section
  document.addEventListener('click', e => {{
    const a = e.target.closest && e.target.closest('a[href^="#"]');
    if (a && a.getAttribute('href') === location.hash) {{ e.preventDefault(); go(); }}
  }});
  window.addEventListener('hashchange', go);
  go();
}})();
</script>
"""
open(OUT, "w").write(HTML)
print(OUT, len(HTML))
