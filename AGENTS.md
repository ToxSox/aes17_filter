# Notes for coding agents

This file holds what the code does not show. [hardware/README.md](hardware/README.md) describes the
tools and the ordering steps.

## State of the build

- Commit 72c08ab holds the files of the first JLCPCB order, five assembled boards.
- The quantities in `hardware/README.md` assume five toggles and five enclosures. The build differs:
  [docs/shopping-2026-11-03.md](docs/shopping-2026-11-03.md) is the current list.

## Generated files

- `make_pcb.py`, `export.py` and `check_release.py` need KiCad 7 with `pcbnew` and `kicad-cli`. Check
  that they are there before relying on them; the maintainer's Mac has neither.
- Without KiCad, a change to `hardware/fab/` is made by hand, and then:
  - make the same change in the generator, so that the next export gives the same file;
  - keep the CRLF line ends of `aes17-filter-cpl.csv`;
  - update the file's SHA-256 in `fab/RELEASE.txt`.
- Say so when `check_release.py` could not be run.

## JLCPCB placement

JLCPCB places a part by the origin of its own EasyEDA footprint, which need not be the middle of the
part. Before ordering a part that only fits one way, compare its pads with KiCad's and record the
result in `ROTATION_OFFSET` and `JLC_ORIGIN` in `hardware/export.py`. The footprint comes from
`https://easyeda.com/api/products/<C-number>/components?version=6.4.19.5`, in units of 10 mil
(0.254 mm).

## Writing and git

- The repository is public: no personal names in its files, other than the credits for the original
  design.
- Documents are in English. `docs/messanweisung-bauteile.md` is in German, for the people measuring
  the parts. It has an online copy, and the two do not sync: change both.
- Commit and push only when asked.
