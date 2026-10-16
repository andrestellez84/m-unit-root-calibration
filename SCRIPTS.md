# Main scripts

An English guide to the scripts that matter for reproducing the paper. The scripts themselves keep their original (Spanish) header comments, because their sha256 is recorded in the manifests and in the provenance of every result file; editing them would break that link. Script names follow the audit in which they were written (`auditNN_*`); `README.md` gives the full table-by-table map with run times.

## Core code

| Script | Role |
|---|---|
| `src/stationarity_test/` | The statistics: GLS detrending, the Bartlett long-run variance with the Andrews bandwidth, MSB-B, null quantiles. |
| `experiments/audit8_unitroot.py` | MSB-GLS, MZt-GLS and DF-GLS with the MAIC of Ng and Perron (`np_statistics`); the comparators. |
| `experiments/audit15_boot_engine.py` | Numba replication of the bootUR 1.0.5 sieve (SB) and sieve wild (SWB) bootstraps, and the AWB, for MZt-GLS. |
| `experiments/audit15_bootur_paso0_v2.R` | Runs bootUR itself on the same series, to check the replication (supplement, Section S2). |
| `experiments/audit10_engine.py` | The calibration of the null law (500 000 paths per sample size). |
| `experiments/download_data.py` | Downloads the price data of the application; `verify_frozen_data.py` checks them against the frozen hashes. |
| `experiments/make_figures_audit13q.py` | Figure 1 of the paper and the figures of the supplement. |
| `experiments/audit18_supplement.py` | Builds the supplement (calls `audit17_supplement.py`, `audit16_supplement.py` and `audit15_supplement.py`). |
| `experiments/*_run_chain.sh` | The order in which the scripts of each audit were run. |

## Tables of the paper

| Table | Generates the tabular (from the included result files) | Produces the result files (simulation) |
|---|---|---|
| Table 1 | `experiments/audit13_tables.py` | `experiments/audit13_e_calib.py` |
| Table 2 | `experiments/audit13_tables.py` | `experiments/audit9_b92_theta.py` |
| Table 3 | `experiments/audit13_q_attrib.py` | `experiments/audit12_bB_attrib.py` |
| Table 4 | `experiments/audit16_v17_tables.py` | `experiments/audit12_bA_ma.py`, `experiments/audit15_b1_boot.py`, `experiments/audit15_b3_fixedb.py` |
| Table 5 | `experiments/audit15_v17_tables.py` | `experiments/audit15_b1_boot.py` |
| Table 6 | `experiments/audit16_v17_tables.py` | `experiments/audit12_bA_ma.py`, `experiments/audit15_b3_fixedb.py` |
| Table B1 | `experiments/audit14_tables.py` | `experiments/audit14_b1_critical.py` |

## Tables of the supplement

All tabulars of the supplement are written by `experiments/audit18_supplement.py`. The result files they read come from:

| Script | Supplement tables |
|---|---|
| `experiments/audit10_b101_theta.py` | S1.1 |
| `experiments/audit10_b103_application.py` | S9.1, S9.2 |
| `experiments/audit10_b103_awb.py` | S4.3 |
| `experiments/audit10_b103_cv.py` | S8.1, S8.2, S8.3, S8.4, S8.5 |
| `experiments/audit10_b103_equalized.py` | S4.1, S4.2 |
| `experiments/audit10_b103_lown.py` | S1.1 |
| `experiments/audit11_t5_claims.py` | S6.5 |
| `experiments/audit12_bA_ma.py` | S2.1, S2.6, S2.7, S2.8 |
| `experiments/audit12_bB_attrib.py` | S2.9 |
| `experiments/audit12_bC_initial.py` | S3.1 |
| `experiments/audit13_e_application.py` | S9.1, S9.2, S9.3, S9.4, S9.5, S9.6 |
| `experiments/audit13_e_awb.py` | S4.3 |
| `experiments/audit13_e_dgp5.py` | S6.1 |
| `experiments/audit13_e_equalized.py` | S1.2, S1.3, S4.1, S4.2 |
| `experiments/audit13_e_size.py` | S1.1 |
| `experiments/audit13_tables.py` | S5.1, S5.2, S5.3, S5.4, S5.5, S5.6, S5.7, S5.8, S5.9, S5.10, S5.11 |
| `experiments/audit14_b1_critical.py` | S8.6 |
| `experiments/audit15_b0_iidasy.py` | S2.2 |
| `experiments/audit15_b0b_lag.py` | S2.3 |
| `experiments/audit15_b1_boot.py` | S2.4 |
| `experiments/audit15_b2_slope.py` | S7.1 |
| `experiments/audit15_b3_fixedb.py` | S2.5 |
| `experiments/audit2_presend_audit2.py` | S7.2 |
| `experiments/audit5b_tarea_r4.py` | S6.3, S6.4 |
| `experiments/audit5b_tarea_r5.py` | S9.2 |
| `experiments/audit8_b2_size.py` | S6.2 |
| `experiments/audit8_b4_local_power.py` | S6.5 |
| `experiments/audit8_b6_application.py` | S9.2 |
| `experiments/audit9_b92_theta.py` | S4.4 |
