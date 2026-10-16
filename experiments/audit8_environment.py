"""
Auditoria A8 - entorno de ejecucion (versiones, hardware, commits de inicio).

Salida: experiments/results/environment_audit8.json.
Uso: python experiments/audit8_environment.py
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit8_common as C                                          # noqa: E402
from audit7_environment import ps_json                             # noqa: E402
from audit6_wild_bootstrap_sweep import find_rscript               # noqa: E402

OUT = os.path.join(C.RESULTS, "environment_audit8.json")
PROTOCOL = "experiments/protocol_audit8.md"


def main():
    rscript = find_rscript()
    rv = subprocess.run([rscript, "--version"], capture_output=True, text=True)
    bootur = subprocess.run([rscript, "-e", 'cat(as.character(packageVersion("bootUR")))'],
                            capture_output=True, text=True).stdout.strip()
    reg = C.git("log", "--diff-filter=A", "--format=%H", "--", PROTOCOL).splitlines()[-1]
    env = {
        "provenance": C.provenance(__file__),
        "versions": C.versions(),
        "r": (rv.stdout + rv.stderr).strip().splitlines()[0],
        "bootUR": bootur,
        "cpu": ps_json("Get-CimInstance Win32_Processor | Select-Object Name,NumberOfCores,NumberOfLogicalProcessors"),
        "memory_bytes": ps_json("Get-CimInstance Win32_ComputerSystem | Select-Object TotalPhysicalMemory"),
        "git": {"protocol_commit": reg, "start_commit": C.git("rev-parse", reg + "^"),
                "protocol_sha256_committed": C.git_blob_sha256(PROTOCOL, reg)},
    }
    C.write_result(OUT, env, __file__)
    print(env["versions"], env["r"], env["bootUR"], env["cpu"], env["git"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
