"""
Final publication figures for DGP 1–3 with DF-GLS.

Unified style, serif fonts embedded, PDF vectorial.
"""

import json
import os
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import rcParams

# ======================================================================
# Publication style
# ======================================================================
rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif', 'Palatino', 'Georgia'],
    'font.size': 12,
    'axes.labelsize': 13,
    'axes.titlesize': 14,
    'legend.fontsize': 10.5,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'figure.dpi': 300,
    'pdf.fonttype': 42,       # TrueType (embeddable)
    'ps.fonttype': 42,
    'axes.linewidth': 0.8,
    'lines.linewidth': 1.8,
    'lines.markersize': 6,
    'axes.grid': False,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.08,
})

RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')
FIGURES_DIR = os.path.join(os.path.dirname(__file__), '..', 'supplementary', 'figures')
N_SIM = 5000
N_GRID = [200, 500, 1000]

# Colors
C_OURS = '#000000'
C_ADF = '#d62728'
C_PP = '#1f77b4'
C_DFGLS = '#2ca02c'

# ======================================================================
# Helpers
# ======================================================================

def load_results(name):
    path = os.path.join(RESULTS_DIR, f'power_comparison_{name}.json')
    with open(path) as f:
        return json.load(f)


def ci_hw(p_hat):
    """Binomial CI half-width (1.96 * SE)."""
    p = np.asarray(p_hat)
    return 1.96 * np.sqrt(p * (1 - p) / N_SIM)


def style_axes(ax, xlabel, n, ylabel=True, ylim=(-0.02, 1.05)):
    ax.set_xlabel(xlabel)
    ax.set_title(f'$n = {n}$')
    ax.set_ylim(ylim)
    ax.axhline(y=0.05, color='gray', linestyle=':', alpha=0.5, linewidth=0.9)
    if ylabel:
        ax.set_ylabel('Rejection rate')
    ax.tick_params(direction='in', top=True, right=True)


def plot_test(ax, x, y, fmt, color, label, zorder=3, lw=None, ms=None, alpha=1.0):
    """Plot a test curve."""
    ax.plot(x, y, fmt, color=color, linewidth=lw or 1.8,
            markersize=ms or 6, label=label, zorder=zorder, alpha=alpha)


def plot_ci_band(ax, x, y, color, alpha=0.12):
    """Shaded CI band."""
    hw = ci_hw(y)
    ax.fill_between(x, y - hw, y + hw, color=color, alpha=alpha,
                    linewidth=0)


# ======================================================================
# DGP 1
# ======================================================================

def plot_dgp1():
    data = load_results('dgp1')['dgp1']
    rhos = [0.80, 0.85, 0.90, 0.93, 0.95, 0.97, 0.99, 1.00]

    fig, axes = plt.subplots(1, 3, figsize=(16, 5.5), sharey=True)

    for i, n in enumerate(N_GRID):
        ax = axes[i]
        nd = data[str(n)]

        ours = np.array([nd[str(r)]['ours_R050'] for r in rhos])
        adf = np.array([nd[str(r)]['adf'] for r in rhos])
        pp = np.array([nd[str(r)]['pp'] for r in rhos])
        dfgls = np.array([nd[str(r)]['dfgls'] for r in rhos])

        # CI bands (Ours and DF-GLS only)
        plot_ci_band(ax, rhos, ours, C_OURS)
        plot_ci_band(ax, rhos, dfgls, C_DFGLS)

        # Lines
        plot_test(ax, rhos, ours, '-o', C_OURS,
                  r'$\tilde{g}_{0.5}^{\boldsymbol{\theta}}$', zorder=5, lw=2.2)
        plot_test(ax, rhos, dfgls, '-^', C_DFGLS, 'DF-GLS', zorder=4)
        plot_test(ax, rhos, adf, '-D', C_ADF, 'ADF', ms=5, alpha=0.8)
        plot_test(ax, rhos, pp, '-+', C_PP, 'PP', ms=7, alpha=0.8)

        style_axes(ax, r'$\rho$', n, ylabel=(i == 0))
        ax.set_xlim(0.78, 1.02)
        ax.invert_xaxis()

        if i == 0:
            ax.legend(loc='upper right', framealpha=0.92, edgecolor='0.7')

    fig.suptitle(
        r'DGP 1: Near-unit-root AR(1) — $Y_t = \rho\,Y_{t-1} + \varepsilon_t$',
        fontsize=15, fontweight='bold', y=1.01)
    plt.tight_layout()

    os.makedirs(FIGURES_DIR, exist_ok=True)
    out = os.path.join(FIGURES_DIR, 'dgp1_power_curves.pdf')
    fig.savefig(out)
    fig.savefig(out.replace('.pdf', '.png'), dpi=300)
    print(f"  DGP1 saved: {out}")
    plt.close(fig)


# ======================================================================
# DGP 2
# ======================================================================

def plot_dgp2():
    data = load_results('dgp2')['dgp2']
    deltas = [0.0, 0.5, 1.0, 2.0, 3.0, 5.0]

    fig, axes = plt.subplots(1, 3, figsize=(16, 5.5), sharey=True)

    for i, n in enumerate(N_GRID):
        ax = axes[i]
        nd = data[str(n)]

        ours = np.array([nd[str(d)]['ours_R050'] for d in deltas])
        adf = np.array([nd[str(d)]['adf'] for d in deltas])
        pp = np.array([nd[str(d)]['pp'] for d in deltas])
        dfgls = np.array([nd[str(d)]['dfgls'] for d in deltas])

        # CI bands
        plot_ci_band(ax, deltas, ours, C_OURS)
        plot_ci_band(ax, deltas, dfgls, C_DFGLS)

        # Lines
        plot_test(ax, deltas, ours, '-o', C_OURS,
                  r'$\tilde{g}_{0.5}^{\boldsymbol{\theta}}$', zorder=5, lw=2.2)
        plot_test(ax, deltas, dfgls, '-^', C_DFGLS, 'DF-GLS', zorder=4)
        plot_test(ax, deltas, adf, '-D', C_ADF, 'ADF', ms=5, alpha=0.8)
        plot_test(ax, deltas, pp, '-+', C_PP, 'PP', ms=7, alpha=0.8)

        style_axes(ax, r'$\delta$ (mean break, $\sigma_{\mathrm{unc}}$ units)',
                   n, ylabel=(i == 0))
        ax.set_xlim(-0.2, 5.3)

        if i == 0:
            ax.legend(loc='upper right', framealpha=0.92, edgecolor='0.7')

    fig.suptitle(
        r'DGP 2: Stationary AR(1) $\rho{=}0.95$ + structural break in mean',
        fontsize=15, fontweight='bold', y=1.01)
    plt.tight_layout()

    out = os.path.join(FIGURES_DIR, 'dgp2_mean_break.pdf')
    fig.savefig(out)
    fig.savefig(out.replace('.pdf', '.png'), dpi=300)
    print(f"  DGP2 saved: {out}")
    plt.close(fig)


# ======================================================================
# DGP 3
# ======================================================================

def plot_dgp3():
    data = load_results('dgp3')['dgp3']
    ratios = [1.0, 1.5, 2.0, 2.5, 3.0, 4.0]

    fig, axes = plt.subplots(1, 3, figsize=(16, 5.5), sharey=True)

    for i, n in enumerate(N_GRID):
        ax = axes[i]
        nd = data[str(n)]

        ours = np.array([nd[str(r)]['ours_R050'] for r in ratios])
        adf = np.array([nd[str(r)]['adf'] for r in ratios])
        pp = np.array([nd[str(r)]['pp'] for r in ratios])
        dfgls = np.array([nd[str(r)]['dfgls'] for r in ratios])

        # CI bands
        plot_ci_band(ax, ratios, ours, C_OURS)
        plot_ci_band(ax, ratios, dfgls, C_DFGLS)

        # Lines
        plot_test(ax, ratios, ours, '-o', C_OURS,
                  r'$\tilde{g}_{0.5}^{\boldsymbol{\theta}}$', zorder=5, lw=2.2)
        plot_test(ax, ratios, dfgls, '-^', C_DFGLS, 'DF-GLS', zorder=4)
        plot_test(ax, ratios, adf, '-D', C_ADF, 'ADF', ms=5, alpha=0.8)
        plot_test(ax, ratios, pp, '-+', C_PP, 'PP', ms=7, alpha=0.8)

        # DGP3-specific: y-axis [0.0, 0.16]
        style_axes(ax, r'$\sigma_2 / \sigma_1$ (variance ratio)',
                   n, ylabel=(i == 0), ylim=(0.0, 0.16))

        if i == 0:
            ax.legend(loc='upper left', framealpha=0.92, edgecolor='0.7')

    fig.suptitle(
        r'DGP 3: Random walk + variance break — size distortion under $H_0$',
        fontsize=15, fontweight='bold', y=1.01)
    plt.tight_layout()

    out = os.path.join(FIGURES_DIR, 'dgp3_variance_break.pdf')
    fig.savefig(out)
    fig.savefig(out.replace('.pdf', '.png'), dpi=300)
    print(f"  DGP3 saved: {out}")
    plt.close(fig)


# ======================================================================
# Main
# ======================================================================

def main():
    print("Generating final publication figures...")
    plot_dgp1()
    plot_dgp2()
    plot_dgp3()
    print("\nAll figures saved to:", FIGURES_DIR)

    # Verify
    for f in ['dgp1_power_curves.pdf', 'dgp2_mean_break.pdf',
              'dgp3_variance_break.pdf']:
        p = os.path.join(FIGURES_DIR, f)
        size_kb = os.path.getsize(p) / 1024
        print(f"  {f}: {size_kb:.1f} KB")


if __name__ == '__main__':
    main()
