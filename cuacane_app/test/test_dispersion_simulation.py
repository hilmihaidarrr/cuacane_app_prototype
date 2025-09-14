import numpy as np
from cuacane_app.utils.simulate_atmos import simulate_atmos  # Sesuaikan dengan path-mu
from datetime import datetime

def test_dispersion_output():
    # Data sensor dummy
    sensor_data = {
        "wind_speed_avg": 2.0,        # m/s
        "wind_dir_avg": 270.0,        # arah angin dari barat → ke timur
        "temp_air": 25.0,             # derajat Celsius
        "humidity": 60.0,             # persen
        "rain_intensity": 0.0,        # mm/h
        "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    Q = 100_000.0  # µg/s
    H = 50.0       # meter

    X, Y, C = simulate_atmos(sensor_data, Q=Q, H=H)

    assert X is not None and Y is not None and C is not None, "❌ Simulasi gagal menghasilkan data"

    maxC = np.nanmax(C)
    peak_idx = np.unravel_index(np.nanargmax(C), C.shape)
    max_x = float(X[peak_idx])
    max_y = float(Y[peak_idx])

    print(f"[✅] Konsentrasi maksimum pada (x={max_x:.1f}, y={max_y:.1f}) = {maxC:.2f} µg/m³")

    # Validasi area sebaran
    assert max_x > 100, "❌ Pusat distribusi tidak muncul pada area bawah cerobong!"
    assert abs(max_y) < 500, "❌ Sebaran menyebar terlalu jauh ke samping!"

    print("✅ Test simulasi dispersi Gaussian berhasil")

if __name__ == "__main__":
    test_dispersion_output()
