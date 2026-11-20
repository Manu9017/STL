"""Calculation report SHV-FUR-6700-CR (HTML) + results.json.

Structure follows the engineering-calc-report skill (BaratiLab, MIT): header block, objective, summary of
checks with margins, inputs with sources, assumptions, decisions, method & results per calc, discussion,
references, sign-off left blank for a qualified engineer.
"""
from __future__ import annotations

import datetime as dt
import html
import json
import re
from pathlib import Path

from ..basis import B, G, ROOT
from . import engine

OUT = ROOT / "out" / "calc"


def _fmt(v):
    if isinstance(v, bool):
        return str(v)
    if isinstance(v, int):
        return f"{v:,}"
    if isinstance(v, float):
        a = abs(v)
        if a >= 1000:
            return f"{v:,.0f}"
        if a >= 100:
            return f"{v:,.1f}"
        if a >= 1:
            return f"{v:,.2f}"
        return f"{v:.3f}"
    if isinstance(v, (list, tuple)):
        return ", ".join(_fmt(x) for x in v)
    return html.escape(str(v))


def md_to_html(md: str) -> str:
    """Tiny converter for the register files: headings, paragraphs, pipe tables, **bold**."""
    out, rows = [], []

    def inline(t):
        t = html.escape(t)
        t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
        t = re.sub(r"`(.+?)`", r"<code>\1</code>", t)
        return t

    def flush():
        if rows:
            head, body = rows[0], [r for r in rows[2:]]
            out.append("<div class='tw'><table><thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in head) +
                       "</tr></thead><tbody>" + "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in body) +
                       "</tbody></table></div>")
            rows.clear()

    for line in md.splitlines():
        if line.startswith("|"):
            rows.append([c.strip() for c in line.strip().strip("|").split("|")])
            continue
        flush()
        if line.startswith("# "):
            continue
        if line.startswith("## "):
            out.append(f"<h3>{inline(line[3:])}</h3>")
        elif line.strip():
            out.append(f"<p>{inline(line)}</p>")
    flush()
    return "\n".join(out)


CSS = """
:root{--bg:#F5F8FF;--card:#FFFFFF;--ink:#0A1F4D;--text:#14213D;--muted:#475A78;--rule:#D3DDEE;--red:#E3000F;
--pass:#0B7A3E;--pass-bg:#E5F5EC;--fail:#B4000C;--fail-bg:#FDE8EA;--marg:#8A5300;--marg-bg:#FFF3D6;--sup:#475A78;--sup-bg:#EEF2F8;--info:#005A87;--info-bg:#E6F6FA;
--mono:"JetBrains Mono",ui-monospace,Menlo,Consolas,monospace;--sans:"Archivo",system-ui,-apple-system,"Segoe UI",sans-serif}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0B1220;--card:#121B2E;--ink:#EEF3FF;--text:#DCE4F5;--muted:#9FB0D0;--rule:#24324E;
--pass:#5CD691;--pass-bg:#10291D;--fail:#FF7A84;--fail-bg:#33141A;--marg:#FFC861;--marg-bg:#33270C;--sup:#9FB0D0;--sup-bg:#1A2438;--info:#6EC6F0;--info-bg:#10283A}}
:root[data-theme="dark"]{--bg:#0B1220;--card:#121B2E;--ink:#EEF3FF;--text:#DCE4F5;--muted:#9FB0D0;--rule:#24324E;
--pass:#5CD691;--pass-bg:#10291D;--fail:#FF7A84;--fail-bg:#33141A;--marg:#FFC861;--marg-bg:#33270C;--sup:#9FB0D0;--sup-bg:#1A2438;--info:#6EC6F0;--info-bg:#10283A}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:15px/1.55 var(--sans)}
.wrap{max-width:1180px;margin:0 auto;padding:24px 16px 80px}
header.doc{display:grid;grid-template-columns:1fr auto;gap:12px 24px;border-bottom:4px solid var(--red);padding-bottom:16px;margin-bottom:24px}
header.doc h1{margin:0;font-size:28px;line-height:1.15;color:var(--ink);font-stretch:112%;font-weight:800}
header.doc .sub{color:var(--muted)}
dl.meta{display:grid;grid-template-columns:auto auto;gap:2px 14px;margin:0;font-size:13px}
dl.meta dt{color:var(--muted)}dl.meta dd{margin:0;font-family:var(--mono)}
h2{color:var(--ink);font-size:22px;margin:40px 0 10px;font-stretch:108%}
h3{color:var(--ink);font-size:17px;margin:22px 0 8px}
p{max-width:80ch}
.card{background:var(--card);border:1px solid var(--rule);padding:16px 18px;margin:12px 0}
.tw{overflow-x:auto;margin:8px 0}
table{border-collapse:collapse;width:100%;font-size:13.5px}
th{text-align:left;font-weight:600;color:var(--muted);border-bottom:2px solid var(--rule);padding:6px 8px;white-space:nowrap}
td{border-bottom:1px solid var(--rule);padding:6px 8px;vertical-align:top}
td.n{font-family:var(--mono);text-align:right;white-space:nowrap}
td:first-child{white-space:nowrap}
.st{font:600 11.5px var(--mono);padding:2px 7px;border-radius:2px;white-space:nowrap}
.PASS{color:var(--pass);background:var(--pass-bg)}.FAIL{color:var(--fail);background:var(--fail-bg)}
.MARGINAL{color:var(--marg);background:var(--marg-bg)}.SUPERSEDED{color:var(--sup);background:var(--sup-bg)}.INFO{color:var(--info);background:var(--info-bg)}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px;margin:14px 0}
.kpi{background:var(--card);border:1px solid var(--rule);padding:12px 14px}
.kpi b{display:block;font:700 22px var(--mono);color:var(--ink)}.kpi span{font-size:12.5px;color:var(--muted)}
ul.m{margin:6px 0;padding-left:20px}ul.m li{margin:3px 0}
.note{border-left:3px solid var(--red);padding:6px 12px;background:var(--card);margin:8px 0}
code{font-family:var(--mono);font-size:12.5px}
.sign{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.sign div{border:1px solid var(--rule);padding:12px;min-height:90px;background:var(--card)}
.sign b{display:block;color:var(--muted);font-size:12px;font-weight:600}
.legend span{margin-right:10px}
@media (max-width:700px){header.doc{grid-template-columns:1fr}.sign{grid-template-columns:1fr}}
"""


def build():
    calcs = engine.run_all()
    OUT.mkdir(parents=True, exist_ok=True)
    allc = [(c["id"], ch) for c in calcs for ch in c["checks"]]
    counts = {}
    for _, ch in allc:
        counts[ch["status"]] = counts.get(ch["status"], 0) + 1

    def status_cell(ch):
        return f"<span class='st {ch['status']}'>{ch['status']}</span>"

    def lim(ch):
        if ch["limit"] is None:
            return "—"
        return ("≤ " if ch["kind"] == "max" else "≥ ") + _fmt(ch["limit"])

    def mg(ch):
        m = engine.margin(ch["value"], ch["limit"], ch["kind"]) if isinstance(ch["value"], (int, float)) else None
        return "—" if m is None else f"{100 * m:+.0f} %"

    summary_rows = "".join(
        f"<tr><td>{cid}</td><td>{html.escape(ch['name'])}</td><td class='n'>{_fmt(ch['value'])}</td><td>{html.escape(ch['unit'])}</td>"
        f"<td class='n'>{lim(ch)}</td><td class='n'>{mg(ch)}</td><td>{status_cell(ch)}</td><td>{html.escape(ch['note'])}</td></tr>"
        for cid, ch in allc if ch["status"] != "INFO" or True)

    by = {c["id"]: c for c in calcs}
    c02, c14, c01, c12 = by["C-02"], by["C-14"], by["C-01"], by["C-12"]
    kp = [(f"{c14['results']['rows'][0][2]:,.0f} kW", "fired at 6.0 t/h (1,172 kW installed)"),
          (f"{c02['results']['cases'][list(c02['results']['cases'])[2]]['tph_max']:.2f} t/h", "capacity at 25 kW/m² (case C)"),
          (f"{c14['results']['rows'][0][4]:.1f} Nm³/t", "gas per tonne at 6.0 t/h"),
          (f"{100 * c14['results']['rows'][0][1] / c14['results']['rows'][0][2]:.0f} %", "furnace efficiency at 6.0 t/h"),
          (f"{by['C-04']['results']['wall W3 1000']['T'][-2]:.0f} °C", "casing skin at 1,000 °C hot face"),
          (f"{c12['results']['zinc_t']:.1f} t", "zinc in the kettle")]
    kpis = "".join(f"<div class='kpi'><b>{a}</b><span>{b}</span></div>" for a, b in kp)

    inputs = "".join(
        f"<tr><td><code>{html.escape(p)}</code></td><td>{_fmt(l['value'])}</td><td>{html.escape(str(l['unit']))}</td>"
        f"<td>{html.escape(B.sources[l['src']].split(' (')[0])}</td><td><span class='st {dict(C='PASS', D='INFO', A='MARGINAL', O='FAIL')[l['status']]}'>"
        f"{dict(C='confirmed', D='decided', A='assumed', O='open')[l['status']]}</span></td><td>{html.escape(l['note'])}</td></tr>"
        for p, l in B.leaves.items())

    def results_block(c):
        r = c["results"]
        parts = []
        if c["id"] == "C-01":
            hdr = "<tr><th>Case</th><th>λ</th><th>Air Nm³/h</th><th>Air m³/h @35 °C</th><th>Flue Nm³/h</th><th>CO₂ % wet</th><th>H₂O % wet</th><th>O₂ % dry</th><th>T_ad °C</th><th>Avail. heat</th></tr>"
            body = "".join(f"<tr><td>{html.escape(k)}</td><td class='n'>{v['lambda']:.3f}</td><td class='n'>{v['air_Nm3h']:,.0f}</td><td class='n'>{v['air_m3h_amb']:,.0f}</td>"
                           f"<td class='n'>{v['flue_Nm3h']:,.0f}</td><td class='n'>{v['CO2_wet']:.1f}</td><td class='n'>{v['H2O_wet']:.1f}</td><td class='n'>{v['O2_dry']:.1f}</td>"
                           f"<td class='n'>{v['T_ad']:,.0f}</td><td class='n'>{100 * v['AH']:.1f} %</td></tr>" for k, v in r["cases"].items())
            parts.append(f"<div class='tw'><table>{hdr}{body}</table></div>")
        if c["id"] == "C-02":
            hdr = "<tr><th>Case</th><th>Surface loss kW</th><th>Max net kW</th><th>Capacity t/h</th><th>Flux @ 6.0 t/h</th><th>Flux @ 6.7 t/h</th></tr>"
            body = "".join(f"<tr><td>{html.escape(k)}</td><td class='n'>{v['surf']:.1f}</td><td class='n'>{v['P_net_max']:.0f}</td><td class='n'>{v['tph_max']:.2f}</td>"
                           f"<td class='n'>{v['flux_6_0']:.1f}</td><td class='n'>{v['flux_6_7']:.1f}</td></tr>" for k, v in r["cases"].items())
            parts.append(f"<div class='tw'><table>{hdr}{body}</table></div>")
        if c["id"] in ("C-05", "C-09"):
            rows = r["items"] if c["id"] == "C-05" else r["rows"]
            body = "".join(f"<tr><td>{html.escape(n)}</td><td class='n'>{'—' if v is None else f'{v:.1f}'}</td><td class='n'>{d:.1f}</td></tr>" for n, v, d in rows)
            tot = r["total_mmWC"] if c["id"] == "C-05" else r["total"]
            parts.append(f"<div class='tw'><table><tr><th>Element</th><th>Velocity m/s</th><th>Loss mmWC</th></tr>{body}"
                         f"<tr><td><b>Total</b></td><td></td><td class='n'><b>{tot:.1f}</b></td></tr></table></div>")
        if c["id"] == "C-06":
            body = "".join(f"<tr><td>{html.escape(n)}</td><td class='n'>{v:.1f}</td><td class='n'>{d:.2f}</td></tr>" for n, v, d, _l in r["rows"])
            parts.append(f"<div class='tw'><table><tr><th>Run</th><th>Velocity m/s</th><th>Loss mbar</th></tr>{body}</table></div>")
        if c["id"] == "C-04":
            keys = [k for k in r if isinstance(r[k], dict) and "q" in r[k] and "T" in r[k] and len(r[k]["T"]) > 1]
            body = "".join(f"<tr><td>{html.escape(k)}</td><td class='n'>{r[k]['q']:,.0f}</td><td class='n'>{' → '.join(f'{t:.0f}' for t in r[k]['T'])}</td></tr>" for k in keys)
            parts.append(f"<div class='tw'><table><tr><th>Build-up</th><th>q W/m²</th><th>Node temperatures °C (hot → cold)</th></tr>{body}</table></div>")
        if c["id"] == "C-10":
            body = "".join(f"<tr><td>{html.escape(n)}</td><td class='n'>{q:,.0f}</td><td>{u}</td><td>{html.escape(nt)}</td></tr>" for n, q, u, nt in r["rows"])
            parts.append(f"<div class='tw'><table><tr><th>Item</th><th>Qty</th><th>Unit</th><th>Basis</th></tr>{body}</table></div>")
        if c["id"] == "C-11":
            body = "".join(f"<tr><td>{html.escape(n)}</td><td class='n'>{a:.2f}</td><td class='n'>{s_:.2f}</td><td class='n'>{cs:.2f}</td><td class='n'>{m:.1f}</td></tr>" for n, a, s_, cs, m in r["rows"])
            parts.append(f"<div class='tw'><table><tr><th>Fan</th><th>Air kW</th><th>Shaft kW</th><th>Cold start kW</th><th>Motor kW</th></tr>{body}</table></div>")
        if c["id"] == "C-14":
            body = "".join(f"<tr><td class='n'>{t:.1f}</td><td class='n'>{n:.0f}</td><td class='n'>{f:.0f}</td><td class='n'>{g:.1f}</td><td class='n'>{gt:.2f}</td><td class='n'>{ft:.0f}</td></tr>" for t, n, f, g, gt, ft in r["rows"])
            parts.append(f"<div class='tw'><table><tr><th>t/h</th><th>Net kW</th><th>Fired kW</th><th>Gas Nm³/h</th><th>Nm³/t</th><th>kWh/t fired</th></tr>{body}</table></div>")
        return "".join(parts)

    sections = []
    for c in calcs:
        checks = "".join(f"<tr><td>{html.escape(ch['name'])}</td><td class='n'>{_fmt(ch['value'])}</td><td>{html.escape(ch['unit'])}</td>"
                         f"<td class='n'>{lim(ch)}</td><td>{status_cell(ch)}</td><td>{html.escape(ch['note'])}</td></tr>" for ch in c["checks"])
        sections.append(f"""<section id="{c['id']}"><h2>{c['id']} · {html.escape(c['title'])}</h2>
<div class="card"><b>Method</b><ul class="m">{''.join(f'<li>{html.escape(m)}</li>' for m in c['method'])}</ul></div>
{results_block(c)}
<div class="tw"><table><tr><th>Check</th><th>Value</th><th>Unit</th><th>Limit</th><th>Status</th><th>Note</th></tr>{checks}</table></div>
{''.join(f'<p class="note">{html.escape(n)}</p>' for n in c['notes'])}</section>""")

    dec = md_to_html((ROOT / "basis" / "decision_register.md").read_text())
    opn = md_to_html((ROOT / "basis" / "open_items.md").read_text())
    legend = ("<p class='legend'><span class='st PASS'>PASS</span> meets the limit · <span class='st MARGINAL'>MARGINAL</span> within 5 % · "
              "<span class='st FAIL'>FAIL</span> · <span class='st SUPERSEDED'>SUPERSEDED</span> a source design as drawn fails; this design "
              "changes it (see the decision noted) · <span class='st INFO'>INFO</span> a result, no limit</p>")
    toc = " · ".join(f"<a href='#{c['id']}'>{c['id']}</a>" for c in calcs)
    doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SHV-FUR-6700 calculations</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,400..800&family=JetBrains+Mono:wght@400;600&display=swap">
<style>{CSS}</style></head><body><div class="wrap">
<header class="doc"><div><div class="sub">SHIVAS TECHNOLOGY LTD · Hot dip galvanizing division</div>
<h1>Calculation report — HV pulse-fired furnace, kettle 6,700 × 1,250 × 1,310, and 4-position dryer</h1>
<div class="sub">One furnace, one dryer, one heat-recovery loop, one stack</div></div>
<dl class="meta"><dt>Document</dt><dd>SHV-FUR-6700-CR</dd><dt>Revision</dt><dd>A</dd><dt>Date</dt><dd>{B.meta['date']}</dd>
<dt>Basis</dt><dd>SHV-FUR-6700-DB Rev A</dd><dt>Prepared</dt><dd>Claude Code (draft)</dd><dt>Checked</dt><dd>—</dd><dt>Approved</dt><dd>—</dd></dl></header>

<h2>Objective</h2>
<p>Show that the furnace, its combustion system and the dryer heat-recovery loop, as modelled in SHV-FUR-6700 Rev A, meet the design limits: kettle wall flux, casing and concrete temperatures, fan and blower duties, gas and air pressures, kettle support stresses, and stack velocity. Where the earlier SHIVAS documents do not meet a limit, the check is shown against the earlier design (<i>superseded</i>) together with the change this design makes.</p>
<div class="kpis">{kpis}</div>

<h2>Summary of checks</h2>{legend}
<p>{' · '.join(f"<span class='st {k}'>{k}</span> {v}" for k, v in sorted(counts.items()))}</p>
<div class="tw"><table><thead><tr><th>Calc</th><th>Check</th><th>Value</th><th>Unit</th><th>Limit</th><th>Margin</th><th>Status</th><th>Note</th></tr></thead><tbody>{summary_rows}</tbody></table></div>

<h2>Decisions made in this design</h2>{dec}
<h2>Open items and assumptions</h2>{opn}

<h2>Calculations</h2><p>{toc}</p>
{''.join(sections)}

<h2>Inputs (design basis, {len(B.leaves)} entries)</h2>
<p>Every value the model and the calculations use comes from <code>basis/design_basis.yaml</code>. Status: confirmed in a SHIVAS source document, decided in this design, assumed, or open.</p>
<div class="tw"><table><thead><tr><th>Key</th><th>Value</th><th>Unit</th><th>Source</th><th>Status</th><th>Note</th></tr></thead><tbody>{inputs}</tbody></table></div>

<h2>References</h2>
<ul class="m">{''.join(f'<li><b>{k}</b>: {html.escape(v)}</li>' for k, v in B.sources.items())}
<li>Cantera 3.2, GRI-Mech 3.0 mechanism (combustion thermochemistry).</li>
<li>CoolProp 8 (air properties). <code>fluids</code> 1.3 and <code>ht</code> (C. Bell): Colebrook friction factor, Crane/Rennels bend K.</li>
<li>Idelchik, Handbook of Hydraulic Resistance (perforated plates). ACI 349 Appendix E (concrete temperature limits). IS 800 (steel at temperature).</li>
<li>Method conventions: BaratiLab mechanical-engineering-skills (MIT): engineering-calc-report, thermal-fluids-calc, design-review-package.</li></ul>

<h2>Sign-off</h2>
<p>These figures were produced by code (<code>shivas_furnace/calc/engine.py</code>). They have not been checked by a qualified engineer.</p>
<div class="sign"><div><b>Prepared</b>Claude Code, {dt.date.today().isoformat()} (draft)</div><div><b>Checked</b></div><div><b>Approved</b></div></div>
</div></body></html>"""
    (OUT / "SHV-FUR-6700-CR.html").write_text(doc)

    def clean(o):
        if isinstance(o, dict):
            return {str(k): clean(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)):
            return [clean(v) for v in o]
        if isinstance(o, float):
            return round(o, 4)
        return o
    (OUT / "results.json").write_text(json.dumps({"basis_rev": B.meta["rev"], "calcs": clean(calcs), "counts": counts}, indent=1, default=str))
    return counts


if __name__ == "__main__":
    print(build())
