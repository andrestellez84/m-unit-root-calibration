import sys, os
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("src"))

import json
from joblib import Parallel, delayed

from experiments.audit5_tarea3 import main as run_t3
from experiments.audit5_tarea4 import run_dgp34_both_pilots as run_t4
from experiments.audit5_tarea5 import run_t5

from experiments.audit5_tarea6 import run_t6

def main():
    print("Running Tarea 3...")
    # run_t3() # I will run this separately due to length
    
    print("Running Tarea 4...")
    run_t4()
    
    print("Running Tarea 5...")
    run_t5()

    print("Running Tarea 6...")
    run_t6()

if __name__ == "__main__":
    main()
