#!/usr/bin/env python3
"""Writes the files JLCPCB asks for from the generated board:

    python3 export.py              # in this directory

  fab/aes17-filter-gerbers.zip   Gerbers for all copper, mask, silk and edge layers plus the
                                 Excellon drill files, in the form JLCPCB's upload expects
  fab/aes17-filter-bom.csv       Comment, Designator, Footprint, LCSC Part # - JLCPCB's BOM columns
  fab/aes17-filter-cpl.csv       Designator, Mid X, Mid Y, Layer, Rotation - JLCPCB's placement columns
  fab/aes17-filter-parts.csv     the same parts with value, note and quantity, for ordering elsewhere
  fab/aes17-filter-drc.txt       the DRC report the board was checked with
  fab/RELEASE.txt                title, revision, the source hash printed on the board, and the
                                 SHA-256 of every file in fab/ - check_release.py verifies it

Run make_pcb.py first; this only reads the .kicad_pcb and design.py.
"""
import csv
import hashlib
import os
import re
import shutil
import unicodedata
import subprocess
import sys
import zipfile

import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import design  # noqa: E402

PCB = os.path.join(HERE, 'aes17-filter.kicad_pcb')
FAB = os.path.join(HERE, 'fab')
os.makedirs(FAB, exist_ok=True)

GERBER_LAYERS = ['F.Cu', 'In1.Cu', 'In2.Cu', 'B.Cu', 'F.Paste', 'B.Paste', 'F.SilkS', 'B.SilkS',
                 'F.Mask', 'B.Mask', 'Edge.Cuts']


def gerbers():
    tmp = os.path.join(FAB, 'gerbers')
    os.makedirs(tmp, exist_ok=True)
    for f in os.listdir(tmp):
        os.remove(os.path.join(tmp, f))
    subprocess.run(['kicad-cli', 'pcb', 'export', 'gerbers', '--layers', ','.join(GERBER_LAYERS),
                    '--no-x2', '--subtract-soldermask', '--use-drill-file-origin', '-o', tmp + '/', PCB],
                   check=True, capture_output=True)
    subprocess.run(['kicad-cli', 'pcb', 'export', 'drill', '--format', 'excellon', '--excellon-units', 'mm',
                    '--excellon-zeros-format', 'decimal', '--generate-map', '--map-format', 'gerberx2',
                    '-o', tmp + '/', PCB], check=True, capture_output=True)
    out = os.path.join(FAB, 'aes17-filter-gerbers.zip')
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
        for f in sorted(os.listdir(tmp)):
            z.write(os.path.join(tmp, f), f)
    return out, sorted(os.listdir(tmp))


def ascii_only(text):
    """JLCPCB's BOM import reads the file as a single-byte encoding and turns every non-ASCII
    character into garbage ("W眉rth"), so the BOM carries plain ASCII only."""
    text = text.replace('Ω', 'R').replace('±', '+-').replace('µ', 'u').replace('×', 'x')
    text = unicodedata.normalize('NFKD', text)
    return ''.join(c for c in text if ord(c) < 128)


# JLCPCB's placement wants the centre of the part and a rotation in its own convention. KiCad's
# footprint origin is pad 1 for axial and radial parts, so the centre is taken from the courtyard
# (the part's outline) instead. Rotation offsets per reference, in degrees, added to KiCad's
# rotation when JLCPCB's preview shows a part turned the wrong way. Set from JLCPCB's 3D preview of
# 1 November 2026: its header and 3296W trimmer models are turned a quarter against KiCad's; its
# NC3FAAH2 model a quarter the other way and its NC3MAAH model a half turn. The headers and the
# trimmers are symmetric in their pins, so a half turn too many still fits the holes; the XLRs
# only fit one way, which the holes enforce whatever this file says.
ROTATION_OFFSET = {'J4': 270, 'J5': 180, 'RV1': 90, 'RV2': 90}


def part_centre(fp):
    """Centre of the footprint's courtyard, or of its pads when it has no courtyard, in mm."""
    try:
        poly = fp.GetCourtyard(pcbnew.F_CrtYd)
        if poly.OutlineCount() > 0:
            bb = poly.BBox()
            return pcbnew.ToMM(bb.Centre().x), pcbnew.ToMM(bb.Centre().y)
    except Exception:
        pass
    xs = [pcbnew.ToMM(p.GetPosition().x) for p in fp.Pads()]
    ys = [pcbnew.ToMM(p.GetPosition().y) for p in fp.Pads()]
    return (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2


def bom_and_cpl():
    board = pcbnew.LoadBoard(PCB)
    fps = {fp.GetReference(): fp for fp in board.GetFootprints()}
    bom_rows = {}
    parts_rows = []
    cpl_rows = []
    for ref, value, fpkey, lcsc, note, pins in design.PARTS:
        if ref.startswith(design.NOT_ASSEMBLED):
            continue
        fp = fps[ref]
        footprint = design.FP[fpkey].split(':')[1]
        place = ref not in design.DO_NOT_PLACE
        parts_rows.append((ref, value, design.comment(ref, value), footprint, lcsc, note, 'yes' if place else 'NO - solder by hand'))
        if not place:
            continue
        key = (design.comment(ref, value), footprint, lcsc)
        bom_rows.setdefault(key, []).append(ref)
        cx, cy = part_centre(fp)
        rot = (fp.GetOrientationDegrees() + ROTATION_OFFSET.get(ref, 0)) % 360
        cpl_rows.append((ref, f"{cx:.3f}", f"{-cy:.3f}", 'Top', f"{rot:.0f}"))
    with open(os.path.join(FAB, 'aes17-filter-bom.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['Comment', 'Designator', 'Footprint', 'LCSC Part #'])
        for (value, footprint, lcsc), refs in bom_rows.items():
            w.writerow([ascii_only(value), ','.join(refs), footprint, lcsc])
    with open(os.path.join(FAB, 'aes17-filter-cpl.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['Designator', 'Mid X', 'Mid Y', 'Layer', 'Rotation'])
        w.writerows(cpl_rows)
    with open(os.path.join(FAB, 'aes17-filter-parts.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['Designator', 'Value', 'Manufacturer part', 'Footprint', 'LCSC Part #', 'Note', 'Placed by JLCPCB'])
        w.writerows(parts_rows)
    return len(bom_rows), len(cpl_rows)


RELEASE_FILES = ('aes17-filter-gerbers.zip', 'aes17-filter-bom.csv', 'aes17-filter-cpl.csv',
                 'aes17-filter-parts.csv', 'aes17-filter-drc.txt', 'aes17-filter-schematic.pdf')


def sha256(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def drc_summary(path):
    txt = open(path).read()
    errors = txt.count('Severity: error')
    m = re.search(r'\*\* Found (\d+) unconnected pads', txt)
    unconnected = int(m.group(1)) if m else -1
    return errors, unconnected


def release():
    """Copies the DRC report into fab/ and writes fab/RELEASE.txt."""
    shutil.copyfile(os.path.join(HERE, 'drc.txt'), os.path.join(FAB, 'aes17-filter-drc.txt'))
    errors, unconnected = drc_summary(os.path.join(FAB, 'aes17-filter-drc.txt'))
    kicad = subprocess.run(['kicad-cli', '--version'], capture_output=True, text=True).stdout.strip()
    lines = [
        f'{design.TITLE} {design.REVISION}, {design.DATE}',
        f'source hash {design.source_hash()} (SHA-256 of hardware/design.py and hardware/make_pcb.py,',
        '  printed on both sides of the board)',
        f'generated with KiCad {kicad}',
        f'DRC: {errors} errors, {unconnected} unconnected pads (aes17-filter-drc.txt)',
        f'board {design.BOARD_LENGTH:g} x {design.BOARD_WIDTH:g} mm, four layers, Hammond 1444-862 chassis',
        '',
        'SHA-256 of the order files (in fab/) and of the board:',
    ]
    for name in RELEASE_FILES + ('../aes17-filter.kicad_pcb',):
        lines.append(f'  {sha256(os.path.join(FAB, name))}  {os.path.normpath(name)}')
    lines += ['', 'Order from a commit whose RELEASE.txt passes `python3 check_release.py`, and name',
              'the commit in the order (a tag or a branch such as release/rev-a).']
    with open(os.path.join(FAB, 'RELEASE.txt'), 'w') as f:
        f.write('\n'.join(lines) + '\n')
    return f'{design.REVISION}, source {design.source_hash()}, DRC {errors} errors'


if __name__ == '__main__':
    out, files = gerbers()
    print('gerbers:', out, len(files), 'files')
    for f in files:
        print('   ', f)
    n_lines, n_parts = bom_and_cpl()
    print(f'bom: {n_lines} lines, cpl: {n_parts} parts')
    print('release:', release())
