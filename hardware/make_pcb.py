#!/usr/bin/env python3
"""Builds aes17-filter.kicad_pcb from design.py with KiCad's pcbnew module (KiCad 7).

    python3 hardware/aes17-filter/make_pcb.py            # writes the board and a DRC report

Everything is placed and routed from the tables below, so the board is reproducible from the
repository without a mouse. Coordinates are millimetres, x along the front edge (input end at 0),
y from the front edge backwards. The filter band was laid out first on a 100 mm deep board; its
coordinates are kept as they were and moved back by design.FRONT, so 'core' coordinates below
are written in that 0..100 frame.
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
FRONT = design.FRONT
WALL = design.WALL


def core(y):
    """A y in the filter band's own 0..100 frame, moved behind the connector strip."""
    return y + FRONT


def mm(v):
    return pcbnew.FromMM(v)


def pt(x, y):
    return VECTOR2I(mm(x), mm(y))


# ----------------------------------------------------------------------------------------------
# Placement: ref -> (x, y, rotation in degrees). The footprint origins are KiCad's: for an axial
# resistor pad 1; for the radial inductor pad 1; for the FKP2 capacitor pad 1; for the Cliff
# socket its signal pin, front facing -x at rotation 0; for the header pin 1.
# ----------------------------------------------------------------------------------------------
Y_P = core(17.0)      # the positive leg's signal line
Y_N = core(83.0)      # the negative leg, mirrored about the band's centre line
# x positions along the signal line (pad 1 of each part); the pitches are the footprints'
X_IN_BUS = 30.0
X_R1 = 36.0           # 1k 3W, pitch 20.32 -> pad 2 at 56.32
X_R1C = 46.16         # 14k, pitch 10.16 -> pad 2 at 56.32
X_A_BUS = 58.85       # the node-A vertical, 0.88 mm from the T pads on either side
X_RV = 60.7
X_L1 = 64.0           # pads 64 / 69
X_R3 = 62.0           # 412, pads 62 / 72.16
X_C34 = 76.5          # first 220p of the bypass pair, pads 76.5 / 81.5
X_C34B = 84.5         # second 220p, pads 84.5 / 89.5
X_R5 = 74.5           # 75R 1W, pitch 15.24 -> pad 2 at 89.74
# The second stage sits 38 mm behind the first (coil centre to coil centre): magnetic coupling
# between drum cores falls with the cube of the distance, and coupling from L1 into L2 is the one
# path that bypasses the filter (it is what spoilt Matt Clark's V1).
X_L3 = 102.0          # pads 102 / 107
X_R7 = 102.0          # 3.4k across L3, pads 102 / 112.16
X_R9 = 113.0          # 24.9, pads 113 / 123.16
X_C1, X_C7, X_C9 = 62.0, 76.0, 108.0   # the shunt capacitors, standing in a row at y +- 25
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


place_leg(design.NAMES_P, Y_P, flip=False)
place_leg(design.NAMES_N, Y_N, flip=True)

# The two pads stand side by side in one block right behind the switch, as six upright resistors
# with the 20:1 taps and the direct ends at the top, towards the switch. Both pads are the same
# copy (not mirror images), so they share one temperature and one geometry and their ratios
# track. The positive leg's output is next door; the negative leg's output comes forward from the
# back of the board on its own track, at the 24.9 ohm node, the lowest impedance in the chain.
PAD_TOP, PAD_COLS = 28.5, (127.0, 132.5, 138.0, 143.5, 149.0, 154.5)
for (ref_hi, ref_mid, ref_lo), (c_hi, c_mid, c_lo) in (
        (('R8', 'R9', 'R10'), PAD_COLS[:3]), (('R18', 'R19', 'R20'), PAD_COLS[3:])):
    PLACE[ref_hi] = (c_hi, PAD_TOP, 270)            # 10 k: direct end on top, the middle node below
    PLACE[ref_mid] = (c_mid, PAD_TOP + 15.24, 90)   # 10 k: middle node below, tap on top
    PLACE[ref_lo] = (c_lo, PAD_TOP, 270)            # 1 k 0.1 %: tap on top, ground below

# The connector row on the front edge, all faces towards -y. Each one's front is located from its
# footprint's fabrication layer (the flange), so that the flange's front face or the socket's
# shoulder lands on the wall's inner face at y = WALL:
#   Neutrik NC3FAAH2 (female): flange at footprint x = 12.7..15.4, front at +x; turned 90 the
#     front faces -y and the flange's front face is 15.4 in front of pin 1. The axis is at
#     footprint (-0.62, 3.79), i.e. 3.79 to the right of pin 1 once turned.
#   Neutrik NC3MAAH (male): flange at footprint y = 17.78..20.48, front at +y; turned 180 the
#     front faces -y, 20.48 in front of the pin row. The axis is 3.81 to the left of pin 1.
#   Cliff S16N-PC: the barrel faces -x, its shoulder 13.5 in front of the signal pin; turned 270
#     it faces -y.
# X positions of the axes along the front: XLR in, red and black at AP's 19.05 mm, green common;
# then the XLR out; then the pad toggle, which sits in the wall straight above the switch.
AX_XLR_IN, AX_RED, AX_BLACK, AX_GREEN, AX_XLR_OUT, AX_TOGGLE = 18.0, 45.0, 64.05, 85.0, 112.0, 136.0
# The switch: K1's footprint, turned half round so that the positive pole's row (F, PAD, OUT,
# coil +) is the back row, next to the pad block, and the negative pole's row the front one.
# Without the relay its six contact holes take the toggle's six wires: COM = OUT, NC = PAD,
# NO = DIRECT, the toggle being 15 mm above them.
K1_X, K1_Y = 144.78, 15.0
PLACE.update({
    'J4': (AX_XLR_IN - 3.79, WALL + 15.4, 90),
    'J1': (AX_RED, WALL + 13.5, 270), 'J2': (AX_BLACK, WALL + 13.5, 270), 'J3': (AX_GREEN, WALL + 13.5, 270),
    'J5': (AX_XLR_OUT + 3.81, WALL + 20.48, 180),
    'K1': (K1_X, K1_Y, 180), 'J9': (150.0, K1_Y, 0), 'D1': (154.5, K1_Y, 90),
    # M3 holes for stand-offs on the chassis' bottom plate: four plain ones on the band's centre
    # line, and H5, plated and on ground, in the connector strip: the one point where the board's
    # ground meets the chassis, next to where the cables come in
    'H1': (14.0, core(50.0), 0), 'H2': (50.0, core(50.0), 0), 'H3': (90.0, core(50.0), 0), 'H4': (151.5, core(50.0), 0),
    'H5': (34.75, 10.0, 0),
})

# ----------------------------------------------------------------------------------------------
# Footprints the library does not have
# ----------------------------------------------------------------------------------------------
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
        return {'Relay_DPDT_Omron_G6A-274P': fp_relay_g6a, 'L_Radial_D11.5mm_P5.00mm': fp_radial_coil}[fpname](board)
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
# The whole filter, up to and including OUT in the direct position, carries the amplifier's
# voltage: 120 V peak at the 85 Vrms rating, 200 V peak at the 140 Vrms V2 once claimed. IPC-2221B
# asks 0.8 mm between bare pads (A6) and 0.4 mm between masked tracks (B4) for 101-300 V, so the
# board keeps 0.8 mm everywhere; it has the room.
CLEARANCE = 0.8
W_SIG = 0.5
W_IN = 0.8


def leg_routes(n, y0, s):
    """Routes of one leg. n: the leg's reference names; y0: its signal line; s: +1 for the
    positive leg (side parts towards +y), -1 for the negative leg."""
    def Y(dy):
        return y0 + dy * s
    nets = design.NETS_P if s > 0 else design.NETS_N
    return [
        # the input bus: a vertical at X_IN_BUS joins the socket, the BNC and the three resistors
        (nets['IN'], F, W_IN, [(X_IN_BUS, Y(13.0)), (X_IN_BUS, Y(-5.0)), (n['R1a'], 1)]),
        (nets['IN'], F, W_IN, [(X_IN_BUS, Y(5.0)), (n['R1b'], 1)]),
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
        # F, the filter output, and the pad are routed with the switch, below
    ]


# The input pair. XLR pin 2 (+) and the red socket run along y = 21 on the top; XLR pin 3 (-) and
# the black socket along the same line on the bottom, right under it, and both turn down x = 30
# together, so the pair encloses no area until the positive leg branches off. The negative input
# then carries on down x = 30 on the bottom to its own leg.
INPUT_ROUTES = [
    ('IN_P', F, W_IN, [('J4', 2), (24.0, 12.7), (24.0, 21.0), (AX_RED, 21.0), ('J1', 1)]),
    ('IN_P', F, W_IN, [(X_IN_BUS, 21.0), (X_IN_BUS, Y_P - 5.0)]),
    ('IN_N', B, W_IN, [('J4', 3), (18.02, 21.0), (AX_BLACK, 21.0), ('J2', 1)]),
    ('IN_N', B, W_IN, [(X_IN_BUS, 21.0), (X_IN_BUS, Y_N - 5.0), ('R12', 1)]),
]

# The output end, all on the outer layers so that both inner layers stay whole ground planes:
# the positive pole's nets on the top, the negative pole's on the bottom, each over its own plane.
#   K1 (turned half round), back row y = 15: F_P 127.0, PAD_P 132.08, OUT_P 137.16, COIL+ 144.78
#                           front row y = 7.38: F_N, PAD_N, OUT_N, COIL- at the same x
#   pad block tops y = 28.5: F_P 127, PAD_P 132.5 + 138, F_N 143.5, PAD_N 149 + 154.5
#   J5: OUT_P pin 2 (108.19, 17.18), OUT_N pin 3 (112.0, 17.18)
X_F_N = 141.0         # the negative output's run from the back, between the two pads
MIDDLE_ROUTES = [
    # positive pole, top layer: straight up from the pad block into the back row
    ('F_P', F, W_SIG, [('R7', 2), (123.16, PAD_TOP), ('R8', 1), ('K1', 8)]),
    ('M_P', F, W_SIG, [('R8', 2), ('R9', 1)]),
    ('PAD_P', F, W_SIG, [('R10', 1), ('R9', 2), (132.5, 17.5), ('K1', 6)]),
    # negative pole, bottom layer: F_N from the back of the board, PAD_N from its pad, both through
    # the back row between its pins to the front row, nested so that they never cross
    ('F_N', B, W_SIG, [('R17', 2), (X_F_N, Y_N), (X_F_N, 22.0), (129.54, 22.0), (129.54, 10.0), ('K1', 9)]),
    ('F_N', B, W_SIG, [(X_F_N, PAD_TOP), ('R18', 1)]),
    ('M_N', F, W_SIG, [('R18', 2), ('R19', 1)]),
    ('PAD_N', F, W_SIG, [('R20', 1), ('R19', 2)]),
    ('PAD_N', B, W_SIG, [('R19', 2), (149.0, 20.0), (134.62, 20.0), (134.62, 10.0), ('K1', 11)]),
    # the commons to the XLR: OUT_P on the top between the two rows, OUT_N on the bottom in front of
    # them, side by side, 2 mm apart and one above the other plane, all the way to the connector
    ('OUT_P', F, W_SIG, [('K1', 4), (137.16, 11.2), (122.5, 11.2), (122.5, 23.0), (AX_XLR_OUT - 3.81, 23.0), ('J5', 2)]),
    ('OUT_N', B, W_SIG, [('K1', 13), (137.16, 3.0), (124.5, 3.0), (124.5, 21.0), (AX_XLR_OUT, 21.0), ('J5', 3)]),
    # relay coil: K1, header and flyback diode in one line
    ('COIL+', F, W_SIG, [('K1', 1), ('J9', 1), ('D1', 1)]),
    ('COIL-', F, W_SIG, [('K1', 16), ('D1', 2)]),
    ('COIL-', B, W_SIG, [('J9', 2), (152.3, 17.54), (152.3, 9.5), ('D1', 2)]),
]

VIAS = []


def resolve(fps, point):
    if isinstance(point[0], str):
        return pad_xy(fps, point[0], point[1])
    return point


def add_tracks(board, fps, netinfo):
    routes = leg_routes(design.NAMES_P, Y_P, +1) + leg_routes(design.NAMES_N, Y_N, -1) + INPUT_ROUTES + MIDDLE_ROUTES
    layer_id = {F: pcbnew.F_Cu, B: pcbnew.B_Cu}
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
    for layer in (pcbnew.In1_Cu, pcbnew.In2_Cu):   # nothing else is routed on the inner layers
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


def add_text(board, text, x, y, size=1.0, layer=pcbnew.F_SilkS, angle=0, bold=False, left=False):
    """A silkscreen text centred on (x, y), or starting there with left=True. Text on the bottom
    layer is mirrored so that it reads from below; a left-aligned one then runs towards -x."""
    t = pcbnew.PCB_TEXT(board)
    t.SetText(text); t.SetPosition(pt(x, y)); t.SetLayer(layer)
    t.SetTextSize(VECTOR2I(mm(size), mm(size))); t.SetTextThickness(mm(max(0.15, size * 0.15)))
    t.SetTextAngleDegrees(angle); t.SetBold(bold)
    if layer == pcbnew.B_SilkS:
        t.SetMirrored(True)
    if left:
        t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_LEFT)
    board.Add(t)


def add_line(board, x1, y1, x2, y2, layer=pcbnew.F_SilkS, width=0.15):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(pt(x1, y1)); s.SetEnd(pt(x2, y2))
    s.SetLayer(layer); s.SetWidth(mm(width))
    board.Add(s)


def add_arrow(board, x1, x2, y):
    """A left-to-right arrow on the top silkscreen, for the signal flow."""
    add_line(board, x1, y, x2, y)
    add_line(board, x2 - 0.9, y - 0.5, x2, y)
    add_line(board, x2 - 0.9, y + 0.5, x2, y)


def add_warning(board, x, y, side=4.0, layer=pcbnew.F_SilkS):
    """A warning triangle with an exclamation mark, centred on (x, y)."""
    h = side * 0.866
    top, left, right = (x, y - h / 2), (x - side / 2, y + h / 2), (x + side / 2, y + h / 2)
    for a, b in ((top, left), (left, right), (right, top)):
        add_line(board, *a, *b, layer, width=0.25)
    add_line(board, x, y - h / 2 + 1.0, x, y + h / 2 - 1.3, layer, width=0.35)
    add_line(board, x, y + h / 2 - 0.75, x, y + h / 2 - 0.55, layer, width=0.35)


def add_block(board, lines, x, y, size=1.0, pitch=1.75):
    """Lines of bottom-side text, left-aligned as read from below; (x, y) is the first line's
    start, which seen from the top is the block's right-hand edge."""
    for i, line in enumerate(lines):
        if line:
            add_text(board, line, x, y + i * pitch * size, size, pcbnew.B_SilkS, left=True)


# Short values for the silkscreen: "R1 1k 3W", in the R/k/n notation that survives a lost dot.
SHORT_VALUE = {
    '1.00k 3W': '1k 3W', '14.0k': '14k', '500R': '500R', '220p': '220p', '412R': '412R', '1mH': '1mH',
    '4.7n': '4n7', '75.0R 1W': '75R 1W', '3.40k': '3k4', '24.9R': '24R9', '10.0k 1W': '10k 1W',
    '1.00k 0.1%': '1k 0.1%', '1N4148': '1N4148',
}
TITLE, REVISION, DATE = 'AES17 filter', 'rev A', '2026-11'
SOURCE = 'github.com/ToxSox/aes17_filter'


def add_silk(board, fps):
    F_SILK = pcbnew.F_SilkS
    values = {ref: value for ref, value, *_ in design.PARTS}
    # ---- every part: reference and value in one label where its reference stood ---------------
    for ref, fp in fps.items():
        r = fp.Reference()
        if ref.startswith('H') or ref.startswith('J') or ref == 'K1':
            if ref.startswith('H') or ref in ('J9', 'K1'):
                r.SetVisible(False)            # holes need no names; J9 and K1 get their own labels
            continue
        if ref in ('R8', 'R9', 'R10', 'R18', 'R19', 'R20'):
            continue                           # the pad block: names in the bodies, values below
        x, y = pcbnew.ToMM(r.GetPosition().x), pcbnew.ToMM(r.GetPosition().y)
        angle = r.GetDrawRotation().AsDegrees() % 180     # as drawn on the board, kept readable
        if ref.startswith('L'):                # the coils' names sat on their pads: put them beside
            x = pcbnew.ToMM(fp.GetPosition().x) + 2.5
            y = Y_P + 7.2 if abs(pcbnew.ToMM(fp.GetPosition().y) - Y_P) < 1 else Y_N - 7.2
            angle = 0
        if ref == 'D1':
            x, angle = 156.5, 90               # beside the diode, clear of its 'K'
        if ref == 'RV1':
            x = 64.36                          # on the side away from R3's pad, as RV2's
        r.SetVisible(False)
        add_text(board, f'{ref} {SHORT_VALUE[values[ref]]}', x, y, 1.0, angle=angle)
    # the pad block: one legend under each pad
    for x, (hi, lo) in ((132.5, ('R8 R9 10k 1W', 'R10 1k 0.1%')), (149.0, ('R18 R19 10k 1W', 'R20 1k 0.1%'))):
        add_text(board, hi, x, 47.2); add_text(board, lo, x, 49.0)
    for ref in ('R8', 'R9', 'R18', 'R19'):
        fps[ref].Reference().SetTextSize(VECTOR2I(mm(1.0), mm(1.0)))   # the 1 k bodies are too slim: 0.8
    # ---- connectors, switch and coil -----------------------------------------------------------
    add_text(board, 'IN XLR 2+ 3-', AX_XLR_IN, 21.6)
    add_text(board, 'IN +', AX_RED, 18.5, 1.2); add_text(board, 'IN -', AX_BLACK, 18.5, 1.2); add_text(board, 'GND', AX_GREEN, 18.5, 1.2)
    add_text(board, 'OUT XLR 2+ 3-', AX_XLR_OUT, 21.6)
    add_text(board, 'chassis', 34.75, 15.0)
    for x, name in ((K1_X - 17.78, 'DIR'), (K1_X - 12.7, 'PAD'), (K1_X - 7.62, 'COM')):
        add_text(board, '+' + name, x, K1_Y + 3.0)
        add_text(board, '-' + name, x, K1_Y - 7.62 - 3.0)
    add_text(board, 'K1: toggle wires (relay not fitted)', 135.0, 21.2)
    add_text(board, '+12V', 150.0, 12.8)
    add_text(board, 'J9', 147.8, 16.3, angle=90)
    # ---- signal flow, one line per leg along its outer edge -----------------------------------
    for y, sign in ((26.3, '+'), (121.3, '-')):
        add_text(board, sign + ' LEG', 19.0, y, 1.2, bold=True)
        add_arrow(board, 24.0, 33.5, y)
        add_text(board, 'INPUT 483-575R', 46.0, y)
        add_arrow(board, 55.0, 67.5, y)
        add_text(board, 'STAGE 1', 75.0, y)
        add_arrow(board, 80.5, 99.5, y)
        add_text(board, 'STAGE 2', 106.0, y)
    add_arrow(board, 111.5, 119.5, 26.3)
    add_text(board, 'PAD 21.8:1', 140.5, 26.3)
    add_arrow(board, 111.5, 119.5, 121.3)
    add_text(board, 'to PAD - (front)', 132.0, 121.3)
    add_text(board, 'trim: 20 kHz = 1 kHz', 48.0, core(36.0)); add_text(board, 'trim: 20 kHz = 1 kHz', 48.0, core(64.0))
    # ---- high voltage, where the voltage comes in ------------------------------------------------
    add_warning(board, 15.0, 36.0, 6.0)
    add_text(board, 'HIGH VOLTAGE', 15.0, 42.0, 1.3, bold=True)
    for i, line in enumerate(('up to 120 V peak', 'on inputs, both', 'legs and OUT')):
        add_text(board, line, 15.0, 44.8 + 1.8 * i)
    # ---- title --------------------------------------------------------------------------------
    add_text(board, f'{TITLE} {REVISION}', 128.0, 70.0, 1.6, bold=True)
    add_text(board, f'{DATE}  CERN-OHL-W-2.0', 128.0, 73.0)
    add_text(board, SOURCE, 128.0, 75.0)
    # ---- the bottom: a crib sheet, read from below -----------------------------------------------
    B = pcbnew.B_SilkS
    add_text(board, f'{TITLE} {REVISION}', 156.5, 50.0, 1.6, B, bold=True, left=True)
    add_block(board, [
        f'{DATE}  CERN-OHL-W-2.0',
        SOURCE,
        'after AP AUX-0025 and M. Clark V2',
        'passive AES17 low-pass, 100k load',
        'chassis bond: H5 only, metal spacer',
    ], 156.5, 53.0)
    add_block(board, [
        'PAD SWITCH: toggle wires into K1',
        '+ back row:  COM 4  PAD 6  DIR 8',
        '- front row: COM 13 PAD 11 DIR 9',
        'later relay G6A-274P DC12:',
        '  at rest = PAD, coil J9 1 = +12V',
        'PAD about 21.8:1 - measure it',
    ], 156.5, 81.0)
    add_block(board, [
        'IN  XLR-F: 2 +  3 -  1 GND',
        '4 mm: red +, black -,',
        '      green GND',
        'OUT XLR-M: 2 +  3 -  1 GND',
        'to QA403: XLR-F to 2 BNC,',
        '  2 -> L+, 3 -> L-,',
        '  1 -> both shells',
    ], 27.5, 26.0)
    add_block(board, [
        'TRIM RV1 (+), RV2 (-):',
        'through an amplifier, one',
        'leg at a time, until',
        '20 kHz = 1 kHz; not from the',
        'QA403 output (100R)',
    ], 99.5, 48.0)
    add_warning(board, 104.0, 86.6, 3.6, B)
    add_text(board, 'HIGH VOLTAGE', 99.5, 87.0, 1.3, B, bold=True, left=True)
    add_block(board, [
        'up to 120 V peak on inputs,',
        'both legs, OUT when direct',
        '85 Vrms max at 20 kHz',
        'QA403 max 40 Vrms: use PAD',
    ], 99.5, 89.6)


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
    nc.SetClearance(mm(CLEARANCE)); nc.SetTrackWidth(mm(0.5)); nc.SetViaDiameter(mm(0.8)); nc.SetViaDrill(mm(0.4))
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
        if ref in ('R8', 'R9', 'R10', 'R18', 'R19', 'R20'):
            # the pad block stands upright and close: each name inside its own body
            pitch = 10.16 if ref in ('R10', 'R20') else 15.24
            fp.Reference().SetPosition(pt(x, PAD_TOP + pitch / 2))
            fp.Reference().SetTextAngleDegrees(90)
        board.Add(fp)
        fps[ref] = fp
        # connector drawings that reach past the board (through the front wall): drop them
        for item in list(fp.GraphicalItems()):
            bb = item.GetBoundingBox()
            if item.GetLayer() == pcbnew.F_SilkS and (pcbnew.ToMM(bb.GetRight()) < 0.3 or pcbnew.ToMM(bb.GetLeft()) > L - 0.3
                                                      or pcbnew.ToMM(bb.GetTop()) < 0.0):   # outlines past the front edge
                fp.Remove(item)
        if ref == 'J5':
            # Neutrik's 3.4 mm lands on pins 1 and 2 leave 0.66 mm to pin 3; 3.0 mm (0.7 mm ring
            # on the 1.6 mm hole) gives 0.86 mm, inside the 0.8 mm the output needs in the direct position
            for pad in fp.Pads():
                if pad.GetNumber() in ('1', '2'):
                    pad.SetSize(VECTOR2I(mm(3.0), mm(3.0)))
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
    add_silk(board, fps)
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
