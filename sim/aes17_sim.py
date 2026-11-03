#!/usr/bin/env python3
"""AC analysis of the AES17 class-D measurement filter in docs/design-review.md.

One leg against ground (the two legs are identical and every shunt capacitor goes to ground, so
the half circuit is exact for a balanced drive):

    in --[R1]--+--[L1 || (R3 + C34)]--+--[R5]--+--[L3 || R7]--+--[R9]--+-- out --(pad)-- load
               |                      |        |              |        |
              C1                     C7       (none)         C9      Rload || Cload
               |                      |                       |
              GND                    GND                     GND

The build itself (BUILD) adds the 20:1 pad, which a 4PDT toggle connects to the output in PAD
and takes off in DIRECT, where the analyzer's 100k is the only load. Needs numpy only. Prints every table
quoted in the document (the common-mode Monte Carlo takes half a minute):

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


def admittance(f, p, Rload=100e3, Cload=0.0, pad=None, tap=True):
    """The nodal admittance matrix at one frequency, and the node the analyzer sits on.
    pad = (Rtop, Rbottom) hangs a divider on the filter output; tap=True puts the analyzer on its
    tap (PAD), tap=False leaves it on the output with the divider still there (DIRECT on this
    board, whose pad is never disconnected)."""
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
        add(7, 8, 1 / pad[0]); add(8, 0, 1 / pad[1])
        if tap:
            load_node = 8
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


# This build: the AUX-0025 values with two 220 pF for the 390 pF and the unshielded Wurth WE-TI
# 7687480102 coils (1.0 ohm), AP's input network with a 500 ohm trimmer: 1k || 14k || (1k + RV),
# and the 20:1 pad (2 x 10.0 k over 1.00 k), on the output in PAD only.
BUILD = dict(AUX0025, C34=440e-12, Ldcr=1.0)
PAD = (20e3, 1e3)
DIRECT = dict()                         # the analyzer on F, the pad switched off
PADDED = dict(pad=PAD, tap=True)        # the analyzer on the pad's tap


def network(rv):
    return 1 / (1 / 1000 + 1 / 14000 + 1 / (1000 + rv))


def trim(p, lo=440.0, hi=700.0, **kw):
    """R1 such that |H(20 kHz)| = |H(1 kHz)|, by bisection: what turning the trimmer does."""
    def err(r1):
        h = transfer(np.array([1e3, 20e3]), dict(p, R1=r1), **kw)
        return db(h[1]) - db(h[0])
    for _ in range(40):
        mid = (lo + hi) / 2
        if err(mid) > 0:     # 20 kHz too high: more resistance, more damping
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def wideband():
    """What the filter does above 20 kHz, where a wideband THD+N reading still looks: the
    harmonics of a 20 kHz tone and the top of an 80-90 kHz measurement bandwidth."""
    print("== above the band: the trimmed build in DIRECT, relative to 1 kHz ==")
    p = dict(BUILD, R1=trim(BUILD))
    freqs = np.array([1e3, 20e3, 30e3, 40e3, 60e3, 80e3])
    h = transfer(freqs, p)
    for f, v in zip(freqs[1:], h[1:]):
        print(f"  {f/1e3:4.0f} kHz {db(v) - db(h[0]):+6.2f} dB  {np.degrees(np.angle(v)):7.1f} deg")


def build_tables():
    print("== this build: DIRECT (pad off) and PAD, into the QA403's 100k and a 185 pF lead ==")
    p = dict(BUILD, R1=trim(BUILD, **DIRECT))
    for label, kw in (("DIRECT, 100k", DIRECT), ("PAD, 100k", PADDED)):
        ref = transfer(np.array([1e3]), p, **kw)[0]
        print(f"  {label:12} ratio {1/abs(ref):7.4f}:1 ({db(ref):+.3f} dB)")
    pc = dict(BUILD, R1=trim(BUILD, Cload=185e-12, **DIRECT))
    for label, kw in (("DIRECT", DIRECT), ("PAD", PADDED)):
        ref, dev, stop = summary(pc, Cload=185e-12, **kw)
        print(f"  trimmed in DIRECT with 185 pF, read in {label:6}: 20 Hz-20 kHz {dev.min():+.3f}/{dev.max():+.3f} dB,"
              f" 20 kHz {dev[-1]:+.3f} dB; " + ' '.join(f"{f/1e3:.0f}k:{v:.1f}" for f, v in zip(STOPBAND, stop)))


# The parts' power ratings, and the share of it this design allows in a closed box.
RATINGS = {      # name: (ohms, rated W)
    'R1a 1k 3W':          (1000., 3.0),
    'R1c 14k 0.25W':      (14e3, 0.25),
    'R3 412R 0.6W':       (412., 0.6),
    'R5 75R 1W':          (75., 1.0),
    'R7 3k40 0.6W':       (3400., 0.6),
    'R9 24R9 0.25W':      (24.9, 0.25),
    'pad 10k 0.25W':      (10e3, 0.25),
    'pad 1k 0.25W':       (1e3, 0.25),
}
DERATE = 0.5


def part_powers(f, p, rv, vin=1.0):
    """Power in every resistor, and the trimmer's current, for vin per leg, in PAD: the only
    position in which the pad dissipates, and the one any voltage over the QA403's 40 Vrms is
    measured in."""
    v = node_voltages(f, p, vin, **PADDED)
    s = 2j * math.pi * f
    vnet = v[1] - v[2]
    i_c34 = (v[2] - v[4]) / (p['R3'] + 1 / (s * p['C34']))
    i_pad = v[7] / (PAD[0] + PAD[1])
    pw = {'R1a 1k 3W':     abs(vnet) ** 2 / 1000.,
          'R1c 14k 0.25W': abs(vnet) ** 2 / 14e3,
          'R3 412R 0.6W':  abs(i_c34) ** 2 * p['R3'],
          'R5 75R 1W':     abs(v[4] - v[5]) ** 2 / p['R5'],
          'R7 3k40 0.6W':  abs(v[5] - v[6]) ** 2 / p['R7'],
          'R9 24R9 0.25W': abs(v[6] - v[7]) ** 2 / p['R9'],
          'pad 10k 0.25W': abs(i_pad) ** 2 * PAD[0] / 2,
          'pad 1k 0.25W':  abs(i_pad) ** 2 * PAD[1]}
    i_rv = abs(vnet) / (1000 + rv)
    return pw, i_rv


RATING_FREQS = (1e3, 5e3, 10e3, 12e3, 15e3, 20e3, 30e3, 50e3, 70e3, 100e3, 150e3, 250e3, 500e3, 1e6)


def rating(verbose=True):
    """The highest sine voltage per leg (leg to ground) the parts take, over frequency, at the
    trimmer setting that is worst for each part. Every resistor is checked at DERATE of its rating;
    the trimmer is a Bourns 3296, 0.5 W at 70 C over the whole 500 ohm element: used as a rheostat
    the current, sqrt(0.5 / 500) = 31.6 mA, is what the element takes; the coils' 400 V (WE-TI HV;
    Wurth gives it without saying between what) is read as node to ground, 283 Vrms of sine
    anywhere, and never sets the limit.
    A BTL amplifier puts half its differential voltage on each leg."""
    i_max = math.sqrt(0.5 / 500)
    worst = {}
    for rv in (5.0, 140.0, 281.0):          # networks 484, 513 (nominal trim), 540 ohm
        p = dict(BUILD, R1=network(rv))
        for f in RATING_FREQS:
            pw, i_rv = part_powers(f, p, rv)
            lim = {'coil 400 Vpk': 400 / math.sqrt(2), 'trimmer 31.6 mA': i_max / i_rv}
            for name, (_r, watts) in RATINGS.items():
                lim[name] = math.sqrt(DERATE * watts / pw[name])
            name = min(lim, key=lim.get)
            if f not in worst or lim[name] < worst[f][0]:
                worst[f] = (lim[name], name, rv)
    if verbose:
        print(f"== the highest sine voltage per leg (leg to ground), every resistor at {DERATE:.0%} of its rating ==")
        for f, (vmax, name, rv) in sorted(worst.items()):
            print(f"  {f/1e3:6.1f} kHz: {vmax:5.0f} Vrms per leg   ({name}, trimmer at {rv:.0f} ohm)")
        print("  rating: 75 Vrms per leg to 15 kHz (the pad), falling to 55 Vrms at 20 kHz (the trimmer),"
              " 30 Vrms from 30 kHz to 1 MHz (trimmer, R7 3.40k, R3 412R); a BTL amplifier may put twice"
              " that across its terminals")
        print("  several frequencies at once (audio and a class-D carrier, a two-tone test): the powers add,"
              " so the sum of (V / Vmax(f))^2 over the tones must stay at or below 1")
    return worst


def cmrr(n=500, seed=2):
    """Common mode in, difference out: both legs built from parts drawn within tolerance, each
    trimmed on its own in DIRECT (pad off), then driven together. Prints the 95th percentile of
    |H+ - H-| / |H| in dB, i.e. how much of a common-mode signal the QA403's differential input
    sees as signal, and the trimmed legs' worst passband deviation."""
    print(f"== common mode to difference, 95th percentile of {n} boards, each leg trimmed alone ==")
    freqs = np.array([50., 1e3, 10e3, 20e3, 100e3])
    # paired: '' nothing, 'L' the coils, 'C' the film capacitors, 'LC' both; a pair is measured
    # and matched to 1 % between the legs (one value drawn within tolerance per pair, then each
    # leg's part within 1 % of it)
    cases = (('coils +-5 %, pad 0.1 % (as built)',     0.05, 0.001, ''),
             ('coils +-5 %, pad 1 % upper arms (rev A)', 0.05, 0.010, ''),
             ('coils +-20 %, pad 0.1 %',              0.20, 0.001, ''),
             ('coils +-5 % paired to 1 %, pad 0.1 %', 0.05, 0.001, 'L'),
             ('capacitors paired to 1 %, coils not',  0.05, 0.001, 'C'),
             ('coils and capacitors paired to 1 %',   0.05, 0.001, 'LC'))
    tol_c = {'C1': 0.025, 'C34': 0.025, 'C7': 0.05, 'C9': 0.05}
    for label, tol_l, tol_pad, paired in cases:
        rng = np.random.default_rng(seed)
        res = {'DIRECT untrimmed': [], 'DIRECT': [], 'PAD': []}
        ripple = []
        for _ in range(n):
            legs = []
            l_pair = [1 + rng.uniform(-tol_l, tol_l) for _ in range(2)]
            c_pair = {k: 1 + rng.uniform(-t, t) for k, t in tol_c.items()}
            for leg in range(2):
                q = dict(BUILD, R1=network(140.))
                for i, k in enumerate(('L1', 'L3')):
                    q[k] *= l_pair[i] * (1 + rng.uniform(-0.01, 0.01)) if 'L' in paired else 1 + rng.uniform(-tol_l, tol_l)
                for k, t in tol_c.items():
                    q[k] *= c_pair[k] * (1 + rng.uniform(-0.01, 0.01)) if 'C' in paired else 1 + rng.uniform(-t, t)
                for k in ('R3', 'R5', 'R7', 'R9'):
                    q[k] *= 1 + rng.uniform(-0.01, 0.01)
                pad = (PAD[0] * (1 + rng.uniform(-tol_pad, tol_pad)), PAD[1] * (1 + rng.uniform(-0.001, 0.001)))
                h0 = transfer(freqs, q)
                q['R1'] = trim(q)
                legs.append((h0, transfer(freqs, q), transfer(freqs, q, pad=pad, tap=True)))
                ripple.append(np.abs(db(transfer(PASSBAND, q)) - db(transfer(np.array([1e3]), q))[0]).max())
            for i, key in enumerate(res):
                hp, hn = legs[0][i], legs[1][i]
                res[key].append(np.abs(hp - hn) / np.abs((hp + hn) / 2))
        print(f"  {label}: trimmed passband within +-{max(ripple):.3f} dB")
        for key, vals in res.items():
            p95 = db(np.percentile(np.array(vals), 95, axis=0))
            print(f"    {key:17} " + '  '.join(f"{f/1e3:g}k {v:6.1f}" for f, v in zip(freqs, p95)))


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
    build_tables()
    wideband()
    dissipation()
    rating()
    cmrr()
    analyzer_ranges()
    noise()
