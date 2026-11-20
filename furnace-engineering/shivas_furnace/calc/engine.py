"""SHV-FUR-6700 engineering calculations.

Each calc returns a dict: {id, title, method, inputs, steps, results, checks, notes}.
Checks: {name, value, unit, limit, kind ('max'|'min'|'info'), status}. Status is computed, never typed.

Libraries:  Cantera (GRI-Mech 3.0) for combustion thermochemistry, CoolProp for air properties,
`fluids` (C. Bell) for friction factors and fitting K-values. Everything else is closed-form.
"""
from __future__ import annotations

import math

import cantera as ct
import fluids
from CoolProp.CoolProp import PropsSI
from fluids.fittings import bend_rounded, contraction_sharp, diffuser_conical, entrance_sharp, exit_normal

from ..basis import B, G

SIGMA = 5.670374419e-8
G0 = 9.80665
VM = 0.022414          # Nm3/mol at 0 degC, 1 atm
P_ATM = 101325.0
MMWC = 9.80665         # Pa per mmWC
T_AMB = B.v("process.ambient")


def _status(value, limit, kind):
    if kind == "info" or limit is None:
        return "INFO"
    ok = value <= limit if kind == "max" else value >= limit
    if ok:
        return "PASS"
    over = (value / limit - 1) if kind == "max" else (limit / value - 1)
    return "MARGINAL" if over <= 0.05 else "FAIL"


def check(name, value, unit, limit=None, kind="info", note="", ref=False):
    """ref=True: the check evaluates a superseded source design (Rev H / SH-INS as drawn). Its result is
    evidence for a decision in this design, not a result of this design."""
    st = _status(value, limit, kind)
    if ref and st in ("FAIL", "MARGINAL"):
        st = "SUPERSEDED"
    return {"name": name, "value": value, "unit": unit, "limit": limit, "kind": kind,
            "status": st, "note": note, "ref": ref}


def margin(value, limit, kind):
    if limit in (None, 0) or kind == "info":
        return None
    return (limit / value - 1) if kind == "max" else (value / limit - 1)


# =========================================================================== C-01 combustion
GAS = ct.Solution("gri30.yaml")
LHV_MOL = None


def _h_mix(X: dict, T_C: float) -> float:
    """Molar enthalpy J/mol of composition X at T (1 atm), absolute (incl. formation)."""
    GAS.TPX = T_C + 273.15, P_ATM, X
    return GAS.enthalpy_mole / 1000.0


def lhv_methane():
    """LHV J/mol from Cantera: H(CH4 + 2 O2 at 25 C) - H(CO2 + 2 H2O(g) at 25 C)."""
    hr = _h_mix({"CH4": 1}, 25) + 2 * _h_mix({"O2": 1}, 25)
    hp = _h_mix({"CO2": 1}, 25) + 2 * _h_mix({"H2O": 1}, 25)
    return hr - hp


def products(lam):
    """Complete combustion of 1 mol CH4 with lam x stoichiometric dry air (O2 + 3.76 N2)."""
    o2 = 2 * lam
    n2 = 3.76 * o2
    return {"CO2": 1.0, "H2O": 2.0, "N2": n2, "O2": o2 - 2.0}


def c01_combustion():
    global LHV_MOL
    LHV_MOL = lhv_methane()
    lhv_kwh = LHV_MOL / VM / 3.6e6
    Q_fired = B.v("process.fired_duty")                      # kW
    gas = Q_fired * 3600 / (B.v("process.gas_lhv") * 1000) * 1000 / 1000   # Nm3/h at Rev H LHV
    gas = Q_fired / B.v("process.gas_lhv")                   # Nm3/h
    stoich_air = 2 * 4.76                                    # Nm3 air / Nm3 CH4
    lam_revH = B.v("process.air_flow_rev_h") / (gas * stoich_air)
    lam_d = 1 + B.v("process.excess_air_design") / 100
    rows = {}
    for tag, lam in (("Rev H air (λ=%.3f)" % lam_revH, lam_revH), ("design λ=%.3f" % lam_d, lam_d), ("λ=1.15", 1.15)):
        P = products(lam)
        n_p = sum(P.values())
        air = gas * stoich_air * lam
        flue = gas * n_p
        wet = {k: 100 * v / n_p for k, v in P.items()}
        dry_o2 = 100 * P["O2"] / (n_p - P["H2O"])
        # adiabatic flame temperature, reactants at ambient, HP equilibrium
        X_r = {"CH4": 1.0, "O2": 2 * lam, "N2": 3.76 * 2 * lam}
        GAS.TPX = T_AMB + 273.15, P_ATM, X_r
        GAS.equilibrate("HP")
        T_ad = GAS.T - 273.15
        # available heat with flue leaving at flue_temp (complete combustion)
        H_r = _h_mix({"CH4": 1}, T_AMB) + 2 * lam * _h_mix({"O2": 1}, T_AMB) + 3.76 * 2 * lam * _h_mix({"N2": 1}, T_AMB)
        Tf = B.v("process.flue_temp")
        H_p = sum(n * _h_mix({sp: 1}, Tf) for sp, n in P.items())
        AH = (H_r - H_p) / LHV_MOL
        rows[tag] = {"lambda": lam, "air_Nm3h": air, "air_m3h_amb": air * (T_AMB + 273.15) / 273.15,
                     "flue_Nm3h": flue, "CO2_wet": wet["CO2"], "H2O_wet": wet["H2O"], "O2_wet": wet["O2"],
                     "O2_dry": dry_o2, "T_ad": T_ad, "AH": AH}
    d = rows["design λ=%.3f" % lam_d]
    blower_m3h = 1400.0
    blower_Nm3h = blower_m3h * 273.15 / (T_AMB + 273.15)
    lam_max_full = blower_Nm3h / (gas * stoich_air)
    Q_at_design_lam = blower_Nm3h / (stoich_air * lam_d) * B.v("process.gas_lhv")
    checks = [
        check("Cantera LHV of methane", lhv_kwh, "kWh/Nm3", None, "info", "Rev H basis 9.9"),
        check("Gas at full fire", gas, "Nm3/h", None, "info", "Rev H 118"),
        check("Rev H air ratio λ (as drawn)", lam_revH, "-", 1.05, "min", "Rev H air is almost stoichiometric; design uses λ 1.125", ref=True),
        check("Design air at full fire", d["air_m3h_amb"], "m3/h @35°C", blower_m3h, "max", "MBI-4040 rated 1,400 m3/h"),
        check("Max λ blower can give at 1,172 kW", lam_max_full, "-", lam_d, "min"),
        check("Max firing rate at design λ", Q_at_design_lam, "kW", None, "info"),
        check("Adiabatic flame temperature (design λ)", d["T_ad"], "degC", None, "info"),
        check("Available heat at 800 °C flue", 100 * d["AH"], "%", None, "info"),
        check("Flue at design λ", d["flue_Nm3h"], "Nm3/h", None, "info", "Rev H 1,296"),
    ]
    return {"id": "C-01", "title": "Combustion: air, flue and available heat (Cantera GRI-Mech 3.0)",
            "method": ["Fuel taken as methane, which reproduces the Rev H LHV of 9.9 kWh/Nm3. Dry air O2 + 3.76 N2.",
                       "Stoichiometric air = 2 × 4.76 = 9.52 Nm3/Nm3. Air = Q_fired / LHV × 9.52 × λ.",
                       "Adiabatic flame temperature: HP equilibrium of the reactants at 35 °C (Cantera).",
                       "Available heat AH = [H_reactants(35 °C) − H_products(800 °C)] / LHV, complete combustion."],
            "results": {"LHV_kWh_Nm3": lhv_kwh, "gas_Nm3h": gas, "lambda_revH": lam_revH, "cases": rows,
                        "blower_Nm3h": blower_Nm3h, "lam_max_full": lam_max_full, "Q_max_design_lam": Q_at_design_lam},
            "checks": checks,
            "notes": ["Rev H's 1,132 Nm3/h of air is λ ≈ 1.01 at 1,172 kW. Pulse-fired HV burners are normally set at "
                      "10–15 % excess air, so full-fire air is ≈1,264 Nm3/h = ≈1,426 m3/h at 35 °C, just above the "
                      "MBI-4040's 1,400 m3/h. Confirm the blower curve basis (actual vs normal m3/h) with Mittal.",
                      "At design λ the blower supports ≈%.0f kW fired, which is above the ≈%s kW needed for sustained "
                      "production (C-02), so the limit only bites at full fire on heat-up." % (Q_at_design_lam, "870")]}


# =========================================================================== C-02 heat balance / capacity
def c02_capacity(c01):
    cp_steel = 0.52      # kJ/kg K mean 30-455 (Rev H validation)
    T_b, T_in = B.v("process.bath_temp"), B.v("process.steel_in_temp")
    jig = 0.12           # EF jig_fraction
    pickup = 0.05        # EF zinc_pickup t Zn / t steel
    zn_make = 0.39 * (419.5 - T_in) + 112 + 0.52 * (T_b - 419.5)      # kJ/kg zinc (EF MAT)
    q_steel = cp_steel * (T_b - T_in) / 3.6                           # kWh/t
    q_t = q_steel * (1 + jig) + pickup * zn_make / 3.6                 # kWh/t process
    A_bath = G.kLi * G.kWi / 1e6
    Tb, Ta = T_b + 273.15, T_AMB + 273.15
    q_surf = 0.40 * SIGMA * (Tb ** 4 - Ta ** 4) + 4.5 * (T_b - T_AMB)
    P_surf_open = q_surf * A_bath / 1000
    hz = B.v("kettle.zinc_depth")
    A_side = 2 * (G.kLi + G.kWi) * hz / 1e6                           # Rev H 18.44 m2
    A_base = G.kLo * G.kWo / 1e6
    q_lim = B.v("process.wall_flux_limit")
    # three operating cases
    cases = {
        "A  Rev H basis: sides only, cover open": {"surf": P_surf_open, "base_share": 0.0},
        "B  sides only, enclosure covers closed between dips (surface loss ÷ 2)": {"surf": 0.5 * P_surf_open, "base_share": 0.0},
        "C  suspended kettle: hearth carries 10 % (D-01), covers managed": {"surf": 0.5 * P_surf_open, "base_share": 0.10},
    }
    for c in cases.values():
        P_wall = q_lim * A_side / (1 - c["base_share"])
        c["P_net_max"] = P_wall
        c["tph_max"] = (P_wall - c["surf"]) / q_t
        c["flux_6_0"] = (6.0 * q_t + c["surf"]) * (1 - c["base_share"]) / A_side
        c["flux_6_7"] = (6.7 * q_t + c["surf"]) * (1 - c["base_share"]) / A_side
    kA, kB, kC = list(cases)
    eta_RevH = B.v("process.net_duty") / B.v("process.fired_duty")
    checks = [
        check("Process heat per tonne", q_t, "kWh/t", None, "info", "steel + 12 % jigs + zinc make-up"),
        check("Bath surface loss, cover open", P_surf_open, "kW", None, "info"),
        check("Rev H 626 kW on the side walls", B.v("process.net_duty") / A_side, "kW/m2", q_lim, "max", "Rev H validation finding", ref=True),
        check("Case A: capacity at 25 kW/m²", cases[kA]["tph_max"], "t/h", 6.0, "min", "Rev H convention, cover open", ref=True),
        check("Case B: flux at 6.0 t/h", cases[kB]["flux_6_0"], "kW/m2", q_lim, "max", "Rev K lower production figure"),
        check("Case B: capacity at 25 kW/m²", cases[kB]["tph_max"], "t/h", 6.0, "min"),
        check("Case C: flux at 6.7 t/h", cases[kC]["flux_6_7"], "kW/m2", q_lim, "max", "Rev K upper production figure"),
        check("Case C: capacity at 25 kW/m²", cases[kC]["tph_max"], "t/h", 6.7, "min"),
        check("Rev H furnace efficiency (net/fired)", 100 * eta_RevH, "%", None, "info"),
    ]
    return {"id": "C-02", "title": "Heat balance, kettle wall flux and production capacity",
            "method": ["q_process = cp·(T_bath − T_in)·(1 + jig) + pickup·(cp_s·(419.5 − T_in) + L_f + cp_l·(T_bath − 419.5))",
                       "cp = 0.52 kJ/kg K (mean 30–455 °C, Rev H validation); jig fraction 0.12; zinc pickup 0.05 t/t (STL-EF basis).",
                       "Surface loss = [0.40 σ (T_b⁴ − T_a⁴) + 4.5 (T_b − T_a)] × bath area 6.7 × 1.25 m².",
                       "Side-wall flux = side share × net / 2(L+W)·h_zinc on inside dimensions (Rev H convention, 18.44 m²)."],
            "results": {"q_t": q_t, "P_surf_open": P_surf_open, "A_side": A_side, "A_base": A_base, "cases": cases,
                        "eta_RevH": eta_RevH, "net_6_0": 6.0 * q_t + 0.5 * P_surf_open, "net_6_7": 6.7 * q_t + 0.5 * P_surf_open},
            "checks": checks,
            "notes": ["The kettle side walls, not the burners, set production. With the Rev H convention (sides only, cover "
                      "open) the 25 kW/m² ceiling allows ≈%.1f t/h. Keeping the enclosure covers shut between dips gives "
                      "≈%.1f t/h, and with the suspended kettle's hearth taking ≈10 %% of the heat ≈%.1f t/h, which "
                      "brackets Rev K's 6.0–6.7 t/h." % (cases[kA]["tph_max"], cases[kB]["tph_max"], cases[kC]["tph_max"]),
                      "Firing 1,172 kW continuously would put ≈34 kW/m² on the walls (Rev H finding). The PLC caps the pulse "
                      "duty to the flux limit through the zinc and chamber thermocouples; full fire is for heat-up and recovery."]}


# =========================================================================== C-04 lining conduction
# k(T) = a + b T  (W/m K, T in degC mean).  REF-01/02/04 from STL-EF Rev D; 64 kg/m3 fitted to typical
# 1260-grade blanket data (0.09 @ 260, 0.24 @ 816 degC) - replace with the supplier's sheet (A-03).
MATS = {
    "module128": (0.055, 0.000145, "Ceramic fibre module 128 kg/m3, 1430 grade (STL-EF REF-01)"),
    "blanket96": (0.048, 0.00016, "Ceramic fibre blanket 96 kg/m3, 1260 grade (STL-EF REF-02)"),
    "blanket64": (0.020, 0.00027, "Ceramic fibre blanket 64 kg/m3, 1260 grade (typical data, A-03)"),
    "casi245":   (0.062, 0.00007, "Calcium silicate board 245 kg/m3 (STL-EF REF-04)"),
    "microporous": (0.021, 0.000011, "Microporous board 320 kg/m3 (STL-EF REF-03)"),
    "hdboard":   (0.060, 0.00012, "HD ceramic fibre board ~300 kg/m3 (assumed, A-04)"),
    "ifb":       (0.14, 0.00018, "Insulating firebrick IS 8, ~800 kg/m3 (typical)"),
    "steel":     (45.0, 0.0, "Carbon steel"),
    "concrete":  (1.7, 0.0, "RCC"),
    "soil":      (1.2, 0.0, "Soil, moist (assumed)"),
    "fibreboard": (0.045, 0.00012, "Ceramic fibre board 260 kg/m3 (typical)"),
}


def h_out_free(Ts, Ta=T_AMB, eps=0.85, vertical=True):
    dT = max(Ts - Ta, 0.1)
    hc = 1.42 * (dT / 1.2) ** 0.25 if vertical else 1.52 * dT ** (1 / 3)
    hr = eps * SIGMA * ((Ts + 273.15) ** 4 - (Ta + 273.15) ** 4) / dT
    return hc + hr


def wall_1d(T_hot, layers, outside="free", T_amb=T_AMB, h_fixed=None, sink=None, eps=0.85):
    """Steady 1-D through [(mat, t_mm)...]. outside: 'free' (convection+radiation), 'fixed' h, or 'sink'
    (layers continue into a fixed-temperature sink, given via `sink`=(T_sink)). Returns node temps."""
    n = len(layers)
    T = [T_hot - (T_hot - T_amb) * i / (n + 1) for i in range(n + 2)]
    q = 0.0
    for _ in range(500):
        R = []
        for i, (m, t) in enumerate(layers):
            a, b, _d = MATS[m]
            k = a + b * 0.5 * (T[i] + T[i + 1])
            R.append(t / 1000 / k)
        if outside == "free":
            Rout = 1 / h_out_free(T[n], T_amb, eps)
        elif outside == "fixed":
            Rout = 1 / h_fixed
        else:
            Rout = 0.0
        Tend = sink if outside == "sink" else T_amb
        q = (T_hot - Tend) / (sum(R) + Rout)
        Tn = [T_hot]
        for r in R:
            Tn.append(Tn[-1] - q * r)
        Tn.append(Tend)
        if max(abs(a - b) for a, b in zip(T, Tn)) < 1e-4:
            T = Tn
            break
        T = [0.5 * (a + b) for a, b in zip(T, Tn)]
    return {"q": q, "T": T}


def duct_in_trench(T_gas, layers, T_air=45.0, eps=0.85, h_c=4.0, P_duct=3.45, P_tr=4.52, R_ground=1.6):
    """Lined duct in a vented trench. Duct skin loses heat by convection to trench air and radiation to the RCC;
    the RCC takes that radiation and gives it to the air (h_c) and the ground (R_ground m2K/W)."""
    Tw = T_air + 10
    for _ in range(300):
        def h_outer(Ts):
            hr = eps * SIGMA * ((Ts + 273.15) ** 4 - (Tw + 273.15) ** 4) / max(Ts - Tw, 0.1)
            return h_c + hr
        # skin by 1-D with an effective sink temperature
        Ts = T_air + 30
        for _ in range(200):
            h = h_outer(Ts)
            rad_share = (h - h_c) / h
            T_sink = rad_share * Tw + (1 - rad_share) * T_air
            r = wall_1d(T_gas, layers, outside="fixed", h_fixed=h, T_amb=T_sink)
            Tn = r["T"][-2]
            if abs(Tn - Ts) < 0.01:
                break
            Ts = 0.5 * (Ts + Tn)
        q_rad_per_m = eps * SIGMA * ((Ts + 273.15) ** 4 - (Tw + 273.15) ** 4) * P_duct
        # RCC balance per metre: q_rad = (h_c (Tw - T_air) + (Tw - 30)/R_ground) * P_tr
        Twn = (q_rad_per_m / P_tr + h_c * T_air + 30 / R_ground) / (h_c + 1 / R_ground)
        if abs(Twn - Tw) < 0.01:
            break
        Tw = 0.5 * (Tw + Twn)
    return {"T_skin": Ts, "T_rcc": Tw, "q_skin": r["q"], "T": r["T"]}


def c04_linings():
    res = {}
    W1 = [("module128", 200), ("blanket96", 50), ("steel", 6)]                       # all-fibre, as SH-INS / Rev K wording
    W3 = [("module128", 175), ("microporous", 50), ("casi245", 25), ("steel", 6)]     # D-05 adopted
    for Th in (900, 1000, 1100):
        res[f"wall W1 {Th}"] = wall_1d(Th, W1)
        res[f"wall W3 {Th}"] = wall_1d(Th, W3)
    # floor (inside the wall lining): ventilated foundation D-15, casing underside to 50 degC channel air, h = 12
    F0 = [("hdboard", 25), ("blanket64", 150), ("steel", 10)]
    F2 = [("hdboard", 25), ("blanket64", 150), ("microporous", 25), ("casi245", 50), ("steel", 10)]   # D-04
    res["floor INS-B3 on pad (no ventilation)"] = wall_1d(850, F0 + [("concrete", 600), ("soil", 1500)], outside="sink", sink=30)
    res["floor F2 ventilated"] = wall_1d(850, F2, outside="fixed", h_fixed=12, T_amb=50)
    Tf = res["floor F2 ventilated"]["T"][-2]
    # pad top under the channel: radiation from the casing floor in, convection to channel air + conduction to ground out
    Tp = 50.0
    for _ in range(200):
        qr = 0.8 * SIGMA * ((Tf + 273.15) ** 4 - (Tp + 273.15) ** 4)
        Tpn = (qr + 4.0 * 50 + 30 / 0.35) / (4.0 + 1 / 0.35 + 0.0) if False else None
        # pad (0.6 m RCC) + ground 1.6 m2K/W in series to 30 degC
        Rg = 0.6 / 1.7 + 1.6
        Tpn = (qr + 4.0 * 50 + 30 / Rg) / (4.0 + 1 / Rg)
        if abs(Tpn - Tp) < 0.01:
            break
        Tp = 0.5 * (Tp + Tpn)
    res["pad top ventilated"] = {"q": 0, "T": [Tp]}
    # flue: Rev H lined trench as drawn vs D-10 lined duct in a vented trench
    res["flue RevH best"] = wall_1d(800, [("ifb", 230), ("blanket96", 50), ("concrete", 200)], outside="sink", sink=35)
    res["flue RevH buried"] = wall_1d(800, [("ifb", 230), ("blanket96", 50), ("concrete", 200), ("soil", 1000)], outside="sink", sink=30)
    duct = duct_in_trench(800, [("module128", 100), ("microporous", 50), ("steel", 6)])
    res["flue duct D-10"] = {"q": duct["q_skin"], "T": duct["T"]}
    res["cover RevH"] = wall_1d(800, [("ifb", 75), ("blanket96", 50), ("steel", 6)], outside="free", eps=0.6)
    for t in (50, 100):
        res[f"dryer {t}"] = wall_1d(120, [("fibreboard", t), ("concrete", 250), ("soil", 1000)], outside="sink", sink=30)
    sk = lambda k: res[k]["T"][-2]
    checks = [
        check("Casing skin, all-fibre 200 + 50, hot face 1,000 °C", sk("wall W1 1000"), "degC", 65, "max", "why D-05 adds microporous", ref=True),
        check("Casing skin, D-05 wall, hot face 900 °C", sk("wall W3 900"), "degC", 65, "max", "typical alley"),
        check("Casing skin, D-05 wall, hot face 1,000 °C", sk("wall W3 1000"), "degC", 65, "max", "design case; Rev K target 53–55 °C (O-08)"),
        check("Casing skin, D-05 wall, hot face 1,100 °C", sk("wall W3 1100"), "degC", 70, "max", "beside the burner blocks"),
        check("Microporous hot side at 1,100 °C", res["wall W3 1100"]["T"][1], "degC", 950, "max", "microporous service limit"),
        check("Wall loss, D-05 at 1,000 °C", res["wall W3 1000"]["q"], "W/m2", None, "info"),
        check("Pad top, SH-INS B3 floor laid on the pad", res["floor INS-B3 on pad (no ventilation)"]["T"][3], "degC", 65, "max", "why D-15 ventilates the foundation", ref=True),
        check("Casing floor plate, F2 + ventilated foundation", Tf, "degC", 100, "max"),
        check("Pad top under the ventilated channels", Tp, "degC", 65, "max", "ACI 349 App. E sustained 65 °C"),
        check("Rev H flue trench RCC face, ideal sink", res["flue RevH best"]["T"][2], "degC", 70, "max", "Rev H target 60–70 °C", ref=True),
        check("Rev H flue trench RCC face, buried", res["flue RevH buried"]["T"][2], "degC", 70, "max", ref=True),
        check("D-10 lined flue duct skin", duct["T_skin"], "degC", None, "info", "inside the vented trench, not accessible"),
        check("D-10 trench RCC face", duct["T_rcc"], "degC", 65, "max", "trench air 45 °C"),
        check("Rev H cover plate (75 tile + 50 fibre)", sk("cover RevH"), "degC", 60, "max", "walk-on limit", ref=True),
        check("Dryer pit RCC behind 50 mm board", res["dryer 50"]["T"][1], "degC", 65, "max", ref=True),
        check("Dryer pit RCC behind 100 mm board (D-14)", res["dryer 100"]["T"][1], "degC", 65, "max"),
    ]
    return {"id": "C-04", "title": "Linings: casing skin, hearth and foundation, flue duct and trench, dryer pit (1-D, k(T))",
            "method": ["Steady 1-D conduction through layers with k = a + b·T_mean, iterated to convergence.",
                       "Free surface: h = 1.42 (ΔT/1.2)^0.25 + ε σ (Ts⁴ − Ta⁴)/ΔT, ε = 0.85, Ta = 35 °C (STL-EF method).",
                       "Ventilated foundation: casing underside to 50 °C channel air, h = 12 W/m²K (convection + radiation); "
                       "pad top from radiation in = convection (h 4) + conduction through 0.6 m RCC + ground (1.6 m²K/W).",
                       "Duct in trench: skin couples to trench air (h 4) and by radiation to the RCC; RCC passes it to air and ground.",
                       "Materials: " + "; ".join(f"{k}: k = {a} + {b}·T ({d})" for k, (a, b, d) in MATS.items() if k != "steel")],
            "results": {k: {"q": v["q"], "T": v["T"]} for k, v in res.items()} | {"duct": duct, "W3_q1000": res["wall W3 1000"]["q"]},
            "checks": checks,
            "notes": ["No 250 mm build-up reaches Rev K's 53–55 °C skin at a 900–1,000 °C hot face with these conductivities. "
                      "D-05 (175 module + 50 microporous + 25 CaSi) gives 61–65 °C and cuts the wall loss by ≈40 % against "
                      "all-fibre. The long faces sit inside the furnace pit; the end faces in the burner pits get a mesh guard.",
                      "A suspended kettle puts hot gas on the hearth, so the floor loses heat continuously. Laid straight on "
                      "the pad (SH-INS B3), the RCC would run at several hundred °C in steady state. D-15 sets the casing on a "
                      "ventilated steel grillage and adds microporous to the floor.",
                      "Rev H's lined trench cannot keep the RCC near 60–70 °C (12 Oct validation). D-10 carries the flue in an "
                      "internally lined steel duct (700 × 400 clear, ≈5.4 m/s) inside a vented trench."]}


# =========================================================================== air/flue properties & ducts
def rho_air(T_C, p=P_ATM):
    return PropsSI("D", "T", T_C + 273.15, "P", p, "Air")


def mu_air(T_C):
    return PropsSI("V", "T", T_C + 273.15, "P", P_ATM, "Air")


def duct_dp(Q, T_C, w, h=None, L=0.0, K=0.0, rough=1.0e-3, d=None):
    """Pressure drop (Pa) of a straight run + sum K, for air at T. Rectangular (w x h, m) or round (d, m)."""
    rho, mu = rho_air(T_C), mu_air(T_C)
    if d is not None:
        A, Dh = math.pi * d * d / 4, d
    else:
        A, Dh = w * h, 2 * w * h / (w + h)
    v = Q / A
    Re = rho * v * Dh / mu
    f = fluids.friction_factor(Re=Re, eD=rough / Dh)
    vp = 0.5 * rho * v * v
    return {"v": v, "VP": vp, "Re": Re, "f": f, "dp_fric": f * L / Dh * vp, "dp_K": K * vp,
            "dp": f * L / Dh * vp + K * vp, "rho": rho}


# =========================================================================== C-05 combustion air system
def c05_air(c01):
    lam = 1 + B.v("process.excess_air_design") / 100
    case = [v for k, v in c01["results"]["cases"].items() if k.startswith("design")][0]
    T = T_AMB
    Q = case["air_m3h_amb"] / 3600                        # m3/s total
    items = []
    p8 = duct_dp(Q, T, 0, d=0.2027, L=6.0, K=bend_rounded(Di=0.2027, angle=90, rc=0.3, fd=0.018) * 3, rough=4.5e-5)
    items.append(("8\" discharge, 6 m, 3 bends", p8))
    ven = duct_dp(Q, T, 0.15, 0.15, K=0.15)               # unrecovered loss ~15 % of throat VP (classical venturi 10-20 %)
    items.append(("Venturi 150 × 150 throat (15 % unrecovered)", ven))
    hdr = duct_dp(Q, T, 0.30, 0.15, L=4.0, K=0.5 + 0.3, rough=1.5e-4)
    items.append(("Header 300 × 150, 4 m, transition + tee", hdr))
    ring = duct_dp(Q / 2, T, 0.15, 0.15, L=10.0, K=2 * 0.3 + 0.5, rough=1.5e-4)
    items.append(("Ring 150 × 150, 10 m per half, 2 corners + branch tee", ring))
    br = duct_dp(Q / 2, T, 0, d=0.1023, L=3.5, K=3 * bend_rounded(Di=0.1023, angle=90, rc=0.15, fd=0.02) + 0.3 + 1.0, rough=4.5e-5)
    items.append(("4\" branch, 3.5 m, 3 bends, butterfly D2 open, outlet", br))
    total = sum(i[1]["dp"] for i in items)
    available = 725 * MMWC - total
    need = 306 * MMWC
    checks = [check("System loss blower → burner", total / MMWC, "mmWC", None, "info"),
              check("4\" branch velocity", br["v"], "m/s", 25, "max", "noise / loss"),
              check("Pressure left at the burner", available / MMWC, "mmWC", need / MMWC, "min", "Rev H: 306 mmWC needed")]
    return {"id": "C-05", "title": "Combustion air: blower to burner pressure budget (fluids)",
            "method": ["Air at 35 °C, design λ, both burners at full fire. Darcy friction (Colebrook via fluids.friction_factor).",
                       "Bend K from fluids.fittings.bend_rounded (Crane). Venturi unrecovered loss 15 % of throat VP."],
            "results": {"items": [(n, d["v"], d["dp"] / MMWC) for n, d in items], "total_mmWC": total / MMWC,
                        "available_mmWC": available / MMWC, "Q_m3s": Q},
            "checks": checks, "notes": ["Blower static 725 mmWC leaves ample pressure at the burners; the ratio controller GIK40 "
                                        "and the D2 butterflies trim the split."]}


# =========================================================================== C-06 gas piping
def c06_gas():
    gas = B.v("process.gas_flow_full_fire")
    p_g = 100e2          # Pa gauge, assumed regulated pressure (A-05)
    rho_n = 0.717        # kg/Nm3 methane
    rho = rho_n * (P_ATM + p_g) / P_ATM * 273.15 / (273.15 + T_AMB)
    mu = 1.1e-5
    L_hdr = G.plen(G.gas_header) / 1000
    L_N, L_S = G.plen(G.gas_main_N) / 1000, G.plen(G.gas_main_S) / 1000
    def run(name, d, L, frac, K):
        Q = gas * frac / 3600 * (273.15 + T_AMB) / 273.15 * P_ATM / (P_ATM + p_g)
        v = Q / (math.pi * d * d / 4)
        Re = rho * v * d / mu
        f = fluids.friction_factor(Re=Re, eD=4.5e-5 / d)
        return (name, v, (f * L / d + K) * 0.5 * rho * v * v / 100, L)
    rows = [run(f"DN65 header skid → tee (ID 62.7), {L_hdr:.1f} m", 0.0627, L_hdr, 1.0, 3 * 0.3 + 1.0),
            run(f"DN50 main, north pit (ID 52.5), {L_N:.1f} m", 0.0525, L_N, 0.5, 6 * 0.3 + 1.0),
            run(f"DN50 main, south pit (ID 52.5), {L_S:.1f} m", 0.0525, L_S, 0.5, 5 * 0.3 + 1.0),
            run("DN40 burner train pipework (ID 40.9), 2.5 m", 0.0409, 2.5, 0.5, 2.0)]
    checks = [check(r[0] + " velocity", r[1], "m/s", 20, "max", "gas line guideline") for r in rows]
    checks.append(check("Pipework loss skid → north burner train", rows[0][2] + rows[1][2] + rows[3][2], "mbar", None, "info",
                        "set the J125-S4 outlet = GIK40 rated inlet + this + valve losses (O-06)"))
    return {"id": "C-06", "title": "Gas piping: velocities and pressure loss at full fire",
            "method": ["Methane, ρn = 0.717 kg/Nm³, regulated 100 mbar(g) assumed (A-05), 35 °C. Darcy–Weisbach, fittings as K.",
                       "Run lengths are measured on the same pipe routes the CAD model draws (basis.Geo.gas_header / gas_main_N / gas_main_S)."],
            "results": {"rows": rows, "L": (L_hdr, L_N, L_S)}, "checks": checks,
            "notes": ["Confirm the PNG supply pressure and the J125-S4 outlet set point; the burner train (GIK40 ratio "
                      "controller) needs its rated inlet pressure from the Bloom data sheet."]}


# =========================================================================== C-07 flue passage & duct
def c07_flue(c01):
    case = [v for k, v in c01["results"]["cases"].items() if k.startswith("design")][0]
    Tf = B.v("process.flue_temp")
    rows = []
    for name, Nm3h in (("Rev H flue", B.v("process.flue_flow")), ("Design λ flue", case["flue_Nm3h"])):
        Q = Nm3h / 3600 * (Tf + 273.15) / 273.15
        rows.append((name, Nm3h, Q, Q / 0.21, Q / 0.28, Q / 0.70))
    d = rows[1]
    checks = [check("Passage 700 × 300 velocity (design λ)", d[3], "m/s", None, "info", "Rev H 6.7 m/s"),
              check("D-10 duct 700 × 400 velocity", d[4], "m/s", 3.0, "min", "keeps the duct self-cleaning"),
              check("Rev H trench 700 × 1000 velocity", d[5], "m/s", 3.0, "min", "too slow: ash settles", ref=True)]
    return {"id": "C-07", "title": "Flue passage and lined flue duct", "method": ["Q = Nm³/h × (T+273)/273 / 3600."],
            "results": {"rows": rows}, "checks": checks, "notes": []}


# =========================================================================== C-08 loop energy balance
def c08_loop(c01):
    case = [v for k, v in c01["results"]["cases"].items() if k.startswith("design")][0]
    temps = B.v("loop.temps")
    flue_X = products(case["lambda"])
    nf = sum(flue_X.values())
    flue_X = {k: v / nf for k, v in flue_X.items()}
    AIR = {"O2": 0.21, "N2": 0.79}
    F = B.v("process.flue_flow")
    R = B.v("loop.return_flow")
    A = B.v("loop.fresh_air")
    mol = lambda Nm3h: Nm3h / 3600 / VM          # mol/s
    H_in = mol(F) * _h_mix(flue_X, temps["flue"]) + mol(R) * _h_mix(AIR, temps["return"]) + mol(A) * _h_mix(AIR, temps["fresh"])
    tot = mol(F + R + A)
    X_mix = {k: (mol(F) * flue_X.get(k, 0) + (mol(R) + mol(A)) * AIR.get(k, 0)) / tot for k in set(flue_X) | set(AIR)}
    lo, hi = 50.0, 400.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if tot * _h_mix(X_mix, mid) > H_in:
            hi = mid
        else:
            lo = mid
    T_mix = 0.5 * (lo + hi)
    suction_m3h = (F + R + A) * (T_mix + 273.15) / 273.15
    blower_m3h_120 = (F + R + A) * (120 + 273.15) / 273.15
    bleed = B.v("process.flue_flow") + A                      # what goes in must come out
    dryer_Nm3h = F + R + A - bleed
    cp_air_kJ_Nm3K = (_h_mix(AIR, 120) - _h_mix(AIR, 100)) / 20 / VM / 1000
    duty_dryer = dryer_Nm3h / 3600 * cp_air_kJ_Nm3K * (temps["supply"] - temps["return"])
    flue_heat = mol(F) * (_h_mix(flue_X, temps["flue"]) - _h_mix(flue_X, temps["supply"])) / 1000
    bleed_heat = bleed / 3600 * cp_air_kJ_Nm3K * (temps["supply"] - temps["fresh"])
    checks = [check("Adiabatic mix temperature at suction", T_mix, "degC", 130, "max", "Rev H 130 °C; blower casing limit 120 °C after losses"),
              check("Suction volume at T_mix", suction_m3h, "m3/h", None, "info"),
              check("Blower volume at 120 °C", blower_m3h_120, "m3/h", 48000, "max", "AEP-ZA-9.0 48,000 m3/h"),
              check("Bleed = flue + fresh (mass balance)", bleed, "Nm3/h", None, "info", "Rev H 4,729"),
              check("Dryer duty (20 K across the loads)", duty_dryer, "kW", None, "info", "Rev H 205–220 kW"),
              check("Heat in the bleed (to 30 °C)", bleed_heat, "kW", None, "info", "Rev H ≈150 kW"),
              check("Flue heat recovered 800→120 °C", flue_heat, "kW", None, "info")]
    return {"id": "C-08", "title": "Heat-recovery loop: mixing temperature and energy balance (Cantera enthalpies)",
            "method": ["Enthalpy balance flue (800 °C) + dryer return (100 °C) + fresh air (30 °C) → mix; bisection on T_mix.",
                       "Bleed = flue + fresh air (steady loop mass balance)."],
            "results": {"T_mix": T_mix, "suction_m3h": suction_m3h, "blower_m3h_120": blower_m3h_120, "bleed": bleed,
                        "dryer_Nm3h": dryer_Nm3h, "duty_dryer": duty_dryer, "bleed_heat": bleed_heat, "flue_heat": flue_heat},
            "checks": checks,
            "notes": ["The fresh-air damper's ≈15 % minimum stop (STL-MB-DMP-02) is what keeps the blower inlet at or below "
                      "the 120 °C casing and bearing limit when the dryer return runs hot."]}


# =========================================================================== C-09 loop pressure budget + boxes
def c09_loop_dp():
    Tsup, Tret, Tsuc = 120.0, 100.0, 130.0
    Qb = 48000 / 3600                          # m3/s at 120
    Qd = 11.44                                 # dryer flow m3/s at 120 (Rev H)
    Qr = 10.86                                 # return at 100
    Qs = 12.27                                 # suction at 130
    rows = []
    def add(name, d):
        rows.append((name, d["v"], d["dp"] / MMWC))
    add("Return trench 900 × 1000, 5.5 m, 2 radiused bends", duct_dp(Qr, Tret, 0.9, 1.0, L=5.5, K=2 * 0.35, rough=1.5e-3))
    add("Junction (radiused merge)", duct_dp(Qs, Tsuc, 1.0, 1.0, K=0.4))
    add("Suction trench 1000 × 1000, 4 m", duct_dp(Qs, Tsuc, 1.0, 1.0, L=4.0, rough=1.5e-3))
    rows.append(("Mixing box S2 with R700 deflector (SH-MB-01)", None, B.v("loop.mixing_box_loss")))
    add("Inlet spool Ø900 + cruciform straightener", duct_dp(Qs, Tsuc, 0, d=0.9, L=0.6, K=0.25))
    add("Discharge trench 1100 × 1000, 16 m, 2 bends", duct_dp(Qb, Tsup, 1.1, 1.0, L=16, K=2 * 0.35 + 0.3, rough=1.5e-3))
    add("Bleed tee (run)", duct_dp(Qd, Tsup, 1.1, 1.0, K=0.1))
    add("Supply transition 1000 × 700 through the wall", duct_dp(Qd, Tsup, 1.0, 0.7, K=0.5))
    # perforated faces: Ø15 holes in 2 mm plate, staggered 60° at 37 pitch
    d_h, pitch, face = 0.015, 0.037, (7.0, 1.0)
    phi = 0.9069 * (d_h / pitch) ** 2
    A_open = phi * face[0] * face[1]
    v_hole = Qd / A_open
    K_hole = 2.7                                     # thin perforated plate at ~15 % open (Idelchik), on hole velocity
    dp_hole = K_hole * 0.5 * rho_air(Tsup) * v_hole ** 2
    n_holes = face[0] * face[1] / (0.866 * pitch ** 2)
    rows.append(("Supply box holes Ø15 @ 37 stag. (14.9 % open)", v_hole, dp_hole / MMWC))
    rows.append(("Dryer chamber cross-flow + loads", Qd / (5.0 * 1.4), 1.0))
    v_hole_r = Qr / A_open
    rows.append(("Extraction box holes", v_hole_r, K_hole * 0.5 * rho_air(Tret) * v_hole_r ** 2 / MMWC))
    add("Return transition 1000 × 700", duct_dp(Qr, Tret, 1.0, 0.7, K=0.5))
    total = sum(r[2] for r in rows)
    # distribution: centre feed, box 1300 x 350, half flow each way
    feed_v = (Qd / 2) / (1.3 * 0.35)
    feed_vp = 0.5 * rho_air(Tsup) * feed_v ** 2
    ratio = dp_hole / feed_vp
    end_feed_v = Qd / (1.0 * 0.35)
    end_ratio = dp_hole / (0.5 * rho_air(Tsup) * end_feed_v ** 2)
    fan_hot = 72.0
    fan_std_to_hot = 72.0 * rho_air(120) / rho_air(20)
    checks = [check("Loop total (D-12 centre-fed boxes)", total, "mmWC", fan_hot, "max", "if 72 mmWC is rated at 120 °C"),
              check("Loop total vs fan if 72 mmWC is a 20 °C rating", total, "mmWC", fan_std_to_hot, "max", "→ confirm rating basis"),
              check("Hole ΔP / feed VP, centre feed 1300 × 350", ratio, "-", 2.0, "min", "uniform discharge rule of thumb"),
              check("Hole ΔP / feed VP, Rev H end feed 1000 × 350", end_ratio, "-", 2.0, "min", "Rev H finding", ref=True),
              check("Holes per face", n_holes, "nos", None, "info", "Rev H ≈5,890"),
              check("Hole velocity", v_hole, "m/s", None, "info")]
    return {"id": "C-09", "title": "Heat-recovery loop pressure budget and perforated-box distribution",
            "method": ["Concrete trenches ε = 1.5 mm; radiused bends K = 0.35; air properties from CoolProp at the local temperature.",
                       "Perforated plate K = 2.7 on hole velocity (Idelchik, thin plate ~15 % open). Mixing box from SH-MB-01.",
                       "Distribution criterion: hole ΔP ≥ 2 × feed velocity pressure (static regain stays small)."],
            "results": {"rows": rows, "total": total, "feed_v": feed_v, "ratio": ratio, "end_ratio": end_ratio,
                        "n_holes": n_holes, "phi": phi, "fan_std_to_hot": fan_std_to_hot},
            "checks": checks,
            "notes": ["With centre-fed 1,300 × 350 boxes the loop needs about the fan's 72 mmWC, provided that figure is the "
                      "hot (120 °C) rating. If it is a standard-air rating the fan delivers ≈54 mmWC hot and the VFD must run "
                      "it above 50 Hz, or the impeller be re-selected. Confirm with AEP."]}


# =========================================================================== C-11 fans
def c11_fans():
    rows = []
    Q, dp = 48000 / 3600, 72 * MMWC
    air_kw = Q * dp / 1000
    shaft = air_kw / 0.75
    cold = shaft * rho_air(30) / rho_air(120)
    rows.append(("Recirculation AEP-ZA-9.0", air_kw, shaft, cold, 22.0))
    Qc, dpc = 1400 / 3600, 725 * MMWC
    air_c = Qc * dpc / 1000
    rows.append(("Combustion MBI-4040", air_c, air_c / 0.60, air_c / 0.60, 5.5))
    pit_vol = 3.0 * 1.8 * (0 - G.bpit_floor) / 1000
    ach_req = 20
    checks = [check("Recirc fan cold-start shaft power", cold, "kW", 22.0, "max", "30 HP = 22 kW"),
              check("Combustion blower shaft power", air_c / 0.60, "kW", 5.5, "max", "motor rating not in the sources: 5.5 kW derived (A-06)"),
              check("Burner pit volume", pit_vol, "m3", None, "info"),
              check("Pit fan minimum flow at 20 ACH", pit_vol * ach_req, "m3/h", None, "info", "set 3 HP fan duty ≥ this")]
    return {"id": "C-11", "title": "Fan power", "method": ["P_air = Q·Δp; shaft = P_air/η (η 0.75 recirc, 0.60 combustion); cold start scales with ρ."],
            "results": {"rows": rows, "pit_vol": pit_vol}, "checks": checks, "notes": []}


# =========================================================================== C-12 structure
def c12_structure():
    zinc_t = G.kLi * G.kWi * B.v("kettle.zinc_depth") / 1e9 * B.v("process.zinc_density")
    sh = G.rim - G.k_out_bot
    steel_vol = (2 * (G.kLo + G.kWo) * sh * G.kt + G.kLo * G.kWo * G.kt) / 1e9
    flange_vol = (2 * (G.kLo + G.kWo) + 4 * G.flw) * G.flw * G.flt / 1e9
    kettle_t = (steel_vol + flange_vol) * 7.85
    W = (zinc_t + kettle_t) * G0 * 1.05                                  # kN, +5 % immersed jig
    pitch = int(B.v("support.rib_pitch"))
    n_ribs = 2 * len(range(-3500, 3501, pitch)) + 2 * 3          # as modelled: 15 per long side, 3 per end (SUP-03)
    P = W / n_ribs
    arm = (G.cap_in_X - G.ring_out_X) / 1000 + 0.075                    # into the cap beam weld line
    M = P * arm                                                          # kN m
    Z = 12 * 200 ** 2 / 6 / 1e9                                          # m3
    sigma = M / Z / 1000                                                 # MPa
    allow = B.v("support.rib_allowable")
    # kettle growth
    grow = 13.5e-6 * (B.v("process.bath_temp") - 20) * G.kLo
    # kettle long wall, one-way vertical span flange -> bottom, triangular hydrostatic load
    p0 = B.v("process.zinc_density") * 1000 * G0 * B.v("kettle.zinc_depth") / 1000      # Pa
    Ls = (G.rim - G.k_in_bot) / 1000
    Mw = p0 * Ls ** 2 / (9 * math.sqrt(3))                               # N m / m
    Zw = 1.0 * (G.kt / 1000) ** 2 / 6
    sig_w = Mw / Zw / 1e6
    E450 = 170e9
    Iw = 1.0 * (G.kt / 1000) ** 3 / 12
    defl = 0.00652 * p0 * Ls ** 4 / (E450 * Iw) * 1000
    # foundation bearing: kettle + zinc + casing + lining + pad
    casing_t = 2 * (G.cL + G.cW) / 1000 * (G.ctop - G.cbase) / 1000 * G.ct / 1000 * 7.85 * 1.6 + G.cL * G.cW / 1e6 * G.cfp / 1000 * 7.85
    lining_t = 2.5 * (2 * (G.cL + G.cW) / 1000 * 1.6 * 0.25 * 0.125) + 0.2 * G.cL * G.cW / 1e6
    pad_t = 3.0 * 8.5 * 0.6 * 2.5
    q_found = (zinc_t + kettle_t + casing_t + lining_t + pad_t) * G0 / (3.0 * 8.5)
    sbc = 150.0
    checks = [check("Zinc in the kettle", zinc_t, "t", None, "info", "Rev K 64.3 t"),
              check("Kettle steel (walls, bottom, flange)", kettle_t, "t", None, "info", "Rev H ≈12 t"),
              check("Suspended load incl. 5 % jig", W, "kN", None, "info"),
              check("Ribs on the support ring", n_ribs, "nos", None, "info"),
              check("Rib cantilever stress 12 × 200", sigma, "MPa", allow, "max", "E250 at 250 °C (IS 800), STL-EF"),
              check("Kettle growth along its length 20→450 °C", grow, "mm", None, "info", "slides on the graphite strip"),
              check("Kettle wall bending, hydrostatic (indicative)", sig_w, "MPa", 25, "max", "creep-governed; kettle maker to confirm"),
              check("Kettle wall elastic deflection (indicative)", defl, "mm", None, "info"),
              check("Foundation bearing pressure", q_found, "kN/m2", sbc, "max", "SBC 150 kN/m² assumed (A-07)")]
    return {"id": "C-12", "title": "Structure: kettle support ring, kettle wall, foundation",
            "method": ["Load path (STL-EF): flange → graphite strip → ISA 100 bearing ring → 12 × 200 ribs @ 500 → cap beam → casing → pad.",
                       "Rib: cantilever M = P × arm, σ = M/Z, Z = t h²/6.",
                       "Kettle wall: one-way vertical strip, simply supported flange-to-bottom, triangular load p0 = ρ g h: "
                       "M = p0 L²/(9√3), δ = 0.00652 p0 L⁴/(E I), E(450 °C) = 170 GPa."],
            "results": {"zinc_t": zinc_t, "kettle_t": kettle_t, "W_kN": W, "n_ribs": n_ribs, "sigma": sigma, "grow": grow,
                        "sig_w": sig_w, "defl": defl, "q_found": q_found, "arm": arm},
            "checks": checks,
            "notes": ["The kettle wall figure is a sanity check only. Kettle wall design (creep at 450 °C, corner stresses, "
                      "bulge allowance) belongs to the kettle maker's calculation."]}


# =========================================================================== C-13 stack
def c13_stack(c08):
    bleed = c08["results"]["bleed"]
    T = 120.0
    Q = bleed / 3600 * (T + 273.15) / 273.15
    d = 0.4
    v = Q / (math.pi * d * d / 4)
    H = B.v("levels.stack_top") / 1000
    draft = G0 * H * (rho_air(T_AMB) - rho_air(T))
    checks = [check("Stack exit velocity Ø400", v, "m/s", 20, "max", "Rev H 15 m/s"),
              check("Stack exit velocity Ø400 (min)", v, "m/s", 6, "min", "plume rise"),
              check("Natural draft 12 m", draft / MMWC, "mmWC", None, "info"),
              check("Stack height", H, "m", 11, "min", "confirm against the SPCB consent (O-05)")]
    return {"id": "C-13", "title": "Bleed stack", "method": ["Draft = g H (ρ_amb − ρ_gas)."],
            "results": {"v": v, "draft": draft}, "checks": checks, "notes": []}


# =========================================================================== C-14 energy
def c14_energy(c01, c02, c04):
    AH = [v for k, v in c01["results"]["cases"].items() if k.startswith("design")][0]["AH"]
    area_casing = (2 * (G.cL + G.cW) * (G.ctop - G.cbase) + G.cL * G.cW) / 1e6
    P_lining = c04["results"]["W3_q1000"] * area_casing / 1000
    rows = []
    for tph, net in ((6.0, c02["results"]["net_6_0"]), (6.7, c02["results"]["net_6_7"])):
        fired = (net + P_lining) / AH
        gas = fired / B.v("process.gas_lhv")
        rows.append((tph, net, fired, gas, gas / tph, fired / tph))
    checks = [check("Casing + floor loss (D-05 / D-15)", P_lining, "kW", None, "info"),
              check("Fired duty at 6.0 t/h", rows[0][2], "kW", B.v("process.fired_duty"), "max"),
              check("Fired duty at 6.7 t/h", rows[1][2], "kW", B.v("process.fired_duty"), "max"),
              check("Gas per tonne at 6.0 t/h", rows[0][4], "Nm3/t", None, "info"),
              check("Furnace efficiency at 6.0 t/h", 100 * rows[0][1] / rows[0][2], "%", None, "info", "Rev H 53.4 % at 1,172 kW")]
    return {"id": "C-14", "title": "Firing rate and gas consumption at production",
            "method": ["Fired = (net + casing loss) / available heat (C-01, flue 800 °C, design λ). Casing loss = D-05 wall flux × casing area."],
            "results": {"rows": rows, "P_lining": P_lining}, "checks": checks, "notes": []}


# =========================================================================== C-10 insulation quantities
def c10_quantities():
    H_wall = (G.ctop - G.f_plate_top) / 1000                         # lining height m
    perim = 2 * (G.cL + G.cW) / 1000 - 4 * 2 * G.lin / 1000          # mean perimeter of the lining
    A_wall = perim * H_wall - 0.21 - 2 * 0.16                         # less flue port and burner blocks
    A_floor = (G.cL - 2 * G.lin) * (G.cW - 2 * G.lin) / 1e6 - 2 * 0.49   # inside the lining, less leak pits
    rows = []
    rows.append(("Folded module 300 × 300 × 175, 128 kg/m³ 1430, Z-anchor SS310", A_wall / 0.09 * 1.03, "nos", "walls, +3 % cut"))
    rows.append(("Microporous panel 1000 × 500 × 25 (2 layers walls, 1 layer floor)", (2 * A_wall + A_floor) / 0.5 * 1.05, "nos", "+5 %"))
    rows.append(("Calcium silicate 1000 × 500 × 25 (walls 1 layer, floor 2 layers)", (A_wall + 2 * A_floor) / 0.5 * 1.05, "nos", "+5 %"))
    # floor blanket 64 kg/m3, 8300 x 610 x 50: strips 7,725 long (7,700 + 25 compression), 2,250 / 610 -> 4 strips per layer
    rows.append(("Blanket 64 kg/m³ 8,300 × 610 × 50 — hearth, 3 layers A–B–A", 3 * 4, "rolls", "4 strips 7,725 per layer, 4th ripped to 420"))
    rows.append(("Blanket 64 kg/m³ 8,300 × 610 × 50 — top closure T1, 3 layers", 7, "rolls", "SH-INS 7 per location"))
    rows.append(("Blanket 64 kg/m³ 8,300 × 610 × 50 — bottom band 305 × 50", 1, "rolls", "SH-INS: 1 per kettle, butt joints"))
    rows.append(("Blanket 64 kg/m³ 4,200 × 610 × 25 — corner shields 2 × 25", 2, "rolls", "SH-INS: 1 per shield"))
    rows.append(("HD board 500 × 1,000 × 25 — top closure between ribs", 22, "nos", "35 bays of 488 + corners, 2 cuts per board, +2 spare"))
    rows.append(("HD board 500 × 1,000 × 25 — hearth wear face", A_floor / 0.5 * 1.05, "nos", "+5 %"))
    rows.append(("SS 310S plate 6 mm, 750 × 1,500 developed", 2, "nos", "1 per burner, rolled R350"))
    checks = [check("Wall lining area", A_wall, "m2", None, "info"), check("Hearth area inside the lining", A_floor, "m2", None, "info"),
              check("50 mm rolls for one furnace", 12 + 7 + 1, "rolls", None, "info", "SH-INS two-furnace stock: 67")]
    return {"id": "C-10", "title": "Insulation quantities for one furnace (D-04/D-05 build-ups, SH-INS cutting rules)",
            "method": ["Areas from the derived geometry; strip layouts per SH-INS-01 Rev B (A–B–A, 25 mm compression per joint)."],
            "results": {"rows": rows, "A_wall": A_wall, "A_floor": A_floor}, "checks": checks, "notes": []}


def run_all():
    c01 = c01_combustion()
    c02 = c02_capacity(c01)
    c04 = c04_linings()
    c05 = c05_air(c01)
    c06 = c06_gas()
    c07 = c07_flue(c01)
    c08 = c08_loop(c01)
    c09 = c09_loop_dp()
    c11 = c11_fans()
    c12 = c12_structure()
    c13 = c13_stack(c08)
    c14 = c14_energy(c01, c02, c04)
    c10 = c10_quantities()
    return [c01, c02, c04, c05, c06, c07, c08, c09, c10, c11, c12, c13, c14]


if __name__ == "__main__":
    for c in run_all():
        print(f"\n== {c['id']} {c['title']}")
        for k in c["checks"]:
            lim = "" if k["limit"] is None else f" (limit {k['limit']})"
            v = k["value"]
            vs = f"{v:,.2f}" if isinstance(v, (int, float)) else str(v)
            print(f"  [{k['status']:4s}] {k['name']}: {vs} {k['unit']}{lim}  {k['note']}")
