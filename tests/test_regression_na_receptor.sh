#!/usr/bin/env bash
# Byte-identical regression: receptor with an UNPARAMETRIZED metal (Na+) vs
# AutoDock Vina 1.2.7.
#
# Guards audit finding #1: cache::populate() used to exclude EVERY receptor
# atom with el == EL_TYPE_Met from the donor-type maps, silently zeroing the
# standard Vina interaction of unparametrized metals (Na, K, Co, Hg, Cd...) in
# the grid path. The correct behavior -- kept byte-identical to upstream
# Vina 1.2.7 -- is to exclude only PARAMETRIZED ions (Zn/Mn/Mg/Ca/Fe/Cu/Ni),
# exactly like non_cache::owns_pair() does on the direct path.
#
# The test receptor is tests/data/1iep_receptor_na.pdbqt: the validated 1iep
# receptor plus one Na+ placed 1.7 A from a ligand donor oxygen, inside the
# docking box, so the Na+-donor interaction is non-negligible and any
# over-exclusion changes the local-optimization trajectory (and the output).
#
# Usage:
#   tests/test_regression_na_receptor.sh /path/to/vina /path/to/vina_original_1.2.7
#
# Both binaries must accept the same CLI. The comparison uses --local_only,
# which exercises scoring and analytic gradients without Monte Carlo randomness.

set -euo pipefail

if [ "$#" -ne 2 ]; then
    echo "usage: $0 <vinametalic-binary> <reference-vina-1.2.7-binary>" >&2
    exit 2
fi

VINA_BIN=$1
REFERENCE_BIN=$2
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
DATA="$HERE/data"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

run() {
    "$1" --receptor "$DATA/1iep_receptor_na.pdbqt" \
         --ligand "$DATA/1iep_ligand.pdbqt" \
         --center_x 15.19 --center_y 53.903 --center_z 16.917 \
         --size_x 20 --size_y 20 --size_z 20 \
         --local_only --seed 42 --out "$2"
}

run "$VINA_BIN" "$TMP/vinametalic.pdbqt" > "$TMP/vinametalic.log" 2>&1
run "$REFERENCE_BIN" "$TMP/reference.pdbqt" > "$TMP/reference.log" 2>&1

echo "VinaMetalic: $(grep -m1 'Estimated Free Energy' "$TMP/vinametalic.log")"
echo "Reference  : $(grep -m1 'Estimated Free Energy' "$TMP/reference.log")"

if cmp -s "$TMP/vinametalic.pdbqt" "$TMP/reference.pdbqt"; then
    echo "RESULT: BYTE_IDENTICAL"
else
    echo "RESULT: DIFFERENT (unparametrized-metal equivalence with Vina 1.2.7 is broken)" >&2
    diff -u "$TMP/reference.pdbqt" "$TMP/vinametalic.pdbqt" | head -40 >&2 || true
    exit 1
fi
