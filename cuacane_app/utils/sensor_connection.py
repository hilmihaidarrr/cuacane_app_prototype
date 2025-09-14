from datetime import datetime, timedelta
from collections import deque
import csv
import os
import numpy as np
import json
import requests
from PyQt5.QtCore import QObject, pyqtSignal, pyqtProperty, pyqtSlot, QTimer, QVariant
from PyQt5.QtWidgets import QApplication
from cuacane_app.utils.simulate_atmos import simulate_atmos
from cuacane_app.utils.multi_predictor import load_all_models, predict_from_data, get_full_series_for_chart
from cuacane_app.utils.line_parser import parse_0R0_line

def get_latest_raw_from_cloud():
    try:
        r = requests.get("https://cuacane-cloud-api.onrender.com/latest_raw", timeout=5)
        data = r.json()
        raw_line = data.get("raw", "")
        return raw_line
    except Exception as e:
        print(f"[⛔] Gagal ambil data dari cloud: {e}")
        return None

class SensorConnectionManager(QObject):
    connectionStatusChanged = pyqtSignal()
    latestDataChanged = pyqtSignal()
    simulationFailed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.latest_data = {}
        self.windPredictionModel = MultiHorizonPredictionModel(sensor_manager=self)
        self._disperse_timer = QTimer()
        self._disperse_timer.timeout.connect(self._run_dispersion_loop)
        self._disperse_Q = None
        self._disperse_H = None
        self._disperse_running = False
        self._last_raw_line = None
        self._last_raw_timestamp = datetime.min


        # Timer untuk ping dan baca data sensor
        self.timer = QTimer()
        self.timer.timeout.connect(self._read_from_cloud)
        self.timer.start(5000)

        # Timer untuk update datetime setiap detik
        self.datetime_timer = QTimer()
        self.datetime_timer.timeout.connect(self._emit_datetime)
        self.datetime_timer.start(1000)

        # History data
        self._history_dict = {
            "temp_air": deque(maxlen=30),
            "humidity": deque(maxlen=30),
            "pressure": deque(maxlen=30),
            "rain_intensity": deque(maxlen=30),
            "rain_accum": deque(maxlen=30),
            "wind_speed_avg": deque(maxlen=30),
            "wind_dir_avg": deque(maxlen=30),
        }

    @pyqtProperty(bool, notify=connectionStatusChanged)
    def is_connected(self):
        return True  # karena kamu selalu polling dari cloud, dianggap selalu "terhubung"


    @pyqtProperty(QVariant, notify=latestDataChanged)
    def latest_data_qml(self):
        current = dict(self.latest_data)
        current["datetime"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return current

    def _read_from_cloud(self):
        raw_line = get_latest_raw_from_cloud()

        now = datetime.now()

        # ⛔ Jika tidak ada data sama sekali
        if not raw_line:
            print("[⛔] Tidak ada data diterima dari cloud.")
            return

        # ⏱️ Jika data sama, cek apakah sudah lewat 3 menit
        if raw_line == self._last_raw_line:
            elapsed = (now - self._last_raw_timestamp).total_seconds()
            if elapsed < 180:
                print(f"[🟡] Data masih sama, dilewati. Baru {int(elapsed)} detik.")
                return
            else:
                print("[⏱️] Data masih sama, tapi sudah 3 menit → tetap dicatat.")

        # ✅ Simpan raw terbaru dan timestamp-nya
        self._last_raw_line = raw_line
        self._last_raw_timestamp = now

        # Parsing dan update UI
        parsed = parse_0R0_line(raw_line)
        print(f"[🌐] Data dari cloud: {parsed}")

        if parsed and any(v is not None for v in parsed.values()):
            append_to_log(parsed)
            for key, value in parsed.items():
                if value is not None:
                    self.latest_data[key] = value
            self.latestDataChanged.emit()

            now_str = now.strftime("%H:%M:%S")
            for key in self._history_dict:
                if key in parsed and parsed[key] is not None:
                    self._history_dict[key].append({
                        "value": parsed[key],
                        "timestamp": now_str
                    })

            speed_hist = list(self._history_dict["wind_speed_avg"])
            dir_hist = list(self._history_dict["wind_dir_avg"])
            buffer_ready_now = len(speed_hist) >= 4 and len(dir_hist) >= 4
            if hasattr(self, "main_window") and self.main_window:
                self.windPredictionModel._buffer_ready = buffer_ready_now
                self.windPredictionModel.predictionChanged.emit()


    def _emit_datetime(self):
        self.latestDataChanged.emit()
            
    @pyqtSlot(float, float)
    def startDispersionLoop(self, Q_value: float, H_value: float):
        if self._disperse_running:
            print("[ℹ️] Simulasi sudah berjalan.")
            return

        # Validasi data saat start
        required_keys = ["wind_speed_avg", "wind_dir_avg", "temp_air", "humidity", "datetime"]
        missing_or_invalid = [
            k for k in required_keys
            if k not in self.latest_data or self.latest_data[k] in (None, 0.0)
        ]
        if missing_or_invalid:
            msg = f"❌ Tidak bisa memulai simulasi: data tidak lengkap → {missing_or_invalid}"
            print(f"[⛔] {msg}")
            self.simulationFailed.emit(msg)  # 🔔 Emit ke QML
            return


        print(f"[▶️] Memulai loop simulasi dispersi (Q={Q_value}, H={H_value})...")
        self._disperse_Q = Q_value
        self._disperse_H = H_value
        # Jalankan satu kali langsung saat tombol Start ditekan
        self._run_dispersion_loop()
        self._disperse_timer.start(10000)
        self._disperse_running = True


    @pyqtSlot()
    def stopDispersionLoop(self):
        if not self._disperse_running:
            print("[ℹ️] Simulasi tidak berjalan.")
            return
        print("[⏹️] Menghentikan loop simulasi dispersi...")
        self._disperse_timer.stop()
        self._disperse_running = False

    def _run_dispersion_loop(self):
        try:
            if self._disperse_Q is None or self._disperse_H is None:
                print("[⚠️] Nilai Q/H belum di-set.")
                return
            
            # Validasi minimal data cuaca
            required_keys = ["wind_speed_avg", "wind_dir_avg", "temp_air", "humidity", "datetime"]
            missing_or_invalid = [
                k for k in required_keys
                if k not in self.latest_data or self.latest_data[k] in (None, 0.0)
            ]
            if missing_or_invalid:
                print(f"[⛔] Simulasi dibatalkan: data tidak lengkap atau tidak valid: {missing_or_invalid}")
                return

            print("[🌬️] Menjalankan simulasi loop dispersi...")
            X, Y, C = simulate_atmos(
                data_dict=self.latest_data,
                Q=self._disperse_Q,
                H=self._disperse_H,
                stability='auto',     # biarkan auto → mapping A–F → CATEGORY 1..6 di dalam
                z_eval=0.0,           # evaluasi konsentrasi di permukaan
                xs=0.0, ys=0.0,       # sumber di origin lokal (nanti ditranslasi ke sensor_lat/lon)
                mask_upwind=True      # hanya downwind > 0
            )
            if X is None or Y is None or C is None:
                print("[⚠️] Simulasi loop gagal.")
                return

            C = np.where(np.isfinite(C), C, 0.0)
            maxC = float(np.nanmax(C))
            if not np.isfinite(maxC) or maxC <= 0.0:
                print("[⚠️] C maksimum tidak valid.")
                return


            sensor_lat = -6.8877831363571
            sensor_lon = 107.60727549580955

            heatmap_data = []
            for i in range(C.shape[0]):
                for j in range(C.shape[1]):
                    val = float(C[i, j])
                    if val <= 0:
                        continue
                    lat = sensor_lat + float(Y[i, j]) / 110540.0
                    lon = sensor_lon + float(X[i, j]) / 111320.0
                    heatmap_data.append([lat, lon, val])

            heatmap_data.sort(key=lambda x: x[2], reverse=True)
            heatmap_data = heatmap_data[:100000]

            json_data = json.dumps(heatmap_data)
            qml_root = self.main_window.maps_qml.rootObject()
            if qml_root:
                qml_root.updateHeatmapFromPython(json_data)
            else:
                print("[❌] rootObject maps_qml tidak ditemukan")

        except Exception as e:
            print(f"[❌] Error loop simulasi dispersi: {e}")

    @pyqtProperty(bool, notify=latestDataChanged)
    def isDispersionRunning(self):
        return self._disperse_running

    @pyqtSlot()
    def clearAtmosVisualization(self):
        try:
            for widget in QApplication.allWidgets():
                if hasattr(widget, "browser") and hasattr(widget.browser, "page"):
                    widget.browser.page().runJavaScript("""
                        if (typeof heatLayer !== 'undefined' && heatLayer) {
                            map.removeLayer(heatLayer);
                            heatLayer = null;
                            console.log("[🧹] Heatmap dihapus dari peta");
                        }
                    """)
                    print("[🧽] Perintah hapus heatmap dikirim ke map.html")
        except Exception as e:
            print(f"[❌] Gagal hapus heatmap: {e}")

    def get_lag_features(self):
        try:
            speed_hist = list(self._history_dict["wind_speed_avg"])
            dir_hist = list(self._history_dict["wind_dir_avg"])

          #  print(f"[DEBUG] wind_speed_avg buffer: {len(speed_hist)}")
           # print(f"[DEBUG] wind_dir_avg buffer: {len(dir_hist)}")

            # Pastikan cukup data
            if len(speed_hist) < 4 or len(dir_hist) < 4:
                if hasattr(self, "main_window") and self.main_window:
                    self.windPredictionModel._buffer_ready = False
                    self.windPredictionModel.predictionChanged.emit()
                raise ValueError("Insufficient history")
            
            if hasattr(self, "main_window") and self.main_window:
                self.windPredictionModel._buffer_ready = True
                self.windPredictionModel.predictionChanged.emit()

            lag2_windspeed = float(speed_hist[-3]["value"])
            lag3_windspeed = float(speed_hist[-4]["value"])

            lag2_dir_deg = float(dir_hist[-3]["value"])
            lag3_dir_deg = float(dir_hist[-4]["value"])

            lag2_sin_dir = np.sin(np.radians(lag2_dir_deg))
            lag3_cos_dir = np.cos(np.radians(lag3_dir_deg))

            return {
                "lag2_windspeed": lag2_windspeed,
                "lag3_windspeed": lag3_windspeed,
                "lag2_sin_dir": lag2_sin_dir,
                "lag3_cos_dir": lag3_cos_dir
            }
        except Exception as e:
           # print(f"[⚠️] Gagal ambil lag: {e}")
            return {
                "lag2_windspeed": 0.0,
                "lag3_windspeed": 0.0,
                "lag2_sin_dir": 0.0,
                "lag3_cos_dir": 0.0
            }


    @pyqtProperty(QVariant, notify=latestDataChanged)
    def history_temp_air(self):
        return list(self._history_dict["temp_air"])

    @pyqtProperty(QVariant, notify=latestDataChanged)
    def history_humidity(self):
        return list(self._history_dict["humidity"])

    @pyqtProperty(QVariant, notify=latestDataChanged)
    def history_pressure(self):
        return list(self._history_dict["pressure"])

    @pyqtProperty(QVariant, notify=latestDataChanged)
    def history_rain_intensity(self):
        return list(self._history_dict["rain_intensity"])

    @pyqtProperty(QVariant, notify=latestDataChanged)
    def history_rain_accum(self):
        return list(self._history_dict["rain_accum"])

    @pyqtProperty(QVariant, notify=latestDataChanged)
    def history_wind_speed_avg(self):
        return list(self._history_dict["wind_speed_avg"])

    @pyqtProperty(QVariant, notify=latestDataChanged)
    def history_wind_dir_avg(self):
        return list(self._history_dict["wind_dir_avg"])
    
    @pyqtProperty(QObject, constant=True)
    def predictionModel(self):
        return self.windPredictionModel


def append_to_log(data):
    log_path = "cuacane_app/data_logs/realtime_log.csv"
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    # Cek apakah file sudah ada
    file_exists = os.path.exists(log_path)

    # Jika file belum ada, buat dengan header
    if not file_exists:
        with open(log_path, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=data.keys())
            writer.writeheader()

    # Cek apakah data identik dengan baris terakhir
    if file_exists:
        with open(log_path, mode='r', newline='') as file:
            reader = list(csv.DictReader(file))
            if reader:
                last_row = reader[-1]
                # Bandingkan semua field
                if all(str(last_row.get(k, "")) == str(data.get(k, "")) for k in data.keys()):
                    print("[⚠️] Data identik, tidak ditulis ulang.")
                    return

    # Tulis data jika tidak duplikat
    with open(log_path, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=data.keys())
        writer.writerow(data)
        print("[✅] Data berhasil ditulis ke log.")
    


class MultiHorizonPredictionModel(QObject):
    predictionChanged = pyqtSignal()
    predictionExpiryChanged = pyqtSignal()

    def __init__(self, sensor_manager, use_dummy_model=False):
        super().__init__()
        self.models = load_all_models()
        self.sensor_manager = sensor_manager
        self._selected_horizon = "15m"

        self._latest_speed = 0.0
        self._latest_direction = 0.0
        self._prediction_expiry = "No Prediction Yet"
        self._history = deque(maxlen=20)
        self._buffer_ready = False

        if use_dummy_model:
            self.models = {}  # akan diset manual di test
        else:
            self.models = load_all_models()
        
        

    @pyqtSlot(str)
    def setHorizon(self, h):
        print(f"[⚙️] Horizon diubah ke: {h}")
        self._selected_horizon = h

    @pyqtSlot()
    def predictNow(self):
        try:
            print(f"[🔮] Melakukan prediksi untuk horizon {self._selected_horizon}...")
            lag = self.sensor_manager.get_lag_features()
            if all(v == 0.0 for v in lag.values()):
               # print("[⛔] Prediksi dibatalkan: data history belum cukup untuk lag.")
                self._prediction_expiry = "❌ Prediction Failed: buffer data not ready"
                self.predictionExpiryChanged.emit()
                return

            data = dict(self.sensor_manager.latest_data)

            # Fitur waktu
            hour = datetime.now().hour
            month = datetime.now().month
            weekday = datetime.now().weekday()
            sin_hour = np.sin(2 * np.pi * hour / 24)
            cos_hour = np.cos(2 * np.pi * hour / 24)
            sin_month = np.sin(2 * np.pi * month / 12)
            cos_month = np.cos(2 * np.pi * month / 12)

            # Semua calon fitur lengkap
            full_input = {
                "air_temp": data.get("temp_air", 0.0),
                "relative_humid": data.get("humidity", 0.0),
                "air_pressure": data.get("pressure", 0.0) / 1013.25,  # konversi dari hPa ke atm
                "rain_duration": data.get("rain_duration", 0.0),
                "rain_intensity": data.get("rain_intensity", 0.0),
                "hour": hour,
                "month": month,
                "weekday": weekday,
                "sin_hour": sin_hour,
                "cos_hour": cos_hour,
                "sin_month": sin_month,
                "cos_month": cos_month,
                "prev_windspeed": data.get("wind_speed_avg", 0.0),
                "prev_sin_dir": np.sin(np.radians(data.get("wind_dir_avg", 0.0))),
                "prev_cos_dir": np.cos(np.radians(data.get("wind_dir_avg", 0.0))),
                **lag
            }

            # Hanya ambil fitur yang dibutuhkan sesuai horizon
            from cuacane_app.utils.multi_predictor import FEATURE_ORDER
            feature_keys = FEATURE_ORDER[self._selected_horizon]
            filtered_input = {k: full_input.get(k, 0.0) for k in feature_keys}

            # === Tambahkan buffer ke model sebelum prediksi ===
            hist_speed = list(self.sensor_manager._history_dict["wind_speed_avg"])[-4:]
            hist_dir = list(self.sensor_manager._history_dict["wind_dir_avg"])[-4:]

            if len(hist_speed) < 4 or len(hist_dir) < 4:
                #print("[⛔] Buffer dari history_dict belum cukup")
                return

            self.models[self._selected_horizon]["buffer_speed"] = hist_speed
            self.models[self._selected_horizon]["buffer_dir"] = hist_dir

         #   print(f"[✅] Buffer dimasukkan ke model {self._selected_horizon}:")
          #  print("  speed_buffer =", self.models[self._selected_horizon]["buffer_speed"])
           # print("  dir_buffer   =", self.models[self._selected_horizon]["buffer_dir"])


            speed, direction = predict_from_data(self.models, filtered_input, self._selected_horizon)

            self._latest_speed = speed
            self._latest_direction = direction
            # Sesuaikan waktu validitas prediksi berdasarkan horizon
            horizon_to_delta = {
                "15m": timedelta(minutes=15),
                "1h": timedelta(hours=1),
                "3h": timedelta(hours=3),
                "6h": timedelta(hours=6)
            }
            delta = horizon_to_delta.get(self._selected_horizon, timedelta(minutes=15))
            self._prediction_expiry = (datetime.now() + delta).strftime("Valid Till %H:%M WIB")


            self._history.append({
                "timestamp": datetime.now().strftime("%H:%M"),
                "speed": speed,
                "dir": direction,
                "horizon": self._selected_horizon
            })

            print(f"[✅] Prediksi: {speed:.2f} m/s, {direction:.1f}°")
            self.predictionChanged.emit()
            self.predictionExpiryChanged.emit()

        except Exception as e:
            print(f"[❌] Gagal prediksi: {e}")
            self._latest_speed = 0.0
            self._latest_direction = 0.0

    @pyqtProperty(float, notify=predictionChanged)
    def predictionSpeed(self):
        return self._latest_speed

    @pyqtProperty(float, notify=predictionChanged)
    def predictionDirection(self):
        return self._latest_direction

    @pyqtProperty(str, notify=predictionExpiryChanged)
    def predictionExpiry(self):
        return self._prediction_expiry

    @pyqtProperty(QVariant, notify=predictionChanged)
    def predictionHistory(self):
        return list(self._history)
    
    @pyqtProperty(bool, notify=predictionChanged)
    def bufferReady(self):
        return self._buffer_ready
    
    @pyqtProperty(QVariant, notify=predictionChanged)
    def chart15m(self):
        return get_full_series_for_chart(self.models, "15m")

    @pyqtProperty(QVariant, notify=predictionChanged)
    def chart1h(self):
        return get_full_series_for_chart(self.models, "1h")

    @pyqtProperty(QVariant, notify=predictionChanged)
    def chart3h(self):
        return get_full_series_for_chart(self.models, "3h")

    @pyqtProperty(QVariant, notify=predictionChanged)
    def chart6h(self):
        return get_full_series_for_chart(self.models, "6h")



