"""
Auditoria A19 - punto 3 (protocol_audit19.md, L3) y nota de S4.3 (L2.2): ediciones de forma del suplemento.

Parte de supplementary/supplement.tex tal como lo dejo A18 (Paso 0: sha256 de E0). Cada edicion es una sustitucion con un ancla
que debe aparecer exactamente una vez; todas quedan registradas. No se vuelve a correr la cadena A16-A18.
  L3.g  control de remisiones: etiquetas del cuerpo del v25 (compilacion temporal) frente a body_labels de A18 (v18b);
  L3.a  leyendas de las tablas sin negritas (verificado en la fuente y en el PDF compilado);
  L3.b  definicion de RM en la nota de cada tabla con columna RM;
  L3.c  parrafo de invariancia en su propia subseccion;
  L3.d  oracion SB/SWB al final de la subseccion de quiebres de varianza;
  L3.e  oracion de S7;
  L2.2  oracion de la nota de tab:awb (de awb_rule_audit19.json);
  L3.f  compilacion antes y despues (paginas, errores, referencias);
  L3.h  MANIFEST.sha256 del suplemento y busqueda de identificadores.
Con --out <dir> trabaja sobre una copia en <dir> (prueba). Salida: experiments/results/supplement_v25_audit19.json
(o supplement_v25_trial_audit19.json).
"""
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

import audit19_common as C                                         # noqa: E402
import audit16_supplement as S16                                   # noqa: E402
import audit15_supplement as A15S                                  # noqa: E402

OUT = os.path.join(C.RESULTS, "supplement_v25_audit19.json")
OUT_TRIAL = os.path.join(C.RESULTS, "supplement_v25_trial_audit19.json")
SUPP_SHA256_A18 = "0b6e45cd754df554b5c0f258dc556dde0d9da2dcfc6be15a8e5c38ee808b3b91"
BOLD_PHRASE = " Bold entries follow the rule stated in its note."
NO_BOLD = ("tab:size02", "tab:localpower02", "tab:dgp102", "tab:ctpower02", "tab:dgp202", "tab:dgp502", "tab:fp02")
WITH_BOLD = ("tab:calib02", "tab:dgp302", "tab:misspec02", "tab:awb02")
RM_DEF = r"RM: the centred rolling-means statistic with $\theta = 0.1$."
INVAR_START = "The invariance of Proposition~2 of the main text was checked numerically"
INVAR_TITLE = r"\subsection*{A numerical check of invariance}"
SIEVE_TITLE = r"\subsection*{The sieve bootstraps}"
SB_SWB = ("The sieve bootstrap (SB) and the sieve wild bootstrap (SWB) calibrations of MZ$_t$-GLS were not evaluated under "
          "variance breaks.")
HEAVY_TITLE = r"\subsection*{Heavy tails and conditional heteroskedasticity}"
S7_OLD = r"The slope of 1/3 follows from the Andrews rule once $\hat a$ settles; it says nothing about the stochastic part."
S7_NEW = (r"Appendix A.5 of the main text proves $(B+1)\hat\sigma^2 \to_p 2\gamma(0)$; the slope of 1/3 is that of the Andrews "
          r"bandwidth.")
THETA_P = (r"\\Theta_p", r"Theta_p", r"n\^\{-1/3\}", r"stochastic part")
AWB_ANCHOR = r"not the $(1 + \#)/(R + 1)$ of Section~3.5 of the main text."
NUM = re.compile(r"^\(?[-\u2212]?\d*\.\d+\)?$|^\(?[-\u2212]?\d+\)?$")


class Edits:
    def __init__(self, tex):
        self.tex, self.log = tex, []

    def sub(self, tag, old, new, where=None):
        """Sustituye old por new; old debe aparecer exactamente una vez (en el fragmento where, si se da)."""
        scope = where if where is not None else self.tex
        n = scope.count(old)
        if n != 1:
            raise SystemExit("ancla de %s: %d apariciones (se exige 1): %r" % (tag, n, old[:120]))
        if where is not None:
            if self.tex.count(where) != 1:
                raise SystemExit("fragmento de %s no unico" % tag)
            self.tex = self.tex.replace(where, where.replace(old, new))
        else:
            self.tex = self.tex.replace(old, new)
        self.log.append({"edit": tag, "old": old, "new": new, "count": n})


def floats(tex, env="table"):
    """{etiqueta: texto del entorno} de cada \\begin{table}...\\end{table}."""
    out = {}
    for m in re.finditer(r"\\begin\{%s\}.*?\\end\{%s\}" % (env, env), tex, flags=re.S):
        lab = re.search(r"\\label\{([^}]*)\}", m.group(0))
        if lab:
            out[lab.group(1)] = m.group(0)
    return out


def inputs_of(block):
    return re.findall(r"\\input\{tables/([^}]*)\}", block)


def has_rm_column(supp, block):
    return any(re.search(r"& RM &", open(os.path.join(supp, "tables", f + ".tex"), encoding="utf-8").read())
               for f in inputs_of(block))


def body_labels_v25(tmp):
    """Compila el v25 (pdflatex x2) en tmp y devuelve {etiqueta: [tipo, numero]}, el .aux y el resumen."""
    d = os.path.join(tmp, "v25")
    with zipfile.ZipFile(C.ZIP_V25) as z:
        for n in z.namelist():
            if n.endswith("/"):
                continue
            rel = n.split("/", 1)[1] if "/" in n else n
            p = os.path.join(d, rel)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "wb") as fh:
                fh.write(z.read(n))
    for _ in range(2):
        subprocess.run([S16.PDFLATEX, "-interaction=nonstopmode", "main.tex"], cwd=d, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    aux = open(os.path.join(d, "main.aux"), encoding="utf-8", errors="replace").read()
    out = {}
    for m in re.finditer(r"\\newlabel\{([^}@]+)\}\{\{([^}]*)\}\{[^}]*\}\{(?:[^{}]|\{[^{}]*\})*\}\{([a-z]+)\.", aux):
        out[m.group(1)] = [m.group(3), m.group(2)]
    log = open(os.path.join(d, "main.log"), encoding="utf-8", errors="replace").read()
    pages = re.search(r"Output written on .*?\((\d+) pages?", log)
    return out, aux, {"compiled": pages is not None, "pages": int(pages.group(1)) if pages else None,
                      "errors": len(re.findall(r"^! ", log, flags=re.M)),
                      "undefined_references": len(re.findall(r"Reference `[^']*' on page \d+ undefined", log))}


def compile_supp(supp, tmp, tag):
    """S16.compile_check, pero conserva el PDF en tmp para la verificacion de negritas."""
    dst = os.path.join(tmp, tag)
    shutil.copytree(supp, dst)
    runs = []
    for exe in (S16.PDFLATEX, S16.BIBTEX, S16.PDFLATEX, S16.PDFLATEX):
        args = [exe, "-interaction=nonstopmode", "supplement.tex"] if exe == S16.PDFLATEX else [exe, "supplement"]
        runs.append(subprocess.run(args, cwd=dst, capture_output=True, text=True, encoding="utf-8", errors="replace").returncode)
    log = open(os.path.join(dst, "supplement.log"), encoding="utf-8", errors="replace").read()
    aux = open(os.path.join(dst, "supplement.aux"), encoding="utf-8", errors="replace").read()
    pages = re.search(r"Output written on .*?\((\d+) pages?", log)
    res = {"compiled": os.path.exists(os.path.join(dst, "supplement.pdf")), "errors": len(re.findall(r"^! ", log, flags=re.M)),
           "first_errors": re.findall(r"^! .*$", log, flags=re.M)[:5],
           "undefined_references": len(re.findall(r"Reference `[^']*' on page \d+ undefined", log)),
           "undefined_citations": len(re.findall(r"Citation `[^']*' on page \d+ undefined", log)),
           "rerun_warnings": len(re.findall(r"Rerun to get", log)),
           "overfull": len(re.findall(r"Overfull \\hbox", log)), "pages": int(pages.group(1)) if pages else None,
           "returncodes": runs}
    labels = {m.group(1): m.group(2) for m in re.finditer(r"\\newlabel\{([^}@]+)\}\{\{([^}]*)\}", aux)}
    return res, labels, os.path.join(dst, "supplement.pdf")


def bold_in_pdf(pdf, labels, targets):
    """Spans numericos en negrita en la franja de cada tabla: de su leyenda a la siguiente leyenda o al pie de la pagina."""
    import fitz
    doc = fitz.open(pdf)
    caps = []
    for pno, page in enumerate(doc):
        for b in page.get_text("dict")["blocks"]:
            txt = "".join(s["text"] for l in b.get("lines", []) for s in l["spans"]).strip()
            m = re.match(r"^(Table|Figure) (S\d+\.\d+)[.:]", txt)
            if m:
                caps.append((pno, b["bbox"][1], m.group(1), m.group(2)))
    out = {}
    for lab in targets:
        num = labels[lab]
        hit = [c for c in caps if c[2] == "Table" and c[3] == num]
        if len(hit) != 1:
            out[lab] = {"number": num, "found_caption": len(hit), "bold_numeric_spans": None}
            continue
        pno, y0 = hit[0][0], hit[0][1]
        nxt = [c[1] for c in caps if c[0] == pno and c[1] > y0]
        y1 = min(nxt) if nxt else doc[pno].rect.y1
        bold = []
        for b in doc[pno].get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                for s in l["spans"]:
                    if y0 <= s["bbox"][1] < y1 and (s["flags"] & 16 or "bold" in s["font"].lower()) and NUM.match(s["text"].strip()):
                        bold.append(s["text"].strip())
        out[lab] = {"number": num, "found_caption": 1, "page": pno + 1, "bold_numeric_spans": len(bold), "examples": bold[:5]}
    return out


def main():
    args = sys.argv[1:]
    trial = "--out" in args
    real = S16.SUPP_REAL
    if trial:
        supp = os.path.abspath(args[args.index("--out") + 1])
        if os.path.exists(supp):
            shutil.rmtree(supp)
        shutil.copytree(real, supp)
    else:
        supp = real
    path = os.path.join(supp, "supplement.tex")
    sha_in = C.sha256_file(path)
    if sha_in != SUPP_SHA256_A18:
        raise SystemExit("Paso 0: supplement.tex no es el de A18 (E0): %s" % sha_in)
    tex0 = open(path, encoding="utf-8").read()
    tmp = tempfile.mkdtemp(prefix="a19_supp_")
    try:
        # L3.g: remisiones al cuerpo
        a18 = C.read_json("supplement_v18b_audit18.json")
        body18 = a18["body_labels"]
        body25, aux25, v25_comp = body_labels_v25(tmp)
        changed = {k: {"v18b": v, "v25": body25.get(k)} for k, v in body18.items() if body25.get(k) != v}
        refs = [r for r in a18["references"] if r["how"].startswith("cuerpo")]
        ref_changed = sorted({r["label"] for r in refs if r["label"] in changed})
        rendered = [{"label": r["label"], "v18b": r["resolved_as"],
                     "v25": S16.render_body(r["label"], {k: tuple(v) for k, v in body25.items()}, r["resolved_as"][0].isupper())
                     if r["label"] in body25 else None} for r in refs]
        a5 = re.findall(r"\\numberline \{A\.5\}([^\n]*)", aux25)
        appendix_a5 = {"toc_entries": a5, "is_proof_of_theorem_2": any("thm:consistency" in e or "Theorem 2" in e for e in a5),
                       "thm_consistency": body25.get("thm:consistency"), "bootdef": body25.get("sec:bootdef")}
        if ref_changed or not appendix_a5["is_proof_of_theorem_2"] or body25.get("sec:bootdef") != ["subsection", "3.5"]:
            raise SystemExit("L3.g: cambia una remision al cuerpo en el v25: %s | A.5: %s | sec:bootdef: %s"
                             % (ref_changed, a5, body25.get("sec:bootdef")))
        # L3.f (antes) y L3.a (verificacion de negritas)
        before, labels0, pdf0 = compile_supp(supp, tmp, "before")
        bold0 = bold_in_pdf(pdf0, labels0, NO_BOLD + WITH_BOLD)
        fl0 = floats(tex0)
        src_bold = {lab: sum(open(os.path.join(supp, "tables", f + ".tex"), encoding="utf-8").read().count("\\textbf")
                             for f in inputs_of(fl0[lab])) for lab in NO_BOLD + WITH_BOLD}
        detector_ok = all(bold0[l]["bold_numeric_spans"] for l in WITH_BOLD if src_bold[l])
        E = Edits(tex0)
        kept, removed = [], []
        for lab in NO_BOLD:
            block = floats(E.tex)[lab]
            if src_bold[lab] == 0 and bold0[lab]["bold_numeric_spans"] == 0 and detector_ok:
                E.sub("L3.a " + lab, BOLD_PHRASE + "}", "}", where=block)
                removed.append(lab)
            else:
                kept.append(lab)
        # L3.b: definicion de RM
        E.sub("L3.b quitar (S1)", "\\label{supp:s1}\n\n" + RM_DEF + "\n\n", "\\label{supp:s1}\n\n")
        E.sub("L3.b quitar (S5)", "\\subsection*{Tables with $\\theta = 0.02$}\n\n" + RM_DEF + "\n\n",
              "\\subsection*{Tables with $\\theta = 0.02$}\n\n")
        rm_tables = []
        for lab, block in floats(E.tex).items():
            if not has_rm_column(supp, block):
                continue
            if "\\end{tablenotes}" in block:
                kind, old = "tablenotes", "\n\\end{tablenotes}"
                new = " " + RM_DEF + old
                i = block.rindex(old)
                nb = block[:i] + new + block[i + len(old):]
            elif "\\end{minipage}" in block:
                kind, old = "minipage", "\n\\end{minipage}"
                i = block.rindex(old)
                nb = block[:i] + " " + RM_DEF + old + block[i + len(old):]
            else:
                kind, old = "nota nueva", "\\end{adjustbox}\n"
                if block.count(old) != 1:
                    raise SystemExit("L3.b: %s sin nota ni adjustbox unico" % lab)
                nb = block.replace(old, old + "\\par\\medskip\\begin{minipage}{\\textwidth}\\footnotesize\n" + RM_DEF + "\n\\end{minipage}\n")
            E.sub("L3.b nota " + lab, block, nb)
            rm_tables.append({"label": lab, "number": labels0.get(lab), "inputs": inputs_of(block), "note": kind})
        # L3.c: invariancia
        m = re.search(re.escape(INVAR_START) + r"[^\n]*\n\n", E.tex)
        if not m or E.tex.count(INVAR_START) != 1:
            raise SystemExit("L3.c: parrafo de invariancia no unico")
        para = m.group(0)
        sieve = E.tex.index(SIEVE_TITLE)
        if not (sieve < m.start() < E.tex.index("\\subsection*{Scale diagnostics}")):
            raise SystemExit("L3.c: el parrafo no esta en «The sieve bootstraps»")
        E.sub("L3.c quitar", para, "")
        E.sub("L3.c subseccion", SIEVE_TITLE + "\n", INVAR_TITLE + "\n\n" + para + SIEVE_TITLE + "\n")
        # L3.d: SB/SWB
        E.sub("L3.d quitar", "\n\n" + SB_SWB + "\n", "\n")
        E.sub("L3.d insertar", HEAVY_TITLE + "\n", SB_SWB + "\n\n" + HEAVY_TITLE + "\n")
        # L3.e: S7
        E.sub("L3.e", S7_OLD, S7_NEW)
        theta_p_left = {p: len(re.findall(p, E.tex)) for p in THETA_P}
        # L2.2: oracion de la nota de tab:awb
        awb = C.read_json("awb_rule_audit19.json")
        if not awb["p2_holds"]:
            raise SystemExit("L2.2: P2 no se cumple; no se edita la nota")
        E.sub("L2.2 tab:awb", AWB_ANCHOR, AWB_ANCHOR + " " + awb["s43_sentence"], where=floats(E.tex)["tab:awb"])
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(E.tex)
        # L3.f (despues) y negritas otra vez
        after, labels1, pdf1 = compile_supp(supp, tmp, "after")
        bold1 = bold_in_pdf(pdf1, labels1, NO_BOLD + WITH_BOLD)
        fl1 = floats(E.tex)
        captions_left = {lab: (BOLD_PHRASE in fl1[lab]) for lab in NO_BOLD + WITH_BOLD}
        # L3.h: MANIFEST y busqueda de identificadores
        man = []
        for dp, _, fs in os.walk(supp):
            for fn in sorted(fs):
                p = os.path.join(dp, fn)
                r = os.path.relpath(p, supp).replace("\\", "/")
                if r != "MANIFEST.sha256":
                    man.append("%s  %s" % (C.sha256_file(p), r))
        mtxt = "\n".join(sorted(man, key=lambda s: s.split("  ", 1)[1])) + "\n"
        with open(os.path.join(supp, "MANIFEST.sha256"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(mtxt)
        manifest_ok = all(C.sha256_file(os.path.join(supp, l.split("  ", 1)[1])) == l.split("  ", 1)[0] for l in mtxt.strip().splitlines())
        A15S.SUPP = supp
        sc = A15S.scan()
        numbers_before = sorted(re.findall(r"(?<![\w.])\d+\.\d+(?![\w.])", tex0))
        numbers_after = sorted(re.findall(r"(?<![\w.])\d+\.\d+(?![\w.])", E.tex))
        ok = (after["errors"] == 0 and after["undefined_references"] == 0 and after["undefined_citations"] == 0 and manifest_ok
              and not kept and len(rm_tables) >= 6 and all(v == 0 for k, v in theta_p_left.items() if k != r"n\^\{-1/3\}"))
        out = {"provenance": C.provenance(__file__), "reading": "protocol_audit19.md, L2.2 y L3", "trial": trial,
               "inputs": {"supplement_tex_sha256_a18": sha_in, "v25_zip_sha256": C.sha256_file(C.ZIP_V25)},
               "main_text_refs": {"v25_compile": v25_comp, "labels_changed_v18b_to_v25": changed, "referenced_changed": ref_changed,
                                  "references": rendered, "appendix_a5": appendix_a5,
                                  "all_rendered_equal": all(r["v18b"] == r["v25"] for r in rendered)},
               "bold_check": {"source_textbf": src_bold, "pdf_before": bold0, "pdf_after": bold1, "detector_validated": detector_ok,
                              "captions_removed": removed, "captions_kept": kept, "phrase_left": captions_left},
               "rm_tables": rm_tables, "rm_assignment_list": ["tab:dgp1", "tab:ctpower", "tab:dgp102", "tab:ctpower02", "tab:dgp202",
                                                              "tab:dgp302"],
               "rm_definitions_left_outside_notes": E.tex.count("\n" + RM_DEF + "\n\n"),
               "s7": {"old": S7_OLD, "new": S7_NEW, "theta_p_patterns_left": theta_p_left},
               "edits": E.log, "n_edits": len(E.log),
               "numbers_unchanged": {"before": len(numbers_before), "after": len(numbers_after),
                                     "added": sorted(set(numbers_after) - set(numbers_before)),
                                     "removed": sorted(set(numbers_before) - set(numbers_after))},
               "compile_before": before, "compile_after": after,
               "pages": {"before": before["pages"], "after": after["pages"]},
               "supplement_tex_sha256_after": C.sha256_file(path),
               "manifest_regenerated": {"entries": len(man), "all_match": manifest_ok}, "anonymization_scan": sc, "ok": bool(ok)}
        C.write_result(OUT_TRIAL if trial else OUT, out, __file__)
        if not trial:
            C.register_outputs(__file__, [path, os.path.join(supp, "MANIFEST.sha256")], out["provenance"])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("remisiones: cambiadas", ref_changed, "| todas iguales:", out["main_text_refs"]["all_rendered_equal"], "| A.5:", a5)
    print("negritas: quitadas", removed, "| conservadas", kept, "| detector", detector_ok)
    print("RM en", [r["label"] for r in rm_tables])
    print("paginas", out["pages"], "| despues:", {k: after[k] for k in ("errors", "undefined_references", "undefined_citations")})
    print("numeros añadidos", out["numbers_unchanged"]["added"], "quitados", out["numbers_unchanged"]["removed"])
    print("MANIFEST", out["manifest_regenerated"], "| identificadores", sc["non_hash_hits"], "| ok", ok)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
