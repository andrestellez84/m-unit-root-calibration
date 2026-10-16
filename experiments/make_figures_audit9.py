"""
Auditoria A9 - B9.7 (2): figuras. Lee solo JSON; PDF vectorial, doble columna (19 cm),
legibles en escala de grises (marcadores y estilos de linea distintos).

1. fig_local_power_audit9.pdf: potencia local frente a c (demeaned / tendencia):
   envolvente, primaria, MSB-GLS, DF-GLS, MZt-GLS (sim) y la primaria con theta = 0.
2. fig_theta_ladder_audit9.pdf: brecha a la envolvente frente a theta en c = 5, 10, 15.
3. fig_power_equalized_audit9.pdf: DGP 1 (fila 1) y caso con tendencia (fila 2) a
   tamano igualado, potencia frente a rho, n = 200, 500, 1000.
4. fig_size_shift_audit9.pdf: Delta de tamano (pp) frente a n en las GARCH de
   persistencia 0.99 (z normal) y 0.95 (z t(5)), con bandas +-1.96 EE; incluye
   MSB-GLS-sim; AWB (DF-GLS) arrastrado de A8 hasta n = 1000.
5. fig_dgp3_audit9.pdf: tasa de rechazo frente a r bajo la nula verdadera (DGP 3),
   n = 200, 500, 1000: primaria (sim), primaria AWB (B9.5, si existe), RM, ADF-sim,
   DF-GLS-sim y AWB-DF-GLS (A8).

Salidas: experiments/figures/*_audit9.pdf, copia en paper/figures/ y
experiments/results/figures_audit9.json.
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

import audit9_common as C                                          # noqa: E402
import audit9_figconfig as F                                       # noqa: E402

FIG_DIR = os.path.join(HERE, "figures")
PAPER_FIG_DIR = os.path.join(C.REPO, "paper", "figures")
OUT = os.path.join(C.RESULTS, "figures_audit9.json")
GARCH_PANELS = (("p099", "persistencia 0.99, z normal"), ("p095_t5", "persistencia 0.95, z t(5)"))
CASE_TITLE = {"dm": "demeaned", "ct": "con tendencia", "c": "demeaned"}


def style(ax, key, label, x, y):
    col, mk, ls = F.STYLE[key]
    ax.plot(x, y, color=col, marker=mk or None, linestyle=ls, linewidth=F.LINE_WIDTH, markersize=F.MARKER_SIZE,
            label=label)


def dress(ax, title, xlabel):
    ax.set_title(title, fontsize=F.FONT_SIZE)
    ax.set_xlabel(xlabel, fontsize=F.FONT_SIZE)
    ax.grid(alpha=F.GRID_ALPHA)
    ax.tick_params(labelsize=F.FONT_SIZE)


def finish(fig, axes, path, bottom):
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=min(len(labels), 6), fontsize=F.LEGEND_SIZE,
               frameon=False, bbox_to_anchor=(0.5, F.LEGEND_BOTTOM))
    fig.subplots_adjust(bottom=bottom, wspace=F.SUBPLOT_WSPACE, hspace=F.SUBPLOT_HSPACE)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def fig_local_power(b92, prim):
    path = os.path.join(FIG_DIR, "fig_local_power_audit9.pdf")
    fig, axes = plt.subplots(1, 2, figsize=(F.WIDTH_DOUBLE, F.HEIGHT_TWO_PANEL), sharey=True)
    curves = [("envelope", "envolvente (P_T)", "envelope"), ("primary", "primaria (θ = %g)" % b92["primary_theta"], prim),
              ("msb", "MSB-GLS", "msb"), ("dfgls", "DF-GLS", "dfgls"), ("mzt", "MZ_t-GLS", "mzt")]
    if prim != "gls_t0":
        curves.append(("theta0", "primaria con θ = 0", "gls_t0"))
    for ax, case in zip(axes, ("dm", "ct")):
        pw = b92["local_power"][case]["power"]
        cs = sorted(pw, key=float)
        for key, lab, proc in curves:
            style(ax, key, lab, [float(c) for c in cs], [pw[c][proc] for c in cs])
        ax.axhline(C.ALPHA, color="0.5", linewidth=F.LINE_WIDTH / 2)
        ax.set_ylim(F.POWER_YMIN, F.POWER_YMAX)
        dress(ax, CASE_TITLE[case], "c")
    axes[0].set_ylabel("potencia (n = %d)" % b92["config"]["n_local"], fontsize=F.FONT_SIZE)
    finish(fig, axes, path, F.BOTTOM_MARGIN)
    return path


def fig_theta_ladder(b92):
    path = os.path.join(FIG_DIR, "fig_theta_ladder_audit9.pdf")
    fig, axes = plt.subplots(1, 2, figsize=(F.WIDTH_DOUBLE, F.HEIGHT_TWO_PANEL), sharey=True)
    thetas = b92["config"]["thetas"]
    for ax, case in zip(axes, ("dm", "ct")):
        pw = b92["local_power"][case]["power"]
        for c, key in zip(F.LADDER_C, ("c5", "c10", "c15")):
            row = pw[str(c)]
            style(ax, key, "c = %g" % c, thetas, [(row["envelope"] - row["gls_t%g" % t]) * F.PP for t in thetas])
        ax.set_xticks(thetas)
        dress(ax, CASE_TITLE[case], "θ")
    axes[0].set_ylabel("brecha a la envolvente (pp)", fontsize=F.FONT_SIZE)
    finish(fig, axes, path, F.BOTTOM_MARGIN)
    return path


def fig_power_equalized(b91, prim):
    path = os.path.join(FIG_DIR, "fig_power_equalized_audit9.pdf")
    fig, axes = plt.subplots(2, 3, figsize=(F.WIDTH_DOUBLE, F.HEIGHT_EQUALIZED), sharey=True)
    curves = [("primary", "primaria", prim), ("rm", "RM", "rm_t0.1"), ("adf_sim", "ADF-sim", "adf"),
              ("pp_sim", "PP-sim", "pp"), ("dfgls_sim", "DF-GLS-sim", "dfgls"), ("mzt_sim", "MZ_t-GLS-sim", "mzt"),
              ("msb_sim", "MSB-GLS-sim", "msb")]
    for r, (pref, lab_row) in enumerate((("dgp1_", "DGP 1"), ("ct_power_", "con tendencia"))):
        for ax, n in zip(axes[r], F.EQ_N):
            cells = sorted((v for k, v in b91["cells"].items() if k.startswith(pref) and v["n"] == n), key=lambda v: -v["rho"])
            x = [v["rho"] for v in cells]
            for key, lab, proc in curves:
                style(ax, key, lab, x, [v["rates_sim"][proc]["rate"] for v in cells])
            ax.set_xlim(F.DGP1_RHO_MAX, min(x))
            ax.set_ylim(F.POWER_YMIN, F.POWER_YMAX)
            dress(ax, "%s, n = %d" % (lab_row, n), "ρ")
        axes[r][0].set_ylabel("potencia (tamaño igualado)", fontsize=F.FONT_SIZE)
    finish(fig, list(axes[0]), path, F.BOTTOM_MARGIN_EQUALIZED)
    return path


def fig_size_shift(b92, prim):
    path = os.path.join(FIG_DIR, "fig_size_shift_audit9.pdf")
    b3 = C.read_json("b3_comparators_audit8.json")
    fig, axes = plt.subplots(1, 2, figsize=(F.WIDTH_DOUBLE, F.HEIGHT_TWO_PANEL), sharey=True)
    curves = [("primary", "primaria", prim), ("adf_sim", "ADF-sim", "adf"), ("dfgls_sim", "DF-GLS-sim", "dfgls"),
              ("mzt_sim", "MZ_t-GLS-sim", "mzt"), ("msb_sim", "MSB-GLS-sim", "msb"), ("msbhac", "MSB-HAC", "msbhac")]
    mis = b92["misspec"]
    for ax, (key, title) in zip(axes, GARCH_PANELS):
        series = [(sk, lab, [(n, mis["c|garch_%s_n%d" % (key, n)]["delta_vs_independent"][proc]) for n in F.SIZE_N
                             if "c|garch_%s_n%d" % (key, n) in mis]) for sk, lab, proc in curves]
        awb = [(n, b3["paired_delta"]["garch_%s_n%d" % (key, n)]["awb"]) for n in F.SIZE_N
               if "awb" in b3["paired_delta"].get("garch_%s_n%d" % (key, n), {})]
        series.append(("awb", "AWB DF-GLS (A8)", awb))
        for sk, lab, pts in series:
            x = [p[0] for p in pts]
            y = [p[1]["delta"] * F.PP for p in pts]
            e = [p[1]["se"] * F.PP * F.Z95 for p in pts]
            style(ax, sk, lab, x, y)
            ax.fill_between(x, [a - b for a, b in zip(y, e)], [a + b for a, b in zip(y, e)], color=F.STYLE[sk][0],
                            alpha=F.BAND_ALPHA, linewidth=0)
        ax.axhline(0, color="0.5", linewidth=F.LINE_WIDTH / 2)
        ax.set_xscale("log")
        ax.set_xticks(list(F.SIZE_N))
        ax.set_xticklabels([str(n) for n in F.SIZE_N])
        dress(ax, title, "n")
    axes[0].set_ylabel("Δ de tamaño (pp)", fontsize=F.FONT_SIZE)
    finish(fig, axes, path, F.BOTTOM_MARGIN)
    return path


def fig_dgp3(b92, b95, prim):
    path = os.path.join(FIG_DIR, "fig_dgp3_audit9.pdf")
    b5 = C.read_json("b5_power_audit8.json")
    fig, axes = plt.subplots(1, 3, figsize=(F.WIDTH_DOUBLE, F.HEIGHT_THREE_PANEL), sharey=True)
    curves = [("primary", "primaria", prim), ("rm", "RM", "rm_t0.1"), ("adf_sim", "ADF-sim", "adf"),
              ("dfgls_sim", "DF-GLS-sim", "dfgls")]
    for ax, n in zip(axes, F.DGP3_N):
        cells = sorted((v for v in b92["dgp3"].values() if v["n"] == n), key=lambda v: v["r"])
        x = [v["r"] for v in cells]
        for key, lab, proc in curves:
            style(ax, key, lab, x, [v["rates"][proc]["rate"] for v in cells])
        if b95 is not None:
            pts = sorted((float(k.split("_r")[1].split("_n")[0]), v["awb"]["rate"]) for k, v in b95["cells"].items()
                         if k.startswith("dgp3_") and v["n"] == n)
            style(ax, "primary_awb", "primaria AWB", [p[0] for p in pts], [p[1] for p in pts])
        ab = sorted((v["r"], v["rates"]["awb"]["rate"]) for v in b5["dgp3"].values() if v["n"] == n and "awb" in v["rates"])
        style(ax, "awb_dfgls", "AWB DF-GLS (A8)", [p[0] for p in ab], [p[1] for p in ab])
        ax.axhline(C.ALPHA, color="0.5", linewidth=F.LINE_WIDTH / 2)
        dress(ax, "n = %d" % n, "r")
    axes[0].set_ylabel("tasa de rechazo (nula verdadera)", fontsize=F.FONT_SIZE)
    finish(fig, axes, path, F.BOTTOM_MARGIN)
    return path


def main():
    os.makedirs(FIG_DIR, exist_ok=True)
    os.makedirs(PAPER_FIG_DIR, exist_ok=True)
    plt.rcParams.update({"font.size": F.FONT_SIZE, "pdf.fonttype": 42})
    b92 = C.read_json("b92_theta_audit9.json")
    b91 = C.read_json("b91_equalized_audit9.json")
    b95 = C.read_json("b95_awb_audit9.json") if os.path.exists(os.path.join(C.RESULTS, "b95_awb_audit9.json")) else None
    prim = "gls_t%g" % b92["primary_theta"]
    paths = [fig_local_power(b92, prim), fig_theta_ladder(b92), fig_power_equalized(b91, prim), fig_size_shift(b92, prim),
             fig_dgp3(b92, b95, prim)]
    figs = {}
    for p in paths:
        dst = os.path.join(PAPER_FIG_DIR, os.path.basename(p))
        shutil.copyfile(p, dst)
        figs[os.path.basename(p)] = {"sha256": C.sha256_file(p), "paper_copy": C.rel(dst),
                                     "paper_copy_sha256": C.sha256_file(dst), "bytes": os.path.getsize(p)}
    srcs = ["b92_theta_audit9.json", "b91_equalized_audit9.json", "b3_comparators_audit8.json", "b5_power_audit8.json"]
    if b95 is not None:
        srcs.append("b95_awb_audit9.json")
    out = {"provenance": C.provenance(__file__, seed_family=C.FAMILY["B9.7"]), "primary_theta": b92["primary_theta"],
           "sources": srcs, "figures": figs,
           "notes": {"fig_size_shift_audit9.pdf": "AWB DF-GLS arrastrado de A8 (b3_comparators_audit8.json, referencia "
                                                  "gaussiana independiente de la familia 92); el resto, referencia de B9.2",
                     "fig_dgp3_audit9.pdf": "ADF y DF-GLS con valor critico simulado; AWB DF-GLS de A8 (b5_power_audit8.json)"}}
    C.write_result(OUT, out, __file__)
    C.register_outputs(__file__, paths + [os.path.join(PAPER_FIG_DIR, os.path.basename(p)) for p in paths], out["provenance"])
    for k, v in figs.items():
        print(k, v["sha256"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
