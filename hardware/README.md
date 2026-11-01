# AES17 filter board: files and how to order

The passive class-D measurement filter from [docs/design-review.md](../docs/design-review.md),
as a board. Everything here is generated from `design.py`; nothing was drawn by hand, so a
changed value or part is a changed line and a re-run.

| File | What it is |
|---|---|
| `design.py` | every part with value, footprint, LCSC number and note; every net |
| `make_pcb.py` | places and routes the board with KiCad 7's `pcbnew` module, fills the ground planes, runs the DRC; writes `aes17-filter.kicad_pcb` |
| `export.py` | writes `fab/`: the Gerber + drill zip, the JLCPCB bill of materials and placement file, a parts list with notes |
| `make_schematic.py` | draws `aes17-filter-schematic.svg/.png` (schemdraw) |
| `make_endplates.py` | draws the two end plates' drilling, `aes17-filter-endplates.svg/.png` |
| `aes17-filter.kicad_pcb` | the board, for KiCad 7 or newer; there is no `.kicad_sch`, the schematic is the drawing |
| `fab/aes17-filter-gerbers.zip` | upload this to JLCPCB |
| `fab/aes17-filter-bom.csv` | upload this as the BOM (Comment, Designator, Footprint, LCSC Part #) |
| `fab/aes17-filter-cpl.csv` | upload this as the placement file (Designator, Mid X, Mid Y, Layer, Rotation) |
| `fab/aes17-filter-parts.csv` | the same parts with values and notes, for ordering anything elsewhere |

![top side](aes17-filter-top.png)

## The board

100 × 158 mm, four layers, 1.6 mm. 100 mm because the Hammond 1455N1601's rails take a 100 mm
board (confirmed from Hammond's drawing: "extrusion designed for 100 mm wide PC board", slot
100.00 ± 0.51 mm, 1.6 mm wide). 158 mm because the connectors on the two short edges pass
through the box's end plates and the extrusion is 160 mm long. Layer 1 carries the signal, layer
2 is a ground plane, layer 3 a ground plane with the two filter-output tracks to the switch in
it, layer 4 the few crossings. Both legs are mirror images about the centre line. The DRC in
KiCad 7 reports no errors and no unconnected nets; the warnings it does report are silkscreen
over pads and the footprints not being from a library table.

The connectors are the AUX-0025's, so the same cables fit both: the input end plate carries a
female XLR (pin 2 +, pin 3 −, pin 1 and shell ground) and, next to it, red and black 4 mm
sockets at 19.05 mm for a dual banana plug and a green common; the output plate carries a male
XLR (pin 2 +, pin 3 −) and the pad toggle. The QA403 is fed through a self-made lead, XLR
female to two BNC males. The connectors' fronts stick out through the plates: the XLRs are
screwed to the plate, the Cliff sockets held by the board alone (they have no panel retention;
the plate just has a clearance hole for the Ø11 barrel).

## Ordering at JLCPCB

1. **PCB.** Upload `fab/aes17-filter-gerbers.zip`. Four layers, 1.6 mm, any colour, 1 oz copper,
   HASL or ENIG as you like, five pieces (the minimum). The stack-up JLCPCB offers for four
   layers (JLC04161H-7628 or similar) is fine; nothing here depends on impedance.
2. **Assembly.** Tick assembly, **two boards**, top side only, Economic. Upload
   `fab/aes17-filter-bom.csv` and `fab/aes17-filter-cpl.csv`. All parts are through-hole;
   JLCPCB hand-solders those ($3.58 per order plus $0.0164 per joint, one extra day).
3. **Parts review.** In the parts page every line with an LCSC number resolves on its own,
   including the coils: the Würth WE-TIS 7447471102 is JLCPCB part **C1331105** (not in LCSC's
   own shop, which is why the first search missed it; JLCPCB lists it as ±20 %, the datasheet
   says ±10 %, and the trimmer covers either). It is a pre-order part like the WIMA capacitors;
   JLCPCB's global-sourcing quote of 1 November 2026, should it be needed instead, was Digi-Key
   3.01 € (339 in stock, 8-14 business days), RS 2.74 € at five, Element14 2.97 €, Mouser 3.37 €.
   The unshielded Würth 7447480102, C1331132, fits the same footprint and is the fallback. The
   BOM file is plain ASCII on purpose: JLCPCB's import reads "Würth" as "W眉rth". Four more lines are **pre-order** (both WIMA capacitors, the Cliff sockets): JLCPCB
   buys them after payment, quotes the final price within 48 hours, and they take nine to
   twenty business days to arrive; connectors carry a $20 inspection fee per type, so the three
   Cliff colours cost $60 in inspection alone. The cheaper route for the Cliff sockets is to
   **leave them out of the assembly** (delete J1, J2, J3 from the BOM upload), buy them at
   Digi-Key (6.80 € each against $11-12 pre-order) and solder the three per board yourself - one
   pin and four pegs each.
4. **Every line has an LCSC number.** Two were found without a stock figure visible from
   here: the pad's 10 kΩ 1 W resistors (R8, R9, R18, R19) are the UNI-ROYAL MFR01SF1002A10,
   C58714, with the Yageo MFR1WSFTE52-10K, C172916, as the alternative if the first shows no
   stock in the BOM tool; both fit the 15.24 mm footprint.
5. **Do not place K1.** It is marked "do not place" in the files and is not in the BOM; the
   footprint waits for the matrix controller.
6. After the order: the five boards arrive, two assembled. Nothing else is needed from JLCPCB.

### What JLCPCB's BOM tool quoted on 1 November 2026

For an assembly of five boards (quantities include JLCPCB's attrition allowance), in euros:

| Line | Qty | Total | Per piece | Status |
|---|---|---|---|---|
| TE 5227161-7 BNC (C591726) | 20 | 99.63 | 4.98 | in stock; no longer on the board - the XLR output replaced the BNCs |
| Cliff FCR7350R / B / G (C6041087 / C6555263 / C6041085) | 5 each | 58.13 / 58.13 / 50.32 | 11.6 / 11.6 / 10.1 | **shortage: pre-order**, plus the connector inspection fee per type |
| WIMA 220 pF 630 V ±2.5 % (C5742108) | 30 | 7.19 | 0.24 | shortage: pre-order |
| WIMA 4.7 nF 250 V (C20412818) | 25 | 10.70 | 0.43 | shortage: pre-order |
| Bourns 3296W-1-501LF (C69564) | 10 | 6.75 | 0.67 | in stock |
| TE YR1B1K0CC 0.1 % (C1364308) | 10 | 3.57 | 0.36 | in stock |
| UNI-ROYAL 1 kΩ 3 W (C58750) | 21 | 1.04 | 0.05 | in stock |
| UNI-ROYAL 10 kΩ 1 W (C58714) | 21 | 0.51 | 0.02 | in stock |
| 75 Ω 1 W (C160685) | 11 | 0.47 | 0.04 | in stock |
| 14 k, 412, 3.4 k, 24.9 (C127223, C3558411, C3517441, C3542579) | 11-15 each | 0.15 / 0.06 / 0.17 / 0.36 | 0.01-0.02 | in stock |
| 1N4148 (C258182), headers (C65114, C492401) | 10 / 5 / 5 | 0.26 / 0.20 / 0.08 | | in stock |
| Würth 7447471102 coils | 20 | about 58 | 2.9 | unmatched by design: "Vorbestellen" → global sourcing |

About 356 € of parts for five assembled boards, 71 € per board, of which the three Cliff sockets
are 33 € and the four BNCs 20 € (the BNCs have since left the board). The Cliff sockets are the line to take out of the assembly:
pre-order at 11 € each plus the inspection fee, against 6.80 € at Digi-Key for a part with one
pin and four pegs to solder. Assembling two boards instead of five brings the parts to about
140 € plus the coils.

## What is not on the board

| Qty for two boards | Part | Where |
|---|---|---|
| 8 | M3 × 8 screws and nuts for the XLR flanges | any |
| 1 | a cable from the amplifier's terminals to a male XLR plug (pin 2 +, pin 3 −), or dual banana leads - the same cable then feeds an AUX-0025 | self-made |
| 2 | an XLR-female-to-two-BNC-male lead to the QA403: pin 2 to L+ centre, pin 3 to L− centre, pin 1 to both BNC shells; about 30 cm, both legs equal | self-made (Neutrik NC3FXX, two BNC plugs, two pieces of RG58 or RG174) |
| 2 | DPDT toggle, ON-ON, panel mount, 1/4 in bushing, solder lugs | any; APEM 5000, C&K 7201, Knitter MTA 206 |
| 2 | Hammond 1455N1601 (or 1455N1601BK black) | Reichelt, Mouser, Digi-Key, RS, Conrad |
| 6 | Cliff FCR7350 R, B, G if bought outside JLCPCB | Digi-Key, Farnell |
| | wire for the toggle: six short pieces to J8 | |

## Building the two boards

1. Check the assembled board against `fab/aes17-filter-parts.csv`; measure the four coils if
   an LCR meter is at hand (not required, the trimmer takes care of their spread).
2. Drill the end plates after `aes17-filter-endplates.png`. The hole table is at the end of this
   file. The drawing assumes the board in the **lowest rail**; the plate's holes move up by one
   rail pitch per rail, so measure the box and the rail you use before drilling. Easiest: slide
   the board in, hold the undrilled plate against the connector fronts, mark through from
   inside.
3. Slide the board in, fit the plates, nuts on the BNCs.
4. Wire the toggle to J8: lugs of pole A to pins 1 (pad), 3 (common), 5 (direct); pole B to
   2, 4, 6. Check with an ohmmeter that in one position pin 3 reads to pin 1 and 4 to 2, in the
   other 3 to 5 and 4 to 6.
5. Trim and measure the ratios as in the bring-up list of
   [docs/design-review.md](../docs/design-review.md): both trimmers through an amplifier until
   20 kHz equals 1 kHz, then the pad ratio at 1 kHz, into Klirr's probe profiles.

## Regenerating

```
python3 hardware/make_pcb.py        # board + DRC report (needs KiCad 7 with pcbnew for Python)
python3 hardware/export.py          # fab/ (needs kicad-cli)
python3 hardware/make_schematic.py  # schematic (pip install schemdraw)
python3 hardware/make_endplates.py  # end plates (matplotlib)
```

## End plate holes

See `aes17-filter-endplates.png`; the table below is printed by `make_endplates.py`.

| Plate | Hole | Ø mm | x from left, seen from inside | y above the bottom edge |
|---|---|---|---|---|
| input | XLR IN (female), Neutrik NC3FAAH2 | 22.5 | 22.2 | 20.5 |
| input | its two M3 screws | 3.2 | 32.1 / 12.3 | 30.4 / 10.6 |
| input | 4 mm IN + (red) | 11.5 | 51.6 | 14.3 |
| input | 4 mm IN − (black) | 11.5 | 70.6 | 14.3 |
| input | 4 mm GND (green) | 11.5 | 89.6 | 14.3 |
| output | XLR OUT (male), Neutrik NC3MAAH | 22.5 | 81.6 | 20.5 |
| output | its two M3 screws | 3.2 | 71.7 / 91.5 | 30.4 / 10.6 |
| output | pad toggle, 1/4 in bushing | 6.4 | 51.6 | 34.0 |

The y values assume the board's top surface 8.0 mm above the plate's bottom edge (lowest rail,
6.4 mm floor to slot plus the 1.6 mm board); the Cliff socket axis is 6.3 mm above the board.
**The XLR axis height of 12.5 mm is read off Neutrik's front view, not a dimensioned value: hold
a connector against the board before drilling.** Cliff does not specify a panel hole for the
S16N-PC; Ø11.5 clears its Ø11.0 barrel. Neutrik asks for a hole of at least Ø22 and two Ø3.2
screw holes 19.8 mm apart on the diagonal.
