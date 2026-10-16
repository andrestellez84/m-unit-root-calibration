"""
Variants of the rolling-mean component shared by the statistic and its null
calibration (A8, block B1).

All defaults reproduce the published statistic exactly:

    cal_sigma = "one"   the null is calibrated on Gaussian random walks with the
                        scale fixed at sigma = 1 (Definition 1 of the paper).
    cal_sigma = "hac"   every simulated calibration path computes sigma_hat with
                        the same HAC routine (Newey-West, Andrews bandwidth) that
                        is applied to the data.

    tau_mode = "theta"  tau = round(theta * n), bounded to [2, n // 2].
    tau_mode = "zero"   tau_1 = 0, so e_k = Y_k and g_1 = sqrt(Var_k(Y_k)): the
                        demeaned Sargan-Bhargava / MSB statistic with sigma_hat
                        (report label MSB-HAC). tau_2 keeps its theta value.

    anchor = "mean"     g_1 = sqrt(Var_k(e_k)), centred at the mean of the e_k
                        (report label RM).
    anchor = "gls"      g_1 = sqrt((1/N_k) sum_k (e_k - mu_hat)^2), N_k = n - tau + 1,
                        a non-centred second moment around a GLS anchor
                        (report label RM-GLS):
                          deterministics "c":  mu_hat by GLS with cbar = -7
                              (Elliott-Rothenberg-Stock), regression of
                              (Y_0, Y_1 - a Y_0, ..., Y_n - a Y_{n-1}) on
                              (1, 1 - a, ..., 1 - a), a = 1 + cbar / n;
                          deterministics "ct": the rolling means are formed on the
                              QD-detrended residual (cbar = -13.5, as in
                              deterministics.detrend_qd) and centred at zero.
                        g_2 is not modified by the anchor.

The standardization is the same in every variant: g_1 / (sigma_hat n^{1/2}).
"""

import numpy as np

from stationarity_test.deterministics import (
    apply_deterministics,
    detrend_qd,
    validate_deterministics,
)
from stationarity_test.hac_estimator import hac_newey_west
from stationarity_test.utils import rolling_mean, rolling_var, sample_variance_over_k

CAL_SIGMA = ("one", "hac")
TAU_MODES = ("theta", "zero")
ANCHORS = ("mean", "gls")
CBAR_CONST = -7.0


def validate_variant(cal_sigma: str = "one", tau_mode: str = "theta", anchor: str = "mean",
                     detrend: str = "qd") -> None:
    if cal_sigma not in CAL_SIGMA:
        raise ValueError(f"cal_sigma must be one of {CAL_SIGMA}, got {cal_sigma!r}")
    if tau_mode not in TAU_MODES:
        raise ValueError(f"tau_mode must be one of {TAU_MODES}, got {tau_mode!r}")
    if anchor not in ANCHORS:
        raise ValueError(f"anchor must be one of {ANCHORS}, got {anchor!r}")
    if anchor == "gls" and detrend != "qd":
        raise ValueError("anchor='gls' uses QD detrending; detrend must be 'qd'")


def gls_mean(Y: np.ndarray, cbar: float = CBAR_CONST) -> float:
    """GLS (quasi-differenced) estimate of the mean, a = 1 + cbar / n, n = len(Y) - 1."""
    Y = np.asarray(Y, dtype=np.float64)
    n = len(Y) - 1
    a = 1.0 + cbar / n
    yq = np.empty(n + 1)
    yq[0] = Y[0]
    yq[1:] = Y[1:] - a * Y[:-1]
    zq = np.full(n + 1, 1.0 - a)
    zq[0] = 1.0
    return float(np.dot(zq, yq) / np.dot(zq, zq))


def gls_anchored_series(Y: np.ndarray, deterministics: str = "c") -> np.ndarray:
    """Series whose rolling means enter the non-centred moment of RM-GLS."""
    if deterministics == "c":
        return np.asarray(Y, dtype=np.float64) - gls_mean(Y)
    return detrend_qd(Y)


def g1_raw(Y: np.ndarray, Y_stat: np.ndarray, tau_1: int, deterministics: str = "c",
           anchor: str = "mean") -> float:
    """Raw rolling-mean seminorm for the chosen anchor."""
    if anchor == "mean":
        means = rolling_mean(Y_stat, tau_1)
        return float(np.sqrt(max(sample_variance_over_k(means), 0.0)))
    u = gls_anchored_series(Y, deterministics)
    means = rolling_mean(u, tau_1)
    return float(np.sqrt(np.mean(means * means)))


def g2_raw(Y_stat: np.ndarray, tau_2: int) -> float:
    variances = rolling_var(Y_stat, tau_2)
    return float(np.sqrt(max(sample_variance_over_k(variances), 0.0)))


def path_statistic(Y: np.ndarray, n: int, tau_1: int, tau_2: int, R: float, sigma_sq: float,
                   c_1: float, c_2: float, deterministics: str = "c", detrend: str = "qd",
                   anchor: str = "mean", need_g2: bool = True) -> tuple[float, float, float]:
    """
    Standardized components and combined statistic on one path.

    sigma_sq is the squared scale used in the standardization: 1.0 for the
    published calibration, the HAC estimate for data and for cal_sigma="hac".
    Returns (statistic, g1_std, g2_std).
    """
    Y_stat = apply_deterministics(Y, deterministics, detrend)
    g1 = g1_raw(Y, Y_stat, tau_1, deterministics, anchor)
    g2 = g2_raw(Y_stat, tau_2) if need_g2 else 0.0
    sigma = np.sqrt(sigma_sq)
    scale_1 = sigma * n ** (c_1 / 2.0)
    scale_2 = sigma_sq * n ** (c_2 / 2.0)
    g1_std = g1 / scale_1 if scale_1 > 0 else 0.0
    g2_std = g2 / scale_2 if scale_2 > 0 else 0.0
    stat = np.sqrt((1.0 - R)**2 * g1_std**2 + R**2 * g2_std**2)
    return float(stat), float(g1_std), float(g2_std)


def hac_sigma_sq(Y: np.ndarray, andrews_pilot: str = "alpha1") -> float:
    """HAC long-run variance of diff(Y) of the original (not detrended) series."""
    return hac_newey_west(np.diff(Y), andrews_pilot=andrews_pilot)


__all__ = ["CAL_SIGMA", "TAU_MODES", "ANCHORS", "CBAR_CONST", "validate_variant", "gls_mean",
           "gls_anchored_series", "g1_raw", "g2_raw", "path_statistic", "hac_sigma_sq",
           "validate_deterministics"]
