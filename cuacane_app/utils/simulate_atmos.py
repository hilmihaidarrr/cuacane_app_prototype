# simulate_atmos.py
import numpy as np
from cuacane_app.utils.pasquill_classifier import PasquillStabilityClassifier
from cuacane_app.utils.calc_sigmas import calc_sigmas  # gunakan file calc_sigmas.py yang sudah kamu punya

# Mapping Pasquill A–F -> CATEGORY 1..6 (Very Unstable..Very Stable)
PASQ_TO_CAT = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6}

def simulate_atmos(
    data_dict: dict,
    Q: float,                  # laju emisi (µg/s atau unit massa/s)
    H: float,                  # tinggi sumber (m)
    stability: str = 'auto',   # 'auto' atau 'A'..'F'
    grid_size: int = 1000,
    max_distance: float = 5000.0,   # m
    max_cross: float = 1000.0,      # m
    z_eval: float = 0.0,            # evaluasi di ketinggian z (m), default permukaan
    xs: float = 0.0, ys: float = 0.0,  # posisi sumber (m) relatif origin
    mask_upwind: bool = True        # hanya hitung untuk downwind > 0
):
    """
    Gaussian plume dengan ground reflection (sesuai rumus target):

      C = Q / (2π u σy σz) * exp(-crosswind²/(2 σy²))
          * [exp(-(z-H)²/(2 σz²)) + exp(-(z+H)²/(2 σz²))]

    - σy, σz dihitung via Pasquill–Gifford (calc_sigmas)
    - Menggunakan data sensor Cuacane (u, arah angin, T, RH, hujan, datetime)
    - Output: X, Y, C (koordinat meter relatif sensor; C = konsentrasi)
    """
    try:
        # 1) Ambil data angin dari sensor
        u = float(data_dict.get("wind_speed_avg", 0.1))
        if not np.isfinite(u) or u < 0.1:
            u = 0.1  # floor untuk hindari pembagian nol
        theta_from = float(data_dict.get("wind_dir_avg", 0.0))  # derajat, arah DATANG (meteorologi)

        # 2) Tentukan kelas stabilitas
        if stability == 'auto':
            required = ["temp_air", "humidity", "datetime"]
            if any(k not in data_dict or data_dict[k] in (None, "") for k in required):
                stability = 'D'  # fallback netral
            else:
                stability = PasquillStabilityClassifier.from_dict(data_dict)

        # Normalisasi huruf ke uppercase
        if isinstance(stability, str):
            stability = stability.upper().strip()

        CATEGORY = PASQ_TO_CAT.get(stability, PASQ_TO_CAT['D'])  # default ke D (4) bila invalid

        # 3) Grid koordinat (meter, simetris)
        x = np.linspace(-max_distance, max_distance, grid_size)
        y = np.linspace(-max_cross, max_cross, grid_size)
        X, Y = np.meshgrid(x, y)                 
        Z = np.full_like(X, float(z_eval))       

        # 4) Translasi relatif terhadap sumber
        x1 = X - xs
        y1 = Y - ys

        # 5) Vektor angin "menuju" (arah datang -> hembusan = dir_from - 180)
        ang = np.deg2rad(theta_from - 180.0)
        wx = u * np.sin(ang)
        wy = u * np.cos(ang)

        # 6) Proyeksi ke downwind & crosswind
        hyp = np.hypot(x1, y1)
        dot = wx * x1 + wy * y1
        denom = (u * np.maximum(hyp, 1e-15))
        cos_th = np.clip(dot / denom, -1.0, 1.0)
        subtended = np.arccos(cos_th)
        downwind = np.cos(subtended) * hyp
        crosswind = np.sin(subtended) * hyp

        # 7) σy, σz via PG piecewise
        sig_y, sig_z = calc_sigmas(CATEGORY, downwind)
        sig_y = np.where(sig_y <= 0.0, 1e-6, sig_y)
        sig_z = np.where(sig_z <= 0.0, 1e-6, sig_z)

        # 8) Gaussian plume dengan ground reflection
        C = np.zeros_like(X, dtype=float)
        mask = (downwind > 0.0) if mask_upwind else np.ones_like(X, dtype=bool)

        cy = np.exp(- (crosswind[mask] ** 2) / (2.0 * (sig_y[mask] ** 2)))
        cz_top = np.exp(- ((Z[mask] - H) ** 2) / (2.0 * (sig_z[mask] ** 2)))
        cz_ref = np.exp(- ((Z[mask] + H) ** 2) / (2.0 * (sig_z[mask] ** 2)))

        C[mask] = (Q / (2.0 * np.pi * u * sig_y[mask] * sig_z[mask])) * cy * (cz_top + cz_ref)

        # 9) Sanitasi nilai
        C = np.where(np.isfinite(C), C, 0.0)

        return X, Y, C

    except Exception as e:
        print(f"[❌] Error pada simulate_atmos (baru): {e}")
        return None, None, None
