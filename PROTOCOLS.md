# Protocols, amendments and registered predictions

This is an English guide to the protocol documents in `experiments/`. Each document was committed to version control before the
computations it governs, and its content is part of the provenance of the results (several result files record its sha256 or the
commit that introduced it). The documents themselves are in Spanish, except `protocol.md`; **the Spanish originals are the
registered versions** and are not translated here, because a translated file would no longer match its registered hash. Anonymized
copies of the same documents are in `supplementary/protocols/`.

Each protocol of an audit copies the assignment literally, records the decisions taken before registration, and fixes the
"operational readings": the exact rule that each step follows, the seed families, the numerical gates that must pass before an
expensive block runs, and what counts as each possible outcome.

## Application (pre-registered)

| File | Content |
|---|---|
| `protocol.md` | Pre-specified protocol of the monitoring application to four equity indices: data, events, windows, control periods, metrics and the adverse-reporting rule. Registered on 2026-06-12, before any price data were downloaded; its sha256 is in `protocol_hash.json`. |
| `protocol_hash.json` | sha256 of `protocol.md` and the time it was registered. |

## Audit 7: the two-channel extension (DGP 5)

| File | Content |
|---|---|
| `prediccion_dgp5_audit7.md` | Registered hypothesis, predictions and falsification condition for the pre-registered experiment on the two-channel statistic under a variance break (supplement, Section S6). |
| `enmienda_dgp5_audit7.md` | First amendment: why design choices were made after the first block (the nominal gate of the variance channel failed), and the rules for reading the cells. The predictions are not changed. |
| `enmienda2_dgp5_audit7.md` | Second amendment: cells added to the grid, the n = 1000 cells withdrawn, and how the added cells are read. The predictions and the falsification condition are not changed. |

## Audits 8 to 14

| File | Content |
|---|---|
| `protocol_audit8.md` | A8: the primary configuration of the test fixed in advance, the validation gates (B1), size (B2), comparators (B3), local power (B4), power (B5) and the application (B6). |
| `protocol_audit8_amend1.md` | A8, amendment 1: the tolerance of the check against the published Ng and Perron quantiles, revised after the B1 data and before any B2 data, with the reason given by the author. |
| `protocol_audit8_amend2.md` | A8, amendment 2: the gate B2b re-evaluated on independent paths, with the reason given by the author. |
| `protocol_audit9.md` | A9: final configuration of the primary statistic; equalized-size power, the ladder of smoothing windows theta, attribution, finite-sample size, the wild-bootstrap (AWB) calibration and critical values, each with its gate. |
| `protocol_audit10.md` | A10: a clean decision on theta under a rule fixed before the comparison (supplement, Section S5) and consolidation of all results with a calibration of 500 000 paths. |
| `protocol_audit11.md` | A11: closing tasks for a manuscript version: figures in English, the GLS anchor, the trend case of the consistency argument, and verification of the claims. |
| `prediccion_ma_audit12.md` | A12: registered prediction for the experiment with moving-average errors. |
| `protocol_audit12.md` | A12: moving-average and autoregressive errors (36 designs), the Perron-Qu lag selection, the initial condition, the GLS anchor bias and the statistic without a window (theta = 0). |
| `protocol_audit13.md` | A13: regeneration of every table of the paper with theta = 0, from stored paths, and the closing checks. |
| `protocol_audit13_amend1.md` | A13, amendment 1: final coherence check of a manuscript version (every number against its result file), the attribution table and the figure legends. |
| `protocol_audit14.md` | A14: the critical values of MSB-GLS and MZt-GLS with exact bootstrap standard errors (Table B1), the sources of numbers not yet traced, and verification of a manuscript version. |

## Audit 15 and its amendments (audits 16 to 18)

`protocol_audit15.md` itself is distributed only in its anonymized copy, `supplementary/protocols/protocol_audit15.md`.

| File | Content |
|---|---|
| `protocol_audit15.md` (in `supplementary/protocols/`) | A15: bootstrap calibrations of MZt-GLS under serial correlation (sieve, sieve wild and autoregressive wild bootstraps), fixed-bandwidth Bartlett scales, the iid and asymptotic comparison, and anonymization of the supplement. |
| `prediccion_boot_audit15.md` | A15: registered predictions for the bootstrap experiment and the fixed-b experiment, with numerical margins for each outcome. |
| `protocol_audit15_amend1.md` | Amendment 1: the author's decisions before computation (arms, order of checks, sealed probes, downloads). |
| `protocol_audit15_amend2.md` | Amendment 2: the rules read from the source code of bootUR 1.0.5 and from Lazarus, Lewis, Stock and Watson (2018) that the replication follows, and the seed streams per arm. |
| `protocol_audit15_amend3.md` | Amendment 3: the author's decisions after the first check of the bootUR replication (a larger number of bootstrap replications, new criteria, the computing budget). |
| `protocol_audit15_amend4.md` | Amendment 4: the tables and printed figures of a manuscript version, and the reconstruction of the supplement. |
| `protocol_audit15_amend5.md` | Amendment 5: repository maintenance, corrections to the supplement generator and the summary table. |
| `protocol_audit15_amend6.md` | Amendment 6 (audit A16): checks of the text against the code, new printed figures, the reconstruction of the supplement and a coherence check of a manuscript version. |
| `protocol_audit15_amend7.md` | Amendment 7 (audit A17): checks of the submitted version (formulas against the code, the bootstrap description against bootUR), edits to the supplement and the submission package. |
| `protocol_audit15_amend8.md` | Amendment 8 (audit A18): final repackaging of the submitted version. |

Audits 1 to 6 predate the practice of writing a protocol per audit; their scripts and result files are included, and the
application they used was governed by `protocol.md`.
