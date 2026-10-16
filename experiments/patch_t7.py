import re
import sys

def patch_rdv():
    with open('experiments/real_data_validation.py', 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Add run_dfgls
    dfgls_func = """def run_dfgls(window):
    from arch.unitroot import DFGLS
    try:
        return DFGLS(window, trend='c').pvalue
    except:
        return 1.0
"""
    if "def run_dfgls" not in c:
        c = c.replace("def run_kpss(window):", dfgls_func + "\ndef run_kpss(window):")

    # 2. Add p_dfgls to lists
    c = c.replace("p_adf = []\n    p_pp = []\n    p_kpss = []", "p_adf = []\n    p_pp = []\n    p_kpss = []\n    p_dfgls = []")
    
    # 3. Add to loops
    c = c.replace("p_adf.append(run_adf(window))\n        p_pp.append(run_pp(window))\n        p_kpss.append(run_kpss(window))", "p_adf.append(run_adf(window))\n        p_pp.append(run_pp(window))\n        p_kpss.append(run_kpss(window))\n        p_dfgls.append(run_dfgls(window))")

    # 4. Add to result dict
    c = c.replace("'p_kpss': p_kpss,", "'p_kpss': p_kpss,\n        'p_dfgls': p_dfgls,")

    # 5. Add to save format logic
    c = c.replace("    kpss_fp =", "    dfgls_fp = compute_false_positive_rate(res, '2016-01-01', '2018-12-31')\n    kpss_fp =")
    c = c.replace("            fmt_fp(pp_fp),\n            fmt_fp(kpss_fp)", "            fmt_fp(pp_fp),\n            fmt_fp(dfgls_fp),\n            fmt_fp(kpss_fp)")

    # 6. Pass pilot down: full_pipeline is used?
    # Where does it call the test?
    # "res = stationarity_test(window)"
    # No, it uses adaptive test!
    # "stat = np.sqrt((1.0 - r_hat)**2 * g1**2 + r_hat**2 * g2**2)"
    # Let's check how it runs our test:
    # "res = compute_statistic(window, theta=(0.1,0.1), R=0.5)"
    # We will inject andrews_pilot
    c = re.sub(r'res = compute_statistic\(window, (.*?)\)', r'res = compute_statistic(window, \1, andrews_pilot=PILOT)', c)

    # 7. Add PILOT global and N_CAL
    # Actually wait, `real_data_validation.py` builds the adaptive cdf.
    # `cdf_adaptive = build_null_cdf_adaptive(theta=(0.1, 0.1), n=D, N_cal=10000, seed=42)`
    c = re.sub(r'build_null_cdf_adaptive\((.*?)N_cal=10000(.*?)\)', r'build_null_cdf_adaptive(\1N_cal=N_CAL\2)', c)
    c = re.sub(r'build_null_cdf_adaptive\((.*?)N_cal=N_CAL(.*?), seed=42\)', r'build_null_cdf_adaptive(\1N_cal=N_CAL\2, seed=42, andrews_pilot=PILOT)', c)

    with open('experiments/real_data_validation.py', 'w', encoding='utf-8') as f:
        f.write(c)

patch_rdv()
