"""
Auditoria A15 - B15.5: inventario de lo que identifica al autor y propuesta anonimizada
(protocol_audit15.md, lecturas 5.1 y 5.2). No modifica el repositorio.

Alcance: (A) supplementary/**; (B) lo que ejecuta supplementary/reproduce.ps1 y los metadatos del
paquete (pyproject.toml, CITATION.cff, requirements.txt); (C) el suplemento de SUPPLEMENT_PLAN
(JSON de resultados de primer nivel, protocolos, predicciones, manifiestos, tabulares exportados,
figuras del manuscrito) y el codigo de experiments/ que los produce. Categorias: rutas de
usuario, nombres de usuario y del autor, correos, URL de repositorio, hashes de commit y
metadatos de PDF; ademas, autores de la historia de git.

Propuesta: mapa de reemplazos y construccion de una copia anonimizada en un directorio temporal
(fuera del repositorio), con nuevo recuento de aciertos sobre la copia.

Salida: experiments/results/b5_anon_audit15.json.
"""
import glob
import hashlib
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit15_common as C                                         # noqa: E402

OUT = os.path.join(C.RESULTS, "b5_anon_audit15.json")
TEXT_EXT = (".py", ".md", ".json", ".csv", ".txt", ".toml", ".cff", ".ps1", ".sh", ".tex", ".log", ".bib", ".yml", ".yaml")
MARKER_EMAIL = "anonymous@example.org"
PATTERNS = {
    "ruta_de_usuario": r"(?i)[a-z]:(?:\\\\|\\|/)+users(?:\\\\|\\|/)+[^\\/\s\"'<>|]+|/c/Users/[^/\s\"'<>|]+|/home/[^/\s\"'<>|]+",
    "usuario_git": r"(?i)andrestellez84",
    "usuario_local": r"(?<![A-Za-z])andre(?![A-Za-z])",
    "apellido": r"(?i)t[eé]llez",
    "correo": r"(?<![A-Za-z0-9._%+-])(?!anonymous@example\.org(?![A-Za-z0-9.-]))[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
    "url_repositorio": r"https?://(?:www\.)?(?:github\.com|gitlab\.com|bitbucket\.org|osf\.io|zenodo\.org)/[^\s\"')<>\]]+",
    "hash_de_commit": r"(?<![0-9a-f])[0-9a-f]{40}(?![0-9a-f])",
}
REPLACE = {
    "ruta_de_usuario": "<RUTA_ANONIMA>",
    "usuario_git": "anonymous-author",
    "usuario_local": "user",
    "apellido": "Author",
    "correo": MARKER_EMAIL,
    "url_repositorio": "[supplementary files provided to the journal]",
}
SAMPLES = 5
EXCLUDE = ("experiments/results/b5_anon_audit15.json", "experiments/audit15_b5_anon.py")
DROP_LINES = {"experiments/protocol_audit15.md": (314,)}          # enmienda 1, E1.7 (linea del commit be2280c)


def scope():
    """Alcance de la enmienda 1 (E1.7): sin supplementary/ ni los archivos del propio inventario de B15.5."""
    files = set()
    with open(os.path.join(C.REPO, "supplementary", "reproduce.ps1"), encoding="utf-8") as f:
        for m in re.finditer(r"experiments/[A-Za-z0-9_]+\.py", f.read()):
            files.add(os.path.join(C.REPO, m.group(0)))
    for p in ("pyproject.toml", "CITATION.cff", "requirements.txt"):
        files.add(os.path.join(C.REPO, p))
    pats = ("experiments/results/*.json", "experiments/protocol*.md", "experiments/prediccion*.md", "experiments/*.py",
            "experiments/*.sh", "experiments/results/tables_audit1[345]/*", "paper/figures/*_audit13q.pdf")
    for pat in pats:
        files.update(p for p in glob.glob(os.path.join(C.REPO, pat)) if os.path.isfile(p))
    keep = [os.path.abspath(p) for p in files if os.path.exists(p)]
    return sorted(p for p in keep if os.path.relpath(p, C.REPO).replace("\\", "/") not in EXCLUDE
                  and not os.path.relpath(p, C.REPO).replace("\\", "/").startswith("supplementary/"))


def scan_text(path, text):
    hits = {}
    for cat, pat in PATTERNS.items():
        ms = list(re.finditer(pat, text))
        if ms:
            hits[cat] = {"count": len(ms), "samples": [{"line": text.count("\n", 0, m.start()) + 1, "match": m.group(0)[:120]}
                                                       for m in ms[:SAMPLES]]}
    return hits


def pdf_meta(path):
    import fitz
    with fitz.open(path) as d:
        return {k: v for k, v in (d.metadata or {}).items() if v}


def inventory(files, root):
    inv, pdfs = {}, {}
    for p in files:
        r = os.path.relpath(p, root).replace("\\", "/")
        if p.lower().endswith(".pdf"):
            pdfs[r] = pdf_meta(p)
            continue
        if not p.lower().endswith(TEXT_EXT):
            continue
        with open(p, encoding="utf-8", errors="replace") as f:
            h = scan_text(p, f.read())
        if h:
            inv[r] = h
    return inv, pdfs


def totals(inv):
    t = {cat: {"files": 0, "hits": 0} for cat in PATTERNS}
    for h in inv.values():
        for cat, x in h.items():
            t[cat]["files"] += 1
            t[cat]["hits"] += x["count"]
    return t


def anonymize_text(text, rel_path):
    drop = DROP_LINES.get(rel_path)
    if drop:
        lines = text.splitlines(keepends=True)
        text = "".join(l for i, l in enumerate(lines, 1) if i not in drop)
    for cat, rep in REPLACE.items():
        text = re.sub(PATTERNS[cat], rep, text)
    return text


def build_copy(files, dest):
    pdf_done = 0
    for p in files:
        r = os.path.relpath(p, C.REPO)
        q = os.path.join(dest, r)
        os.makedirs(os.path.dirname(q), exist_ok=True)
        if p.lower().endswith(TEXT_EXT):
            with open(p, encoding="utf-8", errors="replace") as f:
                t = f.read()
            with open(q, "w", encoding="utf-8", newline="") as f:
                f.write(anonymize_text(t, r.replace("\\", "/")))
        elif p.lower().endswith(".pdf"):
            import fitz
            with fitz.open(p) as d:
                d.set_metadata({})
                d.del_xml_metadata()
                d.save(q, garbage=3, deflate=True)
            pdf_done += 1
        else:
            shutil.copy2(p, q)
    return pdf_done


def git_authors():
    lines = C.git("log", "--all", "--format=%an <%ae>|%cn <%ce>").splitlines()
    names = set()
    for l in lines:
        names.update(x.strip() for x in l.split("|") if x.strip())
    return sorted(names)


def main():
    files = scope()
    inv, pdfs = inventory(files, C.REPO)
    dest = os.path.join(tempfile.mkdtemp(prefix="anon_audit15_"), "package")
    npdf = build_copy(files, dest)
    copied = sorted(os.path.join(dp, f) for dp, _, fs in os.walk(dest) for f in fs)
    inv2, pdfs2 = inventory(copied, dest)
    t_after = totals(inv2)
    residual = {}
    for r, h in inv2.items():
        for cat, x in h.items():
            if cat != "hash_de_commit":
                residual.setdefault(cat, []).append({"file": r, "count": x["count"], "samples": x["samples"]})
    out = {"provenance": C.provenance(__file__), "reading": "protocol_audit15.md, lecturas 5.1 y 5.2",
           "scope": {"files": len(files), "by_top_dir": {d: sum(1 for p in files if os.path.relpath(p, C.REPO).replace("\\", "/").startswith(d))
                                                         for d in ("supplementary/", "experiments/results/", "experiments/", "paper/")}},
           "patterns": PATTERNS, "inventory": inv, "totals": totals(inv), "pdf_metadata": pdfs,
           "pdf_fields_present": sorted({k for m in pdfs.values() for k in m}),
           "git_history_identities": git_authors(),
           "supplementary_describes": "supplementary/README.md y CITATION.cff describen el paquete original (estadistico de dos canales)",
           "proposal": {"replacements": REPLACE, "commit_hashes": "se conservan (el repositorio sera privado durante la revision)",
                        "excluded_files": list(EXCLUDE), "dropped_lines": {k: list(v) for k, v in DROP_LINES.items()},
                        "supplementary": "fuera del alcance: se rehara segun SUPPLEMENT_PLAN.md (bloque aparte, despues de B15.1)",
                        "pdf": "metadatos Info y XMP vaciados (PyMuPDF set_metadata({}) y del_xml_metadata())",
                        "git": "no distribuir .git; la historia contiene las identidades listadas",
                        "citation": "CITATION.cff sin repository-code ni autores durante la revision",
                        "external_url": "ninguna: el suplemento va como archivos a la revista"},
           "trial_build": {"location": "directorio temporal de la sesion, fuera del repositorio (no se registra la ruta)",
                           "files": len(copied), "pdf_rewritten": npdf, "hashes_kept": t_after["hash_de_commit"]["hits"],
                           "totals_after": t_after, "residual_non_hash": residual,
                           "pdf_fields_after": sorted({k for m in pdfs2.values() for k in m}),
                           "clean": not residual and not any(k != "format" for m in pdfs2.values() for k in m)},
           "previous_residue": {"commit": "0a76b01", "string": MARKER_EMAIL,
                                "cause": "el residuo correo de la corrida limpia del commit 0a76b01 era el propio marcador de reemplazo, "
                                         "dentro de experiments/results/b5_anon_audit15.json de la corrida de prueba anterior, que "
                                         "estaba en el alcance; su conteo (6) superaba las 5 muestras guardadas y el criterio lo conto "
                                         "como residuo. El mensaje 'queda limpia' describia la corrida de prueba anterior, en la que "
                                         "ese JSON aun no existia; el reporte describia la corrida limpia. Corregido: el JSON y este "
                                         "script salen del alcance y el detector excluye el marcador (enmienda 1, E1.7)."},
           "sha256_manifest_of_scope": hashlib.sha256("".join(sorted(C.sha256_file(p) for p in files)).encode()).hexdigest()}
    C.write_result(OUT, out, __file__)
    shutil.rmtree(os.path.dirname(dest), ignore_errors=True)
    print("archivos en alcance:", len(files), out["scope"]["by_top_dir"])
    for cat, x in out["totals"].items():
        print("  %-16s archivos %4d aciertos %6d" % (cat, x["files"], x["hits"]))
    print("PDF con metadatos:", sum(1 for m in pdfs.values() if m), "de", len(pdfs), "campos", out["pdf_fields_present"])
    print("identidades en git:", out["git_history_identities"])
    print("copia de prueba: limpia", out["trial_build"]["clean"], "residuo", residual, "hashes conservados",
          out["trial_build"]["hashes_kept"],
          "campos PDF despues", out["trial_build"]["pdf_fields_after"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
