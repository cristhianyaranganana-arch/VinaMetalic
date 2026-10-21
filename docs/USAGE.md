# Usage

VinaMetalic accepts the AutoDock Vina command line. This page documents the metal
coordination options and the automatic CN adjustment.

## Basic run

    vina --receptor receptor.pdbqt --ligand ligand.pdbqt \
         --center_x 142.54 --center_y 32.19 --center_z 48.55 \
         --size_x 22 --size_y 22 --size_z 22 \
         --seed 42 --exhaustiveness 16 --num_modes 9 \
         --out results.pdbqt

or with a configuration file (`receptor`, `ligand`, `center_*`, `size_*`,
`seed`, `exhaustiveness`, `num_modes`, `metals`):

    cd examples/glft2
    vina --config config.txt --out results.pdbqt

Paths inside a configuration file are resolved relative to the current working
directory, not the configuration file location.

Metal coordination scoring is enabled by default (`--metals auto`). It is
activated only when the receptor contains a metal ion with built-in parameters.

## Automatic receptor occupancy detection

Before scoring, VinaMetalic inspects the rigid receptor (`grid_atoms`) and counts
the N/O/S atoms typed as coordination donors that lie within the ion's
coordination cutoff. The ligand CN target is then

    CN_target = max(0, CN_ideal - CN_receptor_bound)

The adjustment is computed once per receptor and is therefore thread-safe.
With `-v` (the default), the result is printed before docking:

    VinaMetalic: Mn2+ CN target = ideal 6 - receptor-bound 4 = 2

The penalty compares this target with the smooth count of movable donors in the
coordination shell. A receptor with four protein donors therefore expects two
additional ligand donors, without any per-site configuration.

Coordination cutoffs are ion-specific (for example 3.0 Å for Zn²⁺, 3.1 Å for
Mn²⁺, 3.3 Å for Ca²⁺; see `src/lib/metal_parameters.cpp`).

## Metal options

| Option | Default | Description |
|---|---|---|
| `--metals auto\|off` | `auto` | Enable or disable metal coordination scoring. |
| `--metal_params FILE` | — | JSON file overriding built-in ion parameters (`ideal_cn`, cutoffs, radii, geometry, weights). |
| `--metal_oxidation Fe=3` | — | Declare oxidation states for multi-valent metals. Charges must be integers in [-4, 8]; invalid values abort with an error instead of silently defaulting to +2. |
| `--weight_metal_vdw W` | 1.0 | Weight of the metal 12-6 pair term. |
| `--weight_metal_cn W` | 1.0 | Weight of the CN penalty. |
| `--weight_metal_geom W` | 1.0 | Weight of the geometry bonus. |
| `--metal_cn_strict` | off | Penalize the CN deviation against the full ideal coordination number instead of the receptor-occupancy-reduced target (useful when the ligand should restore a complete shell). The CN report line gains a `[strict: penalizing against ideal CN]` tag when active. |
| `--metal_breakdown` | off | After a `--score_only` or `--local_only` run, print the metal energy breakdown: metal vdW, CN penalty, geometry bonus and the number of donor-metal contacts. |

The weights are placeholders pending benchmark calibration; see
`docs/LIMITATIONS.md`.

### Parameter override example

```json
{
  "Mn2+": {
    "ideal_cn": 6,
    "cn_cutoff": 3.1,
    "geometry": "octahedral"
  }
}
```

Run with `--metal_params override.json`. An overridden `ideal_cn` is still
reduced by the automatic receptor occupancy.

## Preparing receptors with Cu2+ / Ni2+

Meeko's `mk_prepare_receptor.py` does not emit the Cu/Ni AutoDock types, so a
receptor prepared with the standard pipeline leaves those ions with a generic
type and the metal scoring never activates for them. After preparing the
receptor, retype the metal atoms from their element symbol:

    python3 scripts/fix_metal_types.py receptor.pdbqt -o receptor_fixed.pdbqt

The script rewrites only the atom-type column of metal atoms (Zn, Mn, Mg, Ca,
Fe, Cu, Ni), never coordinates or charges, and reports metals without
VinaMetalic parameters (Na, K, Co, Cd, Hg) so they stay generic on purpose.

If the occupancy warning appears (`occupancy is N typed donor(s), but M N/O/S
receptor atom(s) lie within the ... cutoff`), some coordinating atoms are not
typed as donors: fix the receptor typing instead of trusting the CN target.

## Regression tests vs AutoDock Vina 1.2.7

Receptors with **no parametrized metal** (and receptors whose only metals are
unparametrized, e.g. Na+) must produce byte-identical output to upstream
Vina 1.2.7. The CTest suite covers both cases when a reference binary is
provided:

    cmake -S . -B build -DVINA_REGRESSION_TEST=ON -DVINA_127_BIN=/path/to/vina_1.2.7
    cmake --build build && ctest --test-dir build

Equivalently, run the scripts directly:

    tests/test_regression_no_metal.sh  ./vina /path/to/vina_1.2.7
    tests/test_regression_na_receptor.sh ./vina /path/to/vina_1.2.7

Recorded results live in `docs/validation/`.

## Reference data files

- `data/ad4_reference/` — original AutoDock 4 parameter files from the
  AutoDock 4 distribution (GPL-2, see `COPYING` there):
  `AD4_parameters.dat`, `AD4.1_bound.dat`, `AD4_PARM99.dat`.
- `data/ad4_reference/AD4Zn.dat` — the AutoDock4Zn parameter set
  (Santos-Martins et al., *J. Chem. Inf. Model.* 2014,
  DOI 10.1021/ci500209e). It is kept **as reference only**: VinaMetalic ports
  the Zn²⁺ 12-6 vdW terms and the CN/geometry terms, but not yet the full
  directional AD4Zn model (`nbp_r_eps`, TZ pseudoatoms, Zn–H interactions).
  See [LIMITATIONS.md](LIMITATIONS.md) #7.
- `data/metal/metal_parameters_example.json` — starting point for
  `--metal_params` overrides.

## Scoring-only and local-only runs

`--score_only` and `--local_only` use the same receptor preparation and print
the CN target line, so they can be used to check the detected occupancy:

    vina --receptor examples/glft2/receptor.pdbqt \
         --ligand examples/glft2/ligand.pdbqt \
         --center_x 142.54 --center_y 32.19 --center_z 48.55 \
         --size_x 22 --size_y 22 --size_z 22 --score_only

## Interpreting results

- Coordination energy is integrated into the total affinity. After a
  `--score_only` or `--local_only` run, `--metal_breakdown` prints the per-term
  values (metal vdW, CN penalty, geometry bonus, donor-metal contacts);
  library users can obtain the same values from
  `metal_scoring::eval_breakdown`.
- The log line `CN target = ideal X - receptor-bound Y = Z` documents the
  occupancy adjustment for each metal.
- With a receptor containing no parametrized metal (or only unparametrized
  ones such as Na+), VinaMetalic is equivalent to AutoDock Vina 1.2.7; see
  `docs/validation/regression_no_metal.log` and
  `docs/validation/regression_na_receptor.log`.

## Reproducibility checklist

Record the binary version (`vina --version`), the SHA-256 of the binary, the
input PDBQT hashes, the seed, exhaustiveness, box, and the full log. Binaries
built against different Boost versions may explore different trajectories for
the same seed while producing identical energies at a given pose; use
`--local_only` for scoring comparisons.
