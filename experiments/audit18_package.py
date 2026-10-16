"""
Auditoria A18 - B18.3-B18.5, paquete (enmienda 8, lecturas E8.3-E8.5).

Como audit17_package (E7.5), sobre paper_latex_v18b.zip: arma el paquete, limpia las fechas de la figura del cuerpo (las del
suplemento ya vienen limpias de supplementary/, E8.3), verifica todos los PDF con pdfinfo y en bytes, compila el cuerpo y el
suplemento juntos, repite la busqueda de identificadores (patrones de B15.5, nombres de archivo, metadatos de PDF y fechas) y
genera submission_v18b.zip en el directorio temporal de la sesion (A18_PKG_DIR), sin commitearlo.
Salida: experiments/results/submission_v18b_audit18.json.
"""
import os
import re
import shutil
import sys
import tempfile
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit18_common as C                                         # noqa: E402
import audit17_package as P17                                      # noqa: E402

OUT = os.path.join(C.RESULTS, "submission_v18b_audit18.json")
SUPP = os.path.join(C.REPO, "supplementary")
PKG_ZIP_NAME = "submission_v18b.zip"
TOP = "submission_v18b"


def main():
    st = C.git("status", "--porcelain", "--", "supplementary")
    tmp = tempfile.mkdtemp(prefix="a18_pkg_")
    pkg = os.path.join(tmp, TOP)
    os.makedirs(pkg)
    with zipfile.ZipFile(C.ZIP_V18B) as z:
        mem = P17.members(z)
        files = {k: z.read(v).decode("utf-8", errors="replace") for k, v in mem.items() if k.endswith(".tex")}
        texs, tabs, figs = P17.included(files)
        fig_files = {k for f in figs for k in mem if k.startswith("figures/")
                     and os.path.splitext(os.path.basename(k))[0] == os.path.splitext(os.path.basename(f))[0]}
        take = sorted(set(texs) | set(tabs) | fig_files | {k for k in P17.KEEP if k in mem})
        for k in take:
            p = os.path.join(pkg, k)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "wb") as fh:
                fh.write(z.read(mem[k]))
        excluded = sorted(k for k in mem if k not in take)
    shutil.copytree(SUPP, os.path.join(pkg, "supplementary"))
    body_pdf = {k: C.strip_pdf_dates(os.path.join(pkg, k)) for k in sorted(fig_files) if k.lower().endswith(".pdf")}
    allf = [os.path.join(dp, f) for dp, _, fs in os.walk(pkg) for f in fs]
    pdf_check = {os.path.relpath(p, pkg).replace("\\", "/"): C.check_pdf_dates(p) for p in allf if p.lower().endswith(".pdf")}
    artifacts = [os.path.relpath(p, pkg).replace("\\", "/") for p in allf if p.endswith(P17.ARTIFACTS) and not p.lower().endswith(".pdf")]
    work = os.path.join(tmp, "work")
    shutil.copytree(pkg, work)
    for _ in range(2):
        P17.run([P17.PDFLATEX, "-interaction=nonstopmode", "main.tex"], work)
    main_stats = P17.log_stats(os.path.join(work, "main.log"))
    bibw = os.path.join(tmp, "bibcheck")
    shutil.copytree(pkg, bibw)
    P17.run([P17.PDFLATEX, "-interaction=nonstopmode", "main.tex"], bibw)
    shutil.move(os.path.join(bibw, "main.bbl"), os.path.join(bibw, "main_given.bbl"))
    P17.run([P17.BIBTEX, "main"], bibw)
    norm = lambda s: re.sub(r"\s+", " ", s).strip()                   # noqa: E731
    bbl_same = norm(open(os.path.join(bibw, "main.bbl"), encoding="utf-8", errors="replace").read()) == \
        norm(open(os.path.join(bibw, "main_given.bbl"), encoding="utf-8", errors="replace").read())
    sw = os.path.join(work, "supplementary")
    for exe in (P17.PDFLATEX, P17.BIBTEX, P17.PDFLATEX, P17.PDFLATEX):
        P17.run([exe, "-interaction=nonstopmode", "supplement.tex"] if exe == P17.PDFLATEX else [exe, "supplement"], sw)
    supp_stats = P17.log_stats(os.path.join(sw, "supplement.log"))
    text_hits, pdf_meta = {}, {}
    for p in allf:
        r = os.path.relpath(p, pkg).replace("\\", "/")
        if p.lower().endswith(".pdf"):
            md = P17.AN.pdf_meta(p)
            pdf_meta[r] = md
            h = P17.AN.scan_text(p, " | ".join("%s=%s" % kv for kv in md.items()))
            if h:
                text_hits["pdfmeta:" + r] = h
        elif p.lower().endswith(P17.TEXT_SCAN):
            h = P17.AN.scan_text(p, open(p, encoding="utf-8", errors="replace").read())
            if h:
                text_hits[r] = h
        hn = P17.AN.scan_text(p, r)
        if hn:
            text_hits["filename:" + r] = hn
    author = {f: {c: x for c, x in h.items() if c in P17.AUTHOR_CATS} for f, h in text_hits.items()}
    author = {f: h for f, h in author.items() if h}
    other = {f: {c: x for c, x in h.items() if c not in P17.AUTHOR_CATS} for f, h in text_hits.items()}
    other = {f: h for f, h in other.items() if h}
    manifest = open(os.path.join(pkg, "supplementary", "MANIFEST.sha256"), encoding="utf-8").read().strip().splitlines()
    manifest_ok = all(C.sha256_file(os.path.join(pkg, "supplementary", l.split("  ", 1)[1])) == l.split("  ", 1)[0] for l in manifest)
    zdir = os.environ.get("A18_PKG_DIR") or tmp
    os.makedirs(zdir, exist_ok=True)
    zpath = os.path.join(zdir, PKG_ZIP_NAME)
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(allf):
            zf.write(p, TOP + "/" + os.path.relpath(p, pkg).replace("\\", "/"))
    listing = [{"path": os.path.relpath(p, pkg).replace("\\", "/"), "bytes": os.path.getsize(p), "sha256": C.sha256_file(p)} for p in sorted(allf)]
    pdf_ok = all(not v["raw_has_date_key"] and not v["raw_has_date_value"] and not v["pdfinfo_date_lines"] for v in pdf_check.values())
    out = {"provenance": C.provenance(__file__), "reading": "enmienda 8, lecturas E8.3-E8.5",
           "inputs": {"v18b_zip_sha256": C.sha256_file(C.ZIP_V18B), "supplementary_git_status": st.splitlines(),
                      "supplementary_commit": C.git("log", "-1", "--format=%H", "--", "supplementary")},
           "included_tex": sorted(texs), "included_tables": sorted(tabs), "included_figures": sorted(fig_files), "excluded_from_zip": excluded,
           "compilation_artifacts_in_package": artifacts, "body_pdf_date_strip": body_pdf, "pdf_date_check": pdf_check,
           "supplement_manifest": {"entries": len(manifest), "all_match": manifest_ok},
           "compile": {"v18b": main_stats, "v18b_bbl_matches_bibtex": bbl_same, "supplement": supp_stats},
           "anonymity": {"author_identifying_hits": author, "other_hits": other, "pdf_metadata": pdf_meta},
           "files": listing, "n_files": len(listing), "zip": {"name": PKG_ZIP_NAME, "bytes": os.path.getsize(zpath), "sha256": C.sha256_file(zpath)},
           "gates": {"v18b_clean": main_stats["errors"] == 0 and main_stats["undefined_references"] == 0 and main_stats["undefined_citations"] == 0,
                     "supplement_clean": supp_stats["errors"] == 0 and supp_stats["undefined_references"] == 0 and supp_stats["undefined_citations"] == 0,
                     "no_artifacts": not artifacts, "no_author_hits": not author, "no_pdf_dates": pdf_ok,
                     "body_pdf_content_preserved": all(v["content_streams_equal"] and v["raster_equal"] for v in body_pdf.values()),
                     "manifest_ok": manifest_ok, "supplementary_committed": not st.strip()}}
    C.write_result(OUT, out, __file__)
    shutil.rmtree(tmp, ignore_errors=True)
    print("v18b:", main_stats, "| bbl:", bbl_same, "| suplemento:", supp_stats)
    print("pdf:", {k: (not v["raw_has_date_key"], v["pdfinfo_date_lines"]) for k, v in pdf_check.items()})
    print("zip:", zpath, out["zip"]["bytes"], out["zip"]["sha256"], "| puertas:", out["gates"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
