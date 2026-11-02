# AES17 class-D measurement filter

A passive low-pass that sits between a class-D amplifier and an audio analyzer, so that the
amplifier's switching residue never reaches the analyzer's input stage. It is the circuit of
the Audio Precision AUX-0025, on a 158 × 124 mm board in a Hammond 1444-862 aluminium chassis
with every connector in its front long wall, with the 20 kHz knee trimmable, a 20:1 pad switched by a toggle or a relay, and the
AUX-0025's own connectors: female XLR and dual banana in, male XLR out. Designed for a QuantAsylum QA403 and the
[Klirr](https://github.com/ToxSox/klirr) measurement software, usable with anything that has a
100 kΩ input.

**Status: designed, simulated, generated, not yet built - a prototype, not yet a reference.**
The Gerbers and the JLCPCB files are in `hardware/fab/`, checked against each other by
`hardware/check_release.py`; the first order has not been placed. Everything below the
simulation line is therefore a claim, not a measurement. The design review's
[verification plan](docs/design-review.md#verification-what-makes-it-a-reference) lists what has
to pass before it counts as a reference: the ferrite coils' linearity first, then the ground with
bridged amplifiers, heat, and the stop band.

![the board](hardware/aes17-filter-top.png)

## Where this comes from

This repository is a fork of Matt Clark's
[aes17_filter_25](https://github.com/mattclarkdotnet/aes17_filter_25) (V2, May 2024), itself a
DIY copy of the AUX-0025, released under the CERN-OHL-W 2.0. The V2 KiCad project, Gerbers,
case cut-outs and dissipation spreadsheet were removed from this tree because they no longer
describe this board; they are intact in the history, on the branch **`v2-mattclark`** (the GitHub proxy of this session refused to push a tag, so it is a branch). The licence
stays the CERN-OHL-W 2.0 (`LICENSE.txt`), and the source location of this derived design is
https://github.com/ToxSox/aes17_filter.

What changed against V2, and why, is argued at length in
[docs/design-review.md](docs/design-review.md), which also takes up the three changes the V2
README had planned (shielded coils: yes, the trimmer makes their tolerance irrelevant; a 60 V
goal: no gain; an SMD version: dearer for small runs). In short:

| | V2 (mattclarkdotnet) | this fork | why |
|---|---|---|---|
| Input resistor | 500 Ω 5 W fixed | AP's network: 1 kΩ 3 W ‖ 14 kΩ ‖ (1 kΩ 3 W + 500 Ω trimmer) | the trimmer sets the 20 kHz knee; V2 sits at +0.10 dB and spreads to 0.21 dB with 5 % coils, trimmed boards land at ±0.03 dB whatever the parts |
| Filter values | E24 approximations (330 Ω + 440 pF, 68 Ω, 3.3 kΩ, 22 Ω) | the AUX-0025's own (412 Ω + 2 × 220 pF, 75 Ω, 3.40 kΩ, 24.9 Ω), all E96 | 1-2 dB more in the stop band, nothing to lose |
| Pad | 9 kΩ / 1 kΩ, two poles per leg, hand-wired toggle | 2 × 10 kΩ / 1 kΩ (about 21.8:1), one pole per leg, a DPDT toggle wired into the footprint of an Omron G6A relay for later, pad at rest | the QA403 clips at 40 Vrms and loses 20 dB of floor above its +18 dBV range; 20:1 keeps a 2 kW amplifier below both |
| Connectors | XLR in and out, banana test points | the AUX-0025's: female XLR plus a dual-banana pair and a common in, male XLR out, through the chassis' front wall | one set of cables tests this filter and an AUX-0025 alike; a QA403 hangs on an XLR-to-two-BNC lead |
| Board | 175 × 90 mm, four layers | 158 × 124 mm, four layers, generated from a data file; all connectors on the front long edge; whole ground planes, 0.8 mm clearance, pad and switch at the output connector, one chassis bond at the input | the filter hangs with its connectors towards the operator, as the AUX-0025's front panel; the layout rules are in [hardware/README.md](hardware/README.md#layout-rules-it-follows) |
| Rating | "140 Vrms continuous" | a curve, per leg to ground: 85 Vrms to 12 kHz (the coils' 120 V), 53 Vrms at 20 kHz, 35 Vrms from 30 to 100 kHz (the trimmer's current) | at 20 kHz the shunt capacitors draw current through the input network: V2's single resistor takes 13 W at 140 V, and this build's trimmer reaches its rating at 56 V |
| Assembly | hand-built | JLCPCB, through-hole parts included, nothing hand-selected | the trimmer absorbs the tolerances |

## What is in the tree

| Path | What |
|---|---|
| [docs/design-review.md](docs/design-review.md) | the review of the V2 design against the AUX-0025 and the QA403, the simulation, the pad decision, the build decisions, the bill of materials, grounding with bridged amplifiers, the verification plan, safety |
| [docs/sourcing.md](docs/sourcing.md) | the shopping list with hard specifications, substitutes and open questions |
| [sim/aes17_sim.py](sim/aes17_sim.py) | the AC analysis that produced every number in the review (numpy only) |
| [hardware/](hardware/) | `design.py` (parts and nets as data), `make_pcb.py` (places, routes and checks the board with KiCad's `pcbnew`), `export.py` (Gerbers, BOM, placement), the schematic, the front-wall drilling, and [hardware/README.md](hardware/README.md) with the ordering steps |
| [hardware/fab/](hardware/fab/) | `aes17-filter-gerbers.zip`, `aes17-filter-bom.csv`, `aes17-filter-cpl.csv` for JLCPCB; `aes17-filter-parts.csv` with notes |

## Simulated performance

One leg against ground, 100 kΩ load, relative to 1 kHz; the script prints the full tables.

| | V2 as published | this fork, trimmed |
|---|---|---|
| Passband 20 Hz - 20 kHz | −0.00 / +0.10 dB nominal, up to 0.21 dB spread with ±5 % coils | within ±0.03 dB after trimming, whatever the coils and capacitors |
| −3 dB | 58 kHz | 58 kHz |
| 250 kHz | −53.6 dB | −52.5 dB (two 220 pF instead of 390 pF) |
| 500 kHz | −57.5 dB | −58.4 dB |
| 1 MHz | −69 dB | −70 dB |
| Insertion loss | −0.05 dB | −0.05 dB |
| Source noise at the analyzer | −124 dBV direct | −124 dBV direct, −122 dBV through the pad |
| Input resistor at 63 Vrms, 20 kHz | 2.7 W | 1.4 W in each of two |

A real box will land a few decibels short of the stop-band figures: one V1 build measured 45 dB
at 248 kHz against 55 simulated, and the 1 mH coils' self-resonance (1.3 MHz) takes 10-20 dB off
above 2 MHz, where the filter is 80 dB down anyway.

## Bill of materials, per board

The generated list is `hardware/fab/aes17-filter-bom.csv`; this is the same in words. Prices
are LCSC or JLCPCB's global-sourcing quote on 1 November 2026, single quantity.

| Qty | Part | For | Source | ≈ |
|---|---|---|---|---|
| 4 | **Würth WE-TIS 7447471102**, 1 mH ±10 %, shielded, 2.1 Ω, 0.46 A | L1-L4 | JLCPCB C1331105 (a JLCPCB part, not in LCSC's own shop), pre-order; JLCPCB lists it as ±20 %, the datasheet says ±10 %. Global sourcing quoted it at 2.74-3.37 € from Digi-Key, RS, Element14 and Mouser if ever needed. Fallback on the same footprint: unshielded Würth 7447480102, C1331132. The trimmer absorbs the tolerance: trimmed boards land within 0.029 dB (0.032 dB even at ±20 %) and need R1 between 484 and 540 Ω, well inside the network's 483-575 Ω | 2.9 € |
| 4 | UNI-ROYAL MFR03SF1001A10, 1.00 kΩ 1 % 3 W 50 ppm | input network | C58750 | $0.06 |
| 2 | 14.0 kΩ 1 % 0.25 W | input network | C127223 | $0.01 |
| 2 | Bourns 3296W-1-501LF, 500 Ω 25-turn trimmer | 20 kHz knee | C69564 | $0.97 |
| 6 | WIMA FKP2J002201D00HSSD, 220 pF 630 V ±2.5 % | C1, C5, and the bypass pairs C2+C9, C6+C10 (440 pF) | C5742108, pre-order | $0.23 |
| 4 | WIMA FKP2F014701I00JA00, 4.7 nF 250 V ±5 % | C3, C4, C7, C8 | C20412818, pre-order | $0.41 |
| 2 | 412 Ω 1 % 0.25 W, Yageo MFR-25FTE52-412R | bypass across L1 | C3558411 | $0.01 |
| 2 | 75.0 Ω 1 % 1 W, CCO MF1W | between the stages | C160685 | $0.05 |
| 2 | 3.40 kΩ 1 % 0.25 W, Yageo MFR-25FBF52-3K4 | across L3 | C3517441 | $0.02 |
| 2 | 24.9 Ω 1 % 0.25 W, Yageo MFR-25FBF52-24R9 | output | C3542579 | $0.03 |
| 4 | UNI-ROYAL MFR01SF1002A10, 10.0 kΩ 1 % 1 W | pad, upper arms (2 × 10 kΩ over 1 kΩ, about 21.8:1) | C58714 (Yageo MFR1WSFTE52-10K, C172916, as alternative) | $0.05 |
| 2 | TE YR1B1K0CC, 1.00 kΩ 0.1 % | pad, lower arm | C1364308 | $0.50 |
| 1 | 1 × 2 pin header 2.54 mm | relay coil | C492401 | $0.02 |
| 1 | 1N4148 DO-35 | flyback | C258182 | $0.03 |
| 0 | Omron G6A-274P-ST-US DC12 | K1, footprint only, for the relay matrix later | C129439 | - |
| 1 | Neutrik NC3FAAH2, female XLR, horizontal PCB | J4, input (pin 2 +, pin 3 −) | C368522, in stock | $0.84-1.80 |
| 1 | Neutrik NC3MAAH, male XLR, horizontal PCB | J5, output (pin 2 +, pin 3 −) | C368463, in stock | $0.79-1.80 |
| 3 | Cliff FCR7350 R / B / G, 4 mm safety sockets, at 19.05 mm for a dual banana plug | J1-J3 | C6041087 / C6555263 / C6041085, pre-order at $11-12, or 6.80 € at Digi-Key and soldered by hand | 7 € |

Not on the board, per board: eight M3 screws and nuts for the XLR flanges, one DPDT ON-ON
toggle with a 1/4 in bushing (its six wires go into K1's holes), one Hammond 1444-862 chassis
with its 1434-86 bottom plate and five 10 mm M3 spacers, the one under the plated hole H5 metal; and once for the bench a lead from the
amplifier terminals to a male XLR plug (or dual banana leads) and an XLR-female-to-two-BNC lead
for the QA403, both of which an AUX-0025 takes as well.

## Ordering and building

[hardware/README.md](hardware/README.md): upload the three files in `hardware/fab/` to JLCPCB,
five boards, two assembled, Economic. Every BOM line but the coils has an LCSC number; the coils
are requested as a global-sourcing part, four lines are pre-order parts (both WIMA capacitors,
the Cliff sockets), and the Cliff sockets are cheaper bought at Digi-Key and soldered by hand. Then drill the front wall after
`hardware/aes17-filter-frontwall.png`, trim both legs through an amplifier until 20 kHz equals
1 kHz, measure the pad ratio, and the filter is a probe profile in Klirr.

## Licence

CERN Open Hardware Licence Version 2 - Weakly Reciprocal, as the original. Copyright of the
original design Matt Clark 2023-2024; the changes described above and in the design review were
made in November 2026 in this repository. If you build or change it, the licence asks that you
keep these notices and make your changes available under the same terms.
