"""
Effect size helpers used across the hypothesis tests in
notebooks/04_statistical_tests.ipynb.
"""

import numpy as np


def cohens_d(group_a, group_b):
    n1, n2 = len(group_a), len(group_b)
    pooled_std = np.sqrt(
        ((n1 - 1) * group_a.std(ddof=1) ** 2 + (n2 - 1) * group_b.std(ddof=1) ** 2)
        / (n1 + n2 - 2)
    )
    return (group_a.mean() - group_b.mean()) / pooled_std


def rank_biserial_r(u_statistic, n1, n2):
    # Effect size for Mann-Whitney U
    return 1 - (2 * u_statistic) / (n1 * n2)


def epsilon_squared_kw(h_statistic, n):
    # Effect size for Kruskal-Wallis 
    return h_statistic / (n - 1)


def bootstrap_ci_mean(data, n_boot=5000, ci=95, random_state=42):
    rng = np.random.default_rng(random_state)
    boot_means = np.array([
        rng.choice(data, size=len(data), replace=True).mean()
        for _ in range(n_boot)
    ])
    lower = np.percentile(boot_means, (100 - ci) / 2)
    upper = np.percentile(boot_means, 100 - (100 - ci) / 2)
    return data.mean(), lower, upper