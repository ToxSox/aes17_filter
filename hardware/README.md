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

The input end plate carries, top to bottom seen from inside: BNC IN + (from the matrix bus),
red 4 mm IN +, green 4 mm GND, black 4 mm IN −, BNC IN −. The output plate carries BNC OUT +,
the pad toggle, BNC OUT −. The connectors' fronts stick out through the plates: the BNCs are
held by their nuts, the Cliff sockets by the board alone (they have no panel retention; the
plate just has a clearance hole for the Ø11 barrel).

## Ordering at JLCPCB

1. **PCB.** Upload `fab/aes17-filter-gerbers.zip`. Four layers, 1.6 mm, any colour, 1 oz copper,
   HASL or ENIG as you like, five pieces (the minimum). The stack-up JLCPCB offers for four
   layers (JLC04161H-7628 or similar) is fine; nothing here depends on impedance.
2. **Assembly.** Tick assembly, **two boards**, top side only, Economic. Upload
   `fab/aes17-filter-bom.csv` and `fab/aes17-filter-cpl.csv`. All parts are through-hole;
   JLCPCB hand-solders those ($3.58 per order plus $0.0164 per joint, one extra day).
3. **Parts review.** In the parts page every line with an LCSC number resolves on its own. **The
   coils L1-L4 have no LCSC number on purpose**: the Würth WE-TIS 7447471102 is not in LCSC's
   catalogue, so for that line choose "Global Sourcing Parts" (or request the part by number in
   the parts manager before uploading) and let JLCPCB quote it. On 1 November 2026 their quote
   came back from four distributors: Digi-Key 3.01 € (339 in stock, 8-14 business days), RS
   2.74 € at five, Element14 2.97 €, Mouser 3.37 € - so about 29 € for the ten coils. If sourcing
   ever fails, assign the Würth 7447480102, C1331132, pre-order, which fits the same footprint
   and loses only the shielding. Four more lines are **pre-order** (both WIMA capacitors, the Cliff sockets): JLCPCB
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

## What is not on the board

| Qty for two boards | Part | Where |
|---|---|---|
| 8 | TE 1-329632-2 jam nut, 1/2-28, for the BNCs (the -7 ships without) | LCSC C305927, $0.51, or any 1/2-28 UNEF nut |
| 2 | DPDT toggle, ON-ON, panel mount, 1/4 in bushing, solder lugs | any; APEM 5000, C&K 7201, Knitter MTA 206 |
| 2 | Hammond 1455N1601 (or 1455N1601BK black) | Reichelt, Mouser, Digi-Key, RS, Conrad |
| 4 | BNC lead, male to male, 50 Ω, 20-30 cm, two equal per board | any |
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
| input | BNC IN + | 12.9 | 15.6 | 14.9 |
| input | 4 mm IN + (red) | 11.5 | 33.6 | 14.3 |
| input | 4 mm GND (green) | 11.5 | 51.6 | 14.3 |
| input | 4 mm IN − (black) | 11.5 | 69.6 | 14.3 |
| input | BNC IN − | 12.9 | 87.6 | 14.9 |
| output | BNC OUT + | 12.9 | 81.6 | 14.9 |
| output | BNC OUT − | 12.9 | 21.6 | 14.9 |
| output | pad toggle, 1/4 in bushing | 6.4 | 51.6 | 34.0 |

The y values assume the board's top surface 8.0 mm above the plate's bottom edge (lowest rail,
6.4 mm floor to slot plus the 1.6 mm board); the BNC axis is 6.9 mm and the Cliff socket axis
6.3 mm above the board. The TE drawing gives the BNC's panel cut-out as Ø12.83 with a D-flat
5.54 mm from the centre; a round Ø12.9 hole works with the nut tightened, the flat only stops
rotation. Cliff does not specify a panel hole for the S16N-PC; Ø11.5 clears its Ø11.0 barrel.
