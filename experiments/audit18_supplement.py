"""
Auditoria A18 - B18.2-B18.4, suplemento (enmienda 8, lecturas E8.2-E8.4).

Reutiliza audit17_supplement (sin modificarlo) con la entrada paper_latex_v18b.zip para numerar las remisiones al cuerpo, y
anade una edicion: la frase del encargo al final de la nota de tab:awb (S4.3). Despues limpia las fechas de los PDF de
supplementary/figures (E8.3), regenera MANIFEST.sha256, recompila (control) y repite la busqueda de identificadores.
Con --out <dir> genera alli (prueba). Salida: experiments/results/supplement_v18b_audit18.json (o ..._trial_...).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit18_common as C                                         # noqa: E402
import audit17_supplement as S17                                   # noqa: E402

S16, A15S = S17.S16, S17.A15S
OUT = os.path.join(C.RESULTS, "supplement_v18b_audit18.json")
OUT_TRIAL = os.path.join(C.RESULTS, "supplement_v18b_trial_audit18.json")
AWB_SENTENCE = (r"The AWB p-value here is $\#\{S^{*} \leq S\}/R$, not the $(1 + \#)/(R + 1)$ of Section~3.5 of the main text.")
AWB_ANCHOR = r"(region \$\[0\.0405, 0\.0600\]\$ for 2000 paths\.)"
BOOTDEF = "sec:bootdef"


def main():
    args = sys.argv[1:]
    trial = "--out" in args
    supp = os.path.abspath(args[args.index("--out") + 1]) if trial else S16.SUPP_REAL
    c17 = S17.C
    # entrada v18b y salida de A18 (sustituciones en este proceso; los modulos de A16/A17 no se modifican en disco)
    c17.ZIP_V18, c17.v18 = C.ZIP_V18B, C.v18b
    c17.write_result, c17.provenance = (lambda *a, **k: None), C.provenance
    S17.OUT = S17.OUT_TRIAL = os.path.join(C.RESULTS, "_discard_audit18.json")
    edit = ("S4_breaks", AWB_ANCHOR, r"\1 " + AWB_SENTENCE.replace("\\", r"\\"))
    S16.EDITS = S16.EDITS + (edit,)
    captured = {}
    orig_write = c17.write_result

    def capture(path, obj, script):
        captured["obj"] = obj
    c17.write_result = capture
    sys.argv = [sys.argv[0]] + (["--out", supp] if trial else [])
    S17.main()
    c17.write_result = orig_write
    d = captured["obj"]
    tex = open(os.path.join(supp, "supplement.tex"), encoding="utf-8").read()
    # E8.3: fechas de los PDF del suplemento
    pdfs = {}
    for fn in sorted(os.listdir(os.path.join(supp, "figures"))):
        if fn.lower().endswith(".pdf"):
            pdfs["figures/" + fn] = C.strip_pdf_dates(os.path.join(supp, "figures", fn))
    # E8.4: MANIFEST regenerado, compilacion de control y busqueda de identificadores
    man = []
    for dp, _, fs in os.walk(supp):
        for fn in sorted(fs):
            p = os.path.join(dp, fn)
            if os.path.relpath(p, supp).replace("\\", "/") != "MANIFEST.sha256":
                man.append("%s  %s" % (C.sha256_file(p), os.path.relpath(p, supp).replace("\\", "/")))
    mtxt = "\n".join(sorted(man, key=lambda s: s.split("  ", 1)[1])) + "\n"
    with open(os.path.join(supp, "MANIFEST.sha256"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(mtxt)
    A15S.SUPP = supp
    sc = A15S.scan()
    comp = S16.compile_check(supp)
    comp.pop("labels", None)
    i = tex.index("\\label{tab:awb}")
    awb_float = tex[tex.rfind("\\begin{table}", 0, i):tex.index("\\end{table}", i)]
    body = d["body_labels"]
    awb_cfg = C.read_json("e_awb_audit13.json")["config"]
    edits = [x for x in d["editorial_edits"] if x["pattern"] == AWB_ANCHOR]
    manifest_ok = all(C.sha256_file(os.path.join(supp, l.split("  ", 1)[1])) == l.split("  ", 1)[0] for l in mtxt.strip().splitlines())
    d.update({"provenance": C.provenance(__file__), "reading": "enmienda 8, lecturas E8.2-E8.4 (construccion con audit17_supplement)",
              "inputs": {"v18b_zip_sha256": C.sha256_file(C.ZIP_V18B), "v16_zip_sha256": d["inputs"]["v16_zip_sha256"],
                         "note": "body_labels y v18_control_compile proceden de paper_latex_v18b.zip"},
              "b18_edit": {"block": "S4_breaks", "anchor": AWB_ANCHOR, "sentence": AWB_SENTENCE, "count": edits[0]["count"] if edits else 0,
                           "in_tab_awb_note": AWB_SENTENCE in awb_float, "occurrences_in_supplement": tex.count(AWB_SENTENCE),
                           "bootdef_is_3_5": body.get(BOOTDEF, [None, None])[1] == "3.5", "bootdef_label": body.get(BOOTDEF),
                           "a13_awb_pvalue": awb_cfg["pvalue"], "a13_awb_replicas": awb_cfg["B"]},
              "b18_pdf_dates": pdfs, "manifest_regenerated": {"entries": len(man), "all_match": manifest_ok},
              "anonymization_scan": sc, "compile": comp, "n_files": len(man) + 1})
    for k in ("files",):
        for rel, v in d[k].items():
            if rel in pdfs:
                v["sha256_after_date_strip"] = pdfs[rel]["sha256_after"]
    C.write_result(OUT_TRIAL if trial else OUT, d, __file__)
    disc = os.path.join(C.RESULTS, "_discard_audit18.json")
    if os.path.exists(disc):
        os.remove(disc)
    print("edicion S4.3:", {k: v for k, v in d["b18_edit"].items() if k != "sentence"})
    print("pdf:", {k: (v["ok"], v["removed_keys"], v["pdfinfo_date_lines"]) for k, v in pdfs.items()})
    print("MANIFEST:", d["manifest_regenerated"], "| aciertos:", sc["non_hash_hits"], "| compilacion:", comp)
    return 0


if __name__ == "__main__":
    sys.exit(main())
