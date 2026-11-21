# Open items, holds and assumptions — SHV-FUR-6700 Rev A

Nothing on this list is invented in the model. Where a value is needed to draw or calculate, the assumption is stated here and marked **A** in `design_basis.yaml`.

## Holds (must close before fabrication)

| # | Item | Owner | Effect |
|---|---|---|---|
| O-01 | **Trench depth, Hold H1.** Rev H uses a uniform 1,000 mm. The R-02 foundation drawings show −1,400 / −1,000 with a 1,260 × 1,780 section. The model uses 1,000 clear (and D-10 for the flue). | Civil | Trench levels, mixing-box excavation |
| O-02 | **Flue temperature at the tap point** is not confirmed. All loop figures assume 800 °C. | Commissioning data | C-04, C-07, C-08 |
| O-03 | **Bloom HV-400 GA.** The burner body in the model is an envelope (Ø380 × 520 + Ø460 × 170 flange). Rated gas and air inlet pressures are also needed. | Bloom / Eclipse | Burner block, pit layout, C-05, C-06 |
| O-04 | **AEP-VB-2.5 rating basis** (actual or normal m³/h). SH-PID-02A Rev U fixes the blower and its 7.5 HP motor; the 1,400 m³/h at 725 mmWC duty comes from Rev H. Full fire at λ 1.125 needs ≈1,430 m³/h at 35 °C. At λ 1.125 the blower supports ≈1,147 kW. Production needs ≈760–840 kW, so the limit only applies at full fire. | AEP | C-01, C-11 |
| O-05 | **Stack height and sampling port** against the SPCB consent. | Client / SPCB | Stack |
| O-06 | **PNG supply pressure and J125-S4 outlet set point.** Pipework loss skid → north burner is ≈6 mbar at full fire. | Gas supplier | C-06 |
| O-07 | **AEP-ZA-9.0: is 72 mmWC rated at 20 °C or at 120 °C?** The loop needs ≈71 mmWC hot with centre-fed boxes and the corner blower (D-22). A 20 °C rating gives only ≈54 mmWC hot. | AEP | C-09 |
| O-08 | **Rev K skin target of 53–55 °C** cannot be reached in 250 mm at a 900–1,000 °C hot face. D-05 gives 61–65 °C. Either accept that, or thicken locally where people stand. | SHIVAS | C-04 |
| O-09 | **Mixing-box handing.** The blower cut-out face differs between Rev N (right face) and SH-MB-01 Rev A (left face). The model follows SH-MB-01 (west face). | SHIVAS | Layout |
| O-10 | *Closed.* Burner count: SH-PID-02A Rev U and Bloom PO 1018 give 4 HV-400 for two furnaces, 2 per furnace. | — | — |
| O-11 | **Kettle maker's design**: creep at 450 °C, corner stresses, bulge allowance, plate chemistry (Si ≤ 0.03 %, P ≤ 0.02 %), UT and RT. | Kettle maker | Kettle |
| O-12 | **Structural design** of the grillage, cap beam, furnace and burner pit walls, trench walls, blower plinths and stack foundation. | Structural engineer | Civil |
| O-13 | **Combustion safety review** of the burner management, gas train and purge against the applicable standard (EN 746-2 / NFPA 86), by a competent person. The model shows the PID-02 hardware. It makes no compliance claim. | SHIVAS / Eclipse | — |
| O-14 | **Dryer chain drive**: VFD or torque limiter. Door clear opening against the longest jig. | SHIVAS | Dryer |
| O-15 | **Pit fan duty.** Each fan needs ≥ 189 m³/h (20 air changes per hour of a 9.45 m³ pit). Confirm the 3 HP fan's curve. | Supplier | C-11 |
| O-16 | **Zinc-fume bag filter (ZFE) location, fan and duct route beyond the flanged stub.** The model stops the Ø700 at X +4.6 m, north of the furnace. The fan must cover ≈52 mmWC hood loss plus the filter and duct. | SHIVAS | C-15 |
| O-17 | **Enclosure structure**: posts, girts, outriggers and the deck connection over the casing walls (D-24), and wind on the 4.7 m walls. | Structural engineer | Enclosure |
| O-18 | **Door interlock**: only one skimming door open at a time, and the skimming stop at 1,000 mm (D-25), to be written into the enclosure control logic. | SHIVAS | C-15 |
| O-19 | **SH-PID-02A Rev U start-up sequence text** still says "PILOT: C2 opens, C7 sparks at C18, C6 must prove the pilot" and lists trip C17. Neither C17 nor C18 is on the bill of material, and note 2 says direct spark through C12 with no pilot. Correct the sequence to: ignition gas C2 opens, C7 sparks at C12, C6 proves the ignition flame. | SHIVAS / Eclipse | BMS |

## Holds on SH-PID-02A Rev U (carried from the P&ID)

| Hold | Item | Where in the model |
|---|---|---|
| H1 | Does the HV-400 take a single gas inlet with the ignition gas merged? Confirm with Bloom before the pipework is fixed. | NG-50-1x3 merge tee and 2" inlet, status open |
| H2 | D1 is tapped on the blower discharge, so a shut D2 at a burner is not detected. | D1 on the 7" line |
| H3 | Parasitic circulation in the closed ring. Allow for it when the purge time is set. | CA-150-103 ring |
| H6 | A10 command authority undefined: one train, four burners, nobody assigned. A10 must close on any burner lockout and on emergency stop. | A10 on the skid |
| H8 | Air impulse to B1: 1" per the valve GA, ¼" tube on the P&ID. Measure on site. | IMP-1, IMP-2 |
| H21 | D2, D6, C19 and the UV cooling air items are on neither purchase order. Raise them or the burners cannot be balanced or isolated. | D2, C19, C9, C11, CA-15-101 marked "to order" |

## Assumptions used in the calculations

| # | Assumption | Conservative? |
|---|---|---|
| A-01 | Fuel is methane; this reproduces Rev H's 9.9 kWh/Nm³ LHV. PNG with 2–5 % C2+ changes air and flue by < 2 %. | Neutral |
| A-02 | Combustion air is dry. | Slightly unconservative on flue volume (≈1–2 %) |
| A-03 | Conductivity of 64 kg/m³ blanket: k = 0.020 + 0.00027·T (typical 1260-grade data). Replace with the supplier's sheet. | Neutral |
| A-04 | HD board: k = 0.060 + 0.00012·T, ~300 kg/m³. | Neutral |
| A-05 | Regulated gas pressure 100 mbar(g). | Conservative on velocity |
| A-06 | *Closed.* Combustion blower motor 7.5 HP = 5.5 kW, now in SH-PID-02A Rev U. | — |
| A-12 | Enclosure air 50 °C for the extraction losses (C-15). | Neutral |
| A-13 | Skimming-door windows sit in the doors at a +1.300 sill (eye level from FFL); the annexure does not place them. | — |
| A-07 | Safe bearing capacity 150 kN/m². The pad bears ≈49 kN/m². | — |
| A-08 | Ventilated foundation channels at 50 °C air, h = 12 W/m²K at the casing underside. Flue trench air at 45 °C. | Must be checked at commissioning |
| A-09 | Lining hot face 1,000 °C for design, 1,100 °C beside the burner blocks. | Conservative for most of the wall |
| A-10 | SS 310S, 6 mm, for the corner shield plates. 12 mm for the lip plate (SH-INS also assumed this). | — |
| A-11 | Mean steel cp 0.52 kJ/kg K, jig mass 12 % of work, zinc pickup 5 % (STL-EF basis). | Neutral |
