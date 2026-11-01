# AES17 filter: sourcing checklist

A work list for whoever (or whatever) goes shopping for the parts in
[design-review.md](design-review.md). **Update of 1 November 2026, evening:** a second pass through
LCSC's catalogue settled most lines; the result is the bill of materials in the main document and
the generated `hardware/fab/aes17-filter-bom.csv`. The BNC is the TE 5227161-7 with
the 1-329632-2 jam nut (both in stock), the 390 pF became two 220 pF, the pad's upper arms became
2 × 10 kΩ 1 W because 9.53 kΩ in 0.1 % is stocked nowhere through-hole, and the Cliff sockets are
pre-order at $11 each at LCSC against 6.80 € at Digi-Key. The 10 kΩ 1 W is the UNI-ROYAL
MFR01SF1002A10 (C58714) or the Yageo MFR1WSFTE52-10K (C172916); their stock is only visible in
the JLCPCB BOM tool. Still open below: the toggle, the box, and the Mouser/Reichelt cross-check. Everything known so far about stock and lead times comes from
**one distributor on one day: Digi-Key Germany, 1 November 2026.** Mouser (mouser.de) and
Reichelt (reichelt.de) were not reachable from the session that wrote the document, and neither
were Bürklin, Conrad, RS and TME product pages (403 or 503). All of them carry the same makers,
so nothing below is settled until it has been looked up there too.

How to use this: work through section 1 part by part, fill the result table in section 3, and
answer the questions in section 2 where a page says so. Record for every part the **exact
manufacturer part number, distributor order number, unit price at the quantity in the table,
stock on hand, stated lead time if out of stock, and the URL.** A part that only exists as a
reel or a 1 000-piece minimum is "not available" for this purpose. Where a specification is
marked *hard*, a part that misses it is not a substitute, however cheap.

Quantities are for **two boards plus the spares the document asks for**. Shops to check, in
this order: mouser.de, reichelt.de, digikey.de (to confirm the figures here have not moved),
buerklin.com, rs-online.de or conrad.de, tme.eu, and for inductors also Farnell/element14 and
soselectronic.com. For the enclosure, also hammfg.com for the drawing.

**Checked on 1 November 2026 at JLCPCB's parts shop** (the same C-numbers are on lcsc.com, which
ships parts on their own; at JLCPCB a part bought goes into the account's inventory for
assembly). All four are **pre-order items: the price shown is for reference and is confirmed
within 48 hours after payment**, and the lead time is whatever global sourcing takes, usually
two to four weeks. That is fine for this project and settles the four hardest lines:

| Part | C-number | Price shown | Minimum | What it settles |
|---|---|---|---|---|
| WIMA FKP2J002201D00HSSD, 220 pF 630 V **±2.5 %** | C5742108 | 0.23 € | 1 (30 pieces 6.93 €) | the 220 pF in a tight grade, by the piece - no 24 000-piece minimum, no selecting from 5 % lots needed, though measuring them still pays |
| WIMA FKP2F014701I00JA00, 4.7 nF 250 V ±5 % | C20412818 | 0.41 € | 19 (25 pieces 10.31 €) | the 4.7 nF, as at Digi-Key but cheaper |
| Vishay PAC500005000FAC000, 500 Ω 5 W 1 % | C1369475 | 0.49 € | 16 (7.87 €) | the repo's input resistor is **available** here, at a quarter of Digi-Key's back-ordered price - so the single-resistor variant without the trim network is open again, see 1.2 |
| Würth 7447480102, 1 mH ±5 %, WE-TI 120 V | C1331132 | 2.14 € | 4 (20 pieces 42.77 €) | the inductor, by the piece. The 120 V rating is enough (the coil never sees more than about 20 V); the HV sibling is the better part only if it costs the same |

Those four are the parts this build shares with the repo's BOM. The board is to be
**assembled by JLCPCB including the through-hole parts**, so every line should preferably be a
part JLCPCB can source (its own library, LCSC, or pre-order); no part is hand-selected, because
the trimmer absorbs the tolerances (see "Assembly" in the main document). Lots of twenty are
therefore no longer needed: the quantities below are per five boards for the parts JLCPCB
places, and per two boards for what goes on by hand (toggle, box, BNC leads). **What this
build adds or changes against the repo, and still has to be found:**

| Change in this build | Parts to find | Section | Likely at JLCPCB/LCSC? |
|---|---|---|---|
| AP's values instead of the repo's E24 ones | 412 Ω, 3.40 kΩ, 24.9 Ω (0.6 W), 75.0 Ω (1 W), all 1 % metal film; **390 pF 630 V polypropylene** instead of 2 × 220 pF | 1.4, 1.5 | resistors yes (E96 is standard there); 390 pF: look for WIMA FKP2J003901D00HSSD / JSSD or Kemet PFR |
| The 20 kHz trim | 2 × 1.00 kΩ 1 % 3 W per leg, 14.0 kΩ, **500 Ω 25-turn trimmer (Bourns 3296W-1-501LF)** | 1.2, 1.3 | trimmer yes; 3 W 1 % resistors: check Vishay RS02B / CPF3 or Chinese 3 W metal film 1 % |
| The 20:1 pad instead of 9 k / 1 k | 9.53 kΩ and 1.00 kΩ, **0.1 %**, 0.5 W, axial | 1.6 | 0.1 % axial is thin there; 1 % at 50 ppm is the stated fallback |
| Toggle in the end plate, relay footprint kept for the matrix | DPDT ON-ON panel toggle, 2 × 3 header (the Omron G6A-274P is not bought yet) | 1.7 | yes, toggles are commodity |
| BNC instead of XLR | 4 × PCB right-angle BNC with panel nut, **Molex 73100-0105** | 1.8 | yes, and Chinese equivalents; the panel nut is the thing to confirm |
| 4 mm safety sockets instead of Cliff test jacks | 3 × shrouded 4 mm PCB socket ≥ 20 A, **Cliff FCR7350 R/B/G** | 1.8 | Cliff unlikely; a shrouded Chinese 4 mm PCB socket at ≥ 20 A is acceptable if it is right-angle and the datasheet gives the rating |
| Closed extruded case instead of the open 1444 chassis | **Hammond 1455N1601** | 1.9 | no; Reichelt, Mouser, Bürklin, RS, Conrad |
| The board itself | four layers, ≤ 100 × 100 mm, five pieces | 1.10 | that is the shop |

Nothing in the repo's BOM beyond the four pre-order lines above carries over unchanged: the
XLRs, the Cliff FCR7350 test jacks at the input (kept, but three of them and as the amplifier
terminals), the 330 Ω / 68 Ω / 3.3 kΩ / 22 Ω values and the 2.7 kΩ / 1.8 kΩ pad are replaced.

Also still open: every question in section 2.

## 1. Parts

### 1.1 Inductors, 1 mH - 20 pieces (five boards)

| | |
|---|---|
| Hard | 1000 µH, **±5 % or better**, rated current ≥ 0.5 A, DCR ≤ 1.5 Ω, radial through-hole, 5 mm pin pitch (so it fits the one footprint), self-resonance ≥ 1 MHz |
| First choice | **Würth 7687480102** (WE-TI HV, 400 V DC rating). Digi-Key: 285 in stock, 1.61 €. Confirm at Mouser and Reichelt; buy where ten are in stock |
| Same coil, lower voltage rating | Würth 7447480102 (WE-TI, 120 V DC). Digi-Key: 0 in stock, back order to 26 May 2027; **JLCPCB/LCSC C1331132, pre-order, 2.14 €, minimum 4**. The 120 V rating is enough for this filter (the inductor never sees more than about 20 V), so this part is fully acceptable; at 2.14 € it is the fallback if the HV part is not in stock at 1.61 € |
| Other ±5 % radials, acceptable | Fastron 09P-102J-50 (±5 %, 2.6 Ω, 280 mA - DCR and current are below the hard line, only if nothing else exists), Hammond 1537R (±5 %, 0.83 Ω, 1.25 A, but Ø15 × 32 mm - fits only with a footprint change), TDK B78148S1105J000 (±5 %, 130 mA - too little current, reject) |
| Not acceptable as a straight swap | anything ±10 % or ±20 % (Bourns RLB1314-102KL, Würth WE-TIS 7447471102 / 744731102, Coilcraft RFS1317-105KL, Bourns SRR1280-102K, TDK B82477) - unless **twenty** are bought to select five matched pairs from, which is a legitimate plan if the price is low; then note it as such |
| Also check | whether Mouser or Farnell list **Coilcraft RFS1317-105KL** (shielded, ±10 %, 1.02 Ω, 0.68 A) with stock and price; it is the one shielded radial that could replace the Würth part by selection |

### 1.2 Input resistors, 1.00 kΩ 1 % 3 W - 6 pieces

| | |
|---|---|
| Hard | 1.00 kΩ, **1 %**, ≥ 3 W continuous, through-hole axial, working voltage ≥ 150 V. Wirewound is **fine** (AP uses Dale RS-2B wirewound here; a few µH in series with 1 mH is nothing) |
| First choice | **Vishay Dale RS02B1K000FE12** or any RS02B 1.00 kΩ 1 % variant (3 W, wirewound, the AP part family). Not checked at any shop yet |
| Equal | Vishay CPF3 1.00 kΩ 1 % (3 W metal film; Digi-Key had the 499 Ω variant CPF3499R00FKE14 at 2.19 €, 993 in stock - check the 1k and **find its working-voltage rating in the CPF datasheet**, it was not visible on Digi-Key), Stackpole WW3FT (3 W wirewound), Vishay NS02B (3 W non-inductive, about 5 €) |
| Note | the repo's part, **Vishay PAC500005000FAC000** (500 Ω 5 W), is not needed in the new network. It **is available at JLCPCB/LCSC as C1369475, pre-order, 0.49 €, minimum 16** (Digi-Key: back order to July 2027). That reopens the choice: one 500 Ω 5 W per leg and no trim (the repo as built, 20 kHz within about ±0.2 dB depending on the inductors), or AP's network with the trim (within ±0.02 dB after adjustment). The document's decision stands - the trim is what makes the board as flat as the original - but the PAC is the right part if the trim network's 1 kΩ 3 W resistors turn out hard to get: then 500 Ω fixed plus a 100 Ω trimmer in series with it is the poor man's trim (the trimmer then carries the full current, 0.5 W at 63 V and 20 kHz, so a 1 W or a 3296 at reduced range) |

### 1.3 Trimmer, 500 Ω multi-turn - 3 pieces

| | |
|---|---|
| Hard | 500 Ω, ≥ 0.5 W, 25-turn, through-hole, cermet |
| First choice | **Bourns 3296W-1-501LF** (top adjust) or 3296Y-1-501LF (side adjust). Commodity part, on LCSC; record price and stock |

### 1.4 Film capacitors - selected from lots

| Position | Qty to buy | Hard | First choice | Alternatives |
|---|---|---|---|---|
| 220 pF (C1, one per leg) | 10 | polypropylene (FKP/KP, film/foil), **≥ 400 V DC**, 5 mm pitch, 7.2 mm body | **Settled: WIMA FKP2J002201D00HSSD (630 V, ±2.5 %), JLCPCB/LCSC C5742108, pre-order, 0.23 €, minimum 1.** Eight is enough, since no selecting is needed; still measure them | Kemet PFR5221J630J11L4BULK (±5 %, 630 V, same footprint, 1.58 € at Digi-Key), Vishay KP1830122633 (±2.5 %, 630 V, 0.48 €, Digi-Key 0 stock), WIMA ±5 % JSSD if the pre-order falls through |
| 390 pF (bypass across L1, one per leg) | 10 | same as above | WIMA FKP2 390 pF 630 V, ±5 % or ±2.5 % (part number pattern FKP2J003901D00JSSD / …HSSD - confirm the exact code on the shop page) | Kemet PFR5391…630, Vishay KP1830 series 390 pF |
| 4.7 nF (C7, C9, two per leg) | 20 | polypropylene, **≥ 250 V DC**, 5 mm pitch, body ≤ 7.2 × 6.5 mm | **Settled: WIMA FKP2F014701I00JA00** (250 V, ±5 %), JLCPCB/LCSC C20412818, pre-order, 0.41 €, minimum 19 - or Digi-Key, 1 852 in stock, 0.67 €. Twenty, to select four pairs | WIMA FKP2F014701I00HSSD (±2.5 %, Digi-Key 5 000 minimum - **check Reichelt and the JLCPCB shop**), Kemet PFR5472F630J13L4BULK (±1 %, 630 V, Digi-Key 0 stock - **check Mouser**) |

No selection: ±5 % is fine with the trimmer. Tighter grades at the same price are welcome but
not worth a second shop.

### 1.5 Small resistors, 1 %, through-hole - 4 pieces each

| Value | Rating | First choice | Note |
|---|---|---|---|
| 14.0 kΩ | 0.6 W | any metal film 1 % (Vishay MRS25, Yageo MFR-25, KOA MF1/4) | commodity |
| 412 Ω | 0.6 W | same | E96 value, check the shop carries it in 1 % |
| 75.0 Ω | **1 W** | Vishay CMF60 75R0 or KOA MF1WS 75 Ω | the repo's CMF65 68 Ω is obsolete at Digi-Key (969 left); not needed |
| 3.40 kΩ | 0.6 W | any metal film 1 % | E96 |
| 24.9 Ω | 0.6 W | any metal film 1 % | E96 |

### 1.6 Pad resistors, 0.1 % - 10 × 9.53 kΩ, 5 × 1.00 kΩ

| | |
|---|---|
| Hard | **0.1 %**, ≤ 25 ppm/K, ≥ 0.5 W, through-hole axial |
| First choice | Vishay Dale CMF55 or PTF56 0.1 %, or Vishay MBB/MBE 0207 0.1 %; TE Connectivity Neohm, Welwyn RC55Y. Record whichever shop has both values in 0.1 % |
| Fallback | 0.1 % is a convenience, not a necessity - Klirr measures the ratio. If 0.1 % costs over 3 € a piece, take 1 % at ≤ 50 ppm/K and say so |

### 1.7 Pad switch and header - 2 pieces

| | |
|---|---|
| Hard | DPDT, ON-ON (two stable positions, no centre-off), panel mount for a 2 mm aluminium end plate, solder lugs, rated ≥ 1 A (the current is microamps; the rating is for contact quality) |
| First choice | any miniature toggle of that kind (APEM 5000 series, C&K 7201, Knitter MTA 206, or the shop's house brand). Record price and the panel hole diameter |
| Plus | one 2 × 3 pin header 2.54 mm per board, commodity |
| Not now | the **Omron G6A-274P-ST-US DC12** relay keeps its footprint on the board but is not bought until the matrix controller exists; if a shop has it cheaply, note the price for later |

### 1.8 Connectors

| Part | Qty | Hard | First choice | Alternatives / notes |
|---|---|---|---|---|
| BNC jack, PCB right angle | 10 | 50 Ω, right angle, through-hole, bulkhead nut so it can be fixed in the end plate | **Molex 73100-0105** (Digi-Key 1.95 €, 22 000 in stock) | Amphenol RF 31-5431 (4.97 €), TE 5227161-3 (4.68 €; the TE 1-1337543-0 is obsolete). **Confirm the chosen one's datasheet shows a threaded front and a panel nut** - the document relies on the jack being bolted to the end plate |
| 4 mm safety socket, PCB right angle | 7 (3 per board + 1) | shrouded 4 mm, ≥ 20 A, PCB mount, right angle, colours red / black / green | **Cliff FCR7350R / FCR7350B / FCR7350G** (Digi-Key 6.80-6.99 € each) | Electro-PJP 3263-PCB (25 A), Hirschmann/SKS only as panel mount (PKI 10 A, then wired to the board - acceptable). The 7 € apiece is the biggest single line in the BOM; a cheaper shrouded PCB socket at ≥ 20 A is welcome |

### 1.9 Enclosure - 2 pieces, plus the drawing

| | |
|---|---|
| Hard | extruded aluminium with PCB guide rails and two removable end plates; **inside length ≥ 120 mm, rail-to-rail width accepting a 100 mm board**, inside height ≥ 40 mm |
| First choice | **Hammond 1455N1601** (160 × 103 × 53 mm). Digi-Key 30.51 €, Bürklin 27.66 €, RS 24.92 €, Conrad lists 1455N1601BK as 534408. Reichelt not checked |
| Must be confirmed from the drawing | **the width between the rails** and the **rail slot width** of the 1455N series. Secondary sources say it takes a 100 mm Eurocard; Hammond's own PDF drawing (hammfg.com, "1455N1601" → drawing) is the authority. If the rails take less than 100 mm, the board goes down to the slot width or up to the 1455Q/1455P (125 mm wide) |
| Fallback | Hammond 1590D die-cast (188 × 120 × 58 mm, 25 €), board on standoffs, connectors through the walls |

### 1.10 The PCB

Not a shop item here; for completeness: JLCPCB, four layers, 1.6 mm, ≤ 100 × 100 mm, five
pieces, ENIG not required. Quote the price with shipping to Germany at the time of ordering.

## 2. Questions only a browser can settle

1. **Hammond 1455N rail width**, see 1.9.
2. **Vishay CPF3 working voltage**, see 1.2.
3. **WIMA tolerance grades by the piece**: does Reichelt (or Bürklin, TME, or the JLCPCB shop)
   sell FKP2 in ±2.5 % (code H) or ±1 % (code E) at 390 pF and 4.7 nF, 400 V or 630 V? The
   220 pF is settled. Give part numbers and prices.
4. **Mouser stock** for every "0 in stock" and "back order" line above: Würth 7447480102,
   Vishay PAC500005000FAC000, Vishay KP1830122633, Kemet PFR5472F630J13L4BULK.
5. **Omron G6A-274P-ST-US DC12** price at Mouser, Reichelt and LCSC, for later (Reichelt lists
   Omron signal relays under its own names; search "G6A-274P"). Not needed for the first build.
6. **Two BNC leads**, male to male, 50 Ω, 20-30 cm, equal length, for the filter's output to
   the QA403's L+ and L−: a shop and a price. (The QA403 is connected by cable; its front-panel
   BNC pitch does not matter.)

## 3. Result table

Copy, fill, and paste back into this file (or into a comment on the pull request).

| Line | Part number chosen | Shop and order number | Unit price (qty) | Stock | Lead time if none | URL | Deviation from first choice and why |
|---|---|---|---|---|---|---|---|
| 1.1 inductors ×20 | Würth 7447480102 (fallback; HV part preferred if 1.61 €) | JLCPCB/LCSC C1331132, pre-order | 2.14 € (20: 42.77 €) | pre-order | 2-4 weeks, price confirmed after payment | | 120 V rating, acceptable |
| 1.2 1.00 kΩ 3 W ×6 | | | | | | | |
| 1.3 trimmer ×3 | | | | | | | |
| 1.4 220 pF ×10 | WIMA FKP2J002201D00HSSD ±2.5 % | JLCPCB/LCSC C5742108, pre-order | 0.23 € | pre-order | 2-4 weeks | | |
| 1.4 390 pF ×10 | | | | | | | |
| 1.4 4.7 nF ×20 | WIMA FKP2F014701I00JA00 ±5 % | JLCPCB/LCSC C20412818, pre-order (min 19) | 0.41 € (25: 10.31 €) | pre-order | 2-4 weeks | | |
| 1.5 small resistors | | | | | | | |
| 1.6 9.53 kΩ 0.1 % ×10 | | | | | | | |
| 1.6 1.00 kΩ 0.1 % ×5 | | | | | | | |
| 1.7 toggle ×2 | | | | | | | |
| 1.8 BNC ×10 | | | | | | | |
| 1.8 4 mm sockets ×7 | | | | | | | |
| 1.9 enclosure ×2 | | | | | | | |
| 2.1 1455N rail width | | | | | | | |
| 2.2 CPF3 voltage | | | | | | | |
| 2.6 BNC leads ×2 | | | | | | | |

A total at the bottom, with shipping per shop, decides whether it is one order or three.
