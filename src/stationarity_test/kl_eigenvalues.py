"""
Module F1.A: Karhunen-Loève eigenvalue computation.

Computes the eigenvalues lambda_k^{(i, theta)} of the covariance operator
associated with each functional limit F_i^theta.

Two separate code paths (Decision D2):
    Component 1 — Linear operator on W:
        Kernel K_theta^{(1)}(u, v) = Cov[W_bar_u^theta, W_bar_v^theta]
        where W_bar_u^theta = (1/theta) * int_u^{u+theta} W(s) ds.
        Analytical expression via integration of min(s, s').

    Component 2 — Operator on quadratic process [S_theta(·)]^2:
        Kernel K_theta^{(2)}(u, v) = Cov([S_theta(u)]^2, [S_theta(v)]^2)
        where S_theta(u)^2 = (1/theta) int_u^{u+theta} (W(s) - W_bar_u^theta)^2 ds.
        Computed via Wick's theorem (fourth moment formula for Gaussian):
        E[W(a)W(b)W(c)W(d)] = min(a,b)min(c,d) + min(a,c)min(b,d) + min(a,d)min(b,c)
        
        NOTE: The functional limit of Component 2 is of fourth order. The eigenvalues 
        of K^{(2)} are those of the covariance of S^2(u) and DO NOT define a chi-squared 
        mixture for the limit distribution. Their sum is E[F_2^theta] and serves only 
        as a verification target.

Notation follows the Strict Mathematical Glossary (docs/glossary.md).
"""

import numpy as np
from scipy import linalg as la
from scipy.sparse.linalg import eigsh

from stationarity_test.utils import validate_theta


# ===================================================================
# Component 1: Covariance kernel for rolling mean of Brownian motion
# ===================================================================

def _covariance_kernel_component1(theta: float, M: int) -> np.ndarray:
    """
    Build the M x M covariance matrix for component 1 (rolling mean).

    K_theta^{(1)}(u, v) = Cov[ (1/theta) int_u^{u+theta} W(s) ds,
                                (1/theta) int_v^{v+theta} W(s) ds ]

    Using Cov(W(s), W(s')) = min(s, s'), the double integral evaluates to:

    K_theta^{(1)}(u, v) = (1/theta^2) * int_u^{u+theta} int_v^{v+theta} min(s, s') ds ds'

    For intervals [a1, b1] and [a2, b2], the integral of min(s, s') is:
    I = int_{a1}^{b1} int_{a2}^{b2} min(s, s') ds ds'

    This can be evaluated analytically by splitting at the diagonal.

    Parameters
    ----------
    theta : float
        Window parameter in (0, 1/2].
    M : int
        Number of discretization points on [0, 1 - theta].

    Returns
    -------
    np.ndarray
        Symmetric positive semidefinite matrix of shape (M, M).
    """
    # Mesh on [0, 1 - theta]
    u_grid = np.linspace(0.0, 1.0 - theta, M)

    K = np.empty((M, M), dtype=np.float64)

    for i in range(M):
        u_i = u_grid[i]
        a1, b1 = u_i, u_i + theta

        for j in range(i, M):
            u_j = u_grid[j]
            a2, b2 = u_j, u_j + theta

            # Integral of min(s, s') over [a1, b1] x [a2, b2]
            val = _integral_min(a1, b1, a2, b2)
            val /= (theta * theta)

            K[i, j] = val
            K[j, i] = val

    # Subtract the outer product of means to get the CENTERED covariance
    # The variance in the definition is Var_u[...], so we need:
    # K_centered(u_i, u_j) = K(u_i, u_j) - E_u[K(u_i, ·)] * E_u[K(·, u_j)] / etc.
    # Actually, the eigenvalues of Var_u[X_u] correspond to the covariance
    # operator of X_u - E[X_u]. But our functional F_1^theta computes
    # sqrt(Var_u[e_u^theta]), which is the std dev of the process over u.
    # The eigenvalues relevant for the null distribution come from the
    # covariance of the centered process e_u - mean_u(e_u).

    # Center the kernel: subtract the mean from each row and column
    row_means = K.mean(axis=1)
    grand_mean = row_means.mean()
    K -= row_means[:, np.newaxis]
    K -= row_means[np.newaxis, :]
    K += grand_mean

    return K


def _integral_min(a1: float, b1: float, a2: float, b2: float) -> float:
    """
    Compute int_{a1}^{b1} int_{a2}^{b2} min(s, s') ds ds'.

    Analytical formula obtained by splitting the domain at s = s':

    Case 1: b1 <= a2 (intervals don't overlap, [a1,b1] fully below [a2,b2]):
        I = (b1^2 - a1^2)/2 * (b2 - a2)

    Case 2: a1 >= b2 (intervals don't overlap, [a1,b1] fully above [a2,b2]):
        I = (b2^2 - a2^2)/2 * (b1 - a1)

    General case (intervals may overlap):
        I = int_{a1}^{b1} [ int_{a2}^{min(s,b2)} s' ds' + int_{max(s,a2)}^{b2} s ds ] ds
        We use the identity for the general case.
    """
    # Use the general formula:
    # I = int_{a1}^{b1} int_{a2}^{b2} min(s, t) dt ds
    # = int_{a1}^{b1} [ int_{a2}^{min(s,b2)} t dt + s * max(0, b2 - max(s, a2)) ] ds
    # if s >= b2: entire inner integral is int_{a2}^{b2} t dt = (b2^2 - a2^2)/2
    # if s <= a2: entire inner integral is s * (b2 - a2)
    # if a2 < s < b2: int_{a2}^{s} t dt + s*(b2 - s) = (s^2 - a2^2)/2 + s*b2 - s^2
    #                = s*b2 - s^2/2 - a2^2/2

    # For efficiency, we compute this analytically by cases.
    # Let c = max(a1, a2), d = min(b1, b2) (overlap region boundaries)

    if b1 <= a2:
        # [a1, b1] entirely below [a2, b2], min(s, t) = s for all t in [a2, b2]
        return (b1**2 - a1**2) / 2.0 * (b2 - a2)

    if a1 >= b2:
        # [a1, b1] entirely above [a2, b2], min(s, t) = t for all t in [a2, b2]
        return (b2**2 - a2**2) / 2.0 * (b1 - a1)

    # General overlapping case: split integral at boundaries
    # Region 1: s in [a1, max(a1, a2)] where s <= a2 (if a1 < a2)
    # Region 2: s in [max(a1, a2), min(b1, b2)] where a2 <= s <= b2
    # Region 3: s in [min(b1, b2), b1] where s >= b2 (if b1 > b2)

    result = 0.0

    # Region 1: s in [a1, min(a2, b1)], here s <= a2, so min(s,t) = s for t in [a2,b2]
    s_lo = a1
    s_hi = min(a2, b1)
    if s_hi > s_lo:
        result += (s_hi**2 - s_lo**2) / 2.0 * (b2 - a2)

    # Region 2: s in [max(a1,a2), min(b1,b2)], overlapping zone
    s_lo = max(a1, a2)
    s_hi = min(b1, b2)
    if s_hi > s_lo:
        # Inner integral: int_{a2}^{s} t dt + s * (b2 - s)
        # = (s^2 - a2^2)/2 + s*b2 - s^2
        # = s*b2 - s^2/2 - a2^2/2
        # Outer integral over s:
        # int_{s_lo}^{s_hi} [s*b2 - s^2/2 - a2^2/2] ds
        # = b2*(s_hi^2 - s_lo^2)/2 - (s_hi^3 - s_lo^3)/6 - a2^2*(s_hi - s_lo)/2
        result += (b2 * (s_hi**2 - s_lo**2) / 2.0
                   - (s_hi**3 - s_lo**3) / 6.0
                   - a2**2 * (s_hi - s_lo) / 2.0)

    # Region 3: s in [max(b2, a1), b1], here s >= b2, so min(s,t) = t for t in [a2,b2]
    s_lo = max(b2, a1)
    s_hi = b1
    if s_hi > s_lo:
        result += (b2**2 - a2**2) / 2.0 * (s_hi - s_lo)

    return result


# ===================================================================
# Component 2: Covariance kernel for rolling variance (Wick's theorem)
# Fully vectorized with NumPy for performance.
# ===================================================================

def _covariance_kernel_component2(theta: float, M: int) -> np.ndarray:
    """
    Build the M x M covariance matrix for component 2 (rolling variance).

    K_theta^{(2)}(u, v) = Cov([S_theta(u)]^2, [S_theta(v)]^2)

    where S_theta(u)^2 = (1/theta) int_u^{u+theta} (W(s) - W_bar_u^theta)^2 ds

    Under Decision D2, g_2 operates on the VARIANCE [sigma_k]^2, not sigma_k.

    Computed via Wick's theorem (vectorized NumPy implementation).

    Parameters
    ----------
    theta : float
        Window parameter in (0, 1/2].
    M : int
        Number of discretization points.

    Returns
    -------
    np.ndarray
        Symmetric positive semidefinite matrix of shape (M, M).
    """
    u_grid = np.linspace(0.0, 1.0 - theta, M)

    # Sub-mesh points per window for Gauss-Legendre quadrature.
    # n_sub=32 gives trace convergence within ~0.5% of the continuous limit.
    # (n_sub=8 had ~5-8% trace inflation that required large kappa corrections.)
    n_sub = 32

    # Precompute GL nodes/weights for each u position
    # We precompute the min-matrices once per window pair, vectorized.
    K_mat = np.empty((M, M), dtype=np.float64)

    for i in range(M):
        u_i = u_grid[i]
        s1, w1 = _gauss_legendre_mesh(u_i, u_i + theta, n_sub)
        w1_normed = w1 / theta

        for j in range(i, M):
            u_j = u_grid[j]
            s2, w2 = _gauss_legendre_mesh(u_j, u_j + theta, n_sub)
            w2_normed = w2 / theta

            val = _cov_s2_s2_vectorized(s1, w1_normed, s2, w2_normed)
            K_mat[i, j] = val
            K_mat[j, i] = val

    # Center the kernel (Var_u operates on the centered process)
    row_means = K_mat.mean(axis=1)
    grand_mean = row_means.mean()
    K_mat -= row_means[:, np.newaxis]
    K_mat -= row_means[np.newaxis, :]
    K_mat += grand_mean

    return K_mat


def _cov_s2_s2_vectorized(s1, w1, s2, w2):
    """
    Compute Cov(S^2(u1), S^2(u2)) using fully vectorized Wick's theorem.

    S^2(u) = A(u) - B(u)^2  where:
        A(u) = sum_a w_a * W(s_a)^2          (discretized integral of W^2)
        B(u) = sum_a w_a * W(s_a)            (discretized mean)

    All expectations use E[W(a)W(b)W(c)W(d)] via Wick, computed with
    min-matrices and outer products.
    """
    n1, n2 = len(s1), len(s2)

    # --- Precompute min-matrices ---
    # M11[a, b] = min(s1[a], s1[b])
    M11 = np.minimum(s1[:, None], s1[None, :])
    # M22[c, d] = min(s2[c], s2[d])
    M22 = np.minimum(s2[:, None], s2[None, :])
    # M12[a, c] = min(s1[a], s2[c])
    M12 = np.minimum(s1[:, None], s2[None, :])

    # --- E[S^2(u)] = E[A(u)] - E[B(u)^2] ---
    E_A1 = np.sum(w1 * s1)  # E[W(s)^2] = s
    E_A2 = np.sum(w2 * s2)

    # E[B(u)^2] = sum_{a,b} w_a w_b min(s_a, s_b)
    E_B1_sq = np.einsum('a,b,ab->', w1, w1, M11)
    E_B2_sq = np.einsum('a,b,ab->', w2, w2, M22)

    E_S2_u1 = E_A1 - E_B1_sq
    E_S2_u2 = E_A2 - E_B2_sq

    # --- E[A1 * A2] ---
    # = sum_{a,b} w1_a w2_b * (s1_a * s2_b + 2 * min(s1_a, s2_b)^2)
    E_A1A2 = np.einsum('a,b,ab->', w1, w2,
                        np.outer(s1, s2) + 2.0 * M12**2)

    # --- E[A1 * B2^2] ---
    # = sum_{a,b,c} w1_a w2_b w2_c * (s1_a * min(s2_b, s2_c) + 2 * min(s1_a, s2_b) * min(s1_a, s2_c))
    # Vectorized: for each a, compute matrix over (b, c)
    # Term 1: s1_a * M22[b,c] summed with weights
    term1_A1B2 = np.einsum('a,a->', w1 * s1, np.ones(n1)) * np.einsum('b,c,bc->', w2, w2, M22)
    # Actually, more carefully:
    # sum_a w1_a * s1_a * sum_{b,c} w2_b w2_c * M22[b,c]
    term1 = np.sum(w1 * s1) * np.einsum('b,c,bc->', w2, w2, M22)
    # Term 2: 2 * sum_{a,b,c} w1_a w2_b w2_c * M12[a,b] * M12[a,c]
    # = 2 * sum_a w1_a * (sum_b w2_b M12[a,b]) * (sum_c w2_c M12[a,c])
    # = 2 * sum_a w1_a * v2[a]^2 where v2[a] = sum_b w2_b M12[a,b]
    v2 = M12 @ w2  # shape (n1,)
    term2 = 2.0 * np.sum(w1 * v2**2)
    E_A1B2sq = term1 + term2

    # --- E[B1^2 * A2] (by symmetry with E[A1 * B2^2]) ---
    term1_sym = np.sum(w2 * s2) * np.einsum('a,b,ab->', w1, w1, M11)
    v1 = M12.T @ w1  # M12.T[c, a] = M12[a, c]; shape (n2,)
    term2_sym = 2.0 * np.sum(w2 * v1**2)
    E_B1sqA2 = term1_sym + term2_sym

    # --- E[B1^2 * B2^2] ---
    # = sum_{a,b,c,d} w1_a w1_b w2_c w2_d * [M11[a,b]*M22[c,d] + M12[a,c]*M12[b,d] + M12[a,d]*M12[b,c]]
    # Term1: (sum_{a,b} w1_a w1_b M11[a,b]) * (sum_{c,d} w2_c w2_d M22[c,d])
    t1 = E_B1_sq * E_B2_sq

    # Term2: sum_{a,b,c,d} w1_a w1_b w2_c w2_d M12[a,c] M12[b,d]
    # = (sum_a w1_a M12[a,:]) . (sum_b w1_b M12[b,:]) with w2 weighting
    # = (M12.T @ w1) . w2) ^2  -- no, more carefully:
    # = sum_{c,d} w2_c w2_d * (sum_a w1_a M12[a,c]) * (sum_b w1_b M12[b,d])
    # = sum_{c,d} w2_c w2_d v1[c] v1[d]   where v1 = M12.T @ w1
    # = (sum_c w2_c v1[c])^2
    t2 = (np.sum(w2 * v1))**2

    # Term3: sum_{a,b,c,d} w1_a w1_b w2_c w2_d M12[a,d] M12[b,c]
    # = sum_{c,d} w2_c w2_d * (sum_a w1_a M12[a,d]) * (sum_b w1_b M12[b,c])
    # = sum_{c,d} w2_c w2_d v1[d] v1[c]   (same as t2)
    t3 = t2  # by symmetry of the sum

    E_B1sqB2sq = t1 + t2 + t3

    # --- Assemble ---
    E_product = E_A1A2 - E_A1B2sq - E_B1sqA2 + E_B1sqB2sq
    return E_product - E_S2_u1 * E_S2_u2


def _gauss_legendre_mesh(a: float, b: float, n: int) -> tuple[np.ndarray, np.ndarray]:
    """
    Gauss-Legendre quadrature nodes and weights on [a, b].

    Parameters
    ----------
    a, b : float
        Integration bounds.
    n : int
        Number of quadrature points.

    Returns
    -------
    nodes : np.ndarray
        Quadrature nodes on [a, b].
    weights : np.ndarray
        Quadrature weights (sum to b - a).
    """
    nodes_ref, weights_ref = np.polynomial.legendre.leggauss(n)
    nodes = 0.5 * (b - a) * nodes_ref + 0.5 * (a + b)
    weights = 0.5 * (b - a) * weights_ref
    return nodes, weights


# ===================================================================
# Main interface
# ===================================================================

def compute_eigenvalues(
    theta: float,
    component: int,
    K: int = 100,
    eps: float = 1e-6
) -> tuple[np.ndarray, float]:
    """
    Compute the first K eigenvalues of the covariance operator for the
    given component and window parameter theta.

    Parameters
    ----------
    theta : float
        Window parameter in (0, 1/2].
    component : int
        1 for rolling mean (linear kernel), 2 for rolling variance (Wick kernel).
    K : int
        Number of eigenvalues to return.
    eps : float
        Tolerance for truncation error bound.

    Returns
    -------
    eigenvalues : np.ndarray
        Array of shape (K,) with eigenvalues in decreasing order.
    truncation_bound : float
        Upper bound on sum_{k > K} lambda_k.

    Raises
    ------
    ValueError
        If theta is not in (0, 1/2] or component is not in {1, 2}.
    """
    validate_theta(theta)
    if component not in (1, 2):
        raise ValueError(f"component must be 1 or 2, got {component}")

    # Mesh size: M = max(500, ceil(50 / theta))  (corrected scaling rule)
    # Component 2 uses smaller M due to O(M^2 * n_sub^2) Wick kernel cost
    if component == 1:
        M = max(500, int(np.ceil(50.0 / theta)))
    else:
        M = min(100, max(50, int(np.ceil(20.0 / theta))))

    # Ensure K <= M (can't have more eigenvalues than mesh points)
    K = min(K, M)

    # Iterative refinement loop
    max_iterations = 5
    for iteration in range(max_iterations):
        # Build covariance matrix
        if component == 1:
            K_matrix = _covariance_kernel_component1(theta, M)
        else:
            K_matrix = _covariance_kernel_component2(theta, M)

        # Scale by mesh spacing (Nyström discretization weight).
        # The functionals are defined with Var_u w.r.t. the probability
        # measure du/(1-theta) on [0, 1-theta], so the quadrature weight
        # is 1/(M-1) — the mesh spacing on the UNIT probability interval,
        # NOT (1-theta)/(M-1) which would be the Lebesgue spacing.
        # See Audit A3 §1 for the derivation.
        weight = 1.0 / max(M - 1, 1)
        K_matrix *= weight

        # Compute eigenvalues
        if M <= 1000:
            # Full eigendecomposition
            all_eigenvalues = la.eigh(K_matrix, eigvals_only=True)
            # eigh returns in ascending order, reverse for descending
            all_eigenvalues = all_eigenvalues[::-1]
        else:
            # Sparse: top K eigenvalues via Lanczos
            all_eigenvalues = eigsh(
                K_matrix, k=min(K + 10, M - 1), which='LM', return_eigenvectors=False
            )
            all_eigenvalues = np.sort(all_eigenvalues)[::-1]

        # Clip small negative eigenvalues (numerical artifacts)
        all_eigenvalues = np.maximum(all_eigenvalues, 0.0)

        # Extract top K
        top_K = all_eigenvalues[:K]

        # Truncation bound: trace - sum of top K
        trace = np.trace(K_matrix)  # before eigendecomposition, but trace is invariant
        truncation_bound = max(0.0, trace - np.sum(top_K))

        if truncation_bound <= eps or iteration == max_iterations - 1:
            break

        # Refine: increase M by factor 1.5, capped at 4000 to prevent OOM
        M = min(int(M * 1.5), 4000)
        K = min(K, M)

    return top_K, truncation_bound
