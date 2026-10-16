"""
Auditoria A7 - Bloque 3.4: figuras (matplotlib, PDF vectorial en experiments/figures/).

Todas las cifras se leen de JSON. Ningun test se distingue solo por el color:
cada curva tiene marcador y estilo de linea propios.

  dgp1_power_curves.pdf   power_comparison_dgp1.json (propuesto R=0.50, ADF, PP, DF-GLS)
                          + bootstrap DF-GLS (wild_bootstrap_r_audit6.json, rho in {0.95, 0.97, 0.99})
  dgp2_mean_break.pdf     power_comparison_dgp2.json + Zivot-Andrews (dgp2_break_tests_audit6.json)
  dgp3_variance_break.pdf propuesto, ADF y PP de power_comparison_dgp34_alpha1_audit5b.json (piloto
                          alpha(1)); DF-GLS de power_comparison_dgp3.json; bootstrap DF-GLS
                          (wild_bootstrap_r_audit6.json, n in {200, 1000})
  dgp4_components.pdf     power_comparison_dgp34_alpha1_audit5b.json (componentes normalizados a r=1)
  dgp5_mixed_power.pdf    dgp5_mixed_audit7.json: potencia a tamano igualado frente a r por (n, rho);
                          propuesto R=0.50 y R adaptativo contra la union Bonferroni y la union
                          calibrada conjuntamente; la extension (post-registro) sombreada.

Registra procedencia en experiments/results/figures_audit7.json.
Uso: python experiments/audit7_figures.py
"""
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                  # noqa: E402
from matplotlib import rcParams                                  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit7_common as C                                        # noqa: E402

FIG = os.path.join(HERE, "figures")
OUT_META = os.path.join(C.RESULTS, "figures_audit7.json")

rcParams.update({
    "font.family": "serif", "font.serif": ["Times New Roman", "DejaVu Serif"],
    "font.size": 11, "axes.labelsize": 12, "axes.titlesize": 12, "legend.fontsize": 9,
    "pdf.fonttype": 42, "ps.fonttype": 42, "axes.linewidth": 0.8,
    "savefig.bbox": "tight", "savefig.pad_inches": 0.06,
})

# Estilos: (marcador, linea, color). El color es redundante.
S = {
    "ours": ("o", "-", "#000000"),
    "ours_adapt": ("s", "--", "#555555"),
    "dfgls": ("^", "--", "#2ca02c"),
    "boot": ("*", (0, (5, 1.5)), "#9467bd"),
    "adf": ("D", ":", "#d62728"),
    "pp": ("P", "-.", "#1f77b4"),
    "za": ("v", (0, (3, 1, 1, 1)), "#8c564b"),
    "union_bonf": ("^", ":", "#d62728"),
    "union_joint": ("D", "-.", "#1f77b4"),
}
LABEL = {"ours": r"Propuesto $R=0.50$", "ours_adapt": r"Propuesto $\hat R$", "dfgls": "DF-GLS",
         "boot": "DF-GLS bootstrap (AWB)", "adf": "ADF", "pp": "PP", "za": "Zivot-Andrews",
         "union_bonf": r"Unión Bonferroni", "union_joint": r"Unión calibrada conjunta"}
USED = {}


def load(name):
    path = os.path.join(C.RESULTS, name)
    with open(path, encoding="utf-8") as f:
        USED[name] = C._sha256_file(path)
        return json.load(f)


def curve(ax, key, x, y, lo=None, hi=None, ms=5.5):
    m, ls, col = S[key]
    ax.plot(x, y, marker=m, linestyle=ls, color=col, label=LABEL[key], markersize=ms, linewidth=1.5)
    if lo is not None:
        ax.fill_between(x, lo, hi, color=col, alpha=0.10, linewidth=0)


def finish(ax, xlabel, title, ylabel, ylim):
    ax.set_xlabel(xlabel)
    ax.set_title(title)
    ax.set_ylim(*ylim)
    ax.axhline(0.05, color="gray", linestyle=":", linewidth=0.8)
    if ylabel:
        ax.set_ylabel("Tasa de rechazo")
    ax.tick_params(direction="in", top=True, right=True)


def save(fig, name):
    os.makedirs(FIG, exist_ok=True)
    path = os.path.join(FIG, name)
    fig.savefig(path)
    plt.close(fig)
    print("  %s" % path)
    return path


def bottom_legend(fig, ax):
    """Leyenda en una fila bajo los paneles: no tapa ninguna curva."""
    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=len(labels), frameon=False,
               bbox_to_anchor=(0.5, 0.0))


def keyed(d, x):
    """Busca la clave de un parametro float en un dict con claves str ('0.9' o '0.90')."""
    for k in d:
        if abs(float(k) - x) < 1e-9:
            return d[k]
    raise KeyError(x)


def sorted_params(d):
    return sorted(float(k) for k in d)


def fig_dgp1():
    pc = load("power_comparison_dgp1.json")["dgp1"]
    wb = load("wild_bootstrap_r_audit6.json")["dgp1"]
    ns = sorted(int(n) for n in pc)
    fig, axes = plt.subplots(1, len(ns), figsize=(15, 4.8), sharey=True)
    for ax, n in zip(axes, ns):
        cells = pc[str(n)]
        rhos = sorted_params(cells)
        for key, col in (("ours", "ours_R050"), ("dfgls", "dfgls"), ("adf", "adf"), ("pp", "pp")):
            y = np.array([keyed(cells, r)[col] for r in rhos])
            lo = np.array([keyed(cells, r)[col + "_ci_lo"] for r in rhos])
            hi = np.array([keyed(cells, r)[col + "_ci_hi"] for r in rhos])
            curve(ax, key, rhos, y, lo if key in ("ours", "dfgls") else None, hi if key in ("ours", "dfgls") else None)
        if str(n) in wb:
            br = sorted_params(wb[str(n)])
            b = [keyed(wb[str(n)], r)["adf"] for r in br]
            curve(ax, "boot", br, [c["rate"] for c in b], [c["ci_lower"] for c in b], [c["ci_upper"] for c in b], ms=8)
        finish(ax, r"$\rho$", r"$n = %d$" % n, ax is axes[0], (-0.02, 1.05))
        ax.invert_xaxis()
    bottom_legend(fig, axes[0])
    fig.suptitle(r"DGP 1: AR(1) cerca de la raíz unitaria", y=1.02)
    return save(fig, "dgp1_power_curves.pdf")


def fig_dgp2():
    pc = load("power_comparison_dgp2.json")["dgp2"]
    za = load("dgp2_break_tests_audit6.json")["dgp2_power"]
    ns = sorted(int(n) for n in pc)
    fig, axes = plt.subplots(1, len(ns), figsize=(15, 4.8), sharey=True)
    for ax, n in zip(axes, ns):
        cells = pc[str(n)]
        ds = sorted_params(cells)
        for key, col in (("ours", "ours_R050"), ("dfgls", "dfgls"), ("adf", "adf"), ("pp", "pp")):
            y = np.array([keyed(cells, d)[col] for d in ds])
            lo = np.array([keyed(cells, d)[col + "_ci_lo"] for d in ds])
            hi = np.array([keyed(cells, d)[col + "_ci_hi"] for d in ds])
            curve(ax, key, ds, y, lo if key in ("ours", "dfgls") else None, hi if key in ("ours", "dfgls") else None)
        zc = za[str(n)]
        zd = sorted_params(zc)
        curve(ax, "za", zd, [keyed(zc, d)["za_power"] for d in zd],
              [keyed(zc, d)["za_ci"][0] for d in zd], [keyed(zc, d)["za_ci"][1] for d in zd])
        finish(ax, r"$\delta$ (quiebre de media, unidades de $\sigma_{\mathrm{inc}}$)", r"$n = %d$" % n,
               ax is axes[0], (-0.02, 1.05))
    bottom_legend(fig, axes[0])
    fig.suptitle(r"DGP 2: AR(1) estacionario $\rho=0.95$ con quiebre de media", y=1.02)
    return save(fig, "dgp2_mean_break.pdf")


def fig_dgp3():
    a5 = load("power_comparison_dgp34_alpha1_audit5b.json")["dgp3"]
    pc = load("power_comparison_dgp3.json")["dgp3"]
    wb = load("wild_bootstrap_r_audit6.json")["dgp3"]
    ns = sorted(int(n) for n in a5)
    fig, axes = plt.subplots(1, len(ns), figsize=(15, 4.8), sharey=True)
    for ax, n in zip(axes, ns):
        cells = a5[str(n)]
        rs = sorted_params(cells)
        for key, col in (("ours", "ours_R050"), ("adf", "adf"), ("pp", "pp")):
            y = np.array([keyed(cells, r)[col] for r in rs])
            if key == "ours":
                lo, hi = zip(*[C.clopper_pearson(int(round(v * 5000)), 5000) for v in y])
                curve(ax, key, rs, y, np.array(lo), np.array(hi))
            else:
                curve(ax, key, rs, y)
        dcells = pc[str(n)]
        drs = sorted_params(dcells)
        curve(ax, "dfgls", drs, [keyed(dcells, r)["dfgls"] for r in drs],
              [keyed(dcells, r)["dfgls_ci_lo"] for r in drs], [keyed(dcells, r)["dfgls_ci_hi"] for r in drs])
        if str(n) in wb:
            br = sorted_params(wb[str(n)])
            b = [keyed(wb[str(n)], r)["adf"] for r in br]
            curve(ax, "boot", br, [c["rate"] for c in b], [c["ci_lower"] for c in b], [c["ci_upper"] for c in b], ms=8)
        finish(ax, r"$r = \sigma_2/\sigma_1$", r"$n = %d$" % n, ax is axes[0], (0.0, 0.17))
    bottom_legend(fig, axes[0])
    fig.suptitle(r"DGP 3: paseo aleatorio con quiebre de varianza (tamaño bajo $H_0$ de raíz unitaria)", y=1.02)
    return save(fig, "dgp3_variance_break.pdf")


def fig_dgp4():
    a5 = load("power_comparison_dgp34_alpha1_audit5b.json")["dgp4"]
    ns = sorted(int(n) for n in a5)
    fig, axes = plt.subplots(1, len(ns), figsize=(15, 4.6), sharey=True)
    for ax, n in zip(axes, ns):
        cells = a5[str(n)]
        rs = sorted_params(cells)
        g1 = np.array([keyed(cells, r)["E_g1_std"] for r in rs])
        g2 = np.array([keyed(cells, r)["E_g2_std"] for r in rs])
        base_1, base_2 = keyed(cells, rs[0])["E_g1_std"], keyed(cells, rs[0])["E_g2_std"]
        ax.plot(rs, g1 / base_1, marker="o", linestyle="-", color="#1f77b4",
                label=r"$\mathbb{E}[g_{1,\mathrm{std}}]$ (canal de media)")
        ax.plot(rs, g2 / base_2, marker="s", linestyle="--", color="#d62728",
                label=r"$\mathbb{E}[g_{2,\mathrm{std}}]$ (canal de varianza)")
        ax.axhline(1.0, color="gray", linestyle=":", linewidth=0.8)
        ax.set_xlabel(r"$r = \sigma_2/\sigma_1$")
        ax.set_title(r"$n = %d$" % n)
        ax.tick_params(direction="in", top=True, right=True)
        if ax is axes[0]:
            ax.set_ylabel(r"Valor normalizado (cociente respecto de $r=1$)")
    bottom_legend(fig, axes[0])
    fig.suptitle(r"DGP 4: respuesta de los componentes, AR(0.5) estacionario con quiebre de varianza (piloto $\alpha(1)$)", y=1.02)
    return save(fig, "dgp4_components.pdf")


def fig_dgp5():
    d5 = load("dgp5_mixed_audit7.json")
    cells = list(d5["cells"].values())
    ns = sorted({c["n"] for c in cells})
    rhos = sorted({c["rho"] for c in cells})
    fig, axes = plt.subplots(len(ns), len(rhos), figsize=(14, 4.2 * len(ns)), sharey=True, squeeze=False)
    for i, n in enumerate(ns):
        for j, rho in enumerate(rhos):
            ax = axes[i][j]
            sub = sorted([c for c in cells if c["n"] == n and c["rho"] == rho], key=lambda c: c["r"])
            rs = [c["r"] for c in sub]
            weak = [c["r"] for c in sub if c["grid"] == "extension_enmienda2"]
            if weak:
                ax.axvspan(min(weak) - 0.03, max(weak) + 0.03, facecolor="0.9", hatch="///", edgecolor="0.6",
                           linewidth=0, label="Extensión post-registro" if (i, j) == (0, 0) else None)
            for key, proc in (("ours", "proposed_R050"), ("ours_adapt", "proposed_adaptive"),
                              ("union_bonf", "union_bonferroni"), ("union_joint", "union_joint")):
                p = [c["power_size_matched"][proc] for c in sub]
                curve(ax, key, rs, [q["rate"] for q in p], [q["ci_lower"] for q in p], [q["ci_upper"] for q in p])
            finish(ax, r"$r = \sigma_2/\sigma_1$" if i == len(ns) - 1 else "",
                   r"$n = %d$, $\rho = %.2f$" % (n, rho), j == 0, (-0.02, 1.05))
    fig.subplots_adjust(hspace=0.30)
    bottom_legend(fig, axes[0][0])
    fig.suptitle("DGP 5: AR(1) con quiebre de varianza, potencia a tamaño igualado al 5%", y=1.01)
    return save(fig, "dgp5_mixed_power.pdf")


def main():
    paths = [fig_dgp1(), fig_dgp2(), fig_dgp3(), fig_dgp4(), fig_dgp5()]
    C.atomic_write_json(OUT_META, {
        "provenance": C.provenance(dgp="figures", n_sim=None, seed_formula=None),
        "figures": {os.path.basename(p): C._sha256_file(p) for p in paths},
        "sources_sha256": USED})
    print(OUT_META)
    return 0


if __name__ == "__main__":
    sys.exit(main())
