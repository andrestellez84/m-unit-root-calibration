"""
Extend DGP 1 with DF-GLS baseline.

Runs the same DGP1 grid (rho x n x N_sim=5000) with identical seeds,
computes DF-GLS rejection rates with binomial CI, merges into existing
power_comparison_dgp1.json, and regenerates dgp1_power_curves.pdf.

Usage:
    python experiments/extend_dgp1_dfgls.py
"""

import sys
import os
import json
import time
import warnings
from datetime import datetime

import numpy as np
from scipy.stats import norm

warnings.filterwarnings("ignore", category=UserWarning)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from arch.unitroot import DFGLS

# ======================================================================
# Configuration (identical to power_comparison.py)
# ======================================================================
ALPHA = 0.05
N_SIM = 5000
N_GRID = [200, 500, 1000]
DGP1_RHOS = [0.80, 0.85, 0.90, 0.93, 0.95, 0.97, 0.99, 1.00]

RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')
FIGURES_DIR = os.path.join(os.path.dirname(__file__), '..', 'supplementary', 'figures')


def generate_ar1(n, rho, sigma=1.0, rng=None):
    """Generate AR(1): Y_t = rho * Y_{t-1} + eps_t."""
    if rng is None:
        rng = np.random.default_rng()
    eps = rng.standard_normal(n) * sigma
    Y = np.empty(n + 1)
    Y[0] = 0.0
    for t in range(n):
        Y[t + 1] = rho * Y[t] + eps[t]
    return Y


def run_dfgls(Y):
    """Run DF-GLS test (lags by AIC, trend='c'). Returns p-value."""
    try:
        result = DFGLS(Y, trend='c')
        return result.pvalue
    except Exception:
        return 1.0  # fail-safe


def ci_95_binomial(p_hat, n_sim):
    """Wilson score 95% CI half-width for binomial proportion."""
    z = 1.96
    denom = 1 + z**2 / n_sim
    center = (p_hat + z**2 / (2 * n_sim)) / denom
    width = z * np.sqrt(p_hat * (1 - p_hat) / n_sim + z**2 / (4 * n_sim**2)) / denom
    return float(center - width), float(center + width)


def main():
    print("=" * 70)
    print("  DGP 1 Extension: Adding DF-GLS baseline")
    print(f"  rho in {DGP1_RHOS}")
    print(f"  n in {N_GRID}, N_sim={N_SIM}")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # Load existing results
    results_path = os.path.join(RESULTS_DIR, 'power_comparison_dgp1.json')
    with open(results_path) as f:
        all_results = json.load(f)

    dgp1 = all_results['dgp1']
    total = len(DGP1_RHOS) * len(N_GRID)
    idx = 0

    for n in N_GRID:
        n_key = str(n)
        for rho in DGP1_RHOS:
            idx += 1
            rho_key = str(rho)
            t0 = time.perf_counter()

            # Same seed as power_comparison.py
            seed_base = 100000 + n * 100 + int(rho * 100)
            rej_dfgls = 0

            for i in range(N_SIM):
                rng = np.random.default_rng(seed_base + i)
                Y = generate_ar1(n=n, rho=rho, rng=rng)
                if run_dfgls(Y) < ALPHA:
                    rej_dfgls += 1

            rate = rej_dfgls / N_SIM
            ci_lo, ci_hi = ci_95_binomial(rate, N_SIM)
            elapsed = time.perf_counter() - t0

            # Merge into existing cell
            dgp1[n_key][rho_key]['dfgls'] = rate
            dgp1[n_key][rho_key]['dfgls_ci_lo'] = ci_lo
            dgp1[n_key][rho_key]['dfgls_ci_hi'] = ci_hi

            # Also add CIs for existing tests if not present
            for test_key in ['ours_R050', 'adf', 'pp', 'kpss_rej']:
                if test_key in dgp1[n_key][rho_key]:
                    val = dgp1[n_key][rho_key][test_key]
                    lo, hi = ci_95_binomial(val, N_SIM)
                    dgp1[n_key][rho_key][f'{test_key}_ci_lo'] = lo
                    dgp1[n_key][rho_key][f'{test_key}_ci_hi'] = hi

            print(f"  [{idx:2d}/{total}] n={n:4d}, rho={rho:.2f}: "
                  f"DFGLS={rate:.3f} [{ci_lo:.3f}, {ci_hi:.3f}]  "
                  f"ADF={dgp1[n_key][rho_key]['adf']:.3f}  "
                  f"PP={dgp1[n_key][rho_key]['pp']:.3f}  "
                  f"Ours={dgp1[n_key][rho_key]['ours_R050']:.3f}  "
                  f"({elapsed:.1f}s)")

    # Save merged results
    all_results['dgp1'] = dgp1
    all_results['dfgls_extension'] = {
        'completed_at': datetime.utcnow().isoformat(),
        'n_sim': N_SIM,
        'alpha': ALPHA,
    }

    with open(results_path, 'w') as f:
        json.dump(all_results, f, indent=2)
    print(f"\n  Results saved to: {results_path}")

    # Print comparison table
    print(f"\n{'=' * 70}")
    print("  KEY COMPARISONS")
    print(f"{'=' * 70}")

    for rho, n in [(0.97, 500), (0.99, 1000)]:
        cell = dgp1[str(n)][str(rho)]
        print(f"\n  (rho={rho}, n={n}):")
        print(f"    Ours(R050): {cell['ours_R050']:.3f} "
              f"[{cell.get('ours_R050_ci_lo', '?'):.3f}, "
              f"{cell.get('ours_R050_ci_hi', '?'):.3f}]")
        print(f"    DF-GLS:     {cell['dfgls']:.3f} "
              f"[{cell['dfgls_ci_lo']:.3f}, {cell['dfgls_ci_hi']:.3f}]")
        print(f"    ADF:        {cell['adf']:.3f} "
              f"[{cell.get('adf_ci_lo', '?'):.3f}, "
              f"{cell.get('adf_ci_hi', '?'):.3f}]")
        print(f"    PP:         {cell['pp']:.3f} "
              f"[{cell.get('pp_ci_lo', '?'):.3f}, "
              f"{cell.get('pp_ci_hi', '?'):.3f}]")

    # Regenerate figure
    print(f"\n  Regenerating DGP1 figure with DF-GLS curve...")
    plot_dgp1_extended(dgp1)
    print(f"\n{'=' * 70}")
    print(f"  DONE.")
    print(f"{'=' * 70}")


def plot_dgp1_extended(dgp1_data):
    """Plot DGP1 power curves including DF-GLS."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    plt.rcParams.update({
        'font.size': 11,
        'axes.labelsize': 12,
        'axes.titlesize': 13,
        'legend.fontsize': 10,
        'figure.dpi': 150,
    })

    rhos = DGP1_RHOS
    n_values = N_GRID

    def ci_hw(p_hat):
        """Binomial CI half-width for shading."""
        return 1.96 * np.sqrt(p_hat * (1 - p_hat) / N_SIM)

    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)

    for ax_idx, n in enumerate(n_values):
        ax = axes[ax_idx]
        n_data = dgp1_data[str(n)]

        ours = np.array([n_data[str(rho)]['ours_R050'] for rho in rhos])
        adf = np.array([n_data[str(rho)]['adf'] for rho in rhos])
        pp = np.array([n_data[str(rho)]['pp'] for rho in rhos])
        dfgls = np.array([n_data[str(rho)]['dfgls'] for rho in rhos])

        # CI bands
        for arr, color in [(ours, 'black'), (adf, 'red'),
                           (pp, 'blue'), (dfgls, '#2ca02c')]:
            hw = ci_hw(arr)
            ax.fill_between(rhos, arr - hw, arr + hw,
                            color=color, alpha=0.08)

        # Lines
        ax.plot(rhos, ours, 'k-o', linewidth=2.0, markersize=6,
                label=r'$\tilde{g}_{0.5}^{\boldsymbol{\theta}}$', zorder=5)
        ax.plot(rhos, dfgls, '-s', color='#2ca02c', linewidth=1.8,
                markersize=5, label='DF-GLS', alpha=0.85, zorder=4)
        ax.plot(rhos, adf, 'r-D', linewidth=1.5, markersize=5,
                label='ADF', alpha=0.8)
        ax.plot(rhos, pp, 'b-+', linewidth=1.5, markersize=7,
                label='PP', alpha=0.8)

        # Nominal size
        ax.axhline(y=0.05, color='gray', linestyle=':', alpha=0.6,
                   linewidth=1)

        ax.set_xlabel(r'$\rho$')
        ax.set_title(f'$n = {n}$')
        ax.set_xlim(0.78, 1.02)
        ax.set_ylim(-0.02, 1.05)
        ax.invert_xaxis()

        if ax_idx == 0:
            ax.set_ylabel('Rejection rate')
            ax.legend(loc='upper right', framealpha=0.9)

    fig.suptitle(
        r'DGP 1: Near-unit-root AR(1) $Y_t = \rho\,Y_{t-1} + \varepsilon_t$',
        fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()

    os.makedirs(FIGURES_DIR, exist_ok=True)
    fig.savefig(os.path.join(FIGURES_DIR, 'dgp1_power_curves.pdf'),
                bbox_inches='tight')
    fig.savefig(os.path.join(FIGURES_DIR, 'dgp1_power_curves.png'),
                bbox_inches='tight', dpi=200)
    print("    DGP1 figure saved (with DF-GLS).")
    plt.close(fig)


if __name__ == '__main__':
    main()
