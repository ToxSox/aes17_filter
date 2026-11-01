#!/usr/bin/env python3
"""AC analysis of the AES17 class-D measurement filter in docs/design-review.md.

One leg against ground (the two legs are identical and every shunt capacitor goes to ground, so
the half circuit is exact for a balanced drive):

    in --[R1]--+--[L1 || (R3 + C34)]--+--[R5]--+--[L3 || R7]--+--[R9]--+-- out --(pad)-- load
               |                      |        |              |        |
              C1                     C7       (none)         C9      Rload || Cload
               |                      |                       |
              GND                    GND                     GND

Needs numpy only. Prints every table quoted in the document:

    python3 sim/aes17_sim.py
"""
import math
import numpy as np

# The aes17_filter_25 V2 values, read from the PCB file (the repo's XML netlist is V1).
REPO = dict(R1=500., C1=220e-12, R3=330., C34=440e-12, L1=1e-3, L3=1e-3, Ldcr=1.0,
            C7=4.7e-9, R5=68., R7=3300., C9=4.7e-9, R9=22.)
# The AUX-0025 as traced (Cranial Crumbs, 2015). The input network 1k || 14k || (1k + 0..200)
# is 467..520 ohm; 503 is the middle of the pot.
AUX0025 = dict(REPO, R1=503., R3=412., C34=390e-12, R5=75., R7=3400., R9=24.9, Ldcr=0.5)


def admittance(f, p, Rload=100e3, Cload=0.0, pad=None):
    """The nodal admittance matrix at one frequency, and the node the analyzer sits on."""
    s = 2j * math.pi * f
    Y = np.zeros((9, 9), dtype=complex)  # 0 GND, 1 in, 2..6 internal, 7 out, 8 pad tap

    def add(a, b, y):
        Y[a, a] += y; Y[b, b] += y; Y[a, b] -= y; Y[b, a] -= y

    add(1, 2, 1 / p['R1']); add(2, 0, s * p['C1'])
    add(2, 3, 1 / p['R3']); add(3, 4, s * p['C34'])
    add(2, 4, 1 / (s * p['L1'] + p['Ldcr'])); add(4, 0, s * p['C7'])
    add(4, 5, 1 / p['R5'])
    add(5, 6, 1 / (s * p['L3'] + p['Ldcr'])); add(5, 6, 1 / p['R7']); add(6, 0, s * p['C9'])
    add(6, 7, 1 / p['R9'])
    load_node = 7
    if pad:
        add(7, 8, 1 / pad[0]); add(8, 0, 1 / pad[1]); load_node = 8
    add(load_node, 0, 1 / Rload)
    if Cload:
        add(load_node, 0, s * Cload)
    return Y, load_node


def node_voltages(f, p, vin=1.0, **kw):
    """Every node voltage for vin at node 1 (node 0 is ground)."""
    Y, _ = admittance(f, p, **kw)
    keep = [k for k in range(2, 9) if k != 8 or kw.get('pad')]
    v = np.zeros(9, dtype=complex); v[1] = vin
    v[keep] = np.linalg.solve(Y[np.ix_(keep, keep)], -Y[np.ix_(keep, [1])][:, 0] * vin)
    return v


def transfer(freqs, p, **kw):
    """V(analyzer)/V(in) for each frequency. pad = (Rtop, Rbottom) puts a divider after R9 and
    the analyzer on its tap."""
    _, load_node = admittance(1e3, p, **kw)
    return np.array([node_voltages(f, p, **kw)[load_node] for f in freqs])


def db(x):
    return 20 * np.log10(np.abs(x))


PASSBAND = np.logspace(math.log10(20), math.log10(20e3), 60)
STOPBAND = np.array([150e3, 200e3, 250e3, 300e3, 500e3, 1e6])


def summary(p, **kw):
    ref = db(transfer(np.array([1000.]), p, **kw))[0]
    dev = db(transfer(PASSBAND, p, **kw)) - ref
    stop = db(transfer(STOPBAND, p, **kw)) - ref
    return ref, dev, stop


def line(label, p, **kw):
    ref, dev, stop = summary(p, **kw)
    print(f"{label:44} loss@1k {ref:+.3f}  20Hz-20kHz {dev.min():+.3f}/{dev.max():+.3f}  20k {dev[-1]:+.3f}  "
          + ' '.join(f"{f/1e3:.0f}k:{v:.1f}" for f, v in zip(STOPBAND, stop)))


def response_tables():
    print("== transfer in dB relative to 1 kHz; stop band at 150/200/250/300/500/1000 kHz ==")
    line("repo V2, 100k", REPO)
    line("repo V2, 100k || 185 pF (QA403 + lead)", REPO, Cload=185e-12)
    line("repo V2, 50k", REPO, Rload=50e3)
    line("repo V2, 10k", REPO, Rload=10e3)
    line("AUX-0025 values, 100k", AUX0025)
    line("AUX-0025 values, 100k || 185 pF", AUX0025, Cload=185e-12)
    print("-- R1 is the 20 kHz knee: the AUX-0025's trimpot range --")
    for r1 in (470, 487, 503, 520, 540):
        line(f"AUX-0025 values, R1 = {r1}, 100k || 185 pF", dict(AUX0025, R1=r1), Cload=185e-12)
    print("-- a fixed re-centring of the repo values --")
    line("repo + R7 4.7k, C9 5.6n, 100k", dict(REPO, R1=499., R7=4700., C9=5.6e-9))
    print("-- the pad after the filter, into 100k --")
    for rt, rb in ((9000, 1000), (19060, 1000)):
        ref, dev, _ = summary(REPO, pad=(rt, rb))
        print(f"pad {rt}/{rb}: ratio {10**(-ref/20):.2f}:1 ({ref:+.2f} dB), passband {dev.min():+.3f}/{dev.max():+.3f}")


def monte_carlo(tolL, tolC, tolR, n=400, seed=1):
    rng = np.random.default_rng(seed)
    spread, at20k, worst_rej = [], [], []
    for _ in range(n):
        p = dict(REPO)
        for k in ('L1', 'L3'):
            p[k] *= 1 + rng.uniform(-tolL, tolL)
        for k in ('C1', 'C34', 'C7', 'C9'):
            p[k] *= 1 + rng.uniform(-tolC, tolC)
        for k in ('R1', 'R3', 'R5', 'R7', 'R9'):
            p[k] *= 1 + rng.uniform(-tolR, tolR)
        _, dev, stop = summary(p)
        spread.append(dev.max() - dev.min()); at20k.append(dev[-1]); worst_rej.append(stop[2:5].max())
    spread, at20k, worst_rej = map(np.array, (spread, at20k, worst_rej))
    print(f"L ±{tolL*100:.0f} % C ±{tolC*100:.1f} % R ±{tolR*100:.0f} %: passband spread max {spread.max():.2f} dB "
          f"(95 % {np.percentile(spread, 95):.2f}), 20 kHz {at20k.min():+.2f}..{at20k.max():+.2f} dB, "
          f"worst 250-500 kHz {worst_rej.max():.1f} dB")


def dissipation():
    print("== current through R1 and L1 and the power in R1, per leg (output open into 100k) ==")
    for vin, label in ((44.7, '500 W / 4 ohm'), (63.2, '1000 W / 4 ohm'), (89.4, '2000 W / 4 ohm'), (140., 'repo max')):
        cells = []
        for f in (1e3, 20e3):
            v = node_voltages(f, REPO, vin)
            i_r1 = (v[1] - v[2]) / REPO['R1']
            i_l1 = (v[2] - v[4]) / (2j * math.pi * f * REPO['L1'] + REPO['Ldcr'])
            cells.append(f"{f/1e3:.0f} kHz: {abs(i_r1)**2 * REPO['R1']:.2f} W in R1, {abs(i_l1)*1e3:.0f} mA in L1")
        print(f"  {label:16} {cells[0]};  {cells[1]}")
    print("  (rule of thumb: at 20 kHz the power in R1 is 0.68 mW per volt squared; a 5 W part allows 85 Vrms)")


def analyzer_ranges():
    print("== where each operating point lands in the QA403's ranges, and the floor under it ==")
    floor = {0: -118, 6: -114, 12: -110, 18: -104, 24: -83, 30: -83, 36: -81, 42: -79}  # Cordell, 20 kHz BW

    def pick(dbv, headroom=1.0):
        return next((r for r in sorted(floor) if r >= dbv + headroom), None)
    pads = (('direct', 1.0), ('3.42:1', 3.423), ('4.85:1', 4.85), ('10.6:1', 10.59), ('20:1', 20.0))
    for name, v in (('5 W / 4 ohm', 4.47), ('5 W / 2 ohm', 3.16), ('100 W / 4 ohm', 20.0),
                    ('500 W / 4 ohm', 44.7), ('1000 W / 4 ohm', 63.2), ('2000 W / 4 ohm', 89.4)):
        cells = []
        for pn, ratio in pads:
            va = v / ratio
            if va > 39.6:
                cells.append(f"{pn}: over 40 Vrms")
                continue
            d = 20 * math.log10(va); r = pick(d)
            cells.append(f"{pn}: +{r} range, {d - floor[r]:.0f} dB")
        print(f"  {name:14} {v:5.1f} V  " + ' | '.join(cells))


def noise():
    print("== thermal noise of the source resistance the analyzer sees, 20 kHz, 300 K ==")
    for label, r in (('direct: 590 ohm per leg, 1180 differential', 1180.),
                     ('20:1 pad: about 950 ohm per leg', 1900.)):
        vn = math.sqrt(4 * 1.38e-23 * 300 * r * 20e3)
        print(f"  {label}: {vn*1e6:.2f} uV = {20*math.log10(vn):.1f} dBV")


if __name__ == '__main__':
    response_tables()
    print("== Monte Carlo, 400 samples, parts uniformly within tolerance, repo values, 100k ==")
    monte_carlo(0.05, 0.025, 0.01)
    monte_carlo(0.10, 0.025, 0.01)
    monte_carlo(0.02, 0.01, 0.01)
    dissipation()
    analyzer_ranges()
    noise()
