"""
Auditoria A12 - frases del manuscrito v12 que tocan B12.A-F (para la seccion 7 del reporte).

Lee paper_latex_v12.zip sin extraerlo (clase Manuscript de audit11_t5_claims) y
registra archivo:linea, la cita y los grupos capturados. No compara nada: la
comparacion con los resultados la hace el generador del reporte leyendo este JSON y
los de los bloques.

Salida: experiments/results/claims_audit12.json.
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit12_common as C                                         # noqa: E402
from audit11_t5_claims import Manuscript                           # noqa: E402

OUT = os.path.join(C.RESULTS, "claims_audit12.json")
PATTERNS = {
    "ma_mtests": ("sec1_introduction.tex", r"better size control in the presence of negative moving-average", 2),
    "hac_scale": ("sec1_introduction.tex", r"scales that moment by a Bartlett HAC estimate", 2),
    "initial_sec1": ("sec1_introduction.tex", r"our designs set it to zero", 1),
    "initial_sec3": ("sec3_theory.tex", r"our alternatives start at zero", 2),
    "anchor_remark": ("sec3_theory.tex", r"\\frac12 - \\frac\{\\kappa\(\\cbar\)\}\{n\} \+ O\(n\^\{-2\}\)", 1),
    "anchor_sim": ("appA_proofs.tex", r"gives \$([0-9.]+)\$, \$([0-9.]+)\$ and \$([0-9.]+)\$ at \$n = (\d+)\$, \$(\d+)\$ and \$(\d+)\$", 2),
    "anchor_remark_n2000": ("sec3_theory.tex", r"accurate at \$n = (\d+)\$ \(simulated \$([0-9.]+)\$", 2),
    "anchor_remark_n200": ("sec3_theory.tex", r"not at \$n = (\d+)\$ \(simulated \$([0-9.]+)\$", 2),
    "attrib_power": ("sec5_montecarlo.tex", r"power: \$([0-9.]+)\$ points on average over the seven autoregressive", 2),
    "attrib_size": ("sec5_montecarlo.tex", r"\(a\)\$-\$\(b\) is within \$([0-9.]+)\$", 1),
    "attrib_mechanism": ("sec5_montecarlo.tex", r"does not collapse as fast in", 1),
    "ma_not_examined": ("sec7_conclusion.tex", r"whether it survives negative moving-average", 2),
    "initial_sec7": ("sec7_conclusion.tex", r"all our alternatives start from a zero initial", 2),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manuscript-zip", default=os.path.join(os.path.dirname(C.REPO), "paper_latex_v12.zip"))
    a = ap.parse_args()
    M = Manuscript(a.manuscript_zip)
    quotes = {k: M.find(f, pat, span) for k, (f, pat, span) in PATTERNS.items()}
    out = {"provenance": C.provenance(__file__), "manuscript": {"zip": os.path.basename(a.manuscript_zip),
                                                               "sha256": C.sha256_file(a.manuscript_zip)},
           "quotes": quotes}
    C.write_result(OUT, out, __file__)
    for k, q in quotes.items():
        print(k, q["file"], q["line"], q["groups"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
