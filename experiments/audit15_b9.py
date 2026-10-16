"""
Auditoria A15 - B15.9 (enmienda 5, lecturas 9.2 y 9.3). Sin simulacion.

9.2: supplement_plan_v17_audit15.json con la lista de tablas y textos que pasan del cuerpo al suplemento en
     la reconstruccion posterior al v17, tal como la da el encargo (no se ejecuta nada).
9.3: descarga (autorizada en el encargo) de la plantilla Interact de Taylor & Francis a experiments/external_audit15/
     (no se commitea, E3.6); registra URL, tamano, sha256, \\ProvidesClass de interact.cls y los estilos de
     referencias (.bst) que trae el paquete. El estilo que pide la revista se declara como evidencia indirecta.

Salidas: experiments/results/supplement_plan_v17_audit15.json, experiments/results/template_audit15.json.
"""
import os
import re
import sys
import urllib.request
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit15_common as C                                         # noqa: E402

OUT_PLAN = os.path.join(C.RESULTS, "supplement_plan_v17_audit15.json")
OUT_TPL = os.path.join(C.RESULTS, "template_audit15.json")
EXT = os.path.join(HERE, "external_audit15")
TPL_URL = "https://files.taylorandfrancis.com/InteractNLMLaTeX.zip"
TPL_FILE = os.path.join(EXT, "InteractNLMLaTeX.zip")
OVERLEAF = ("https://www.sharelatex.com/templates/journals/journal-of-statistical-computation-and-simulation",
            "Taylor & Francis LaTeX template for authors (Interact layout + NLM reference style)")

# Encargo B15.9.2, literal
PLAN_TABLES = ("tab:serial", "tab:boot", "tab_serial_asy", "tab_fixedb_size", "tab_lag", "tab:size", "tab:dgp1", "tab:ctpower",
               "tab:dgp2", "tab:dgp3", "tab:misspec", "tab:awb", "tab:dgp5", "tab:initial", "tab:serialpower", "tab:critB")
PLAN_OTHER = ("las seis figuras", "texto de sec:theta con tab:deviations", "aplicacion completa (sec6 y tab:fp)")


def plan():
    out = {"provenance": C.provenance(__file__), "reading": "enmienda 5, lectura 9.2",
           "status": "lista registrada; la reconstruccion se hace despues del v17",
           "tables_to_supplement": list(PLAN_TABLES), "n_tables": len(PLAN_TABLES), "also": list(PLAN_OTHER),
           "text_literal": ("tab:serial, tab:boot, tab_serial_asy, tab_fixedb_size, tab_lag, tab:size, tab:dgp1, tab:ctpower, "
                            "tab:dgp2, tab:dgp3, tab:misspec, tab:awb, tab:dgp5, tab:initial, tab:serialpower, tab:critB y las "
                            "seis figuras; mas el texto de sec:theta con tab:deviations, y la aplicacion completa (sec6 y tab:fp).")}
    C.write_result(OUT_PLAN, out, __file__)
    print("plan:", len(PLAN_TABLES), "tablas +", PLAN_OTHER)


def template():
    os.makedirs(EXT, exist_ok=True)
    downloaded = False
    if not os.path.exists(TPL_FILE):
        req = urllib.request.Request(TPL_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as r, open(TPL_FILE, "wb") as fh:
            fh.write(r.read())
        downloaded = True
    with zipfile.ZipFile(TPL_FILE) as z:
        names = z.namelist()
        cls = [n for n in names if n.lower().endswith("interact.cls")]
        provides = None
        if cls:
            txt = z.read(cls[0]).decode("latin-1")
            m = re.search(r"\\ProvidesClass\{[^}]*\}\s*\[([^\]]*)\]", txt)
            provides = m.group(1).strip() if m else None
        bst = [n for n in names if n.lower().endswith(".bst")]
        tex = [n for n in names if n.lower().endswith(".tex")]
        style_lines = {}
        for n in tex:
            t = z.read(n).decode("latin-1")
            style_lines[n] = sorted(set(re.findall(r"\\bibliographystyle\{[^}]*\}", t)))
    out = {"provenance": C.provenance(__file__), "reading": "enmienda 5, lectura 9.3",
           "url": TPL_URL, "local": C.rel(TPL_FILE), "committed": False, "downloaded_this_run": downloaded,
           "bytes": os.path.getsize(TPL_FILE), "sha256": C.sha256_file(TPL_FILE),
           "interact_cls": cls, "provides_class": provides, "files": names, "bst_files": bst,
           "bibliographystyle_in_tex": style_lines,
           "reference_style": {"from_package": "NLM (nombre del paquete y archivos .bst incluidos)",
                               "journal_instructions": "tandfonline.com devuelve 403 desde este entorno; no leidas",
                               "indirect_evidence": {"overleaf_link": OVERLEAF[0], "redirects_to": OVERLEAF[1]},
                               "confirm_by_author": True}}
    C.write_result(OUT_TPL, out, __file__)
    print("plantilla:", out["bytes"], "bytes", out["sha256"], "|", provides, "| bst:", bst, "|", style_lines)


if __name__ == "__main__":
    stage = sys.argv[1] if len(sys.argv) > 1 else "all"
    if stage in ("all", "plan"):
        plan()
    if stage in ("all", "template"):
        template()
