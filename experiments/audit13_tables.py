"""
Auditoria A13 - B13.E(1)-(2): tablas del manuscrito regeneradas con theta = 0.

Solo lee JSON (y el v13 para la estructura). Para cada tabla que el v13 reporta con
theta = 0.02 (protocol_audit13.md, lecturas 2, 5, 13 y 15):
  - las filas (claves) y el formato se toman del tabular del v13;
  - las cifras se rellenan desde los JSON dos veces: con la fuente del v13
    (theta = 0.02) y con la de A13 (theta = 0);
  - Paso 0 de transcripcion: la version theta = 0.02 reproduce celda a celda el
    tabular impreso (numero y negrita);
  - compuerta informativa: diferencia maxima entre theta = 0 y theta = 0.02 en las
    celdas de RM-GLS, en las unidades de la tabla;
  - el tabular con theta = 0 se escribe en
    experiments/results/tables_audit13/tab_<nombre>_audit13.tex, con la misma
    disposicion que el v13 (solo cambian las cifras y las etiquetas de theta).

Salida: experiments/results/tables_audit13.json.
"""
import decimal
import io
import math
import os
import re
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit13_common as C                                         # noqa: E402

OUT = os.path.join(C.RESULTS, "tables_audit13.json")
V13_DIR = "v13/"
RULES = re.compile(r"^\s*((\\(toprule|midrule|bottomrule|addlinespace)|\\cmidrule\([a-z]*\)\{[^}]*\})\s*)+")
NUM = re.compile(r"[-+]?\d*\.?\d+")


# ---------------------------------------------------------------------------
# Lectura del v13
# ---------------------------------------------------------------------------
class V13:
    def __init__(self, path):
        with open(path, "rb") as f:
            self.raw = f.read()
        self.z = zipfile.ZipFile(io.BytesIO(self.raw))
        self.files = {n[len(V13_DIR):]: self.z.read(n).decode("utf-8") for n in self.z.namelist()
                      if n.endswith(".tex")}

    def tabular(self, label):
        for fname, text in self.files.items():
            i = text.find("\\label{tab:%s}" % label)
            if i < 0:
                continue
            j = text.find("\\begin{tabular}", i)
            k = text.find("\\input{", i)
            if k >= 0 and (j < 0 or k < j):
                name = text[k + len("\\input{"):text.find("}", k)]
                return name + ".tex", self.tabular_in(self.files[name + ".tex"])
            return fname, self.tabular_in(text[j:])
        raise KeyError(label)

    @staticmethod
    def tabular_in(text):
        a = text.find("\\begin{tabular}")
        b = text.find("\\end{tabular}", a)
        return text[a:b + len("\\end{tabular}")]


def split_rows(tab):
    """Trozos separados por \\\\: (prefijo de reglas, contenido, separador)."""
    body = tab
    parts = re.split(r"(\\\\)", body)
    out = []
    for i in range(0, len(parts), 2):
        chunk = parts[i]
        sep = parts[i + 1] if i + 1 < len(parts) else ""
        m = RULES.match(chunk.lstrip("\n"))
        lead = chunk[:len(chunk) - len(chunk.lstrip("\n"))]
        rest = chunk.lstrip("\n")
        pre = m.group(0) if m else ""
        out.append([lead + pre, rest[len(pre):], sep])
    return out


def cells_of(content):
    return [c.strip() for c in content.split("&")]


def norm(cell):
    s = cell.strip()
    bold = s.startswith("\\textbf{")
    if bold:
        s = s[len("\\textbf{"):-1]
    s = s.replace("$", "").replace(" ", "").replace("\\%", "%")
    return bold, s


def num(cell):
    m = NUM.search(cell.replace("$", ""))
    return float(m.group(0)) if m else None


def data_rows(tab, nkey):
    """[(indice del trozo, seccion, claves, celdas)] de las filas de datos del tabular."""
    rows, section = [], None
    chunks = split_rows(tab)
    in_body = False
    for i, (pre, content, sep) in enumerate(chunks):
        in_body = in_body or "\\midrule" in pre
        c = content.strip()
        if not in_body or not c:
            continue
        if "\\multicolumn" in c and "&" not in c:
            section = re.sub(r"\\multicolumn\{\d+\}\{[a-z]\}\{", "", c).replace("\\emph{", "").replace("}", "").strip()
            continue
        if c.startswith("\\multicolumn") and "&" in c:
            cl = cells_of(c)
            rows.append((i, section, [cl[0]], cl[1:]))
            continue
        if "&" not in c:
            continue
        cl = cells_of(c)
        rows.append((i, section, cl[:nkey], cl[nkey:]))
    return chunks, rows


def rebuild(chunks, rows, new_cells, header_subs=()):
    out = [list(ch) for ch in chunks]
    for (i, _, keys, _), cells in zip(rows, new_cells):
        out[i][1] = " & ".join(keys + cells) + " "
    text = "".join(a + b + c for a, b, c in out)
    for old, new in header_subs:
        text = text.replace(old, new, 1)
    return text


# ---------------------------------------------------------------------------
# Formato
# ---------------------------------------------------------------------------
ROUNDING = {"mode": "binary"}
VALUES = []          # valores sin redondear por celda de cada fila construida (doble redondeo)
MODES = ("binary", "half_up")


def fdec(x, d, mode=None):
    """
    Redondeo a d decimales. "binary": el de "%.*f" de Python (flotante binario).
    "half_up": mitad hacia arriba sobre la representacion decimal (el de una
    transcripcion a mano desde una tabla de 4 decimales). La convencion de cada
    tabla es la que reproduce el v13 (Paso 0 de transcripcion).
    """
    mode = mode or ROUNDING["mode"]
    if mode == "binary":
        return "%.*f" % (d, x)
    q = decimal.Decimal(1).scaleb(-d)
    return str(decimal.Decimal(repr(float(x))).quantize(q, rounding=decimal.ROUND_HALF_UP))


def f3(x):
    return fdec(x, 3)


def f4(x):
    return fdec(x, 4)


def bold(s, flag):
    return "\\textbf{%s}" % s if flag else s


def in_reg(r, region=None):
    if "in_region" in r:
        return r["in_region"]
    return region[0] <= r["rate"] <= region[1]


P_DEC = 3            # decimales de los p-valores del v13; por debajo de 10^-3: "<0.001" o notacion cientifica


def p_small(p):
    return "$<$%.*f" % (P_DEC, 10 ** -P_DEC) if p < 10 ** -P_DEC else "%.*f" % (P_DEC, p)


def p_sci(p):
    if p >= 10 ** -P_DEC:
        return "%.*f" % (P_DEC, p)
    e = int(math.floor(math.log10(p)))
    return "$%.1f\\times10^{%d}$" % (p / 10 ** e, e)


def rtag(x):
    return ("%g" % x).replace(".", "p")


# ---------------------------------------------------------------------------
# Constructores: devuelven (celdas, valores de RM-GLS para la compuerta)
# ---------------------------------------------------------------------------
def build_size(rows, src):
    out, gate = [], {}
    for _, _, keys, _ in rows:
        n = int(num(keys[0]))
        cells = []
        for case in ("dm", "ct"):
            r = src["%s|%d" % (case, n)]
            cells.append("%s [%s, %s]" % (f4(r["rate"]), f4(r["wilson_lower"]), f4(r["wilson_upper"])))
            gate["%s|%d" % (case, n)] = r["rate"]
        out.append(cells)
        VALUES.append([None, None])
    return out, gate


def size_sources():
    es = C.read_json("e_size_audit13.json")
    low = C.read_json("b103_lown_audit10.json")
    b101 = C.read_json("b101_theta_audit10.json")
    new = {k: v["rates"][C.PRIM] for k, v in es["cells"].items()}
    old = {}
    for k in es["cells"]:
        old[k] = low["cells"][k]["rates"][C.PRIM_V13] if k in low["cells"] else b101["cells"][k]["rates"][C.PRIM_V13]["pooled"]
    return new, old


def build_calib(rows, cases):
    det = {"Constant": "c", "Trend": "ct"}
    out, gate = [], {}
    for _, sec, keys, _ in rows:
        n = str(int(num(keys[0])))
        c = cases[det[sec]]
        ac = c["approximation_cost"][n]
        cm = c["approximation_cost_comparators"][n]
        cells = [f4(ac["cv_at_n"])]
        for r in (ac["size_with_cv_at_n"], ac["size_with_cv_n20000"], cm["dfgls"]["size_published_asymptotic"],
                  cm["dfgls"]["size_simulated_at_n"], cm["msb"]["size_published_asymptotic"], cm["msb"]["size_simulated_at_n"]):
            cells.append(bold(f4(r["rate"]), not in_reg(r)))
        out.append(cells)
        VALUES.append([ac["cv_at_n"]] + [r["rate"] for r in (ac["size_with_cv_at_n"], ac["size_with_cv_n20000"],
                      cm["dfgls"]["size_published_asymptotic"], cm["dfgls"]["size_simulated_at_n"],
                      cm["msb"]["size_published_asymptotic"], cm["msb"]["size_simulated_at_n"])])
        gate["%s|%s|q" % (det[sec], n)] = ac["cv_at_n"]
        gate["%s|%s|size_q_n" % (det[sec], n)] = ac["size_with_cv_at_n"]["rate"]
        gate["%s|%s|size_q_20000" % (det[sec], n)] = ac["size_with_cv_n20000"]["rate"]
    return out, gate


def build_localpower(rows, prim, other):
    b92 = C.read_json("b92_theta_audit9.json")
    det = {"Constant": "dm", "Trend": "ct"}
    out, gate = [], {}
    for _, sec, keys, _ in rows:
        c = "%s" % float(num(keys[0]))
        pw = b92["local_power"][det[sec]]["power"][c]
        ps = ("envelope", prim, other, "dfgls", "mzt", "msb", "msb_asy")
        out.append([f3(pw[p]) for p in ps])
        VALUES.append([pw[p] for p in ps])
        gate["%s|c%s" % (det[sec], c)] = pw[prim]
    return out, gate


EQ_PROCS = ("rm_t0.1", "adf", "pp", "dfgls", "mzt", "msb")


def build_power(rows, cells, prim, prefix):
    out, gate = [], {}
    for _, _, keys, _ in rows:
        rho, n = num(keys[0]), int(num(keys[1]))
        k = "%s_rho%s_n%d" % (prefix, rtag(rho), n)
        c = cells[k]
        out.append([f3(c["rates_sim"][prim]["rate"])] + [f3(c["rates_sim"][p]["rate"]) for p in EQ_PROCS]
                   + [p_small(c["mcnemar_primary_vs_sim"]["dfgls"]["p_value"])])
        VALUES.append([c["rates_sim"][p]["rate"] for p in (prim,) + EQ_PROCS] + [c["mcnemar_primary_vs_sim"]["dfgls"]["p_value"]])
        gate[k] = c["rates_sim"][prim]["rate"]
    return out, gate


def build_dgp2(rows, cells, prim):
    out, gate = [], {}
    for _, _, keys, _ in rows:
        d, n = num(keys[0]), int(num(keys[1]))
        k = "dgp2_delta%s_n%d" % (rtag(d), n)
        c = cells[k]
        out.append([f3(c["rates_sim"][p]["rate"]) for p in (prim,) + EQ_PROCS + ("za",)]
                   + [p_sci(c["mcnemar_primary_vs_sim"]["dfgls"]["p_value"])])
        VALUES.append([c["rates_sim"][p]["rate"] for p in (prim,) + EQ_PROCS + ("za",)] + [None])
        gate[k] = c["rates_sim"][prim]["rate"]
    return out, gate


def build_dgp3(rows, cells, prim):
    out, gate = [], {}
    for _, _, keys, _ in rows:
        r, n = num(keys[0]), int(num(keys[1]))
        k = "dgp3_r%s_n%d" % (rtag(r), n)
        c = cells[k]
        out.append([bold(f3(c["rates_sim"][p]["rate"]), not in_reg(c["rates_sim"][p])) for p in (prim,) + EQ_PROCS])
        VALUES.append([c["rates_sim"][p]["rate"] for p in (prim,) + EQ_PROCS])
        gate[k] = c["rates_sim"][prim]["rate"]
    return out, gate


MISSPEC_LABEL = {"t(5)": "heavy_t5", "t(3)": "heavy_t3", "G0.95,N": "garch_base", "G0.98,N": "garch_p098",
                 "G0.99,N": "garch_p099", "G0.95,t(5)": "garch_p095_t5"}
MISSPEC_PROCS = ("adf", "adf_asy", "pp_asy", "dfgls", "mzt", "msb")


def build_misspec(rows, prim):
    b92 = C.read_json("b92_theta_audit9.json")
    mis = b92["misspec"]
    out, gate, shifts = [], {}, {}
    for _, _, keys, _ in rows:
        if keys[0].startswith("\\multicolumn"):
            n = int(num(keys[0].split("$n =")[1]))
            cells = [k for k in mis if k.startswith("c|garch_") and k.endswith("_n%d" % n)]
            row = []
            for p in (prim,) + MISSPEC_PROCS:
                ds = [mis[k]["delta_vs_independent"][p] for k in cells]
                m = sum(d["delta"] for d in ds) / len(ds)
                se = math.sqrt(sum(d["se"] ** 2 for d in ds)) / len(ds)
                row.append("%+.2f (%.2f)" % (m * C.PP, se * C.PP))
                if p == prim:
                    shifts[str(n)] = {"mean_pp": m * C.PP, "se_pp": se * C.PP, "cells": sorted(cells)}
                    gate["shift|n%d" % n] = m
            out.append(row)
            VALUES.append([None] * len(row))
            continue
        lab = norm(keys[0])[1]
        n = int(num(keys[1]))
        k = "c|%s_n%d" % (MISSPEC_LABEL[lab], n)
        rr = mis[k]["rates"]
        out.append([bold(f4(rr[p]["rate"]), not in_reg(rr[p])) for p in (prim,) + MISSPEC_PROCS])
        VALUES.append([rr[p]["rate"] for p in (prim,) + MISSPEC_PROCS])
        gate[k] = rr[prim]["rate"]
    return out, gate, shifts


def build_critb(rows, theta):
    cv = C.read_json("b103_cv_audit10.json")["table"]
    out, gate = [], {}
    alphas = ("0.01", "0.025", "0.05", "0.1")
    for _, _, keys, _ in rows:
        n = int(num(keys[0]))
        cells = []
        for case in ("dm", "ct"):
            e = cv["%s|%g|%d" % (case, theta, n)]
            cells += [f4(e["cv"][a]) for a in alphas]
            for a in alphas:
                gate["%s|%d|%s" % (case, n, a)] = e["cv"][a]
        out.append(cells)
        VALUES.append([cv["%s|%g|%d" % (cs, theta, n)]["cv"][a] for cs in ("dm", "ct") for a in alphas])
    return out, gate


AWB_LABEL = {"Randomwalk,r=1": "dgp3_r1", "Randomwalk,r=2": "dgp3_r2", "Randomwalk,r=4": "dgp3_r4",
             "GARCH0.95,normal": "garch_base", "GARCH0.98,normal": "garch_p098", "GARCH0.99,normal": "garch_p099",
             "GARCH0.95,t(5)": "garch_p095_t5", "Gaussianrandomwalk": "indep", "AR(0.95)": "dgp1_rho0p95",
             "AR(0.99)": "dgp1_rho0p99"}


def build_awb(rows, cells):
    out, gate = [], {}
    for _, _, keys, _ in rows:
        base = AWB_LABEL[norm(keys[0])[1]]
        n = int(num(keys[1]))
        k = "%s_n%d" % (base, n)
        c = cells[k]
        power = base.startswith("dgp1_")
        row = [bold(f3(c["awb"]["rate"]), not power and not in_reg(c["awb"])),
               bold(f3(c["sim"]["rate"]), not power and not in_reg(c["sim"])),
               p_small(c["mcnemar_awb_vs_sim"]["p_value"]), "%.1f" % c["power_loss_pp"] if power else ""]
        out.append(row)
        VALUES.append([c["awb"]["rate"], c["sim"]["rate"], c["mcnemar_awb_vs_sim"]["p_value"], c["power_loss_pp"]])
        gate[k + "|awb"] = c["awb"]["rate"]
        gate[k + "|sim"] = c["sim"]["rate"]
    return out, gate


def build_dgp5(rows, cells):
    import audit7_design as D7
    out, gate = [], {}
    for _, _, keys, _ in rows:
        rho, r = num(keys[0]), num(keys[1])
        k = D7.dgp5_tag(200, rho, float(r))
        c = cells[k]
        sm = c["size_matched"]
        out.append([f3(sm[p]["rate"]) for p in ("primary", "proposed_R050", "union_joint", "bootstrap_dfgls")]
                   + ["%.2f\\%%" % (c["g2_share_R050_median"] * C.PP)])
        VALUES.append([sm[p]["rate"] for p in ("primary", "proposed_R050", "union_joint", "bootstrap_dfgls")] + [None])
        gate[k] = sm["primary"]["rate"]
    return out, gate


FP_LABEL = {"\\RMGLS{}": "final", "\\RMGLS{},AWB": "final_awb", "Registeredstatistic": "rhat_prereg", "ADF": "adf",
            "PP": "pp", "DF-GLS(AIC)": "dfgls_aic", "DF-GLS(MAIC)": "dfgls_maic", "MZ_t-GLS": "mzt", "KPSS^a": "kpss"}


def build_fp(rows, summary, matched, keymap):
    out, gate = [], {}
    for _, _, keys, _ in rows:
        t = FP_LABEL[norm(keys[0])[1]]
        k = keymap.get(t, t)
        s = summary[k]
        row = [f4(s["fp_mean"]), f3(s["fp_max"]), "%d" % s["detections"], "%.1f" % s["mean_latency_detected"]]
        m = matched["tests"].get(k)
        row += (["%d" % m["false_alarm_episodes"], "%.1f" % m["mean_run_length"], "%.1f" % m["censored_latency_mean"]]
                if m else ["--", "--", "--"])
        out.append(row)
        VALUES.append([s["fp_mean"], s["fp_max"], None, s["mean_latency_detected"], None,
                       m["mean_run_length"] if m else None, m["censored_latency_mean"] if m else None])
        if t in ("final", "final_awb"):
            gate[t + "|fp_mean"] = s["fp_mean"]
            gate[t + "|fp_max"] = s["fp_max"]
            gate[t + "|detections"] = s["detections"]
            gate[t + "|latency"] = s["mean_latency_detected"]
            if m:
                gate[t + "|episodes"] = m["false_alarm_episodes"]
                gate[t + "|latency_c"] = m["censored_latency_mean"]
    return out, gate


# ---------------------------------------------------------------------------
# Comparacion y compuerta
# ---------------------------------------------------------------------------
def decimals(cell):
    s = norm(cell)[1]
    m = re.search(r"\.(\d+)", s)
    return len(m.group(1)) if m else 0


def double_rounding(printed, value):
    """El impreso es el redondeo (mitad hacia arriba) del valor ya redondeado a un decimal mas."""
    d = decimals(printed)
    return norm(printed)[1] == fdec(float(fdec(value, d + 1, "binary")), d, "half_up")


def transcription(rows, built, values):
    num_m, bold_m, dbl, n = [], [], [], 0
    for (_, sec, keys, printed), mine, vals in zip(rows, built, values):
        if len(printed) != len(mine):
            num_m.append({"row": keys, "section": sec, "printed": printed, "mine": mine, "why": "numero de celdas"})
            continue
        for j, (a, b) in enumerate(zip(printed, mine)):
            n += 1
            (ba, sa), (bb, sb) = norm(a), norm(b)
            if sa != sb:
                rec = {"row": keys, "section": sec, "col": j, "printed": a, "mine": b}
                if vals is not None and vals[j] is not None and double_rounding(a, vals[j]):
                    dbl.append(dict(rec, value=vals[j]))
                else:
                    num_m.append(rec)
            elif ba != bb:
                bold_m.append({"row": keys, "section": sec, "col": j, "printed": a, "mine": b})
    return {"cells_compared": n, "number_mismatches": num_m, "double_rounding_in_v13": dbl,
            "bold_mismatches_in_v13": bold_m, "passes": not num_m and len(rows) == len(built)}


def gate_diff(new, old, scale):
    best = None
    for k in new:
        d = (new[k] - old[k]) * scale(k)
        if best is None or abs(d) > abs(best[1]):
            best = (k, d)
    return {"max_abs": abs(best[1]), "signed": best[1], "cell": best[0], "cells": len(new),
            "by_cell": {k: {"theta0": new[k], "v13": old[k], "diff": (new[k] - old[k]) * scale(k)} for k in new}}


def pp_scale(k):
    return C.PP


def unit_scale(k):
    return 1.0


def main():
    v = V13(C.MANUSCRIPT)
    tables = {}

    def add(label, nkey, build_new, build_old, scale, units, sources, subs=()):
        fname, tab = v.tabular(label)
        chunks, rows = data_rows(tab, nkey)
        trials = {}
        for mode in MODES:
            ROUNDING["mode"] = mode
            VALUES.clear()
            old, g_old = build_old(rows)[:2]
            trials[mode] = (transcription(rows, old, list(VALUES)), old, g_old)
        mode = min(MODES, key=lambda m: (len(trials[m][0]["number_mismatches"]) + len(trials[m][0]["double_rounding_in_v13"]),
                                         MODES.index(m)))
        ROUNDING["mode"] = mode
        tr, old, g_old = trials[mode]
        new, g_new = build_new(rows)[:2]
        tex = rebuild(chunks, rows, new, subs)
        path = os.path.join(C.TABLES, "tab_%s_audit13.tex" % label)
        C.write_text(path, "%% Generado por experiments/audit13_tables.py desde %s (no editar a mano)\n%s\n"
                     % (", ".join(sources), tex), __file__)
        tables[label] = {"v13_file": fname, "rows": [{"section": s, "keys": k, "theta0": a, "v13": b}
                                                     for (_, s, k, _), a, b in zip(rows, new, old)],
                         "rounding": mode, "transcription_v13": tr,
                         "gate": dict(gate_diff(g_new, g_old, scale), units=units),
                         "sources": list(sources), "tex": C.rel(path), "tex_sha256": C.sha256_file(path),
                         "header_substitutions": [list(s) for s in subs]}

    s_new, s_old = size_sources()
    add("size", 1, lambda r: build_size(r, s_new), lambda r: build_size(r, s_old), pp_scale, "pp",
        ("e_size_audit13.json", "b101_theta_audit10.json", "b103_lown_audit10.json"))
    cal = C.read_json("e_calib_audit13.json")["cases_by_theta"]
    add("calib", 1, lambda r: build_calib(r, cal[C.PRIM]), lambda r: build_calib(r, cal[C.PRIM_V13]),
        lambda k: 1.0 if k.endswith("|q") else C.PP, "q: unidades del estadistico; tamanos: pp", ("e_calib_audit13.json",))
    add("localpower", 1, lambda r: build_localpower(r, C.PRIM, C.PRIM_V13), lambda r: build_localpower(r, C.PRIM_V13, C.PRIM),
        pp_scale, "pp", ("b92_theta_audit9.json",), subs=(("$\\theta = 0$", "$\\theta = %g$" % C.THETA_V13),))
    eq0 = C.read_json("e_equalized_audit13.json")["cells"]
    eq2 = C.read_json("b103_equalized_audit10.json")["cells"]
    add("dgp1", 2, lambda r: build_power(r, eq0, C.PRIM, "dgp1"), lambda r: build_power(r, eq2, C.PRIM_V13, "dgp1"),
        pp_scale, "pp", ("e_equalized_audit13.json", "b103_equalized_audit10.json"))
    add("ctpower", 2, lambda r: build_power(r, eq0, C.PRIM, "ct_power"), lambda r: build_power(r, eq2, C.PRIM_V13, "ct_power"),
        pp_scale, "pp", ("e_equalized_audit13.json", "b103_equalized_audit10.json"))
    add("dgp2", 2, lambda r: build_dgp2(r, eq0, C.PRIM), lambda r: build_dgp2(r, eq2, C.PRIM_V13), pp_scale, "pp",
        ("e_equalized_audit13.json", "b103_equalized_audit10.json"),
        subs=(("($\\theta = %g$)" % C.THETA_V13, "($\\theta = %g$)" % C.THETA),))
    add("dgp3", 2, lambda r: build_dgp3(r, eq0, C.PRIM), lambda r: build_dgp3(r, eq2, C.PRIM_V13), pp_scale, "pp",
        ("e_equalized_audit13.json", "b103_equalized_audit10.json"))
    add("misspec", 2, lambda r: build_misspec(r, C.PRIM), lambda r: build_misspec(r, C.PRIM_V13), pp_scale, "pp",
        ("b92_theta_audit9.json",))
    fname, tab = v.tabular("misspec")
    _, mrows = data_rows(tab, 2)
    tables["misspec"]["mean_shift"] = {"theta0": build_misspec(mrows, C.PRIM)[2], "v13": build_misspec(mrows, C.PRIM_V13)[2]}
    add("critB", 1, lambda r: build_critb(r, C.THETA), lambda r: build_critb(r, C.THETA_V13), unit_scale,
        "unidades del estadistico", ("b103_cv_audit10.json",))
    cvt = C.read_json("b103_cv_audit10.json")["table"]
    tables["critB"]["max_bootstrap_se"] = {"%g" % t: max(e["max_se"] for e in cvt.values() if e["theta"] == t)
                                          for t in (C.THETA, C.THETA_V13)}
    if C.have("e_awb_audit13.json"):
        aw0 = C.read_json("e_awb_audit13.json")["cells"]
        aw2 = C.read_json("b103_awb_audit10.json")["cells"]
        add("awb", 2, lambda r: build_awb(r, aw0), lambda r: build_awb(r, aw2), pp_scale, "pp",
            ("e_awb_audit13.json", "b103_awb_audit10.json"))
    if C.have("e_dgp5_audit13.json"):
        d5 = C.read_json("e_dgp5_audit13.json")
        d52 = C.read_json("b103_dgp5_audit10.json")["cells"]
        add("dgp5", 2, lambda r: build_dgp5(r, d5["cells"]), lambda r: build_dgp5(r, d52), pp_scale, "pp",
            ("e_dgp5_audit13.json", "b103_dgp5_audit10.json"))
    if C.have("e_application_audit13.json"):
        ap = C.read_json("e_application_audit13.json")
        a10 = C.read_json("b103_application_audit10.json")
        add("fp", 1, lambda r: build_fp(r, ap["summary"], ap["matched_rate"], {}),
            lambda r: build_fp(r, a10["summary"], a10["matched_rate"], {}),
            lambda k: C.PP if k.endswith(("fp_mean", "fp_max")) else 1.0,
            "FP: pp; detecciones y episodios: numero; latencias: dias",
            ("e_application_audit13.json", "b103_application_audit10.json"))
    out = {"provenance": C.provenance(__file__, seed_family=None),
           "manuscript": {"path": os.path.basename(C.MANUSCRIPT), "sha256": C.sha256_file(C.MANUSCRIPT)},
           "theta": C.THETA, "reference_theta": C.THETA_V13, "reading": "protocol_audit13.md, lecturas 2, 5, 13 y 15",
           "tables": tables,
           "transcription_all_pass": all(t["transcription_v13"]["passes"] for t in tables.values())}
    C.write_result(OUT, out, __file__)
    for k, t in tables.items():
        tr = t["transcription_v13"]
        print("%-10s %s transcripcion %s (%d celdas; numero %d, doble redondeo %d, negrita %d)  compuerta %.4f %s en %s" % (
            k, t["rounding"], tr["passes"], tr["cells_compared"], len(tr["number_mismatches"]),
            len(tr["double_rounding_in_v13"]), len(tr["bold_mismatches_in_v13"]), t["gate"]["max_abs"], t["gate"]["units"],
            t["gate"]["cell"]))
        for m in tr["number_mismatches"][:6] + tr["double_rounding_in_v13"] + tr["bold_mismatches_in_v13"]:
            print("    ", m)
    return 0 if out["transcription_all_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
