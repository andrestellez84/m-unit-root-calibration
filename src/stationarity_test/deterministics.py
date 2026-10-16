"""
Deterministic components for the stationarity test (A7, Block 2).

deterministics = "c"  : current behaviour. The series is used as it is.
deterministics = "ct" : before forming the rolling means e_k^tau and rolling
                        variances [sigma_k^tau]^2, Y is replaced by its residuals
                        from detrending against (1, t). Two variants:

  detrend = "qd"  (main) Elliott-Rothenberg-Stock quasi-differencing with
                  cbar = -13.5, the DF-GLS convention for the trend case.
  detrend = "ols"        OLS residuals of Y on (1, t).

The HAC scale is still computed on diff(Y) of the ORIGINAL series (it is
demeaned, so a linear drift does not affect it). With this, the statistic is
invariant to Y -> a*Y + b + c*t: both residual constructions remove b + c*t
exactly, the residuals scale with a, and sigma_hat scales with |a|.
"""

import numpy as np

DETERMINISTICS = ("c", "ct")
DETREND_METHODS = ("qd", "ols")
CBAR_TREND = -13.5


def validate_deterministics(deterministics: str, detrend: str) -> None:
    if deterministics not in DETERMINISTICS:
        raise ValueError(f"deterministics must be one of {DETERMINISTICS}, got {deterministics!r}")
    if detrend not in DETREND_METHODS:
        raise ValueError(f"detrend must be one of {DETREND_METHODS}, got {detrend!r}")


def _trend_regressors(T: int) -> np.ndarray:
    t = np.arange(1, T + 1, dtype=np.float64)
    return np.column_stack([np.ones(T), t])


def detrend_ols(Y: np.ndarray) -> np.ndarray:
    """Residuals of the OLS regression of Y on (1, t)."""
    Y = np.asarray(Y, dtype=np.float64)
    Z = _trend_regressors(len(Y))
    beta, *_ = np.linalg.lstsq(Z, Y, rcond=None)
    return Y - Z @ beta


def detrend_qd(Y: np.ndarray, cbar: float = CBAR_TREND) -> np.ndarray:
    """
    ERS quasi-differenced (GLS) detrending against (1, t).

    alpha = 1 + cbar / T. The first observation enters in levels; the rest as
    y_t - alpha * y_{t-1}, and likewise for the regressors. beta is the OLS
    coefficient of the quasi-differenced regression and the residual is
    Y - Z beta on the original scale.
    """
    Y = np.asarray(Y, dtype=np.float64)
    T = len(Y)
    alpha = 1.0 + cbar / T
    Z = _trend_regressors(T)
    ya = np.empty(T)
    za = np.empty_like(Z)
    ya[0] = Y[0]
    za[0] = Z[0]
    ya[1:] = Y[1:] - alpha * Y[:-1]
    za[1:] = Z[1:] - alpha * Z[:-1]
    beta, *_ = np.linalg.lstsq(za, ya, rcond=None)
    return Y - Z @ beta


def apply_deterministics(Y: np.ndarray, deterministics: str = "c", detrend: str = "qd") -> np.ndarray:
    """Series on which the rolling statistics are formed."""
    validate_deterministics(deterministics, detrend)
    if deterministics == "c":
        return Y
    return detrend_qd(Y) if detrend == "qd" else detrend_ols(Y)
