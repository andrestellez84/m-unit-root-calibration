"""
Auditoria A13 - B13.E(3): las seis figuras con theta = 0 como primaria (sufijo _audit13).

Mismo codigo de dibujo que A11 (make_figures_audit11, en ingles); solo cambian el
theta de la primaria y las fuentes que dependen de theta (protocol_audit13.md,
lectura 12):
  - potencia a tamano igualado y DGP 3: e_equalized_audit13.json;
  - AWB en la figura de DGP 3: e_awb_audit13.json;
  - ganancia de calibracion: n <= 150 de e_size_audit13.json (familia 141; MSB-GLS
    publicado de b103_lown_audit10.json), 200-1000 de b101_theta_audit10.json,
    2000 y 5000 de b92_theta_audit9.json (valor critico en n) y de
    e_calib_audit13.json (valor critico de n = 20 000 y MSB-GLS publicado);
  - potencia local, escalera de theta y desplazamiento GARCH: b92_theta_audit9.json.
Paso 0: con theta = 0.02 y las fuentes del v13, este generador produce exactamente
los datos que grafica A11 (draw_all de make_figures_audit11), llamada a llamada.
Las figuras _audit10 no se tocan.

Salidas: experiments/figures/ y paper/figures/fig_*_audit13.pdf, experiments/results/figures_audit13.json.
"""
import os
import shutil
import sys
import tempfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                    # noqa: E402
import numpy as np                                                 # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit13_common as C                                         # noqa: E402
import audit11_figconfig as F                                      # noqa: E402
import make_figures_audit10 as M10                                 # noqa: E402
import make_figures_audit11 as M11                                 # noqa: E402

OUT = os.path.join(C.RESULTS, "figures_audit13.json")
ORDER = tuple(n.replace("_audit10.pdf", "_audit13.pdf") for n in M11.ORDER)


def gain_points13(theta):
    prim = C.tname(theta)
    es = C.read_json("e_size_audit13.json")
    low = C.read_json("b103_lown_audit10.json")
    b101 = C.read_json("b101_theta_audit10.json")
    b92 = C.read_json("b92_theta_audit9.json")
    fin = C.read_json("e_calib_audit13.json")["cases_by_theta"][prim]
    out = {}
    for case, det in M11.CASES:
        pts = {"cv_at_n": {}, "cv_big": {}, "msb_pub": {}}
        for n in F.GAIN_N:
            k = "%s|%d" % (case, n)
            if k in b101["cells"]:
                c = b101["cells"][k]
                N = c["rates"][prim]["pooled"]["n"]
                pts["cv_at_n"][n] = M10.point(c["rates"][prim]["pooled"], N, "b101_theta_audit10.json",
                                              "cells.%s.rates.%s.pooled" % (k, prim))
                pts["cv_big"][n] = M10.point(c["size_with_cv_n20000"][prim], N, "b101_theta_audit10.json",
                                             "cells.%s.size_with_cv_n20000.%s" % (k, prim))
                pts["msb_pub"][n] = M10.point(c["msb_published_cv"], N, "b101_theta_audit10.json", "cells.%s.msb_published_cv" % k)
            elif k in es["cells"]:
                c = es["cells"][k]
                N = c["rates"][prim]["n"]
                pts["cv_at_n"][n] = M10.point(c["rates"][prim], N, "e_size_audit13.json", "cells.%s.rates.%s" % (k, prim))
                pts["cv_big"][n] = M10.point(c["size_with_cv_n20000"][prim], N, "e_size_audit13.json",
                                             "cells.%s.size_with_cv_n20000.%s" % (k, prim))
                m = low["cells"][k]["msb_published_cv"]
                pts["msb_pub"][n] = M10.point(m, m["n"], "b103_lown_audit10.json", "cells.%s.msb_published_cv" % k)
            else:
                g = b92["gaussian_size"]["%s|%d" % (det, n)][prim]
                ac = fin[det]["approximation_cost"][str(n)]
                ms = fin[det]["approximation_cost_comparators"][str(n)]["msb"]["size_published_asymptotic"]
                pts["cv_at_n"][n] = M10.point(g, g["n"], "b92_theta_audit9.json", "gaussian_size.%s|%d.%s" % (det, n, prim))
                pts["cv_big"][n] = M10.point(ac["size_with_cv_n20000"], ac["size_with_cv_n20000"]["n"], "e_calib_audit13.json",
                                             "cases_by_theta.%s.%s.approximation_cost.%d.size_with_cv_n20000" % (prim, det, n))
                pts["msb_pub"][n] = M10.point(ms, ms["n"], "e_calib_audit13.json",
                                              "cases_by_theta.%s.%s.approximation_cost_comparators.%d.msb.size_published_asymptotic"
                                              % (prim, det, n))
        out[case] = pts
    return out


def inputs(theta, sources):
    b92 = dict(C.read_json("b92_theta_audit9.json"))
    b92["primary_theta"] = theta
    if sources == "v13":
        eq = C.read_json("b103_equalized_audit10.json")
        awb = C.read_json("b103_awb_audit10.json")
        pts = M10.gain_points(theta)
    else:
        eq = C.read_json("e_equalized_audit13.json")
        awb = C.read_json("e_awb_audit13.json")
        pts = gain_points13(theta)
    b91_like = {"cells": {k: v for k, v in eq["cells"].items() if k.startswith(("dgp1_", "ct_power_"))}}
    b92_dgp3 = dict(b92)
    b92_dgp3["dgp3"] = {k: {"n": v["n"], "r": v["r"], "rates": v["rates_sim"]} for k, v in eq["cells"].items()
                        if k.startswith("dgp3_")}
    return b92, b91_like, b92_dgp3, awb, pts


def draw(theta, sources, out_dir, names):
    b92, b91_like, b92_dgp3, awb, pts = inputs(theta, sources)
    prim = C.tname(theta)
    p = [os.path.join(out_dir, n) for n in names]
    M11.fig_local_power(b92, prim, p[0])
    M11.fig_theta_ladder(b92, p[1])
    M11.fig_power_equalized(b91_like, prim, p[2])
    M11.fig_size_shift(b92, prim, p[3])
    M11.fig_dgp3(b92_dgp3, awb, prim, p[4])
    M11.fig_calibration_gain(pts, p[5])
    return p, pts


def calls_by_figure(rec, names):
    figs, cur, k = {}, [], 0
    for kind, arrs in rec.calls:
        if kind == "savefig":
            figs[names[k]] = cur
            cur, k = [], k + 1
        else:
            cur.append((kind, arrs))
    return figs


def same(a, b):
    return ([k for k, _ in a] == [k for k, _ in b]
            and all(len(x) == len(y) and all(np.array_equal(u, v, equal_nan=True) for u, v in zip(x, y))
                    for (_, x), (_, y) in zip(a, b)))


def main():
    os.makedirs(C.FIGURES, exist_ok=True)
    os.makedirs(C.PAPER_FIGURES, exist_ok=True)
    plt.rcParams.update({"font.size": F.FONT_SIZE, "pdf.fonttype": 42})
    tmp = tempfile.mkdtemp(prefix="figs_audit13_")
    try:
        with M11.recording() as r11:
            M11.draw_all(C.THETA_V13, tmp)
        with M11.recording() as r13v:
            draw(C.THETA_V13, "v13", tmp, ORDER)
        with M11.recording() as r13:
            paths, pts = draw(C.THETA, "a13", C.FIGURES, ORDER)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    a11 = calls_by_figure(r11, ORDER)
    v13 = calls_by_figure(r13v, ORDER)
    new = calls_by_figure(r13, ORDER)
    figs = {}
    for p in paths:
        name = os.path.basename(p)
        dst = os.path.join(C.PAPER_FIGURES, name)
        shutil.copyfile(p, dst)
        figs[name] = {"sha256": C.sha256_file(p), "bytes": os.path.getsize(p), "paper_copy": C.rel(dst),
                      "paper_copy_sha256": C.sha256_file(dst),
                      "paso0_v13_data_identical_to_a11": bool(same(a11[name], v13[name])),
                      "data_sha256": M11.digest(new[name]), "calls": len(new[name]),
                      "data": [[k, [np.asarray(a).tolist() for a in arrs]] for k, arrs in new[name]]}
    out = {"provenance": C.provenance(__file__, seed_family=None), "primary_theta": C.THETA,
           "reading": "protocol_audit13.md, lectura 12",
           "sources_theta_dependent": ["e_equalized_audit13.json", "e_awb_audit13.json", "e_size_audit13.json",
                                       "e_calib_audit13.json", "b101_theta_audit10.json", "b92_theta_audit9.json"],
           "sources_theta_free": ["b3_comparators_audit8.json", "b5_power_audit8.json", "b103_lown_audit10.json"],
           "paso0_all_identical": all(v["paso0_v13_data_identical_to_a11"] for v in figs.values()),
           "calibration_gain_points": {case: {k: {str(n): v for n, v in d.items()} for k, d in pp.items()}
                                       for case, pp in pts.items()},
           "figures": figs}
    C.write_result(OUT, out, __file__)
    C.register_outputs(__file__, paths + [os.path.join(C.PAPER_FIGURES, os.path.basename(p)) for p in paths],
                       out["provenance"])
    for k, v in figs.items():
        print(k, v["sha256"], "Paso 0", v["paso0_v13_data_identical_to_a11"])
    return 0 if out["paso0_all_identical"] else 1


if __name__ == "__main__":
    sys.exit(main())
