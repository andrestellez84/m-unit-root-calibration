"""
Auditoria A11 - T1: las seis figuras de A10 con texto en ingles, desde los mismos JSON.

Mismos nombres de archivo (sufijo _audit10, el .tex los referencia asi), en
experiments/figures y paper/figures. Los datos se preparan exactamente como en
make_figures_audit10 (regenerate_five y gain_points); solo cambian titulos, ejes,
leyendas y dos detalles de marcas del eje x (protocolo_audit11, lectura 4).

Igualdad de datos: se interceptan Axes.plot, Axes.fill_between y Axes.axhline en
dos corridas, la de A10 (make_figures_audit10 en una carpeta temporal) y la nueva,
y se comparan los arrays float64 llamada a llamada con np.array_equal. Los JSON de
A10 (figures_audit10.json, manifest_audit10.json) no se tocan.

Salidas: los seis PDF, experiments/results/figures_audit11.json.
"""
import contextlib
import hashlib
import os
import shutil
import sys
import tempfile

import matplotlib
import matplotlib.ticker
matplotlib.use("Agg")
import matplotlib.axes                                             # noqa: E402
import matplotlib.figure                                           # noqa: E402
import matplotlib.pyplot as plt                                    # noqa: E402
import numpy as np                                                 # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit11_common as C                                         # noqa: E402
import audit11_figconfig as F                                      # noqa: E402
import make_figures_audit9 as M9                                   # noqa: E402
import make_figures_audit10 as M10                                 # noqa: E402

OUT = os.path.join(C.RESULTS, "figures_audit11.json")
ORDER = ("fig_local_power_audit10.pdf", "fig_theta_ladder_audit10.pdf", "fig_power_equalized_audit10.pdf",
         "fig_size_shift_audit10.pdf", "fig_dgp3_audit10.pdf", "fig_calibration_gain_audit10.pdf")
CASES = (("dm", "c"), ("ct", "ct"))


# ---------------------------------------------------------------------------
# Registro de los datos graficados
# ---------------------------------------------------------------------------
class Recorder:
    def __init__(self):
        self.calls = []

    def add(self, kind, arrays):
        self.calls.append((kind, [np.asarray(a, dtype=np.float64).copy() for a in arrays]))

    def split(self):
        """Llamadas agrupadas por figura, en el orden de savefig."""
        figs, cur = {}, []
        for kind, arrs in self.calls:
            if kind == "savefig":
                figs[self.names.pop(0)] = cur
                cur = []
            else:
                cur.append((kind, arrs))
        return figs


@contextlib.contextmanager
def recording():
    rec = Recorder()
    rec.names = []
    orig = {"plot": matplotlib.axes.Axes.plot, "fill_between": matplotlib.axes.Axes.fill_between,
            "axhline": matplotlib.axes.Axes.axhline, "savefig": matplotlib.figure.Figure.savefig}

    def plot(self, *args, **kw):
        rec.add("plot", [a for a in args if not isinstance(a, str)])
        return orig["plot"](self, *args, **kw)

    def fill_between(self, x, y1, y2=0, **kw):
        rec.add("fill_between", [x, y1, y2])
        return orig["fill_between"](self, x, y1, y2, **kw)

    def axhline(self, y=0, *args, **kw):
        rec.add("axhline", [y])
        return orig["axhline"](self, y, *args, **kw)

    def savefig(self, fname, *args, **kw):
        rec.names.append(os.path.basename(str(fname)).replace("_audit9.pdf", "_audit10.pdf"))
        rec.calls.append(("savefig", []))
        return orig["savefig"](self, fname, *args, **kw)
    matplotlib.axes.Axes.plot = plot
    matplotlib.axes.Axes.fill_between = fill_between
    matplotlib.axes.Axes.axhline = axhline
    matplotlib.figure.Figure.savefig = savefig
    try:
        yield rec
    finally:
        matplotlib.axes.Axes.plot = orig["plot"]
        matplotlib.axes.Axes.fill_between = orig["fill_between"]
        matplotlib.axes.Axes.axhline = orig["axhline"]
        matplotlib.figure.Figure.savefig = orig["savefig"]


def digest(calls):
    h = hashlib.sha256()
    for kind, arrs in calls:
        h.update(kind.encode())
        for a in arrs:
            h.update(str(a.shape).encode())
            h.update(np.ascontiguousarray(a).tobytes())
    return h.hexdigest()


def compare(old, new):
    out = {}
    for name in ORDER:
        a, b = old[name], new[name]
        same_kinds = [k for k, _ in a] == [k for k, _ in b]
        eq = same_kinds and all(len(x) == len(y) and all(np.array_equal(u, v, equal_nan=True) for u, v in zip(x, y))
                                for (_, x), (_, y) in zip(a, b))
        out[name] = {"calls_a10": len(a), "calls_a11": len(b), "values_a10": int(sum(u.size for _, x in a for u in x)),
                     "values_a11": int(sum(u.size for _, x in b for u in x)), "same_call_sequence": same_kinds,
                     "bitwise_identical": bool(eq), "sha256_a10": digest(a), "sha256_a11": digest(b)}
    return out


# ---------------------------------------------------------------------------
# Figuras en ingles (logica de make_figures_audit9 / make_figures_audit10)
# ---------------------------------------------------------------------------
def fig_local_power(b92, prim, path):
    fig, axes = plt.subplots(1, 2, figsize=(F.WIDTH_DOUBLE, F.HEIGHT_TWO_PANEL), sharey=True)
    curves = [("envelope", "Envelope (P_T)", "envelope"),
              ("primary", "%s (θ = %g)" % (F.PRIMARY_LABEL, b92["primary_theta"]), prim),
              ("msb", "MSB-GLS", "msb"), ("dfgls", "DF-GLS", "dfgls"), ("mzt", "MZ_t-GLS", "mzt")]
    if prim != "gls_t0":
        curves.append(("theta0", "%s (θ = 0)" % F.PRIMARY_LABEL, "gls_t0"))
    for ax, case in zip(axes, ("dm", "ct")):
        pw = b92["local_power"][case]["power"]
        cs = sorted(pw, key=float)
        for key, lab, proc in curves:
            M9.style(ax, key, lab, [float(c) for c in cs], [pw[c][proc] for c in cs])
        ax.axhline(C.ALPHA, color="0.5", linewidth=F.LINE_WIDTH / 2)
        ax.set_ylim(F.POWER_YMIN, F.POWER_YMAX)
        M9.dress(ax, F.CASE_TITLE_EN[case], "c")
    axes[0].set_ylabel("Power (n = %d)" % b92["config"]["n_local"], fontsize=F.FONT_SIZE)
    M9.finish(fig, axes, path, F.BOTTOM_MARGIN)


def fig_theta_ladder(b92, path):
    fig, axes = plt.subplots(1, 2, figsize=(F.WIDTH_DOUBLE, F.HEIGHT_TWO_PANEL), sharey=True)
    thetas = b92["config"]["thetas"]
    for ax, case in zip(axes, ("dm", "ct")):
        pw = b92["local_power"][case]["power"]
        for c, key in zip(F.LADDER_C, ("c5", "c10", "c15")):
            row = pw[str(c)]
            M9.style(ax, key, "c = %g" % c, thetas, [(row["envelope"] - row["gls_t%g" % t]) * F.PP for t in thetas])
        ax.set_xticks(thetas)
        ax.set_xticklabels([F.LADDER_TICK_FORMAT % t for t in thetas])
        for i, lab in enumerate(ax.get_xticklabels()):
            if i in F.LADDER_TICK_ALIGN:
                lab.set_horizontalalignment(F.LADDER_TICK_ALIGN[i])
        M9.dress(ax, F.CASE_TITLE_EN[case], "θ")
    axes[0].set_ylabel("Distance to envelope (pp)", fontsize=F.FONT_SIZE)
    M9.finish(fig, axes, path, F.BOTTOM_MARGIN)


def fig_power_equalized(b91, prim, path):
    fig, axes = plt.subplots(2, 3, figsize=(F.WIDTH_DOUBLE, F.HEIGHT_EQUALIZED), sharey=True)
    curves = [("primary", F.PRIMARY_LABEL, prim), ("rm", "RM", "rm_t0.1"), ("adf_sim", "ADF-sim", "adf"),
              ("pp_sim", "PP-sim", "pp"), ("dfgls_sim", "DF-GLS-sim", "dfgls"), ("mzt_sim", "MZ_t-GLS-sim", "mzt"),
              ("msb_sim", "MSB-GLS-sim", "msb")]
    for r, (pref, lab_row) in enumerate(F.EQ_ROWS_EN):
        for ax, n in zip(axes[r], F.EQ_N):
            cells = sorted((v for k, v in b91["cells"].items() if k.startswith(pref) and v["n"] == n), key=lambda v: -v["rho"])
            x = [v["rho"] for v in cells]
            for key, lab, proc in curves:
                M9.style(ax, key, lab, x, [v["rates_sim"][proc]["rate"] for v in cells])
            ax.set_xlim(F.DGP1_RHO_MAX, min(x))
            ax.set_ylim(F.POWER_YMIN, F.POWER_YMAX)
            M9.dress(ax, "%s, n = %d" % (lab_row, n), "ρ")
        axes[r][0].set_ylabel("Power (equalized size)", fontsize=F.FONT_SIZE)
    M9.finish(fig, list(axes[0]), path, F.BOTTOM_MARGIN_EQUALIZED)


def fig_size_shift(b92, prim, path):
    b3 = C.read_json("b3_comparators_audit8.json")
    fig, axes = plt.subplots(1, 2, figsize=(F.WIDTH_DOUBLE, F.HEIGHT_TWO_PANEL), sharey=True)
    curves = [("primary", F.PRIMARY_LABEL, prim), ("adf_sim", "ADF-sim", "adf"), ("dfgls_sim", "DF-GLS-sim", "dfgls"),
              ("mzt_sim", "MZ_t-GLS-sim", "mzt"), ("msb_sim", "MSB-GLS-sim", "msb"), ("msbhac", "MSB-HAC", "msbhac")]
    mis = b92["misspec"]
    for ax, (key, title) in zip(axes, F.GARCH_PANELS_EN):
        series = [(sk, lab, [(n, mis["c|garch_%s_n%d" % (key, n)]["delta_vs_independent"][proc]) for n in F.SIZE_N
                             if "c|garch_%s_n%d" % (key, n) in mis]) for sk, lab, proc in curves]
        awb = [(n, b3["paired_delta"]["garch_%s_n%d" % (key, n)]["awb"]) for n in F.SIZE_N
               if "awb" in b3["paired_delta"].get("garch_%s_n%d" % (key, n), {})]
        series.append(("awb", "AWB DF-GLS", awb))
        for sk, lab, pts in series:
            x = [p[0] for p in pts]
            y = [p[1]["delta"] * F.PP for p in pts]
            e = [p[1]["se"] * F.PP * F.Z95 for p in pts]
            M9.style(ax, sk, lab, x, y)
            ax.fill_between(x, [a - b for a, b in zip(y, e)], [a + b for a, b in zip(y, e)], color=F.STYLE[sk][0],
                            alpha=F.BAND_ALPHA, linewidth=0)
        ax.axhline(0, color="0.5", linewidth=F.LINE_WIDTH / 2)
        ax.set_xscale("log")
        ax.set_xticks(list(F.SIZE_N))
        ax.set_xticklabels([str(n) for n in F.SIZE_N])
        M9.dress(ax, title, "n")
    axes[0].set_ylabel("Size shift (pp)", fontsize=F.FONT_SIZE)
    M9.finish(fig, axes, path, F.BOTTOM_MARGIN)


def fig_dgp3(b92, b95, prim, path):
    b5 = C.read_json("b5_power_audit8.json")
    fig, axes = plt.subplots(1, 3, figsize=(F.WIDTH_DOUBLE, F.HEIGHT_THREE_PANEL), sharey=True)
    curves = [("primary", F.PRIMARY_LABEL, prim), ("rm", "RM", "rm_t0.1"), ("adf_sim", "ADF-sim", "adf"),
              ("dfgls_sim", "DF-GLS-sim", "dfgls")]
    for ax, n in zip(axes, F.DGP3_N):
        cells = sorted((v for v in b92["dgp3"].values() if v["n"] == n), key=lambda v: v["r"])
        x = [v["r"] for v in cells]
        for key, lab, proc in curves:
            M9.style(ax, key, lab, x, [v["rates"][proc]["rate"] for v in cells])
        if b95 is not None:
            pts = sorted((float(k.split("_r")[1].split("_n")[0]), v["awb"]["rate"]) for k, v in b95["cells"].items()
                         if k.startswith("dgp3_") and v["n"] == n)
            M9.style(ax, "primary_awb", "%s, AWB" % F.PRIMARY_LABEL, [p[0] for p in pts], [p[1] for p in pts])
        ab = sorted((v["r"], v["rates"]["awb"]["rate"]) for v in b5["dgp3"].values() if v["n"] == n and "awb" in v["rates"])
        M9.style(ax, "awb_dfgls", "AWB DF-GLS", [p[0] for p in ab], [p[1] for p in ab])
        ax.axhline(C.ALPHA, color="0.5", linewidth=F.LINE_WIDTH / 2)
        M9.dress(ax, "n = %d" % n, "r")
    axes[0].set_ylabel("Rejection rate (null true)", fontsize=F.FONT_SIZE)
    M9.finish(fig, axes, path, F.BOTTOM_MARGIN)


def fig_calibration_gain(pts, path):
    fig, axes = plt.subplots(1, 2, figsize=(F.WIDTH_DOUBLE, F.HEIGHT_TWO_PANEL), sharey=True)
    curves = (("cv_at_n", "%s, critical value at n" % F.PRIMARY_LABEL),
              ("cv_big", "%s, critical value at n = 20,000" % F.PRIMARY_LABEL),
              ("msb_pub", "MSB-GLS, published asymptotic critical value"))
    for ax, (case, _) in zip(axes, CASES):
        ref = pts[case]["cv_at_n"]
        ns = sorted(ref)
        ax.fill_between(ns, [ref[n]["region"][0] for n in ns], [ref[n]["region"][1] for n in ns],
                        color=F.STYLE["region"][0], alpha=F.SHADE_ALPHA * 2, linewidth=0,
                        label="Exact region (N at each point)")
        for key, lab in curves:
            x = sorted(pts[case][key])
            M10.style(ax, key, lab, x, [pts[case][key][n]["rate"] for n in x])
        ax.axhline(C.ALPHA, color="0.5", linewidth=F.LINE_WIDTH / 2)
        ax.set_xscale("log")
        ax.xaxis.set_minor_locator(matplotlib.ticker.NullLocator())
        ax.set_xticks(list(F.GAIN_N))
        ax.set_xticklabels(["" if n in F.GAIN_HIDDEN_TICK_LABELS else str(n) for n in F.GAIN_N],
                           rotation=F.GAIN_TICK_ROTATION)
        ax.set_ylim(F.GAIN_YMIN, F.GAIN_YMAX)
        M9.dress(ax, F.CASE_TITLE_EN[case], "n")
    axes[0].set_ylabel("Empirical size", fontsize=F.FONT_SIZE)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=F.GAIN_LEGEND_NCOL, fontsize=F.LEGEND_SIZE, frameon=False,
               bbox_to_anchor=(0.5, F.GAIN_LEGEND_BOTTOM))
    fig.subplots_adjust(bottom=F.BOTTOM_MARGIN, wspace=F.SUBPLOT_WSPACE, hspace=F.SUBPLOT_HSPACE)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Entradas (identicas a make_figures_audit10.regenerate_five y gain_points)
# ---------------------------------------------------------------------------
def inputs(theta):
    b92 = dict(C.read_json("b92_theta_audit9.json"))
    b92["primary_theta"] = theta
    eq = C.read_json("b103_equalized_audit10.json")
    b91_like = {"cells": {k: v for k, v in eq["cells"].items() if k.startswith(("dgp1_", "ct_power_"))}}
    b92_dgp3 = dict(b92)
    b92_dgp3["dgp3"] = {k: {"n": v["n"], "r": v["r"], "rates": v["rates_sim"]} for k, v in eq["cells"].items()
                        if k.startswith("dgp3_")}
    awb = C.read_json("b103_awb_audit10.json") if M10.have("b103_awb_audit10.json") else None
    return b92, b91_like, b92_dgp3, awb, M10.gain_points(theta)


def draw_all(theta, out_dir):
    b92, b91_like, b92_dgp3, awb, pts = inputs(theta)
    prim = "gls_t%g" % theta
    p = {name: os.path.join(out_dir, name) for name in ORDER}
    fig_local_power(b92, prim, p[ORDER[0]])
    fig_theta_ladder(b92, p[ORDER[1]])
    fig_power_equalized(b91_like, prim, p[ORDER[2]])
    fig_size_shift(b92, prim, p[ORDER[3]])
    fig_dgp3(b92_dgp3, awb, prim, p[ORDER[4]])
    fig_calibration_gain(pts, p[ORDER[5]])
    return [p[name] for name in ORDER]


def draw_a10(theta, out_dir):
    saved = M10.FIG_DIR
    M10.FIG_DIR = out_dir
    try:
        M10.regenerate_five(theta)
        M10.fig_calibration_gain(theta, M10.gain_points(theta))
    finally:
        M10.FIG_DIR = saved


def main():
    os.makedirs(C.FIGURES, exist_ok=True)
    os.makedirs(C.PAPER_FIGURES, exist_ok=True)
    plt.rcParams.update({"font.size": F.FONT_SIZE, "pdf.fonttype": 42})
    theta = C.read_json("b101_theta_audit10.json")["primary_theta"]
    a10 = C.read_json("figures_audit10.json")["figures"]
    before = {name: {"sha256_disk": C.sha256_file(os.path.join(C.FIGURES, name)),
                     "sha256_figures_audit10": a10[name]["sha256"],
                     "paper_copy_sha256_disk": C.sha256_file(os.path.join(C.PAPER_FIGURES, name))} for name in ORDER}
    tmp = tempfile.mkdtemp(prefix="figs_audit11_")
    try:
        with recording() as r10:
            draw_a10(theta, tmp)
        with recording() as r11:
            paths = draw_all(theta, C.FIGURES)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    identity = compare(r10.split(), r11.split())
    figs = {}
    for p in paths:
        name = os.path.basename(p)
        dst = os.path.join(C.PAPER_FIGURES, name)
        shutil.copyfile(p, dst)
        figs[name] = {"sha256": C.sha256_file(p), "bytes": os.path.getsize(p), "paper_copy": C.rel(dst),
                      "paper_copy_sha256": C.sha256_file(dst), "before": before[name], "data": identity[name]}
    out = {"provenance": C.provenance(__file__, seed_family=C.FAMILY["T1"]), "primary_theta": theta,
           "sources": ["b92_theta_audit9.json", "b103_equalized_audit10.json", "b103_awb_audit10.json",
                       "b3_comparators_audit8.json", "b5_power_audit8.json", "b101_theta_audit10.json",
                       "b103_lown_audit10.json", "b103_finite_audit10.json"],
           "reference_code": "experiments/make_figures_audit10.py (corrida en carpeta temporal)",
           "all_bitwise_identical": all(v["bitwise_identical"] for v in identity.values()), "figures": figs}
    C.write_result(OUT, out, __file__)
    C.register_outputs(__file__, paths + [os.path.join(C.PAPER_FIGURES, os.path.basename(p)) for p in paths],
                       out["provenance"])
    for k, v in figs.items():
        print(k, v["sha256"], "datos identicos" if v["data"]["bitwise_identical"] else "DATOS DISTINTOS",
              v["data"]["calls_a11"], v["data"]["values_a11"])
    return 0 if out["all_bitwise_identical"] else 1


if __name__ == "__main__":
    sys.exit(main())
