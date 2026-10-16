"""
Auditoria A8 - B8: figuras. Lee solo JSON; PDF vectorial legible en escala de
grises (marcadores y estilos de linea distintos), doble columna (19 cm).

1. fig_local_power_audit8.pdf: potencia local frente a c (demeaned / tendencia).
2. fig_size_shift_audit8.pdf: Delta pareado (pp) frente a n (escala log), con
   bandas +-1.96 EE; persistencia 0.99 con z normal y 0.95 con z t(5). AWB solo
   hasta n = 1000 (enmienda 2).
3. fig_dgp1_power_audit8.pdf: potencia frente a rho (eje decreciente desde 1),
   n = 200, 500, 1000; en n = 1000, rho en [0.93, 1].
4. fig_dgp5_audit8.pdf: potencia a tamano igualado frente a r (log2) por rho, con
   el interior registrado r in {2, 3} sombreado; cuota de energia de g2 (log) con
   linea en 2.5%.

Salidas: experiments/figures/*_audit8.pdf, copia en paper/figures/ y
experiments/results/figures_audit8.json (sha256).
Uso: python experiments/make_figures_audit8.py
"""
import os
import shutil
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                    # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit8_common as C                                          # noqa: E402
import audit8_figconfig as F                                       # noqa: E402

FIG_DIR = os.path.join(HERE, "figures")
PAPER_FIG_DIR = os.path.join(C.REPO, "paper", "figures")
OUT = os.path.join(C.RESULTS, "figures_audit8.json")
GARCH_PANELS = (("p099", "persistencia 0.99, z normal"), ("p095_t5", "persistencia 0.95, z t(5)"))
SIZE_N = (200, 500, 1000, 2000, 5000)


def style(ax_plot, key, label, x, y, **kw):
    col, mk, ls = F.STYLE[key]
    ax_plot.plot(x, y, color=col, marker=mk or None, linestyle=ls, linewidth=F.LINE_WIDTH,
                 markersize=F.MARKER_SIZE, label=label, **kw)


def finish(fig, axes, path, bottom):
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=min(len(labels), 6), fontsize=F.LEGEND_SIZE,
               frameon=False, bbox_to_anchor=(0.5, F.LEGEND_BOTTOM))
    fig.subplots_adjust(bottom=bottom, wspace=F.SUBPLOT_WSPACE, hspace=F.SUBPLOT_HSPACE)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def primary_info():
    b4 = C.read_json("b4_local_power_audit8.json")
    gls = bool(b4["gls_rule"]["adopt_gls"])
    return b4, gls


def fig_local_power(b4, gls):
    path = os.path.join(FIG_DIR, "fig_local_power_audit8.pdf")
    fig, axes = plt.subplots(1, 2, figsize=(F.WIDTH_DOUBLE, F.HEIGHT_TWO_PANEL), sharey=True)
    prim = "gls_t0.1" if gls else "rm_t0.1"
    curves = [("envelope", "envolvente (P_T)", "envelope"), ("primary", "primaria", prim)]
    if gls:
        curves.append(("rm", "RM", "rm_t0.1"))
    curves += [("dfgls", "DF-GLS", "dfgls"), ("msb", "MSB-GLS", "msb"), ("mzt", "MZ_t-GLS", "mzt")]
    for ax, (case, title) in zip(axes, (("dm", "demeaned"), ("ct", "con tendencia"))):
        pw = b4["cases"][case]["power"]
        cs = sorted(pw, key=float)
        x = [float(c) for c in cs]
        for key, lab, proc in curves:
            style(ax, key, lab, x, [pw[c][proc] for c in cs])
        ax.axhline(F.NOMINAL_LINE, color="0.5", linewidth=F.LINE_WIDTH / 2)
        ax.set_title(title, fontsize=F.FONT_SIZE)
        ax.set_xlabel("c", fontsize=F.FONT_SIZE)
        ax.set_ylim(F.POWER_YMIN, F.POWER_YMAX)
        ax.grid(alpha=F.GRID_ALPHA)
        ax.tick_params(labelsize=F.FONT_SIZE)
    axes[0].set_ylabel("potencia (n = %d)" % b4["config"]["n"], fontsize=F.FONT_SIZE)
    finish(fig, axes, path, F.BOTTOM_MARGIN)
    return path


def fig_size_shift(gls):
    b3 = C.read_json("b3_comparators_audit8.json")
    path = os.path.join(FIG_DIR, "fig_size_shift_audit8.pdf")
    fig, axes = plt.subplots(1, 2, figsize=(F.WIDTH_DOUBLE, F.HEIGHT_TWO_PANEL), sharey=True)
    prim = "rm_rmgls_hac" if gls else "rm_R0_t0.1_hac"
    curves = [("primary", "primaria", prim), ("adf_sim", "ADF-sim", "adf_sim"), ("dfgls_sim", "DF-GLS-sim", "dfgls_sim"),
              ("mzt_sim", "MZ_t-GLS-sim", "mzt_sim"), ("msbhac", "MSB-HAC", "rm_msbhac_hac"), ("awb", "AWB", "awb")]
    pdl = b3["paired_delta"]
    for ax, (key, title) in zip(axes, GARCH_PANELS):
        for sk, lab, proc in curves:
            pts = [(n, pdl["garch_%s_n%d" % (key, n)][proc]) for n in SIZE_N
                   if proc in pdl.get("garch_%s_n%d" % (key, n), {})]
            x = [p[0] for p in pts]
            y = [p[1]["delta"] * 100 for p in pts]
            e = [p[1]["se"] * 100 * 1.96 for p in pts]
            style(ax, sk, lab, x, y)
            ax.fill_between(x, [a - b for a, b in zip(y, e)], [a + b for a, b in zip(y, e)],
                            color=F.STYLE[sk][0], alpha=F.BAND_ALPHA, linewidth=0)
        ax.axhline(0.0, color="0.5", linewidth=F.LINE_WIDTH / 2)
        ax.set_xscale("log")
        ax.set_xticks(list(SIZE_N))
        ax.set_xticklabels([str(n) for n in SIZE_N])
        ax.set_title(title, fontsize=F.FONT_SIZE)
        ax.set_xlabel("n", fontsize=F.FONT_SIZE)
        ax.grid(alpha=F.GRID_ALPHA)
        ax.tick_params(labelsize=F.FONT_SIZE)
    axes[0].set_ylabel("Δ de tamaño (pp)", fontsize=F.FONT_SIZE)
    finish(fig, axes, path, F.BOTTOM_MARGIN)
    return path


def fig_dgp1(b5, gls):
    path = os.path.join(FIG_DIR, "fig_dgp1_power_audit8.pdf")
    fig, axes = plt.subplots(1, 3, figsize=(F.WIDTH_DOUBLE, F.HEIGHT_THREE_PANEL), sharey=True)
    prim = b5["primary"] == "RM-GLS" and "rmgls" or "rm"
    curves = [("primary", "primaria", prim), ("adf", "ADF", "adf"), ("pp", "PP", "pp"), ("dfgls", "DF-GLS", "dfgls"),
              ("mzt", "MZ_t-GLS", "mzt")]
    for ax, n in zip(axes, (200, 500, 1000)):
        cells = sorted((v for v in b5["dgp1"].values() if v["n"] == n), key=lambda v: -v["rho"])
        if n == 1000:
            cells = [v for v in cells if v["rho"] >= F.DGP1_N1000_RHO_MIN]
        x = [v["rho"] for v in cells]
        for sk, lab, proc in curves:
            style(ax, sk, lab, x, [v["rates"][proc]["rate"] for v in cells])
        ax.set_xlim(F.DGP1_RHO_MAX, min(x))
        ax.set_ylim(F.POWER_YMIN, F.POWER_YMAX)
        ax.set_title("n = %d" % n, fontsize=F.FONT_SIZE)
        ax.set_xlabel("ρ", fontsize=F.FONT_SIZE)
        ax.grid(alpha=F.GRID_ALPHA)
        ax.tick_params(labelsize=F.FONT_SIZE)
    axes[0].set_ylabel("potencia", fontsize=F.FONT_SIZE)
    finish(fig, axes, path, F.BOTTOM_MARGIN)
    return path


def fig_dgp5(b5):
    path = os.path.join(FIG_DIR, "fig_dgp5_audit8.pdf")
    cells = list(b5["dgp5"]["cells"].values())
    rhos = sorted({v["rho"] for v in cells})
    fig, axes = plt.subplots(2, len(rhos), figsize=(F.WIDTH_DOUBLE, F.HEIGHT_DGP5), sharex=True)
    curves = [("r05", "R = 0.5", "proposed_R050"), ("rhat", "R̂", "proposed_adaptive"), ("union", "unión conjunta", "union_joint"),
              ("bootstrap", "bootstrap", "bootstrap_dfgls"), ("primary", "primaria", "primary")]
    for j, rho in enumerate(rhos):
        cs = sorted((v for v in cells if v["rho"] == rho), key=lambda v: v["r"])
        x = [v["r"] for v in cs]
        top, bot = axes[0][j], axes[1][j]
        for ax in (top, bot):
            ax.axvspan(F.REGISTERED_INTERIOR[0], F.REGISTERED_INTERIOR[1], color="0.5", alpha=F.SHADE_ALPHA, linewidth=0)
            ax.set_xscale("log", base=F.LOG2_BASE)
            ax.grid(alpha=F.GRID_ALPHA)
            ax.tick_params(labelsize=F.FONT_SIZE)
        for sk, lab, proc in curves:
            style(top, sk, lab, x, [v["size_matched"][proc]["rate"] for v in cs])
        top.set_ylim(F.POWER_YMIN, F.POWER_YMAX)
        top.set_title("ρ = %g" % rho, fontsize=F.FONT_SIZE)
        style(bot, "r05", "cuota de g₂ (R = 0.5)", x, [v["g2_share_R050_median"] for v in cs])
        bot.set_yscale("log")
        bot.axhline(F.SHARE_LINE, color="0.5", linewidth=F.LINE_WIDTH / 2)
        bot.set_xlabel("r", fontsize=F.FONT_SIZE)
    axes[0][0].set_ylabel("potencia (tamaño igualado)", fontsize=F.FONT_SIZE)
    axes[1][0].set_ylabel("cuota mediana de g₂", fontsize=F.FONT_SIZE)
    finish(fig, list(axes[0]), path, F.BOTTOM_MARGIN_DGP5)
    return path


def main():
    os.makedirs(FIG_DIR, exist_ok=True)
    os.makedirs(PAPER_FIG_DIR, exist_ok=True)
    plt.rcParams.update({"font.size": F.FONT_SIZE, "pdf.fonttype": 42})
    b4, gls = primary_info()
    b5 = C.read_json("b5_power_audit8.json")
    paths = [fig_local_power(b4, gls), fig_size_shift(gls), fig_dgp1(b5, gls), fig_dgp5(b5)]
    figs = {}
    for p in paths:
        dst = os.path.join(PAPER_FIG_DIR, os.path.basename(p))
        shutil.copyfile(p, dst)
        figs[os.path.basename(p)] = {"sha256": C.sha256_file(p), "paper_copy": C.rel(dst),
                                     "paper_copy_sha256": C.sha256_file(dst), "bytes": os.path.getsize(p)}
    out = {"provenance": C.provenance(__file__, seed_family=C.FAMILY["B8"]), "primary_is_gls": gls,
           "sources": ["b4_local_power_audit8.json", "b3_comparators_audit8.json", "b5_power_audit8.json"],
           "figures": figs}
    C.write_result(OUT, out, __file__)
    C.register_outputs(__file__, paths + [os.path.join(PAPER_FIG_DIR, os.path.basename(p)) for p in paths], out["provenance"])
    for k, v in figs.items():
        print(k, v["sha256"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
