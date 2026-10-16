"""
Auditoria A17 - B17.4 (enmienda 7, lectura E7.4): coherencia tipo B13.Q Q3 SOLO sobre
(a) las lineas que cambian del v17 al v18 (diff por archivo .tex), y
(b) las tablas S2.1, S4.3, S7.1 y S9.2 del suplemento reconstruido (supplementary/).
Solo lee JSON, codigo, los zips del v17/v18 y supplementary/. Compila el v18 en un directorio temporal (pdflatex x2 con el
.bbl entregado) para la comprobacion de la retirada del stub.
Salida: experiments/results/coherence_v18_audit17.json.
"""
import difflib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit17_common as C                                         # noqa: E402
import audit16_code_check as K                                     # noqa: E402
import audit16_supplement as S16                                   # noqa: E402
import audit13_q_claims as QC                                      # noqa: E402
import audit13_t_tables as TT                                      # noqa: E402

OUT = os.path.join(C.RESULTS, "coherence_v18_audit17.json")
SUPP = os.path.join(C.REPO, "supplementary")
T16 = os.path.join(C.RESULTS, "tables_audit16")
T13 = os.path.join(C.RESULTS, "tables_audit13")
PDFLATEX = S16.PDFLATEX
BOUND_DEC = 1


# ---------------------------------------------------------------------------
# utilidades
# ---------------------------------------------------------------------------
def norm_nl(s):
    return s.replace("\r\n", "\n")


def evaluate(text, tpl, vals, bounds=()):
    m = re.search(QC.pattern(tpl), text)
    if m is None:
        return {"found": False, "template": tpl}
    rows = []
    for i, (p, x) in enumerate(zip(m.groups(), vals)):
        if x is None:
            rows.append({"printed": p, "value": None, "verdict": "sin fuente"})
            continue
        up = i in bounds
        conv = QC.conventions(p, x, up)
        holds = (x <= float(p) + QC.BOUND_EPS) if up else True
        rows.append({"printed": p, "value": x, "conventions": conv, "bound": "upper" if up else None, "bound_holds": holds,
                     "verdict": "confirma" if conv and holds else "corrige", "correct": None if conv and holds else QC.correct(p, x, "upper" if up else None)})
    return {"found": True, "line": text[:m.start()].count("\n") + 1, "quote": re.sub(r"\s+", " ", m.group(0)), "numbers": rows,
            "verdict": "confirma" if all(r["verdict"] == "confirma" for r in rows) else "corrige"}


def compile_v18():
    tmp = tempfile.mkdtemp(prefix="a17_v18c_")
    with zipfile.ZipFile(C.ZIP_V18) as z:
        for n in z.namelist():
            if n.endswith("/"):
                continue
            rel = n.split("/", 1)[1] if "/" in n else n
            p = os.path.join(tmp, rel)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "wb") as fh:
                fh.write(z.read(n))
    for _ in range(2):
        subprocess.run([PDFLATEX, "-interaction=nonstopmode", "main.tex"], cwd=tmp, capture_output=True, text=True, encoding="utf-8", errors="replace")
    log = open(os.path.join(tmp, "main.log"), encoding="utf-8", errors="replace").read()
    pages = re.search(r"Output written on .*?\((\d+) pages?", log)
    res = {"errors": len(re.findall(r"^! ", log, flags=re.M)), "undefined_references": len(re.findall(r"Reference `[^']*' on page \d+ undefined", log)),
           "undefined_citations": len(re.findall(r"Citation `[^']*' on page \d+ undefined", log)),
           "overfull": len(re.findall(r"Overfull \\hbox", log)), "pages": int(pages.group(1)) if pages else None}
    shutil.rmtree(tmp, ignore_errors=True)
    return res


# ---------------------------------------------------------------------------
# (a) diff v17 -> v18
# ---------------------------------------------------------------------------
def hunks(v17, v18):
    out = []
    for f in sorted(set(v17.files) | set(v18.files)):
        if not f.endswith(".tex"):
            continue
        a, b = norm_nl(v17.files.get(f, "")).splitlines(), norm_nl(v18.files.get(f, "")).splitlines()
        sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == "equal":
                continue
            out.append({"file": f, "tag": tag, "v17_lines": [i1 + 1, i2], "v18_lines": [j1 + 1, j2], "removed": a[i1:i2], "added": b[j1:j2]})
    return out


def lp_trend_max():
    return max(abs(QC.gap("ct", c, p)) for c in QC.LP_C() if c > 0 for p in (QC.PRIM, "msb", "dfgls", "mzt"))


def classify(h, ctx):
    """Asigna cada hunk a su comprobacion (E7.4a)."""
    f, add = h["file"], " ".join(h["added"])
    rem = " ".join(h["removed"])
    if f == "main.tex" and "@currentlabel{S2.1}" in rem:
        return "stub", [{"check": "stub de tab:serial retirado de main.tex", "holds": "@currentlabel{S2.1}" not in ctx["v18"].files["main.tex"]},
                        {"check": "compilacion del v18 sin referencias indefinidas", "holds": ctx["v18c"]["undefined_references"] == 0},
                        {"check": "compilacion del v18 sin errores", "holds": ctx["v18c"]["errors"] == 0}]
    if f == "sec2_statistics.tex" and "T_n" in add:
        cc = ctx["code_cites"]
        return "Tn", [{"check": "M y DF-GLS con T_n = n + 1 (%s; %s)" % (cc["gls_a"]["where"], cc["arch_ct"]["where"]), "holds": True},
                      {"check": "MSB-B: T_n = n (constante, %s) y n + 1 (tendencia, %s)" % (cc["msbb_gls_const"]["where"], cc["msbb_gls_trend"]["where"]),
                       "holds": True}]
    if f == "sec2_statistics.tex" and ("mathrm{MSB}" in add or "mathrm{MZ}" in add or "T = n + 1" in add or "common sample" in add
                                       or "k_{\\max}" in add or "DF-GLS is" in add or "t = k+1" in add or "intercept" in add):
        m = ctx["mstats"]
        return "mstats", [{"check": "evaluacion literal de eq:mstats (E7.1): MSB rel <= 1e-12 y MZ_t abs <= 1e-10", "holds": m["passes"]},
                          {"check": "k_max del texto = codigo", "holds": m["description"]["kmax_agrees"]},
                          {"check": "MAIC del texto en la muestra comun = k del codigo", "holds": m["description"]["maic_agrees"]},
                          {"check": "t de DF-GLS en t = k+1..n = arch.DFGLS", "holds": m["description"]["dfgls_sample_agrees"]}]
    if f == "sec3_theory.tex":
        b = ctx["boot35"]
        return "boot35", [{"check": "afirmaciones de la seccion 3.5 frente a bootUR y al motor: 0 'difiere' (E7.2)", "holds": b["summary"]["difiere"] == 0},
                          {"check": "comprobaciones de la seccion 3.5 sin fallos", "holds": not b["checks_failed"]}]
    if f == "sec4_montecarlo.tex" and "within" in add:
        x = lp_trend_max()
        r = evaluate(add, "the four tests are within $<>$ points", [x], bounds=(0,))
        return "within", [{"check": "'within %s' como cota del maximo %.6g" % (r["numbers"][0]["printed"], x), "holds": r["verdict"] == "confirma",
                           "detail": r}]
    if f == "sec4_montecarlo.tex" and "\\input" in add:
        names = re.findall(r"\\input\{tables/([^}]*)\}", add)
        out = []
        for nm in names:
            got = norm_nl(ctx["v18"].files.get("tables/%s.tex" % nm, ""))
            ref = norm_nl(open(os.path.join(T16, nm + ".tex"), encoding="utf-8").read()) if os.path.exists(os.path.join(T16, nm + ".tex")) else None
            out.append({"check": "tables/%s.tex del v18 = tables_audit16/%s.tex" % (nm, nm), "holds": ref is not None and got == ref})
        return "inputs", out
    if f.startswith("tables/"):
        nm = os.path.splitext(os.path.basename(f))[0]
        if h["added"] and not h["removed"]:
            got = norm_nl(ctx["v18"].files.get(f, ""))
            p = os.path.join(T16, nm + ".tex")
            ref = norm_nl(open(p, encoding="utf-8").read()) if os.path.exists(p) else None
            return "table_added", [{"check": "%s del v18 = tables_audit16/%s.tex" % (f, nm), "holds": ref is not None and got == ref}]
        if h["removed"] and not h["added"]:
            used = any(("\\input{tables/%s}" % nm) in t for k, t in ctx["v18"].files.items() if k.endswith(".tex"))
            return "table_removed", [{"check": "%s ya no se usa en el v18" % f, "holds": not used}]
    return "sin clasificar", []


def numbers_in(h):
    toks = []
    for l in h["added"]:
        for m in re.finditer(r"(?<![A-Za-z_\\\d.])-?\d+(?:\.\d+)?", re.sub(r"\\cite[pt]?\{[^}]*\}|~\\cite\{[^}]*\}", " ", l)):
            toks.append(m.group(0))
    return toks


# ---------------------------------------------------------------------------
# (b) tablas del suplemento
# ---------------------------------------------------------------------------
def strip_comments(s):
    return "\n".join(l for l in norm_nl(s).splitlines() if not l.lstrip().startswith("%")).strip()


def float_of(tex, label):
    i = tex.index("\\label{%s}" % label)
    a = tex.rfind("\\begin{table}", 0, i)
    b = tex.index("\\end{table}", i)
    return tex[a:b]


def tab_s21(tex):
    a12 = C.read_json("bA_ma_audit12.json")
    recs, s_tex, _, region = TT.serial()
    supp = open(os.path.join(SUPP, "tables", "tab_serial_audit13.tex"), encoding="utf-8").read()
    fl = float_of(tex, "tab:serial")
    lo, hi = S16.A15S.TB.fdec(region[0], 4, "binary"), None
    d = 4
    while round(region[1], d) != region[1]:
        d += 1
    hi = S16.A15S.TB.fdec(region[1], d, "binary")
    return {"table": "S2.1 (tab:serial)", "regenerated_equals_supplement": strip_comments(s_tex) == strip_comments(supp),
            "cells": len(recs), "note_checks": [
                {"check": "region [%s, %s] en la nota" % (lo, hi), "holds": ("[%s, %s]" % (lo, hi)) in fl},
                {"check": "2x10^4 caminos (config.N_size = %d)" % a12["config"]["N_size"], "holds": a12["config"]["N_size"] == 20000 and "2\\times10^4" in fl.replace(" ", "")},
                {"check": "N_cal = 5x10^5 (config.N_cal = %d)" % a12["config"]["N_cal"], "holds": a12["config"]["N_cal"] == 500000 and "5\\times10^5" in fl.replace(" ", "")}]}


def tab_s43(tex):
    cfg = C.read_json("e_awb_audit13.json")
    reg = cfg["exact_region_2000"]
    supp = open(os.path.join(SUPP, "tables", "tab_awb_audit13.tex"), encoding="utf-8").read()
    src = open(os.path.join(T13, "tab_awb_audit13.tex"), encoding="utf-8").read()
    gate = C.read_json("tables_audit13.json")["tables"]["awb"]["gate"]
    fl = float_of(tex, "tab:awb")
    return {"table": "S4.3 (tab:awb)", "identical_to_tables_audit13": strip_comments(src) == strip_comments(supp), "a13_gate": gate,
            "note_checks": [
                {"check": "%d caminos comunes (config.N_sim)" % cfg["config"]["N_sim"], "holds": ("%d common paths" % cfg["config"]["N_sim"]) in fl},
                {"check": "R = %d replicas (config.B)" % cfg["config"]["B"], "holds": ("$R = %d$" % cfg["config"]["B"]) in fl},
                {"check": "sin 'B = 399'", "holds": "B = 399" not in fl},
                {"check": "region [%s, %s] para 2000 caminos" % (S16.A15S.TB.fdec(reg[0], 4, "binary"), S16.A15S.TB.fdec(reg[1], 4, "binary")),
                 "holds": ("[%s, %s]" % (S16.A15S.TB.fdec(reg[0], 4, "binary"), S16.A15S.TB.fdec(reg[1], 4, "binary"))) in fl}],
            "observation": "el p-valor del AWB de A13 es %s; la seccion 3.5 da (1 + #{T* <= T})/(R + 1) para las tres calibraciones de MZ_t" % cfg["config"]["pvalue"]}


def tab_s71(tex):
    e4 = C.read_json("e4_slope_audit15.json")["b"]
    t = open(os.path.join(SUPP, "tables", "s7_hac_a_rates.tex"), encoding="utf-8").read()
    keys = ("slope_B_pre_script", "R2_B_pre_script", "slope_B_ceil_script", "R2_B_ceil_script", "slope_B_pre_lib", "slope_g1s", "slope_g2s")
    rows, bad = [], []
    for lab, r in e4.items():
        m = re.search(r"^%s &(.*)\\\\" % re.escape(lab), t, flags=re.M)
        cells = [c.strip().replace("$-$", "-") for c in m.group(1).split("&")] if m else []
        want = [S16.A15S.TB.fdec(r[k], 4, "binary") for k in keys]
        ok = cells == want
        rows.append({"process": lab, "printed": cells, "json_binary": want, "equal": ok})
        if not ok:
            bad.append(lab)
    sent = re.search(r"The slope of 1/3 follows from the Andrews rule", tex) is not None
    return {"table": "S7.1 (tab:hacrates)", "rows": rows, "all_equal": not bad,
            "s7_sentence_present": sent,
            "slopes_vs_one_third": {lab: {"B_pre_script": r["slope_B_pre_script"], "B_pre_lib": r["slope_B_pre_lib"]} for lab, r in e4.items()}}


def tab_s92(tex):
    app = C.read_json("e_application_audit13.json")["summary"]
    v13 = C.read_json("b103_application_audit10.json")["summary"]
    dev = C.read_json("deviation_table_audit8.json")["rows"]
    a5 = C.read_json("real_data_comparison_audit5b.json")["summary"]["a1_50k"]
    fl = float_of(tex, "tab:deviations")
    items = [
        ("pilot", "Registered statistic: mean FP $<> \\to <>$", [dev[0]["preregistered_value"], dev[0]["deployed_value"]],
         "deviation_table_audit8.json rows[0]"),
        ("stat_window", "Mean FP $<> \\to <>$; detections $<> \\to <>$; mean latency $<> \\to <>$ days \\\\ \\addlinespace Window "
         "& -- & $\\theta = 0$ instead of the $\\theta = 0.02$ selected by the registered rule of Section~S5 & Mean FP $<> \\to <>$; "
         "detections $<> \\to <>$; mean latency $<> \\to <>$ days",
         [app["rhat_prereg"]["fp_mean"], app["final"]["fp_mean"], app["rhat_prereg"]["detections"], app["final"]["detections"],
          app["rhat_prereg"]["mean_latency_detected"], app["final"]["mean_latency_detected"], v13["final"]["fp_mean"], app["final"]["fp_mean"],
          v13["final"]["detections"], app["final"]["detections"], v13["final"]["mean_latency_detected"], app["final"]["mean_latency_detected"]],
         "e_application_audit13.json summary; b103_application_audit10.json summary.final (theta 0.02)"),
        ("dkw", "uniform error $<>$ by", [QC.dkw(dev[1]["n_cal"] if "n_cal" in dev[1] else 5 * 10 ** 4)], "formula DKW con N_cal = 5e4"),
        ("awb", "$R = 399$ & Mean FP $<> \\to <>$; detections $<> \\to <>$; latency $<> \\to <>$",
         [app["final"]["fp_mean"], app["final_awb"]["fp_mean"], app["final"]["detections"], app["final_awb"]["detections"],
          app["final"]["mean_latency_detected"], app["final_awb"]["mean_latency_detected"]], "e_application_audit13.json summary"),
        ("ncal", "moved its mean FP to $<>$ with the same <> detections", [a5["mean_fp"]["ours"], a5["detections"]["ours"]],
         "real_data_comparison_audit5b.json summary.a1_50k.<mean_fp|detections>.ours"),
    ]
    out = []
    for key, tpl, vals, src in items:
        r = evaluate(fl, tpl, vals)
        r.update(key=key, source=src)
        out.append(r)
    return {"table": "S9.2 (tab:deviations)", "items": out, "R_399": "$R = 399$" in fl, "B_399_left": "B = 399" in fl,
            "all_confirm": all(x.get("verdict") == "confirma" for x in out)}


def main():
    v17, v18 = C.v17(), C.v18()
    v18c = compile_v18()
    ctx = {"v18": v18, "v18c": v18c, "mstats": C.read_json("mstats_v18_audit17.json"), "boot35": C.read_json("boot35_v18_audit17.json")}
    cc = {}
    code =K.read_lines(os.path.join(HERE, "audit8_unitroot.py"))
    af, alab = K.arch_file()
    arch = K.read_lines(af)
    cc["gls_a"] = K.cite("experiments/audit8_unitroot.py", code, r"a = 1\.0 \+ cbar / T", r"def gls_detrend")
    cc["arch_ct"] = K.cite(alab, arch, r"ct = c / nobs", r"class DFGLS")
    cc["msbb_gls_const"] = K.cite("src/stationarity_test/rm_core.py", K.read_lines(os.path.join(C.REPO, "src", "stationarity_test", "rm_core.py")),
                                  r"a = 1\.0 \+ cbar / n", r"def gls_mean")
    cc["msbb_gls_trend"] = K.cite("src/stationarity_test/deterministics.py", K.read_lines(os.path.join(C.REPO, "src", "stationarity_test", "deterministics.py")),
                                  r"alpha = 1\.0 \+ cbar / T", r"def detrend_qd")
    ctx["code_cites"] = cc
    hs = hunks(v17, v18)
    rows = []
    for h in hs:
        kind, checks = classify(h, ctx)
        rows.append({**h, "kind": kind, "checks": checks, "numbers": numbers_in(h),
                     "verdict": "coincide" if checks and all(c["holds"] for c in checks) else ("sin clasificar" if not checks else "revisar")})
    tex = open(os.path.join(SUPP, "supplement.tex"), encoding="utf-8").read()
    tabs = [tab_s21(tex), tab_s43(tex), tab_s71(tex), tab_s92(tex)]
    out = {"provenance": C.provenance(__file__), "reading": "enmienda 7, lectura E7.4",
           "inputs": {"v17_zip_sha256": v17.sha256, "v18_zip_sha256": v18.sha256, "supplement_tex_sha256": C.sha256_file(os.path.join(SUPP, "supplement.tex"))},
           "v18_compile": v18c, "a_diff": rows, "b_tables": tabs,
           "summary": {"hunks": len(rows), "coincide": sum(1 for r in rows if r["verdict"] == "coincide"),
                       "revisar": [(r["file"], r["v18_lines"]) for r in rows if r["verdict"] == "revisar"],
                       "sin_clasificar": [(r["file"], r["v18_lines"]) for r in rows if r["verdict"] == "sin clasificar"]}}
    C.write_result(OUT, out, __file__)
    print("v18:", v18c)
    for r in rows:
        print("(a)", r["file"], r["v18_lines"], r["kind"], r["verdict"], [c["check"] for c in r["checks"] if not c["holds"]], r["numbers"])
    for t in tabs:
        print("(b)", t["table"], {k: v for k, v in t.items() if k not in ("table", "rows", "items", "note_checks", "slopes_vs_one_third", "a13_gate")},
              [c["check"] for c in t.get("note_checks", []) if not c["holds"]],
              [(x.get("key"), x.get("verdict")) for x in t.get("items", [])])
    return 0


if __name__ == "__main__":
    sys.exit(main())
