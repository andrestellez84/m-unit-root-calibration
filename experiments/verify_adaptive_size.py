"""
Verify that the adaptive-R test has correct empirical size under H0.

Steps:
    1. Build the adaptive null CDF with (theta, n) = ((0.1, 0.1), 200),
       N_cal = 10000, seed = 42.
    2. Simulate N_test = 5000 fresh random walks (seed = 9999).
    3. For each path, compute the adaptive statistic (g1_std, g2_std ->
       R_hat -> combined stat) and evaluate p = cdf(stat).
    4. Count rejections at alpha = 0.05.
    5. Assert rejection rate is in [0.035, 0.065].

Uses sigma = 1 (known) for standardization, matching the null CDF
calibration.
"""

import numpy as np

from stationarity_test.constants import DEFAULT_SCALING_EXPONENTS
from stationarity_test.empirical_eigenvalues import build_null_cdf_adaptive
from stationarity_test.utils import rolling_mean, rolling_var, sample_variance_over_k


def main() -> None:
    # --- Parameters ---
    theta = (0.1, 0.1)
    n = 200
    N_cal = 10000
    cal_seed = 42
    N_test = 5000
    test_seed = 9999
    alpha = 0.05

    # --- Step 1: Build adaptive null CDF ---
    print(f"Building adaptive null CDF: theta={theta}, n={n}, "
          f"N_cal={N_cal}, seed={cal_seed} ...")
    cdf_func = build_null_cdf_adaptive(theta, n, N_cal=N_cal, seed=cal_seed)
    print("  Done.")

    # --- Step 2: Simulate fresh random walks ---
    c_1 = DEFAULT_SCALING_EXPONENTS[1]
    c_2 = DEFAULT_SCALING_EXPONENTS[2]

    theta_1, theta_2 = theta
    tau_1 = max(2, min(int(round(theta_1 * n)), n // 2))
    tau_2 = max(2, min(int(round(theta_2 * n)), n // 2))

    scale_1 = 1.0 * n ** (c_1 / 2.0)
    scale_2 = 1.0 * n ** (c_2 / 2.0)

    rng = np.random.default_rng(test_seed)
    rejections = 0

    print(f"Testing {N_test} fresh random walks (seed={test_seed}) ...")
    for j in range(N_test):
        innovations = rng.standard_normal(n)
        Y = np.empty(n + 1, dtype=np.float64)
        Y[0] = 0.0
        np.cumsum(innovations, out=Y[1:])

        # Raw seminorms
        means = rolling_mean(Y, tau_1)
        g1_raw = float(np.sqrt(max(sample_variance_over_k(means), 0.0)))

        variances = rolling_var(Y, tau_2)
        g2_raw = float(np.sqrt(max(sample_variance_over_k(variances), 0.0)))

        # Standardize (sigma=1 exactly)
        g1_std = g1_raw / scale_1
        g2_std = g2_raw / scale_2

        # Adaptive weight
        denom = g1_std**2 + g2_std**2
        if denom > 0.0:
            R_hat = g2_std**2 / denom
        else:
            R_hat = 0.5

        # Combined statistic
        stat = np.sqrt(
            (1.0 - R_hat)**2 * g1_std**2 + R_hat**2 * g2_std**2
        )

        # P-value from the adaptive CDF
        p_value = float(cdf_func(stat))

        # Reject H0 if p-value exceeds 1 - alpha (upper tail)
        if p_value >= 1.0 - alpha:
            rejections += 1

    rejection_rate = rejections / N_test

    # --- Step 5: Report and assert ---
    print(f"\n{'='*50}")
    print(f"  alpha           = {alpha}")
    print(f"  N_test          = {N_test}")
    print(f"  rejections      = {rejections}")
    print(f"  rejection rate  = {rejection_rate:.4f}")
    print(f"  expected range  = [0.035, 0.065]")
    print(f"{'='*50}")

    assert 0.035 <= rejection_rate <= 0.065, (
        f"Rejection rate {rejection_rate:.4f} outside [0.035, 0.065]!"
    )
    print("\n[PASS] Size verification PASSED.")


if __name__ == "__main__":
    main()
