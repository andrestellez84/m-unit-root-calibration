"""
Auditoria A13 - B13.Q, Q5: valores criticos simulados de MSB-GLS y MZ_t-GLS prometidos por la
App. B del v14 (protocol_audit13_amend1.md, lectura 7).

Solo lee lo existente; no calcula ningun cuantil. Para n in {100, 200, 500, 1000}, casos c y
ct, niveles 1 %, 2.5 %, 5 % y 10 %, y los procedimientos msb y mzt, busca el valor critico
simulado con N_cal = 500 000 en los JSON que los guardan:
  - b101_theta_audit10.json: cells.<dm|ct>|<n>.sim_thresholds (n in {200, 500, 1000});
  - bA_ma_audit12.json: config.iid_quantiles.<n>|<caso> (n in {100, 200, 500});
y registra, sin cargar filas, si las muestras de calibracion de A10 (audit10_cal/cal_n<n>.npz)
contienen las columnas y cuantas filas tienen. Lo que falta va a "No ejecutado".

Salida: experiments/results/q_supplement_audit13.json.
"""
import os
import sys
import zipfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit13_common as C                                         # noqa: E402
import audit10_engine as E10                                       # noqa: E402

OUT = os.path.join(C.RESULTS, "q_supplement_audit13.json")
NS = (100, 200, 500, 1000)
CASES = {"c": "dm", "ct": "ct"}
LEVELS = ("0.01", "0.025", "0.05", "0.1")
PROCS = ("msb", "mzt")


def npz_header(path):
    """Forma de 'rows' y lista de columnas sin cargar las filas."""
    with zipfile.ZipFile(path) as z:
        with z.open("rows.npy") as f:
            version = np.lib.format.read_magic(f)
            shape, _, _ = np.lib.format._read_array_header(f, version)
    with np.load(path) as zz:
        cols = [str(c) for c in zz["cols"]]
    return shape, cols


def main():
    b101 = C.read_json("b101_theta_audit10.json")
    bA = C.read_json("bA_ma_audit12.json")
    found = {}
    for n in NS:
        for case, lab in CASES.items():
            for p in PROCS:
                for lev in LEVELS:
                    key = "%s|%d|%s|%s" % (case, n, p, lev)
                    srcs = []
                    if lev == "0.05":
                        c = b101["cells"].get("%s|%d" % (lab, n))
                        if c is not None and p in c["sim_thresholds"]:
                            srcs.append({"json": "b101_theta_audit10.json", "path": "cells.%s|%d.sim_thresholds.%s" % (lab, n, p),
                                         "value": c["sim_thresholds"][p], "N_cal": b101["config"]["N_cal"]})
                        q = bA["config"]["iid_quantiles"].get("%d|%s" % (n, case))
                        if q is not None and p in q:
                            srcs.append({"json": "bA_ma_audit12.json", "path": "config.iid_quantiles.%d|%s.%s" % (n, case, p),
                                         "value": q[p], "N_cal": bA["config"]["N_cal_finite"]["%d|%s" % (n, case)][p]})
                    found[key] = {"case": case, "n": n, "proc": p, "level": lev, "sources": srcs,
                                  "exists_with_N_cal_500000": any(s["N_cal"] == E10.N_CAL for s in srcs),
                                  "sources_agree": len({s["value"] for s in srcs}) <= 1}
    samples = {}
    for n in NS:
        path = os.path.join(E10.CKPT_CAL, "cal_n%d.npz" % n)
        shape, cols = npz_header(path)
        samples[str(n)] = {"path": C.rel(path), "rows": int(shape[0]),
                           "has_columns": {"%s|%s" % (case, p): "%s|%s" % (case, p) in cols for case in CASES for p in PROCS}}
    missing = sorted(k for k, v in found.items() if not v["exists_with_N_cal_500000"])
    out = {"provenance": C.provenance(__file__, seed_family=None), "reading": "protocol_audit13_amend1.md, lectura 7",
           "n": list(NS), "levels": list(LEVELS), "procs": list(PROCS), "found": found, "calibration_samples": samples,
           "missing": missing, "present": sorted(k for k in found if k not in missing)}
    C.write_result(OUT, out, __file__)
    print("presentes:", len(out["present"]), "faltan:", len(missing))
    for k in out["present"]:
        print("  ", k, [(s["json"], round(s["value"], 4), s["N_cal"]) for s in found[k]["sources"]], found[k]["sources_agree"])
    print("muestras:", samples)
    return 0


if __name__ == "__main__":
    sys.exit(main())
