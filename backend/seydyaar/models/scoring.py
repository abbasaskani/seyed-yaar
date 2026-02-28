from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple, Optional
import math
import numpy as np

from scipy.ndimage import median_filter, distance_transform_edt


def _gauss(x: np.ndarray, mu: float, sigma: float) -> np.ndarray:
    sigma = max(float(sigma), 1e-6)
    return np.exp(-0.5 * ((x - mu) / sigma) ** 2)


def score_temp_c(sst_c: np.ndarray, opt_c: float, sigma_c: float) -> np.ndarray:
    return _gauss(sst_c, opt_c, sigma_c)


def score_chl_mg_m3(chl: np.ndarray, opt_mg_m3: float, sigma_log10: float) -> np.ndarray:
    chl = np.clip(chl, 1e-6, None)
    return _gauss(np.log10(chl), np.log10(opt_mg_m3), sigma_log10)


def score_current_m_s(spd: np.ndarray, opt_m_s: float, sigma_m_s: float) -> np.ndarray:
    return _gauss(spd, opt_m_s, sigma_m_s)


def score_waves_hs(hs_m: np.ndarray, soft_max_m: float = 1.5, softness: float = 0.35) -> np.ndarray:
    # logistic penalty: ~1 below soft_max, declines above
    return 1.0 / (1.0 + np.exp((hs_m - soft_max_m) / max(softness, 1e-6)))


def gradient_magnitude(arr: np.ndarray) -> np.ndarray:
    gy, gx = np.gradient(arr.astype(np.float32))
    return np.sqrt(gx * gx + gy * gy)


def _robust01(x: np.ndarray, lo_q: float = 5.0, hi_q: float = 95.0) -> np.ndarray:
    lo = float(np.nanpercentile(x, lo_q))
    hi = float(np.nanpercentile(x, hi_q))
    out = (x - lo) / (hi - lo + 1e-9)
    return np.clip(out, 0.0, 1.0).astype(np.float32)


def _belkin_smooth(arr: np.ndarray, size: int = 7, iters: int = 1) -> np.ndarray:
    # Belkin & O'Reilly (2009) use an iterative contextual median filter.
    # Here we apply a practical "Belkin-inspired" median smoothing before gradients.
    x = arr.astype(np.float32)
    for _ in range(max(int(iters), 1)):
        x = median_filter(x, size=int(size), mode="nearest")
    return x


def front_components(
    sst_c: np.ndarray,
    chl_mg_m3: np.ndarray,
    ssh_m: np.ndarray,
    method: str = "gradient",
    belkin_size: int = 7,
    belkin_iters: int = 1,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    if method.lower() in ("belkin", "median"):
        sst_f = _belkin_smooth(sst_c, size=belkin_size, iters=belkin_iters)
        chl_f = _belkin_smooth(np.log10(np.clip(chl_mg_m3, 1e-6, None)), size=belkin_size, iters=belkin_iters)
        ssh_f = _belkin_smooth(ssh_m, size=belkin_size, iters=belkin_iters)
        tf = gradient_magnitude(sst_f)
        cf = gradient_magnitude(chl_f)
        sf = gradient_magnitude(ssh_f)
        return tf.astype(np.float32), cf.astype(np.float32), sf.astype(np.float32)

    # fallback: raw gradients
    tf = gradient_magnitude(sst_c)
    cf = gradient_magnitude(np.log10(np.clip(chl_mg_m3, 1e-6, None)))
    sf = gradient_magnitude(ssh_m)
    return tf.astype(np.float32), cf.astype(np.float32), sf.astype(np.float32)


def front_score(
    temp_front: np.ndarray,
    chl_front: np.ndarray,
    ssh_front: np.ndarray,
    w_temp: float = 0.5,
    w_chl: float = 0.25,
    w_ssh: float = 0.25,
) -> np.ndarray:
    s = w_temp * temp_front + w_chl * chl_front + w_ssh * ssh_front
    return _robust01(s, 5, 95)


def score_sss_psu(sss_psu: np.ndarray, opt_psu: float, sigma_psu: float) -> np.ndarray:
    return _gauss(sss_psu, opt_psu, sigma_psu)


def score_mld_m(mld_m: np.ndarray, opt_m: float, sigma_m: float) -> np.ndarray:
    return _gauss(mld_m, opt_m, sigma_m)


def score_o2_floor(o2_umol_l: np.ndarray, min_umol_l: float = 150.0, softness: float = 20.0) -> np.ndarray:
    # soft floor: penalize low oxygen
    # score ~1 above min, declines below min
    return 1.0 / (1.0 + np.exp((min_umol_l - o2_umol_l) / max(float(softness), 1e-6)))


def _grid_spacing_m(lat_mean_deg: float, dx_deg: float, dy_deg: float) -> Tuple[float, float]:
    # crude but fine for AOI-sized domains
    R = 6371000.0
    dx_m = math.radians(dx_deg) * R * math.cos(math.radians(lat_mean_deg))
    dy_m = math.radians(dy_deg) * R
    return float(dx_m), float(dy_m)


def okubo_weiss(
    u_m_s: np.ndarray,
    v_m_s: np.ndarray,
    lat_mean_deg: float,
    dx_deg: float,
    dy_deg: float,
) -> Tuple[np.ndarray, np.ndarray]:
    """Compute Okubo–Weiss parameter (s^-2) and relative vorticity (s^-1).

    OW = Sn^2 + Ss^2 - zeta^2, where:
      Sn = du/dx - dv/dy
      Ss = dv/dx + du/dy
      zeta = dv/dx - du/dy
    """
    dx_m, dy_m = _grid_spacing_m(lat_mean_deg, dx_deg, dy_deg)

    dudy, dudx = np.gradient(u_m_s.astype(np.float32), dy_m, dx_m)
    dvdy, dvdx = np.gradient(v_m_s.astype(np.float32), dy_m, dx_m)

    Sn = dudx - dvdy
    Ss = dvdx + dudy
    zeta = dvdx - dudy

    ow = (Sn * Sn + Ss * Ss - zeta * zeta).astype(np.float32)
    return ow, zeta.astype(np.float32)


def score_okubo_eddy(ow_s2: np.ndarray) -> np.ndarray:
    # vorticity-dominated eddy cores tend to have OW < 0
    ed = (-ow_s2).astype(np.float32)
    return _robust01(ed, 50, 95)


def wind_stress_curl(
    tau_x: np.ndarray,
    tau_y: np.ndarray,
    lat_mean_deg: float,
    dx_deg: float,
    dy_deg: float,
) -> np.ndarray:
    dx_m, dy_m = _grid_spacing_m(lat_mean_deg, dx_deg, dy_deg)
    dtauy_dy, dtauy_dx = np.gradient(tau_y.astype(np.float32), dy_m, dx_m)
    dtaux_dy, dtaux_dx = np.gradient(tau_x.astype(np.float32), dy_m, dx_m)
    curl = (dtauy_dx - dtaux_dy).astype(np.float32)
    return curl


def ekman_pumping(
    curl_tau: np.ndarray,
    lat_mean_deg: float,
    rho_w: float = 1025.0,
) -> np.ndarray:
    Omega = 7.292115e-5
    f = 2.0 * Omega * math.sin(math.radians(lat_mean_deg))
    f = float(f) if abs(f) > 1e-10 else (1e-10 if f >= 0 else -1e-10)
    return (curl_tau / (rho_w * f)).astype(np.float32)


def score_upwelling(w_ekman: np.ndarray) -> np.ndarray:
    # For NH AOI (Arabian Sea), positive w_Ekman tends to mean upwelling-favorable.
    wp = np.clip(w_ekman.astype(np.float32), 0.0, None)
    return _robust01(wp, 50, 95)


def bathy_shelfbreak_score(
    depth_m_pos_down: np.ndarray,
    lat_mean_deg: float,
    dx_deg: float,
    dy_deg: float,
    scale_km: float = 120.0,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return (score 0..1, shelfbreak_mask u8, dist_km). depth positive down."""
    dx_m, dy_m = _grid_spacing_m(lat_mean_deg, dx_deg, dy_deg)
    gy, gx = np.gradient(depth_m_pos_down.astype(np.float32), dy_m, dx_m)
    slope = np.sqrt(gx * gx + gy * gy)  # unitless (m/m)

    # shelf break roughly at 100-200m; we allow 50-300m to be robust
    cand = (depth_m_pos_down > 50.0) & (depth_m_pos_down < 300.0)
    thr = float(np.nanpercentile(slope[cand] if np.any(cand) else slope, 90))
    shelf = cand & (slope >= thr)

    # distance to shelfbreak (km)
    inv = ~shelf
    dist_pix = distance_transform_edt(inv)
    pix_m = float(np.sqrt(dx_m * dx_m + dy_m * dy_m))
    dist_km = (dist_pix * pix_m / 1000.0).astype(np.float32)

    score = np.exp(-dist_km / max(float(scale_km), 1e-6)).astype(np.float32)
    return score, shelf.astype(np.uint8), dist_km


def enm_levels_three(x: np.ndarray, lo: float, hi: float) -> np.ndarray:
    """Return 0 / 0.3 / 1 based on thresholds."""
    out = np.zeros_like(x, dtype=np.float32)
    out = np.where(x >= lo, 0.3, out)
    out = np.where(x >= hi, 1.0, out)
    return out


def habitat_envelope(
    *,
    sst_c: np.ndarray,
    chl_mg_m3: np.ndarray,
    front01: np.ndarray,
    sss_psu: Optional[np.ndarray],
    mld_m: Optional[np.ndarray],
    o2_umol_l: Optional[np.ndarray],
    priors: Dict,
) -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
    """ENM / envelope-style habitat score (0..1), inspired by IOTC/Druon-like logic.

    Designed to be explainable and robust when you don't have lots of catch/effort.
    """
    env = priors.get("envelope", {})

    # productivity tier (0, 0.3, 1) from CHL and/or front
    chl_lo = float(env.get("chl_lo", 0.10))
    chl_hi = float(env.get("chl_hi", 0.25))
    front_lo = float(env.get("front_lo", 0.20))
    front_hi = float(env.get("front_hi", 0.45))

    prod_chl = enm_levels_three(chl_mg_m3, chl_lo, chl_hi)
    prod_fr  = enm_levels_three(front01, front_lo, front_hi)
    prod = np.maximum(prod_chl, prod_fr).astype(np.float32)

    # abiotic masks
    def _mask_range(arr: np.ndarray, lo: float, hi: float) -> np.ndarray:
        return ((arr >= lo) & (arr <= hi)).astype(np.float32)

    sst_lo = float(env.get("sst_lo", float(priors.get("sst_opt_c", 28.0) - 6.0)))
    sst_hi = float(env.get("sst_hi", float(priors.get("sst_opt_c", 28.0) + 6.0)))
    m_sst = _mask_range(sst_c, sst_lo, sst_hi)

    m_sss = 1.0
    if sss_psu is not None and "sss_lo" in env and "sss_hi" in env:
        m_sss = _mask_range(sss_psu, float(env["sss_lo"]), float(env["sss_hi"]))

    m_mld = 1.0
    if mld_m is not None and "mld_lo" in env and "mld_hi" in env:
        m_mld = _mask_range(mld_m, float(env["mld_lo"]), float(env["mld_hi"]))

    m_o2 = 1.0
    if o2_umol_l is not None and "o2_min" in env:
        # soft floor
        m_o2 = score_o2_floor(o2_umol_l, float(env["o2_min"]), float(env.get("o2_softness", 20.0)))

    phab = (prod * m_sst * m_sss * m_mld * m_o2).astype(np.float32)
    phab = np.clip(phab, 0.0, 1.0)

    comps = {"enm_prod": prod, "enm_m_sst": m_sst.astype(np.float32)}
    if isinstance(m_sss, np.ndarray): comps["enm_m_sss"] = m_sss.astype(np.float32)
    if isinstance(m_mld, np.ndarray): comps["enm_m_mld"] = m_mld.astype(np.float32)
    if isinstance(m_o2, np.ndarray): comps["enm_m_o2"] = m_o2.astype(np.float32)
    return phab, comps


@dataclass
class HabitatInputs:
    sst_c: np.ndarray
    chl_mg_m3: np.ndarray
    current_m_s: np.ndarray
    waves_hs_m: np.ndarray
    ssh_m: np.ndarray

    # Optional layers
    u_m_s: Optional[np.ndarray] = None
    v_m_s: Optional[np.ndarray] = None
    sss_psu: Optional[np.ndarray] = None
    mld_m: Optional[np.ndarray] = None
    o2_umol_l: Optional[np.ndarray] = None
    tau_x: Optional[np.ndarray] = None
    tau_y: Optional[np.ndarray] = None
    bathy_m_pos_down: Optional[np.ndarray] = None


def habitat_scoring(
    inputs: HabitatInputs,
    priors: Dict,
    weights: Dict,
    *,
    dx_deg: float,
    dy_deg: float,
    lat_mean_deg: float,
) -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
    """HSI-style habitat score (0..1) with optional extra predictors."""

    s_temp = score_temp_c(inputs.sst_c, priors["sst_opt_c"], priors["sst_sigma_c"])
    s_chl  = score_chl_mg_m3(inputs.chl_mg_m3, priors["chl_opt_mg_m3"], priors["chl_sigma_log10"])
    s_cur  = score_current_m_s(inputs.current_m_s, priors["current_opt_m_s"], priors["current_sigma_m_s"])

    # front method
    fm = str(priors.get("front_method", "gradient"))
    belkin_size = int(priors.get("belkin_size", 7))
    belkin_iters = int(priors.get("belkin_iters", 1))
    tf, cf, sf = front_components(inputs.sst_c, inputs.chl_mg_m3, inputs.ssh_m, method=fm, belkin_size=belkin_size, belkin_iters=belkin_iters)

    fw = priors.get("front_weights", {"temp":0.5,"chl":0.25,"ssh":0.25})
    s_front = front_score(tf, cf, sf, float(fw.get("temp",0.5)), float(fw.get("chl",0.25)), float(fw.get("ssh",0.25)))

    # Optional scores
    s_sss = None
    if inputs.sss_psu is not None and "sss_opt_psu" in priors and "sss_sigma_psu" in priors:
        s_sss = score_sss_psu(inputs.sss_psu, float(priors["sss_opt_psu"]), float(priors["sss_sigma_psu"]))

    s_mld = None
    if inputs.mld_m is not None and "mld_opt_m" in priors and "mld_sigma_m" in priors:
        s_mld = score_mld_m(inputs.mld_m, float(priors["mld_opt_m"]), float(priors["mld_sigma_m"]))

    s_o2 = None
    if inputs.o2_umol_l is not None and "o2_min_umol_l" in priors:
        s_o2 = score_o2_floor(inputs.o2_umol_l, float(priors.get("o2_min_umol_l", 150.0)), float(priors.get("o2_softness", 20.0)))

    s_eddy = None
    ow = None
    zeta = None
    if inputs.u_m_s is not None and inputs.v_m_s is not None:
        ow, zeta = okubo_weiss(inputs.u_m_s, inputs.v_m_s, lat_mean_deg, dx_deg, dy_deg)
        s_eddy = score_okubo_eddy(ow)

    s_upw = None
    curl_tau = None
    w_ek = None
    if inputs.tau_x is not None and inputs.tau_y is not None:
        curl_tau = wind_stress_curl(inputs.tau_x, inputs.tau_y, lat_mean_deg, dx_deg, dy_deg)
        w_ek = ekman_pumping(curl_tau, lat_mean_deg)
        s_upw = score_upwelling(w_ek)

    s_bathy = None
    shelf_mask = None
    shelf_dist_km = None
    if inputs.bathy_m_pos_down is not None:
        s_bathy, shelf_mask, shelf_dist_km = bathy_shelfbreak_score(inputs.bathy_m_pos_down, lat_mean_deg, dx_deg, dy_deg, scale_km=float(priors.get("shelf_scale_km", 120.0)))

    # weights (auto-renormalize) — include only available layers
    w = {k: float(v) for k, v in dict(weights).items()}
    # Never double-count waves here (ops handles it)
    w.pop("waves", None)

    avail = {
        "temp": s_temp,
        "chl": s_chl,
        "front": s_front,
        "current": s_cur,
        "sss": s_sss,
        "mld": s_mld,
        "o2": s_o2,
        "eddy": s_eddy,
        "upwelling": s_upw,
        "bathy": s_bathy,
    }

    # prune missing
    for k in list(w.keys()):
        if (k not in avail) or (avail[k] is None):
            w.pop(k, None)

    total = sum(max(v, 0.0) for v in w.values())
    if total <= 0:
        w = {"temp": 1.0}
        total = 1.0
    for k in list(w.keys()):
        w[k] = max(float(w[k]), 0.0) / total

    phab = np.zeros_like(s_temp, dtype=np.float32)
    for k, wk in w.items():
        phab += wk * avail[k].astype(np.float32)

    phab = np.clip(phab, 0.0, 1.0)

    comps: Dict[str, np.ndarray] = {
        "score_temp": s_temp.astype(np.float32),
        "score_chl": s_chl.astype(np.float32),
        "score_front": s_front.astype(np.float32),
        "score_current": s_cur.astype(np.float32),
        "temp_front": tf.astype(np.float32),
        "chl_front": cf.astype(np.float32),
        "ssh_front": sf.astype(np.float32),
    }
    if s_sss is not None: comps["score_sss"] = s_sss.astype(np.float32)
    if s_mld is not None: comps["score_mld"] = s_mld.astype(np.float32)
    if s_o2 is not None: comps["score_o2"] = s_o2.astype(np.float32)
    if ow is not None: comps["okubo_weiss"] = ow.astype(np.float32)
    if zeta is not None: comps["rel_vorticity"] = zeta.astype(np.float32)
    if s_eddy is not None: comps["score_eddy"] = s_eddy.astype(np.float32)
    if curl_tau is not None: comps["curl_tau"] = curl_tau.astype(np.float32)
    if w_ek is not None: comps["ekman_w"] = w_ek.astype(np.float32)
    if s_upw is not None: comps["score_upwelling"] = s_upw.astype(np.float32)
    if s_bathy is not None: comps["score_bathy"] = s_bathy.astype(np.float32)
    if shelf_mask is not None: comps["shelf_break_mask"] = shelf_mask.astype(np.float32)
    if shelf_dist_km is not None: comps["shelf_dist_km"] = shelf_dist_km.astype(np.float32)

    return phab, comps
