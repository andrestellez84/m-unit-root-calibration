"""
Auditoria A11 - T5: cifras citadas del manuscrito v12 frente a los JSON.

Lee las frases directamente de paper_latex_v12.zip (sin extraerlo en el repo) y
registra archivo:linea y la cifra impresa. Regla (protocolo_audit11, lectura 8):
una cifra se confirma si el valor del JSON, redondeado a la precision impresa,
coincide; un rango "a to b" si min y max de las diferencias citadas redondean a a
y b; "about thirty" si la cantidad redondeada a la decena es 30; "more than
thirty" si la cantidad es > 30.

  1. sec5 "dropping it changes size by at most 0.1 points": b2_size_audit8.json (B2a).
  2. sec5 "rebalancing ... lowered power by 14 to 28 points":
     adaptive_size_power_audit5b.json (configuracion operativa alpha1_hac_Ncal50000,
     la de las columnas sigma_hat de la tabla de v11).
  3. sec1/sec2/sec5/sec7 "thirty points" al centrar en la media: b4_local_power_audit8.json.
  4. sec6, Tabla de la aplicacion, fila "Registered statistic":
     b103_application_audit10.json (rhat_prereg); A9 y A8 como referencia.
Tambien localiza las frases de T3 (sesgo del ancla) para las citas de la seccion 7.

Salida: experiments/results/t5_claims_audit11.json.
"""
import argparse
import os
import re
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit11_common as C                                         # noqa: E402

OUT = os.path.join(C.RESULTS, "t5_claims_audit11.json")
WORDS = {"thirty": 30}
REBAL_CONFIG = "alpha1_hac_Ncal50000"
REBAL_CELLS = ("DGP1_rho095_n200", "DGP1_rho097_n500", "DGP1_rho099_n1000")
B4_C = "10.0"
B4_THETA = "0.1"
PP = 100


class Manuscript:
    def __init__(self, path):
        self.path = path
        self.z = zipfile.ZipFile(path)
        self.names = {os.path.basename(n): n for n in self.z.namelist() if n.endswith(".tex")}

    def lines(self, fname):
        return self.z.read(self.names[fname]).decode("utf-8").splitlines()

    def find(self, fname, pattern, span=1):
        """Primera linea (1-indexada) cuya ventana de `span` lineas unidas casa con el patron."""
        L = self.lines(fname)
        for k in range(len(L)):
            parts = [l.strip() for l in L[k:k + span]]
            text = " ".join(parts)
            m = re.search(pattern, text)
            if m:
                ends = [sum(len(x) + 1 for x in parts[:j + 1]) for j in range(len(parts))]
                first = next(j for j, e in enumerate(ends) if m.start() < e)
                return {"file": "v12/" + fname, "line": k + 1 + first, "quote": text, "groups": list(m.groups())}
        raise KeyError("frase no encontrada en %s: %s" % (fname, pattern))


def decimals(s):
    return len(s.split(".")[1]) if "." in s else 0


def same_printed(value, printed):
    d = decimals(printed)
    return round(value, d) == round(float(printed), d)


def claim1(M):
    q = M.find("sec5_montecarlo.tex", r"dropping it changes size by at most \$([0-9.]+)\$ points", 2)
    b = C.read_json("b2_size_audit8.json")["B2a"]
    cells = b["cells"]
    evaluated = b["gate"]["cells_evaluated"]
    worst = max(evaluated, key=lambda k: abs(cells[k]["delta_pp"]))
    val = abs(cells[worst]["delta_pp"])
    printed = q["groups"][0]
    kinds = sorted({cells[k]["kind"] for k in evaluated})
    return {"quote": q, "printed": printed, "json": "b2_size_audit8.json",
            "json_path": "B2a.cells.<celda>.delta_pp (max |.| sobre B2a.gate.cells_evaluated); B2a.gate.max_abs_delta_pp",
            "max_abs_delta_pp": val, "gate_max_abs_delta_pp": b["gate"]["max_abs_delta_pp"], "cell": worst,
            "cells_evaluated": len(evaluated), "kinds": kinds, "comparison": "R = 0 frente a R = 0.5, RM theta = 0.1 (A8 B2a)",
            "min_mcnemar_p": b["gate"]["min_mcnemar_p"], "sign_test_p": b["gate"]["sign_test_p"],
            "N_sim": C.read_json("b2_size_audit8.json")["config"]["N_sim"], "N_cal": C.read_json("b2_size_audit8.json")["config"]["N_cal"],
            "confirmed": round(val, decimals(printed)) <= float(printed)}


def claim2(M):
    q = M.find("sec5_montecarlo.tex", r"lowered power by \$(\d+)\$ to \$(\d+)\$", 1)
    b = C.read_json("adaptive_size_power_audit5b.json")
    by_cfg = {}
    for cfg, v in b.items():
        if isinstance(v, dict) and all(c in v for c in REBAL_CELLS):
            d = {c: (v[c]["adaptive"] - v[c]["rebalanced"]) * PP for c in REBAL_CELLS}
            by_cfg[cfg] = {"diff_pp": d, "min": min(d.values()), "max": max(d.values()),
                           "rates": {c: {"adaptive": v[c]["adaptive"], "rebalanced": v[c]["rebalanced"]} for c in REBAL_CELLS}}
    op = by_cfg[REBAL_CONFIG]
    lo, hi = q["groups"]
    return {"quote": q, "printed": [lo, hi], "json": "adaptive_size_power_audit5b.json",
            "json_path": "%s.<celda>.adaptive - rebalanced" % REBAL_CONFIG, "operative_config": REBAL_CONFIG,
            "operative": op, "all_configs": by_cfg, "N_sim": None,
            "N_cal": int(re.search(r"Ncal(\d+)", REBAL_CONFIG).group(1)),
            "N_note": "el JSON no registra N_sim; N_cal sale del nombre de la configuracion",
            "confirmed": round(op["min"]) == int(lo) and round(op["max"]) == int(hi)}


def claim3(M):
    quotes = [M.find("sec1_introduction.tex", r"sample mean cost (more than|about) (\w+) points of local power", 2),
              M.find("sec2_statistic.tex", r"worth (more than|about) (\w+) points of local power", 2),
              M.find("sec5_montecarlo.tex", r"costs (about|more than) (\w+) points of local power", 2),
              M.find("sec7_conclusion.tex", r"cost (about|more than) (\w+) points of local", 2)]
    b = C.read_json("b4_local_power_audit8.json")
    out = {}
    for case in ("dm", "ct"):
        pw = b["cases"][case]["power"]
        gap = b["cases"][case]["gap_to_envelope"]
        thetas = sorted({k.split("_t")[1] for k in pw[B4_C] if k.startswith("gls_t")}, key=float)
        by = {}
        for t in thetas:
            costs = {c: (pw[c]["gls_t%s" % t] - pw[c]["rm_t%s" % t]) * PP for c in pw}
            cmax = max(costs, key=lambda c: costs[c])
            by[t] = {"power_rmgls": pw[B4_C]["gls_t%s" % t], "power_rm": pw[B4_C]["rm_t%s" % t],
                     "cost_pp": costs[B4_C], "gap_rm_pp": gap["rm_t%s" % t][B4_C] * PP,
                     "gap_rmgls_pp": gap["gls_t%s" % t][B4_C] * PP, "max_cost_pp_over_c": costs[cmax], "c_at_max_cost": cmax}
        out[case] = by
    main = out["dm"][B4_THETA]
    verdicts = []
    for q in quotes:
        kind, word = q["groups"]
        target = WORDS[word]
        ok = main["cost_pp"] > target if kind == "more than" else round(main["cost_pp"], -1) == target
        verdicts.append({"file": q["file"], "line": q["line"], "kind": kind, "number": target, "confirmed": ok,
                         "confirmed_if_gap_rm": (main["gap_rm_pp"] > target if kind == "more than"
                                                 else round(main["gap_rm_pp"], -1) == target)})
    g1 = b["gls_rule"]["G1"]
    return {"quotes": quotes, "json": "b4_local_power_audit8.json",
            "json_path": "cases.<caso>.power.%s y gap_to_envelope; gls_rule.G1" % B4_C, "n": b["config"]["n"],
            "c": float(B4_C), "theta_a8": float(B4_THETA), "thetas_available": sorted(out["dm"], key=float),
            "N_sim": b["config"]["N_power"], "N_cal": b["config"]["N_cal"],
            "by_case": out, "G1": g1, "verdicts": verdicts,
            "quantity_for_claim": "coste de centrar = potencia(RM-GLS) - potencia(RM), demeaned, c = 10, theta = 0.1",
            "confirmed": all(v["confirmed"] for v in verdicts)}


def claim4(M):
    q = M.find("sec6_application.tex", r"^Registered statistic & (.*) \\\\$", 1)
    printed = [s.strip() for s in q["groups"][0].split("&")]
    rate = M.find("sec6_application.tex", r"common false-alarm rate of \$([0-9.]+)\$", 2)
    out = {}
    for tag, name in (("A10", "b103_application_audit10.json"), ("A9", "b96_application_audit9.json"),
                      ("A8", "b6_application_audit8.json")):
        b = C.read_json(name)
        s, m = b["summary"]["rhat_prereg"], b["matched_rate"]["tests"]["rhat_prereg"]
        vals = [s["fp_mean"], s["fp_max"], s["detections"], s["mean_latency_detected"], m["false_alarm_episodes"],
                m["mean_run_length"], m["censored_latency_mean"]]
        out[tag] = {"json": name, "values": vals, "target_fpr": b["matched_rate"]["target_fpr_pooled_primary"],
                    "match": [same_printed(v, p) for v, p in zip(vals, printed)]}
    fields = ["fp_mean", "fp_max", "detections", "mean_latency_detected", "false_alarm_episodes", "mean_run_length",
              "censored_latency_mean"]
    return {"quote": q, "printed": printed, "fields": fields, "rate_quote": rate, "printed_rate": rate["groups"][0],
            "json_paths": ["summary.rhat_prereg.%s" % f for f in fields[:4]]
            + ["matched_rate.tests.rhat_prereg.%s" % f for f in fields[4:]],
            "by_audit": out, "rate_confirmed": same_printed(out["A10"]["target_fpr"], rate["groups"][0]),
            "confirmed": all(out["A10"]["match"])}


def t3_quotes(M):
    return {"remark_n2000": M.find("sec3_theory.tex", r"accurate at \$n = (\d+)\$ \(simulated \$([0-9.]+)\$ against \$([0-9.]+)\$\)", 2),
            "remark_n200": M.find("sec3_theory.tex", r"not at \$n = (\d+)\$ \(simulated \$([0-9.]+)\$ against \$([0-9.]+)\$\)", 2),
            "remark_kappa": M.find("sec3_theory.tex", r"kappa\(-7\) \\approx ([0-9.]+)", 1),
            "appendix": M.find("appA_proofs.tex", r"gives \$([0-9.]+)\$, \$([0-9.]+)\$ and \$([0-9.]+)\$", 2),
            "appendix_first_order": M.find("appA_proofs.tex", r"first-order values \$([0-9.]+)\$, \$([0-9.]+)\$ and \$([0-9.]+)\$", 2)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manuscript-zip", default=os.path.join(os.path.dirname(C.REPO), "paper_latex_v12.zip"))
    a = ap.parse_args()
    M = Manuscript(a.manuscript_zip)
    out = {"provenance": C.provenance(__file__, seed_family=C.FAMILY["T5"]),
           "manuscript": {"zip": os.path.basename(a.manuscript_zip), "sha256": C.sha256_file(a.manuscript_zip)},
           "claims": {"1": claim1(M), "2": claim2(M), "3": claim3(M), "4": claim4(M)}, "t3_quotes": t3_quotes(M)}
    C.write_result(OUT, out, __file__)
    for k, v in out["claims"].items():
        print(k, "confirmada" if v["confirmed"] else "NO confirmada")
    c3 = out["claims"]["3"]["by_case"]["dm"][B4_THETA]
    print("coste de centrar", c3)
    print("fila", out["claims"]["4"]["printed"], out["claims"]["4"]["by_audit"]["A10"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
