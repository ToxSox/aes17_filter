#!/usr/bin/env python3
"""Draws the drilling of the front long wall of the Hammond 1444-862 chassis for the filter
board and prints the hole table. Positions come from the connector placement in make_pcb.py
and the connectors' axis heights; the wall is drawn as seen from the front, from outside, which
is how it is drilled and how it faces the operator.

    python3 hardware/make_frontwall.py   -> aes17-filter-frontwall.svg / .png
"""
import os
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_pcb  # noqa: E402

# Hammond 1444-862: 203.2 x 152.4 x 50.8 mm outside, 1.02 mm aluminium, open at the bottom and
# closed by the 1434-86 bottom plate. The long walls are 203.2 x 50.8 mm; the board is centred
# along the wall and stands on spacers on the bottom plate.
WALL_LENGTH, WALL_HEIGHT = 203.2, 50.8
BOARD_X0 = (WALL_LENGTH - make_pcb.L) / 2       # the board's x = 0, from the wall's left end seen from outside
SPACER = 10.0                                   # M3 spacers between bottom plate and board
BOARD_TOP = SPACER + 1.6                        # board top surface above the wall's bottom edge (= the bottom plate)

XLR_AXIS = 12.5     # Neutrik A-series horizontal PCB connectors: axis about 12.5 mm above the board, read
                    # off Neutrik's front view (the flange reaches 12.5 below the axis), not a dimensioned
                    # value - hold a connector against the board before drilling
CLIFF_AXIS = 6.3    # Cliff S16N-PC: 5.5 mm axis height on 0.8 mm stand-offs
XLR_HOLE, XLR_SCREW, XLR_SCREW_D = 22.5, 9.9, 3.2   # Neutrik: hole >= 22 mm, two M3 holes 19.8 mm apart on a diagonal
CLIFF_HOLE = 11.5   # clears the socket's 11.0 mm barrel; Cliff does not specify a panel hole
TOGGLE_HOLE = 6.4   # 1/4 in bushing
TOGGLE_AXIS = 24.0  # the toggle sits high, straight above K1's footprint (8.4 mm relay), so that its
                    # body (about 13 x 8 mm, 13-18 mm deep with the lugs) clears whatever is fitted
                    # there and its six wires drop about 15 mm into K1's contact holes

HOLES = [
    # label, x along the board, axis above the board, hole diameter, XLR screws?
    ('XLR IN (female)', make_pcb.AX_XLR_IN, XLR_AXIS, XLR_HOLE, True),
    ('4 mm IN + (red)', make_pcb.AX_RED, CLIFF_AXIS, CLIFF_HOLE, False),
    ('4 mm IN - (black)', make_pcb.AX_BLACK, CLIFF_AXIS, CLIFF_HOLE, False),
    ('4 mm GND (green)', make_pcb.AX_GREEN, CLIFF_AXIS, CLIFF_HOLE, False),
    ('XLR OUT (male)', make_pcb.AX_XLR_OUT, XLR_AXIS, XLR_HOLE, True),
    ('pad toggle', make_pcb.AX_TOGGLE, TOGGLE_AXIS, TOGGLE_HOLE, False),
]

# What belongs on the panel next to the holes (engraved, printed or a label strip): x along the
# board, height above the wall's bottom edge, text. The rating is per leg, to ground.
LEGEND = [
    (make_pcb.AX_XLR_IN, 5.0, 'IN  2+ 3-'),
    (make_pcb.AX_RED, 5.0, 'IN +'), (make_pcb.AX_BLACK, 5.0, 'IN -'), (make_pcb.AX_GREEN, 5.0, 'GND'),
    ((make_pcb.AX_RED + make_pcb.AX_GREEN) / 2, 45.0,
     'max per leg: 85 Vrms to 12 kHz, 53 Vrms at 20 kHz, 35 Vrms 30-100 kHz'),
    ((make_pcb.AX_RED + make_pcb.AX_GREEN) / 2, 41.0, 'GND to the amplifier ground; IN - is not ground'),
    (make_pcb.AX_XLR_OUT, 5.0, 'OUT  2+ 3-'),
    (make_pcb.AX_TOGGLE, 45.0, 'PAD 1:21.8  /  DIRECT'),
    (make_pcb.AX_TOGGLE, 25.0, 'DIRECT: max 40 Vrms\ninto the QA403;\nswitch muted only'),
]


def holes():
    """(label, x from the wall's left end seen from outside, y above the bottom edge, diameter)."""
    out = []
    for label, x_board, axis, dia, screws in HOLES:
        x = BOARD_X0 + x_board
        y = BOARD_TOP + axis
        out.append((label, x, y, dia))
        if screws:
            # Neutrik draws the screw holes upper right and lower left seen from behind the panel,
            # so from the front they are upper left and lower right
            out.append((f'{label} screw', x - XLR_SCREW, y + XLR_SCREW, XLR_SCREW_D))
            out.append((f'{label} screw', x + XLR_SCREW, y - XLR_SCREW, XLR_SCREW_D))
    return out


def draw(hole_list):
    fig, ax = plt.subplots(figsize=(11, 4.2))
    ax.add_patch(Rectangle((0, 0), WALL_LENGTH, WALL_HEIGHT, fill=False, lw=1.2))
    ax.axhline(BOARD_TOP, color='0.6', lw=0.8, ls='--')
    ax.text(1.5, BOARD_TOP - 3.0, f'board top surface ({BOARD_TOP:g} mm, on {SPACER:g} mm spacers)', fontsize=7, color='0.4')
    ax.plot([BOARD_X0, BOARD_X0 + make_pcb.L], [BOARD_TOP - 1.6, BOARD_TOP - 1.6], color='0.75', lw=3)
    big = [h for h in hole_list if h[3] > 4]
    for i, (label, x, y, d) in enumerate(hole_list):
        ax.add_patch(Circle((x, y), d / 2, fill=False, lw=1.0))
        ax.plot([x - d / 2 - 1.5, x + d / 2 + 1.5], [y, y], color='0.3', lw=0.5)
        ax.plot([x, x], [y - d / 2 - 1.5, y + d / 2 + 1.5], color='0.3', lw=0.5)
        if d > 4:
            j = big.index((label, x, y, d))
            ax.text(x, WALL_HEIGHT + 2.0 + 6.0 * (j % 2), f'{label}\nØ{d:g}  x={x:.1f}  y={y:.1f}', ha='center', fontsize=6.5)
        else:
            ax.text(x + 2.4, y, f'Ø{d:g} ({x:.1f}, {y:.1f})', va='center', fontsize=5.5)
    for x_board, y, text in LEGEND:
        ax.text(BOARD_X0 + x_board, y, text, ha='center', va='center', fontsize=6, color='tab:blue')
    ax.set_xlim(-5, WALL_LENGTH + 5)
    ax.set_ylim(-5, WALL_HEIGHT + 16)
    ax.set_aspect('equal')
    ax.set_title('Hammond 1444-862, front long wall, seen from outside: x from the left end, y from the bottom edge (mm)',
                 fontsize=8, loc='left')
    ax.tick_params(labelsize=7)
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, 'aes17-filter-frontwall.svg'))
    fig.savefig(os.path.join(HERE, 'aes17-filter-frontwall.png'), dpi=150)


if __name__ == '__main__':
    lst = holes()
    draw(lst)
    print('| Hole | Ø mm | x from the left end, seen from outside | y above the bottom edge |')
    print('|---|---|---|---|')
    for label, x, y, d in lst:
        print(f'| {label} | {d:g} | {x:.1f} | {y:.1f} |')
    print()
    print('Panel legend (blue in the drawing):')
    for x_board, y, text in LEGEND:
        print(f'  at x = {BOARD_X0 + x_board:.1f}, y = {y:g}: ' + text.replace(chr(10), ' '))
