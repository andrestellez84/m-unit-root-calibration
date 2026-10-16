"""
Permanent regression test for Andrews pilot propagation.
Verifies that andrews_pilot ('alpha1' vs 'alpha2') propagates correctly
through the pipeline and changes the bandwidth/standardization on AR(0.5), n=1000.
"""

import os
import sys
import pytest
import numpy as np

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("src"))

from stationarity_test.statistic import compute_statistic
from stationarity_test.hac_estimator import hac_newey_west
from experiments.power_comparison import (
    run_our_test,
    run_experiment_cell,
    run_dgp4,
    generate_ar1,
    THETA_FIXED,
    R_CONFIGS,
)
import experiments.power_comparison as pc


def test_compute_statistic_pilot_propagation():
    """Verify compute_statistic changes g1_std and g2_std on AR(0.5) n=1000."""
    rng = np.random.default_rng(12345)
    n = 1000
    rho = 0.5
    g1_a1, g1_a2 = [], []
    g2_a1, g2_a2 = [], []

    for _ in range(200):
        eps = rng.standard_normal(n + 1)
        Y = np.zeros(n + 1)
        for t in range(1, n + 1):
            Y[t] = rho * Y[t - 1] + eps[t]

        r1 = compute_statistic(Y, (0.1, 0.1), R=0.5, andrews_pilot="alpha1")
        r2 = compute_statistic(Y, (0.1, 0.1), R=0.5, andrews_pilot="alpha2")
        g1_a1.append(r1["g1_std"])
        g1_a2.append(r2["g1_std"])
        g2_a1.append(r1["g2_std"])
        g2_a2.append(r2["g2_std"])

    m1_a1 = float(np.mean(g1_a1))
    m1_a2 = float(np.mean(g1_a2))
    m2_a1 = float(np.mean(g2_a1))
    m2_a2 = float(np.mean(g2_a2))

    diff1 = (m1_a1 - m1_a2) / m1_a2
    diff2 = (m2_a1 - m2_a2) / m2_a2

    print(f"\n[compute_statistic] E[g1]: a1={m1_a1:.5f}, a2={m1_a2:.5f}, diff={diff1 * 100:.2f}%")
    print(f"[compute_statistic] E[g2]: a1={m2_a1:.5f}, a2={m2_a2:.5f}, diff={diff2 * 100:.2f}%")

    assert diff1 >= 0.10, f"g1 diff {diff1:.4f} < 0.10"
    assert diff2 >= 0.20, f"g2 diff {diff2:.4f} < 0.20"


def test_run_experiment_cell_pilot_propagation():
    """Verify run_experiment_cell propagates andrews_pilot and reports differing E_g1_std."""
    cdf_cache = {(r_name, 1000): (lambda stat: 0.05) for r_name in R_CONFIGS}

    cell_a1 = run_experiment_cell(
        dgp_func=generate_ar1,
        dgp_kwargs={"rho": 0.5},
        n=1000,
        theta=THETA_FIXED,
        r_configs=R_CONFIGS,
        cdf_cache=cdf_cache,
        N_sim=200,
        seed_base=12345,
        andrews_pilot="alpha1",
    )
    cell_a2 = run_experiment_cell(
        dgp_func=generate_ar1,
        dgp_kwargs={"rho": 0.5},
        n=1000,
        theta=THETA_FIXED,
        r_configs=R_CONFIGS,
        cdf_cache=cdf_cache,
        N_sim=200,
        seed_base=12345,
        andrews_pilot="alpha2",
    )

    diff1 = (cell_a1["E_g1_std"] - cell_a2["E_g1_std"]) / cell_a2["E_g1_std"]
    diff2 = (cell_a1["E_g2_std"] - cell_a2["E_g2_std"]) / cell_a2["E_g2_std"]

    print(f"\n[run_experiment_cell] E[g1]: a1={cell_a1['E_g1_std']:.5f}, a2={cell_a2['E_g1_std']:.5f}, diff={diff1 * 100:.2f}%")
    print(f"[run_experiment_cell] E[g2]: a1={cell_a1['E_g2_std']:.5f}, a2={cell_a2['E_g2_std']:.5f}, diff={diff2 * 100:.2f}%")

    assert diff1 >= 0.10, f"g1 diff {diff1:.4f} < 0.10"
    assert diff2 >= 0.20, f"g2 diff {diff2:.4f} < 0.20"


def test_run_dgp4_pilot_propagation(monkeypatch):
    """Verify run_dgp4 internal HAC call passes pilot and produces differing diagnostics."""
    cdf_cache = {(r_name, 1000): (lambda stat: 0.05) for r_name in R_CONFIGS}

    monkeypatch.setattr(pc, "N_GRID", [1000])
    monkeypatch.setattr(pc, "DGP4_RATIOS", [1.0])
    monkeypatch.setattr(pc, "N_SIM", 200)

    res_a1 = run_dgp4(cdf_cache, pilot="alpha1")
    res_a2 = run_dgp4(cdf_cache, pilot="alpha2")

    cell_a1 = res_a1[1000][1.0]
    cell_a2 = res_a2[1000][1.0]

    diff1 = (cell_a1["E_g1_std"] - cell_a2["E_g1_std"]) / cell_a2["E_g1_std"]
    diff2 = (cell_a1["E_g2_std"] - cell_a2["E_g2_std"]) / cell_a2["E_g2_std"]

    print(f"\n[run_dgp4] E[g1]: a1={cell_a1['E_g1_std']:.5f}, a2={cell_a2['E_g1_std']:.5f}, diff={diff1 * 100:.2f}%")
    print(f"[run_dgp4] E[g2]: a1={cell_a1['E_g2_std']:.5f}, a2={cell_a2['E_g2_std']:.5f}, diff={diff2 * 100:.2f}%")

    assert diff1 >= 0.10, f"g1 diff {diff1:.4f} < 0.10"
    assert diff2 >= 0.20, f"g2 diff {diff2:.4f} < 0.20"


def test_dgp_routines_forward_pilot(monkeypatch):
    """Verify run_dgp1, run_dgp2, run_dgp3 forward the pilot argument to run_experiment_cell."""
    forwarded_pilots = []

    def fake_experiment_cell(*args, **kwargs):
        forwarded_pilots.append(kwargs.get("andrews_pilot"))
        return {
            "ours_R050": 0.05,
            "ours_R025": 0.05,
            "ours_R075": 0.05,
            "adf": 0.05,
            "pp": 0.05,
            "kpss_rej": 0.05,
            "E_g1_std": 0.01,
            "E_g2_std": 0.001,
            "std_g1": 0.001,
            "std_g2": 0.0001,
        }

    monkeypatch.setattr(pc, "run_experiment_cell", fake_experiment_cell)
    monkeypatch.setattr(pc, "N_GRID", [1000])
    monkeypatch.setattr(pc, "DGP1_RHOS", [0.95])
    monkeypatch.setattr(pc, "DGP2_DELTAS", [0.0])
    monkeypatch.setattr(pc, "DGP3_RATIOS", [1.0])

    cdf_cache = {}

    for pilot in ["alpha1", "alpha2"]:
        forwarded_pilots.clear()
        pc.run_dgp1(cdf_cache, pilot=pilot)
        assert forwarded_pilots == [pilot], f"run_dgp1 did not forward {pilot}: got {forwarded_pilots}"

        forwarded_pilots.clear()
        pc.run_dgp2(cdf_cache, pilot=pilot)
        assert forwarded_pilots == [pilot], f"run_dgp2 did not forward {pilot}: got {forwarded_pilots}"

        forwarded_pilots.clear()
        pc.run_dgp3(cdf_cache, pilot=pilot)
        assert forwarded_pilots == [pilot], f"run_dgp3 did not forward {pilot}: got {forwarded_pilots}"

        forwarded_pilots.clear()
        pc.run_size_verification(cdf_cache, pilot=pilot)
        assert forwarded_pilots == [pilot], f"run_size_verification did not forward {pilot}: got {forwarded_pilots}"
