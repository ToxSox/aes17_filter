# The AES17 filter

A passive low-pass between a class-D amplifier and the QA403, so that the amplifier's switching
residue never reaches the analyzer's input stage. Audio Precision sells this as the AUX-0025;
Matt Clark's [aes17_filter_25](https://github.com/mattclarkdotnet/aes17_filter_25) (V2, May
2024, CERN-OHL-W) is a DIY copy of it, and this repository is a fork of it. This document reviews
that design against what a bench with a QuantAsylum QA403 needs, with the numbers to argue with, and says what this fork changes. It was
written before anything was ordered; the status of the build is in the [README](../README.md).

Decided: **single-channel boards**, two built from the five-board minimum order. **The
AUX-0025's connectors and nothing else**, so that one set of cables serves both filters: a
female XLR and a dual banana pair in, a male XLR out; the QA403 is fed through an
XLR-to-two-BNC lead.
**The topology and the impedance level stay as they are** - the design is a faithful copy of the
AUX-0025 and nothing found below beats it for the money. What changes: the **20 kHz knee gets a
trim**, the **pad becomes 20:1**, switched by a 4PDT toggle that takes it off the output in DIRECT
it, the **inductors are the unshielded ±5 % drum cores** V2 measured, and the **voltage rating
is stated honestly** as a curve rather than a number. The reasoning follows. (Revised on
2 November 2026 after a second outside review: the pad's load and leg matching, the rating
above 70 kHz, the coil, and a pad switch that takes the pad off the output in DIRECT.)

## What the filter is for, on a QA403

The QA403's own anti-aliasing is good: its product sheet shows a 0 dBV tone at 346 kHz
suppressed by more than 120 dB at its alias, and QuantAsylum themselves say they have not met a
class-D amplifier that needed a pre-filter. So the filter does not exist to keep the carrier out
of the FFT. It exists for three other reasons:

- **The input stage.** A modern module leaves 0.25-0.35 Vrms of residual at 400-620 kHz on the
  speaker terminals (Purifi quotes 0.25 Vrms for the 1ET9040BA; a Hypex NC252MP was measured at
  340 mV; an 80 kHz output filter raises that to about 2 Vrms). Through a 20:1 pad that is still
  10-100 mV of fast edges into a buffer that was designed for audio. AP's reason for the AUX
  family is exactly this: slew-induced distortion in the analyzer's front end, which shows up as
  IMD that is not the amplifier's.
- **Ranging.** Auto-ranging goes by the peak the analyzer sees. A carrier riding on the signal costs
  headroom and, in the worst case, clips a range the audio alone would have fitted.
- **DC and relay cycling.** A single-supply module idles at half its rail. The QA403's input is
  AC-coupled below 1 Hz, so the step at power-on walks through the ranges and QuantAsylum's forum
  has a thread on the attenuator relay cycling on it. The filter does not fix that, but it is
  where the 20 kHz residue of the step is absorbed instead of the analyzer.

What the filter will **not** do is lower the noise floor of a measurement. The QA403's 20 kHz
bandwidth already ends where the filter starts. Any "more signal-to-noise" has to come from where
the signal sits in the analyzer's ranges, which is the pad's job, below.

## What the repo design is

The repository's XML netlist export is stale (it is V1, with Zener clamps at the output that were
removed in October 2023 because they cost 5 dB of noise). The real V2 circuit is in the PCB file,
and per leg against ground it reads:

```
amp  ──[ R1 500 Ω 3-5 W ]──┬──[ L1 1 mH ]──────────┬──[ R5 68 Ω ]──┬──[ L3 1 mH ]──┬──[ R9 22 Ω ]──┬── out
                           │   ╰─[ R3 330 ]─[ C 440 p ]─╯             │   ╰─[ R7 3.3 k ]─╯            │
                        C1 220 p                   C7 4.7 n          │                C9 4.7 n     pad 9 k / 1 k
                           │                        │                 │                   │            │
                          GND                      GND               GND                 GND          GND
```

Both legs are identical, every shunt capacitor goes to ground (so the stop band applies to
common-mode as well as differential signals), the two legs meet only at the XLR shells, and a
switchable 9 kΩ / 1 kΩ pad sits after the 22 Ω. It is a transcription of the AUX-0025 into
E-series values. The AUX-0025's circuit was traced and published in 2015 (Cranial Crumbs, "Audio
Precision's class D filter"; AP's own 2003 white paper confirms the topology and the "500 Ω in
series with 10 nF per side" input model):

| Position | AUX-0025 (traced) | aes17_filter_25 V2 | Note |
|---|---|---|---|
| Series input | 1.0 k 3 W ‖ 14.0 k ‖ (1.0 k 3 W + 200 Ω trimpot) ≈ 467-520 Ω | 500 Ω 3-5 W fixed | **the trim is the 20 kHz knee adjustment** |
| First shunt | 220 pF 400 V | 220 pF 250 V | |
| First inductor + bypass | 1 mH, 412 Ω + 390 pF 630 V across it | 1 mH, 330 Ω + 440 pF across it | |
| Second shunt | 4700 pF 630 V | 4.7 nF 250 V | |
| Series between stages | 75.0 Ω | 68 Ω | |
| Second inductor + damping | 1 mH, 3.40 k across it | 1 mH, 3.3 k across it | |
| Third shunt | 4700 pF 630 V | 4.7 nF 250 V | |
| Series output | 24.9 Ω | 22 Ω | |
| Inductors | 28 AWG on a PQ2625 bobbin, **no core** (air) | Würth 7687480102 (WE-TI HV) ferrite drum core, ±5 %, 1.0 Ω, SRF 1.3 MHz | the one real difference |
| Pad | none | 9 k / 1 k after the output resistor, switchable | |

So "is the design state of the art" has a short answer: it *is* the state of the art, because it
is the AUX-0025, and AP has not changed that circuit since 2003. There is no newer topology in
the DIY world to move to. Every published alternative (the Clockworks matched-impedance filter
of 2018, Redako's compact board of 2025, the "Audioidiot" air-core build on ASR in 2026, E1DA's
gentler LC board) is either the same circuit with different parts or a worse trade.

## Simulated behaviour

The numbers below are from a nodal AC analysis of one leg against ground
([sim/aes17_sim.py](../sim/aes17_sim.py); it needs only numpy and prints every table in this
section). It reproduces the repo's published curve, which is the check that the
netlist above is right.

![Simulated transfer of the filter](images/response.png)

**Passband.** Into 100 kΩ, relative to 1 kHz, the V2 values peak by **+0.10 dB at 20 kHz**; the
repo quotes this as "±0.05 dB" by centring it. The AUX-0025 values give +0.075 dB; with the
analyzer's 100 kΩ and about 185 pF of input plus cable it is +0.05 dB, and AP then trims each leg
to flat with the pot. The −3 dB point is 58 kHz. Load dependence is only insertion loss:
−0.05 dB into 100 kΩ, −0.1 into 50 kΩ, −0.5 into 10 kΩ, with the same shape. **This board takes
the pad off the output in DIRECT** (two switch poles per leg), so DIRECT is the bare filter into
the analyzer, −0.05 dB or 1.006:1, as on the AUX-0025. An intermediate version left the pad's
21 kΩ on the output in both positions; that cost 0.30 dB and, through the trim, 14 dB of
rejection at 50 Hz (`build_tables()` and `cmrr()` print both positions).

**Stop band.** −53.6 dB at 250 kHz, a shelf at −52 to −58 dB through 500 kHz (the bypass
resistor across each inductor sets it), −69 dB at 1 MHz, then falling 12 dB per octave. The
AUX-0025 values are within 1-2 dB of this everywhere. One V1 build measured only 45 dB at
248 kHz on an HP 3585A; parasitics and layout eat something, so expect 45-50 dB in a real box.

**What does not matter.** Magnetic coupling between the two inductors of one leg changes the
stop band by under 2 dB even at k = 3 % (they are in series, so the coupled path mostly adds to
the wanted one); coupling is linear and cannot by itself add distortion, only move the curve. The Würth part's self-resonance (parallel capacitance of 15-30 pF) costs 10-20
dB only above 2 MHz, where the filter is already 80 dB down. DCR between 0.3 and 3 Ω moves the
20 kHz figure by 0.02 dB. So the V2 author's "space the inductors out" is harmless but was not
what fixed his HD3 problem; see the ASR section.

**What does matter: tolerances.** 400-sample Monte Carlo on the passband, all parts at the
edges of their stated tolerance, 100 kΩ load:

| Parts | Passband spread 20 Hz-20 kHz, worst / 95 % | 20 kHz relative to 1 kHz | Worst rejection 250-500 kHz |
|---|---|---|---|
| L ±5 %, C ±2.5 %, R ±1 % (repo BOM) | 0.21 / 0.17 dB | +0.01 to +0.21 dB | 51.4 dB |
| L ±10 %, C ±2.5 % (shielded-inductor option) | 0.28 / 0.22 dB | −0.06 to +0.28 dB | 50.7 dB |
| L ±2 %, C ±1 % | 0.16 / 0.14 dB | +0.05 to +0.16 dB | 52.1 dB |

Tighter parts alone do not reach the AUX-0025's ±0.05 dB, because the nominal already sits at
+0.10. What does reach it is **R1 as a trim**: between 487 and 520 Ω the 20 kHz figure swings
from +0.15 to −0.06 dB, with nothing else moving (250 kHz changes by 0.1 dB). That is why AP has
a pot there, and it is the single change that makes a DIY board as flat as the original.
Alternatively a fixed re-centring - R7 4.7 k and C9 5.6 n instead of 3.3 k and 4.7 n - halves
the spread (−0.03 / +0.02 dB nominal) and adds 2 dB at 250 kHz, but it cannot follow the
inductors you actually received; the trim can.

**Leg matching.** The QA403, like an APx, subtracts its + and − inputs in the analogue input
stage, so whatever differs between the two legs turns common mode into signal, and no per-channel
probe factor in software can take it out again. `cmrr()` in the simulation builds both legs from
parts drawn within tolerance, trims each alone as below, and drives them together; the 95th
percentile of the common mode that reaches the analyzer as difference:

| Parts (each leg trimmed alone in DIRECT) | 50 Hz | 1 kHz | 10 kHz | 20 kHz | 100 kHz |
|---|---|---|---|---|---|
| coils ±5 %, pad all 0.1 % (**as built**), DIRECT (pad off) | **−74 dB** | −58 dB | −38 dB | −31 dB | −15 dB |
| the same, PAD | **−52 dB** | −52 dB | −38 dB | −31 dB | −15 dB |
| pad with 1 % upper arms (rev A as first drawn), PAD | **−36 dB** | −36 dB | −35 dB | −31 dB | −15 dB |
| pad left on the output in DIRECT (the intermediate version) | −59 dB | −57 dB | −38 dB | −31 dB | −15 dB |
| coils ±20 % (the WE-TIS as JLCPCB lists it), DIRECT | −64 dB | −49 dB | −28 dB | −21 dB | **−5 dB** |
| coils ±5 % paired to 1 % between the legs, DIRECT | −76 dB | −60 dB | −40 dB | −33 dB | −19 dB |
| coils ±5 %, untrimmed, DIRECT | −81 dB | −55 dB | −35 dB | −29 dB | −15 dB |

Three things follow. The pad's resistors must match between the legs, not only be known: with
1 % upper arms the pad position let 1.5 % of any hum or common-mode residue through, so all
three pad resistors are now 0.1 % / 15 ppm parts of one family. The coils' tolerance is what
sets the top of the band, which is the second reason (after linearity) for the ±5 % part.
And trimming each leg alone costs low-frequency rejection: the legs end up with different R1
(495-534 Ω) against whatever loads the output, a gain difference of up to 0.3 % against the
pad's 21 kΩ but only 0.02 % against the analyzer's 100 kΩ - the main reason the pad comes off
the output in DIRECT. In PAD it is on, so PAD stays at −52 dB at mains frequency. Pairing the
coils between the legs (an LCR meter, four coils, ten minutes) buys 2-4 dB; it is worth doing
when the coils are soldered by hand, and not a reason to give up JLCPCB's assembly. Bridged
amplifiers put little common mode in the audio band; these are figures to measure (test 3
below), not to assume.

**Dissipation, and the honest voltage rating.** The shunt capacitors draw current at the top
of the band, and all of it flows through R1. In V2, with its single 500 Ω resistor:

| At the amplifier | 1 kHz | 20 kHz | Output shorted, 1 kHz |
|---|---|---|---|
| 45 V (500 W / 4 Ω) | 0.00 W in R1 | **1.4 W in R1**, 52 mA in L1 | 2.9 W |
| 63 V (1000 W / 4 Ω) | 0.01 W | **2.7 W**, 73 mA | 5.7 W |
| 89 V (2000 W / 4 Ω) | 0.01 W | **5.4 W**, 103 mA | 11.4 W |
| 140 V (repo's "max") | 0.04 W | **13.3 W**, 161 mA | 27.9 W |

The repo's silkscreen says "140 Vrms continuous into >10 k load". That is true at 1 kHz and
false at 20 kHz, where a 5 W resistor is at 2.5 times its rating. AP rates the AUX-0025 as
140 Vrms "DC to 7.5 kHz, decreasing to 53 Vrms from 20 kHz to 2 MHz" for exactly this reason.

**This build's rating, per leg to ground** (`rating()` in the simulation, each limit at the
trimmer setting worst for it):

| Frequency | up to 15 kHz | 20 kHz | 30 kHz | 50 kHz | 100 kHz | 250 kHz | 500 kHz | 1 MHz |
|---|---|---|---|---|---|---|---|---|
| Sine, Vrms per leg | **75** | **57** | 41 | 36 | 37 | 45 | 34 | 31 |
| set by | the pad's 10 k | trimmer | trimmer | trimmer | R6 3.40 k | R4 412 Ω | R4 | R4 |

Stated as **75 Vrms per leg to 15 kHz, 55 Vrms at 20 kHz, 30 Vrms from 30 kHz to 1 MHz.** Every
resistor is held to half its rating in the closed box. The first version of `rating()` checked
only the input network, the trimmer, the pad and the coils, and so claimed 85 Vrms above
100 kHz; an outside review found that the two small resistors around the coils carry the stop
band: **R6/R16** (3.40 kΩ across L2) near the second stage's resonance, and **R4/R14** (412 Ω in
series with the 440 pF bypass) above 150 kHz, where L1 has the whole input across it. As
0.25 W parts they reached half their rating at 25 Vrms at 100 kHz and 22 Vrms at 500 kHz - the
carrier of a filterless class-D output can be that. Both are now **0.6 W Vishay MRS25 /
MBB0207** in the same 0207 body and footprint. The parts that set it:

- **The pad, below 15 kHz.** The 10 kΩ upper arms are 0.25 W precision parts (TE YR1B, chosen
  for 0.1 % and 15 ppm, see "The pad"); at half their rating they take 74 Vrms per leg. The
  coils' 120 V (read as node to ground, 85 Vrms) is no longer the limit.
- **The trimmer, above 12 kHz.** The Bourns 3296 is rated 0.5 W at 70 °C over its whole 500 Ω
  element, and used as a rheostat it is the current through the part in use that the element
  takes: √(0.5 W / 500 Ω) = 31.6 mA. It is worst with the trimmer near zero (network 484 Ω), and
  reached at 56 Vrms per leg at 20 kHz and at 36 Vrms at 50 kHz, at the filter's corner, where
  the input network sees almost the whole voltage. AP's 53 Vrms from 20 kHz is the same limit.
- **R6 and R4, above 70 kHz**, as above.
- The 3 W resistors, at half their rating in a closed box, would allow 63-68 Vrms at 20 kHz.

An earlier version of this document said 85 Vrms at 20 kHz, counting only the resistors; that
was wrong, and so was the 85 Vrms above 100 kHz that the second version printed. What it means for this bench: a BTL amplifier puts half its differential voltage on
each leg, so 2 kW into 4 Ω (89 V across the terminals, 45 V per leg) fits even at 20 kHz. A
single-ended amplifier at the same power does not: its full-power points above 12 kHz must be
held to the curve. Measurement software that keeps one maximum voltage per probe should keep
75 V, and the frequency dependence is a rule for full-power response sweeps, which are the only
measurement that reaches it.

**A short at the output is a fault, not an operating case.** With the output shorted the
network carries the whole current at any frequency: the trimmer passes its rating from about
39 Vrms per leg, the 3 W resistors theirs from about 66 V. Neither the board nor AP's original
has a fuse, and a fuse would be a nonlinear part in the signal path; the protection is the
operator's - and the verification below includes a timed short at a safe level to see what gives
first.

**Noise.** The source resistance the analyzer sees is 590 Ω per leg, 1.2 kΩ differential:
0.63 µV in 20 kHz, −124 dBV, six dB under the QA403's best floor. With a 20:1 pad behind it the
output impedance is about 950 Ω per leg, −122 dBV. The filter is not where the noise is.

## What the ASR builders found

The design thread ("DIY amp testing (with AES17 filter)", ASR, 2023-2026, 8 pages) is worth
the read; the conclusions that bind this build:

- **The shunt capacitors must go to ground**, not to a floating midpoint between the legs. V1
  started floating; IVX (E1DA) pointed out that a floating LC rejects no common mode at all, and
  the ground ties were added in August 2023. Done in V2, keep it.
- **The +6 dB HD3 penalty** that sarieri measured on a V1 board at 5 V (−127 to −133 dB against
  −137 dB through E1DA's filter) went away on V2 (−133 dB and better). The V2 author credits the
  spacing; the simulation says spacing cannot do that, and sarieri's own breadboard of the same
  circuit had no penalty, so the likelier cause is **what the V1 layout coupled into the
  ferrite cores and traces** (the XLRs and the high-current input run were next to the coils).
  Either way: keep inductors away from the input run and the connectors, and remember that these
  figures are 15-20 dB below anything a QA403 can resolve. For this bench the ferrite-versus-air
  question is settled by hum, not distortion: Clockworks measured 60 Hz pickup in air-core coils
  change three-fold with orientation even inside a steel box, and this bench has a 1 kW load
  bank and a lab supply within a metre. **Ferrite drum cores, measured and paired.**
- **Source impedance is everything.** The author's 0.5-0.7 dB droop at 20 kHz turned out to be
  the 88 Ω output impedance of the DAC he tested with. An amplifier (< 1 Ω) is what the filter is
  designed around, and AP specifies < 2 Ω. **This also means the QA403's own generator cannot be
  used to trim the filter directly**: its output is 100 Ω single-ended and 200 Ω balanced (product
  sheet), which adds to R1 and would set the knee for a source that no amplifier has. Trim
  through an amplifier.
- **Load impedance** below about 10 kΩ bends the response (50 Ω gives a 12 dB peak at 30 kHz).
  The QA403's 100 kΩ per BNC is fine; the bench's existing 5 kΩ L-pad behind the filter would cost
  1 dB of insertion loss and must be re-measured with the filter in place if it is ever used
  that way.
- **The pad belongs after the filter**, as low in impedance as dissipation allows, and
  bypassable. A pad in front wrecks the response; the author and the thread tried three
  variants and came back to this.
- **No clamp diodes** at the output. They cost 5 dB of noise floor in the V1 build.
- **All-metal case, bonded**, pin-1/shell to the ground pour at one point, and a dedicated
  ground post "reserved for solving hum". Bare-board measurements were position-sensitive;
  boxed ones were not.

## The pad

The QA403's input is the constraint, and its product sheet is specific:

| QA403 fact | Value |
|---|---|
| Full-scale ranges | 0, +6, +12, +18, +24, +30, +36, +42 dBV |
| Attenuator | a relay engages for +24 dBV and above and raises the noise floor by about 20 dB |
| Maximum input | **+32 dBV = 40 Vrms**, software-clipped even on the +42 dBV range; absolute maximum 56 Vpk including DC |
| Input impedance | 100 kΩ per BNC to Audio Common, AC-coupled below 1 Hz; about 100 pF (user-measured, not specified) |
| Noise floor per range, 20 kHz, inputs shorted (Cordell's measurements, not a QuantAsylum spec) | 0 dBV: −118; +6: −114; +12: −110; +18: −104; **+24: −83; +30: −83; +36: −81; +42: −79 dBV** |

Two things follow. **Nothing above 40 Vrms may reach the BNCs** - the "+42 dBV" range name
suggests 126 Vrms and that is not what the input takes; even 42 Vrms is over the absolute
maximum (42 Vrms of sine is 59 Vpk). And the sweet spot is narrow: a signal should
sit in the **+18 dBV range or below**, because the step to +24 costs 20 dB of floor at once,
while below +18 the floor falls only 4-6 dB per range, so the dynamic range relative to full
scale barely changes (118 dB at 0 dBV, 122 dB at +18).

Put the bench's operating points through that, with the signal placed in the lowest range that
holds it with 1 dB of headroom:

| Operating point | At the amplifier | Direct | 3.42:1 (bench pad, down) | 4.85:1 (bench pad, up) | 10.6:1 (repo) | 20:1 |
|---|---|---|---|---|---|---|
| 5 W into 4 Ω | 4.47 V | +18 range, **117 dB** | +6, 116 dB | +6, 113 dB | 0, 111 dB | 0, 105 dB |
| 5 W into 2 Ω | 3.16 V | +12 range, **120 dB** | +6, 113 dB | 0, 114 dB | 0, 107 dB | 0, 102 dB |
| 100 W into 4 Ω | 20 V | +30, 109 dB | +18, **119 dB** | +18, 116 dB | +12, 116 dB | +6, 114 dB |
| 500 W into 4 Ω | 44.7 V | **over 40 Vrms** | +24, 105 dB | +24, 102 dB | +18, **117 dB** | +12, **117 dB** |
| 1000 W into 4 Ω | 63.2 V | over 40 Vrms | +30, 108 dB | +24, 105 dB | +18, **120 dB** | +12, **120 dB** |
| 2000 W into 4 Ω | 89.4 V | over 40 Vrms | +30, 111 dB | +30, 108 dB | +24, 102 dB | +18, **117 dB** |

(The dB figure is the analyzer's noise floor below the signal - the ceiling any SNR or THD+N
reading can reach, before the amplifier adds anything.)

So the intuition behind "the repo's pad is more than I need, and without one I'd have more
voltage at the analyzer, which may be no bad thing" is **right for the audio block and wrong
for the power sweeps**. Direct is the best possible connection at 5 W, by 4-7 dB over the
present L-pad. But 500 W and up cannot be measured direct at all, and through the present
4.85:1 they land in the attenuator ranges, 12-15 dB worse than through 10:1 or 20:1. The
present pad is a compromise that is optimal nowhere. A lower pad than the repo's would make the
power sweeps worse, not better.

**Decision: two positions, direct and 20:1, on the filter board.** 20:1 rather than the repo's
10:1 because it keeps a 2 kW / 4 Ω amplifier in the +18 range and gives up nothing at 500 W
or 1 kW. Values: **2 × 10.0 kΩ
in series and 1.00 kΩ to ground, all three 0.1 % / 15 ppm (TE YR1B, one family)**, per leg -
the ratio including the filter's 590 Ω and the analyzer's 100 kΩ is about 21.8:1, and it is
measured in place anyway. 9.53 kΩ in 0.1 % is stocked nowhere through-hole; 10.0 kΩ is. The
tolerance is not about knowing the ratio (that is measured) but about the two legs having the
same one: the analyzer subtracts the legs before anything can correct them (see "Leg matching").
The first draw of rev A had 1 % / 50 ppm upper arms and would have let −36 dB of common mode
through in PAD, and drifted against the cold 15 ppm lower arm in a power sweep. Loading on the
filter is 21 kΩ in PAD and nothing in DIRECT. At 85 V the pair dissipates 0.33 W, 0.16 W each; at
63 V, 0.18 W. Half their 0.25 W rating is reached at 74 Vrms per leg, which is the board's
low-frequency rating.

The switch is a **4PDT ON-ON toggle in the front wall**, non-shorting, with **gold contacts**
(APEM 5666CDB or similar), two poles per leg, its ten wires soldered into W1, a field of ten
holes straight below it. The filter stays passive: nothing in the box needs a supply or a
control line, so the analyzer's ground is the only ground it has. The two positions are two
probe settings, named by what the operator sees, and a gain check between steps catches a
switch that did not move.

Two poles per leg, so that **DIRECT is the bare filter**, as on the AUX-0025 and as in V2:

| Pole (per leg) | Common | PAD throw | DIRECT throw |
|---|---|---|---|
| a, pad feed | pad top (PT) | filter output (F) | not connected |
| b, output | output XLR (pin 2 for +, 3 for −) | pad tap (PAD) | filter output (F) |

In PAD, pole a puts the pad on the output and pole b takes the tap; in DIRECT the pad hangs
from nothing and the output is F. W1's holes are two rows of five in the same order, OUT, F, F,
PT, PAD: the back row for the + leg, the front row for the − leg, each labelled on the
silkscreen; the two F holes of a leg are joined on the board, one for each pole's wire. A
toggle breaks before it makes, so in either direction the output is open for a moment and never
sees the unpadded voltage through the pad's tap; if pole a fails open in PAD, the output sees a
1 kΩ to ground, which is safe. At 100 kΩ the switch carries microamperes, a dry circuit, where
silver contacts grow a sulphide film that makes level steps and low-level distortion: gold is a
requirement, not an option. The open contacts see up to 120 V peak between F and the tap; a
miniature toggle's dielectric rating (several hundred volts between open contacts) covers it,
but check the data sheet of the part bought.

With that, the bench's L-pad is retired. The 5 W block runs direct through the filter, every
power sweep above about 35 Vrms runs through 20:1, and choosing the probe per step becomes the
thing to build on the software side.

## The build

**Circuit:** the AUX-0025 values rather than the repo's E24 approximations, since every one of
them exists in E96: 412 Ω, 390 pF, 75.0 Ω, 3.40 kΩ, 24.9 Ω. They sit 1-2 dB better in the shelf
and 0.03 dB flatter at 20 kHz. The input network as AP has it, with a wider pot: **1.00 kΩ 3 W ‖
14.0 kΩ ‖ (1.00 kΩ 3 W + 500 Ω multi-turn trimmer)**, which spans 483-575 Ω. AP's 200 Ω pot
spans 483-525 Ω and is enough for AP's own 2.5 % parts; the unshielded ±5 % Würth WE-TI coil
fitted here, with 5 % capacitors straight from the reel, needs 495-534 Ω in the Monte Carlo
below; ±10 % coils need 484-543 Ω, and ±20 % coils 462-563 Ω, which the network cannot reach at
the bottom: about 3 % of such legs stay at up to 0.12 dB. The network spreads 6 W of rating over
two resistors, and the trimmer carries at most half the current (0.25 W at 63 V and 20 kHz; a
Bourns 3296W is rated 0.5 W).

**Capacitors:** polypropylene (WIMA FKP2 or Kemet PFR, 5 mm pitch, the same footprint), 630 V
for the 220 pF and 390 pF, 250 V or better for the 4.7 nF. ±5 % is good enough, because the
trimmer absorbs it - see "Assembly" below; JLCPCB's parts shop has the 220 pF in ±2.5 % and the
4.7 nF in ±5 % on pre-order, and the 390 pF should be found there in the same families.
Anything but C0G is out if ceramic is ever used. So the plan
is **±5 % film, bought in twenties and selected**: twenty 4.7 nF at 0.67 € and twenty 220 pF at
0.51 € cost less than one reel minimum, and an LCR meter sorts them into ±1 % sets in ten
minutes. Anything but C0G is out if ceramic is ever used.

**Inductors:** Würth **7687480102** (WE-TI HV: 1 mH ±5 %, 1.0 Ω, 0.8 A, 400 V, unshielded drum
core; Digi-Key, soldered by hand) - the repo's own part, the coil V2 measured at −133 dB HD3.
Its 120 V sibling 7447480102 is the same coil (JLCPCB C1331132, pre-order). An earlier revision of this fork fitted
the shielded WE-TIS 7447471102 for its lower hum pickup, and the argument for the unshielded
coil (taken from the review that followed) is linearity: the shielding sleeve closes the
magnetic path around the drum and shortens the air gap that keeps a ferrite coil linear, so
more of the stored energy sits in the ferrite, with its hysteresis and lower saturation
(0.68 A against 0.8 A). At 20 kHz and 55 Vrms per leg L1 carries 60 mA of capacitor current,
13 % of the shielded coil's saturation current; no measurement of either coil at these levels
exists for this board, so the one with a measured record is fitted, and the WE-TIS stays a
drop-in on the same footprint for test 4 to compare. The unshielded coil is also the tighter
part (±5 %, where JLCPCB lists the WE-TIS at ±20 %), which the common-mode table above and the
trim range both reward. What it costs: coupling between the drum cores. Simulated with the
coupling as a mutual inductance, k = 1 % between L1 and L2 (38 mm apart, axes parallel) moves
the stop band by 1-1.5 dB, and hum pickup from a nearby transformer is test 4's second half.
Pairing the coils by measurement is optional (see "Leg matching"). On the board as laid out the two legs' coils
are **66 mm apart**, the same as V2, and the two coils of one leg **30 mm**, against V2's
165 mm; the latter is the pair the simulation says matters least, the coils of one leg being in
series, and the nearest connector pin is 50 mm away. Both legs are laid out as mirror images,
every coil in the same orientation.

**Assembly.** The board is meant to be **assembled by JLCPCB, through-hole parts included**,
and nothing is hand-selected. The Monte Carlo that decides this: 200 boards with the coils
anywhere within their tolerance and the capacitors anywhere within ±5 %, each leg then trimmed
with R1 alone, in DIRECT, into the analyzer's 100 kΩ. The coil as fitted is the
unshielded Würth WE-TI HV 7687480102, ±5 % with 1.0 Ω of winding resistance (the table was
computed with the 7447480102's 1.15 Ω; the difference is under 0.001 dB).

| Parts as delivered | Untrimmed, worst leg | Trimmed, worst leg | R1 range the trim needed |
|---|---|---|---|
| **WE-TI (HV) 7687480102 / 7447480102, ±5 %, 1.0-1.15 Ω; C ±5 %** (the board as built) | 0.11 dB | **0.032 dB** | 495-534 Ω |
| WE-TIS 7447471102, ±10 % (datasheet), 2.1 Ω; C ±5 % | 0.17 dB | 0.034 dB | 484-543 Ω |
| WE-TIS as JLCPCB lists it, ±20 %, 2.1 Ω; C ±5 % | 0.30 dB | 0.12 dB (3 % of legs out of the trimmer's reach) | 462-563 Ω |

Within the trimmer's reach the trimmed residual is the same whatever the parts: it is the shape
of the curve, not the tolerance, that sets it. What the tolerance does set is how well the two
legs match at the top of the band (see "Leg matching"). So the
board goes through assembly except what JLCPCB has only on pre-order (the capacitors quoted at
19-21 working days): the ten film capacitors, the four coils, the two 412 Ω and the three Cliff
sockets are bought locally, the capacitors and coils measured and paired between the legs, and
soldered by hand. The hand work is: solder those, drill the front wall, wire the toggle (ten wires),
turn two trimmers, measure the pad ratio. Of the five boards, two are assembled; JLCPCB lets
the assembly count differ from the board count.

**Connectors:** the AUX-0025's, so the same cables test either filter. Input: a female XLR
(Neutrik NC3FAAH2, horizontal PCB mount; pin 2 is +, pin 3 is −, pin 1 and the shell contact
are ground, exactly AP's pin-out) and, beside it, red and black 4 mm safety sockets (Cliff
FCR7350, 24 A) at AP's 19.05 mm spacing so a dual banana plug fits, with a green common socket -
AP's "common terminal". Output: a male XLR (Neutrik NC3MAAH, pin 2 +, pin 3 −, pin 1 shield to
the filter's ground) as on the AUX-0025, and nothing else: the QA403 connects through a
self-made lead, XLR female to two BNC males (pin 2 to L+, pin 3 to L−, pin 1 to both shields),
the same lead an AUX-0025 takes. The XLR is rated 50 V by its standard and used to 140 Vrms
by AP; its exposed plug pins carry the amplifier voltage when the cable is pulled from the
filter under power, which the shrouded 4 mm sockets do not - the reason both are there. The BNC shells
are the board's ground, which is the analyzer's Audio Common; that is the one ground the filter
has, and the box is bonded to it. The XLR-to-two-BNC lead to the analyzer should be short,
30 cm or so: it keeps the capacitive load under AP's 360 pF limit (RG58 is 100 pF/m), and its
two BNC legs should be the same length.

**Board:** four layers, 1.6 mm, **158 × 124 mm**, every connector on the front long edge. The
first 24 mm behind that edge are the connector strip, with the switch at its right-hand end and
the two pads right behind it; the filter is the 100 mm band behind the strip. Layers 2 and 3 are
whole ground planes with nothing routed on them; signal on top, the crossings, the negative
pole's switch nets and its long output run on the bottom. 0.8 mm clearance throughout (IPC-2221B
for bare pads at 101-300 V; laid out for 120 V peak, 85 Vrms per leg, above the 75 Vrms rating). Four plain M3
holes on the band's centre line for spacers on the bottom plate, two more in the back corners
so that the back of the board does not hang 50 mm past them, and a seventh, plated and on
ground, in the connector strip: the one bond between the ground plane and the chassis, where the
cables come in. No Zeners, no fuses. The layout rules behind the arrangement - whole planes,
pairs kept together, long runs only at low impedance, the pad and switch at the output
connector, 38 mm between the coils of a leg - are listed with their reasons in
[hardware/README.md](../hardware/README.md#layout-rules-it-follows).
The design files are generated, not drawn: [hardware/](../hardware/) holds the data module,
the generator that places and routes the board with KiCad's Python module, the Gerbers, the
JLCPCB bill of materials and placement file, and the ordering notes.

**Box:** Hammond 1444-862 (bent aluminium chassis, 203 × 152 × 51 mm, flat 1 mm walls, about
20 €) with its 1434-86 bottom plate (about 11 €) - the box the original V2 recommended. **All
connectors come through its front long wall**, so the filter hangs with that wall towards the
operator, as the AUX-0025's front panel does: from the left the XLR input, the red and black
4 mm sockets at 19.05 mm, the green common, the XLR output, and the pad toggle, mounted high
above the switch. Its walls are
straight, unlike a die-cast box's 2-3° draft and its lid-screw bosses in the middle of the long
walls, which both stood in the way of a connector row. The board stands on 10 mm spacers on the
bottom plate, its front edge 3.3 mm behind the wall so the XLR flanges and the sockets'
shoulders lie against it.

## Bill of materials, per board

The authoritative list is generated: [hardware/fab/aes17-filter-bom.csv](../hardware/fab/aes17-filter-bom.csv)
in JLCPCB's columns and `aes17-filter-parts.csv` with notes. Prices are LCSC on 1 November 2026,
single quantity, in US dollars where that is what the shop shows; "pre-order" means JLCPCB
sources the part after payment and it can only be used for their assembly. Two assembled boards
with boxes come to about **250 € plus JLCPCB's assembly fees**, against 1 815 US dollars list for
an AUX-0025 (Axiometrix shop, October 2026).

| Qty | Part | For | LCSC | Note | ≈ |
|---|---|---|---|---|---|
| 4 | **Würth WE-TI HV 7687480102**, 1 mH ±5 %, 1.0 Ω, 0.8 A, unshielded | L1-L4 | C5523460 | **soldered by hand**, from Digi-Key (1.61 €, 285 in stock on 1 November 2026); at JLCPCB only pre-order (the 120 V 7447480102, C1331132, 2.14 €). Alternative on the same footprint, for test 4's comparison: the shielded WE-TIS 7447471102, C1331105 (JLCPCB lists it ±20 %) | 2.1 € |
| 4 | UNI-ROYAL MFR03SF1001A10, 1.00 kΩ 1 % 3 W 50 ppm | input network | C58750 | in stock; Vishay RS02B1K000FE12 (C3397612) is the AP part at $3.71 | $0.06 |
| 2 | 14.0 kΩ 1 % 0.25 W | input network | C127223 | | $0.01 |
| 2 | Bourns 3296W-1-501LF, 500 Ω 25-turn | 20 kHz knee | C69564 | in stock | $0.97 |
| 6 | WIMA FKP2J002201D00HSSD, 220 pF 630 V ±2.5 % | C1, C5 and the bypass pairs C2+C9, C6+C10 | C5742108 | **soldered by hand**, bought locally (Bürklin, also in ±1 %): JLCPCB quoted 19 working days of pre-order; 390 pF is not stocked, so two 220 pF in parallel make 440 pF as the repo has it (1 dB less at 250 kHz than AP's 390 pF, nothing else) | $0.23 |
| 4 | WIMA FKP2F014701I00JA00, 4.7 nF 250 V ±5 % | C3, C4, C7, C8 | C20412818 | **soldered by hand**, bought locally (Digi-Key): JLCPCB quoted 21 working days of pre-order | $0.41 |
| 2 | 412 Ω 1 % **0.6 W**, Vishay MRS25000C4120FCT00 | bypass across L1 | C1235858 | **soldered by hand**, bought locally: 3 in stock at JLCPCB on 2 November 2026; 0207 body, same footprint; same part: Vishay MBB02070C4120FRP00 (C1758271), Yageo MF0207FTE52-412R (C3401155) | - |
| 2 | 75.0 Ω 1 % 1 W, CCO MF1W | between stages | C160685 | | $0.05 |
| 2 | 3.40 kΩ 1 % **0.6 W**, Vishay MRS25000C3401FCT00 | across L3 | C1366835 | 0207 body, same footprint; 125 in stock at JLCPCB on 2 November 2026 | - |
| 2 | 24.9 Ω 1 % 0.25 W, Yageo MFR-25FBF52-24R9 | output | C3542579 | | $0.03 |
| 4 | TE YR1B10KCC, 10.0 kΩ **0.1 % 15 ppm** 0.25 W | pad, upper arm | C1364313 | 2 397 in stock at JLCPCB on 2 November 2026; the same family as the lower arm, so the legs' ratios match to 0.2 % and track in temperature. 9.53 kΩ in 0.1 % is stocked nowhere through-hole; 2 × 10 kΩ over 1 kΩ gives 21.8:1 into the analyzer | $0.50 |
| 2 | TE YR1B1K0CC, 1.00 kΩ 0.1 % 15 ppm | pad, lower arm | C1364308 | in stock | $0.50 |
| 1 | Neutrik NC3FAAH2, female XLR, horizontal PCB | J4, input | C368522 | in stock at LCSC; AP's input connector | $0.84-1.80 |
| 1 | Neutrik NC3MAAH, male XLR, horizontal PCB | J5, output | C368463 | in stock at LCSC; AP's output connector; the QA403 hangs on an XLR-to-two-BNC lead | $0.79-1.80 |
| 3 | Cliff FCR7350 R / B / G, 4 mm safety socket, PCB | J1-J3, at 19.05 mm for a dual banana | C6041087 / C6555263 / C6041085 | **soldered by hand**: pre-order at $11-12 each at LCSC; 6.80 € at Digi-Key - bought there and solder the three by hand if the JLCPCB price stands | $11 |
| 1 | **4PDT** toggle ON-ON, non-shorting, **gold contacts**, panel mount, 1/4 in bushing, solder lugs; APEM 5666CDB or similar | pad switch, in the front wall | - | ten wires into W1; a dry circuit, silver contacts are not suitable; not a JLCPCB part (RS, Mouser) | 8-15 € |
| 4 | screws for the two XLR flanges | the front wall | - | M3 as drawn on the front wall (3.2 mm holes); check against Neutrik's drawing of the NC3FAAH2 / NC3MAAH whether the flange takes M3 through or a 2.9 mm self-tapping screw, and drill to suit | 0.5 € |
| 1 | Hammond 1444-862 chassis + 1434-86 bottom plate | box | - | flat 1 mm aluminium walls; all connectors in the front long wall | 31 € |
| 5 | M3 spacers 10 mm + screws | board on the bottom plate; the one under H5 metal, bonding ground to the chassis | - | | 1 € |
| | four-layer PCB 158 × 124 mm, five pieces, two assembled | | | JLCPCB | see README |

JLCPCB's assembly terms, from their help pages in October 2026: minimum two boards; Economic
assembly setup $8.18 and $3.07 per unique extended part for feeder loading; through-hole parts
are hand-soldered at $3.58 per order plus $0.0164 per joint; pre-order parts take one to three
days of review and nine to twenty business days to arrive, and connectors carry a $20 inspection
fee per type. The ordering steps are in [hardware/README.md](../hardware/README.md).

What was looked at and not chosen: air-core coils (Mundorf ±2 %, Jantzen ±3 %) are 50 mm
across and hum antennas; BNC jacks on the board (TE 5227161-7 with jam nut, $6.85 the pair per
leg; the Molex 73100-0105 has no panel mount at all) were in the design until the connector set
was made the AUX-0025's, where one XLR-to-BNC lead does the same job for the price of two BNC
plugs.

## Ground, and bridged amplifiers

Every shunt capacitor goes to the filter's ground, which is also the chassis (through H5), the
output XLR's pin 1 and so the QA403's ground. That is what gives the filter its common-mode
rejection - V1 tried a floating midpoint and rejected no common mode at all - and it is the
AUX-0025's arrangement too. It also means that a bridged (BTL) or floating class-D output is
loaded against that ground, not only across its terminals:

| Each input to ground | DC | 20 kHz | 100 kHz | 400 kHz | 1 MHz |
|---|---|---|---|---|---|
| Impedance, per leg | 21 kΩ in PAD (the pad), 100 kΩ in DIRECT (the QA403) | 870 Ω | 1.3 kΩ | 1.2 kΩ | 750 Ω |
| Current for 10 V of common-mode residue | - | 12 mA | 8 mA | 9 mA | 13 mA |

A BTL amplifier with BD modulation can carry several volts of carrier as common mode, and that
current has to return to the amplifier somewhere. **The green socket is the path it should take:
connect it to the amplifier's ground (its power ground, or its chassis if that is where the
output stage is referenced).** Left open, the common-mode current returns through the analyzer
lead, the QA403, USB, the computer and the mains earth to the amplifier: a ground loop that the
measurement sees. Neither input is ground: on a BTL amplifier the black terminal is an output
like the red one. Both points are on the board's bottom side and belong on the front panel.

What the AUX-0025's datasheet promises for balanced and unbalanced amplifiers is AP's own
layout's; for this board it is a verification item (below), with the numbers above as the
expectation.

## Verification: what makes it a reference

Until the tests below have passed on a built board, this filter is a **prototype**, and the
figures in this document are simulations and comparisons with earlier builds. The order follows
the risk: the ferrite's linearity, the ground with bridged amplifiers, heat, and the stop band.
Each test names the instruments it needs; a QA403, an amplifier, a scope with a function
generator (or a nanoVNA) and a thermometer cover all of them.

**0. Before power.** Check the toggle wiring against the switch table with an ohmmeter: from
the output XLR's pin 2 (then 3) to pin 1, inputs open, about 1.0 kΩ in PAD and open (megohms)
in DIRECT. Each input reads about 21 kΩ to the chassis in PAD and open in DIRECT, and nothing
lower in either.

**1. Trim**, **through an amplifier, not the generator** (the QA403's output is 100 Ω, which
would move the knee by half a decibel). Any amplifier does - the next device under test, or a
10 € class-D board; its own response cancels because both analyzer inputs see it. QA403 OUT →
amplifier → a few volts at its terminals. Amplifier + to the filter's red input, the filter's
black input to its green ground socket (one leg at a time, single-ended), the amplifier
terminals also straight to the QA403's **right** input, the filter's output (through the
XLR-to-BNC lead) to the **left** input. The left-minus-right frequency response in dB is the
filter alone. Turn the + leg's trimmer until 20 kHz and 1 kHz agree within 0.02 dB, then move
the amplifier to the black input, ground the red one, and trim the − leg. Mark the trimmers.

**2. Pad ratio, over frequency.** The same set-up, PAD position, at 20 Hz, 1 kHz and 20 kHz:
the ratio is what the measurement software divides out of every level, and its change over the band should stay under
0.02 dB (the pad's own capacitance and the lead's 30 pF form a pole in the megahertz). The
DIRECT path is a probe too, with a ratio of about 1.006. Trim with the analyzer lead that will
be used: its capacitance sits on the output in DIRECT and behind the pad's 950 Ω in PAD, and
the pad itself loads the filter in PAD only, so a board trimmed flat in DIRECT with 185 pF on it
reads +0.025 dB at 20 kHz in PAD - record both, or divide both out.

**3. Leg symmetry.** Both inputs joined and driven together against the green socket (pure
common mode), output read differentially: that is the common-mode-to-differential conversion of
the built board, in DIRECT and in PAD. The simulation expects, trimmed, −74 / −52 dB at 50 Hz
(DIRECT / PAD), −31 dB at 20 kHz and −15 dB at 100 kHz; trimming matches the legs' amplitude at
20 kHz, not their phase, so record the curve rather than assume it. If it is much worse at
50 Hz, measure the pads' ratios leg against leg; if at 20-100 kHz, measure the coils.

**4. Ferrite linearity - the first gate.** The question is whether the coils add distortion at
the levels a clean amplifier reaches. Measure the same amplifier signal twice at the same
analyzer level: once through the filter in PAD, once through a plain resistive 20:1 divider
(metal film, no inductors). The difference is the filter's. At 100 Hz, 1 kHz, 6.67 kHz and
10 kHz; at 1, 5, 20, 40 and 80 Vrms per leg (80 V below 12 kHz only, see the rating); then SMPTE
IMD (60 Hz + 7 kHz, 4:1) and CCIF (19 + 20 kHz) at 20 and 40 V; both legs. **Pass: the filter
adds no more than 1 dB to any reading**, i.e. its own contribution stays at least 6 dB under the
amplifier's. If a leg fails, the test is repeated with an air-core 1 mH coil on flying leads in
place of L1, then L2, which tells which coil it is; the alternatives are a larger core (lower
flux density) or air-core coils off the board. Repeat on a board with the shielded WE-TIS
7447471102 in place of the fitted WE-TI: that settles the shielded-or-not question by
measurement. The same set-up, input shorted and the box next to the load bank or a mains
transformer, and turned through 90° and 180°, shows the hum the unshielded coils pick up; the
two legs are 66 mm apart, so a field gradient across the box is not common mode to them. A
uniform field is, but only if L1 and L3 (and L2 and L4) have the same winding sense; the coils
carry no marking, so hardware/README.md shows how to find it with the QA403 before soldering.

**5. Ground with a bridged amplifier.** With a BTL class-D amplifier: the common-mode current
in the green lead (a 1 Ω resistor in it and the scope across it, or a current probe), against
the table above; the amplifier's own residue and THD with the filter and with a plain resistive
probe; and the measurement with the computer on battery and on the mains (the QA403's ground
then floats or does not). Pass: the THD readings agree within 1 dB in all three cases, and the
amplifier's protection does not react to the filter.

**6. Heat.** A 20 kHz sine on one leg, single-ended, lid closed, 15 minutes each at 35, 45 and
55 Vrms; then the temperatures of R1/R2 (and R11/R12), the trimmer, L1 and C1 with a
thermocouple or an IR thermometer, and the 20 kHz ratio from test 1 watched for drift. Then
25 Vrms at 100 kHz (R6) and at 500 kHz (R4), 15 minutes each, and the pad resistors after
15 minutes at 70 Vrms and 1 kHz, with the pad ratio watched. Pass: the
trimmer's body under 70 °C (its rating's reference), the film capacitors under 85 °C (FKP2 is
rated 100 °C), the 3 W resistors under 150 °C, the ratio drifting less than 0.02 dB. A
temperature-indicator strip on R1 is a cheap witness for later use. Then a timed short: output
shorted, 20 V per leg at 1 kHz, 60 s, nothing over the limits above; no more than that - a
short at full voltage is a fault (see the rating), not a test.

**7. Stop band, per stage.** A QA403 cannot see 250 kHz. A function generator and a scope (10:1
probe, its ground spring on TP1 or TP2), or a nanoVNA with a 500 Ω series pad, from 100 kHz to
20 MHz: at the stage-1 output (C3/C7 pin 1), the stage-2 output (C4/C8 pin 1) and the XLR, in
DIRECT and in PAD, with the board in the closed chassis and out of it. Expect 45-50 dB at
250 kHz (one V1 build measured 45 against 55 simulated) and the coils' self-resonance above
1 MHz. A PAD reading much worse than DIRECT minus 27 dB means coupling into the pad's 1 kΩ
node; a closed-chassis reading much better than an open one means the chassis is doing work
the layout should.

**8. The switch.** Switch only with the amplifier off: the toggle breaks before it makes
(specify a non-shorting part with gold contacts, whose switching rating is only 0.4 VA at
20 V; they carry the full voltage closed, but switching 75 Vrms would burn the gold off), so the analyzer sees an open input for a
moment, never the unpadded voltage, but DIRECT at full power is over the QA403's 40 Vrms. A toggle with a locking
lever (pull to switch) keeps DIRECT from being selected by accident. Check both positions under
a 5 V signal with the scope on the output for anything but a clean step.

If all eight pass, the board is a reference within its rating and the numbers in the tables at
the top of this document can be replaced by measured ones.

## Safety, as far as this board goes

- **The rating is per leg** (see "Dissipation"): 75 Vrms to 15 kHz, 55 Vrms at 20 kHz, 30 Vrms
  from 30 kHz to 1 MHz. It belongs on the front panel at the inputs, with "max 40 Vrms into the
  QA403 in DIRECT" at the switch; the front-wall drawing carries that legend.
- **DC counts.** The filter passes DC, and a single-supply bridged amplifier (a TPA3255 on 48 V,
  for one) idles with half its supply, +24 V, on both terminals. In DIRECT that DC adds to the
  signal's peak at the QA403, whose absolute maximum is 56 Vpk including DC: 25 Vrms on top of
  +24 V is already 59 Vpk, although it is far below "40 Vrms". With such an amplifier, or one
  whose output stage is not known, use PAD (the pad divides the DC too), and switch only with the
  amplifier off, not merely muted, since muting leaves the DC on the terminals.
- **Not for line-level sources.** The filter is a load of about 870 Ω per leg at 20 kHz, mostly
  capacitive, and is trimmed for a source of a few ohms. A DAC or preamplifier output with
  50-100 Ω per leg loses 0.3-0.6 dB at 20 kHz through it and may not like the load; the name
  "AES17 filter" means the class-D pre-filter that sits in front of an analyzer's own AES17
  low-pass, as the AUX-0025 does, not that low-pass itself.
- **DIRECT passes the amplifier's full voltage** to the male XLR, whose pins are recessed but are
  the analyzer's input. A locking toggle and switching only with the amplifier off are the
  protection.
- **The chassis is the filter's ground**, bonded at H5, and through the output lead the QA403's.
  It is a shield, not a protective earth; the bench's earthing is the amplifier's and the
  computer's business.
- **Underneath**, the solder side sits 8 mm above the bottom plate on 10 mm spacers, every lead
  carrying the input voltage. A sheet of 0.25 mm polyester or fish paper on the bottom plate,
  cut around the seven spacers, keeps a bent lead or a dropped screw off the chassis.
- **No fuse and no thermal cut-out**: both would be nonlinear parts in the signal path, which is
  why AP has none either. The rating and test 6's timed short are the protection, and a
  temperature-indicator strip on R1 records it if the rating was ever exceeded.
- Clearances are 0.8 mm (IPC-2221B for bare pads, 101-300 V). That is a board-level figure for a
  clean, dry lab, not a safety approval; nothing about this box is certified.

## What this asks of the measurement software

Whatever runs the QA403 behind this filter should do three things:

- **Limit the direct path to 39 Vrms or less, and to 56 Vpk including DC** - the QA403's
  absolute maximum is 56 Vpk and its software clips at 40 Vrms. A pre-step check that lets
  42 Vrms through, or that ignores a bridged amplifier's half-supply DC, is a check that does not
  protect the instrument.
- **A probe needs a frequency response, not only a ratio.** The filter's residual ±0.03 dB, and
  the −0.05 dB insertion loss in DIRECT, are known once per board and could be divided out of the
  frequency response row the way the ratio is divided out of every level; the row would then
  show the amplifier and not the filter. Everything else (THD+N, SNR, power) is unaffected.
- **Per-step probe choice.** Direct for the audio block, 20:1 for the sweeps, in one run: a
  prompt to the operator between steps and a gain check after it.

## The original author's three planned changes

The V2 README lists three "possible future changes". Each was checked against this fork's design
with the same simulation and the same price lists.

**Shielded Coilcraft inductors, held back by their ±10 % tolerance.** The tolerance was the
only argument against them, and the trimmer removes it: trimmed per leg, ±10 % coils land
within 0.028 dB (±5 % coils: 0.029 dB) and need R1 between 478 and 548 Ω, inside the network's
483 to 575 Ω; even ±20 % coils trim to 0.032 dB with R1 between 454 and 562 Ω. Their higher DCR
(1.7 to 2.1 Ω against 1.0 Ω) moves nothing the trimmer does not take out, and the stop band is
unchanged. What shielding buys is exactly what the V1 builders complained about: a drum core
picks up the stray field of a transformer or a load bank and the result moves when the box
moves. So this change looked **worth making, and free once the trimmer exists**; the second
review reversed it for linearity and leg matching (see "Inductors" under "The build"), and the
shielded part is now the comparison in test 4 rather than the fitted coil. The parts:
the Coilcraft RFS1317-105KL (radial, ±10 %, 1.02 Ω, 0.68 A) is not at LCSC; the Bourns
SRR1280-102K (SMD 12.5 mm, ±10 %, 1.7 Ω, 0.68 A, JLCPCB C2041786, extended, about $1) needs
SMD pads and brings SMT assembly fees onto a through-hole board; the **Würth WE-TIS 7447471102**
(radial, shielded, ±10 %, 2.1 Ω typical, 0.46 A rated, 0.68 A saturation, SRF 1.1 MHz, 120 V,
Ø11 × 11.5 mm, **5 mm pitch, Ø1.2 mm holes**) is a drop-in for the footprint on this board and
was in stock at Digi-Key at 2.21 €. It is not in LCSC's catalogue; JLCPCB's global sourcing may
find it (it did: C1331105, listed as ±20 %), otherwise the four coils are bought at Digi-Key and
soldered by hand, eight joints. The coil line in `design.py` names it as the alternative.

**A 60 Vrms goal instead of 140, to allow smaller and cheaper parts.** The parts that the
voltage rating sets are few and cheap: the two 3 W input resistors per leg ($0.06 each) would
become 2 W parts, the 630 V capacitors 400 V ones (the 630 V WIMA at ±2.5 % is the one actually
stocked), the 1 W pad resistors 0.5 W. Under a dollar per board, and the limit this board has
is not the parts' voltages anyway but the pad's and the trimmer's power, as the rating
curve in the "Dissipation" section shows: 75 Vrms per leg to 15 kHz, 55 Vrms at 20 kHz. Smaller
resistors would give that up for under a dollar. **Not worth making**; the honest rating curve
is what this item was really about.

**A mostly SMD version, orderable through JLCPCB, probably not safe into a short.** The board
is orderable through JLCPCB as it is: every part is through-hole and JLCPCB hand-solders them at
$3.58 per order plus $0.0164 per joint, about $5.60 for this board's 120 joints. An SMD version
would replace that with SMT setup ($8.18), a stencil ($1.53) and a feeder fee of $3.07 per
extended part (about ten here), so for two to five boards it costs **more**, and the connectors
stay through-hole whatever happens, so the hand-soldering line stays too. What SMD would give:
0.1 % resistors for the pad in stock (Yageo RT0603BRD079K53L, 8 000 pieces), C0G capacitors with
nothing to measure, shielded coils as above, and a smaller board that the box has no use for.
What it would take: the 3 W input resistors become 2512 parts of 1 to 2 W, so the 20 kHz rating
falls to 50 or 60 V and a shorted output destroys them - the author's own caveat. **Not for this
run.** For a batch of twenty or more, a board with SMD passives and through-hole connectors would
be cheaper per piece and is a reasonable second revision; the data module and generator are
written so that it is a change of footprints, not a redesign.

## What was not changed, and why

- **Not a two-channel board.** The five-board minimum makes two single boards cheaper than one
  dual board and leaves three spares; a dual board doubles the inductor count per failure. One
  channel is what the original is, too.
- **Not SMD.** The parts that set the response are the 1 mH inductors and 630 V film capacitors,
  which are through-hole at the quality needed; a JLC-assembled SMD board would be C0G and
  shielded SMD inductors at ±10 % and lose the trim's point. Could be revisited if a second batch
  is ever needed.
- **Not air-core inductors.** AP's choice, and it removes the ferrite's low-frequency
  distortion, but it trades it for hum pickup on a bench with a kilowatt load bank, and the
  distortion in question measured 15-20 dB below the QA403's residual on V2 boards - on other
  boards with other coils, so it is the first gate of the verification, not a settled fact. An
  air-core coil on flying leads is the comparison there; a footprint for one is not on the
  board, because a 1 mH air coil is 50 mm across.
- **Not a lower impedance level or a third stage.** A constrained re-optimisation of the same
  topology found no set of values that adds more than 2 dB of rejection without raising the
  dissipation at 20 kHz, and an extra LC stage is another 30 € per board for rejection that the
  analyzer's own filters already provide. The AUX-0040 (40 kHz passband, rejection from 400 kHz)
  is the other sensible point on the curve, and only relevant if a 40 kHz bandwidth measurement
  is ever wanted.

## The second review, point by point

An outside audio and hardware review of rev A (source hash 7f42e40) came in on 2 November 2026,
before anything was ordered. Every number in it was re-simulated here; what it changed:

| Point | Verdict | What was done |
|---|---|---|
| `rating()` checked neither R4 nor R6; 85 Vrms claimed above 100 kHz | **right** | both now 0.6 W in the same footprint; `rating()` checks every resistor; the rating is 75 / 55 / 30 Vrms per leg |
| the DIRECT model left out the pad's 21 kΩ: −0.30 dB, not −0.05 | **right** | the pad now comes off the output in DIRECT (4PDT, two poles per leg): −0.05 dB again, as on the AUX-0025; the simulation models both positions |
| 1 % upper pad arms: −36 to −39 dB of common mode in PAD, which no probe factor can correct | **right** | all pad resistors 0.1 % / 15 ppm, one family: −52 dB |
| trimming each leg alone costs low-frequency rejection in DIRECT | **right**, smaller than claimed | with the pad on the output −80 → −59 dB at 50 Hz; with it switched off in DIRECT −74 dB; pairing the coils recommended where they are hand-soldered |
| shielded ferrite coils less linear than the unshielded drum | **plausible, unmeasured** | the unshielded ±5 % coil V2 measured is fitted; the shielded one is test 4's comparison. The "10-25 dB" in the review is not backed by a measurement either |
| JLCPCB lists the WE-TIS at ±20 % | **right**, and worse than stated | ±20 % coils can need R1 below the network's 483 Ω; one more reason for the ±5 % coil |
| the schematic generator did not read `design.py` (9.53 k, 390 p) | **right** | it does now, prints the design's hash, and `check_release.py` compares it |
| a bridged single-supply amplifier's half-supply DC adds to the peak at the QA403 in DIRECT | **right** | in the safety section, the README, the panel legend and the crib sheet |
| silver contacts in the toggle | **right** | gold contacts are now a hard requirement |
| XLR flange screws: Plastite, not M3 | **unverified** | Neutrik's drawing was not reachable from here; the BOM now says to check it |
| the 250 kHz notch detuned by 440 pF; "R4 = 357 Ω would fix it" | **half right** | 440 pF puts the notch at 240 kHz (1 dB at 250 kHz, already in the tables); R4 sets the notch's depth, not its frequency, so changing it would not retune it. Kept |
| `MFR03S` small-size 3 W, the Cermet trimmer's TCR | **minor** | at half rating the 3 W parts are within their spec; the trimmer's 100 ppm on its 140 Ω share moves 20 kHz by under 0.001 dB per 10 K. Kept; the heat test watches both |
| one ground plane, pin 1 on it; not AES48 | **by design** | the shunt capacitors need the analyzer's ground as their reference, as on the AUX-0025; "Ground, and bridged amplifiers" and test 5 cover the loop |
| hum pickup with 66 mm between the legs | **plausible, unquantified** | test 4 now turns the box in the field |
| F_N on the bottom past the pad tap | **negligible** | 0.2 pF from F_N into the 950 Ω tap is −90 dB at 20 kHz; the stop-band test in PAD would show more |
| name and source-impedance limits | **right** | stated in the README and the safety section |
