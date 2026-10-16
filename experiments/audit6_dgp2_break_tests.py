"""
Auditoría A6 — Componente 1: Tests de Quiebre Estructural sobre DGP 2 y Control de Tamaño.

Contenido:
  Paso 0: Verificación estricta de reproducción de power_comparison_dgp2.json (5,000 series, 0.4028).
  Tarea 1: Zivot-Andrews y Lee-Strazicich (Modelo A) sobre DGP 2 (N_sim=5000, 18 celdas).
  Tarea 2: Control de tamaño de ZA y LS bajo paseo aleatorio puro y paseo aleatorio con quiebre de media (Amendment 4).
"""

import os
import sys
import time
import json
import warnings
from datetime import datetime, timezone

import numpy as np
from scipy.stats import beta
from joblib import Parallel, delayed
from arch.unitroot import ZivotAndrews

# Suppress arch/statsmodels interpolation warnings
warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from stationarity_test.empirical_eigenvalues import build_null_cdf
from stationarity_test.hac_estimator import hac_newey_west
from stationarity_test.utils import rolling_mean, rolling_var, sample_variance_over_k
from stationarity_test.constants import DEFAULT_SCALING_EXPONENTS

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

ALPHA = 0.05
N_SIM = 5000
N_GRID = [200, 500, 1000]
DELTAS = [0.0, 0.5, 1.0, 2.0, 3.0, 5.0]
DGP2_RHO = 0.95
LS_CRITICAL_VALUE_5PCT = -3.566


def clopper_pearson_ci(k: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    """Exact Clopper-Pearson binomial confidence interval."""
    if k == 0:
        low = 0.0
    else:
        low = float(beta.ppf(alpha / 2, k, n - k + 1))
    if k == n:
        high = 1.0
    else:
        high = float(beta.ppf(1 - alpha / 2, k + 1, n - k))
    return float(round(low, 4)), float(round(high, 4))


def generate_ar1_break_mean(n: int, rho: float, delta: float, sigma: float = 1.0, rng=None):
    """
    Generate stationary AR(1) with structural break in mean at midpoint.
    Y[0] = 0.0, length = n + 1.
    """
    if rng is None:
        rng = np.random.default_rng()
    eps = rng.standard_normal(n) * sigma
    t_break = n // 2
    sigma_unc = sigma / np.sqrt(1.0 - rho ** 2)
    mu = delta * sigma_unc
    Y = np.empty(n + 1)
    Y[0] = 0.0
    for t in range(n):
        mu_t = mu if t >= t_break else 0.0
        Y[t + 1] = rho * (Y[t] - mu_t) + mu_t + eps[t]
    return Y


def generate_rw_pure(n: int, sigma: float = 1.0, rng=None):
    """Generate pure random walk under H0."""
    if rng is None:
        rng = np.random.default_rng()
    eps = rng.standard_normal(n) * sigma
    Y = np.empty(n + 1)
    Y[0] = 0.0
    np.cumsum(eps, out=Y[1:])
    return Y


def generate_rw_break_mean(n: int, delta_mu: float = 1.0, sigma: float = 1.0, rng=None):
    """Generate random walk with structural break in mean (level shift) under H0."""
    if rng is None:
        rng = np.random.default_rng()
    eps = rng.standard_normal(n) * sigma
    t_break = n // 2
    # Mean shift of size delta_mu at t_break
    shift = np.zeros(n)
    shift[t_break:] = delta_mu
    eps_shifted = eps + np.diff(np.concatenate(([0.0], shift)))
    Y = np.empty(n + 1)
    Y[0] = 0.0
    np.cumsum(eps_shifted, out=Y[1:])
    return Y


def lee_strazicich_model_a(y: np.ndarray, k_max: int = 4, trim: float = 0.10) -> tuple[float, int]:
    """
    Lee and Strazicich (2004) Minimum LM Unit Root Test with One Structural Break (Model A).

    Deterministic model: Z_t = [1, t, D_t]' where D_t = 1(t >= T_B + 1).
    Step 1: OLS regression of Delta y_t on Delta Z_t = [1, Delta D_t]'
    Step 2: Augmented LM regression of Delta y_t on Delta Z_t, S_lag, and lags of Delta S_tilde.
    General-to-specific lag selection with 10% critical value (1.645).
    Search over T_B in [trim*T, (1-trim)*T] to find minimum LM t-statistic.
    """
    T = len(y)
    dy = np.diff(y)
    N = len(dy)
    t_start = max(int(trim * T), k_max + 2)
    t_end = min(int((1.0 - trim) * T), N - 2)
    sum_dy = np.sum(dy)

    min_t = np.inf
    best_tb = None

    for tb in range(t_start, t_end):
        idx = tb - 1  # Index in dy
        d_val = dy[idx]
        mu_hat = (sum_dy - d_val) / (N - 1)
        d_hat = d_val - mu_hat

        t_vec = np.arange(1, T)
        D_vec = np.zeros(T - 1)
        D_vec[idx:] = 1.0
        S_tilde = np.empty(T)
        S_tilde[0] = 0.0
        S_tilde[1:] = y[1:] - y[0] - mu_hat * t_vec - d_hat * D_vec

        S_lag = S_tilde[:-1]
        dD = np.zeros(N)
        dD[idx] = 1.0
        dS = np.diff(S_tilde)

        # General-to-specific lag selection
        for k in range(k_max, -1, -1):
            eff_N = N - k
            if eff_N <= 4 + k:
                continue
            y_eff = dy[k:]
            cols = [np.ones(eff_N), dD[k:], S_lag[k:]]
            for j in range(1, k + 1):
                cols.append(dS[k - j : N - j])
            X = np.column_stack(cols)

            beta_hat, _, _, _ = np.linalg.lstsq(X, y_eff, rcond=None)
            res = y_eff - X @ beta_hat
            s2 = np.sum(res ** 2) / max(eff_N - X.shape[1], 1)
            inv_xx = np.linalg.inv(X.T @ X)

            if k > 0:
                se_last = np.sqrt(s2 * inv_xx[-1, -1])
                t_last = beta_hat[-1] / se_last if se_last > 0 else 0.0
                if abs(t_last) >= 1.645:
                    se_phi = np.sqrt(s2 * inv_xx[2, 2])
                    final_t = beta_hat[2] / se_phi if se_phi > 0 else 0.0
                    break
            else:
                se_phi = np.sqrt(s2 * inv_xx[2, 2])
                final_t = beta_hat[2] / se_phi if se_phi > 0 else 0.0
                break

        if final_t < min_t:
            min_t = final_t
            best_tb = tb

    return float(min_t), int(best_tb if best_tb is not None else 0)


def evaluate_single_series(y: np.ndarray, k_max: int = 4) -> dict:
    """Evaluate Zivot-Andrews and Lee-Strazicich on a single series."""
    # Zivot-Andrews with intercept break (trend='c')
    try:
        za = ZivotAndrews(y, trend="c")
        za_rej = bool(za.pvalue < ALPHA)
        za_stat = float(za.stat)
        za_pval = float(za.pvalue)
    except Exception:
        za_rej = False
        za_stat = 0.0
        za_pval = 1.0

    # Lee-Strazicich Model A
    try:
        ls_stat, ls_tb = lee_strazicich_model_a(y, k_max=k_max)
        ls_rej = bool(ls_stat < LS_CRITICAL_VALUE_5PCT)
    except Exception:
        ls_rej = False
        ls_stat = 0.0
        ls_tb = 0

    return {
        "za_rej": za_rej,
        "za_stat": za_stat,
        "za_pval": za_pval,
        "ls_rej": ls_rej,
        "ls_stat": ls_stat,
        "ls_tb": ls_tb,
    }


def step0_verify_reproduction() -> dict:
    """
    Paso 0: Verificar que la semilla y pipeline reproducen exactamente
    power_comparison_dgp2.json al cuarto decimal.
    """
    print("\n" + "=" * 70)
    print("  PASO 0: Verificación de Reproducción de power_comparison_dgp2.json")
    print("=" * 70)

    json_path = os.path.join(RESULTS_DIR, "power_comparison_dgp2.json")
    with open(json_path, "r", encoding="utf-8") as f:
        stored_data = json.load(f)["dgp2"]

    target_cell = stored_data["200"]["0.0"]
    expected_rate = target_cell["ours_R050"]

    # Precalibrate null CDF (R=0.50, n=200, N_cal=50000, seed=42)
    t0 = time.time()
    cdf_050 = build_null_cdf((0.1, 0.1), 0.50, 200, N_cal=50000, seed=42)
    t_cal = time.time() - t0
    print(f"  CDF R=0.50 n=200 calibrada en {t_cal:.2f}s")

    # Run cell with 200 series first (demonstration check)
    n = 200
    delta = 0.0
    seed_base = 200000 + n * 100 + int(delta * 10)
    c_1 = DEFAULT_SCALING_EXPONENTS[1]
    c_2 = DEFAULT_SCALING_EXPONENTS[2]
    tau_1 = max(2, min(int(round(0.1 * n)), n // 2))
    tau_2 = max(2, min(int(round(0.1 * n)), n // 2))

    rejections_200 = 0
    for i in range(200):
        rng = np.random.default_rng(seed_base + i)
        Y = generate_ar1_break_mean(n=n, rho=DGP2_RHO, delta=delta, rng=rng)
        means = rolling_mean(Y, tau_1)
        g1_raw = float(np.sqrt(max(sample_variance_over_k(means), 0.0)))
        variances = rolling_var(Y, tau_2)
        g2_raw = float(np.sqrt(max(sample_variance_over_k(variances), 0.0)))
        diffs = np.diff(Y)
        s2 = hac_newey_west(diffs, andrews_pilot="alpha2")
        s = np.sqrt(s2)
        g1s = g1_raw / (s * n ** (c_1 / 2.0)) if s > 0 else 0.0
        g2s = g2_raw / (s2 * n ** (c_2 / 2.0)) if s2 > 0 else 0.0
        stat = np.sqrt(0.25 * g1s ** 2 + 0.25 * g2s ** 2)
        p = float(cdf_050(stat))
        if p < ALPHA:
            rejections_200 += 1

    rate_200 = rejections_200 / 200
    print(f"  Muestra previa 200 series: {rejections_200}/200 = {rate_200:.4f}")

    # Run full cell 5,000 series
    rejections_5000 = rejections_200
    for i in range(200, 5000):
        rng = np.random.default_rng(seed_base + i)
        Y = generate_ar1_break_mean(n=n, rho=DGP2_RHO, delta=delta, rng=rng)
        means = rolling_mean(Y, tau_1)
        g1_raw = float(np.sqrt(max(sample_variance_over_k(means), 0.0)))
        variances = rolling_var(Y, tau_2)
        g2_raw = float(np.sqrt(max(sample_variance_over_k(variances), 0.0)))
        diffs = np.diff(Y)
        s2 = hac_newey_west(diffs, andrews_pilot="alpha2")
        s = np.sqrt(s2)
        g1s = g1_raw / (s * n ** (c_1 / 2.0)) if s > 0 else 0.0
        g2s = g2_raw / (s2 * n ** (c_2 / 2.0)) if s2 > 0 else 0.0
        stat = np.sqrt(0.25 * g1s ** 2 + 0.25 * g2s ** 2)
        p = float(cdf_050(stat))
        if p < ALPHA:
            rejections_5000 += 1

    rate_5000 = rejections_5000 / 5000
    diff = abs(rate_5000 - expected_rate)
    print(f"  Cómputo 5,000 series: {rejections_5000}/5000 = {rate_5000:.4f}")
    print(f"  Esperado en JSON:     {expected_rate:.4f}")
    print(f"  Diferencia absoluta:  {diff:.6f}")

    if diff > 1e-4:
        raise RuntimeError(
            f"FALLO DE REPRODUCIBILIDAD EN PASO 0: obtenido {rate_5000:.4f}, esperado {expected_rate:.4f}"
        )
    print("  >> PASO 0 VERIFICADO: REPRODUCCIÓN EXACTA AL CUARTO DECIMAL (PASS)\n")

    return {
        "status": "PASS",
        "rate_200": rate_200,
        "rate_5000": rate_5000,
        "expected_rate": expected_rate,
        "diff": diff,
        "formula": "seed_base = 200000 + n * 100 + int(delta * 10)",
    }


def run_experiment_dgp2_breaks(n_jobs: int = 12) -> dict:
    """Run ZA and LS over DGP 2 grid, paired with existing baselines."""
    print("=" * 70)
    print("  TAREA 1: Zivot-Andrews y Lee-Strazicich sobre DGP 2")
    print(f"  n in {N_GRID}, deltas in {DELTAS}, N_sim={N_SIM}, cores={n_jobs}")
    print("=" * 70)

    json_path = os.path.join(RESULTS_DIR, "power_comparison_dgp2.json")
    with open(json_path, "r", encoding="utf-8") as f:
        existing_dgp2 = json.load(f)["dgp2"]

    results = {}

    for n in N_GRID:
        n_key = str(n)
        results[n_key] = {}

        for delta in DELTAS:
            d_key = str(delta)
            seed_base = 200000 + n * 100 + int(delta * 10)
            t0 = time.perf_counter()

            # Pre-generate series to ensure exact RNG sequence
            def worker(i):
                rng = np.random.default_rng(seed_base + i)
                y = generate_ar1_break_mean(n=n, rho=DGP2_RHO, delta=delta, rng=rng)
                return evaluate_single_series(y, k_max=4)

            cell_res = Parallel(n_jobs=n_jobs, batch_size=50)(
                delayed(worker)(i) for i in range(N_SIM)
            )

            za_rej = sum(1 for r in cell_res if r["za_rej"])
            ls_rej = sum(1 for r in cell_res if r["ls_rej"])

            za_rate = za_rej / N_SIM
            ls_rate = ls_rej / N_SIM

            za_ci = clopper_pearson_ci(za_rej, N_SIM, ALPHA)
            ls_ci = clopper_pearson_ci(ls_rej, N_SIM, ALPHA)
            elapsed = time.perf_counter() - t0

            # Baseline comparisons from stored JSON
            base_cell = existing_dgp2[n_key][d_key]
            ours_rate = base_cell["ours_R050"]
            adf_rate = base_cell["adf"]
            pp_rate = base_cell["pp"]
            dfgls_rate = base_cell.get("dfgls", np.nan)

            results[n_key][d_key] = {
                "za_power": float(round(za_rate, 4)),
                "za_ci": list(za_ci),
                "ls_power": float(round(ls_rate, 4)),
                "ls_ci": list(ls_ci),
                "ours_R050": float(ours_rate),
                "adf": float(adf_rate),
                "pp": float(pp_rate),
                "dfgls": float(dfgls_rate),
                "elapsed_sec": float(round(elapsed, 2)),
            }

            print(
                f"  n={n:4d}, delta={delta:3.1f}: "
                f"ZA={za_rate:.4f} {za_ci} | LS={ls_rate:.4f} {ls_ci} | "
                f"Ours={ours_rate:.4f} | DF-GLS={dfgls_rate:.4f} ({elapsed:.1f}s)"
            )

    return results


def run_size_control_breaks(n_jobs: int = 12) -> dict:
    """
    Tarea 2 (Amendment 4): Control de tamaño de ZA y LS bajo paseo aleatorio
    puro y paseo aleatorio con quiebre de media (5,000 réplicas).
    """
    print("\n" + "=" * 70)
    print("  TAREA 2 (Amendment 4): Control de Tamaño de ZA y LS bajo H0")
    print(f"  H0_1: Paseo aleatorio puro | H0_2: Paseo aleatorio con quiebre de media (Delta=1.0)")
    print(f"  n in {N_GRID}, N_sim={N_SIM}, cores={n_jobs}")
    print("=" * 70)

    size_results = {
        "pure_rw": {},
        "break_rw": {},
    }

    # 1. Pure Random Walk
    print("\n--- H0: Paseo Aleatorio Puro ---")
    for n in N_GRID:
        n_key = str(n)
        seed_base = 100000 + n * 100
        t0 = time.perf_counter()

        def worker_pure(i):
            rng = np.random.default_rng(seed_base + i)
            y = generate_rw_pure(n=n, rng=rng)
            return evaluate_single_series(y, k_max=4)

        cell_res = Parallel(n_jobs=n_jobs, batch_size=50)(
            delayed(worker_pure)(i) for i in range(N_SIM)
        )

        za_rej = sum(1 for r in cell_res if r["za_rej"])
        ls_rej = sum(1 for r in cell_res if r["ls_rej"])

        za_rate = za_rej / N_SIM
        ls_rate = ls_rej / N_SIM
        za_ci = clopper_pearson_ci(za_rej, N_SIM, ALPHA)
        ls_ci = clopper_pearson_ci(ls_rej, N_SIM, ALPHA)
        elapsed = time.perf_counter() - t0

        size_results["pure_rw"][n_key] = {
            "za_size": float(round(za_rate, 4)),
            "za_ci": list(za_ci),
            "ls_size": float(round(ls_rate, 4)),
            "ls_ci": list(ls_ci),
            "elapsed_sec": float(round(elapsed, 2)),
        }
        print(f"  [Pure RW]  n={n:4d}: ZA={za_rate:.4f} {za_ci} | LS={ls_rate:.4f} {ls_ci} ({elapsed:.1f}s)")

    # 2. Random Walk with Mean Break
    print("\n--- H0: Paseo Aleatorio con Quiebre de Media (Delta=1.0) ---")
    for n in N_GRID:
        n_key = str(n)
        seed_base = 150000 + n * 100
        t0 = time.perf_counter()

        def worker_break(i):
            rng = np.random.default_rng(seed_base + i)
            y = generate_rw_break_mean(n=n, delta_mu=1.0, rng=rng)
            return evaluate_single_series(y, k_max=4)

        cell_res = Parallel(n_jobs=n_jobs, batch_size=50)(
            delayed(worker_break)(i) for i in range(N_SIM)
        )

        za_rej = sum(1 for r in cell_res if r["za_rej"])
        ls_rej = sum(1 for r in cell_res if r["ls_rej"])

        za_rate = za_rej / N_SIM
        ls_rate = ls_rej / N_SIM
        za_ci = clopper_pearson_ci(za_rej, N_SIM, ALPHA)
        ls_ci = clopper_pearson_ci(ls_rej, N_SIM, ALPHA)
        elapsed = time.perf_counter() - t0

        size_results["break_rw"][n_key] = {
            "za_size": float(round(za_rate, 4)),
            "za_ci": list(za_ci),
            "ls_size": float(round(ls_rate, 4)),
            "ls_ci": list(ls_ci),
            "elapsed_sec": float(round(elapsed, 2)),
        }
        print(f"  [Break RW] n={n:4d}: ZA={za_rate:.4f} {za_ci} | LS={ls_rate:.4f} {ls_ci} ({elapsed:.1f}s)")

    return size_results


def main():
    t_global = time.time()

    # Paso 0: Verificación estricta
    step0_res = step0_verify_reproduction()

    # Tarea 1: DGP 2 breaks
    dgp2_res = run_experiment_dgp2_breaks(n_jobs=12)

    # Tarea 2: Control de tamaño ZA y LS
    size_res = run_size_control_breaks(n_jobs=12)

    payload = {
        "metadata": {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "n_sim": N_SIM,
            "alpha": ALPHA,
            "dgp2_rho": DGP2_RHO,
            "deltas": DELTAS,
            "n_grid": N_GRID,
            "ls_critical_value_5pct": LS_CRITICAL_VALUE_5PCT,
            "step0_reproduction": step0_res,
        },
        "dgp2_power": dgp2_res,
        "size_control": size_res,
        "elapsed_total_sec": float(round(time.time() - t_global, 2)),
    }

    out_file = os.path.join(RESULTS_DIR, "dgp2_break_tests_audit6.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"\n======================================================================")
    print(f"  Resultados completos guardados en: {out_file}")
    print(f"  Tiempo total: {payload['elapsed_total_sec']:.1f}s")
    print(f"======================================================================\n")


if __name__ == "__main__":
    main()
