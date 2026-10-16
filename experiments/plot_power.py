"""
Phase 3 — Power comparison figures for the paper.

Generates publication-quality matplotlib figures from the JSON results.
Includes 95% binomial confidence intervals on all rejection rates.

Figure 1: Size table (LaTeX)
Figure 2: DGP1 power curves — Near-unit-root AR(1)
Figure 3: DGP2 power curves — Stationary AR(1) + mean break
Figure 4: DGP3 power curves — Random walk with variance break
"""

import json
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ======================================================================
# Style
# ======================================================================
plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 11,
    'axes.labelsize': 12,
    'axes.titlesize': 13,
    'legend.fontsize': 9,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'axes.grid': False,
    'axes.spines.top': False,
    'axes.spines.right': False,
})

RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')
FIGURES_DIR = os.path.join(os.path.dirname(__file__), 'figures')
os.makedirs(FIGURES_DIR, exist_ok=True)

N_SIM = 5000  # For CI calculation


def load_results(name):
    path = os.path.join(RESULTS_DIR, f'power_comparison_{name}.json')
    with open(path) as f:
        return json.load(f)


def ci_95(p, n=N_SIM):
    """95% binomial CI half-width for proportion p with n trials."""
    return 1.96 * np.sqrt(np.clip(p * (1 - p), 0, 0.25) / n)


# ======================================================================
# Figure: DGP1 — Power curves with CI bands
# ======================================================================

def plot_dgp1():
    data = load_results('dgp1')['dgp1']

    rhos = [0.80, 0.85, 0.90, 0.93, 0.95, 0.97, 0.99, 1.00]
    n_values = [200, 500, 1000]

    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)

    for ax_idx, n in enumerate(n_values):
        ax = axes[ax_idx]
        n_data = data[str(n)]

        ours_r50 = np.array([n_data[str(rho)]['ours_R050'] for rho in rhos])
        adf = np.array([n_data[str(rho)]['adf'] for rho in rhos])
        pp = np.array([n_data[str(rho)]['pp'] for rho in rhos])

        ci_ours = ci_95(ours_r50)
        ci_adf = ci_95(adf)
        ci_pp = ci_95(pp)

        # Error bands
        ax.fill_between(rhos, ours_r50 - ci_ours, ours_r50 + ci_ours,
                        color='black', alpha=0.1)
        ax.fill_between(rhos, adf - ci_adf, adf + ci_adf,
                        color='red', alpha=0.07)
        ax.fill_between(rhos, pp - ci_pp, pp + ci_pp,
                        color='blue', alpha=0.07)

        # Lines
        ax.plot(rhos, ours_r50, 'k-o', linewidth=2.0, markersize=6,
                label=r'$\tilde{g}_{0.5}^{\boldsymbol{\theta}}$', zorder=5)
        ax.plot(rhos, adf, 'r-D', linewidth=1.5, markersize=5,
                label='ADF', alpha=0.8)
        ax.plot(rhos, pp, 'b-+', linewidth=1.5, markersize=7,
                label='PP', alpha=0.8)

        # Nominal size
        ax.axhline(y=0.05, color='gray', linestyle=':', alpha=0.6, linewidth=1)

        ax.set_xlabel(r'$\rho$')
        ax.set_title(f'$n = {n}$')
        ax.set_xlim(0.78, 1.02)
        ax.set_ylim(-0.02, 1.05)
        ax.invert_xaxis()

        if ax_idx == 0:
            ax.set_ylabel('Rejection rate')
            ax.legend(loc='upper right', framealpha=0.9)

    fig.suptitle(r'DGP 1: Near-unit-root AR(1) $Y_t = \rho\,Y_{t-1} + \varepsilon_t$',
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, 'dgp1_power_curves.pdf'))
    fig.savefig(os.path.join(FIGURES_DIR, 'dgp1_power_curves.png'))
    print("  DGP1 figure saved.")
    plt.close(fig)


# ======================================================================
# Figure: DGP2 — AR(1) + mean break with CI bands
# ======================================================================

def plot_dgp2():
    data = load_results('dgp2')['dgp2']

    deltas = [0.0, 0.5, 1.0, 2.0, 3.0, 5.0]
    n_values = [200, 500, 1000]

    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)

    for ax_idx, n in enumerate(n_values):
        ax = axes[ax_idx]
        n_data = data[str(n)]

        ours_r50 = np.array([n_data[str(d)]['ours_R050'] for d in deltas])
        ours_r25 = np.array([n_data[str(d)]['ours_R025'] for d in deltas])
        adf = np.array([n_data[str(d)]['adf'] for d in deltas])
        pp = np.array([n_data[str(d)]['pp'] for d in deltas])

        ci_r50 = ci_95(ours_r50)
        ci_r25 = ci_95(ours_r25)
        ci_adf = ci_95(adf)
        ci_pp = ci_95(pp)

        # Error bands for Ours R50 and ADF
        ax.fill_between(deltas, ours_r50 - ci_r50, ours_r50 + ci_r50,
                        color='black', alpha=0.1)
        ax.fill_between(deltas, adf - ci_adf, adf + ci_adf,
                        color='red', alpha=0.07)

        ax.plot(deltas, ours_r50, 'k-o', linewidth=2.0, markersize=6,
                label=r'$\tilde{g}_{0.5}^{\boldsymbol{\theta}}$', zorder=5)
        ax.plot(deltas, ours_r25, 'k--s', linewidth=1.5, markersize=5,
                label=r'$\tilde{g}_{0.25}^{\boldsymbol{\theta}}$ (mean)', alpha=0.7)
        ax.plot(deltas, adf, 'r-D', linewidth=1.5, markersize=5,
                label='ADF', alpha=0.8)
        ax.plot(deltas, pp, 'b-+', linewidth=1.5, markersize=7,
                label='PP', alpha=0.8)

        ax.axhline(y=0.05, color='gray', linestyle=':', alpha=0.6, linewidth=1)

        ax.set_xlabel(r'Break magnitude $\delta$')
        ax.set_title(f'$n = {n}$')

        if ax_idx == 0:
            ax.set_ylabel('Rejection rate')
            ax.legend(loc='best', framealpha=0.9)

    fig.suptitle(
        r'DGP 2: Stationary AR(1) $\rho=0.95$ + mean break at $\lfloor n/2 \rfloor$',
        fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, 'dgp2_mean_break.pdf'))
    fig.savefig(os.path.join(FIGURES_DIR, 'dgp2_mean_break.png'))
    print("  DGP2 figure saved.")
    plt.close(fig)


# ======================================================================
# Figure: DGP3 — Variance break detection with CI bands
# ======================================================================

def plot_dgp3():
    data = load_results('dgp3')['dgp3']

    ratios = [1.0, 1.5, 2.0, 2.5, 3.0, 4.0]
    n_values = [200, 500, 1000]

    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)

    for ax_idx, n in enumerate(n_values):
        ax = axes[ax_idx]
        n_data = data[str(n)]

        ours_r50 = np.array([n_data[str(r)]['ours_R050'] for r in ratios])
        ours_r25 = np.array([n_data[str(r)]['ours_R025'] for r in ratios])
        adf = np.array([n_data[str(r)]['adf'] for r in ratios])
        pp = np.array([n_data[str(r)]['pp'] for r in ratios])

        ci_r50 = ci_95(ours_r50)
        ci_adf = ci_95(adf)

        ax.fill_between(ratios, ours_r50 - ci_r50, ours_r50 + ci_r50,
                        color='black', alpha=0.1)
        ax.fill_between(ratios, adf - ci_adf, adf + ci_adf,
                        color='red', alpha=0.07)

        ax.plot(ratios, ours_r50, 'k-o', linewidth=2.0, markersize=6,
                label=r'$\tilde{g}_{0.5}^{\boldsymbol{\theta}}$', zorder=5)
        ax.plot(ratios, ours_r25, 'k--s', linewidth=1.5, markersize=5,
                label=r'$\tilde{g}_{0.25}^{\boldsymbol{\theta}}$ (mean)', alpha=0.7)
        ax.plot(ratios, adf, 'r-D', linewidth=1.5, markersize=5,
                label='ADF', alpha=0.8)
        ax.plot(ratios, pp, 'b-+', linewidth=1.5, markersize=7,
                label='PP', alpha=0.8)

        ax.axhline(y=0.05, color='gray', linestyle=':', alpha=0.6, linewidth=1)

        ax.set_xlabel(r'Variance ratio $r = \sigma_2/\sigma_1$')
        ax.set_title(f'$n = {n}$')
        ax.set_ylim(-0.005, 0.15)

        if ax_idx == 0:
            ax.set_ylabel('Rejection rate')
            ax.legend(loc='upper left', framealpha=0.9)

    fig.suptitle(
        r'DGP 3: Random walk with variance break $\sigma_2 = r\,\sigma_1$ at $\lfloor n/2 \rfloor$',
        fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, 'dgp3_variance_break.pdf'))
    fig.savefig(os.path.join(FIGURES_DIR, 'dgp3_variance_break.png'))
    print("  DGP3 figure saved.")
    plt.close(fig)


# ======================================================================
# Tables
# ======================================================================

def print_size_table():
    data = load_results('size')['size']

    print("\n  Table 1: Empirical Size (alpha=0.05, N_sim=5000)")
    print("  " + "=" * 70)
    print(f"  {'Test':<18} {'n=200':>12} {'n=500':>12} {'n=1000':>12}")
    print("  " + "-" * 70)

    tests = [
        ('Ours (R=0.50)', 'ours_R050'),
        ('Ours (R=0.25)', 'ours_R025'),
        ('Ours (R=0.75)', 'ours_R075'),
        ('ADF', 'adf'),
        ('PP', 'pp'),
        ('KPSS', 'kpss_size'),
    ]

    for label, key in tests:
        vals = []
        for n_str in ['200', '500', '1000']:
            v = data[n_str].get(key)
            if v is None:
                # Try alternative key names
                if key == 'kpss_size':
                    v = data[n_str].get('kpss')
                elif key.startswith('ours_'):
                    v = data[n_str].get('ours')
            if isinstance(v, (float, int)):
                ci = ci_95(v)
                vals.append(f"{v:.3f} ± {ci:.3f}")
            else:
                vals.append(str(v) if v is not None else '-')
        print(f"  {label:<18} {vals[0]:>12} {vals[1]:>12} {vals[2]:>12}")

    print("  " + "=" * 70)


def print_dgp1_summary():
    data = load_results('dgp1')['dgp1']
    rhos = [0.80, 0.85, 0.90, 0.93, 0.95, 0.97, 0.99, 1.00]

    print("\n  Table 2: DGP1 Power (N_sim=5000)")
    print("  " + "=" * 85)

    for n in [200, 500, 1000]:
        n_data = data[str(n)]
        print(f"\n  n = {n}:")
        print(f"  {'rho':<8} {'Ours±CI':>16} {'ADF±CI':>16} {'PP':>8} "
              f"{'Delta':>8} {'Sig':>5}")
        print("  " + "-" * 70)
        for rho in rhos:
            cell = n_data[str(rho)]
            ours = cell['ours_R050']
            adf = cell['adf']
            pp = cell['pp']
            delta = ours - adf
            ci_o = ci_95(ours)
            ci_a = ci_95(adf)
            # Difference is significant if |delta| > sqrt(ci_o^2 + ci_a^2)
            ci_delta = np.sqrt(ci_o**2 + ci_a**2)
            sig = "***" if abs(delta) > 3*ci_delta else "**" if abs(delta) > 2*ci_delta else "*" if abs(delta) > ci_delta else ""
            print(f"  {rho:<8.2f} {ours:>6.3f}±{ci_o:.3f}  {adf:>6.3f}±{ci_a:.3f}"
                  f"  {pp:>8.3f} {delta:>+8.3f} {sig:>5}")


def print_dgp2_summary():
    try:
        data = load_results('dgp2')['dgp2']
    except FileNotFoundError:
        print("\n  DGP2 results not yet available.")
        return

    deltas = [0.0, 0.5, 1.0, 2.0, 3.0, 5.0]

    print("\n  Table 3: DGP2 Power — AR(1) rho=0.95 + mean break (N_sim=5000)")
    print("  " + "=" * 90)

    for n in [200, 500, 1000]:
        n_data = data[str(n)]
        print(f"\n  n = {n}:")
        print(f"  {'delta':<8} {'Ours R50':>10} {'Ours R25':>10} {'ADF':>10} "
              f"{'PP':>10} {'Delta_ADF':>10}")
        print("  " + "-" * 65)
        for d in deltas:
            cell = n_data[str(d)]
            r50 = cell['ours_R050']
            r25 = cell['ours_R025']
            adf = cell['adf']
            pp = cell['pp']
            delta_v = r50 - adf
            print(f"  {d:<8.1f} {r50:>10.3f} {r25:>10.3f} "
                  f"{adf:>10.3f} {pp:>10.3f} {delta_v:>+10.3f}")


def print_dgp3_summary():
    data = load_results('dgp3')['dgp3']
    ratios = [1.0, 1.5, 2.0, 2.5, 3.0, 4.0]

    print("\n  Table 4: DGP3 Rejection — RW with variance break (N_sim=5000)")
    print("  " + "=" * 85)

    for n in [200, 500, 1000]:
        n_data = data[str(n)]
        print(f"\n  n = {n}:")
        print(f"  {'ratio':<8} {'Ours R50±CI':>16} {'ADF±CI':>16} "
              f"{'PP':>8} {'Delta':>8}")
        print("  " + "-" * 60)
        for r in ratios:
            cell = n_data[str(r)]
            r50 = cell['ours_R050']
            adf = cell['adf']
            pp = cell['pp']
            delta = r50 - adf
            ci_o = ci_95(r50)
            ci_a = ci_95(adf)
            print(f"  {r:<8.1f} {r50:>6.3f}±{ci_o:.3f}  {adf:>6.3f}±{ci_a:.3f}"
                  f"  {pp:>8.3f} {delta:>+8.3f}")


# ======================================================================
# DGP4: Component diagnostics plot
# ======================================================================

def plot_dgp4_components():
    data = load_results('dgp4')['dgp4']

    ratios = [1.0, 1.5, 2.0, 2.5, 3.0, 4.0]
    n_values = [200, 500, 1000]

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    for ax_idx, n in enumerate(n_values):
        ax = axes[ax_idx]
        n_data = data[str(n)]

        g1_means = [n_data[str(r)]['E_g1_std'] for r in ratios]
        g2_means = [n_data[str(r)]['E_g2_std'] for r in ratios]

        # Normalize to baseline (r=1.0) for clearer comparison
        g1_base = g1_means[0] if g1_means[0] > 0 else 1.0
        g2_base = g2_means[0] if g2_means[0] > 0 else 1.0
        g1_norm = [x / g1_base for x in g1_means]
        g2_norm = [x / g2_base for x in g2_means]

        ax.plot(ratios, g1_norm, 'b-o', linewidth=2.0, markersize=6,
                label=r'$\mathbb{E}[g_{1,\mathrm{std}}]$ (mean channel)')
        ax.plot(ratios, g2_norm, 'r-s', linewidth=2.0, markersize=6,
                label=r'$\mathbb{E}[g_{2,\mathrm{std}}]$ (variance channel)')

        ax.axhline(y=1.0, color='gray', linestyle=':', alpha=0.5)

        ax.set_xlabel(r'Variance ratio $r = \sigma_2/\sigma_1$')
        ax.set_title(f'$n = {n}$')
        ax.set_ylim(0.0, None)

        if ax_idx == 0:
            ax.set_ylabel('Normalized component value (ratio to $r=1$)')
            ax.legend(loc='upper left', framealpha=0.9)

    fig.suptitle(
        r'DGP 4: Component response — stationary AR(0.5) + variance break',
        fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, 'dgp4_components.pdf'))
    fig.savefig(os.path.join(FIGURES_DIR, 'dgp4_components.png'))
    print("  DGP4 components figure saved.")
    plt.close(fig)


def print_dgp4_summary():
    data = load_results('dgp4')['dgp4']
    ratios = [1.0, 1.5, 2.0, 2.5, 3.0, 4.0]

    print("\n  Table 5: DGP4 Component Diagnostics — AR(0.5) + variance break")
    print("  " + "=" * 90)

    for n in [200, 500, 1000]:
        n_data = data[str(n)]
        print(f"\n  n = {n}:")
        print(f"  {'ratio':<8} {'E[g1_std]':>10} {'E[g2_std]':>10} "
              f"{'g2/g2(1)':>10} {'Ours R50':>10} {'ADF':>10} {'KPSS':>10}")
        print("  " + "-" * 75)
        g2_base = n_data['1.0']['E_g2_std']
        for r in ratios:
            cell = n_data[str(r)]
            g2_ratio = cell['E_g2_std'] / g2_base if g2_base > 0 else 0
            print(f"  {r:<8.1f} {cell['E_g1_std']:>10.4f} {cell['E_g2_std']:>10.4f} "
                  f"{g2_ratio:>10.1f}x {cell['ours_R050']:>10.3f} "
                  f"{cell['adf']:>10.3f} {cell['kpss_rej']:>10.3f}")


# ======================================================================
# Main
# ======================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("  Generating Phase 3 figures and tables")
    print("=" * 70)

    print_size_table()
    print_dgp1_summary()
    print_dgp2_summary()
    print_dgp3_summary()

    plot_dgp1()
    try:
        plot_dgp2()
    except FileNotFoundError:
        print("  DGP2 results not yet available, skipping figure.")
    plot_dgp3()

    try:
        print_dgp4_summary()
        plot_dgp4_components()
    except FileNotFoundError:
        print("  DGP4 results not yet available, skipping.")

    print(f"\n  All figures saved to: {FIGURES_DIR}")
    print("=" * 70)

