"""
Auditoría A6 — Experimento 1: Wild Bootstrap (Interoperabilidad R y Alternativa Nativa Python).

Implementación del Autoregressive Wild Bootstrap (AWB / Cavaliere & Taylor 2008, 2009; Smeekes & Urbain 2014)
para contraste con el test propuesto sobre:
  - DGP 3: r in {1, 2, 3, 4} x n in {200, 1000} (8 celdas)
  - DGP 1: rho in {0.95, 0.97, 0.99} x n in {200, 500, 1000} (9 celdas)
  - N_sim = 2000 por celda
  - B = 999 (B = 1999 para r=4 y rho=0.99)
  - Intervalos de confianza binomiales exactos (Clopper-Pearson / Wilson).
"""

import sys
import os
import time
import json
import shutil
import subprocess
from datetime import datetime, timezone

import numpy as np
from scipy.stats import beta

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

ALPHA = 0.05
N_SIM = 2000

DGP3_RATIOS = [1.0, 2.0, 3.0, 4.0]
DGP3_N = [200, 1000]

DGP1_RHOS = [0.95, 0.97, 0.99]
DGP1_N = [200, 500, 1000]


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
    return low, high


def fast_dfgls_stat(y: np.ndarray) -> float:
    """
    Fast GLS-detrended Dickey-Fuller statistic (Elliot, Rothenberg, Stock 1996) with p=0.
    """
    n = len(y) - 1
    c_bar = -7.0  # constant case
    a = 1.0 + c_bar / n

    # Quasi-difference y and x
    y_tilde = np.empty(n + 1)
    y_tilde[0] = y[0]
    y_tilde[1:] = y[1:] - a * y[:-1]

    x_tilde = np.empty(n + 1)
    x_tilde[0] = 1.0
    x_tilde[1:] = 1.0 - a

    # OLS of y_tilde on x_tilde
    beta_gls = np.sum(y_tilde * x_tilde) / np.sum(x_tilde ** 2)
    y_d = y - beta_gls

    # DF regression on detrended data: Delta y_d on y_d_{t-1}
    dy_d = np.diff(y_d)
    y_lag = y_d[:-1]

    denom = np.sum(y_lag ** 2)
    if denom <= 1e-12:
        return 0.0
    phi = np.sum(dy_d * y_lag) / denom
    res = dy_d - phi * y_lag
    s2 = np.sum(res ** 2) / max(len(dy_d) - 1, 1)
    se = np.sqrt(s2 / denom)
    return float(phi / se) if se > 0 else 0.0


def wild_bootstrap_dfgls_pvalue(y: np.ndarray, B: int = 999, rng: np.random.Generator = None) -> float:
    """
    Autoregressive Wild Bootstrap (AWB) test for DF-GLS.
    Innovations multiplied by Rademacher variables.
    """
    if rng is None:
        rng = np.random.default_rng()

    stat_orig = fast_dfgls_stat(y)
    dy = np.diff(y)
    n = len(dy)

    # Rademacher weights: +1 or -1 with prob 0.5
    weights = rng.choice([-1.0, 1.0], size=(B, n))
    boot_dy = weights * dy  # shape (B, n)

    count = 0
    y_star = np.empty(n + 1)
    y_star[0] = 0.0

    for b in range(B):
        np.cumsum(boot_dy[b], out=y_star[1:])
        stat_b = fast_dfgls_stat(y_star)
        if stat_b <= stat_orig:
            count += 1

    return float((count + 1) / (B + 1))


def check_r_environment() -> tuple[bool, str]:
    """Check if Rscript and bootUR are available."""
    rscript = shutil.which("Rscript")
    if not rscript:
        return False, "Rscript no encontrado en PATH del sistema."

    try:
        res = subprocess.run(
            [rscript, "-e", "cat(as.character(packageVersion('bootUR')))\n"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if res.returncode == 0:
            return True, f"R disponible. bootUR versión: {res.stdout.strip()}"
        else:
            return False, f"R disponible pero error en bootUR: {res.stderr.strip()}"
    except Exception as e:
        return False, f"Excepción al invocar Rscript: {e}"


def run_wild_bootstrap_audit6(mode: str = "auto", output_path: str = None) -> dict:
    """
    Run wild bootstrap experiment according to Audit A6 specification.
    """
    if output_path is None:
        output_path = os.path.join(RESULTS_DIR, "wild_bootstrap_audit6.json")

    has_r, r_diag = check_r_environment()
    print("=" * 70)
    print("  Auditoría A6: Experimento 1 — Wild Bootstrap Comparator")
    print(f"  Diagnóstico R: {r_diag}")
    print(f"  Modo: {mode}")
    print("=" * 70)

    if mode == "r_only" or (mode == "auto" and has_r):
        if not has_r:
            raise RuntimeError(f"Modo R solicitado pero entorno R no disponible: {r_diag}")
        r_script = os.path.join(os.path.dirname(__file__), "audit6_wild_bootstrap_bootur.R")
        print(f"  Ejecutando script R vía subprocess: {r_script}")
        subprocess.run(["Rscript", r_script, output_path], check=True)
        with open(output_path, "r", encoding="utf-8") as f:
            return json.load(f)

    # Native Python AWB runner
    print("  Ejecutando implementación nativa de Autoregressive Wild Bootstrap (AWB)...")
    results = {
        "metadata": {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "environment": "Python Native AWB (Rademacher)",
            "r_diagnostic": r_diag,
            "alpha": ALPHA,
            "N_sim": N_SIM,
            "grid_dgp3": {"ratios": DGP3_RATIOS, "n": DGP3_N},
            "grid_dgp1": {"rhos": DGP1_RHOS, "n": DGP1_N},
            "lag_order": "fixed (p=0)",
        },
        "dgp3": {},
        "dgp1": {},
    }

    # DGP 3
    print("\n--- DGP 3: Quiebre de Varianza en Paseo Aleatorio ---")
    for n in DGP3_N:
        n_key = str(n)
        results["dgp3"][n_key] = {}
        for r in DGP3_RATIOS:
            r_key = str(r)
            B = 1999 if r == 4.0 else 999
            seed_base = 300000 + n * 100 + int(r * 10)
            t0 = time.perf_counter()

            rejections = 0
            t_break = n // 2

            for i in range(N_SIM):
                rng = np.random.default_rng(seed_base + i)
                eps = rng.standard_normal(n)
                eps[t_break:] *= r
                y = np.empty(n + 1)
                y[0] = 0.0
                np.cumsum(eps, out=y[1:])

                boot_rng = np.random.default_rng(seed_base + 100000 + i)
                pval = wild_bootstrap_dfgls_pvalue(y, B=B, rng=boot_rng)
                if pval < ALPHA:
                    rejections += 1

            rate = rejections / N_SIM
            ci_lo, ci_hi = clopper_pearson_ci(rejections, N_SIM, ALPHA)
            elapsed = time.perf_counter() - t0

            results["dgp3"][n_key][r_key] = {
                "rate": float(rate),
                "ci_lower": float(ci_lo),
                "ci_upper": float(ci_hi),
                "rejections": int(rejections),
                "B": int(B),
                "elapsed_sec": float(round(elapsed, 2)),
            }
            print(f"  [DGP3] n={n:4d}, r={r:.1f}: Size={rate:.4f} [{ci_lo:.4f}, {ci_hi:.4f}] (B={B}, {elapsed:.1f}s)")

    # DGP 1
    print("\n--- DGP 1: AR(1) Persistente (Potencia Local) ---")
    for n in DGP1_N:
        n_key = str(n)
        results["dgp1"][n_key] = {}
        for rho in DGP1_RHOS:
            rho_key = str(rho)
            B = 1999 if rho == 0.99 else 999
            seed_base = 100000 + n * 100 + int(rho * 100)
            t0 = time.perf_counter()

            rejections = 0
            sigma_unc = 1.0 / np.sqrt(1.0 - rho ** 2)

            for i in range(N_SIM):
                rng = np.random.default_rng(seed_base + i)
                y = np.empty(n + 1)
                y[0] = rng.normal(0.0, sigma_unc)
                eps = rng.standard_normal(n)
                for t in range(n):
                    y[t + 1] = rho * y[t] + eps[t]

                boot_rng = np.random.default_rng(seed_base + 100000 + i)
                pval = wild_bootstrap_dfgls_pvalue(y, B=B, rng=boot_rng)
                if pval < ALPHA:
                    rejections += 1

            rate = rejections / N_SIM
            ci_lo, ci_hi = clopper_pearson_ci(rejections, N_SIM, ALPHA)
            elapsed = time.perf_counter() - t0

            results["dgp1"][n_key][rho_key] = {
                "rate": float(rate),
                "ci_lower": float(ci_lo),
                "ci_upper": float(ci_hi),
                "rejections": int(rejections),
                "B": int(B),
                "elapsed_sec": float(round(elapsed, 2)),
            }
            print(f"  [DGP1] n={n:4d}, rho={rho:.2f}: Power={rate:.4f} [{ci_lo:.4f}, {ci_hi:.4f}] (B={B}, {elapsed:.1f}s)")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nResultados guardados exitosamente en: {output_path}")
    return results


if __name__ == "__main__":
    mode = "r_only" if "--r-only" in sys.argv else ("py_only" if "--py-only" in sys.argv else "auto")
    run_wild_bootstrap_audit6(mode=mode)
