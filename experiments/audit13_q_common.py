"""
Auditoria A13 - B13.Q: lectura del v14 (protocol_audit13_amend1.md, lectura 2).

Lee ../paper_latex_v14.zip sin extraerlo: archivos de texto (.tex, .md) y
tabulares por etiqueta, con la misma logica que audit13_tables.V13.
"""
import io
import os
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit13_common as C                                         # noqa: E402
import audit13_tables as TB                                        # noqa: E402

MANUSCRIPT_V14 = os.path.join(os.path.dirname(C.REPO), "paper_latex_v14.zip")
PREFIX = "v14/"
TEXT_FILES = ("main.tex", "sec1_introduction.tex", "sec2_statistic.tex", "sec3_theory.tex", "sec4_implementation.tex",
              "sec5_montecarlo.tex", "sec6_application.tex", "sec7_conclusion.tex", "appA_proofs.tex",
              "appB_critical_values.tex", "appC_tables.tex", "highlights.tex", "cover_letter.md")


class V14(TB.V13):
    def __init__(self, path=MANUSCRIPT_V14):
        with open(path, "rb") as f:
            self.raw = f.read()
        self.path = path
        self.z = zipfile.ZipFile(io.BytesIO(self.raw))
        self.files = {n[len(PREFIX):]: self.z.read(n).decode("utf-8") for n in self.z.namelist()
                      if n.endswith((".tex", ".md"))}
        self.binary = {n[len(PREFIX):]: self.z.read(n) for n in self.z.namelist() if not n.endswith("/")}

    def lines(self, fname):
        return self.files[fname].splitlines()

    def record(self):
        return {"path": os.path.basename(self.path), "sha256": C.sha256_file(self.path), "bytes": len(self.raw)}
