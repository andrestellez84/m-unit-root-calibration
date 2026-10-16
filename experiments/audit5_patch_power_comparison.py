import re

def patch_power_comparison():
    with open('experiments/power_comparison.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Modify _compute_our_stat
    content = re.sub(
        r'def _compute_our_stat\(Y, theta, R, cdf_func=None\):',
        r'def _compute_our_stat(Y, theta, R, cdf_func=None, andrews_pilot="alpha1"):',
        content
    )
    content = re.sub(
        r's2 = hac_newey_west\(diffs\)',
        r's2 = hac_newey_west(diffs, andrews_pilot=andrews_pilot)',
        content
    )

    # 2. Add pilot argument to run_* functions
    for func in ['run_size_verification', 'run_dgp1', 'run_dgp2', 'run_dgp3', 'run_dgp4']:
        content = re.sub(
            f'def {func}\(cdf_cache=None\):',
            f'def {func}(cdf_cache=None, pilot="alpha1"):',
            content
        )
        content = re.sub(
            f'def {func}\(\):',
            f'def {func}(pilot="alpha1"):',
            content
        )

    # Pass pilot to _compute_our_stat inside the loops
    content = re.sub(
        r'stat, p_val = _compute_our_stat\(Y, theta_fixed, R, cdf\)',
        r'stat, p_val = _compute_our_stat(Y, theta_fixed, R, cdf, andrews_pilot=pilot)',
        content
    )

    # We also need to fix stage argument parsing
    main_pattern = r"stage = 'ALL'\n\s*if len\(sys\.argv\) > 1:\n\s*stage = sys\.argv\[1\]\.upper\(\)"
    new_main = """stage = 'ALL'
    pilot = 'alpha1'
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if arg.startswith('--pilot='):
                pilot = arg.split('=')[1]
            elif not arg.startswith('--'):
                stage = arg.upper()"""
    content = re.sub(main_pattern, new_main, content)

    # Pass pilot to the functions inside __main__
    for func in ['run_size_verification', 'run_dgp1', 'run_dgp2', 'run_dgp3', 'run_dgp4']:
        content = re.sub(
            f"{func}\(cdf_cache\)",
            f"{func}(cdf_cache, pilot=pilot)",
            content
        )
        content = re.sub(
            f"{func}\(\)",
            f"{func}(pilot=pilot)",
            content
        )

    # In Tarea 1, we also need to fix the size check:
    content = re.sub(
        r'print\(f"  Acceptance interval: \[\{0\.035:\.3f\}, \{0\.065:\.3f\}\]"\)',
        r'import scipy.stats as st; lb=st.binom.ppf(0.025, 5000, 0.05)/5000; ub=st.binom.ppf(0.975, 5000, 0.05)/5000; print(f"  Acceptance interval: [{lb:.4f}, {ub:.4f}]")',
        content
    )
    content = re.sub(
        r'return "PASS" if 0\.035 <= val <= 0\.065 else "FAIL"',
        r'return "PASS" if lb <= val <= ub else "FAIL"',
        content
    )

    with open('experiments/power_comparison.py', 'w', encoding='utf-8') as f:
        f.write(content)

patch_power_comparison()
