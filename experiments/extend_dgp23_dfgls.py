"""
Extend DGP 2 and DGP 3 with DF-GLS baseline.

Uses identical seeds, grid, and N_sim as power_comparison.py.
Merges dfgls/CI columns into existing JSONs and regenerates figures.
"""

import sys, os, json, time, warnings
from datetime import datetime
import numpy as np

warnings.filterwarnings("ignore", category=UserWarning)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from arch.unitroot import DFGLS

# ======================================================================
# Config (must match power_comparison.py exactly)
# ======================================================================
ALPHA = 0.05
N_SIM = 5000
N_GRID = [200, 500, 1000]

DGP2_RHO = 0.95
DGP2_DELTAS = [0.0, 0.5, 1.0, 2.0, 3.0, 5.0]
DGP3_RATIOS = [1.0, 1.5, 2.0, 2.5, 3.0, 4.0]

RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')
FIGURES_DIR = os.path.join(os.path.dirname(__file__), '..', 'supplementary', 'figures')


# ======================================================================
# DGP generators (copied from power_comparison.py for exact match)
# ======================================================================

def generate_ar1_break_mean(n, rho, delta, sigma=1.0, rng=None):
    if rng is None:
        rng = np.random.default_rng()
    eps = rng.standard_normal(n) * sigma
    t_break = n // 2
    sigma_unc = sigma / np.sqrt(1 - rho ** 2)
    mu = delta * sigma_unc
    Y = np.empty(n + 1)
    Y[0] = 0.0
    for t in range(n):
        mu_t = mu if t >= t_break else 0.0
        Y[t + 1] = rho * (Y[t] - mu_t) + mu_t + eps[t]
    return Y


def generate_rw_break_variance(n, ratio, sigma1=1.0, rng=None):
    if rng is None:
        rng = np.random.default_rng()
    t_break = n // 2
    sigma2 = sigma1 * ratio
    eps = np.empty(n)
    eps[:t_break] = rng.standard_normal(t_break) * sigma1
    eps[t_break:] = rng.standard_normal(n - t_break) * sigma2
    Y = np.empty(n + 1)
    Y[0] = 0.0
    Y[1:] = np.cumsum(eps)
    return Y


def run_dfgls(Y):
    try:
        return DFGLS(Y, trend='c').pvalue
    except Exception:
        return 1.0


def ci_wilson(p_hat, n):
    z = 1.96
    denom = 1 + z**2 / n
    center = (p_hat + z**2 / (2 * n)) / denom
    width = z * np.sqrt(p_hat * (1 - p_hat) / n + z**2 / (4 * n**2)) / denom
    return round(float(center - width), 4), round(float(center + width), 4)


def add_cis(cell, n_sim):
    """Add Wilson CIs for all existing rate fields."""
    for key in list(cell.keys()):
        if key.endswith('_ci_lo') or key.endswith('_ci_hi'):
            continue
        if isinstance(cell[key], (int, float)) and 0 <= cell[key] <= 1:
            if key not in ('R', 'rho', 'delta', 'ratio'):
                lo, hi = ci_wilson(cell[key], n_sim)
                cell[f'{key}_ci_lo'] = lo
                cell[f'{key}_ci_hi'] = hi


# ======================================================================
# DGP 2 Extension
# ======================================================================

def extend_dgp2():
    print(f"\n{'=' * 70}")
    print("  DGP 2 Extension: Adding DF-GLS")
    print(f"  rho={DGP2_RHO}, delta in {DGP2_DELTAS}")
    print(f"  n in {N_GRID}, N_sim={N_SIM}")
    print(f"{'=' * 70}")

    path = os.path.join(RESULTS_DIR, 'power_comparison_dgp2.json')
    with open(path) as f:
        all_data = json.load(f)
    dgp2 = all_data['dgp2']

    total = len(DGP2_DELTAS) * len(N_GRID)
    idx = 0

    for n in N_GRID:
        n_key = str(n)
        for delta in DGP2_DELTAS:
            idx += 1
            d_key = str(delta)
            seed_base = 200000 + n * 100 + int(delta * 10)
            t0 = time.perf_counter()

            rej = 0
            for i in range(N_SIM):
                rng = np.random.default_rng(seed_base + i)
                Y = generate_ar1_break_mean(n=n, rho=DGP2_RHO, delta=delta, rng=rng)
                if run_dfgls(Y) < ALPHA:
                    rej += 1

            rate = rej / N_SIM
            lo, hi = ci_wilson(rate, N_SIM)
            elapsed = time.perf_counter() - t0

            dgp2[n_key][d_key]['dfgls'] = rate
            dgp2[n_key][d_key]['dfgls_ci_lo'] = lo
            dgp2[n_key][d_key]['dfgls_ci_hi'] = hi
            add_cis(dgp2[n_key][d_key], N_SIM)

            ours = dgp2[n_key][d_key]['ours_R050']
            adf = dgp2[n_key][d_key]['adf']
            print(f"  [{idx:2d}/{total}] n={n:4d}, d={delta:.1f}: "
                  f"DFGLS={rate:.3f} [{lo:.3f},{hi:.3f}]  "
                  f"Ours={ours:.3f}  ADF={adf:.3f}  ({elapsed:.1f}s)")

    all_data['dgp2'] = dgp2
    all_data['dfgls_extension'] = {'completed_at': datetime.utcnow().isoformat()}
    with open(path, 'w') as f:
        json.dump(all_data, f, indent=2)
    print(f"  Saved: {path}")

    # Key comparisons
    print(f"\n  === DGP2: Ours vs DF-GLS at delta in {{0.5, 1.0, 2.0}} ===")
    for delta in [0.5, 1.0, 2.0]:
        d_key = str(delta)
        for n in N_GRID:
            c = dgp2[str(n)][d_key]
            print(f"    d={delta}, n={n}: Ours={c['ours_R050']:.3f}  "
                  f"DFGLS={c['dfgls']:.3f}  ADF={c['adf']:.3f}  PP={c['pp']:.3f}")

    return dgp2


# ======================================================================
# DGP 3 Extension
# ======================================================================

def extend_dgp3():
    print(f"\n{'=' * 70}")
    print("  DGP 3 Extension: Adding DF-GLS")
    print(f"  ratio in {DGP3_RATIOS}")
    print(f"  n in {N_GRID}, N_sim={N_SIM}")
    print(f"{'=' * 70}")

    path = os.path.join(RESULTS_DIR, 'power_comparison_dgp3.json')
    with open(path) as f:
        all_data = json.load(f)
    dgp3 = all_data['dgp3']

    total = len(DGP3_RATIOS) * len(N_GRID)
    idx = 0

    for n in N_GRID:
        n_key = str(n)
        for ratio in DGP3_RATIOS:
            idx += 1
            r_key = str(ratio)
            seed_base = 300000 + n * 100 + int(ratio * 10)
            t0 = time.perf_counter()

            rej = 0
            for i in range(N_SIM):
                rng = np.random.default_rng(seed_base + i)
                Y = generate_rw_break_variance(n=n, ratio=ratio, rng=rng)
                if run_dfgls(Y) < ALPHA:
                    rej += 1

            rate = rej / N_SIM
            lo, hi = ci_wilson(rate, N_SIM)
            elapsed = time.perf_counter() - t0

            dgp3[n_key][r_key]['dfgls'] = rate
            dgp3[n_key][r_key]['dfgls_ci_lo'] = lo
            dgp3[n_key][r_key]['dfgls_ci_hi'] = hi
            add_cis(dgp3[n_key][r_key], N_SIM)

            ours = dgp3[n_key][r_key]['ours_R050']
            print(f"  [{idx:2d}/{total}] n={n:4d}, r={ratio:.1f}: "
                  f"DFGLS={rate:.3f} [{lo:.3f},{hi:.3f}]  "
                  f"Ours={ours:.3f}  ({elapsed:.1f}s)")

    all_data['dgp3'] = dgp3
    all_data['dfgls_extension'] = {'completed_at': datetime.utcnow().isoformat()}
    with open(path, 'w') as f:
        json.dump(all_data, f, indent=2)
    print(f"  Saved: {path}")

    # Check if DF-GLS is flat ~0.05
    print(f"\n  === DGP3: Is DF-GLS flat at ~0.05? ===")
    for n in N_GRID:
        vals = [dgp3[str(n)][str(r)]['dfgls'] for r in DGP3_RATIOS]
        print(f"    n={n}: {['%.3f' % v for v in vals]}  "
              f"mean={np.mean(vals):.3f}  range=[{min(vals):.3f},{max(vals):.3f}]")

    return dgp3


# ======================================================================
# Figures
# ======================================================================

def plot_figures(dgp2_data, dgp3_data):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    plt.rcParams.update({
        'font.size': 11, 'axes.labelsize': 12,
        'axes.titlesize': 13, 'legend.fontsize': 9,
        'figure.dpi': 150,
    })

    def ci_hw(p):
        return 1.96 * np.sqrt(p * (1 - p) / N_SIM)

    os.makedirs(FIGURES_DIR, exist_ok=True)

    # --- DGP 2 ---
    deltas = DGP2_DELTAS
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)
    for ax_idx, n in enumerate(N_GRID):
        ax = axes[ax_idx]
        nd = dgp2_data[str(n)]
        ours = np.array([nd[str(d)]['ours_R050'] for d in deltas])
        adf = np.array([nd[str(d)]['adf'] for d in deltas])
        pp = np.array([nd[str(d)]['pp'] for d in deltas])
        dfgls = np.array([nd[str(d)]['dfgls'] for d in deltas])

        for arr, c in [(ours, 'black'), (adf, 'red'),
                       (pp, 'blue'), (dfgls, '#2ca02c')]:
            ax.fill_between(deltas, arr - ci_hw(arr), arr + ci_hw(arr),
                            color=c, alpha=0.08)

        ax.plot(deltas, ours, 'k-o', lw=2, ms=6,
                label=r'$\tilde{g}_{0.5}^{\boldsymbol{\theta}}$', zorder=5)
        ax.plot(deltas, dfgls, '-s', color='#2ca02c', lw=1.8, ms=5,
                label='DF-GLS', alpha=0.85, zorder=4)
        ax.plot(deltas, adf, 'r-D', lw=1.5, ms=5, label='ADF', alpha=0.8)
        ax.plot(deltas, pp, 'b-+', lw=1.5, ms=7, label='PP', alpha=0.8)
        ax.axhline(y=0.05, color='gray', ls=':', alpha=0.6, lw=1)
        ax.set_xlabel(r'$\delta$ (mean break, $\sigma_{unc}$ units)')
        ax.set_title(f'$n = {n}$')
        ax.set_ylim(-0.02, 1.05)
        if ax_idx == 0:
            ax.set_ylabel('Rejection rate')
            ax.legend(loc='upper left', framealpha=0.9)

    fig.suptitle(r'DGP 2: AR(1) $\rho=0.95$ + structural break in mean',
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, 'dgp2_mean_break.pdf'),
                bbox_inches='tight')
    fig.savefig(os.path.join(FIGURES_DIR, 'dgp2_mean_break.png'),
                bbox_inches='tight', dpi=200)
    print("  DGP2 figure saved.")
    plt.close(fig)

    # --- DGP 3 ---
    ratios = DGP3_RATIOS
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)
    for ax_idx, n in enumerate(N_GRID):
        ax = axes[ax_idx]
        nd = dgp3_data[str(n)]
        ours = np.array([nd[str(r)]['ours_R050'] for r in ratios])
        adf = np.array([nd[str(r)]['adf'] for r in ratios])
        pp = np.array([nd[str(r)]['pp'] for r in ratios])
        dfgls = np.array([nd[str(r)]['dfgls'] for r in ratios])

        for arr, c in [(ours, 'black'), (adf, 'red'),
                       (pp, 'blue'), (dfgls, '#2ca02c')]:
            ax.fill_between(ratios, arr - ci_hw(arr), arr + ci_hw(arr),
                            color=c, alpha=0.08)

        ax.plot(ratios, ours, 'k-o', lw=2, ms=6,
                label=r'$\tilde{g}_{0.5}^{\boldsymbol{\theta}}$', zorder=5)
        ax.plot(ratios, dfgls, '-s', color='#2ca02c', lw=1.8, ms=5,
                label='DF-GLS', alpha=0.85, zorder=4)
        ax.plot(ratios, adf, 'r-D', lw=1.5, ms=5, label='ADF', alpha=0.8)
        ax.plot(ratios, pp, 'b-+', lw=1.5, ms=7, label='PP', alpha=0.8)
        ax.axhline(y=0.05, color='gray', ls=':', alpha=0.6, lw=1)
        ax.set_xlabel(r'$\sigma_2 / \sigma_1$ (variance ratio)')
        ax.set_title(f'$n = {n}$')
        ax.set_ylim(-0.02, 1.05)
        if ax_idx == 0:
            ax.set_ylabel('Rejection rate')
            ax.legend(loc='upper left', framealpha=0.9)

    fig.suptitle(r'DGP 3: Random walk with variance break in innovations',
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, 'dgp3_variance_break.pdf'),
                bbox_inches='tight')
    fig.savefig(os.path.join(FIGURES_DIR, 'dgp3_variance_break.png'),
                bbox_inches='tight', dpi=200)
    print("  DGP3 figure saved.")
    plt.close(fig)


def main():
    t_start = time.perf_counter()
    dgp2 = extend_dgp2()
    dgp3 = extend_dgp3()
    print(f"\n  Regenerating figures...")
    plot_figures(dgp2, dgp3)

    elapsed = time.perf_counter() - t_start
    print(f"\n{'=' * 70}")
    print(f"  DONE. Total: {elapsed/60:.1f} min")
    print(f"{'=' * 70}")


if __name__ == '__main__':
    main()
