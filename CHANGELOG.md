# Changelog

All notable changes to VinaMetalic are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-10-21

First release of **VinaMetalic**, fork of AutoDock Vina 1.2.7 with native
metal coordination scoring. The codebase descends from VinaMetal v1.0.0
(commit `96370bc`); every software finding of the independent audit of that
codebase (16+1 findings, all verified against the source) is fixed here. With
no parametrized metal in the receptor — including receptors that contain only
unparametrized metals such as Na⁺ — scoring and output remain byte-identical
to AutoDock Vina 1.2.7.

### Added

- `scripts/fix_metal_types.py`: retypes metal atoms (Zn, Mn, Mg, Ca, Fe, Cu,
  Ni) in a receptor PDBQT from their element symbol, making Cu²⁺/Ni²⁺
  receptors reachable despite Meeko not emitting those AD types (#5).
- Byte-identical regression test **with an unparametrized Na⁺ in the
  receptor** (`tests/test_regression_na_receptor.sh` + test data): guards the
  grid path against over-excluding metals; it fails on the pre-fix code
  (-9.108 vs -9.325 kcal/mol vs upstream) and passes now (#1).
- Runtime robustness guard for occupation detection: `build_cache` re-counts
  every N/O/S receptor atom within the coordination cutoff and warns when the
  typed-donor count is smaller, exposing under-detected occupancy (#10).
- Explicit stderr warning in `index_for_ad_type` when a declared oxidation
  state has no calibrated entry and the code falls back to another one (#7).
- `docs/CALIBRATION_PLAN.md`: full protocol (dataset, grid search,
  leave-one-out, acceptance criteria) to calibrate the metal weights (#9).
- `docs/AUDIT_FIXES.md`: finding-by-finding mapping of the audit and its
  resolution.
- CTest registration of both byte-identical regression tests behind
  `-DVINA_REGRESSION_TEST=ON -DVINA_127_BIN=<path>` (#13).
- macOS ARM64 build/test CI job in addition to Linux x64 (#14).
- `--metal_breakdown` CLI flag (exposes `metal_scoring::eval_breakdown`,
  previously C++-API-only) and `metal_breakdown()` accessor.

### Changed

- Banner reads `VinaMetalic v1.0.0 (fork of AutoDock Vina 1.2.7)`; the
  bug-report URL and the startup citation box point to VinaMetalic (#4).
- Source builds link Boost **statically by default**
  (`-DUSE_STATIC_BOOST=OFF` to disable) for portable binaries (#12).
- `--metal_cn_strict` is now implemented: it penalizes the CN deviation
  against the full ideal coordination number instead of the
  receptor-occupancy-reduced target; the CN report line is tagged when
  active (#2).
- `--metal_oxidation` charges are validated strictly: integers in [-4, 8]
  via `std::stoi`; anything else aborts with an error instead of silently
  becoming the default +2 state (#6).

### Fixed

- Grid path over-exclusion: `cache::populate()` excluded every atom with
  `el == EL_TYPE_Met` from donor-type maps, silently zeroing the standard
  Vina interaction of unparametrized metals (Na, K, Co, Hg, Cd) in map-based
  scoring; it now excludes only parametrized ions (`is_metal_ion`), matching
  the direct path and upstream Vina 1.2.7 (#1).
- Removed the dead `dE_dcos` variable in the geometry gradient block (#3).
- Removed the dangling reference to `MAPA_DE_PORTERIA.md`; the AD4 donor set
  is referenced to `data/ad4_reference/` and the AutoDock4Zn publication.
- `data/AD4Zn.dat` moved to `data/ad4_reference/AD4Zn.dat` and documented as
  reference-only (the directional TZ model is not ported) (#8).
- Corrected the AutoDock4Zn citation everywhere: *J. Chem. Inf. Model.*
  **2014**, *54* (8), **2371–2379** (was 1931–1941) (#17).
- Documented the atom-level occupancy convention as an explicit design
  decision (bidentate carboxylate = two donors) and the CTest coverage of the
  regression suite (#10, #13).
