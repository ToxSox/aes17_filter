#!/usr/bin/env python3
"""Draws the filter schematic with schemdraw (pip install schemdraw):

    python3 hardware/aes17-filter/make_schematic.py

writes aes17-filter-schematic.svg and .png next to this file. One leg is drawn in full; the
other is identical and shares only ground, the header and the relay. Every element is placed
by coordinates so the drawing stays legible whatever schemdraw's defaults are.
"""
import os

import schemdraw
import schemdraw.elements as elm

HERE = os.path.dirname(os.path.abspath(__file__))


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
    R(d, (1, 2), (6, 2), 'R1  1.00k 3W')
    R(d, (1, 0), (3.4, 0), 'R2  1.00k 3W', loc='bottom')
    d += elm.Potentiometer().at((3.4, 0)).to((6, 0)).label('RV1  500R\n20 kHz trim', loc='bottom', fontsize=9)
    R(d, (1, -2), (6, -2), 'R3  14.0k', loc='bottom')
    line(d, (6, 2), (6, -2)); dot(d, (6, 0), 'A')
    # ---- first stage --------------------------------------------------------------------
    line(d, (6, 0), (7.5, 0)); dot(d, (7.5, 0))
    C(d, (7.5, 0), (7.5, -2.2), 'C1\n220p 630V'); gnd(d, (7.5, -2.2))
    L(d, (7.5, 0), (10.5, 0), 'L1  1 mH')
    line(d, (7.5, 0), (7.5, 2)); R(d, (7.5, 2), (9, 2), 'R4\n412R'); C(d, (9, 2), (10.5, 2), 'C2\n390p 630V', loc='top'); line(d, (10.5, 2), (10.5, 0))
    dot(d, (10.5, 0), 'B')
    C(d, (10.5, 0), (10.5, -2.2), 'C3\n4.7n 250V'); gnd(d, (10.5, -2.2))
    # ---- second stage -------------------------------------------------------------------
    R(d, (10.5, 0), (13.5, 0), 'R5  75.0R 1W')
    dot(d, (13.5, 0), 'D')
    L(d, (13.5, 0), (16.5, 0), 'L2  1 mH')
    line(d, (13.5, 0), (13.5, 2)); R(d, (13.5, 2), (16.5, 2), 'R6  3.40k'); line(d, (16.5, 2), (16.5, 0))
    dot(d, (16.5, 0), 'E')
    C(d, (16.5, 0), (16.5, -2.2), 'C4\n4.7n 250V'); gnd(d, (16.5, -2.2))
    R(d, (16.5, 0), (19.5, 0), 'R7  24.9R')
    dot(d, (19.5, 0), 'F', loc='bottom')
    # ---- pad ----------------------------------------------------------------------------
    line(d, (19.5, 0), (19.5, -2.5))
    R(d, (19.5, -2.5), (22.5, -2.5), 'R8  9.53k 0.1%', loc='bottom')
    R(d, (22.5, -2.5), (25.5, -2.5), 'R9  9.53k 0.1%', loc='bottom')
    dot(d, (25.5, -2.5), 'PAD  (20:1 tap)')
    R(d, (25.5, -2.5), (25.5, -5), 'R10  1.00k 0.1%', loc='bottom'); gnd(d, (25.5, -5))
    # ---- switch: toggle wired into K1's holes today, relay K1 later, one pole per leg ----
    line(d, (19.5, 0), (28, 0)); dot(d, (28, 0), 'DIRECT   K1-8 (NO)', loc='top', open_=True)
    line(d, (25.5, -2.5), (28, -2.5)); dot(d, (28, -2.5), 'PAD   K1-6 (NC, relay at rest)', loc='bottom', open_=True)
    dot(d, (30, -1.25), None, open_=True)
    d += elm.Line().at((30, -1.25)).to((28.25, -2.4)).linewidth(2)     # the blade, drawn in the PAD position
    line(d, (30, -1.25), (32, -1.25)); dot(d, (32, -1.25), 'OUT +   K1-4 (COM)   to J5 XLR pin 2', loc='right', open_=True)
    # ---- notes ---------------------------------------------------------------------------
    d += elm.Label().at((0, -7.2)).label(
        'Negative leg, IN - (J4 XLR pin 3 / J2 black) to OUT - (J5 XLR pin 3): identical; R11-R20, RV2, C5-C10, L3, L4; its switch is relay pole B, pins 9 / 13 / 11.\n'
        'XLR pin 1 and shell, J3 (green 4 mm), the ground plane and the box: GND = the QA403\'s Audio Common. Connectors as on the AP AUX-0025; the QA403 takes an XLR-to-two-BNC lead.\n'
        'K1 (Omron G6A-274P-ST-US DC12) is a footprint only until the matrix controller drives it; until then a DPDT toggle is wired into its six contact holes. Coil on J9 (1 = +12 V), D1 1N4148 across the coil, cathode (band) to J9-1.\n'
        'With K1 at rest or a toggle in the PAD position the analyzer sees 1/20 of the amplifier; DIRECT is the full voltage, limited to 40 Vrms by the QA403.',
        halign='left', fontsize=8)

    d.save(os.path.join(HERE, 'aes17-filter-schematic.svg'))
    d.save(os.path.join(HERE, 'aes17-filter-schematic.png'), dpi=150)
    d.save(os.path.join(HERE, 'fab', 'aes17-filter-schematic.pdf'))   # the release copy
print('ok')
