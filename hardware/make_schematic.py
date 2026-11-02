#!/usr/bin/env python3
"""Draws the filter schematic with schemdraw (pip install schemdraw):

    python3 make_schematic.py      # in this directory

writes aes17-filter-schematic.svg and .png next to this file. One leg is drawn in full; the
other is identical and shares only ground, the header and the relay. Every element is placed
by coordinates so the drawing stays legible whatever schemdraw's defaults are.

Every value and every relay pin number is read from design.py, and the drawing carries the
SHA-256 of design.py (design_hash below), which check_release.py compares, so the schematic in a
release cannot describe other parts than the board.
"""
import hashlib
import os
import sys

import schemdraw
import schemdraw.elements as elm

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import design  # noqa: E402

VALUE = {ref: value for ref, value, *_ in design.PARTS}
PIN = {(ref, net): pad for ref, _v, _f, _l, _n, pins in design.PARTS for pad, net in pins}


def design_hash():
    """The first seven hex digits of the SHA-256 of design.py, printed on the drawing."""
    with open(os.path.join(HERE, 'design.py'), 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()[:7]


def v(ref):
    """'R1  1.00k 3W': the reference and its value from design.py."""
    return f'{ref}  {VALUE[ref]}'


def R(d, a, b, label, loc='top'):
    d += elm.Resistor().at(a).to(b).label(label, loc=loc, fontsize=9)


def C(d, a, b, label, loc='bottom'):
    d += elm.Capacitor().at(a).to(b).label(label, loc=loc, fontsize=9)


def L(d, a, b, label):
    d += elm.Inductor2(loops=4).at(a).to(b).label(label, loc='bottom', fontsize=9)


def line(d, *pts):
    for a, b in zip(pts, pts[1:]):
        d += elm.Line().at(a).to(b)


def dot(d, p, label=None, loc='top', open_=False):
    e = elm.Dot(open=open_).at(p)
    if label:
        e = e.label(label, loc=loc, fontsize=9)
    d += e


def gnd(d, p):
    d += elm.Ground().at(p)


with schemdraw.Drawing(show=False) as d:
    d.config(fontsize=9)
    # ---- input --------------------------------------------------------------------------
    dot(d, (0, 0), 'IN +   J4 XLR pin 2 and J1 (red 4 mm) in parallel', loc='left', open_=True)
    line(d, (0, 0), (1, 0)); dot(d, (1, 0))
    line(d, (1, 2), (1, -2))
    R(d, (1, 2), (6, 2), v('R1'))
    R(d, (1, 0), (3.4, 0), v('R2'), loc='bottom')
    d += elm.Potentiometer().at((3.4, 0)).to((6, 0)).label(v('RV1') + '\n20 kHz trim', loc='bottom', fontsize=9)
    R(d, (1, -2), (6, -2), v('R3'), loc='bottom')
    line(d, (6, 2), (6, -2)); dot(d, (6, 0), 'A')
    # ---- first stage --------------------------------------------------------------------
    line(d, (6, 0), (7.5, 0)); dot(d, (7.5, 0))
    C(d, (7.5, 0), (7.5, -2.2), v('C1').replace('  ', '\n')); gnd(d, (7.5, -2.2))
    L(d, (7.5, 0), (10.5, 0), v('L1') + '  ' + design.MPN['L1'])
    line(d, (7.5, 0), (7.5, 2)); R(d, (7.5, 2), (9, 2), v('R4').replace('  ', '\n')); C(d, (9, 2), (10.5, 2), f'C2 || C9\n{VALUE["C2"]} + {VALUE["C9"]}', loc='top'); line(d, (10.5, 2), (10.5, 0))
    dot(d, (10.5, 0), 'B')
    C(d, (10.5, 0), (10.5, -2.2), v('C3').replace('  ', '\n')); gnd(d, (10.5, -2.2))
    # ---- second stage -------------------------------------------------------------------
    R(d, (10.5, 0), (13.5, 0), v('R5'))
    dot(d, (13.5, 0), 'D')
    L(d, (13.5, 0), (16.5, 0), v('L2'))
    line(d, (13.5, 0), (13.5, 2)); R(d, (13.5, 2), (16.5, 2), v('R6')); line(d, (16.5, 2), (16.5, 0))
    dot(d, (16.5, 0), 'E')
    C(d, (16.5, 0), (16.5, -2.2), v('C4').replace('  ', '\n')); gnd(d, (16.5, -2.2))
    R(d, (16.5, 0), (19.5, 0), v('R7'))
    dot(d, (19.5, 0), 'F', loc='bottom')
    # ---- pad ----------------------------------------------------------------------------
    line(d, (19.5, 0), (19.5, -2.5))
    R(d, (19.5, -2.5), (22.5, -2.5), v('R8'), loc='bottom')
    R(d, (22.5, -2.5), (25.5, -2.5), v('R9'), loc='bottom')
    dot(d, (25.5, -2.5), 'PAD  (about 21.8:1 tap)')
    R(d, (25.5, -2.5), (25.5, -5), v('R10'), loc='bottom'); gnd(d, (25.5, -5))
    # ---- switch: toggle wired into K1's holes today, relay K1 later, one pole per leg ----
    line(d, (19.5, 0), (28, 0)); dot(d, (28, 0), f"DIRECT   K1-{PIN['K1', 'F_P']} (NO)", loc='top', open_=True)
    line(d, (25.5, -2.5), (28, -2.5)); dot(d, (28, -2.5), f"PAD   K1-{PIN['K1', 'PAD_P']} (NC, relay at rest)", loc='bottom', open_=True)
    dot(d, (30, -1.25), None, open_=True)
    d += elm.Line().at((30, -1.25)).to((28.25, -2.4)).linewidth(2)     # the blade, drawn in the PAD position
    line(d, (30, -1.25), (32, -1.25)); dot(d, (32, -1.25), f"OUT +   K1-{PIN['K1', 'OUT_P']} (COM)   to J5 XLR pin 2", loc='right', open_=True)
    # ---- notes ---------------------------------------------------------------------------
    d += elm.Label().at((0, -7.2)).label(
        f"Negative leg, IN - (J4 XLR pin 3 / J2 black) to OUT - (J5 XLR pin 3): identical; R11-R20, RV2, C5-C10, L3, L4; its switch is the other relay pole, pins {PIN['K1', 'F_N']} / {PIN['K1', 'OUT_N']} / {PIN['K1', 'PAD_N']}.\n"
        'XLR pin 1 and shell, J3 (green 4 mm), the ground plane and the box: GND = the QA403\'s Audio Common. Connectors as on the AP AUX-0025; the QA403 takes an XLR-to-two-BNC lead.\n'
        f"K1 (Omron G6A-274P-ST-US DC12, polarised coil: pin {PIN['K1', 'COIL+']} +, pin {PIN['K1', 'COIL-']} -) is a footprint only until the matrix controller drives it; until then a DPDT toggle (gold contacts) is wired into its six contact holes. Coil on J9 (1 = +12 V), D1 1N4148 across the coil, cathode (band) to J9-1.\n"
        'The pad stays on the output in both positions: DIRECT reads 100k || 21k (about 1.035:1, measure it). With K1 at rest or a toggle in PAD the analyzer sees about 1/22 of the amplifier;\n'
        'DIRECT is the full voltage, DC included: a single-supply bridged amplifier idles at half its supply on both legs, which adds to the peak the QA403 sees.\n'
        f'All values from design.py, sha256 {design_hash()}.',
        halign='left', fontsize=8)

    d.save(os.path.join(HERE, 'aes17-filter-schematic.svg'))
    d.save(os.path.join(HERE, 'aes17-filter-schematic.png'), dpi=150)
    d.save(os.path.join(HERE, 'fab', 'aes17-filter-schematic.pdf'))   # the release copy
print('ok')
