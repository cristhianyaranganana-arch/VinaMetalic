# Validation logs

Raw output of the runs that certify VinaMetalic v1.0.0, produced with the
release binary (`VinaMetalic v1.0.0 (fork of AutoDock Vina 1.2.7)`). Commands,
seeds and box sizes are recorded inside each log.

| File | System | Result |
|---|---|---|
| `glft2_cnfix.log` | GlfT2, PDB 4FIY chain A, Mn²⁺ | CN target 2 (4 receptor donors, `--score_only`); energy components recorded. |
| `1s63_cnfix.log` | PDB 1s63, Zn²⁺ | CN target 1 (3 receptor donors); top-1 re-docking pose in the examples matches the crystal pose. |
| `regression_no_metal.log` | 1iep, no metal | `--local_only` output **byte-identical** to AutoDock Vina 1.2.7. |
| `regression_na_receptor.log` | 1iep + one Na⁺ (unparametrized metal) | `--local_only` output **byte-identical** to AutoDock Vina 1.2.7. On the pre-fix code this test failed (-9.108 vs -9.325 kcal/mol, different pose) — see `docs/AUDIT_FIXES.md` #1. |
| `vinametalic_v1.0.0_comparative_validation.pdf` | Four-system benchmark (1iep; 1iep + Na⁺; 1s63 Zn²⁺; 4FIY Mn²⁺) | Formal comparative validation report vs AutoDock Vina 1.2.7: byte-identical reproducibility on P1/P2, coordination scoring characterized on P3/P4, binary SHA-256 provenance and reproduction commands. Also attached to Release v1.0.0. |

## Notes

- The 1s63 log shows the runtime occupancy warning (`occupancy is 3 typed
  donor(s), but 4 N/O/S receptor atom(s) lie within the 3 A cutoff`): one
  N/O/S atom near the Zn²⁺ is not typed as a coordination donor. The CN
  target (4 − 3 = 1) matches the crystallographic occupancy and the
  repository's integration test; the warning documents the typing nuance
  instead of hiding it (audit finding #10 mitigation).
- RMSD values quoted in the examples (0.95 Å GlfT2 mode 3, 0.33 Å 1s63 top-1)
  are heavy-atom, symmetry-aware, computed with RDKit `GetBestRMS` against
  the crystal ligand; they are not printed by Vina.
- The regression tests require an upstream AutoDock Vina 1.2.7 binary;
  CI downloads `vina_1.2.7_linux_x86_64` from the Scripps release page and
  runs both via CTest (`-DVINA_REGRESSION_TEST=ON`).
