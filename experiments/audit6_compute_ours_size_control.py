"""
Computa el test propuesto sobre las dos nulas de control de tamano:
1. Paseo aleatorio puro (seed_base = 100000 + n * 100)
2. Paseo aleatorio con quiebre de media Delta=1.0 (seed_base = 150000 + n * 100)
5000 replicas por celda, n in {200, 500, 1000}.
Guarda ours_size y ours_ci directamente en dgp2_break_tests_audit6.json.
"""
import os
import sys
import json
import time
import numpy as np
from scipy.stats import beta
from joblib import Parallel, delayed

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from stationarity_test.empirical_eigenvalues import build_null_cdf
from stationarity_test.hac_estimator import hac_newey_west
from stationarity_test.utils import rolling_mean, rolling_var, sample_variance_over_k
from stationarity_test.constants import DEFAULT_SCALING_EXPONENTS

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
JSON_PATH = os.path.join(RESULTS_DIR, "dgp2_break_tests_audit6.json")

ALPHA = 0.05
N_SIM = 5000
N_GRID = [200, 500, 1000]

def clopper_pearson_ci(k: int, n: int, alpha: float = 0.05):
    low = 0.0 if k == 0 else float(beta.ppf(alpha / 2, k, n - k + 1))
    high = 1.0 if k == n else float(beta.ppf(1 - alpha / 2, k + 1, n - k))
    return float(round(low, 4)), float(round(high, 4))

def generate_rw_pure(n, rng):
    eps = rng.standard_normal(n)
    Y = np.empty(n + 1)
    Y[0] = 0.0
    np.cumsum(eps, out=Y[1:])
    return Y

def generate_rw_break_mean(n, delta_mu, rng):
    eps = rng.standard_normal(n)
    t_break = n // 2
    shift = np.zeros(n)
    shift[t_break:] = delta_mu
    eps_shifted = eps + np.diff(np.concatenate(([0.0], shift)))
    Y = np.empty(n + 1)
    Y[0] = 0.0
    np.cumsum(eps_shifted, out=Y[1:])
    return Y

def evaluate_ours(y, n, cdf_050, c_1, c_2, tau_1, tau_2):
    means = rolling_mean(y, tau_1)
    g1_raw = float(np.sqrt(max(sample_variance_over_k(means), 0.0)))
    variances = rolling_var(y, tau_2)
    g2_raw = float(np.sqrt(max(sample_variance_over_k(variances), 0.0)))
    diffs = np.diff(y)
    s2 = hac_newey_west(diffs, andrews_pilot="alpha2")
    s = np.sqrt(s2)
    g1s = g1_raw / (s * n ** (c_1 / 2.0)) if s > 0 else 0.0
    g2s = g2_raw / (s2 * n ** (c_2 / 2.0)) if s2 > 0 else 0.0
    stat = np.sqrt(0.25 * g1s ** 2 + 0.25 * g2s ** 2)
    p = float(cdf_050(stat))
    return bool(p < ALPHA)

def main():
    print("Cargando JSON base...")
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    c_1 = DEFAULT_SCALING_EXPONENTS[1]
    c_2 = DEFAULT_SCALING_EXPONENTS[2]

    cdfs = {}
    for n in N_GRID:
        print(f"Construyendo CDF n={n}...")
        cdfs[n] = build_null_cdf((0.1, 0.1), R=0.50, n=n, N_cal=50000, seed=42)

    # 1. Pure RW
    print("\n--- Evaluando Test Propuesto bajo Pure RW ---")
    for n in N_GRID:
        n_key = str(n)
        seed_base = 100000 + n * 100
        tau_1 = max(2, min(int(round(0.1 * n)), n // 2))
        tau_2 = max(2, min(int(round(0.1 * n)), n // 2))
        cdf = cdfs[n]

        t0 = time.time()
        def worker(i):
            rng = np.random.default_rng(seed_base + i)
            y = generate_rw_pure(n, rng)
            return evaluate_ours(y, n, cdf, c_1, c_2, tau_1, tau_2)

        rejs = Parallel(n_jobs=12, batch_size=100)(delayed(worker)(i) for i in range(N_SIM))
        rej_count = sum(rejs)
        rate = rej_count / N_SIM
        ci = clopper_pearson_ci(rej_count, N_SIM, ALPHA)
        elapsed = time.time() - t0

        data["size_control"]["pure_rw"][n_key]["ours_size"] = float(round(rate, 4))
        data["size_control"]["pure_rw"][n_key]["ours_ci"] = list(ci)
        data["size_control"]["pure_rw"][n_key]["ours_rejections"] = int(rej_count)
        data["size_control"]["pure_rw"][n_key]["ours_n_sim"] = int(N_SIM)
        data["size_control"]["pure_rw"][n_key]["ours_elapsed_sec"] = round(elapsed, 2)
        print(f"  Pure RW n={n}: ours_size={rate:.4f} {ci} ({rej_count}/{N_SIM}) in {elapsed:.1f}s")

    # 2. Break RW
    print("\n--- Evaluando Test Propuesto bajo Break RW (Delta=1.0) ---")
    for n in N_GRID:
        n_key = str(n)
        seed_base = 150000 + n * 100
        tau_1 = max(2, min(int(round(0.1 * n)), n // 2))
        tau_2 = max(2, min(int(round(0.1 * n)), n // 2))
        cdf = cdfs[n]

        t0 = time.time()
        def worker(i):
            rng = np.random.default_rng(seed_base + i)
            y = generate_rw_break_mean(n, 1.0, rng)
            return evaluate_ours(y, n, cdf, c_1, c_2, tau_1, tau_2)

        rejs = Parallel(n_jobs=12, batch_size=100)(delayed(worker)(i) for i in range(N_SIM))
        rej_count = sum(rejs)
        rate = rej_count / N_SIM
        ci = clopper_pearson_ci(rej_count, N_SIM, ALPHA)
        elapsed = time.time() - t0

        data["size_control"]["break_rw"][n_key]["ours_size"] = float(round(rate, 4))
        data["size_control"]["break_rw"][n_key]["ours_ci"] = list(ci)
        data["size_control"]["break_rw"][n_key]["ours_rejections"] = int(rej_count)
        data["size_control"]["break_rw"][n_key]["ours_n_sim"] = int(N_SIM)
        data["size_control"]["break_rw"][n_key]["ours_elapsed_sec"] = round(elapsed, 2)
        print(f"  Break RW n={n}: ours_size={rate:.4f} {ci} ({rej_count}/{N_SIM}) in {elapsed:.1f}s")

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"\nGuardado exitoso en {JSON_PATH}")

if __name__ == "__main__":
    main()
