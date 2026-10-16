import platform
import sys
import numpy as np
import scipy
import pandas as pd
import datetime

def main():
    lines = [
        "## Metadatos de la Ejecución y Trazabilidad",
        "",
        f"- **Fecha de finalización**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "- **Semillas utilizadas**: 42 (Principal, calibración CDF), 999 (KS test), 10000+ (Simulaciones Monte Carlo)",
        "- **Versiones de Software**:",
        f"  - Python: {platform.python_version()}",
        f"  - NumPy: {np.__version__}",
        f"  - SciPy: {scipy.__version__}",
        f"  - Pandas: {pd.__version__}",
        "- **Rutas de los JSONs de Respaldo**: `experiments/results/*.json` (Nuevos), `experiments/results_old_audit4/*.json` (Antiguos antes de corrección)",
        ""
    ]
    with open("experiments/results/resultados_auditoria_4_metadata.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

if __name__ == "__main__":
    main()
