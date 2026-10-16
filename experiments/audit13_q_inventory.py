"""
Auditoria A13 - B13.Q, Q0: entrada v14 (protocol_audit13_amend1.md, lectura 2).

Registra el sha256 de paper_latex_v14.zip, el commit de la enmienda y compara byte a
byte los tabulares v14/tables/*_audit13.tex y las figuras v14/figures/*_audit13.pdf con
los exportados por A13 (experiments/results/tables_audit13 y paper/figures).

Salida: experiments/results/q_inventory_audit13.json.
"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit13_common as C                                         # noqa: E402
import audit13_q_common as Q                                       # noqa: E402
import audit12_b120_inventory as B120                              # noqa: E402

OUT = os.path.join(C.RESULTS, "q_inventory_audit13.json")
AMENDMENT = "experiments/protocol_audit13_amend1.md"


def main():
    v = Q.V14()
    files = {}
    for name, data in sorted(v.binary.items()):
        if name.startswith("tables/") and name.endswith("_audit13.tex"):
            local = os.path.join(C.TABLES, os.path.basename(name))
        elif name.startswith("figures/") and name.endswith("_audit13.pdf"):
            local = os.path.join(C.PAPER_FIGURES, os.path.basename(name))
        else:
            continue
        h = hashlib.sha256(data).hexdigest()
        lh = C.sha256_file(local) if os.path.exists(local) else None
        files[name] = {"sha256_v14": h, "local": C.rel(local), "sha256_local": lh, "identical": h == lh}
    out = {"provenance": C.provenance(__file__, seed_family=None), "manuscript": v.record(),
           "amendment": B120.committed(AMENDMENT), "reading": "protocol_audit13_amend1.md, lectura 2",
           "text_files": list(Q.TEXT_FILES), "files_vs_a13": files, "all_identical": all(f["identical"] for f in files.values())}
    C.write_result(OUT, out, __file__)
    print(out["manuscript"], "enmienda", out["amendment"]["commit_added"][:7], "identicos", out["all_identical"], len(files))
    return 0


if __name__ == "__main__":
    sys.exit(main())
