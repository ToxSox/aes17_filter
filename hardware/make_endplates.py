#!/usr/bin/env python3
"""Draws the drilling of the two Hammond 1455N1601 end plates for the filter board and prints
the hole table. Positions come from the board's connector placement in make_pcb.py and the
connectors' axis heights; the plate is drawn as seen from inside the box, looking out, with the
board's top surface as the reference line.

    python3 hardware/aes17-filter/make_endplates.py   -> aes17-filter-endplates.svg / .png
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

PLATE_W, PLATE_H = 103.12, 53.09        # Hammond 1455N1601 end plate
BOARD_W = make_pcb.W                    # 100 mm, centred in the plate
BOARD_TOP = 8.0                         # board top surface above the plate's bottom edge when the board
                                        # sits in the lowest rail (6.4 mm floor-to-slot + 1.6 mm board);
                                        # one rail up adds the rail pitch - measure the box before drilling
CLIFF_AXIS = 6.30                       # Cliff S16N-PC axis above the board (5.5 + 0.8 stand-offs)
XLR_AXIS = 12.5                         # Neutrik A-series horizontal PCB: the flange reaches 12.5 mm below the
                                        # axis and sits on the board, so the axis is about 12.5 mm up. Not a
                                        # dimensioned value on Neutrik's sheet: check against the part before drilling
XLR_HOLE = 22.5                         # Neutrik asks for >= 22 mm
XLR_SCREW = 9.9                         # M3 screw holes on the diagonal, 19.8 mm apart (+-9.9 from the axis)
TOGGLE_HEIGHT = 26.0                    # the toggle's bushing above the board; clears the header below it

# (ref, label, axis height, hole diameter, offset of the axis across the board from the footprint origin)
INPUT = [('J4', 'XLR IN (female)', XLR_AXIS, XLR_HOLE, 0.62), ('J1', '4 mm IN + (red)', CLIFF_AXIS, 11.5, 0.0),
         ('J2', '4 mm IN - (black)', CLIFF_AXIS, 11.5, 0.0), ('J3', '4 mm GND (green)', CLIFF_AXIS, 11.5, 0.0)]
OUTPUT = [('J5', 'XLR OUT (male)', XLR_AXIS, XLR_HOLE, 3.81)]
TOGGLE = ('SW', 'pad toggle (1/4 in bushing)', TOGGLE_HEIGHT, 6.4, 50.0)


def holes(connectors, mirror):
    """(label, x from the plate's left edge seen from inside, y above the plate's bottom edge, diameter)."""
    out = []
    for ref, label, axis, dia, across in connectors:
        y_board = make_pcb.PLACE[ref][1] + across
        x = (PLATE_W - BOARD_W) / 2 + (BOARD_W - y_board if mirror else y_board)
        out.append((label, x, BOARD_TOP + axis, dia))
        if dia == XLR_HOLE:   # the two M3 screw holes of the XLR flange, on the diagonal
            sign = -1 if mirror else 1   # female: upper-right and lower-left seen from the rear; male: mirrored
            out.append((f'{label} screw', x + sign * XLR_SCREW, BOARD_TOP + axis + XLR_SCREW, 3.2))
            out.append((f'{label} screw', x - sign * XLR_SCREW, BOARD_TOP + axis - XLR_SCREW, 3.2))
    return out


def draw(ax, title, hole_list):
    ax.add_patch(Rectangle((0, 0), PLATE_W, PLATE_H, fill=False, lw=1.2))
    ax.axhline(BOARD_TOP, color='0.6', lw=0.8, ls='--')
    ax.text(1.5, BOARD_TOP + 0.8, 'board top surface', fontsize=7, color='0.4')
    for i, (label, x, y, d) in enumerate(hole_list):
        ax.add_patch(Circle((x, y), d / 2, fill=False, lw=1.0))
        ax.plot([x - d / 2 - 1.5, x + d / 2 + 1.5], [y, y], color='0.3', lw=0.5)
        ax.plot([x, x], [y - d / 2 - 1.5, y + d / 2 + 1.5], color='0.3', lw=0.5)
        if d > 4:
            ax.text(x, y + d / 2 + 2.0 + 6.5 * (i % 2), f'{label}\nØ{d:g}  x={x:.1f}  y={y:.1f}', ha='center', fontsize=6.5)
        else:
            ax.text(x + 2.5, y, f'Ø{d:g} ({x:.1f}, {y:.1f})', va='center', fontsize=5.5)
    for x in (4.06, PLATE_W - 4.06):
        for y in (3.81, PLATE_H - 3.81):
            ax.add_patch(Circle((x, y), 2.1, fill=False, lw=0.6, ls=':'))
    ax.set_xlim(-5, PLATE_W + 5); ax.set_ylim(-5, PLATE_H + 16); ax.set_aspect('equal')
    ax.set_title(title, fontsize=9, loc='left'); ax.set_xlabel('mm from the left edge, seen from inside the box'); ax.set_ylabel('mm from the bottom edge')
    ax.tick_params(labelsize=7)


if __name__ == '__main__':
    inp = holes(INPUT, mirror=False)
    outp = holes(OUTPUT, mirror=True) + [(TOGGLE[1], (PLATE_W - BOARD_W) / 2 + BOARD_W - TOGGLE[4], BOARD_TOP + TOGGLE[2], TOGGLE[3])]
    fig, axes = plt.subplots(2, 1, figsize=(8, 9))
    draw(axes[0], 'Input end plate (amplifier side), seen from inside', inp)
    draw(axes[1], 'Output end plate (QA403 side), seen from inside', outp)
    fig.suptitle('Hammond 1455N1601 end plates for the AES17 filter board; the board in the lowest rail '
                 f'(top surface {BOARD_TOP:g} mm up). Corner circles: the plate screws.', fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, 'aes17-filter-endplates.svg'))
    fig.savefig(os.path.join(HERE, 'aes17-filter-endplates.png'), dpi=150)
    print('| Plate | Hole | Ø mm | x from left (inside view) | y above bottom edge |')
    print('|---|---|---|---|---|')
    for name, lst in (('input', inp), ('output', outp)):
        for label, x, y, d in lst:
            print(f'| {name} | {label} | {d:g} | {x:.1f} | {y:.1f} |')
