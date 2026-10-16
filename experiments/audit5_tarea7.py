import sys, os
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("src"))

import re
import subprocess
import shutil

def run_t7():
    with open('experiments/real_data_validation.py', 'r', encoding='utf-8') as f:
        orig = f.read()

    # Alpha 1
    if os.path.exists("experiments/results/checkpoints"): shutil.rmtree("experiments/results/checkpoints")
    c = orig.replace('N_CAL = 10000', 'N_CAL = 50000')
    c = c.replace('PILOT = "alpha1"', 'PILOT = "alpha1"')
    with open('experiments/real_data_validation.py', 'w', encoding='utf-8') as f:
        f.write(c)
    print("Running alpha1 N_cal=50000...")
    subprocess.run(["python", "experiments/real_data_validation.py"])
    if os.path.exists("experiments/results/real_data_results.json"):
        shutil.copy("experiments/results/real_data_results.json", "experiments/results/validation_results_audit5_alpha1.json")
    
    # Alpha 2
    if os.path.exists("experiments/results/checkpoints"): shutil.rmtree("experiments/results/checkpoints")
    c = orig.replace('N_CAL = 10000', 'N_CAL = 10000')
    c = c.replace('PILOT = "alpha1"', 'PILOT = "alpha2"')
    with open('experiments/real_data_validation.py', 'w', encoding='utf-8') as f:
        f.write(c)
    print("Running alpha2 N_cal=10000...")
    subprocess.run(["python", "experiments/real_data_validation.py"])
    if os.path.exists("experiments/results/real_data_results.json"):
        shutil.copy("experiments/results/real_data_results.json", "experiments/results/validation_results_audit5_alpha2.json")

    # restore
    with open('experiments/real_data_validation.py', 'w', encoding='utf-8') as f:
        f.write(orig)

if __name__ == "__main__":
    run_t7()
