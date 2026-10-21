# Audit fixes — from the v1.0.0 verification to VinaMetalic 1.0.0

An independent line-by-line audit of VinaMetal v1.0.0 (commit `96370bc`)
verified **14 software problems** reported by an external audit plus **3
methodological notes** (16+1 findings in total). VinaMetalic 1.0.0 resolves
every finding that belongs to the codebase. This page maps each finding to
its fix and its verification.

| # | Finding (verified against VinaMetal v1.0.0) | Resolution in VinaMetalic 1.0.0 | Where to verify |
|---|---|---|---|
| 1 | `cache::populate()` excluded **every** `el == EL_TYPE_Met` atom from donor-type maps, so unparametrized metals (Na, K, Co, Hg, Cd) lost their standard Vina interaction in the grid path; broke byte-identical equivalence | `is_metal_ion(a)` test (only parametrized ions excluded) + **new regression test with a Na+ receptor** that fails on the old code (-9.108 vs -9.325 kcal/mol) and passes now | `src/lib/cache.cpp` · `tests/test_regression_na_receptor.sh` · `docs/validation/regression_na_receptor.log` |
| 2 | `--metal_cn_strict` was declared, documented and stored but never read by `eval()`/`eval_deriv()` (dead option) | Implemented: strict mode penalizes the CN deviation against the **full ideal CN** instead of the occupancy-reduced target; the CN report line is tagged when active | `src/lib/metal_scoring.cpp` (term b) · `src/main/main.cpp` · `docs/USAGE.md` |
| 3 | Dead variable `dE_dcos` in the geometry-gradient block (computed, never used) | Removed | `src/lib/metal_scoring.cpp` |
| 4 | Banner read "AutoDock Vina v1.0.0" and bug reports pointed to the upstream tracker | Banner reads `VinaMetalic v1.0.0 (fork of AutoDock Vina 1.2.7)`; bug-report URL and citation box point to VinaMetalic | `src/main/main.cpp` · `CMakeLists.txt` |
| 5 | Cu2+/Ni2+ unreachable in practice: Meeko cannot emit those AD types | New helper `scripts/fix_metal_types.py` retypes metal atoms from their element symbol after Meeko preparation; documented in USAGE | `scripts/fix_metal_types.py` · `docs/USAGE.md` |
| 6 | `--metal_oxidation Fe=abc` silently became `0` → default +2 (`std::atoi`) | Strict parsing with `std::stoi`: integers only, plausible range [-4, 8], otherwise error + exit | `src/lib/vina.cpp` (`set_metal_oxidation`) |
| 7 | `index_for_ad_type` fell back to the first matching entry (e.g. Fe4→Fe2+) **silently** | Explicit stderr warning naming the requested state and the entry actually used | `src/lib/metal_parameters.cpp` |
| 8 | `data/AD4Zn.dat` orphan: copy with a wrong header, never referenced by code, confused with the real AD4Zn | Moved to `data/ad4_reference/AD4Zn.dat` and documented as reference-only data (the directional TZ model is not ported) | `docs/USAGE.md` ("Reference data files") · `docs/LIMITATIONS.md` #7 |
| 9 | Scoring weights (1.0, 1.0, 1.0) uncalibrated placeholders | Honest labeling kept; full calibration protocol written down (dataset, grid search, leave-one-out, acceptance criteria) | `docs/CALIBRATION_PLAN.md` · `docs/LIMITATIONS.md` #5 |
| 10 | Fragile occupation detection: depends on receptor donor typing; a mis-typed His/Cys/Asp silently lowers the CN target | Runtime robustness guard: build_cache re-counts all N/O/S atoms within the cutoff and warns when the typed count is smaller | `src/lib/metal_scoring.cpp` (`build_cache`) · `docs/LIMITATIONS.md` #4 |
| 11 | Fragile receptor preparation (strict Meeko, no altloc/repair guidance) | Mitigated via documentation + the retyping helper; the deep fix (PDBFixer/Reduce wrapper or patched Meeko) stays on the roadmap | `docs/USAGE.md` · `docs/AUDIT_FIXES.md` |
| 12 | Binaries not portable (dynamic Boost by default) | `USE_STATIC_BOOST` option, **ON by default**; CI keeps static linking; macOS uses shared Boost | `CMakeLists.txt` |
| 13 | Regression test not registered in CTest (manual-only) | Both regression scripts (no-metal and Na+) are CTest tests behind `VINA_REGRESSION_TEST=ON` + `VINA_127_BIN` | `CMakeLists.txt` · `.github/workflows/build.yml` |
| 14 | CI/releases Linux-only | Linux x64 job **with the Vina 1.2.7 regression** + macOS ARM64 build/test job; packaging stays Linux-only for now | `.github/workflows/build.yml` |
| 15 | RMSD by atom order (methodology of the external benchmark, not the software) | Not applicable to the codebase; validation uses symmetry-aware RMSD | `docs/validation/` |
| 16 | 1 seed / exhaustiveness 8 in the external experiment | Not applicable to the codebase; official examples ship `exhaustiveness 16` | `examples/*/config.txt` |
| 17 | README cited AutoDock4Zn with wrong pages (1931-1941) | Corrected everywhere: **54(8), 2371-2379 (2014)** — README and the startup citation box | `README.md` · `src/main/main.cpp` |

## Verification of this release

All checks were executed on the code in this repository:

- `metal_gradient_test`: analytic-gradient checks pass (3/3, including the
  no-metal negative control).
- CN detection: `Mn2+ CN target = ideal 6 - receptor-bound 4 = 2` (GlfT2,
  PDB 4FIY) and `Zn2+ ... 4 - 3 = 1` (PDB 1s63) reproduced exactly.
- Byte-identical regression **without metals**: identical to upstream
  Vina 1.2.7 (`docs/validation/regression_no_metal.log`).
- Byte-identical regression **with an unparametrized Na+ in the receptor**:
  identical to upstream Vina 1.2.7 with the fix; demonstrably different
  without it (`docs/validation/regression_na_receptor.log`).
