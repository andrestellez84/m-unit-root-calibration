"""
Auditoria A13 - B13.Q, Q2: las seis figuras de A13 con los rotulos del v14 (*_audit13q.pdf).

Mismo codigo de dibujo y mismas fuentes que make_figures_audit13 (protocol_audit13_amend1.md,
lectura 4). Solo cambian:
  - la etiqueta de la primaria: "RM-GLS" -> "MSB-B" (PRIMARY_LABEL de A11, sustituido en
    tiempo de ejecucion; audit11_figconfig no se toca);
  - fig_size_shift omite la serie "MSB-HAC" (msbhac, el estadistico anclado en la media con
    tau = 0).
Paso 0: los arrays graficados de las series que quedan son identicos bit a bit, llamada a
llamada, a los guardados en figures_audit13.json; las llamadas que faltan son exactamente
las de la serie msbhac (plot y banda de cada panel).

Salidas: experiments/figures/ y paper/figures/fig_*_audit13q.pdf,
experiments/results/figures_audit13q.json.
"""
import contextlib
import os
import shutil
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.figure                                           # noqa: E402
import matplotlib.pyplot as plt                                    # noqa: E402
import numpy as np                                                 # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit13_common as C                                         # noqa: E402
import audit11_figconfig as F                                      # noqa: E402
import make_figures_audit9 as M9                                   # noqa: E402
import make_figures_audit11 as M11                                 # noqa: E402
import make_figures_audit13 as M13                                 # noqa: E402

OUT = os.path.join(C.RESULTS, "figures_audit13q.json")
OLD_LABEL, NEW_LABEL = "RM-GLS", "MSB-B"
DROPPED = ("msbhac", "MSB-HAC")
ORDER = tuple(n.replace("_audit13.pdf", "_audit13q.pdf") for n in M13.ORDER)


def fig_size_shift_q(b92, prim, path):
    """M11.fig_size_shift sin la serie msbhac (mismo orden y estilo para las demas)."""
    b3 = C.read_json("b3_comparators_audit8.json")
    fig, axes = plt.subplots(1, 2, figsize=(F.WIDTH_DOUBLE, F.HEIGHT_TWO_PANEL), sharey=True)
    curves = [("primary", F.PRIMARY_LABEL, prim), ("adf_sim", "ADF-sim", "adf"), ("dfgls_sim", "DF-GLS-sim", "dfgls"),
              ("mzt_sim", "MZ_t-GLS-sim", "mzt"), ("msb_sim", "MSB-GLS-sim", "msb")]
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


def dropped_series_calls(b92):
    """Arrays (x, y, banda) que la serie msbhac aporta en cada panel de A13, desde b92."""
    mis = b92["misspec"]
    out = []
    for key, _ in F.GARCH_PANELS_EN:
        pts = [(n, mis["c|garch_%s_n%d" % (key, n)]["delta_vs_independent"][DROPPED[0]]) for n in F.SIZE_N
               if "c|garch_%s_n%d" % (key, n) in mis]
        x = [p[0] for p in pts]
        y = [p[1]["delta"] * F.PP for p in pts]
        e = [p[1]["se"] * F.PP * F.Z95 for p in pts]
        out.append([np.asarray(x, dtype=np.float64), np.asarray(y, dtype=np.float64)])
        out.append([np.asarray(x, dtype=np.float64), np.asarray([a - b for a, b in zip(y, e)], dtype=np.float64),
                    np.asarray([a + b for a, b in zip(y, e)], dtype=np.float64)])
    return out


@contextlib.contextmanager
def label_capture():
    """Registra titulos, ejes y leyendas de cada figura al guardarla."""
    cap = []
    orig = matplotlib.figure.Figure.savefig

    def savefig(self, fname, *args, **kw):
        texts = []
        for ax in self.axes:
            texts += [ax.get_title(), ax.get_xlabel(), ax.get_ylabel()] + list(ax.get_legend_handles_labels()[1])
        for lg in self.legends:
            texts += [t.get_text() for t in lg.get_texts()]
        cap.append((os.path.basename(str(fname)), sorted(set(t for t in texts if t))))
        return orig(self, fname, *args, **kw)
    matplotlib.figure.Figure.savefig = savefig
    try:
        yield cap
    finally:
        matplotlib.figure.Figure.savefig = orig


def as_arrays(stored):
    return [(k, [np.asarray(a, dtype=np.float64) for a in arrs]) for k, arrs in stored]


def align(old, new):
    """Emparejamiento voraz: old = new + llamadas eliminadas; devuelve (ok, eliminadas)."""
    j, removed = 0, []
    for kind, arrs in old:
        if j < len(new) and kind == new[j][0] and len(arrs) == len(new[j][1]) and all(
                np.array_equal(u, v, equal_nan=True) for u, v in zip(arrs, new[j][1])):
            j += 1
        else:
            removed.append((kind, arrs))
    return j == len(new), removed


def main():
    os.makedirs(C.FIGURES, exist_ok=True)
    os.makedirs(C.PAPER_FIGURES, exist_ok=True)
    plt.rcParams.update({"font.size": F.FONT_SIZE, "pdf.fonttype": 42})
    saved = (F.PRIMARY_LABEL, M11.fig_size_shift)
    F.PRIMARY_LABEL = NEW_LABEL
    M11.fig_size_shift = fig_size_shift_q
    try:
        with M11.recording() as rec, label_capture() as labels:
            paths, _ = M13.draw(C.THETA, "a13", C.FIGURES, ORDER)
    finally:
        F.PRIMARY_LABEL, M11.fig_size_shift = saved
    new = M13.calls_by_figure(rec, ORDER)
    a13 = C.read_json("figures_audit13.json")["figures"]
    b92 = C.read_json("b92_theta_audit9.json")
    expected_drop = dropped_series_calls(b92)
    figs = {}
    for p, (fname, texts) in zip(paths, labels):
        name = os.path.basename(p)
        old = as_arrays(a13[name.replace("_audit13q.pdf", "_audit13.pdf")]["data"])
        ok, removed = align(old, new[name])
        drop_ok = (len(removed) == len(expected_drop) and all(
            len(a) == len(b) and all(np.array_equal(u, v) for u, v in zip(a, b)) for (_, a), b in zip(removed, expected_drop))
                   if "size_shift" in name else not removed)
        dst = os.path.join(C.PAPER_FIGURES, name)
        shutil.copyfile(p, dst)
        figs[name] = {"sha256": C.sha256_file(p), "bytes": os.path.getsize(p), "paper_copy": C.rel(dst),
                      "paper_copy_sha256": C.sha256_file(dst), "source_a13": name.replace("_audit13q.pdf", "_audit13.pdf"),
                      "calls_a13": len(old), "calls_q": len(new[name]), "removed_calls": len(removed),
                      "remaining_identical_to_a13": bool(ok), "removed_are_msbhac": bool(drop_ok),
                      "texts": texts, "old_label_absent": all(OLD_LABEL not in t for t in texts),
                      "dropped_label_absent": all(DROPPED[1] not in t for t in texts),
                      "data_sha256": M11.digest(new[name])}
    passes = all(v["remaining_identical_to_a13"] and v["removed_are_msbhac"] and v["old_label_absent"]
                 and v["dropped_label_absent"] for v in figs.values())
    out = {"provenance": C.provenance(__file__, seed_family=None), "primary_theta": C.THETA,
           "reading": "protocol_audit13_amend1.md, lectura 4", "label_change": [OLD_LABEL, NEW_LABEL],
           "dropped_series": {"figure": "fig_size_shift_audit13q.pdf", "key": DROPPED[0], "label": DROPPED[1]},
           "reference": "figures_audit13.json (data)", "paso0_passes": passes, "figures": figs}
    C.write_result(OUT, out, __file__)
    C.register_outputs(__file__, paths + [os.path.join(C.PAPER_FIGURES, os.path.basename(p)) for p in paths],
                       out["provenance"])
    for k, v in figs.items():
        print(k, v["calls_a13"], "->", v["calls_q"], "eliminadas", v["removed_calls"], "identicas", v["remaining_identical_to_a13"],
              "msbhac", v["removed_are_msbhac"], "sin RM-GLS", v["old_label_absent"])
    return 0 if passes else 1


if __name__ == "__main__":
    sys.exit(main())
