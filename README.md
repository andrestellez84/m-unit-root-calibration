# Replication package: Calibrating M-type unit-root tests in finite samples: exact tables, the sieve bootstrap and a kernel long-run variance

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23424031.svg)](https://doi.org/10.5281/zenodo.23424031)

Andrés Felipe Téllez Crespo (ORCID [0009-0004-7680-6585](https://orcid.org/0009-0004-7680-6585)), Independent Researcher, Mexico City. License: see *License*.

**How to cite.** Téllez Crespo, A. F. (2026). *Calibrating M-type unit-root tests in finite samples: exact tables, the sieve bootstrap and a kernel long-run variance* — replication package (version 1.0.0). Zenodo. https://doi.org/10.5281/zenodo.23424031 (machine-readable metadata in `CITATION.cff`).
**Repository.** https://github.com/andrestellez84/m-unit-root-calibration (release v1.0.0, identical to the Zenodo record).

This package contains the code, protocols, result files and supplementary material needed to reproduce every table of the paper (Tables 1-6 and B1) and of its supplement (Tables S1.1-S9.6). It does not contain the price data of the application (see *Application data*), simulation checkpoints, or files that contain local user paths (see *What is not included*).

## Contents

| Path | What it is |
|---|---|
| `src/stationarity_test/` | Python package with the statistics (installed with `pip install -e .`, see `pyproject.toml`) |
| `tests/` | Test suite (`python -m pytest tests`) |
| `experiments/*.py`, `*.R`, `*.sh` | Simulation, analysis and table scripts, one file per block of each audit (`auditNN_*`); the `*_run_chain.sh` files give the order in which each audit was run |
| `experiments/protocol*.md`, `prediccion*.md`, `enmienda*.md` | Protocols, amendments and predictions, committed before each computation |
| `experiments/results/*.json` | Result files; each records its generating script, its sha256 and the commit in `provenance` |
| `experiments/results/manifest_audit*.json` | Per-audit manifests: sha256, bytes, script and commit of every result file |
| `experiments/results/MANIFEST_audit5*.sha256` | Earlier `sha256sum` manifests of the pre-registered files (paths relative to the package root) |
| `experiments/results/resultados_auditoria_*.md` | Internal reports of the verification rounds, in Spanish; they are kept because the manifests or a script cite them (the others are not included) |
| `experiments/results/tables_audit1[3-6]/` | The LaTeX tabulars of the paper and their notes, generated from the JSON files |
| `supplementary/` | The supplement: `supplement.tex`, its tables, data, protocols, `README.md` and `MANIFEST.sha256` |
| `experiments/download_data.py`, `experiments/data/data_registry_frozen.json`, `verify_frozen_data.py` | Application data: download and verification |
| `environment.yml`, `ENVIRONMENT.txt` | Software environment (Python, R, bootUR) |
| `MANIFEST.sha256` | sha256 of every file in this package |
| `PROTOCOLS.md`, `SCRIPTS.md` | English guides to the protocol documents and to the main scripts |
| `LICENSE`, `LICENSE-CC-BY-4.0.md`, `CITATION.cff` | Licenses (MIT for the code, CC BY 4.0 for the rest) and citation metadata |

## Environment

Python 3.11.0 with the pinned packages of `environment.yml` (`conda env create -f environment.yml`), R 4.6.1 with bootUR 1.0.5 for the bootUR comparisons. `ENVIRONMENT.txt` lists every version. All timings below were recorded on a Windows 11 workstation using 14-16 cores.

Run the tests after installing: `python -m pytest tests` (369 tests; 15–35 minutes on a first run, which compiles the numba functions, and about 12 minutes once the numba cache exists).

## Application data

The four price files (daily closes, not adjusted) are not distributed. `experiments/download_data.py` downloads them from Yahoo Finance (`yfinance`) into `experiments/data/` and rewrites `experiments/data/data_registry.json` with the hashes of what it downloaded. The hashes of the frozen files used in the paper are kept in `experiments/data/data_registry_frozen.json`:

| Index | Ticker | First date | Last date | Rows | sha256 of the frozen file |
|---|---|---|---|---|---|
| SP500 | `^GSPC` | 1984-01-03 | 2024-12-30 | 10332 | `fdeba3f639c2e0203e4afcd356637c323e2e2426079813dc0d0d54f12635f9bf` |
| FTSE | `^FTSE` | 1984-01-03 | 2024-12-30 | 10355 | `4fe5809f2657fce33dd9d71a2e82c83b2be49bfbcf3159c8a74f48c01a5cc6d0` |
| NIKKEI | `^N225` | 1984-01-04 | 2024-12-30 | 10079 | `e7f0138e4a369903c7952a707280c11b8497c5a06ae23de51bb93389a98dbfff` |
| DAX | `^GDAXI` | 1987-12-30 | 2024-12-30 | 9356 | `d877566e3c82361a703a34cde9202f8e6210989e34b504c958d1d9039167af38` |

To verify a download: `python experiments/download_data.py` and then `python verify_frozen_data.py`, which compares the sha256, row count and date range of each file with the frozen record and exits with code 1 on any mismatch. Yahoo Finance revises past data occasionally, so a fresh download may not match; the application results (`e_application_audit13.json`) correspond to the frozen files only.

## Reproducing the tables

Every table exists at two levels. **(A)** The tabular is generated from result files that are included here; this takes seconds and needs no simulation. **(B)** The result file is generated by a simulation script; some of these read calibration samples or paths stored as checkpoints, which are not included and must be regenerated first, in the order of the `*_run_chain.sh` files (`audit9_run_chain.sh`, `audit10_run_chain.sh`, `audit12_run_chain.sh`, `audit13_run_chain.sh`, `audit14_run_chain.sh`, `audit15_run_final.sh`). Seeds are fixed in each script (`SeedSequence(family, spawn_key=...)`), so a rerun reproduces the stored files. Times are wall-clock times; the source of each is given.

### Main text

| Table | Content | (A) Generator, from included JSON | Result file(s) | (B) Script that produces the result file | Time of (B) | Upstream inputs (checkpoints, not included) |
|---|---|---|---|---|---|---|
| Table 1 | Size with limiting and finite-sample critical values | `python experiments/audit13_tables.py` → `experiments/results/tables_audit13/tab_calib_audit13.tex` | `e_calib_audit13.json` | `experiments/audit13_e_calib.py` | ~ 14 s (`elapsed_analysis_sec` field of the JSON (analysis step only)) | experiments/audit9_calibrate.py (A9 calibration, N_cal = 5e4, n = 2000, 5000); experiments/audit10_b101_theta.py (A10 calibration, N_cal = 5e5, n <= 1000), ~ 36 min; experiments/audit9_b92_theta.py (independent paths, family 102), ~ 2.2 h; experiments/audit9_b94_finite_sample.py (n = 20 000 paths, family 104), ~ 3.5 h |
| Table 2 | Local asymptotic power, n = 2000 | `python experiments/audit13_tables.py` → `experiments/results/tables_audit13/tab_localpower_audit13.tex` | `b92_theta_audit9.json` | `experiments/audit9_b92_theta.py` | ~ 2.2 h (projection recorded before the run, logs_audit9/b92_run_audit9.log) | experiments/audit9_calibrate.py (calibration at n = 2000) |
| Table 3 | Decomposition of the power difference between MSB-B and MSB-GLS | `python experiments/audit13_q_attrib.py` → `experiments/results/tables_audit13/tab_attrib_audit13.tex` | `bB_attrib_audit12.json` | `experiments/audit12_bB_attrib.py` | ~ 2 min (sum of batch times, logs_audit12/bB_audit12.log) | experiments/audit9_b91_equalized.py and experiments/audit9_b92_theta.py (paths), ~ 79 min; experiments/audit10_b101_theta.py and experiments/audit12_cal.py (calibrations), ~ 36 min |
| Table 4 | Size over 36 serially correlated designs and power under iid errors | `python experiments/audit16_v17_tables.py` → `experiments/results/tables_audit16/tab_summary_audit16.tex` | `bA_ma_audit12.json` | `experiments/audit12_bA_ma.py` | ~ 28 min (sum of batch times, logs_audit12/bA_run_audit12.log) | experiments/audit10_b101_theta.py (A10 calibration), ~ 36 min; experiments/audit12_cal.py (family 136 calibration), ~ 30 min |
|  |  |  | `b3_fixedb_audit15.json` | `experiments/audit15_b3_fixedb.py` | ~ 3 min (sum of batch times, logs_audit15/b3_fixedb_audit15.log) | self-contained: its own calibration (family 155) |
|  |  |  | `b1_boot_audit15.json` | `experiments/audit15_b1_boot.py` | ~ 46 min (sum of batch times, logs_audit15/b1_boot_audit15.log) | experiments/audit14_b1_critical.py (iid critical values, from the A10 calibration) |
| Table 5 | Power of MZt-GLS with five calibrations | `python experiments/audit15_v17_tables.py` → `experiments/results/tables_audit15/tab_bootpower_audit15.tex` | `b1_boot_audit15.json` | `experiments/audit15_b1_boot.py` | ~ 46 min (sum of batch times, logs_audit15/b1_boot_audit15.log) | experiments/audit14_b1_critical.py (iid critical values, from the A10 calibration) |
| Table 6 | MSB-B with fixed Bartlett bandwidths | `python experiments/audit16_v17_tables.py` → `experiments/results/tables_audit16/tab_fixedb_audit16.tex` | `b3_fixedb_audit15.json` | `experiments/audit15_b3_fixedb.py` | ~ 3 min (sum of batch times, logs_audit15/b3_fixedb_audit15.log) | self-contained: its own calibration (family 155) |
|  |  |  | `bA_ma_audit12.json` | `experiments/audit12_bA_ma.py` | ~ 28 min (sum of batch times, logs_audit12/bA_run_audit12.log) | experiments/audit10_b101_theta.py (A10 calibration), ~ 36 min; experiments/audit12_cal.py (family 136 calibration), ~ 30 min |
| Table B1 | Critical values of MSB-GLS and MZt-GLS | `python experiments/audit14_tables.py` → `experiments/results/tables_audit14/tab_critMSB_audit14.tex` | `b1_critical_audit14.json` | `experiments/audit14_b1_critical.py` | ~ 23 s (`elapsed_sec` field of the JSON (analysis step only)) | experiments/audit10_b101_theta.py (A10 calibration samples), ~ 36 min |

Figure 1 (`fig_calibration_gain_audit13q.pdf`) is drawn by `python experiments/make_figures_audit13q.py` from `e_calib_audit13.json`.

### Supplement

The supplement is built as a whole by `experiments/audit18_supplement.py` (which calls `audit17_supplement.py`, `audit16_supplement.py` and `audit15_supplement.py`); its tabulars, figures, data and protocols are included, already built, in `supplementary/`, and `supplementary/README.md` maps every tabular to its source. To rebuild it, the two manuscript source archives it transcribes and numbers against, `paper_latex_v16.zip` and `paper_latex_v18b.zip` (not part of this package), must be placed in the parent directory of the package root; then run `python experiments/audit18_supplement.py --out <dir>`. The result files and the scripts that produce them are included:

| Table | Label | Tabular | Result file(s) | Script that produces the result file | Time |
|---|---|---|---|---|---|
| S1.1 | `tab:size` | `supplementary/tables/tab_size_audit13.tex` | `b101_theta_audit10.json` | `experiments/audit10_b101_theta.py` | ~ 36 min (projection recorded before the run, logs_audit10/b101_run_audit10.log) |
|  |  |  | `b103_lown_audit10.json` | `experiments/audit10_b103_lown.py` | ~ 5 s (`elapsed_analysis_sec` field of the JSON (analysis step only)) |
|  |  |  | `e_size_audit13.json` | `experiments/audit13_e_size.py` | ~ 9.9 h (projection recorded before the run, logs_audit13/e_size_audit13.log) |
| S1.2 | `tab:dgp1` | `supplementary/tables/s1_tab_dgp1_full.tex` | `e_equalized_audit13.json` | `experiments/audit13_e_equalized.py` | ~ 15 s (`elapsed_analysis_sec` field of the JSON (analysis step only)) |
| S1.3 | `tab:ctpower` | `supplementary/tables/s1_tab_ctpower_full.tex` | `e_equalized_audit13.json` | `experiments/audit13_e_equalized.py` | ~ 15 s (`elapsed_analysis_sec` field of the JSON (analysis step only)) |
| S2.1 | `tab:serial` | `supplementary/tables/tab_serial_audit13.tex` | `bA_ma_audit12.json` | `experiments/audit12_bA_ma.py` | ~ 28 min (sum of batch times, logs_audit12/bA_run_audit12.log) |
| S2.2 | `tab:serialasy` | `supplementary/tables/tab_serial_asy_audit15.tex` | `b0_iidasy_audit15.json` | `experiments/audit15_b0_iidasy.py` | not recorded (-) |
| S2.3 | `tab:lag` | `supplementary/tables/tab_lag_audit15.tex` | `b0b_lag_audit15.json` | `experiments/audit15_b0b_lag.py` | not recorded (-) |
| S2.4 | `tab:boot` | `supplementary/tables/tab_boot_audit15.tex` | `b1_boot_audit15.json` | `experiments/audit15_b1_boot.py` | ~ 46 min (sum of batch times, logs_audit15/b1_boot_audit15.log) |
| S2.5 | `tab:fixedbsize` | `supplementary/tables/tab_fixedb_size_audit15.tex` | `b3_fixedb_audit15.json` | `experiments/audit15_b3_fixedb.py` | ~ 3 min (sum of batch times, logs_audit15/b3_fixedb_audit15.log) |
| S2.6 | `tab:serialpower` | `supplementary/tables/tab_serialpower_audit13.tex` | `bA_ma_audit12.json` | `experiments/audit12_bA_ma.py` | ~ 28 min (sum of batch times, logs_audit12/bA_run_audit12.log) |
| S2.7 | `tab:diagnull` | `supplementary/tables/s2_diag_a_diagnostics_null.tex` | `bA_ma_audit12.json` | `experiments/audit12_bA_ma.py` | ~ 28 min (sum of batch times, logs_audit12/bA_run_audit12.log) |
| S2.8 | `tab:diagalt` | `supplementary/tables/s2_diag_b_diagnostics_alt.tex` | `bA_ma_audit12.json` | `experiments/audit12_bA_ma.py` | ~ 28 min (sum of batch times, logs_audit12/bA_run_audit12.log) |
| S2.9 | `tab:diagattrib` | `supplementary/tables/s2_diag_c_attribution_diagnostics.tex` | `bB_attrib_audit12.json` | `experiments/audit12_bB_attrib.py` | ~ 2 min (sum of batch times, logs_audit12/bB_audit12.log) |
| S3.1 | `tab:initial` | `supplementary/tables/tab_initial_audit13.tex` | `bC_initial_audit12.json` | `experiments/audit12_bC_initial.py` | ~ 2 min (sum of batch times, logs_audit12/bC_audit12.log) |
| S4.1 | `tab:dgp2` | `supplementary/tables/tab_dgp2_audit13.tex` | `b103_equalized_audit10.json` | `experiments/audit10_b103_equalized.py` | ~ 9 s (`elapsed_analysis_sec` field of the JSON (analysis step only)) |
|  |  |  | `e_equalized_audit13.json` | `experiments/audit13_e_equalized.py` | ~ 15 s (`elapsed_analysis_sec` field of the JSON (analysis step only)) |
| S4.2 | `tab:dgp3` | `supplementary/tables/tab_dgp3_audit13.tex` | `b103_equalized_audit10.json` | `experiments/audit10_b103_equalized.py` | ~ 9 s (`elapsed_analysis_sec` field of the JSON (analysis step only)) |
|  |  |  | `e_equalized_audit13.json` | `experiments/audit13_e_equalized.py` | ~ 15 s (`elapsed_analysis_sec` field of the JSON (analysis step only)) |
| S4.3 | `tab:awb` | `supplementary/tables/tab_awb_audit13.tex` | `b103_awb_audit10.json` | `experiments/audit10_b103_awb.py` | ~ 3 s (`elapsed_analysis_sec` field of the JSON (analysis step only)) |
|  |  |  | `e_awb_audit13.json` | `experiments/audit13_e_awb.py` | ~ 48 min (projection recorded before the run, logs_audit13/e_awb_run_audit13.log) |
| S4.4 | `tab:misspec` | `supplementary/tables/tab_misspec_audit13.tex` | `b92_theta_audit9.json` | `experiments/audit9_b92_theta.py` | ~ 2.2 h (projection recorded before the run, logs_audit9/b92_run_audit9.log) |
| S5.1 | `tab:size02` | `supplementary/tables/s5_tab_size_theta0p02.tex` | `tables_audit13.json` | `experiments/audit13_tables.py` | not recorded (-) |
| S5.2 | `tab:calib02` | `supplementary/tables/s5_tab_calib_theta0p02.tex` | `tables_audit13.json` | `experiments/audit13_tables.py` | not recorded (-) |
| S5.3 | `tab:localpower02` | `supplementary/tables/s5_tab_localpower_theta0p02.tex` | `tables_audit13.json` | `experiments/audit13_tables.py` | not recorded (-) |
| S5.4 | `tab:dgp102` | `supplementary/tables/s5_tab_dgp1_theta0p02.tex` | `tables_audit13.json` | `experiments/audit13_tables.py` | not recorded (-) |
| S5.5 | `tab:ctpower02` | `supplementary/tables/s5_tab_ctpower_theta0p02.tex` | `tables_audit13.json` | `experiments/audit13_tables.py` | not recorded (-) |
| S5.6 | `tab:dgp202` | `supplementary/tables/s5_tab_dgp2_theta0p02.tex` | `tables_audit13.json` | `experiments/audit13_tables.py` | not recorded (-) |
| S5.7 | `tab:dgp302` | `supplementary/tables/s5_tab_dgp3_theta0p02.tex` | `tables_audit13.json` | `experiments/audit13_tables.py` | not recorded (-) |
| S5.8 | `tab:misspec02` | `supplementary/tables/s5_tab_misspec_theta0p02.tex` | `tables_audit13.json` | `experiments/audit13_tables.py` | not recorded (-) |
| S5.9 | `tab:awb02` | `supplementary/tables/s5_tab_awb_theta0p02.tex` | `tables_audit13.json` | `experiments/audit13_tables.py` | not recorded (-) |
| S5.10 | `tab:dgp502` | `supplementary/tables/s5_tab_dgp5_theta0p02.tex` | `tables_audit13.json` | `experiments/audit13_tables.py` | not recorded (-) |
| S5.11 | `tab:fp02` | `supplementary/tables/s5_tab_fp_theta0p02.tex` | `tables_audit13.json` | `experiments/audit13_tables.py` | not recorded (-) |
| S6.1 | `tab:dgp5` | `supplementary/tables/s6_tab_dgp5_full.tex` | `e_dgp5_audit13.json` | `experiments/audit13_e_dgp5.py` | ~ 5 s (`elapsed_sec` field of the JSON (analysis step only)) |
| S6.2 | `tab:negvariance` | `supplementary/tables/s6_neg_a_variance_channel.tex` | `b2_size_audit8.json` | `experiments/audit8_b2_size.py` | ~ 37 min (`calibration_sim_elapsed_sec (suma)` field of the JSON (analysis step only)) |
| S6.3 | `tab:negweight` | `supplementary/tables/s6_neg_b_adaptive_weight.tex` | `rhat_distribution_audit5b.json` | `experiments/audit5b_tarea_r4.py` | not recorded (-) |
| S6.4 | `tab:negrebal` | `supplementary/tables/s6_neg_c_rebalancing.tex` | `adaptive_size_power_audit5b.json` | `experiments/audit5b_tarea_r4.py` | not recorded (-) |
| S6.5 | `tab:neganchor` | `supplementary/tables/s6_neg_d_mean_anchor.tex` | `b4_local_power_audit8.json` | `experiments/audit8_b4_local_power.py` | ~ 28 s (`elapsed_analysis_sec` field of the JSON (analysis step only)) |
|  |  |  | `t5_claims_audit11.json` | `experiments/audit11_t5_claims.py` | not recorded (-) |
| S7.1 | `tab:hacrates` | `supplementary/tables/s7_hac_a_rates.tex` | `e4_slope_audit15.json` | `experiments/audit15_b2_slope.py` | ~ 6 s (`elapsed_sec` field of the JSON (analysis step only)) |
| S7.2 | `tab:hacmedian` | `supplementary/tables/s7_hac_b_hac_median.tex` | `audit2_results_audit2.json` | `experiments/audit2_presend_audit2.py` | not recorded (-) |
| S8.1 | `tab:critB` | `supplementary/tables/s8_critical_theta_0.tex` | `b103_cv_audit10.json` | `experiments/audit10_b103_cv.py` | ~ 2 min (sum of batch times, logs_audit10/b103_cv_audit10.log) |
| S8.2 | `tab:crit0p02` | `supplementary/tables/s8_critical_theta_0p02.tex` | `b103_cv_audit10.json` | `experiments/audit10_b103_cv.py` | ~ 2 min (sum of batch times, logs_audit10/b103_cv_audit10.log) |
| S8.3 | `tab:crit0p05` | `supplementary/tables/s8_critical_theta_0p05.tex` | `b103_cv_audit10.json` | `experiments/audit10_b103_cv.py` | ~ 2 min (sum of batch times, logs_audit10/b103_cv_audit10.log) |
| S8.4 | `tab:crit0p1` | `supplementary/tables/s8_critical_theta_0p1.tex` | `b103_cv_audit10.json` | `experiments/audit10_b103_cv.py` | ~ 2 min (sum of batch times, logs_audit10/b103_cv_audit10.log) |
| S8.5 | `tab:crit0p2` | `supplementary/tables/s8_critical_theta_0p2.tex` | `b103_cv_audit10.json` | `experiments/audit10_b103_cv.py` | ~ 2 min (sum of batch times, logs_audit10/b103_cv_audit10.log) |
| S8.6 | `tab:critMSBse` | `supplementary/tables/tab_critMSB_audit14.tex` | `b1_critical_audit14.json` | `experiments/audit14_b1_critical.py` | ~ 23 s (`elapsed_sec` field of the JSON (analysis step only)) |
| S9.1 | `tab:fp` | `supplementary/tables/tab_fp_audit13.tex` | `b103_application_audit10.json` | `experiments/audit10_b103_application.py` | ~ 18 min (`elapsed_sec` field of the JSON (analysis step only)) |
|  |  |  | `e_application_audit13.json` | `experiments/audit13_e_application.py` | ~ 4 min (`elapsed_sec` field of the JSON (analysis step only)) |
| S9.2 | `tab:deviations` | `supplementary/supplement.tex (inline tabular)` | `b103_application_audit10.json` | `experiments/audit10_b103_application.py` | ~ 18 min (`elapsed_sec` field of the JSON (analysis step only)) |
|  |  |  | `deviation_table_audit8.json` | `experiments/audit8_b6_application.py` | not recorded (-) |
|  |  |  | `e_application_audit13.json` | `experiments/audit13_e_application.py` | ~ 4 min (`elapsed_sec` field of the JSON (analysis step only)) |
|  |  |  | `real_data_comparison_audit5b.json` | `experiments/audit5b_tarea_r5.py` | not recorded (-) |
| S9.3 | `tab:oos` | `supplementary/tables/s9_app_a_oos_size.tex` | `e_application_audit13.json` | `experiments/audit13_e_application.py` | ~ 4 min (`elapsed_sec` field of the JSON (analysis step only)) |
| S9.4 | `tab:adverse` | `supplementary/tables/s9_app_b_adverse_cells.tex` | `e_application_audit13.json` | `experiments/audit13_e_application.py` | ~ 4 min (`elapsed_sec` field of the JSON (analysis step only)) |
| S9.5 | `tab:fpcell` | `supplementary/tables/s9_app_c_fp_by_cell.tex` | `e_application_audit13.json` | `experiments/audit13_e_application.py` | ~ 4 min (`elapsed_sec` field of the JSON (analysis step only)) |
| S9.6 | `tab:latency` | `supplementary/tables/s9_app_d_latency_by_event.tex` | `e_application_audit13.json` | `experiments/audit13_e_application.py` | ~ 4 min (`elapsed_sec` field of the JSON (analysis step only)) |

## Integrity

`MANIFEST.sha256` lists the sha256 of every file in this package (`sha256sum -c MANIFEST.sha256` on Linux/macOS). Each `experiments/results/manifest_audit*.json` records, for every result file of that audit, its sha256, the generating script and its sha256, and the commit; `supplementary/MANIFEST.sha256` covers the supplement.

## Development history

The work was carried out as a sequence of verification rounds, called audits (A1-A18). Each audit started from a written protocol that was committed to version control before any number was computed, and the scripts of an audit carry its number (`auditNN_*`). Changes of plan were registered as numbered amendments, and predictions about the outcome of expensive experiments were committed before running them (`experiments/protocol*.md`, `prediccion*.md`, `enmienda*.md`; anonymized copies in `supplementary/protocols/`). Components of the method that were evaluated and then discarded, such as the smoothing window, the second channel and the adaptive weight, are reported in Sections S5 and S6 of the supplement. The code was written and audited with the assistance of AI coding agents, as declared in Section 4.1 of the paper; all design and reporting decisions were approved by the author, who reviewed all code and takes full responsibility for it. Result files record the agent that produced them in the `provenance.assistant` field from the fifteenth audit on.

## License

- **Code** (`src/`, `tests/`, the scripts in `experiments/` and `verify_frozen_data.py`): MIT License; see `LICENSE`.
- **Results, supplement, figures and documentation** (`experiments/results/`, `supplementary/`, the protocol documents, `README.md`,
  `PROTOCOLS.md`, `SCRIPTS.md`, `ENVIRONMENT.txt`): Creative Commons Attribution 4.0 International (CC BY 4.0); see
  `LICENSE-CC-BY-4.0.md`.

## What is not included

- Price data of the application (see above), simulation checkpoints (`experiments/results/checkpoints/`, several GB), run logs, caches and the version-control history.
- Third-party material downloaded during the audits (the bootUR source tarball and a PDF), recorded by sha256 in `experiments/protocol_audit15_amend2.md`.
- Files that contain a local or temporary file-system path (audit bookkeeping, not inputs of any table):
  - `experiments/protocol_audit15.md`
  - `experiments/results/b5_anon_audit15.json`
  - `experiments/results/inventory_audit8.json`
  - `experiments/results/maintenance_audit15.json`
  - `experiments/results/resultados_auditoria_15.md`
  - `experiments/results/resultados_auditoria_8.md`

  `experiments/protocol_audit15.md` is available, anonymized, as `supplementary/protocols/protocol_audit15.md`.
- Audit reports that no script reads and no manifest lists (the reports of audits 2 to 7 and their task notes), which are working documents in Spanish and are not needed to reproduce any result.

## Note on `b1_validation_audit8.json`

The original file recorded the absolute paths of the modules it compared. The file in this package was regenerated with `python experiments/audit8_b1_validate.py --cores 14` in a clone of the repository at a neutral location (`C:\zb\pe`, temporary directory `C:\zb\tmp`), at the same commit as the rest of the package; apart from those paths, its provenance and its run time, its content is identical to the original. It backs the invariance figure of section 2 of the paper (worst relative discrepancy 5.2e-13 in the constant case and 4.1e-13 in the trend case, printed as 5e-13). Its gate V5 (published Ng-Perron quantiles within 3% for MZa and MPT) is false, as in the original audit. `manifest_audit8.json` was updated with the new entry. Check (V1) needs the version-control history, so the script must be run from a git clone.

`requirements.txt` is the full `pip freeze` of the workstation; `environment.yml` lists only what the code needs.
