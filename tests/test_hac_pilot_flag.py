import pytest
import numpy as np
from stationarity_test.hac_estimator import hac_newey_west

def test_hac_pilot_flag_behavior():
    rng = np.random.default_rng(12345)
    n = 1000
    rho = 0.5
    eps = rng.standard_normal(n)
    Y = np.zeros(n)
    Y[0] = eps[0]
    for t in range(1, n):
        Y[t] = rho * Y[t-1] + eps[t]
        
    diffs = np.diff(np.concatenate(([0], Y)))
    
    s2_1 = hac_newey_west(diffs, andrews_pilot="alpha1")
    s2_2 = hac_newey_west(diffs, andrews_pilot="alpha2")
    
    # We know that for AR(0.5), pilot alpha2 gives smaller B than alpha1
    # B = 6 vs B = 8, so s2 will be different. 
    # With AR(0.5), B alpha2 < B alpha1
    assert s2_1 != s2_2

def test_hac_pilot_flag_invalid():
    rng = np.random.default_rng(123)
    x = rng.standard_normal(100)
    with pytest.raises(ValueError, match="alpha1' or 'alpha2'"):
        hac_newey_west(x, andrews_pilot="basura")
