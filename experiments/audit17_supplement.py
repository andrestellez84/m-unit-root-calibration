"""
Auditoria A17 - B17.3 (enmienda 7, lectura E7.3): reconstruccion de supplementary/ con las ediciones del encargo B17.

Reutiliza audit16_supplement (sin modificarlo) y anade:
- "B = 399" -> "R = 399" en la nota de tab:awb (S4.3) y en tab:deviations (S9.2);
- nota de S2.1: extremo superior de la region para 2e4 caminos escrito sin redondear (bA_ma_audit12.json);
- S7: la frase literal del encargo despues de las tablas del HAC;
- S2: el parrafo sobre SB/SWB se sustituye por los detalles que el cuerpo del v18 no da y el resultado de invariancia
  de MZ_t (code_check_audit16.json); el parrafo del Paso 0 se conserva.
Las remisiones "of the main text" se numeran con la compilacion de control del v18. Cada edicion queda en el JSON.
Con --out <dir> genera alli (prueba). Salida: experiments/results/supplement_v18_audit17.json (o ..._trial_...).
"""
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit17_common as C                                         # noqa: E402
import audit16_supplement as S16                                   # noqa: E402

A15S = S16.A15S
OUT = os.path.join(C.RESULTS, "supplement_v18_audit17.json")
OUT_TRIAL = os.path.join(C.RESULTS, "supplement_v18_trial_audit17.json")
REG_DEC = 4
S7_SENTENCE = "The slope of 1/3 follows from the Andrews rule once $\\hat a$ settles; it says nothing about the stochastic part."
AWB_R = (r"B = 399", "R = 399")


def bound(x):
    d = REG_DEC
    while round(x, d) != x:
        d += 1
    return A15S.TB.fdec(x, d, "binary")


def region_edit():
    reg = C.read_json("bA_ma_audit12.json")["exact_region_20000"]
    lo, hi = bound(reg[0]), bound(reg[1])
    return ("S2_serial_table", r"\[%s, \d\.\d+\]" % re.escape(lo), "[%s, %s]" % (lo, hi)), (lo, hi)


def sb_swb_details():
    d = C.read_json("code_check_audit16.json")["c_invariance"]
    cells = d["cells"]
    bad = [k for k, v in cells.items() if not v["passes"]]
    worst = [cells[k]["diagnostic_worst_rel_mzt"] for k in bad]
    paths = sum(v["paths"] for v in cells.values())
    sci = S16.sci
    return (
        "Three details of the package are not in the main text. First, the SB draws the residuals with replacement from positions "
        "$0, \\dots, T - l$ only, with $l = \\mathrm{round}(1.75\\,T^{1/3})$ the default block length, so the last $l - 1$ residuals "
        "are never drawn. Second, the regression that defines the bootstrap data-generating process is not trimmed: its missing "
        "initial lags are filled with zeros, so the first $p + 1$ residuals are computed with some regressors set to zero, and the "
        "first of them is the detrended first observation itself; the autoregressive recursion that generates the bootstrap "
        "increments starts at zero, and $\\rw^*_0 = 0$. Third, the package reports the $p$-value $\\#\\{t^* < t\\}/B$, while our "
        "calibrations use $(1 + \\#\\{T^{*(r)} \\leq T\\})/(R + 1)$ and reject when it is at most $0.05$.\n\n"
        "The invariance of \\cref{prop:invariance} was checked numerically for MSB-GLS and MZ$_t$-GLS on %d Gaussian random walks "
        "($n \\in \\{%s\\}$, both deterministic cases), each under %d affine transformations: the lag selected by the MAIC never "
        "changed, and MSB changed by at most a relative $%s$. The relative change of MZ$_t$ reached $%s$, on paths on which MZ$_t$ is "
        "close to zero (%s), because its numerator $T^{-1}\\uhat_n^2 - s^2$ is then the difference of two nearly equal terms; the "
        "absolute change never exceeded $%s$." % (
            paths, ", ".join("%d" % n for n in d["config"]["n"]), len(d["config"]["a"]), sci(max(v["max_rel_msb"] for v in cells.values())),
            sci(max(v["max_rel_mzt"] for v in cells.values())), " and ".join("$%s$" % sci(w["mzt"]) for w in worst),
            sci(max(v["diagnostic_max_abs_mzt"] for v in cells.values()))))


def body_labels_v18(tmp):
    """S16.body_labels sobre el zip del v18 (sustitucion temporal de la entrada, restaurada al salir)."""
    c16 = S16.C
    old_zip, old_v17 = c16.ZIP_V17, c16.v17
    try:
        c16.ZIP_V17, c16.v17 = C.ZIP_V18, C.v18
        return S16.body_labels(tmp)
    finally:
        c16.ZIP_V17, c16.v17 = old_zip, old_v17


def sec6_integrity(v16, supp_tex, subs):
    """E6.6.4 repetida admitiendo solo las sustituciones declaradas (E7.3)."""
    src, _ = S16.extract(v16, "S9_application")
    for pat, rep in subs:
        src = re.sub(pat, rep, src)

    def nm(s):                            # misma normalizacion que audit16_supplement.sec6_integrity
        s = re.sub(r"\\(cref|Cref|ref)\{[^}]*\}", " ", s)
        s = re.sub(r"(Table|Section|Figure|Definition|Proposition|Remark|Theorem|equation|Equation)~\S+ of the main text", " ", s)
        s = re.sub(r"Section~S\d+", " ", s)
        s = re.sub(r"\\subsection\*?\{", r"\\subsection{", s)
        s = re.sub(r"\\label\{[^}]*\}", " ", s)
        return re.sub(r"\s+", " ", s).strip()
    a = supp_tex.index("\\label{supp:s9}")
    b = supp_tex.index("\\subsection*{Details}", a)
    sw = [w for w in nm(src).split(" ") if w]
    gw = " " + nm(supp_tex[a:b]) + " "
    missing = [" ".join(sw[i:i + 8]) for i in range(0, len(sw) - 7, 8) if " ".join(sw[i:i + 8]) not in gw]
    ns = re.findall(r"(?<![\w.])\d+(?:\.\d+)?", nm(src))
    ng = re.findall(r"(?<![\w.])\d+(?:\.\d+)?", nm(supp_tex[a:b]))
    return {"chunks_checked": len(range(0, len(sw) - 7, 8)), "chunks_missing": missing[:10], "n_missing": len(missing),
            "numbers_src": len(ns), "numbers_equal": ns == ng, "substitutions_admitted": [list(x) for x in subs]}


def main():
    args = sys.argv[1:]
    trial = "--out" in args
    supp = os.path.abspath(args[args.index("--out") + 1]) if trial else S16.SUPP_REAL
    if trial and os.path.normcase(supp) == os.path.normcase(S16.SUPP_REAL):
        raise SystemExit("--out no puede ser supplementary/")
    v16, v18 = C.v16(), C.v18()
    tmp = tempfile.mkdtemp(prefix="a17_v18_")
    body, v18c = body_labels_v18(tmp)
    shutil.rmtree(tmp, ignore_errors=True)
    redit, (lo, hi) = region_edit()
    new_edits = (redit, ("S4_breaks",) + AWB_R, ("S9_application",) + AWB_R)
    S16.EDITS = S16.EDITS + new_edits
    details = sb_swb_details()
    S16.SB_SWB_TEXT = details
    if os.path.exists(supp):
        shutil.rmtree(supp)
    A15S.SUPP = supp
    W = A15S.Writer()
    res = {"S1": A15S.s1(W), "S2": A15S.s2(W), "S3": A15S.s3(W), "S4": A15S.s4(W), "S5": A15S.s5(W), "S6": A15S.s6(W),
           "S7": A15S.s7(W), "S8": A15S.s8(W), "S9": A15S.s9(W)}
    renamed = {}
    for rel in list(W.files):
        base = os.path.basename(rel)
        if not rel.startswith("tables/"):
            continue
        for old, new in S16.RENAME:
            if base.startswith(old):
                nb = new + base[len(old):]
                os.replace(os.path.join(supp, rel), os.path.join(supp, "tables", nb))
                W.files["tables/" + nb] = W.files.pop(rel)
                renamed[base] = nb
                break
    for name in S16.A13_TABLES:
        W.copy("tables/%s.tex" % name, os.path.join(S16.T13, name + ".tex"))
    for name in ("tab_serial_asy_audit15", "tab_lag_audit15", "tab_boot_audit15", "tab_boot_note_audit15", "tab_fixedb_size_audit15",
                 "tab_fixedb_size_note_audit15"):
        W.copy("tables/%s.tex" % name, os.path.join(S16.T15, name + ".tex"))
    for name in ("tab_critMSB_audit14", "tab_critMSB_note_audit14"):
        W.copy("tables/%s.tex" % name, os.path.join(S16.C.C15.C14.TABLES, name + ".tex"))
    for name in A15S.DATA:
        W.copy("data/" + name, os.path.join(C.RESULTS, name))
    for name, folder in A15S.DATA_EXTRA.items():
        W.copy("data/" + name, os.path.join(folder, name))
    for name in ("code_check_audit16.json", "literals_v17b_audit16.json", "b1_paso0_v2_audit15.json", "b0_t3_audit15.json",
                 "mstats_v18_audit17.json", "boot35_v18_audit17.json"):
        if C.have(name):
            W.copy("data/" + name, os.path.join(C.RESULTS, name))
    os.makedirs(os.path.join(supp, "figures"), exist_ok=True)
    for fg in S16.FIGS:
        p = os.path.join(supp, "figures", fg + ".pdf")
        with open(p, "wb") as fh:
            fh.write(v16.read_bytes("figures/%s.pdf" % fg))
        W.files["figures/%s.pdf" % fg] = {"sources": ["paper_latex_v16.zip:figures/%s.pdf" % fg], "source_sha256": C.sha256_file(p)}
    btxt, nbib = S16.bib(v16, v18)
    W.text("references.bib", btxt, ["paper_latex_v18.zip:references.bib", "paper_latex_v16.zip:references.bib"])
    S, sec_map, reflog, sources, edits = S16.build(v16, v18, body, W, renamed)
    inserted = []
    for sid, title, items in S:
        if sid == "S7":
            i = next(j for j, x in enumerate(items) if "tab:hacmedian" in x) + 1
            items.insert(i, S7_SENTENCE)
            inserted.append({"section": "S7", "position": "despues de tab:hacmedian", "text": S7_SENTENCE})
        if sid == "S2":
            n_para = sum(1 for x in items if x == details)
            inserted.append({"section": "S2", "position": "sustituye el parrafo SB/SWB de A16", "text": details, "count": n_para})
    raw = S16.doc(S, v16, v18)
    sup_labels = set(re.findall(r"\\label\{([^}]*)\}", raw))
    extra = {"app:tables": "Section~S2", "sec:negative": "Section~S6", "sec:implementation": "the main text"}
    tex = S16.resolve_refs(raw, sup_labels, sec_map, body, extra, reflog)
    W.text("supplement.tex", tex, ["generado"])
    for rel in sorted(W.files):
        if rel.startswith("tables/") and rel.endswith(".tex"):
            p = os.path.join(supp, rel)
            src = open(p, encoding="utf-8").read()
            if re.search(r"\\(cref|Cref|ref)\{", src):
                n0 = len(reflog)
                new = S16.resolve_refs(src, sup_labels, sec_map, body, extra, reflog)
                for r in reflog[n0:]:
                    r["file"] = rel
                with open(p, "w", encoding="utf-8", newline="\n") as fh:
                    fh.write(new)
    W.text("README.md", S16.readme(W, S), ["generado"])
    man = []
    for dp, _, fs in os.walk(supp):
        for fn in sorted(fs):
            p = os.path.join(dp, fn)
            man.append("%s  %s" % (C.sha256_file(p), os.path.relpath(p, supp).replace("\\", "/")))
    W.text("MANIFEST.sha256", "\n".join(sorted(man, key=lambda s: s.split("  ", 1)[1])) + "\n", ["generado"])
    A15S.SUPP = supp
    sc = A15S.scan()
    comp = S16.compile_check(supp)
    lab = comp.pop("labels")
    numbering = {"S2": {l: lab.get(l) for l in S16.MAP_S2},
                 "S2_matches_map": [lab.get(l) for l in S16.MAP_S2] == ["S2.%d" % i for i in range(1, len(S16.MAP_S2) + 1)],
                 "tables": {k: v for k, v in lab.items() if k.startswith("tab:")}}
    main_refs = re.findall(r"(Table|Section|Figure|Definition|Proposition|Remark|Theorem|equation|Equation|Appendix)~(\S+) of the main text", tex)
    body_nums = {(S16.TYPE_NAME.get(t, t).lower(), n) for t, n in body.values()}
    bad_main = [x for x in main_refs if (x[0].lower(), x[1].strip("()")) not in body_nums]
    checks = {"B_399_left": len(re.findall(r"B = 399", tex)), "R_399": len(re.findall(r"R = 399", tex)),
              "region_old_left": len(re.findall(r"\[%s, 0\.0531\]" % re.escape(lo), tex)), "region_new": len(re.findall(re.escape("[%s, %s]" % (lo, hi)), tex)),
              "s7_sentence": tex.count(S7_SENTENCE), "s2_details": tex.count("Three details of the package are not in the main text")}
    out = {"provenance": C.provenance(__file__), "reading": "enmienda 7, lectura E7.3", "trial": trial,
           "inputs": {"v16_zip_sha256": v16.sha256, "v18_zip_sha256": v18.sha256},
           "v18_control_compile": v18c, "body_labels": {k: list(v) for k, v in body.items()},
           "b17_edits": [{"block": b, "pattern": p, "replacement": r} for b, p, r in new_edits], "b17_inserted": inserted, "b17_checks": checks,
           "editorial_edits": edits, "references": reflog, "unresolved": [r for r in reflog if r["how"] == "SIN RESOLVER"],
           "main_text_refs": {"count": len(main_refs), "not_in_v18_body": bad_main}, "numbering": numbering,
           "sec6_integrity": sec6_integrity(v16, tex, [AWB_R]), "bib_entries": nbib, "files": {k: v for k, v in sorted(W.files.items())},
           "n_files": len(W.files), "anonymization_scan": sc, "compile": comp}
    C.write_result(OUT_TRIAL if trial else OUT, out, __file__)
    print("archivos:", len(W.files), "| aciertos no-hash:", sc["non_hash_hits"], "| compilacion:", comp)
    print("S2 = mapa:", numbering["S2_matches_map"], "| sin resolver:", out["unresolved"], "| fuera del cuerpo:", bad_main)
    print("comprobaciones B17:", checks)
    print("ediciones:", [(e["block"], e["count"]) for e in edits])
    print("sec6:", out["sec6_integrity"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
