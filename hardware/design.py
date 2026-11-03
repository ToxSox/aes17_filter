"""The AES17 filter board, as data.

Everything that follows - the PCB generator, the JLCPCB bill of materials, the placement file
and the schematic drawing - reads this module, so a value changed here changes all of them.
The circuit is the one in the design review that comes with these files: the AUX-0025 values
per leg, AP's trimmed
input network, a 20:1 pad after the output resistor, switched by a 4PDT toggle in the front
wall, two poles per leg: one connects the pad to the filter output in PAD and takes it off in
DIRECT, the other picks the pad's tap or the filter output for the output XLR. In DIRECT the
filter sees nothing but the analyzer, as the AUX-0025 does.

Coordinates are millimetres on a 158 x 124 mm board: x runs along the front edge from the
input (x = 0) to the output (x = 158), y from the front edge (y = 0) to the back (y = 124).
Every connector sits on the front edge and faces the front long wall of a Hammond 1444-862
aluminium chassis (203 x 152 x 51 mm, flat 1 mm walls), so the filter hangs with that wall
towards the operator, as the AUX-0025's front panel does. The first 24 mm behind the front
edge are the connector strip; the filter itself is the 100 mm band behind it.
"""

import hashlib
import os

TITLE, REVISION, DATE = 'AES17 filter', 'rev A', '2026-11'
SOURCE = 'github.com/ToxSox/aes17_filter'

BOARD_LENGTH = 158.0
BOARD_WIDTH = 124.0
FRONT = 24.0              # depth of the connector strip; the filter band starts here
WALL = -3.3               # the chassis wall's inner face, 3.3 mm in front of the board edge

# Footprints: KiCad 7 library names, or the two that the generator draws itself.
FP = {
    'R_3W':     'Resistor_THT:R_Axial_DIN0614_L14.3mm_D5.7mm_P20.32mm_Horizontal',
    'R_1W':     'Resistor_THT:R_Axial_DIN0414_L11.9mm_D4.5mm_P15.24mm_Horizontal',
    'R_0W6':    'Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal',
    'R_0207_P15': 'Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P15.24mm_Horizontal',   # the pad's 10 k: 0207 body, 1 W pitch
    'C_FKP2_S': 'Capacitor_THT:C_Rect_L7.2mm_W4.5mm_P5.00mm_FKS2_FKP2_MKS2_MKP2',   # 220 p, 390 p
    'C_FKP2_L': 'Capacitor_THT:C_Rect_L7.2mm_W7.2mm_P5.00mm_FKS2_FKP2_MKS2_MKP2',   # 4.7 n
    'L_1mH':    'aes17:L_Radial_D11.5mm_P5.00mm',                      # drawn by the generator; takes the 10.5 mm WE-TI and the 11 mm WE-TIS
    'TRIM':     'Potentiometer_THT:Potentiometer_Bourns_3296W_Vertical',
    'BANANA_R': 'Connector:Banana_Cliff_FCR7350R_S16N-PC_Horizontal',
    'BANANA_B': 'Connector:Banana_Cliff_FCR7350B_S16N-PC_Horizontal',
    'BANANA_G': 'Connector:Banana_Cliff_FCR7350G_S16N-PC_Horizontal',
    'XLR_F':    'Connector_Audio:Jack_XLR_Neutrik_NC3FAAH2_Horizontal',
    'XLR_M':    'Connector_Audio:Jack_XLR_Neutrik_NC3MAAH_Horizontal',
    'WIRES':    'aes17:Wire_Field_4PDT',                       # drawn by the generator: ten solder holes for the toggle
    'HOLE':     'MountingHole:MountingHole_3.2mm_M3',
    'HOLE_GND': 'MountingHole:MountingHole_3.2mm_M3_Pad_Via',
    'TP_LOOP':  'TestPoint:TestPoint_Loop_D2.50mm_Drill1.0mm',
}

# ref, value, footprint key, LCSC part (empty = to be assigned at ordering), note for the BOM.
# MPN gives the manufacturer part number that goes into the JLCPCB "Comment" column for the
# parts whose value alone does not identify them.
# The positive leg's parts are listed first, then the negative leg's with the same values, so
# that the two legs can be checked against each other by eye.
def leg(prefix, names, nets):
    """Builds one leg's parts and connections from the shared recipe. prefix is 'P' or 'N';
    names maps the recipe's roles to reference designators; nets maps role nets to net names."""
    n = nets
    parts = [
        # input network: 1k || 14k || (1k + trimmer)  = 483..575 ohm
        (names['R1a'], '1.00k 3W',  'R_3W',     'C58750', '1 %, 3 W, 50 ppm metal film (UNI-ROYAL MFR03SF1001A10; Vishay RS02B1K000FE12 is C3397612)', [(1, n['IN']), (2, n['A'])]),
        (names['R1b'], '1.00k 3W',  'R_3W',     'C58750', '1 %, 3 W, 50 ppm metal film (UNI-ROYAL MFR03SF1001A10)', [(1, n['IN']), (2, n['T'])]),
        (names['R1c'], '14.0k',     'R_0W6',    'C127223', '1 % metal film 0.25 W (CCO MF1/4W-14K)', [(1, n['IN']), (2, n['A'])]),
        (names['RV1'], '500R',      'TRIM',     'C69564', 'Bourns 3296W-1-501LF, 25 turns', [(1, n['T']), (2, n['A']), (3, n['A'])]),
        # first stage
        (names['C1'],  '220p',      'C_FKP2_S', 'C5742108', 'WIMA FKP2J002201D00HSSD 630 V 2.5 % or FKP2J002201D00ESSD 1 % (Buerklin 42D8516); soldered by hand, LCSC number for reference only', [(1, n['A']), (2, 'GND')]),
        # 0.6 W: this resistor carries the stop band. 0.25 W parts reach their rating at about
        # 30 Vrms per leg at 250-500 kHz, which a filterless class-D output's carrier can be.
        (names['R3'],  '412R',      'R_0W6',    'C1235858', 'Vishay MRS25000C4120FCT00, 1 %, 0.6 W, 50 ppm; same 0207 body: MBB02070C4120FRP00 = C1758271, Yageo MF0207FTE52-412R = C3401155', [(1, n['A']), (2, n['X'])]),
        # 390 pF is not stocked at LCSC; two 220 pF in parallel (440 pF, as the repo has it) are
        (names['C34'], '220p',      'C_FKP2_S', 'C5742108', 'WIMA FKP2J002201D00HSSD 630 V 2.5 % or FKP2J002201D00ESSD 1 % (Buerklin 42D8516); soldered by hand, LCSC number for reference only; one of two in parallel = 440 pF', [(1, n['X']), (2, n['B'])]),
        (names['C34b'], '220p',     'C_FKP2_S', 'C5742108', 'WIMA FKP2J002201D00HSSD 630 V 2.5 % or FKP2J002201D00ESSD 1 % (Buerklin 42D8516); soldered by hand, LCSC number for reference only; one of two in parallel = 440 pF', [(1, n['X']), (2, n['B'])]),
        # the unshielded drum core: the largest air gap, so the most linear ferrite coil of this
        # size, and the coil family V2 measured at -133 dB HD3; the shielded WE-TIS 7447471102
        # (C1331105, +-20 % at JLCPCB) fits the same footprint but is unmeasured for distortion
        (names['L1'],  '1mH',       'L_1mH',    'C1331132', 'Wurth WE-TI 7447480102, unshielded drum core, +-5 %, 1.15 R, 0.8 A; alternative on the same footprint: shielded WE-TIS 7447471102 = C1331105', [(1, n['A']), (2, n['B'])]),
        (names['C7'],  '4.7n',      'C_FKP2_L', 'C20412818', 'WIMA FKP2F014701I00JA00 250 V 5 %; soldered by hand (Digi-Key), LCSC number for reference only', [(1, n['B']), (2, 'GND')]),
        # second stage
        (names['R5'],  '75.0R 1W',  'R_1W',     'C160685', '1 %, 1 W metal film (CCO MF1W-75R)', [(1, n['B']), (2, n['D'])]),
        (names['L3'],  '1mH',       'L_1mH',    'C1331132', 'Wurth WE-TI 7447480102, unshielded drum core, +-5 %, 1.15 R, 0.8 A; alternative on the same footprint: shielded WE-TIS 7447471102 = C1331105', [(1, n['D']), (2, n['E'])]),
        # 0.6 W: around the second stage's resonance (50-150 kHz) this resistor takes the power
        (names['R7'],  '3.40k',     'R_0W6',    'C1366835', 'Vishay MRS25000C3401FCT00, 1 %, 0.6 W, 50 ppm; same 0207 body: MBB02070C3401FCT00 = C1382495', [(1, n['D']), (2, n['E'])]),
        (names['C9'],  '4.7n',      'C_FKP2_L', 'C20412818', 'WIMA FKP2F014701I00JA00 250 V 5 %; soldered by hand (Digi-Key), LCSC number for reference only', [(1, n['E']), (2, 'GND')]),
        (names['R9'],  '24.9R',     'R_0W6',    'C3542579', '1 % metal film 0.25 W (Yageo MFR-25FBF52-24R9)', [(1, n['E']), (2, n['F'])]),
        # the pad: its top (PT) is put on the filter output F by the switch in PAD only, so in
        # DIRECT the filter sees the analyzer alone; the other pole picks the tap or F. 2 x 10.0 k over
        # 1.00 k, all three 0.1 % / 15 ppm from one family: the QA403 subtracts the two legs in its
        # analogue input stage, so the legs' ratios must match each other, which a measured probe
        # factor per channel cannot correct (1 % upper arms left -39 dB of common mode in the
        # difference). 0.25 W each: 0.125 W, half the rating, at 74 Vrms per leg.
        (names['R11'], '10.0k 0.1%', 'R_0207_P15', 'C1364313', '0.1 %, 15 ppm, 0.25 W (TE YR1B10KCC), same family as the 1.00 k', [(1, n['PT']), (2, n['M'])]),
        (names['R12'], '10.0k 0.1%', 'R_0207_P15', 'C1364313', '0.1 %, 15 ppm, 0.25 W (TE YR1B10KCC), same family as the 1.00 k', [(1, n['M']), (2, n['PAD'])]),
        (names['R13'], '1.00k 0.1%', 'R_0W6',   'C1364308', '0.1 %, 15 ppm, 0.25 W (TE YR1B1K0CC)', [(1, n['PAD']), (2, 'GND')]),
    ]
    return parts

NETS_P = dict(IN='IN_P', A='A_P', T='T_P', X='X_P', B='B_P', D='D_P', E='E_P', F='F_P', PT='PT_P', M='M_P', PAD='PAD_P', OUT='OUT_P')
NETS_N = dict(IN='IN_N', A='A_N', T='T_N', X='X_N', B='B_N', D='D_N', E='E_N', F='F_N', PT='PT_N', M='M_N', PAD='PAD_N', OUT='OUT_N')
NAMES_P = dict(R1a='R1', R1b='R2', R1c='R3', RV1='RV1', C1='C1', R3='R4', C34='C2', C34b='C9', L1='L1', C7='C3',
               R5='R5', L3='L2', R7='R6', C9='C4', R9='R7', R11='R8', R12='R9', R13='R10')
NAMES_N = dict(R1a='R11', R1b='R12', R1c='R13', RV1='RV2', C1='C5', R3='R14', C34='C6', C34b='C10', L1='L3', C7='C7',
               R5='R15', L3='L4', R7='R16', C9='C8', R9='R17', R11='R18', R12='R19', R13='R20')

PARTS = leg('P', NAMES_P, NETS_P) + leg('N', NAMES_N, NETS_N) + [
    # connectors, input end (x = 0), the AUX-0025's set: female XLR (pin 2 +, pin 3 -, pin 1 and
    # shell ground) and a dual-banana pair at 19.05 mm (AP's 3/4 in), plus a common terminal
    ('J4', 'IN XLR', 'XLR_F',   'C368522', 'Neutrik NC3FAAH2, pin 2 = +, pin 3 = -, pin 1 and G = ground', [(1, 'GND'), (2, 'IN_P'), (3, 'IN_N'), ('G', 'GND')]),
    ('J1', 'IN +',  'BANANA_R', 'C6041087', 'Cliff FCR7350R red, amplifier +; with J2 at 19.05 mm for a dual banana plug; pre-order at LCSC, cheaper from Digi-Key', [(1, 'IN_P')]),
    ('J2', 'IN -',  'BANANA_B', 'C6555263', 'Cliff FCR7350B black, amplifier -',         [(1, 'IN_N')]),
    ('J3', 'GND',   'BANANA_G', 'C6041085', 'Cliff FCR7350G green, common / chassis',    [(1, 'GND')]),
    # connectors, output end (x = 158): the AUX-0025's male XLR; the QA403 takes an XLR-to-two-BNC lead
    ('J5', 'OUT XLR', 'XLR_M',  'C368463', 'Neutrik NC3MAAH, pin 2 = +, pin 3 = -, pin 1 and G = ground', [(1, 'GND'), (2, 'OUT_P'), (3, 'OUT_N'), ('G', 'GND')]),
    # the pad switch: a 4PDT ON-ON toggle in the front wall (gold contacts, non-shorting), its
    # wires soldered into W1, ten holes straight below it. Per leg two poles:
    #   pole a, pad feed:  common -> PT,  PAD throw -> F,   DIRECT throw not connected
    #   pole b, output:    common -> OUT, PAD throw -> PAD, DIRECT throw -> F
    # so F has two holes per leg, joined on the board. In DIRECT the pad hangs from nothing.
    ('W1', '4PDT wires', 'WIRES', '', 'solder holes for the pad toggle (APEM 5666CDB or similar, 4PDT ON-ON, gold contacts); not a part',
        [(1, 'OUT_P'), (2, 'F_P'), (3, 'F_P'), (4, 'PT_P'), (5, 'PAD_P'),
         (6, 'OUT_N'), (7, 'F_N'), (8, 'F_N'), (9, 'PT_N'), (10, 'PAD_N')]),
    # mounting holes for M3 stand-offs on the chassis' bottom plate; H5 is plated and bonds the
    # ground plane to the chassis in the connector strip, the others are plain
    ('H1', 'M3', 'HOLE', '', 'plain hole, no pad', []),
    ('H2', 'M3', 'HOLE', '', 'plain hole, no pad', []),
    ('H3', 'M3', 'HOLE', '', 'plain hole, no pad', []),
    ('H4', 'M3', 'HOLE', '', 'plain hole, no pad', []),
    ('H5', 'M3 GND', 'HOLE_GND', '', 'plated, on ground: the chassis bond', [(1, 'GND')]),
    # ground loops for a scope probe's tip-and-barrel or ground spring, between the stages, for
    # measuring the stop band at each stage's output (C3/C7 and C4/C8 pin 1) with a short ground
    ('TP1', 'GND', 'TP_LOOP', '', 'ground test point: solder a wire loop', [(1, 'GND')]),
    ('TP2', 'GND', 'TP_LOOP', '', 'ground test point: solder a wire loop', [(1, 'GND')]),
]

NOT_ASSEMBLED = ('H', 'TP', 'W')     # reference prefixes that are holes and pads, not parts

# Parts JLCPCB leaves out, to be soldered by hand after assembly: the ten film capacitors. They
# are pre-order parts at JLCPCB (19-21 working days), and bought locally they can be measured
# and paired between the legs before they go in.
DO_NOT_PLACE = {ref for ref, *_ in PARTS if ref.startswith('C')}

MPN = {
    'L1': 'Wurth 7447480102', 'L2': 'Wurth 7447480102', 'L3': 'Wurth 7447480102', 'L4': 'Wurth 7447480102',
    'R1': 'UNI-ROYAL MFR03SF1001A10', 'R2': 'UNI-ROYAL MFR03SF1001A10', 'R11': 'UNI-ROYAL MFR03SF1001A10', 'R12': 'UNI-ROYAL MFR03SF1001A10',
    'R4': 'Vishay MRS25000C4120FCT00', 'R14': 'Vishay MRS25000C4120FCT00',
    'R6': 'Vishay MRS25000C3401FCT00', 'R16': 'Vishay MRS25000C3401FCT00',
    'R8': 'TE YR1B10KCC', 'R9': 'TE YR1B10KCC', 'R18': 'TE YR1B10KCC', 'R19': 'TE YR1B10KCC',
    'R10': 'TE YR1B1K0CC', 'R20': 'TE YR1B1K0CC',
    'C1': 'WIMA FKP2J002201D00HSSD', 'C5': 'WIMA FKP2J002201D00HSSD',
    'C2': 'WIMA FKP2J002201D00HSSD', 'C6': 'WIMA FKP2J002201D00HSSD', 'C9': 'WIMA FKP2J002201D00HSSD', 'C10': 'WIMA FKP2J002201D00HSSD',
    'C3': 'WIMA FKP2F014701I00JA00', 'C4': 'WIMA FKP2F014701I00JA00', 'C7': 'WIMA FKP2F014701I00JA00', 'C8': 'WIMA FKP2F014701I00JA00',
    'RV1': 'Bourns 3296W-1-501LF', 'RV2': 'Bourns 3296W-1-501LF',
    'J1': 'Cliff FCR7350R', 'J2': 'Cliff FCR7350B', 'J3': 'Cliff FCR7350G',
    'J4': 'Neutrik NC3FAAH2', 'J5': 'Neutrik NC3MAAH',
}


def source_hash():
    """The first seven hex digits of the SHA-256 of the two files the board is generated from.
    It is printed on the board and written into fab/RELEASE.txt, so a board in the hand, the
    order files and a commit can be matched before the commit exists."""
    here = os.path.dirname(os.path.abspath(__file__))
    h = hashlib.sha256()
    for name in ('design.py', 'make_pcb.py'):
        with open(os.path.join(here, name), 'rb') as f:
            h.update(f.read())
    return h.hexdigest()[:7]


def comment(ref, value):
    """What JLCPCB's BOM calls the part: the manufacturer's number where there is one, else the value."""
    return MPN.get(ref, value)

def nets():
    """net name -> list of (ref, pad)."""
    out = {}
    for ref, _value, _fp, _lcsc, _note, pins in PARTS:
        for pad, net in pins:
            out.setdefault(net, []).append((ref, pad))
    return out

if __name__ == '__main__':
    for ref, value, fp, lcsc, note, pins in PARTS:
        print(f"{ref:4} {value:22} {fp:9} {lcsc:10} {note}")
    print()
    for net, pins in sorted(nets().items()):
        print(f"{net:6} " + ' '.join(f"{r}.{p}" for r, p in pins))
