# VinaMetalic

**VinaMetalic** is a fork of [AutoDock Vina 1.2.7](https://github.com/ccsb-scripps/AutoDock-Vina)
with **native metal coordination scoring** for metalloenzymes. It guides
ligand poses toward coordination of the catalytic metal ion, detects the
receptor-bound coordination occupancy automatically, and stays
**byte-identical to upstream Vina 1.2.7** when no parametrized metal is
present.

- Author: **Christian Yaranga Nana** — Universidad Norbert Wiener
- GitHub: <https://github.com/cristhianyaranganana-arch/VinaMetalic>
- License: Apache-2.0 (the AutoDock 4 reference parameter files in
  `data/ad4_reference/` are GPL-2, see `COPYING` there)

![CI](https://github.com/cristhianyaranganana-arch/VinaMetalic/actions/workflows/build.yml/badge.svg)
![Platform](https://img.shields.io/badge/platform-Linux%20x64%20%7C%20macOS%20ARM64-blue)
![License](https://img.shields.io/badge/license-Apache--2.0-green)

## Why

A large fraction of drug targets are metalloenzymes — zinc proteases and
HDACs, carbonic anhydrases, Mn²⁺-dependent glycosyltransferases such as the
tuberculosis target GlfT2, HIV integrase (Mg²⁺), influenza endonuclease
(Mn²⁺) — and the pharmacophore of their approved inhibitors is bidentate
coordination of the catalytic ion. Stock Vina types metals as a generic
hydrophobic-ish sphere: nothing rewards approaching the metal at a real
coordination distance, and poses often never touch the ion. VinaMetalic
replaces that behavior with a physically motivated metal model while keeping
everything else identical to Vina 1.2.7.

## What it adds (and what changed after the audit)

Three conditional scoring terms (evaluated only for parametrized ions, with
analytic gradients consumed by Vina's unmodified BFGS search):

1. **Metal–donor 12-6 pair potential** (AutoDock4 combination rules) with the
   minimum at the Harding mean metal–donor distance per donor element.
2. **Coordination-number penalty** on the smooth count of ligand donors in the
   coordination shell, against a target reduced automatically by the receptor
   occupancy (`CN target = ideal − receptor-bound`, printed at startup).
3. **Bounded geometry bonus** for donor–metal–donor angles matching the ideal
   geometry (tetrahedral / octahedral / square-planar).

VinaMetalic ships parameters for **Zn²⁺, Mn²⁺, Mg²⁺, Ca²⁺, Fe, Cu²⁺, Ni²⁺**.

After an independent line-by-line audit of the predecessor codebase (16+1
findings), this release fixes all of them: the grid-path over-exclusion bug
for unparametrized metals (with a new Na⁺ regression test), the previously
dead `--metal_cn_strict` flag (now implemented), strict `--metal_oxidation`
validation, an explicit warning for oxidation-state fallback, a
`fix_metal_types.py` helper that makes Cu²⁺/Ni²⁺ receptors reachable, a
runtime warning for under-detected occupancy, static-Boost-by-default builds,
the regression suite registered in CTest, Linux+macOS CI, and the corrected
AutoDock4Zn citation. See **[docs/AUDIT_FIXES.md](docs/AUDIT_FIXES.md)** for
the complete finding-by-finding mapping.

## Install

### From source

    git clone https://github.com/cristhianyaranganana-arch/VinaMetalic
    cd VinaMetalic
    cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
    cmake --build build --parallel

Boost >= 1.65 (system, thread, serialization, filesystem, program_options) and
CMake >= 3.12 are required. Builds are **statically linked against Boost by
default** for portability; pass `-DUSE_STATIC_BOOST=OFF` on platforms that
only provide shared Boost (e.g. Homebrew/macOS). See
[docs/INSTALL.md](docs/INSTALL.md).

### Run an example

    cd examples/glft2            # GlfT2 (PDB 4FIY) with a catalytic Mn2+
    ../build/vina --config config.txt --out result.pdbqt

The log prints the automatic occupancy adjustment, e.g.:

    VinaMetalic: Mn2+ CN target = ideal 6 - receptor-bound 4 = 2

## Documentation

- [docs/USAGE.md](docs/USAGE.md) — metal options, occupancy detection,
  Cu²⁺/Ni²⁺ preparation, reproducibility checklist
- [docs/INSTALL.md](docs/INSTALL.md) — build details and platforms
- [docs/LIMITATIONS.md](docs/LIMITATIONS.md) — known limitations, each with
  its shipped mitigation and planned fix
- [docs/CALIBRATION_PLAN.md](docs/CALIBRATION_PLAN.md) — protocol to calibrate
  the metal weights before virtual screening
- [docs/AUDIT_FIXES.md](docs/AUDIT_FIXES.md) — the 16+1 audit findings and
  their resolution
- [docs/validation/](docs/validation/) — recorded validation logs
- [CHANGELOG.md](CHANGELOG.md) — release history

## Tests

    ctest --test-dir build --output-on-failure                      # gradients + CN detection
    tests/test_regression_no_metal.sh   build/vina vina_1.2.7       # byte-identical, no metals
    tests/test_regression_na_receptor.sh build/vina vina_1.2.7      # byte-identical with Na+

The two regression tests compare VinaMetalic output **byte-for-byte** with an
upstream AutoDock Vina 1.2.7 binary for receptors that contain no
parametrized metal (the Na⁺ test guards the grid path against silently
zeroing unparametrized-metal interactions). CI runs them automatically.

## When (not) to use it

**Use it** to enforce mechanistic plausibility on metalloenzyme docking:
discard poses that do not coordinate the catalytic metal when coordination is
required for activity, and to explore metal-directed poses that stock Vina
never samples.

**Do not** interpret the affinities as calibrated binding energies: the metal
weights are placeholders until the calibration benchmark
([docs/CALIBRATION_PLAN.md](docs/CALIBRATION_PLAN.md)) is completed, and the
metal reward is bounded by design, so a coordinating pose can score 0.8–1.5
kcal/mol less favorable than a non-coordinating pose under stock Vina. Known
promiscuous chelators (flavonoids, catechols) coordinate most divalent ions
and must be treated as PAINS-style hypothesis generators, not hits.

## Citation

If you use VinaMetalic, please cite (a CITATION.cff is provided; the Zenodo
DOI will be added on the first release deposit):

> C. Yaranga Nana (Universidad Norbert Wiener).
> *VinaMetalic: metal coordination scoring integrated into AutoDock Vina
> v1.0.0* (2026).
> <https://github.com/cristhianyaranganana-arch/VinaMetalic>

and the foundations this work builds upon:

- Santos-Martins, D.; Forli, S.; Ribeiro, A. J. M.; Ramos, M. J.; Olson, A. J.
  *J. Chem. Inf. Model.* **2014**, *54* (8), 2371–2379 (AutoDock4Zn).
- Eberhardt, J.; Santos-Martins, D.; Tillack, A. F.; Forli, S.
  *J. Chem. Inf. Model.* **2021**, *61*, 3891–3898 (AutoDock Vina 1.2.0).
- Trott, O.; Olson, A. J. *J. Comput. Chem.* **2010**, *31*, 455–461 (Vina).
- Harding, M. M. *Acta Crystallogr. D* **2001**, *57*, 401–411
  (metal–ligand geometry).

## Credits & License

VinaMetalic is built on AutoDock Vina and AutoDock 4 (The Scripps Research
Institute); the original copyright notices are retained in the source files.
It descends from **VinaMetal v1.0.0** by the same author; every software
finding of the independent audit of that codebase is fixed in this release
([docs/AUDIT_FIXES.md](docs/AUDIT_FIXES.md)). The example inputs are derived
from PDB entries **4FIY** and **1s63**. Licensed under Apache-2.0; the
AutoDock 4 reference parameter files are GPL-2 (`data/ad4_reference/COPYING`).
