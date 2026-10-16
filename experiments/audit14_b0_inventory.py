"""
Auditoria A14 - B14.0: entrada v15 (protocol_audit14.md, lecturas 1 y 2).

Registra el sha256 de paper_latex_v15.zip y el commit del protocolo, y compara byte a
byte los 17 archivos de v15/tables/ (16 tabulares y la nota de tab:attrib) con
experiments/results/tables_audit13/ (A13 y B13.Q Q1) y las 6 figuras v15/figures/*_audit13q.pdf
con paper/figures/ (B13.Q Q2). Extension declarada: todo \\input{tables/...} y todo
\\includegraphics del texto apuntan a un archivo del zip, y no quedan figuras *_audit13.pdf.
Familia 150: reservada y sin uso (solo se registra que no colisiona con las previas).

Salida: experiments/results/b0_inventory_audit14.json.
"""
import hashlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit14_common as C                                         # noqa: E402

OUT = os.path.join(C.RESULTS, "b0_inventory_audit14.json")


def local_of(name):
    if name.startswith("tables/") and name.endswith(".tex"):
        return os.path.join(C.TABLES_A13, os.path.basename(name))
    if name.startswith("figures/") and name.endswith(".pdf"):
        return os.path.join(C.PAPER_FIGURES, os.path.basename(name))
    return None


def main():
    v = C.V15()
    files = {}
    for name, data in sorted(v.binary.items()):
        local = local_of(name)
        if local is None:
            continue
        h = hashlib.sha256(data).hexdigest()
        lh = C.sha256_file(local) if os.path.exists(local) else None
        files[name] = {"kind": "tabular" if name.endswith(".tex") else "figura", "sha256_v15": h, "local": C.rel(local),
                       "sha256_local": lh, "identical": h == lh}
    refs = []
    for fname in C.TEXT_FILES:
        if not fname.endswith(".tex"):
            continue
        for i, line in enumerate(v.lines(fname), 1):
            code = re.split(r"(?<!\\)%", line)[0]
            for m in re.finditer(r"\\input\{(tables/[^}]+)\}", code):
                t = m.group(1) if m.group(1).endswith(".tex") else m.group(1) + ".tex"
                refs.append({"file": "v15/" + fname, "line": i, "kind": "input", "target": t, "in_zip": t in v.binary})
            for m in re.finditer(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", code):
                t = m.group(1) if m.group(1).endswith(".pdf") else m.group(1) + ".pdf"
                t = t if t.startswith("figures/") else "figures/" + t
                refs.append({"file": "v15/" + fname, "line": i, "kind": "includegraphics", "target": t, "in_zip": t in v.binary})
    old_figs = sorted(n for n in v.binary if re.match(r"figures/.*_audit13\.pdf$", n))
    tabs = [k for k, f in files.items() if f["kind"] == "tabular"]
    figs = [k for k, f in files.items() if f["kind"] == "figura"]
    out = {"provenance": C.provenance(__file__, seed_family=None), "manuscript": v.record(),
           "protocol": C.committed(C.PROTOCOL), "reading": "protocol_audit14.md, lecturas 1 y 2",
           "family": {"reserved": C.FAMILY["RESERVED"], "used": False,
                      "collides_with_prior": C.FAMILY["RESERVED"] in C.PRIOR_FAMILIES,
                      "prior_range": [min(C.PRIOR_FAMILIES), max(C.PRIOR_FAMILIES)]},
           "text_files": list(C.TEXT_FILES), "files_vs_exports": files,
           "n_tables_dir_files": len(tabs), "n_tabulars": sum(1 for k in tabs if not k.endswith("_note_audit13.tex")),
           "n_figures": len(figs), "all_identical": all(f["identical"] for f in files.values()),
           "references": refs, "references_all_in_zip": all(r["in_zip"] for r in refs),
           "unreferenced_zip_files": sorted(k for k in files if k not in {r["target"] for r in refs}),
           "old_figures_audit13_in_zip": old_figs}
    C.write_result(OUT, out, __file__)
    print(out["manuscript"], "protocolo", (out["protocol"]["commit_added"] or "")[:7])
    print("archivos de tables/: %d (tabulares %d), figuras %d, identicos %s" % (
        len(tabs), out["n_tabulars"], len(figs), out["all_identical"]))
    print("referencias: %d, todas en el zip %s; sin referenciar %s; figuras sin q %s" % (
        len(refs), out["references_all_in_zip"], out["unreferenced_zip_files"], old_figs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
