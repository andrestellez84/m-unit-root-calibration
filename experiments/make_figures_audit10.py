"""
Auditoria A10 - B10.5: figuras finales. Lee solo JSON; PDF vectorial, doble columna
(19 cm), legibles en escala de grises.

Si el theta de B10.1 es 0.1, las cinco figuras de A9 siguen vigentes y solo se
genera la nueva. Si no, las cinco se regeneran con el theta final y sufijo
_audit10, con las funciones de make_figures_audit9 (se dibujan en una carpeta
temporal y se renombran, sin tocar las de A9), alimentadas con:
  - potencia local, escalera de theta y Delta GARCH: b92_theta_audit9.json (los
    cinco theta estan en A9);
  - tamano igualado (DGP 1 y tendencia) y DGP 3: b103_equalized_audit10.json;
  - AWB de la primaria en DGP 3: b103_awb_audit10.json.

Figura nueva fig_calibration_gain_audit10.pdf (dos paneles: demeaned y
tendencia): tamano empirico frente a n (escala log, 60-5000) de la primaria con
el valor critico calibrado en cada n, de la primaria con el valor critico de
n = 20 000 y de MSB-GLS con su valor asintotico publicado; banda en la region
exacta de la N de cada punto y linea en 0.05. Fuentes por n (protocolo, lectura
12): B10.1 (N = 100 000) en 200, 500, 1000; B10.3.7 (N = 50 000) en 60, 100, 150
si existe; B9.2 / B9.4 de A9 (N = 20 000) en el resto.

Salidas: experiments/figures/*_audit10.pdf, copia en paper/figures/ y
experiments/results/figures_audit10.json (incluye los puntos de la figura nueva).
"""
import os
import shutil
import sys
import tempfile

import matplotlib
import matplotlib.ticker
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                    # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit10_common as C                                         # noqa: E402
import audit10_figconfig as F                                      # noqa: E402
import make_figures_audit9 as M9                                   # noqa: E402

FIG_DIR = os.path.join(HERE, "figures")
PAPER_FIG_DIR = os.path.join(C.REPO, "paper", "figures")
OUT = os.path.join(C.RESULTS, "figures_audit10.json")
CASES = (("dm", "c", "demeaned"), ("ct", "ct", "con tendencia"))


def style(ax, key, label, x, y):
    col, mk, ls = F.STYLE[key]
    ax.plot(x, y, color=col, marker=mk or None, linestyle=ls, linewidth=F.LINE_WIDTH, markersize=F.MARKER_SIZE,
            label=label)


def have(name):
    return os.path.exists(os.path.join(C.RESULTS, name))


def point(rec, N, src, path):
    return {"rate": rec["rate"], "wilson": [rec["wilson_lower"], rec["wilson_upper"]], "N": N,
            "region": C.exact_region(N), "source": "experiments/results/" + src, "path": path}


def gain_points(theta):
    prim = "gls_t%g" % theta
    b101 = C.read_json("b101_theta_audit10.json")
    low = C.read_json("b103_lown_audit10.json") if have("b103_lown_audit10.json") else None
    b92 = C.read_json("b92_theta_audit9.json")
    fin_name = "b94_finite_sample_audit9.json" if theta == 0.1 else "b103_finite_audit10.json"
    fin = C.read_json(fin_name)
    out = {}
    for case, det, _ in CASES:
        pts = {"cv_at_n": {}, "cv_big": {}, "msb_pub": {}}
        for n in F.GAIN_N:
            k = "%s|%d" % (case, n)
            if k in b101["cells"]:
                c = b101["cells"][k]
                N = c["rates"][prim]["pooled"]["n"]
                pts["cv_at_n"][n] = point(c["rates"][prim]["pooled"], N, "b101_theta_audit10.json",
                                          "cells.%s.rates.%s.pooled" % (k, prim))
                pts["cv_big"][n] = point(c["size_with_cv_n20000"][prim], N, "b101_theta_audit10.json",
                                         "cells.%s.size_with_cv_n20000.%s" % (k, prim))
                pts["msb_pub"][n] = point(c["msb_published_cv"], N, "b101_theta_audit10.json",
                                          "cells.%s.msb_published_cv" % k)
            elif low is not None and k in low["cells"]:
                c = low["cells"][k]
                N = c["rates"][prim]["n"]
                pts["cv_at_n"][n] = point(c["rates"][prim], N, "b103_lown_audit10.json", "cells.%s.rates.%s" % (k, prim))
                pts["cv_big"][n] = point(c["size_with_cv_n20000"][prim], N, "b103_lown_audit10.json",
                                         "cells.%s.size_with_cv_n20000.%s" % (k, prim))
                pts["msb_pub"][n] = point(c["msb_published_cv"], N, "b103_lown_audit10.json",
                                          "cells.%s.msb_published_cv" % k)
            else:
                g = b92["gaussian_size"]["%s|%d" % (det, n)][prim]
                ac = fin["cases"][det]["approximation_cost"][str(n)]
                ms = fin["cases"][det]["approximation_cost_comparators"][str(n)]["msb"]["size_published_asymptotic"]
                pts["cv_at_n"][n] = point(g, g["n"], "b92_theta_audit9.json", "gaussian_size.%s|%d.%s" % (det, n, prim))
                pts["cv_big"][n] = point(ac["size_with_cv_n20000"], ac["size_with_cv_n20000"]["n"], fin_name,
                                         "cases.%s.approximation_cost.%d.size_with_cv_n20000" % (det, n))
                pts["msb_pub"][n] = point(ms, ms["n"], fin_name,
                                          "cases.%s.approximation_cost_comparators.%d.msb.size_published_asymptotic" % (det, n))
        out[case] = pts
    return out


def fig_calibration_gain(theta, pts):
    path = os.path.join(FIG_DIR, "fig_calibration_gain_audit10.pdf")
    fig, axes = plt.subplots(1, 2, figsize=(F.WIDTH_DOUBLE, F.HEIGHT_TWO_PANEL), sharey=True)
    curves = (("cv_at_n", "primaria (θ = %g), valor crítico en n" % theta),
              ("cv_big", "primaria, valor crítico de n = 20 000"),
              ("msb_pub", "MSB-GLS, valor crítico asintótico publicado"))
    for ax, (case, _, title) in zip(axes, CASES):
        ref = pts[case]["cv_at_n"]
        ns = sorted(ref)
        ax.fill_between(ns, [ref[n]["region"][0] for n in ns], [ref[n]["region"][1] for n in ns],
                        color=F.STYLE["region"][0], alpha=F.SHADE_ALPHA * 2, linewidth=0, label="región exacta (N del punto)")
        for key, lab in curves:
            x = sorted(pts[case][key])
            style(ax, key, lab, x, [pts[case][key][n]["rate"] for n in x])
        ax.axhline(C.ALPHA, color="0.5", linewidth=F.LINE_WIDTH / 2)
        ax.set_xscale("log")
        ax.xaxis.set_minor_locator(matplotlib.ticker.NullLocator())
        ax.set_xticks(list(F.GAIN_N))
        ax.set_xticklabels([str(n) for n in F.GAIN_N], rotation=F.GAIN_TICK_ROTATION)
        ax.set_ylim(F.GAIN_YMIN, F.GAIN_YMAX)
        M9.dress(ax, title, "n")
    axes[0].set_ylabel("tamaño empírico", fontsize=F.FONT_SIZE)
    M9.finish(fig, axes, path, F.BOTTOM_MARGIN)
    return path


def regenerate_five(theta):
    """Las cinco figuras de A9 con el theta final (carpeta temporal, renombradas a _audit10)."""
    b92 = dict(C.read_json("b92_theta_audit9.json"))
    b92["primary_theta"] = theta
    eq = C.read_json("b103_equalized_audit10.json")
    b91_like = {"cells": {k: v for k, v in eq["cells"].items() if k.startswith(("dgp1_", "ct_power_"))}}
    b92_dgp3 = dict(b92)
    b92_dgp3["dgp3"] = {k: {"n": v["n"], "r": v["r"], "rates": v["rates_sim"]} for k, v in eq["cells"].items()
                        if k.startswith("dgp3_")}
    awb = C.read_json("b103_awb_audit10.json") if have("b103_awb_audit10.json") else None
    prim = "gls_t%g" % theta
    tmp = tempfile.mkdtemp(prefix="figs_audit10_")
    saved = M9.FIG_DIR
    M9.FIG_DIR = tmp
    try:
        made = [M9.fig_local_power(b92, prim), M9.fig_theta_ladder(b92), M9.fig_power_equalized(b91_like, prim),
                M9.fig_size_shift(b92, prim), M9.fig_dgp3(b92_dgp3, awb, prim)]
    finally:
        M9.FIG_DIR = saved
    out = []
    for p in made:
        dst = os.path.join(FIG_DIR, os.path.basename(p).replace("_audit9.pdf", "_audit10.pdf"))
        shutil.move(p, dst)
        out.append(dst)
    shutil.rmtree(tmp, ignore_errors=True)
    srcs = ["b92_theta_audit9.json", "b103_equalized_audit10.json", "b3_comparators_audit8.json", "b5_power_audit8.json"]
    if awb is not None:
        srcs.append("b103_awb_audit10.json")
    return out, srcs


def main():
    os.makedirs(FIG_DIR, exist_ok=True)
    os.makedirs(PAPER_FIG_DIR, exist_ok=True)
    plt.rcParams.update({"font.size": F.FONT_SIZE, "pdf.fonttype": 42})
    theta = C.read_json("b101_theta_audit10.json")["primary_theta"]
    paths, srcs = [], ["b101_theta_audit10.json"]
    a9_valid = theta == 0.1
    if not a9_valid:
        p5, s5 = regenerate_five(theta)
        paths += p5
        srcs += s5
    pts = gain_points(theta)
    paths.append(fig_calibration_gain(theta, pts))
    figs = {}
    for p in paths:
        dst = os.path.join(PAPER_FIG_DIR, os.path.basename(p))
        shutil.copyfile(p, dst)
        figs[os.path.basename(p)] = {"sha256": C.sha256_file(p), "paper_copy": C.rel(dst),
                                     "paper_copy_sha256": C.sha256_file(dst), "bytes": os.path.getsize(p)}
    a9figs = C.read_json("figures_audit9.json")["figures"] if a9_valid else None
    out = {"provenance": C.provenance(__file__, seed_family=C.FAMILY["B10.5"]), "primary_theta": theta,
           "a9_figures_remain_valid": a9_valid, "a9_figures": a9figs, "sources": srcs, "figures": figs,
           "calibration_gain_points": pts}
    C.write_result(OUT, out, __file__)
    C.register_outputs(__file__, paths + [os.path.join(PAPER_FIG_DIR, os.path.basename(p)) for p in paths], out["provenance"])
    for k, v in figs.items():
        print(k, v["sha256"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
