"""
Auditoria A16 - B16.1 (enmienda 6, lectura E6.1). Solo lee JSON; redondeo binario.

Reutiliza audit15_v17_tables sin modificarlo; no toca tables_audit15/ ni v17_tables_audit15.json.
  a. tab_summary_audit16.tex (+ nota): como la de A15, pero la potencia de la fila 1 (MSB-B con Andrews)
     sale de b3_fixedb_audit15.json power.pw3_rho0p9_n200_c.rates.gls_t0, igual que tab_fixedb.
  b. tab_fixedb_audit16.tex (+ nota): tabular identico al de A15; en la nota, \\cref{tab:serial}
     -> "Table S2.1 of the supplement".
Salida: experiments/results/v17_tables_audit16.json.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit16_common as C                                         # noqa: E402
import audit15_v17_tables as V                                     # noqa: E402

OUT = os.path.join(C.RESULTS, "v17_tables_audit16.json")
SRC_B1, SRC_B3, SRC_A12 = V.SRC_B1, V.SRC_B3, V.SRC_A12
ROW1_POWER = ("b3", "gls_t0")                    # E6.1: fila 1, potencia desde b3 (como tab_fixedb)
SERIAL_REF = "\\cref{tab:serial}"
SERIAL_TXT = "Table S2.1 of the supplement"


def summary_rows(b1, b3, a12):
    sr = V.summary_rows(b1, b3, a12)
    for r, (lab, cv, src, key) in zip(sr, V.SUM_ROWS):
        r["power_audit"] = V.SUM_AUDIT[src]
        r["power_file"] = V.SUM_FILE[src]
    src, key = ROW1_POWER
    pw = b3["power"][V.SUM_POWER[src]]["rates"].get(key)
    r = sr[0]
    r.update({"power": None if pw is None else pw["rate"], "N_power": None if pw is None else pw["n"],
              "power_source": None if pw is None else "%s power.%s.rates.%s" % (SRC_B3, V.SUM_POWER[src], key),
              "power_audit": V.SUM_AUDIT[src], "power_file": SRC_B3})
    return sr


def tab_summary(b1, b3, a12):
    sr = summary_rows(b1, b3, a12)
    rows = [[r["label"], r["cv"], V.f(r["D"], 4), V.f(r["M"], 4), V.f(r["min"], 3), V.f(r["max"], 3),
             "%d/%d" % (r["iid_in_region"], r["iid_cells"]), V.DASH if r["power"] is None else V.f(r["power"], 3)] for r in sr]
    head = ["& & \\multicolumn{5}{c}{Size} & \\\\", "\\cmidrule(lr){3-7}",
            "Test & Critical value & $D$ & $M$ & min & max & iid in region & Power \\\\"]
    groups = [r["label"] for r in sr]
    by_n = {}
    for r in sr:
        by_n.setdefault(r["N_size"], r["region"])
    n_rows, pw_groups = {}, {}
    for i, r in enumerate(sr, 1):
        n_rows.setdefault((r["audit"], r["N_size"]), []).append(i)
        if r["power"] is not None:
            pw_groups.setdefault((r["power_audit"], r["N_power"], r["power_file"]), []).append(i)
    missing = [i for i, r in enumerate(sr, 1) if r["power"] is None]

    def rows_txt(ix):
        return ("row " if len(ix) == 1 else "rows ") + ", ".join("%d" % i for i in ix)
    size_txt = "; ".join("%s: %s, $%d$ paths per cell" % (rows_txt(ix), a, n) for (a, n), ix in n_rows.items())
    reg_txt = "; ".join("$[%s, %s]$ for $%d$ paths" % (V.bound(reg[0]), V.bound(reg[1]), n) for n, reg in sorted(by_n.items(), reverse=True))
    pw_desc = {SRC_A12: "size-adjusted in the null cell with the same errors, $n$ and case",
               SRC_B3: "critical values simulated under iid errors ($%d$ paths per $n$), no further size adjustment" % b3["config"]["N_cal"],
               SRC_B1: "size-adjusted in the null cell with the same errors, $n$ and case"}
    pw_txt = "; ".join("%s: %s, $%d$ paths, %s" % (rows_txt(ix), a, n, pw_desc[s]) for (a, n, s), ix in pw_groups.items())
    note = ("Nominal level $0.05$. $D$ and $M$: mean and maximum of $|\\text{size} - 0.05|$ over the %d cells with serially "
            "correlated errors; min and max over all %d cells; iid in region: cells with iid errors whose rejection rate lies in the "
            "exact binomial region of its number of paths (%s). Size: %s. Power: AR(1) with $\\rho = 0.90$, iid errors, $n = 200$, "
            "constant case; %s. The three power experiments use different paths.%s\n" % (
                sr[0]["cells_psi_nonzero"], sr[0]["cells"], reg_txt, size_txt, pw_txt,
                "" if not missing else " %s: power not measured in this cell (--)." % rows_txt(missing).capitalize()))
    return V.tabular("llcccccc", head, rows, groups), note, sr


def main():
    b1, b3, a12 = C.read_json(SRC_B1), C.read_json(SRC_B3), C.read_json(SRC_A12)
    prov = C.provenance(__file__)
    outs = {}

    def put(name, tex, note, src):
        p = os.path.join(C.TABLES, name + ".tex")
        q = os.path.join(C.TABLES, name.replace("_audit16", "_note_audit16") + ".tex")
        hdr = "% Generado por experiments/audit16_v17_tables.py desde " + src + " (no editar a mano)\n"
        C.write_text(p, hdr + tex, __file__, prov)
        C.write_text(q, hdr + note, __file__, prov)
        outs[C.rel(p)] = C.sha256_file(p)
        outs[C.rel(q)] = C.sha256_file(q)
    t, n, sr = tab_summary(b1, b3, a12)
    put("tab_summary_audit16", t, n, "%s, %s y %s" % (SRC_A12, SRC_B3, SRC_B1))
    t, n, fr = V.tab_fixedb(b3, a12)
    n_refs = n.count(SERIAL_REF)
    put("tab_fixedb_audit16", t, n.replace(SERIAL_REF, SERIAL_TXT), "%s y %s" % (SRC_B3, SRC_A12))
    a15 = {k: C.sha256_file(os.path.join(C15_TABLES(), k)) for k in ("tab_fixedb_audit15.tex", "tab_summary_audit15.tex")}
    same_tab = (open(os.path.join(C15_TABLES(), "tab_fixedb_audit15.tex"), encoding="utf-8").read().split("\n", 1)[1] ==
                open(os.path.join(C.TABLES, "tab_fixedb_audit16.tex"), encoding="utf-8").read().split("\n", 1)[1])
    out = {"provenance": prov, "reading": "enmienda 6, lectura E6.1",
           "sources": {k: C.sha256_file(os.path.join(C.RESULTS, k)) for k in (SRC_B1, SRC_B3, SRC_A12)},
           "outputs": outs, "rounding": "binary", "summary_rows": sr,
           "row1_power": {"value": sr[0]["power"], "source": sr[0]["power_source"],
                          "equals_tab_fixedb_andrews": sr[0]["power"] == fr["andrews"]["power"]["0p9"],
                          "a15_value": V.summary_rows(b1, b3, a12)[0]["power"]},
           "fixedb_note": {"serial_refs_replaced": n_refs, "replacement": SERIAL_TXT,
                           "tabular_identical_to_a15": same_tab},
           "a15_tables_sha256": a15}
    C.write_result(OUT, out, __file__)
    for k, v in outs.items():
        print(k, v)
    print("fila 1:", out["row1_power"], "| nota fixedb:", out["fixedb_note"])
    return 0


def C15_TABLES():
    return V.C.TABLES


if __name__ == "__main__":
    sys.exit(main())
