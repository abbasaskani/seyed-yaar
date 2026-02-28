from __future__ import annotations

from typing import Dict, List, Tuple, Optional
import numpy as np

from .scoring import score_current_m_s, score_waves_hs


def ops_feasibility(
    current_m_s: np.ndarray,
    waves_hs_m: np.ndarray,
    priors: Dict,
    gear_depth_m: float = 10.0,
) -> np.ndarray:
    """Operational feasibility Pops (0..1).

    *Soft* ops layer (continuous) rather than hard masking.

    gear_depth_m affects the relative importance of waves vs currents:
      - shallower gear → waves matter more
      - deeper gear → currents matter more

    Keep this conservative unless you have gear-specific logs/feedback.
    """

    soft_max = float(priors.get("waves_hs_soft_max_m", 1.5))
    softness = float(priors.get("waves_hs_softness", 0.35))
    s_w = score_waves_hs(waves_hs_m, soft_max_m=soft_max, softness=softness)

    opt = float(priors.get("current_opt_m_s", 0.4))
    sig = float(priors.get("current_sigma_m_s", 0.25))
    s_c = score_current_m_s(current_m_s, opt_m_s=opt, sigma_m_s=sig)

    d = float(gear_depth_m)

    # depth-aware weights: allow shallow like 2m too
    # waves weight in ~[0.45..0.75]
    w_waves = 0.60 + (8.0 - d) * 0.015
    w_curr = 1.0 - w_waves
    w_waves = float(np.clip(w_waves, 0.45, 0.80))
    w_curr = float(np.clip(w_curr, 0.20, 0.55))
    s = w_waves + w_curr
    w_waves /= s
    w_curr /= s

    pops = np.clip(w_waves * s_w + w_curr * s_c, 0.0, 1.0)
    return pops


def ops_feasibility_mix_depths(
    current_m_s: np.ndarray,
    waves_hs_m: np.ndarray,
    priors: Dict,
    depths_m: List[float],
    weights: Optional[List[float]] = None,
) -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
    """Compute Pops as a weighted mixture over multiple effective gear depths.

    Returns:
      pops_mix, components dict (per-depth)
    """
    if not depths_m:
        return ops_feasibility(current_m_s, waves_hs_m, priors, gear_depth_m=10.0), {}

    if weights is None:
        # default: emphasize shallow (surface gillnet)
        weights = [0.55, 0.30, 0.15] + [0.0] * max(0, len(depths_m) - 3)
        weights = weights[:len(depths_m)]

    w = np.asarray(weights, dtype=np.float32)
    if w.size != len(depths_m):
        w = np.ones((len(depths_m),), dtype=np.float32)
    w = np.clip(w, 0.0, None)
    if float(w.sum()) <= 0:
        w[:] = 1.0
    w = w / float(w.sum())

    pops = np.zeros_like(current_m_s, dtype=np.float32)
    comps: Dict[str, np.ndarray] = {}
    for depth, ww in zip(depths_m, w):
        p = ops_feasibility(current_m_s, waves_hs_m, priors, gear_depth_m=float(depth))
        comps[f"pops_{int(depth)}m"] = p.astype(np.float32)
        pops += float(ww) * p.astype(np.float32)

    pops = np.clip(pops, 0.0, 1.0)
    comps["pops_mix"] = pops.astype(np.float32)
    return pops, comps
