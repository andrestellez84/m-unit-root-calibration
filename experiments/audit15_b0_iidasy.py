"""
Auditoria A15 - B15.0: comparacion iid / asintotico desde bA_ma_audit12.json, sin simulacion
(protocol_audit15.md, lecturas 0.1 a 0.4).

Verifica el sha256 de bA_ma_audit12.json contra manifest_audit12.json. Para las 36 celdas y
msb, mzt, msb_pq, mzt_pq y dfgls: (a) celdas con iid > asy; (b) media y maximo de |rate - 0.05|
sobre las 30 celdas con psi != 0 por procedimiento, caso y bloque; (c) conteo "mas cerca de 0.05"
por grupo x caso; (d) rangos de iid - asy por caso. Guarda ademas, por procedimiento, bloque,
caso y grupo, el rango de las tasas (magnitudes a las que puede referirse un literal del parche
T3, lectura 0.4).

Salida: experiments/results/b0_iidasy_audit15.json.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit15_common as C                                         # noqa: E402

OUT = os.path.join(C.RESULTS, "b0_iidasy_audit15.json")
SRC = "bA_ma_audit12.json"
PROCS = ("msb", "mzt", "msb_pq", "mzt_pq", "dfgls")
CASES = ("c", "ct")
BLOCKS = ("iid", "asy")
IID_ERR = "ma_0"
GROUPS = {"psi_m0p8": ("ma_m0p8",), "m0p5": ("ma_m0p5", "ar_m0p5"), "psi_0": ("ma_0",), "p0p5": ("ma_0p5", "ar_0p5")}


def summary(v):
    return {"mean": sum(v) / len(v), "max": max(v), "min": min(v), "n": len(v)}


def main():
    man = C.read_json("manifest_audit12.json")["entries"]["experiments/results/" + SRC]
    disk = C.sha256_file(os.path.join(C.RESULTS, SRC))
    check = {"sha256_manifest": man["sha256"], "sha256_disk": disk, "matches": man["sha256"] == disk}
    if not check["matches"]:
        out = {"provenance": C.provenance(__file__), "sha_check": check, "stopped": True}
        C.write_result(OUT, out, __file__)
        print("sha256 no coincide; B15.0 se detiene")
        return 1
    d = C.read_json(SRC)
    cells = d["size"]
    region = d["exact_region_20000"]
    a, b, cc, dd, ranges = {}, {}, {}, {}, {}
    for p in PROCS:
        diffs = {k: cells[k]["iid"][p]["rate"] - cells[k]["asy"][p]["rate"] for k in cells}
        a[p] = {"iid_gt_asy": sum(1 for x in diffs.values() if x > 0), "equal": sum(1 for x in diffs.values() if x == 0),
                "iid_lt_asy": sum(1 for x in diffs.values() if x < 0), "cells": len(diffs)}
        b[p], cc[p], dd[p], ranges[p] = {}, {}, {}, {}
        for case in CASES:
            nz = [k for k, c in cells.items() if c["case"] == case and c["err_tag"] != IID_ERR]
            b[p][case] = {blk: summary([abs(cells[k][blk][p]["rate"] - C.ALPHA) for k in nz]) for blk in BLOCKS}
            ks = [k for k, c in cells.items() if c["case"] == case]
            dv = [diffs[k] for k in ks]
            dd[p][case] = {"min": min(dv), "max": max(dv), "argmin": min(ks, key=lambda k: diffs[k]),
                           "argmax": max(ks, key=lambda k: diffs[k])}
            cc[p][case], ranges[p][case] = {}, {}
            for g, tags in GROUPS.items():
                gk = [k for k in ks if cells[k]["err_tag"] in tags]
                di = {k: abs(cells[k]["iid"][p]["rate"] - C.ALPHA) for k in gk}
                da = {k: abs(cells[k]["asy"][p]["rate"] - C.ALPHA) for k in gk}
                cc[p][case][g] = {"iid_closer": sum(1 for k in gk if di[k] < da[k]), "asy_closer": sum(1 for k in gk if di[k] > da[k]),
                                  "tie": sum(1 for k in gk if di[k] == da[k]), "cells": len(gk)}
                ranges[p][case][g] = {blk: {"min": min(cells[k][blk][p]["rate"] for k in gk),
                                            "max": max(cells[k][blk][p]["rate"] for k in gk)} for blk in BLOCKS}
        both = [k for k, c in cells.items() if c["err_tag"] != IID_ERR]
        b[p]["both"] = {blk: summary([abs(cells[k][blk][p]["rate"] - C.ALPHA) for k in both]) for blk in BLOCKS}
    rows = []
    for k, c in cells.items():
        rows.append({"cell": k, "err_tag": c["err_tag"], "n": c["n"], "case": c["case"],
                     "rates": {p: {blk: c[blk][p]["rate"] for blk in BLOCKS} for p in PROCS},
                     "in_region": {p: {blk: c[blk][p]["in_region"] for blk in BLOCKS} for p in PROCS},
                     "N": c["iid"]["msb"]["n"]})
    out = {"provenance": C.provenance(__file__), "reading": "protocol_audit15.md, lecturas 0.1 a 0.4", "source": SRC,
           "sha_check": check, "procs": list(PROCS), "groups": {g: list(t) for g, t in GROUPS.items()}, "exact_region_20000": region,
           "n_cells": len(cells), "n_cells_psi_nonzero": sum(1 for c in cells.values() if c["err_tag"] != IID_ERR),
           "a_iid_gt_asy": a, "b_abs_dev": b, "c_closer": cc, "d_diff_range": dd, "group_ranges": ranges, "cells": rows}
    C.write_result(OUT, out, __file__)
    print("sha256:", check["matches"], "celdas", out["n_cells"], "psi != 0", out["n_cells_psi_nonzero"])
    for p in PROCS:
        print(p, "(a)", a[p], "| (b)", {case: {blk: "%.4f/%.4f" % (b[p][case][blk]["mean"], b[p][case][blk]["max"]) for blk in BLOCKS}
                                          for case in ("c", "ct", "both")},
              "| (d)", {case: "%.4f..%.4f" % (dd[p][case]["min"], dd[p][case]["max"]) for case in CASES})
    return 0


if __name__ == "__main__":
    sys.exit(main())
