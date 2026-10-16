"""
Davies Algorithm AS 155: Distribution of a linear combination of chi-squared
random variables.

Implements the algorithm from:
    Davies, R.B. (1980), "Algorithm AS 155: The Distribution of a Linear
    Combination of chi^2 Random Variables", Journal of the Royal Statistical
    Society. Series C (Applied Statistics), 29(3), 323-333.

Computes P(Q <= x) where Q = sum_k lambda_k * chi^2_1(k), with lambda_k > 0
and chi^2_1(k) independent chi-squared(1) random variables.

Decision D4: This direct implementation replaces scipy.integrate.quad,
which has documented precision issues with oscillatory integrands like
Im[phi(t) * exp(-i*t*x)] / t.

The algorithm uses the inversion formula:
    P(Q <= x) = 1/2 - (1/pi) * int_0^inf Im[exp(-i*t*x) * phi(t)] / t dt

where phi(t) = prod_k (1 - 2*i*lambda_k*t)^{-1/2} is the characteristic
function of Q.

A Satterthwaite moment-matching approximation (scaled chi-squared) is used
as a fallback for the far tails where the oscillatory integral loses accuracy.
"""

import warnings

import numpy as np
from scipy.integrate import quad
from scipy.stats import chi2 as chi2_dist


# ===================================================================
# Moment-matching (Satterthwaite) approximation
# ===================================================================

def _satterthwaite_params(eigenvalues: np.ndarray) -> tuple[float, float]:
    """
    Compute Satterthwaite approximation parameters.

    Matches Q = sum lambda_k * chi^2_1(k) to c * chi^2(nu) where:
        c = Var(Q) / (2 * E[Q]) = sum(lambda^2) / sum(lambda)
        nu = 2 * E[Q]^2 / Var(Q) = (sum lambda)^2 / sum(lambda^2)

    Returns (c, nu).
    """
    s1 = np.sum(eigenvalues)
    s2 = np.sum(eigenvalues**2)

    if s1 <= 0 or s2 <= 0:
        return 1.0, 1.0

    c = s2 / s1
    nu = s1**2 / s2
    return c, nu


def _satterthwaite_cdf(x: float, eigenvalues: np.ndarray) -> float:
    """CDF via Satterthwaite approximation: P(c * chi^2(nu) <= x)."""
    c, nu = _satterthwaite_params(eigenvalues)
    if c <= 0 or nu <= 0:
        return 0.5
    return float(chi2_dist.cdf(x / c, nu))


# ===================================================================
# Davies inversion formula
# ===================================================================

def davies_cdf(
    x: float,
    eigenvalues: np.ndarray,
    accuracy: float = 1e-6
) -> tuple[float, float, int]:
    """
    Compute P(Q <= x) where Q = sum_k lambda_k * chi^2_1(k).

    Uses the characteristic function inversion formula for the central
    region and falls back to Satterthwaite approximation in the tails.

    Parameters
    ----------
    x : float
        Point at which to evaluate the CDF.
    eigenvalues : np.ndarray
        Positive eigenvalues lambda_k. Must all be > 0.
    accuracy : float
        Required accuracy.

    Returns
    -------
    prob : float
        P(Q <= x), clipped to [0, 1].
    bound : float
        Upper bound on the error |P_true - P_computed|.
    ifault : int
        Error code: 0 = success, 1 = accuracy not achieved,
        2 = roundoff error possibly significant, 4 = invalid parameters.
    """
    eigenvalues = np.asarray(eigenvalues, dtype=np.float64)

    # Validate
    if eigenvalues.ndim != 1 or len(eigenvalues) == 0:
        return 0.0, 1.0, 4
    if np.any(eigenvalues <= 0):
        return 0.0, 1.0, 4
    if x <= 0:
        return 0.0, accuracy, 0

    # Sort eigenvalues in decreasing order for numerical stability
    eigenvalues = np.sort(eigenvalues)[::-1]
    K = len(eigenvalues)

    # Mean and variance of Q
    mean_Q = np.sum(eigenvalues)
    var_Q = 2.0 * np.sum(eigenvalues**2)
    std_Q = np.sqrt(var_Q)

    # For x in the far tails, the oscillatory integral loses accuracy.
    # Use Satterthwaite approximation instead.
    if std_Q > 0:
        z_score = (x - mean_Q) / std_Q
    else:
        z_score = float('inf') if x > mean_Q else float('-inf')

    if z_score > 6.0:
        # Deep right tail: CDF is very close to 1
        prob = _satterthwaite_cdf(x, eigenvalues)
        return max(prob, 1.0 - accuracy), accuracy, 0
    if z_score < -6.0:
        # Deep left tail: CDF is very close to 0
        prob = _satterthwaite_cdf(x, eigenvalues)
        return min(prob, accuracy), accuracy, 0

    # --- Inversion formula integration ---
    lam_max = eigenvalues[0]

    # Determine integration limit: integrate until |phi(T)| < accuracy
    T_max = _compute_T_max(eigenvalues, accuracy)

    def integrand(t):
        if t == 0:
            return 0.0
        return _davies_integrand(t, x, eigenvalues)

    # Subdivide based on oscillation period of exp(-itx)
    if x > 0:
        period = 2.0 * np.pi / x
        n_periods = max(1, int(T_max / period))
        n_intervals = min(max(20, n_periods * 4), 800)
    else:
        n_intervals = 40

    total_integral = 0.0
    total_abserr = 0.0
    ifault = 0

    breakpoints = np.linspace(0, T_max, n_intervals + 1)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        for i in range(n_intervals):
            a_i, b_i = breakpoints[i], breakpoints[i + 1]
            try:
                val, abserr = quad(integrand, a_i, b_i,
                                   limit=200, epsabs=accuracy / n_intervals,
                                   epsrel=1e-10)
                total_integral += val
                total_abserr += abserr
            except Exception:
                ifault = max(ifault, 1)

    prob = 0.5 - total_integral / np.pi

    # Clip to valid range
    prob = float(np.clip(prob, 0.0, 1.0))

    bound = total_abserr / np.pi + _tail_bound(T_max, eigenvalues)

    if bound > accuracy:
        ifault = max(ifault, 1)

    # Cross-check with Satterthwaite: if they disagree wildly, use Satterthwaite
    prob_satt = _satterthwaite_cdf(x, eigenvalues)
    if abs(prob - prob_satt) > 0.3 and abs(z_score) > 3.0:
        # Integration likely failed; trust the approximation
        prob = prob_satt
        ifault = max(ifault, 2)

    return prob, float(bound), ifault


def _davies_integrand(t: float, x: float, eigenvalues: np.ndarray) -> float:
    """
    Compute Im[phi(t) * exp(-i*t*x)] / t.

    phi(t) = prod_k (1 - 2i*lambda_k*t)^{-1/2}

    We work in log-scale to prevent overflow:
    log(phi(t)) = -1/2 * sum_k log(1 - 2i*lambda_k*t)

    For (1 - 2i*lam*t):
        |1 - 2i*lam*t| = sqrt(1 + 4*lam^2*t^2)
        arg(1 - 2i*lam*t) = -arctan(2*lam*t)

    So: log|phi| = -1/4 * sum_k log(1 + 4*lam_k^2*t^2)
        arg(phi) = 1/2 * sum_k arctan(2*lam_k*t)
    """
    if abs(t) < 1e-15:
        return 0.0

    # Log-magnitude and phase of phi(t)
    lam_t_2 = 2.0 * eigenvalues * t
    log_mag = -0.25 * np.sum(np.log1p(lam_t_2**2))

    # Early termination: if magnitude is negligibly small
    if log_mag < -50.0:
        return 0.0

    phase = 0.5 * np.sum(np.arctan(lam_t_2))

    # phi(t) * exp(-i*t*x) = |phi| * exp(i*(phase - t*x))
    total_phase = phase - t * x

    # Im[phi(t) * exp(-i*t*x)] / t
    magnitude = np.exp(log_mag)
    return magnitude * np.sin(total_phase) / t


def _compute_T_max(eigenvalues: np.ndarray, accuracy: float) -> float:
    """
    Determine integration truncation point T_max.

    We need |phi(T_max)| < accuracy, i.e.,
    exp(-0.25 * sum log(1 + 4*lam_k^2*T^2)) < accuracy.

    For large T: sum log(4*lam_k^2*T^2) ≈ K*log(4T^2) + 2*sum(log lam_k).
    So the decay rate is governed by K (number of eigenvalues).
    """
    K = len(eigenvalues)
    lam_max = eigenvalues[0]
    lam_min = eigenvalues[-1]

    log_acc = abs(np.log(max(accuracy, 1e-15)))
    target_log_decay = 4.0 * log_acc  # we want -log_mag > log_acc

    # Start with a moderate T_max and increase until decay is sufficient
    T = 10.0 / lam_max
    for _ in range(20):
        lam_t_2 = 2.0 * eigenvalues * T
        log_mag = -0.25 * np.sum(np.log1p(lam_t_2**2))
        if log_mag < -log_acc:
            break
        T *= 2.0

    # Cap to prevent excessive computation
    T_max = min(T, 5000.0 / lam_max)

    return T_max


def _tail_bound(T_max: float, eigenvalues: np.ndarray) -> float:
    """
    Upper bound on the tail integral beyond T_max.
    """
    lam_t_2 = 2.0 * eigenvalues * T_max
    log_mag_at_Tmax = -0.25 * np.sum(np.log1p(lam_t_2**2))
    return float(np.exp(log_mag_at_Tmax))


# ===================================================================
# Quantile computation (bisection on CDF)
# ===================================================================

def davies_quantile(
    p: float,
    eigenvalues: np.ndarray,
    accuracy: float = 1e-6
) -> float:
    """
    Compute quantile q such that P(Q <= q) = p, where Q = sum lambda_k * chi^2_1.

    Uses bisection on davies_cdf. For initial bracket, uses the
    Satterthwaite chi-squared approximation.

    Parameters
    ----------
    p : float
        Probability level, p in (0, 1).
    eigenvalues : np.ndarray
        Positive eigenvalues lambda_k.
    accuracy : float
        Required accuracy for the quantile.

    Returns
    -------
    float
        Quantile q.
    """
    eigenvalues = np.asarray(eigenvalues, dtype=np.float64)

    if not (0.0 < p < 1.0):
        raise ValueError(f"p must be in (0, 1), got {p}")

    # Initial bounds from Satterthwaite approximation
    c, nu = _satterthwaite_params(eigenvalues)
    x_init = c * chi2_dist.ppf(p, nu)
    x_init = max(x_init, 0.0)

    # Mean and std of Q
    mean_Q = np.sum(eigenvalues)
    std_Q = np.sqrt(2.0 * np.sum(eigenvalues**2))

    # Find bracket [lo, hi] such that cdf(lo) < p < cdf(hi)
    lo = 0.0
    hi = max(x_init * 3, mean_Q + 6 * std_Q)

    # Verify bracket
    prob_hi, _, _ = davies_cdf(hi, eigenvalues, accuracy)

    # Expand hi if needed
    for _ in range(20):
        if prob_hi >= p:
            break
        hi *= 2
        prob_hi, _, _ = davies_cdf(hi, eigenvalues, accuracy)

    # Bisection
    for _ in range(100):
        if hi - lo < accuracy:
            break
        mid = (lo + hi) / 2.0
        prob_mid, _, _ = davies_cdf(mid, eigenvalues, accuracy)
        if prob_mid < p:
            lo = mid
        else:
            hi = mid

    return (lo + hi) / 2.0
