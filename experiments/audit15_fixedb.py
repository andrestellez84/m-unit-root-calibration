"""
Auditoria A15 - B15.3: MSB-B con Bartlett de ancho fijo (protocol_audit15.md, lecturas 3.1-3.3;
enmienda 2, seccion 4).

sigma2 = gamma_0 + 2 sum_{j=1}^{B} (1 - j/(B + 1)) gamma_j sobre las primeras diferencias
centradas con la media completa, gamma_j con divisor n (hac_estimator.hac_newey_west con
bandwidth = B), autocovarianzas por FFT con relleno de ceros a >= 2n; piso 1e-12 como la libreria.
Configuraciones: b in {0.1, 0.3, 1.0} con B = min(ceil(b n), n - 1) y la regla de LLSW (2018, ec.
(3) y nota 3) S = ceil(1.3 n^{1/2}), B = S - 1. MSB-B = audit9_engine.rmgls(y, n, 0, sigma2, caso).
"""
import math

import numpy as np

B_FRACTIONS = (0.1, 0.3, 1.0)
LLSW_CONST = 1.3                   # Lazarus-Lewis-Stock-Watson (2018), ec. (3)
FLOOR = 10 ** -12                  # piso de hac_newey_west


def configs():
    return [("b=%g" % b, b) for b in B_FRACTIONS] + [("LLSW", None)]


def bandwidth(n, b):
    """n = numero de primeras diferencias."""
    if b is None:
        return int(math.ceil(LLSW_CONST * math.sqrt(n))) - 1
    return min(int(math.ceil(b * n)), n - 1)


def autocov_fft(y):
    x = np.diff(np.asarray(y, dtype=np.float64))
    n = x.shape[0]
    xc = x - np.mean(x)
    m = 1 << int(math.ceil(math.log2(2 * n)))
    f = np.fft.rfft(xc, m)
    g = np.fft.irfft(f * np.conj(f), m)[:n] / n
    return g


def s2_from_autocov(g, B):
    n = g.shape[0]
    B = max(0, min(B, n - 1))
    if g[0] < 10 ** -15:
        return FLOOR
    j = np.arange(1, B + 1)
    s = g[0] + 2.0 * np.sum((1.0 - j / (B + 1.0)) * g[1:B + 1])
    return max(float(s), FLOOR)


def s2_all(y):
    """sigma2 por FFT para las cuatro configuraciones: {nombre: (B, sigma2)}."""
    g = autocov_fft(y)
    n = g.shape[0]
    return {name: (bandwidth(n, b), s2_from_autocov(g, bandwidth(n, b))) for name, b in configs()}
