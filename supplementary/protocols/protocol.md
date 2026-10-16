# Pre-specified Protocol: Real Financial Data Validation

**Date of registration**: 2026-06-12
**Status**: LOCKED (do not modify after hash registration)

## 1. Objective

Validate the practical utility of the stationarity test on real financial
data using a pre-specified protocol immune to hindsight bias. All decisions
in this document were made BEFORE downloading or examining any financial data.

## 2. Events

Six historical financial events, selected for their well-documented impact
on market regimes:

| ID | Event | Date | Rationale |
|----|-------|------|-----------|
| E1 | Black Monday | 1987-10-19 | Largest single-day crash |
| E2 | Asian Crisis | 1997-07-02 | Emerging market contagion |
| E3 | Russian Crisis | 1998-08-17 | Sovereign default + LTCM |
| E4 | Dot-com Crash | 2000-03-10 | Tech bubble peak |
| E5 | Subprime/Lehman | 2008-09-15 | Global financial crisis |
| E6 | COVID-19 | 2020-02-20 | Pandemic onset in markets |

## 3. Indices

| Ticker | Index | Coverage Notes |
|--------|-------|----------------|
| ^GSPC | S&P 500 | Full coverage from 1980+ |
| ^FTSE | FTSE 100 | Reliable from ~1988; E1 EXCLUDED (see §7) |
| ^N225 | Nikkei 225 | Coverage TBD; E1 excluded if pre-1988 (see §7) |
| ^GDAXI | DAX | Official from 1988; E1 EXCLUDED (see §7) |

## 4. Test Configuration

- **Statistic**: g_tilde_R^theta with adaptive R-hat
- **Theta**: (0.1, 0.1) — validated by KS test (D < 0.01)
- **R**: Adaptive (R-hat computed per window)
- **Alpha**: 0.05
- **Null CDF**: Empirical, calibrated with adaptive R mechanism
  (N_cal = 10,000 per window size D)
- **Window sizes**: D in {150, 200, 250, 300} trading days

## 5. Baselines

| Test | Implementation | Notes |
|------|----------------|-------|
| ADF | statsmodels `adfuller`, auto-lag by AIC | H0: unit root |
| PP | statsmodels `PhillipsPerron`, Newey-West | H0: unit root |
| KPSS | statsmodels `kpss`, constant spec | H0: stationarity (opposite) |

## 6. Metrics

### Metric 1: Latency (days to detection)

For each event E with date t_E:
  latency[test, E, index, D] = min{t > t_E : p_test(t) < alpha} - t_E

where p_test(t) is the p-value of the test applied to the window [t-D, t].
Measured in trading days.

### Metric 2: False positive rate

For each control period C:
  fp_rate[test, C, index, D] = #{t in C : p_test(t) < alpha} / |C|

### Control periods (pre-specified as calm)

| Period | Year | Rationale |
|--------|------|-----------|
| C1 | 1993 | Low-volatility expansion |
| C2 | 2005 | Pre-crisis stability |
| C3 | 2017 | Low-VIX environment |

## 7. Pre-specified Exclusions

The following event-index cells are EXCLUDED due to data availability,
NOT due to results (which have not been seen at time of writing):

- **FTSE x E1 (Black Monday 1987)**: ^FTSE data on Yahoo Finance
  is unreliable before 1988.
- **DAX x E1 (Black Monday 1987)**: The DAX index was officially
  introduced on 1988-07-01. Yahoo Finance returns no data for
  ^GDAXI in October 1987 (verified: "possibly delisted" error).
- **Nikkei x E1**: INCLUDED. Yahoo Finance provides ^N225 data
  covering October 1987 with daily resolution (verified).

These exclusions are declared a priori and documented before any data
download. The design has 22 event-index cells (6 events x 4 indices
minus 2 exclusions: FTSE x E1, DAX x E1), plus 12 control-period cells.

## 8. Success and Failure Criteria

### Success criterion
The proposed test achieves:
- Mean latency <= mean latency of ADF AND PP AND KPSS
- False positive rate <= false positive rate of ADF AND PP AND KPSS

### Failure criterion
If the false positive rate of the proposed test is STRICTLY GREATER
than ANY baseline, this is reported as an adverse result, with no
post-hoc adjustment of the protocol.

### Honest reporting commitment
Results are reported regardless of their sign. The protocol is not
modified after data are examined. Any deviation from this protocol
is documented as a protocol violation.

## 9. Data Handling

- Download once via yfinance (Close prices, NOT Adj Close)
- Compute log-prices: log_price = log(Close)
- Save raw CSVs to experiments/data/
- Compute SHA-256 hash of each CSV
- CSVs are frozen after download; yfinance is not re-invoked

## 10. Hash Registration

SHA-256 of this file (before any data download):
[TO BE COMPUTED AND REGISTERED]
