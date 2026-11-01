#!/usr/bin/env python3
"""Builds aes17-filter.kicad_pcb from design.py with KiCad's pcbnew module (KiCad 7).

    python3 hardware/aes17-filter/make_pcb.py            # writes the board and a DRC report

Everything is placed and routed from the tables below, so the board is reproducible from the
repository without a mouse. Coordinates are millimetres, x along the board (input end at 0),
y across it (positive leg at the top).
"""
import os
import sys

import pcbnew
from pcbnew import VECTOR2I, wxPoint

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import design  # noqa: E402

OUT = os.path.join(HERE, 'aes17-filter.kicad_pcb')
LIB = '/usr/share/kicad/footprints'

L, W = design.BOARD_LENGTH, design.BOARD_WIDTH


def mm(v):
    return pcbnew.FromMM(v)


def pt(x, y):
    return VECTOR2I(mm(x), mm(y))


# ----------------------------------------------------------------------------------------------
# Placement: ref -> (x, y, rotation in degrees). The footprint origins are KiCad's: for an axial
# resistor pad 1; for the radial inductor pad 1; for the FKP2 capacitor pad 1; for the Cliff
# socket its signal pin, front facing -x at rotation 0; for the header pin 1.
# ----------------------------------------------------------------------------------------------
Y_P = 17.0            # the positive leg's signal line
Y_N = W - Y_P         # the negative leg, mirrored
# x positions along the signal line (pad 1 of each part); the pitches are the footprints'
X_IN_BUS = 30.0
X_R1 = 36.0           # 1k 3W, pitch 20.32 -> pad 2 at 56.32
X_R1C = 46.16         # 14k, pitch 10.16 -> pad 2 at 56.32
X_A_BUS = 58.8        # the node-A vertical
X_RV = 60.5
X_L1 = 64.0           # pads 64 / 69
X_R3 = 62.0           # 412, pads 62 / 72.16
X_C34 = 76.5          # first 220p of the bypass pair, pads 76.5 / 81.5
X_C34B = 84.5         # second 220p, pads 84.5 / 89.5
X_R5 = 74.5           # 75R 1W, pitch 15.24 -> pad 2 at 89.74
X_L3 = 96.0           # pads 96 / 101
X_R7 = 96.0           # 3.4k across L3, pads 96 / 106.16
X_R9 = 107.0          # 24.9, pads 107 / 117.16
X_R11 = 119.5         # 10k 1W, pitch 15.24 -> pads 119.5 / 134.74
X_R13 = 130.7         # 1k 0.1 %, pads 130.7 / 140.86
X_C1, X_C7, X_C9 = 62.0, 76.0, 102.0   # the shunt capacitors, standing in a row at y +- 25
PLACE = {}


def place_leg(names, y, flip):
    """Lays out one leg along the signal line at y; the lower leg is the upper one mirrored."""
    s = -1 if flip else 1
    rot_v = 90 if flip else 270      # vertical parts: pad 1 towards the signal line
    PLACE[names['R1a']] = (X_R1, y - 5.0 * s, 0)
    PLACE[names['R1b']] = (X_R1, y + 5.0 * s, 0)
    PLACE[names['R1c']] = (X_R1C, y + 13.0 * s, 0)
    PLACE[names['RV1']] = (X_RV, y + 13.0 * s, 270 if flip else 90)
    PLACE[names['C1']] = (X_C1, y + 25.0 * s, rot_v)
    PLACE[names['L1']] = (X_L1, y, 0)
    PLACE[names['R3']] = (X_R3, y - 9.0 * s, 0)
    PLACE[names['C34']] = (X_C34, y - 9.0 * s, 0)
    PLACE[names['C34b']] = (X_C34B, y - 9.0 * s, 0)
    PLACE[names['C7']] = (X_C7, y + 25.0 * s, rot_v)
    PLACE[names['R5']] = (X_R5, y, 0)
    PLACE[names['L3']] = (X_L3, y, 0)
    PLACE[names['R7']] = (X_R7, y - 9.0 * s, 0)
    PLACE[names['C9']] = (X_C9, y + 25.0 * s, rot_v)
    PLACE[names['R9']] = (X_R9, y, 0)
    PLACE[names['R11']] = (X_R11, y - 6.0 * s, 0)
    PLACE[names['R12']] = (X_R11, y + 6.0 * s, 0)
    PLACE[names['R13']] = (X_R13, y + 14.0 * s, 0)


place_leg(design.NAMES_P, Y_P, flip=False)
place_leg(design.NAMES_N, Y_N, flip=True)

PLACE.update({
    # input end plate: BNC +, red, green, black, BNC -  (top to bottom); the sockets' fronts
    # protrude through the plate, their signal pins sit 12 and 14 mm inside the board
    'J4': (12.0, 14.0, 0), 'J1': (14.0, 32.0, 0), 'J3': (14.0, 50.0, 0), 'J2': (14.0, 68.0, 0), 'J5': (12.0, 86.0, 0),
    # output end plate: BNC + and BNC -, the toggle goes between them in the plate
    'J6': (L - 12.0, 20.0, 180), 'J7': (L - 12.0, 80.0, 180),
    # pad switch header (rows: 1-3-5 at y = 47.46 with pin 1 at the right, 2-4-6 at y = 50),
    # relay and coil connector in the middle band
    'J8': (144.54, 47.46, 270), 'K1': (118.0, 46.19, 0), 'J9': (108.0, 48.73, 0), 'D1': (112.0, 50.0, 270),
    # mounting holes, for a box without rails; on the centre line where nothing else is
    'H1': (44.0, 50.0, 0), 'H2': (90.0, 50.0, 0), 'H3': (153.5, 38.0, 0), 'H4': (153.5, 62.0, 0),
})

# ----------------------------------------------------------------------------------------------
# Footprints the library does not have
# ----------------------------------------------------------------------------------------------
BNC = dict(   # TE 5227161-x (drawing C-5227161) and Amphenol 31-5431 share this pattern
    pin_from_front=11.43,     # contact post behind the housing's panel face, mm
    axis_height=6.91,         # BNC axis above the PCB for the -7/-9 low-profile variants (8.59 for -1/-2/-3/-6)
    hooks=[(-5.08, 5.08), (-5.08, -5.08)],   # two 2.01 mm mounting hooks, 10.16 apart, 5.08 in front of the posts
    posts=[(0.0, 2.54), (0.0, -2.54)],       # the ground post is 2.54 beside the contact; both sides are padded
    body=(14.76, 13.72),      # housing width (y) and length behind the panel face (x)
)


def new_footprint(board, name, descr):
    fp = pcbnew.FOOTPRINT(board)
    fp.SetFPID(pcbnew.LIB_ID('klirr', name))
    fp.SetDescription(descr)
    fp.SetAttributes(pcbnew.FP_THROUGH_HOLE)
    return fp


def add_tht_pad(fp, number, x, y, drill, size, shape=pcbnew.PAD_SHAPE_CIRCLE):
    pad = pcbnew.PAD(fp)
    pad.SetNumber(str(number))
    pad.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
    pad.SetShape(shape)
    pad.SetSize(VECTOR2I(mm(size), mm(size)))
    pad.SetDrillSize(VECTOR2I(mm(drill), mm(drill)))
    pad.SetLayerSet(pcbnew.LSET.AllCuMask().addLayer(pcbnew.F_Mask).addLayer(pcbnew.B_Mask))
    pad.SetPos0(pt(x, y))
    pad.SetPosition(pt(x, y))
    fp.Add(pad)
    return pad


def add_fp_line(fp, x1, y1, x2, y2, layer=pcbnew.F_SilkS, width=0.12):
    s = pcbnew.FP_SHAPE(fp)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart0(pt(x1, y1)); s.SetEnd0(pt(x2, y2))
    s.SetStart(pt(x1, y1)); s.SetEnd(pt(x2, y2))
    s.SetLayer(layer)
    s.SetWidth(mm(width))
    fp.Add(s)


def fp_bnc(board):
    fp = new_footprint(board, 'BNC_TE_5227161_Horizontal', 'TE 5227161 / Amphenol 31-5431 right-angle bulkhead BNC jack, panel face at -x')
    add_tht_pad(fp, 1, 0, 0, 1.2, 2.0)
    for dx, dy in BNC['hooks']:
        add_tht_pad(fp, 2, dx, dy, 2.3, 3.4)
    for dx, dy in BNC['posts']:
        add_tht_pad(fp, 2, dx, dy, 1.2, 2.0)
    front = -BNC['pin_from_front']
    w, length = BNC['body']
    add_fp_line(fp, front, -w / 2, front + length, -w / 2)
    add_fp_line(fp, front, w / 2, front + length, w / 2)
    add_fp_line(fp, front + length, -w / 2, front + length, w / 2)
    add_fp_line(fp, front, -w / 2, front, w / 2)
    c0 = front + 0.6     # the courtyard starts just inside the board edge, where the flange sits
    for (x1, y1, x2, y2) in ((c0, -w / 2 - 0.5, front + length + 0.5, -w / 2 - 0.5),
                             (c0, w / 2 + 0.5, front + length + 0.5, w / 2 + 0.5),
                             (c0, -w / 2 - 0.5, c0, w / 2 + 0.5),
                             (front + length + 0.5, -w / 2 - 0.5, front + length + 0.5, w / 2 + 0.5)):
        add_fp_line(fp, x1, y1, x2, y2, pcbnew.F_CrtYd, 0.05)
    return fp


def fp_radial_coil(board):
    """Radial drum-core inductor, 5 mm pitch, body up to 11 mm (Würth WE-TIS 7447471102: 11 x 11.5 mm,
    0.65 mm leads; WE-TI 7447480102: 10.5 mm). Courtyard 11.5 mm."""
    fp = new_footprint(board, 'L_Radial_D11.5mm_P5.00mm', 'Radial inductor, 5 mm pitch, body up to 11 mm')
    add_tht_pad(fp, 1, 0, 0, 1.3, 2.6, pcbnew.PAD_SHAPE_RECT)
    add_tht_pad(fp, 2, 5.0, 0, 1.3, 2.6)
    cx = 2.5
    for layer, r, w in ((pcbnew.F_SilkS, 5.6, 0.12), (pcbnew.F_CrtYd, 5.75, 0.05)):
        c = pcbnew.FP_SHAPE(fp)
        c.SetShape(pcbnew.SHAPE_T_CIRCLE)
        c.SetStart0(pt(cx, 0)); c.SetEnd0(pt(cx + r, 0))
        c.SetStart(pt(cx, 0)); c.SetEnd(pt(cx + r, 0))
        c.SetLayer(layer); c.SetWidth(mm(w))
        fp.Add(c)
    return fp


def fp_relay_g6a(board):
    """Omron G6A-274P: eight 1.0 mm holes, two rows 7.62 mm apart, pins 1/4/6/8 at 0/7.62/12.70/17.78
    along the row (a 16-pin DIP with the unused positions left out), pins 16/13/11/9 opposite.
    Body 20.2 x 10.1 mm, 8.4 mm high. Pin 1 is the coil +, 16 the coil -; 4 and 13 are the
    commons, 6 and 11 the normally closed, 8 and 9 the normally open contacts (Omron data sheet,
    bottom view)."""
    fp = new_footprint(board, 'Relay_DPDT_Omron_G6A-274P', 'Omron G6A-274P DPDT signal relay, 8 pins')
    row = {1: 0.0, 4: 7.62, 6: 12.70, 8: 17.78}
    for n, x in row.items():
        add_tht_pad(fp, n, x, 0.0, 1.0, 1.7, pcbnew.PAD_SHAPE_RECT if n == 1 else pcbnew.PAD_SHAPE_CIRCLE)
    for n, x in {16: 0.0, 13: 7.62, 11: 12.70, 9: 17.78}.items():
        add_tht_pad(fp, n, x, 7.62, 1.0, 1.7)
    x0, x1 = 17.78 / 2 - 10.1, 17.78 / 2 + 10.1
    y0, y1 = 7.62 / 2 - 5.05, 7.62 / 2 + 5.05
    for (a, b, c, d) in ((x0, y0, x1, y0), (x1, y0, x1, y1), (x1, y1, x0, y1), (x0, y1, x0, y0)):
        add_fp_line(fp, a, b, c, d)
        add_fp_line(fp, a, b, c, d, pcbnew.F_CrtYd, 0.05)
    return fp


def load_footprint(board, key):
    name = design.FP[key]
    lib, fpname = name.split(':')
    if lib == 'klirr':
        return {'BNC_TE_5227161_Horizontal': fp_bnc, 'Relay_DPDT_Omron_G6A-274P': fp_relay_g6a, 'L_Radial_D11.5mm_P5.00mm': fp_radial_coil}[fpname](board)
    fp = pcbnew.FootprintLoad(os.path.join(LIB, lib + '.pretty'), fpname)
    if fp is None:
        raise SystemExit(f'footprint not found: {name}')
    return fp


# ----------------------------------------------------------------------------------------------
# Routing. Each entry: net, layer, list of points; a point is (x, y) or ('REF', pad) for a pad
# centre. Consecutive points become track segments. Vias are listed separately.
# The two legs are routed by one recipe mirrored about the board's centre line.
# ----------------------------------------------------------------------------------------------
F, B = 'F.Cu', 'B.Cu'
W_SIG = 0.5
W_IN = 0.8


I2 = 'In2.Cu'


def leg_routes(n, y0, s):
    """Routes of one leg. n: the leg's reference names; y0: its signal line; s: +1 for the
    positive leg (side parts towards +y), -1 for the negative leg."""
    def Y(dy):
        return y0 + dy * s
    nets = design.NETS_P if s > 0 else design.NETS_N
    jin, jbnc = ('J1', 'J4') if s > 0 else ('J2', 'J5')
    return [
        # the input bus: a vertical at X_IN_BUS joins the socket, the BNC and the three resistors
        (nets['IN'], F, W_IN, [(jin, 1), (X_IN_BUS, Y(15.0)), (X_IN_BUS, Y(-5.0)), (n['R1a'], 1)]),
        (nets['IN'], F, W_IN, [(X_IN_BUS, Y(5.0)), (n['R1b'], 1)]),
        (nets['IN'], F, W_IN, [(jbnc, 1), (X_IN_BUS, Y(-3.0))]),
        (nets['IN'], F, W_IN, [(X_IN_BUS, Y(13.0)), (n['R1c'], 1)]),
        # node A: a vertical at X_A_BUS from the 412 ohm up top down to the 220 pF
        (nets['A'], F, W_SIG, [(n['R1a'], 2), (X_A_BUS, Y(-5.0)), (X_A_BUS, Y(-9.0)), (n['R3'], 1)]),
        (nets['A'], F, W_SIG, [(X_A_BUS, Y(-5.0)), (X_A_BUS, Y(25.0)), (n['C1'], 1)]),
        (nets['A'], F, W_SIG, [(n['R1c'], 2), (X_A_BUS, Y(13.0))]),
        (nets['A'], F, W_SIG, [(n['RV1'], 2), (X_A_BUS, Y(15.54))]),
        (nets['A'], F, W_SIG, [(n['RV1'], 3), (X_A_BUS, Y(18.08))]),
        (nets['A'], F, W_SIG, [(X_A_BUS, Y(0.0)), (n['L1'], 1)]),
        # T: the second 1 k into the trimmer, on the back so it can cross the A bus
        (nets['T'], B, W_SIG, [(n['R1b'], 2), (X_RV, Y(5.0)), (n['RV1'], 1)]),
        # X: 412 ohm into the two 220 pF; the second one is reached on the back, past the first's other pad
        (nets['X'], F, W_SIG, [(n['R3'], 2), (n['C34'], 1)]),
        (nets['X'], B, W_SIG, [(n['C34'], 1), (X_C34, Y(-12.0)), (X_C34B, Y(-12.0)), (n['C34b'], 1)]),
        # B: coil out, 75 ohm in, the bypass pair back, 4.7 nF down
        (nets['B'], F, W_SIG, [(n['L1'], 2), (n['R5'], 1)]),
        (nets['B'], F, W_SIG, [(n['C34b'], 2), (X_C34B + 5.0, Y(-4.0)), (X_L1 + 5.0, Y(-4.0)), (n['L1'], 2)]),
        (nets['B'], F, W_SIG, [(n['C34'], 2), (X_C34 + 5.0, Y(-4.0))]),
        (nets['B'], F, W_SIG, [(n['R5'], 1), (X_R5, Y(25.0)), (n['C7'], 1)]),
        # D: 75 ohm out into the second coil and its 3.4 k
        (nets['D'], F, W_SIG, [(n['R5'], 2), (n['L3'], 1), (n['R7'], 1)]),
        # E: second coil out, 3.4 k back, 4.7 nF down, 24.9 ohm on
        (nets['E'], F, W_SIG, [(n['L3'], 2), (n['R9'], 1)]),
        (nets['E'], F, W_SIG, [(n['R7'], 2), (X_R7 + 10.16, Y(-4.0)), (X_R9, Y(-4.0)), (n['R9'], 1)]),
        (nets['E'], F, W_SIG, [(n['R9'], 1), (X_C9, Y(0.0)), (n['C9'], 1)]),
        # F: filter output into the pad's first resistor; the switch end is routed below
        (nets['F'], F, W_SIG, [(n['R9'], 2), (X_R9 + 10.16, Y(-6.0)), (n['R11'], 1)]),
        # M: between the two 9.53 k
        (nets['M'], F, W_SIG, [(n['R11'], 2), (X_R11 + 15.24, Y(0.0)), (X_R11, Y(0.0)), (n['R12'], 1)]),
        # PAD tap: second 9.53 k into the 1 k; the switch end is routed below
        (nets['PAD'], F, W_SIG, [(n['R12'], 2), (X_R11 + 15.24, Y(10.0)), (X_R13, Y(10.0)), (n['R13'], 1)]),
    ]


# relay pins: 4/13 common (OUT), 6/11 normally closed (PAD), 8/9 normally open (F = direct);
# at x = 125.62, 130.70 and 135.78, rows y = 46.19 (+ leg) and 53.81 (- leg).
# header: pins 1-3-5 (+ leg) at y = 47.46, x = 144.54 / 142.00 / 139.46 = PAD / OUT / F;
# pins 2-4-6 (- leg) at y = 50.
X_F_RUN = 147.5       # the F nets come down the east side on the inner layer
MIDDLE_ROUTES = [
    # --- positive leg ---
    ('F_P', I2, W_SIG, [('R7', 2), (X_R9 + 10.16, 36.0), (X_F_RUN, 36.0), (X_F_RUN, 42.0), (139.46, 42.0), ('J8', 5)]),
    ('F_P', I2, W_SIG, [('K1', 8), (135.78, 42.0), (139.46, 42.0)]),
    ('OUT_P', B, W_SIG, [('J6', 1), (143.0, 20.0), (143.0, 40.0), (125.62, 40.0), ('K1', 4)]),
    ('OUT_P', B, W_SIG, [(142.0, 40.0), ('J8', 3)]),
    ('PAD_P', F, W_SIG, [('R10', 1), (130.7, 34.0), ('K1', 6)]),
    ('PAD_P', F, W_SIG, [(130.7, 38.0), (144.54, 38.0), ('J8', 1)]),
    # --- negative leg ---
    ('F_N', I2, W_SIG, [('R17', 2), (X_R9 + 10.16, 64.0), (X_F_RUN, 64.0), (X_F_RUN, 55.5), (139.46, 55.5), ('J8', 6)]),
    ('F_N', I2, W_SIG, [('K1', 9), (135.78, 55.5), (139.46, 55.5)]),
    ('OUT_N', B, W_SIG, [('J7', 1), (143.0, 80.0), (143.0, 60.0), (125.62, 60.0), ('K1', 13)]),
    ('OUT_N', B, W_SIG, [(142.0, 60.0), ('J8', 4)]),
    ('PAD_N', F, W_SIG, [('R20', 1), (130.7, 66.0), ('K1', 11)]),
    ('PAD_N', F, W_SIG, [(130.7, 62.0), (144.54, 62.0), ('J8', 2)]),
    # --- coil ---
    ('COIL+', F, W_SIG, [('J9', 1), (113.0, 48.73), (113.0, 46.19), ('K1', 1)]),
    ('COIL+', F, W_SIG, [('D1', 1), (113.0, 50.0), (113.0, 48.73)]),
    ('COIL-', F, W_SIG, [('J9', 2), (109.5, 51.27), (109.5, 52.8), (115.0, 52.8), (115.0, 53.81), ('K1', 16)]),
    ('COIL-', F, W_SIG, [('D1', 2), (115.0, 57.62), (115.0, 53.81)]),
]

VIAS = []


def resolve(fps, point):
    if isinstance(point[0], str):
        return pad_xy(fps, point[0], point[1])
    return point


def add_tracks(board, fps, netinfo):
    routes = leg_routes(design.NAMES_P, Y_P, +1) + leg_routes(design.NAMES_N, Y_N, -1) + MIDDLE_ROUTES
    layer_id = {F: pcbnew.F_Cu, B: pcbnew.B_Cu, I2: pcbnew.In2_Cu}
    for net, layer, width, points in routes:
        pts = [resolve(fps, p) for p in points]
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            if abs(x1 - x2) < 1e-6 and abs(y1 - y2) < 1e-6:
                continue
            t = pcbnew.PCB_TRACK(board)
            t.SetStart(pt(x1, y1)); t.SetEnd(pt(x2, y2))
            t.SetWidth(mm(width)); t.SetLayer(layer_id[layer]); t.SetNet(netinfo[net])
            board.Add(t)
    for net, x, y in VIAS:
        v = pcbnew.PCB_VIA(board)
        v.SetPosition(pt(x, y)); v.SetDrill(mm(0.4)); v.SetWidth(mm(0.8))
        v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v.SetNet(netinfo[net])
        board.Add(v)


def add_zones(board, netinfo):
    inset = 1.5
    for layer in (pcbnew.In1_Cu, pcbnew.In2_Cu):   # In2 also carries the two F tracks; the pour keeps clear of them
        z = pcbnew.ZONE(board)
        z.SetLayer(layer); z.SetNet(netinfo['GND'])
        z.SetIsFilled(True)
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
        z.SetThermalReliefGap(mm(0.4)); z.SetThermalReliefSpokeWidth(mm(0.6))
        z.SetMinThickness(mm(0.25)); z.SetLocalClearance(mm(0.4))
        outline = z.Outline()
        outline.NewOutline()
        for (x, y) in ((inset, inset), (L - inset, inset), (L - inset, W - inset), (inset, W - inset)):
            outline.Append(mm(x), mm(y))
        board.Add(z)
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())


def add_text(board, text, x, y, size=1.2, layer=pcbnew.F_SilkS, angle=0, bold=False):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(text); t.SetPosition(pt(x, y)); t.SetLayer(layer)
    t.SetTextSize(VECTOR2I(mm(size), mm(size))); t.SetTextThickness(mm(size * 0.15))
    t.SetTextAngleDegrees(angle); t.SetBold(bold)
    board.Add(t)


def add_silk(board):
    add_text(board, 'klirr AES17 filter', 67.0, 48.8, 1.3, bold=True)
    add_text(board, 'github.com/ToxSox/aes17_filter', 67.0, 51.2, 0.9)
    add_text(board, 'IN +', 24.0, 32.0, 1.2); add_text(board, 'GND', 24.0, 50.0, 1.2); add_text(board, 'IN -', 24.0, 68.0, 1.2)
    add_text(board, 'IN + (bus)', 24.0, 14.0, 1.0); add_text(board, 'IN - (bus)', 24.0, 86.0, 1.0)
    add_text(board, 'OUT + to QA403 L+', 138.0, 14.0, 1.0); add_text(board, 'OUT - to QA403 L-', 138.0, 86.0, 1.0)
    add_text(board, '1-3-5: PAD+ OUT+ DIR+', 151.0, 44.0, 0.8); add_text(board, '2-4-6: PAD- OUT- DIR-', 151.0, 53.5, 0.8)
    add_text(board, 'K1 not fitted: toggle on J8', 127.0, 58.0, 0.8)
    add_text(board, 'positive leg', 86.0, 24.0, 0.9); add_text(board, 'negative leg', 86.0, 76.0, 0.9)
    add_text(board, 'trim: 20 kHz = 1 kHz', 52.0, 37.0, 0.8); add_text(board, 'trim: 20 kHz = 1 kHz', 52.0, 63.0, 0.8)


# ----------------------------------------------------------------------------------------------
def build():
    board = pcbnew.BOARD()
    ds = board.GetDesignSettings()
    board.SetCopperLayerCount(4)
    ds.SetBoardThickness(mm(1.6))
    ds.m_TrackMinWidth = mm(0.2)
    ds.m_ViasMinSize = mm(0.6)
    ds.m_MinThroughDrill = mm(0.3)
    ds.m_MinClearance = mm(0.2)
    ds.m_CopperEdgeClearance = mm(0.5)
    nc = ds.m_NetSettings.m_DefaultNetClass
    nc.SetClearance(mm(0.3)); nc.SetTrackWidth(mm(0.5)); nc.SetViaDiameter(mm(0.8)); nc.SetViaDrill(mm(0.4))
    for lid, name in ((pcbnew.In1_Cu, 'GND1'), (pcbnew.In2_Cu, 'GND2')):
        board.SetLayerName(lid, name)

    # nets
    netinfo = {}
    for name in sorted(design.nets()):
        ni = pcbnew.NETINFO_ITEM(board, name)
        board.Add(ni)
        netinfo[name] = ni

    # outline
    for (x1, y1, x2, y2) in ((0, 0, L, 0), (L, 0, L, W), (L, W, 0, W), (0, W, 0, 0)):
        seg = pcbnew.PCB_SHAPE(board)
        seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
        seg.SetStart(pt(x1, y1)); seg.SetEnd(pt(x2, y2))
        seg.SetLayer(pcbnew.Edge_Cuts); seg.SetWidth(mm(0.1))
        board.Add(seg)

    # footprints
    fps = {}
    for ref, value, fpkey, lcsc, note, pins in design.PARTS:
        fp = load_footprint(board, fpkey)
        fp.SetReference(ref)
        fp.SetValue(value)
        x, y, rot = PLACE[ref]
        fp.SetPosition(pt(x, y))
        fp.SetOrientationDegrees(rot)
        if ref in design.DO_NOT_PLACE:
            fp.SetAttributes(fp.GetAttributes() | pcbnew.FP_EXCLUDE_FROM_POS_FILES | pcbnew.FP_EXCLUDE_FROM_BOM)
        fp.Reference().SetTextSize(VECTOR2I(mm(0.8), mm(0.8)))
        fp.Reference().SetTextThickness(mm(0.15))
        fp.Value().SetVisible(False)
        board.Add(fp)
        fps[ref] = fp
        # connector drawings that protrude through the end plates: drop what lies off the board
        for item in list(fp.GraphicalItems()):
            bb = item.GetBoundingBox()
            if item.GetLayer() == pcbnew.F_SilkS and (pcbnew.ToMM(bb.GetRight()) < 0.3 or pcbnew.ToMM(bb.GetLeft()) > L - 0.3):
                fp.Remove(item)
        for pad_number, net in pins:
            found = False
            for pad in fp.Pads():
                if pad.GetNumber() == str(pad_number):
                    pad.SetNet(netinfo[net]); found = True
            if not found:
                raise SystemExit(f'{ref}: no pad {pad_number} in {design.FP[fpkey]}')
    return board, fps, netinfo


def pad_xy(fps, ref, number):
    for pad in fps[ref].Pads():
        if pad.GetNumber() == str(number):
            p = pad.GetPosition()
            return pcbnew.ToMM(p.x), pcbnew.ToMM(p.y)
    raise KeyError((ref, number))


if __name__ == '__main__':
    board, fps, netinfo = build()
    add_tracks(board, fps, netinfo)
    add_silk(board)
    board.Save(OUT)
    # The zone filler and the DRC want a board that came through the file loader (the in-memory
    # one has no connectivity data yet and the filler crashes on it), so reload before both.
    board = pcbnew.LoadBoard(OUT)
    netinfo = {name: board.FindNet(name) for name in design.nets()}
    add_zones(board, netinfo)
    board.Save(OUT)
    print('wrote', OUT, flush=True)
    report = os.path.join(HERE, 'drc.txt')
    pcbnew.WriteDRCReport(board, report, pcbnew.EDA_UNITS_MILLIMETRES, True)
    txt = open(report).read()
    import re
    print('DRC:', re.findall(r'\*\* Found (\d+) [^*]+\*\*', txt))
    for line in txt.splitlines():
        if line.startswith('[') or line.startswith('    '):
            print('  ', line.strip()[:150])
    if '--pads' in sys.argv:
        fps = {fp.GetReference(): fp for fp in board.GetFootprints()}
        for net, pins in sorted(design.nets().items()):
            print(f"{net:6} " + '  '.join(f"{r}.{p}@({pad_xy(fps, r, p)[0]:.2f},{pad_xy(fps, r, p)[1]:.2f})" for r, p in pins))
