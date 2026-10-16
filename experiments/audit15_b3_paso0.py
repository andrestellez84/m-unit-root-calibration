"""
Auditoria A15 - B15.3, Paso 0 (compuerta numerica; protocol_audit15.md, lectura 3.1): sigma2
de Bartlett por FFT frente a la suma directa de hac_estimator.hac_newey_west(bandwidth = B), en
las 100 primeras series de calibracion de la familia 155 con n = 200, para las cuatro
configuraciones (b = 0.1, 0.3, 1.0 y LLSW) y para el ancho de Andrews (frente a hac_sigma_sq).
Criterio: |D| relativo a sigma2 <= 1e-12.

Salida: experiments/results/b3_paso0_audit15.json.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit15_common as C                                         # noqa: E402
import audit15_design as D                                         # noqa: E402
import audit15_fixedb as FB                                        # noqa: E402
import audit12_unitroot as P12                                     # noqa: E402
from stationarity_test.hac_estimator import hac_newey_west          # noqa: E402
from stationarity_test.rm_core import hac_sigma_sq                  # noqa: E402

OUT = os.path.join(C.RESULTS, "b3_paso0_audit15.json")
FAM = C.FAMILY["CAL3"]
N = 200
SERIES = 100
TOL = 10 ** -12


def main():
    cell = D.cell_index(FAM, "cal3_n%d" % N)
    worst = {name: 0.0 for name, _ in FB.configs()}
    worst["andrews"] = 0.0
    bws = {}
    for i in range(SERIES):
        y = P12.null_path(("ma", 0.0), N, C.rep_rng(FAM, cell, i))
        x = np.diff(y)
        g = FB.autocov_fft(y)
        for name, (B, s2) in FB.s2_all(y).items():
            ref = hac_newey_west(x, bandwidth=B)
            worst[name] = max(worst[name], abs(s2 - ref) / ref)
            bws[name] = B
        Ba = P12.andrews_bandwidth(y)
        s2a = FB.s2_from_autocov(g, Ba)
        ref = hac_sigma_sq(y)
        worst["andrews"] = max(worst["andrews"], abs(s2a - ref) / ref)
    out = {"provenance": C.provenance(__file__, seed_family=FAM), "reading": "protocol_audit15.md, lectura 3.1",
           "llsw_rule": {"source": "Lazarus, Lewis, Stock y Watson (2018), JBES 36(4)", "equation": "(3), p. 542",
                         "rounding": "nota 3, p. 542: redondear S hacia arriba", "table": "Tabla 1, fila 2, p. 543",
                         "kernel": "ec. (6), p. 543: k(v) = (1 - |v|) 1(|v| <= 1), v = j/S",
                         "rule": "S = ceil(1.3 T^(1/2)); B = S - 1 con pesos 1 - j/(B + 1)"},
           "n": N, "series": SERIES, "bandwidths_n200": bws, "max_rel_diff": worst, "tolerance": TOL,
           "passes": all(v <= TOL for v in worst.values())}
    C.write_result(OUT, out, __file__)
    print("anchos:", bws)
    print("max |D| relativo:", worst, "pasa:", out["passes"])
    return 0 if out["passes"] else 1


if __name__ == "__main__":
    sys.exit(main())
