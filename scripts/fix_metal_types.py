#!/usr/bin/env python3
"""Retype metal atoms in a receptor PDBQT for VinaMetalic.

Why this exists (audit finding #5)
----------------------------------
Meeko's ``mk_prepare_receptor.py`` does not emit the VinaMetalic AD atom
types for Cu2+ and Ni2+ (nor Co/Cd/Hg), even though VinaMetalic ships
calibrated-or-declared parameters for them (AD_TYPE_Cu=31, AD_TYPE_Ni=32).
A receptor prepared with the documented pipeline therefore leaves those
ions with a generic metal type and VinaMetalic silently falls back to
standard Vina interactions for them.

This script rewrites the AutoDock atom-type field (columns 78-79) of every
metal atom from its element symbol, so a receptor PDBQT produced by Meeko
(or any PDB->PDBQT converter) becomes fully usable by VinaMetalic:

    python3 scripts/fix_metal_types.py receptor.pdbqt -o receptor_fixed.pdbqt

Notes
-----
* VinaMetalic parametrizes: Zn, Mn, Mg, Ca, Fe, Cu, Ni. These are retyped
  to the exact AD type names the parser expects ("Zn", "Mn", "Mg", "Ca",
  "Fe", "Cu", "Ni").
* Na, K, Co, Cd, Hg, U have NO VinaMetalic parameters. They are left
  untouched (generic XS_TYPE_Met_D behavior, identical to upstream Vina)
  and reported so the user knows they will be treated generically.
* The script never modifies coordinates, charges, or non-metal atoms.
"""

import argparse
import sys

# element symbol (uppercase, as found in PDB element / atom-name columns)
# -> AutoDock atom type string expected by VinaMetalic's parser.
PARAMETRIZED = {
    "ZN": "Zn",
    "MN": "Mn",
    "MG": "Mg",
    "CA": "Ca",
    "FE": "Fe",
    "CU": "Cu",
    "NI": "Ni",
}

# Metals recognized but intentionally NOT retyped: VinaMetalic has no
# parameters for them and upstream Vina treats them as generic Met_D.
UNPARAMETRIZED = {"NA", "K", "CO", "CD", "HG", "U"}


def element_of(line):
    """Best-effort metal detection for a PDB/PDBQT atom line.

    Priority: the AutoDock atom-type field (columns 78-79) -- which is where
    PDBQT writers put the element-like type ("Zn", "Cu", "MN"...) -- then the
    PDB element field (columns 77-78, often blank in PDBQT), then the residue
    name of HETATM records (metals are written as single-element residues).

    The atom NAME is deliberately NOT used: standard amino-acid atom names
    collide with metal symbols (CA = alpha carbon, CD = delta carbon,
    HG = gamma hydrogen...).
    """
    t = line[77:79].strip().upper()
    if t in PARAMETRIZED or t in UNPARAMETRIZED:
        return t
    elem = line[76:78].strip().upper()
    if len(elem) == 2 and elem.isalpha() and (elem in PARAMETRIZED or elem in UNPARAMETRIZED):
        return elem
    if line.startswith("HETATM"):
        res = line[17:20].strip().upper()
        if res in PARAMETRIZED or res in UNPARAMETRIZED:
            return res
    return ""


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("pdbqt", help="receptor PDBQT produced by Meeko/OpenBabel/etc.")
    ap.add_argument("-o", "--output", required=True, help="output PDBQT path")
    args = ap.parse_args()

    retyped = {}
    skipped = {}
    out_lines = []

    with open(args.pdbqt, "r", encoding="utf-8", errors="replace") as fh:
        for raw in fh:
            line = raw.rstrip("\n")
            if line.startswith(("ATOM", "HETATM")) and len(line) >= 78:
                elem = element_of(line)
                if elem in PARAMETRIZED:
                    adtype = PARAMETRIZED[elem]
                    current = line[77:79].strip()
                    if current != adtype:
                        # columns 78-79 hold the atom type; keep trailing width
                        line = line[:77] + f"{adtype:<2}" + (line[79:] if len(line) > 79 else "")
                        retyped[elem] = retyped.get(elem, 0) + 1
                elif elem in UNPARAMETRIZED:
                    skipped[elem] = skipped.get(elem, 0) + 1
            out_lines.append(line)

    with open(args.output, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out_lines) + "\n")

    total = sum(retyped.values())
    if total:
        detail = ", ".join(f"{k}x{v}" for k, v in sorted(retyped.items()))
        print(f"fix_metal_types: retyped {total} metal atom(s) -> {detail}")
    else:
        print("fix_metal_types: no retypable metal atoms found (nothing changed)")
    for elem, count in sorted(skipped.items()):
        print(f"fix_metal_types: NOTE {count} {elem} atom(s) kept generic "
              f"(no VinaMetalic parameters; standard Vina treatment applies)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
