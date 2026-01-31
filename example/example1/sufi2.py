import numpy as np
from dataclasses import dataclass
from typing import Dict, Any, Optional, Tuple


@dataclass
class SUFI2Config:
    n_samples: int = 200            # 每轮采样数 N（LHS）
    max_iter: int = 10              # 最大迭代轮数
    behavioral_frac: float = 0.2    # 行为解比例（取前 20%）
    expand_ratio: float = 0.05      # 收缩后再轻微扩张，防止过早收敛（0~0.2 常用）
    range_tol_rel: float = 1e-3     # 相对范围收敛阈值
    range_tol_abs: float = 1e-12    # 绝对范围收敛阈值
    seed: Optional[int] = 1234      # 随机种子
    maximize: Optional[bool] = None # None: 自动读 problem.optType；否则你指定 True/False
    verbose: bool = True


def lhs_sample(lb: np.ndarray, ub: np.ndarray, n: int, rng: np.random.Generator) -> np.ndarray:
    """Latin Hypercube Sampling in [lb, ub]."""
    lb = np.asarray(lb, dtype=float).ravel()
    ub = np.asarray(ub, dtype=float).ravel()
    d = lb.size
    if ub.shape != lb.shape:
        raise ValueError("LB/ub shape mismatch")

    # 每维分成 n 层： (k + u)/n ，然后每一维独立打乱
    H = (rng.random((n, d)) + np.arange(n)[:, None]) / n
    for j in range(d):
        rng.shuffle(H[:, j])

    X = lb + H * (ub - lb)
    return X


def _as_1d(y) -> np.ndarray:
    """把 objFunc 输出尽量规整成 (n,)"""
    y = np.asarray(y)
    if y.ndim == 2 and y.shape[1] == 1:
        y = y[:, 0]
    if y.ndim != 1:
        raise ValueError(f"objFunc must return 1D array-like (n,), got shape={y.shape}")
    return y


def run_sufi2(problem, cfg: SUFI2Config) -> Dict[str, Any]:
    """
    Simplified SUFI-2 for calibration where objFunc returns NSE (scalar per sample).
    Updates problem.LB and problem.ub in-place each iteration.
    """
    rng = np.random.default_rng(cfg.seed)

    # 自动判断最大化/最小化
    maximize = cfg.maximize
    if maximize is None:
        opt_type = getattr(problem, "optType", "max")
        maximize = (str(opt_type).lower() == "max")

    # 记录初始全局边界（用于裁剪 & 收敛判断）
    global_lb = np.asarray(problem.lb, dtype=float).copy().ravel()
    global_ub = np.asarray(problem.ub, dtype=float).copy().ravel()

    best_x_global = None
    best_y_global = -np.inf if maximize else np.inf

    history = []

    for it in range(1, cfg.max_iter + 1):
        lb = np.asarray(problem.lb, dtype=float).ravel()
        ub = np.asarray(problem.ub, dtype=float).ravel()

        # 采样
        X = lhs_sample(lb, ub, cfg.n_samples, rng)

        # 评估：NSE（越大越好，一般）
        y = _as_1d(problem.objFunc(X))

        if maximize:
            order = np.argsort(y)[::-1]
            best_idx = order[0]
            best_y = float(y[best_idx])
            best_x = X[best_idx].copy()
        else:
            order = np.argsort(y)
            best_idx = order[0]
            best_y = float(y[best_idx])
            best_x = X[best_idx].copy()

        # 更新全局最优
        if (maximize and best_y > best_y_global) or ((not maximize) and best_y < best_y_global):
            best_y_global = best_y
            best_x_global = best_x.copy()

        # 选“行为解”：取前 behavioral_frac（也可以改成阈值法）
        k = max(2, int(cfg.n_samples * cfg.behavioral_frac))
        idx_keep = order[:k]
        Xb = X[idx_keep]

        new_lb = Xb.min(axis=0)
        new_ub = Xb.max(axis=0)

        # 稍微扩张一点，避免范围塌太快
        center = 0.5 * (new_lb + new_ub)
        half = 0.5 * (new_ub - new_lb)
        half = half * (1.0 + float(cfg.expand_ratio))
        new_lb = center - half
        new_ub = center + half

        # 裁剪到全局初始边界内
        new_lb = np.maximum(new_lb, global_lb)
        new_ub = np.minimum(new_ub, global_ub)

        # 防止数值上 lb>=UB
        eps = 1e-15
        bad = new_ub <= new_lb
        if np.any(bad):
            mid = 0.5 * (new_lb[bad] + new_ub[bad])
            new_lb[bad] = mid - eps
            new_ub[bad] = mid + eps

        # 写回 problem（你说的接口：改 lb/UB）
        problem.lb = new_lb
        problem.ub = new_ub

        # 收敛判定：范围缩小到一定程度
        cur_range = new_ub - new_lb
        global_range = global_ub - global_lb
        rel = np.max(cur_range / np.maximum(global_range, cfg.range_tol_abs))
        absr = np.max(cur_range)

        history.append({
            "iter": it,
            "best_y_iter": best_y,
            "best_x_iter": best_x,
            "best_y_global": best_y_global,
            "LB": new_lb.copy(),
            "ub": new_ub.copy(),
            "range_rel_max": float(rel),
            "range_abs_max": float(absr),
        })

        if cfg.verbose:
            print(f"[SUFI-2] iter={it:02d}  best_iter={best_y:.6f}  best_global={best_y_global:.6f}  "
                  f"range_rel_max={rel:.3e}  range_abs_max={absr:.3e}")

        if rel <= cfg.range_tol_rel or absr <= cfg.range_tol_abs:
            if cfg.verbose:
                print("[SUFI-2] Converged by range tolerance.")
            break

    return {
        "best_x": best_x_global,
        "best_y": best_y_global,
        "history": history,
        "maximize": maximize,
    }
