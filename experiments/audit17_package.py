"""
Auditoria A17 - B17.5 (enmienda 7, lectura E7.5): compilacion de control del v18 y del suplemento juntos, y paquete de envio.

Paquete (directorio temporal): main.tex, las secciones que main.tex incluye, tables/ (solo archivos alcanzados por
\\input), figures/ (solo los usados por \\includegraphics), interact.cls, tfnlm.bst, references.bib, main.bbl y
supplementary/ tal como esta commiteado. Fuera: main.pdf, CHANGELOG*, SUPPLEMENT_MAP*, cover_letter.md y artefactos.
Compilacion: v18 con pdflatex x2 y el .bbl entregado (y bibtex en una copia para comparar el .bbl); suplemento con pdflatex,
bibtex y pdflatex x2. Anonimato: patrones de B15.5 sobre todos los archivos de texto (incluidos .cls, .bst, .bbl), nombres
de archivo y metadatos de los PDF. Zip del paquete al directorio temporal de la sesion (no se commitea).
Salida: experiments/results/submission_v18_audit17.json.
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

import audit17_common as C                                         # noqa: E402
import audit15_b5_anon as AN                                       # noqa: E402
import audit16_supplement as S16                                   # noqa: E402

OUT = os.path.join(C.RESULTS, "submission_v18_audit17.json")
SUPP = os.path.join(C.REPO, "supplementary")
PDFLATEX, BIBTEX = S16.PDFLATEX, S16.BIBTEX
KEEP = ("interact.cls", "tfnlm.bst", "references.bib", "main.bbl", "main.tex")
EXCLUDED_KNOWN = ("main.pdf", "cover_letter.md")
ARTIFACTS = (".aux", ".log", ".out", ".blg", ".synctex.gz", ".toc", ".fls", ".fdb_latexmk", ".pdf")
TEXT_SCAN = (".tex", ".bib", ".bbl", ".bst", ".cls", ".md", ".json", ".csv", ".txt", ".sha256")
AUTHOR_CATS = ("ruta_de_usuario", "usuario_git", "usuario_local", "apellido", "url_repositorio")
PKG_ZIP_NAME = "submission_v18.zip"


def members(z):
    return {(n.split("/", 1)[1] if "/" in n else n): n for n in z.namelist() if not n.endswith("/")}


def included(files, start="main.tex"):
    """Archivos .tex alcanzados por \\input/\\include desde main.tex, tabulares \\input y figuras \\includegraphics."""
    seen, tabs, figs, order = set(), set(), set(), [start]
    while order:
        f = order.pop(0)
        if f in seen or f not in files:
            continue
        seen.add(f)
        t = re.sub(r"(?<!\\)%.*", "", files[f])
        for m in re.finditer(r"\\(?:input|include)\{([^}]+)\}", t):
            name = m.group(1) if m.group(1).endswith(".tex") else m.group(1) + ".tex"
            if name.startswith("tables/"):
                tabs.add(name)
            order.append(name)
        for m in re.finditer(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", t):
            figs.add(m.group(1))
    return seen, tabs, figs


def run(cmd, cwd):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode


def log_stats(path):
    log = open(path, encoding="utf-8", errors="replace").read()
    pages = re.search(r"Output written on .*?\((\d+) pages?", log)
    return {"errors": len(re.findall(r"^! ", log, flags=re.M)), "first_errors": re.findall(r"^! .*$", log, flags=re.M)[:3],
            "undefined_references": len(re.findall(r"Reference `[^']*' on page \d+ undefined", log)),
            "undefined_citations": len(re.findall(r"Citation `[^']*' on page \d+ undefined", log)),
            "overfull": len(re.findall(r"Overfull \\hbox", log)), "pages": int(pages.group(1)) if pages else None}


def main():
    v18 = C.v18()
    st = C.git("status", "--porcelain", "--", "supplementary")
    tmp = tempfile.mkdtemp(prefix="a17_pkg_")
    pkg = os.path.join(tmp, "submission_v18")
    os.makedirs(pkg)
    with zipfile.ZipFile(C.ZIP_V18) as z:
        mem = members(z)
        files = {k: z.read(v).decode("utf-8", errors="replace") for k, v in mem.items() if k.endswith(".tex")}
        texs, tabs, figs = included(files)
        fig_files = set()
        for f in figs:
            cands = [k for k in mem if k.startswith("figures/") and os.path.splitext(os.path.basename(k))[0] == os.path.splitext(os.path.basename(f))[0]]
            fig_files.update(cands)
        take = sorted(set(texs) | set(tabs) | fig_files | {k for k in KEEP if k in mem})
        for k in take:
            p = os.path.join(pkg, k)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "wb") as fh:
                fh.write(z.read(mem[k]))
        excluded = sorted(k for k in mem if k not in take)
    unused_tables = sorted(k for k in excluded if k.startswith("tables/"))
    shutil.copytree(SUPP, os.path.join(pkg, "supplementary"))
    artifacts = [os.path.relpath(os.path.join(dp, f), pkg).replace("\\", "/") for dp, _, fs in os.walk(pkg) for f in fs
                 if f.endswith(ARTIFACTS) and not os.path.relpath(os.path.join(dp, f), pkg).replace("\\", "/").startswith(("figures/", "supplementary/figures/"))]
    # compilacion de control, en copias
    work = os.path.join(tmp, "work")
    shutil.copytree(pkg, work)
    for _ in range(2):
        run([PDFLATEX, "-interaction=nonstopmode", "main.tex"], work)
    main_stats = log_stats(os.path.join(work, "main.log"))
    bibw = os.path.join(tmp, "bibcheck")
    shutil.copytree(pkg, bibw)
    run([PDFLATEX, "-interaction=nonstopmode", "main.tex"], bibw)
    shutil.move(os.path.join(bibw, "main.bbl"), os.path.join(bibw, "main_given.bbl"))
    run([BIBTEX, "main"], bibw)
    norm = lambda s: re.sub(r"\s+", " ", s).strip()                   # noqa: E731
    bbl_same = norm(open(os.path.join(bibw, "main.bbl"), encoding="utf-8", errors="replace").read()) == \
        norm(open(os.path.join(bibw, "main_given.bbl"), encoding="utf-8", errors="replace").read())
    sw = os.path.join(work, "supplementary")
    for exe in (PDFLATEX, BIBTEX, PDFLATEX, PDFLATEX):
        run([exe, "-interaction=nonstopmode", "supplement.tex"] if exe == PDFLATEX else [exe, "supplement"], sw)
    supp_stats = log_stats(os.path.join(sw, "supplement.log"))
    # anonimato
    allf = [os.path.join(dp, f) for dp, _, fs in os.walk(pkg) for f in fs]
    text_hits, pdf_meta = {}, {}
    for p in allf:
        r = os.path.relpath(p, pkg).replace("\\", "/")
        if p.lower().endswith(".pdf"):
            md = AN.pdf_meta(p)
            pdf_meta[r] = md
            h = AN.scan_text(p, " | ".join("%s=%s" % kv for kv in md.items()))
            if h:
                text_hits["pdfmeta:" + r] = h
        elif p.lower().endswith(TEXT_SCAN):
            h = AN.scan_text(p, open(p, encoding="utf-8", errors="replace").read())
            if h:
                text_hits[r] = h
        hn = AN.scan_text(p, r)
        if hn:
            text_hits["filename:" + r] = hn
    author_hits = {f: {c: x for c, x in h.items() if c in AUTHOR_CATS} for f, h in text_hits.items()}
    author_hits = {f: h for f, h in author_hits.items() if h}
    other_hits = {f: {c: x for c, x in h.items() if c not in AUTHOR_CATS} for f, h in text_hits.items()}
    other_hits = {f: h for f, h in other_hits.items() if h}
    # zip del paquete
    zdir = os.path.join(os.environ.get("A17_PKG_DIR") or tmp)
    os.makedirs(zdir, exist_ok=True)
    zpath = os.path.join(zdir, PKG_ZIP_NAME)
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(allf):
            zf.write(p, "submission_v18/" + os.path.relpath(p, pkg).replace("\\", "/"))
    listing = [{"path": os.path.relpath(p, pkg).replace("\\", "/"), "bytes": os.path.getsize(p), "sha256": C.sha256_file(p)} for p in sorted(allf)]
    out = {"provenance": C.provenance(__file__), "reading": "enmienda 7, lectura E7.5",
           "inputs": {"v18_zip_sha256": v18.sha256, "supplementary_git_status": st.splitlines(),
                      "supplementary_commit": C.git("log", "-1", "--format=%H", "--", "supplementary")},
           "included_tex": sorted(texs), "included_tables": sorted(tabs), "included_figures": sorted(fig_files),
           "excluded_from_zip": excluded, "unused_tables_excluded": unused_tables, "compilation_artifacts_in_package": artifacts,
           "compile": {"v18": main_stats, "v18_bbl_matches_bibtex": bbl_same, "supplement": supp_stats},
           "anonymity": {"author_identifying_hits": author_hits, "other_hits": other_hits, "pdf_metadata": pdf_meta},
           "files": listing, "n_files": len(listing), "zip": {"name": PKG_ZIP_NAME, "bytes": os.path.getsize(zpath), "sha256": C.sha256_file(zpath)},
           "gates": {"v18_clean": main_stats["errors"] == 0 and main_stats["undefined_references"] == 0 and main_stats["undefined_citations"] == 0,
                     "supplement_clean": supp_stats["errors"] == 0 and supp_stats["undefined_references"] == 0 and supp_stats["undefined_citations"] == 0,
                     "no_artifacts": not artifacts, "no_author_hits": not author_hits, "supplementary_committed": not st.strip()}}
    C.write_result(OUT, out, __file__)
    print("v18:", main_stats, "| bbl = bibtex:", bbl_same)
    print("suplemento:", supp_stats)
    print("incluidos:", len(texs), "tex,", len(tabs), "tablas,", len(fig_files), "figuras | excluidos:", excluded)
    print("artefactos:", artifacts, "| aciertos de autor:", author_hits)
    print("otros aciertos:", {f: list(h) for f, h in other_hits.items()})
    print("pdf meta:", {k: v for k, v in list(pdf_meta.items())[:3]})
    print("zip:", zpath, out["zip"]["bytes"], out["zip"]["sha256"], "| puertas:", out["gates"])
    shutil.rmtree(tmp, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
