#!/usr/bin/env python3
"""Checks that the files in fab/ belong together before they are ordered:

    python3 hardware/check_release.py        # exit code 0 = fit to order

  - every part in design.py is on the board, and nothing else is
  - the BOM and the placement file list exactly the parts JLCPCB is to fit
  - the source hash printed on the board is that of the current design.py and make_pcb.py,
    and RELEASE.txt names the same one
  - every file listed in RELEASE.txt still has the SHA-256 written there
  - the DRC report has no errors and no unconnected pads
  - the schematic was drawn from the current design.py (its hash and the positive leg's values)
  - the pad is switched: its top is not on the filter output, so DIRECT sees the analyzer alone
  - the READMEs give the board size and the chassis the generator uses

Run make_pcb.py and export.py first; this only reads.
"""
import csv
import hashlib
import os
import re
import sys

import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import design  # noqa: E402

FAB = os.path.join(HERE, 'fab')
problems = []


def check(ok, what):
    print(('ok    ' if ok else 'FAIL  ') + what)
    if not ok:
        problems.append(what)


board = pcbnew.LoadBoard(os.path.join(HERE, 'aes17-filter.kicad_pcb'))
on_board = {fp.GetReference() for fp in board.GetFootprints()}
in_design = {ref for ref, *_ in design.PARTS}
check(on_board == in_design, f'board and design.py have the same {len(in_design)} parts'
      + ('' if on_board == in_design else f': only on the board {sorted(on_board - in_design)},'
         f' only in design.py {sorted(in_design - on_board)}'))

fitted = {ref for ref in in_design if not ref.startswith(design.NOT_ASSEMBLED) and ref not in design.DO_NOT_PLACE}
with open(os.path.join(FAB, 'aes17-filter-bom.csv')) as f:
    in_bom = {r.strip() for row in csv.DictReader(f) for r in row['Designator'].split(',')}
with open(os.path.join(FAB, 'aes17-filter-cpl.csv')) as f:
    in_cpl = {row['Designator'] for row in csv.DictReader(f)}
check(in_bom == fitted, f'the BOM lists the {len(fitted)} parts to fit'
      + ('' if in_bom == fitted else f': extra {sorted(in_bom - fitted)}, missing {sorted(fitted - in_bom)}'))
check(in_cpl == fitted, 'the placement file lists the same parts'
      + ('' if in_cpl == fitted else f': extra {sorted(in_cpl - fitted)}, missing {sorted(fitted - in_cpl)}'))

src = design.source_hash()
texts = [d.GetText() for d in board.GetDrawings() if isinstance(d, pcbnew.PCB_TEXT)]
check(sum(f'src {src}' in t for t in texts) >= 2, f'source hash {src} is printed on both sides of the board')
release = open(os.path.join(FAB, 'RELEASE.txt')).read()
check(f'source hash {src}' in release, 'RELEASE.txt names the same source hash')
check(f'{design.TITLE} {design.REVISION}' in release, f'RELEASE.txt names {design.TITLE} {design.REVISION}')

for digest, name in re.findall(r'^  ([0-9a-f]{64})  (\S+)$', release, re.M):
    with open(os.path.normpath(os.path.join(FAB, name)), 'rb') as f:
        check(hashlib.sha256(f.read()).hexdigest() == digest, f'{name} is the file RELEASE.txt was written for')

drc = open(os.path.join(FAB, 'aes17-filter-drc.txt')).read()
m = re.search(r'\*\* Found (\d+) unconnected pads', drc)
check(drc.count('Severity: error') == 0 and m is not None and m.group(1) == '0',
      'the DRC report has no errors and no unconnected pads')

svg = open(os.path.join(HERE, 'aes17-filter-schematic.svg')).read()
texts_svg = ' '.join(re.findall(r'<!-- (.*?) -->', svg))
with open(os.path.join(HERE, 'design.py'), 'rb') as f:
    dhash = hashlib.sha256(f.read()).hexdigest()[:7]
values = {ref: value for ref, value, *_ in design.PARTS}
missing = [ref for ref in design.NAMES_P.values() if ref not in texts_svg or values[ref] not in texts_svg]
check(f'sha256 {dhash}' in texts_svg and not missing,
      f'the schematic was drawn from this design.py ({dhash})'
      + ('' if not missing else f': missing or stale {missing}') + ' - run make_schematic.py')

nets = design.nets()
pad_tops = [(ref, pad) for ref, pad in nets.get('PT_P', []) + nets.get('PT_N', []) if ref.startswith('R')]
on_f = {(ref, pad) for ref, pad in nets.get('F_P', []) + nets.get('F_N', [])}
check(len(pad_tops) == 2 and not on_f & set(pad_tops),
      'the pad tops (PT) are separate nets from the filter outputs (F): the toggle takes the pad off in DIRECT')

size = f'{design.BOARD_LENGTH:g} × {design.BOARD_WIDTH:g} mm'
for doc in ('../README.md', 'README.md'):
    path = os.path.normpath(os.path.join(HERE, doc))
    if os.path.exists(path):
        txt = open(path).read()
        check(size in txt and '1444-862' in txt, f'{os.path.relpath(path, os.path.join(HERE, ".."))} gives {size} and the 1444-862')

print()
print('fit to order' if not problems else f'{len(problems)} problem(s): do not order this state')
sys.exit(1 if problems else 0)
