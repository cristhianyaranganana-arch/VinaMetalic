# Calibration plan for the VinaMetalic metal scoring weights

The metal terms ship with placeholder weights (1.0, 1.0, 1.0). Until the
benchmark below is completed, **do not use VinaMetalic for virtual screening
or affinity ranking**; use it as a mechanistic filter (does this ligand
coordinate the catalytic metal?) and always confirm poses visually.

This plan resolves audit finding #9 (uncalibrated weights) and doubles as the
expanded-validation study requested by LIMITATIONS #10.

## 1. Dataset

Select **>= 10 metalloproteins** covering the parametrized ions and both
geometries:

| Ion | Candidate systems (PDB) | Geometry |
|---|---|---|
| Zn2+ | 1s63 (already validated), hCA II (2CBA), MMP-8 (1MMR), HDAC8 (1T69), thermolysin (5TLN) | tetrahedral |
| Mn2+ | GlfT2 (4FIY, already validated), integrase-IN (example), arginase (2AEB), oxalate decarboxylase | octahedral |
| Mg2+ | HIV-1 integrase core (1BL3), RNase H (1ZBL), DNA polymerase fragments | octahedral |
| Ca2+ | trypsin-like example, concanavalin A | variable |
| Fe | n/a (justify exclusion or use heme-free non-heme iron, e.g. 1VJ2) | — |
| Cu2+/Ni2+ | only after their parameters are validated; keep out of the first calibration round | — |

Inclusion criteria per complex:

1. High-resolution crystal structure (<= 2.0 A preferred) with the metal and a
   **crystallographic ligand that directly coordinates the metal**.
2. Metal correctly typed in the PDBQT (check the `VinaMetalic:` CN log line
   and the occupancy warning).
3. No required cofactor films/waters removed arbitrarily: keep the waters the
   crystal coordinates as donors if they are within the cutoff.

## 2. Protocol

For every complex:

1. Prepare receptor and ligand (Meeko; run `scripts/fix_metal_types.py` when
   Cu/Ni are involved). Verify the CN target log line against the
   crystallographic coordination count.
2. **Re-dock** the crystallographic ligand:
   `--seed 42 --exhaustiveness 16 --num_modes 20` (and 3 extra seeds for the
   final weights), box around the metal site.
3. Record: top-1 RMSD (symmetry-aware, e.g. RDKit `GetBestRMS`), best pose
   coordinating distance d(M–donor), CN penalty at pose 1, total affinity.
4. Repeat for a weight grid:
   `w_vdw, w_cn, w_geom ∈ {0.25, 0.5, 1.0, 2.0, 4.0}` (125 combos) using
   `--weight_metal_*`.
5. Optionally re-rank with MM/GBSA or a short MD relaxation to decouple
   "poses that coordinate" from "affinities".

## 3. Objective and acceptance criteria

Primary objective: minimize top-1 pose RMSD against the crystal
coordinates. Secondary: rank the crystallographic pose within the top-3.

A weight set is accepted when, on leave-one-protein-out cross-validation:

- median top-1 RMSD improves vs both baseline Vina 1.2.7 and (1,1,1);
- >= 70 % of complexes reproduce a coordinating pose within 0.5 A of the
  crystallographic M–donor distance;
- no system shows a CN-penalty runaway (|penalty| > 10 kcal/mol at the best
  pose).

## 4. Deliverables

- `data/metal/metal_parameters_calibrated.json` (default weights via
  `--metal_params`, and, once frozen, new compiled-in defaults in
  `src/main/main.cpp`).
- The benchmark scripts and per-complex logs published under
  `docs/validation/calibration/`.
- A CHANGELOG entry and a version bump (minor release: weights change the
  scoring function).

## 5. Known confounders to control

- **PAINS/promiscuous chelators**: flavonoids and catechols coordinate most
  2+ metals; exclude them from the calibration set.
- **Donor typing**: run the occupancy warning check on every receptor before
  trusting CN targets.
- **Bridging ligands** (LIMITATIONS #8): exclude bridging complexes from the
  first round; they are double-penalized by independent CN terms.
