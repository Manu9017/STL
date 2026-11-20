# Open items, holds and assumptions — SHV-FUR-6700 Rev A

Nothing on this list is invented in the model. Where a value is needed to draw or calculate, the assumption is stated here and marked **A** in `design_basis.yaml`.

## Holds (must close before fabrication)

| # | Item | Owner | Effect |
|---|---|---|---|
| O-01 | **Trench depth, Hold H1.** Rev H uses a uniform 1,000 mm. The R-02 foundation drawings show −1,400 / −1,000 with a 1,260 × 1,780 section. The model uses 1,000 clear (and D-10 for the flue). | Civil | Trench levels, mixing-box excavation |
| O-02 | **Flue temperature at the tap point** is not confirmed. All loop figures assume 800 °C. | Commissioning data | C-04, C-07, C-08 |
| O-03 | **Bloom HV-400 GA.** The burner body in the model is an envelope (Ø380 × 520 + Ø460 × 170 flange). Rated gas and air inlet pressures are also needed. | Bloom / Eclipse | Burner block, pit layout, C-05, C-06 |
| O-04 | **Mittal MBI-4040 rating basis** (actual or normal m³/h) and motor kW. Full fire at λ 1.125 needs ≈1,430 m³/h at 35 °C, against 1,400 rated. At λ 1.125 the blower supports ≈1,147 kW. Production needs ≈760–840 kW, so the limit only applies at full fire. | Mittal | C-01, C-11 |
| O-05 | **Stack height and sampling port** against the SPCB consent. | Client / SPCB | Stack |
| O-06 | **PNG supply pressure and J125-S4 outlet set point.** Pipework loss skid → north burner is ≈6 mbar at full fire. | Gas supplier | C-06 |
| O-07 | **AEP-ZA-9.0: is 72 mmWC rated at 20 °C or at 120 °C?** The loop needs ≈74 mmWC hot with centre-fed boxes. A 20 °C rating gives only ≈54 mmWC hot. | AEP | C-09 |
| O-08 | **Rev K skin target of 53–55 °C** cannot be reached in 250 mm at a 900–1,000 °C hot face. D-05 gives 61–65 °C. Either accept that, or thicken locally where people stand. | SHIVAS | C-04 |
| O-09 | **Mixing-box handing.** The blower cut-out face differs between Rev N (right face) and SH-MB-01 Rev A (left face). The model follows SH-MB-01 (west face). | SHIVAS | Layout |
| O-10 | **Burner count.** The POs and SH-PID-02 give 2 HV-400 per furnace; an older note says 4. Modelled as 2. | SHIVAS | Firing |
| O-11 | **Kettle maker's design**: creep at 450 °C, corner stresses, bulge allowance, plate chemistry (Si ≤ 0.03 %, P ≤ 0.02 %), UT and RT. | Kettle maker | Kettle |
| O-12 | **Structural design** of the grillage, cap beam, furnace and burner pit walls, trench walls, blower plinths and stack foundation. | Structural engineer | Civil |
| O-13 | **Combustion safety review** of the burner management, gas train and purge against the applicable standard (EN 746-2 / NFPA 86), by a competent person. The model shows the PID-02 hardware. It makes no compliance claim. | SHIVAS / Eclipse | — |
| O-14 | **Dryer chain drive**: VFD or torque limiter. Door clear opening against the longest jig. | SHIVAS | Dryer |
| O-15 | **Pit fan duty.** Each fan needs ≥ 189 m³/h (20 air changes per hour of a 9.45 m³ pit). Confirm the 3 HP fan's curve. | Supplier | C-11 |

## Assumptions used in the calculations

| # | Assumption | Conservative? |
|---|---|---|
| A-01 | Fuel is methane; this reproduces Rev H's 9.9 kWh/Nm³ LHV. PNG with 2–5 % C2+ changes air and flue by < 2 %. | Neutral |
| A-02 | Combustion air is dry. | Slightly unconservative on flue volume (≈1–2 %) |
| A-03 | Conductivity of 64 kg/m³ blanket: k = 0.020 + 0.00027·T (typical 1260-grade data). Replace with the supplier's sheet. | Neutral |
| A-04 | HD board: k = 0.060 + 0.00012·T, ~300 kg/m³. | Neutral |
| A-05 | Regulated gas pressure 100 mbar(g). | Conservative on velocity |
| A-06 | Combustion blower motor 5.5 kW. Derived as 2.77 kW air power ÷ 0.60; it is not in the sources. | — |
| A-07 | Safe bearing capacity 150 kN/m². The pad bears ≈49 kN/m². | — |
| A-08 | Ventilated foundation channels at 50 °C air, h = 12 W/m²K at the casing underside. Flue trench air at 45 °C. | Must be checked at commissioning |
| A-09 | Lining hot face 1,000 °C for design, 1,100 °C beside the burner blocks. | Conservative for most of the wall |
| A-10 | SS 310S, 6 mm, for the corner shield plates. 12 mm for the lip plate (SH-INS also assumed this). | — |
| A-11 | Mean steel cp 0.52 kJ/kg K, jig mass 12 % of work, zinc pickup 5 % (STL-EF basis). | Neutral |
