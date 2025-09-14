import numpy as np
import torch
from datetime import datetime, timedelta
from cuacane_app.utils.sensor_connection import MultiHorizonPredictionModel
import cuacane_app.utils.multi_predictor as multi_predictor

# === Dummy Komponen ===

class DummyScaler:
    def transform(self, X):
        return np.array([[0.0, 0.0, 0.0]])
    def inverse_transform(self, X):
        return np.array([[3.21, np.sin(np.radians(88)), np.cos(np.radians(88))]])

class DummyModel:
    def __call__(self, x):
        return torch.tensor([[0.0, 0.0, 0.0]], dtype=torch.float32)

class DummySensorManager:
    def __init__(self, lag_ready=True, buffer_ready=True, missing_field=False):
        self._lag_ready = lag_ready
        self._buffer_ready = buffer_ready
        self._missing_field = missing_field

        if buffer_ready:
            self._history_dict = {
                "wind_speed_avg": [1.0, 1.2, 1.4, 1.6],
                "wind_dir_avg": [100, 110, 120, 130]
            }
        else:
            self._history_dict = {
                "wind_speed_avg": [1.0],
                "wind_dir_avg": [100]
            }

    def get_lag_features(self):
        if self._lag_ready:
            return {'lag1': 0.5, 'lag2': 0.4, 'lag3': 0.3}
        else:
            return {'lag1': 0.0, 'lag2': 0.0, 'lag3': 0.0}

    @property
    def latest_data(self):
        if self._missing_field:
            return {}
        return {
            'temp_air': 25.0,
            'humidity': 70.0,
            'pressure': 0.925,
            'rain_duration': 0.0,
            'rain_intensity': 0.0,
            'wind_speed_avg': 1.5,
            'wind_dir_avg': 120.0
        }

# === Setup Model dengan Dummy dan Override predict_from_data ===

def setup_model(sensor_manager, horizon="15m"):
    model = MultiHorizonPredictionModel(sensor_manager, use_dummy_model=True)
    model._selected_horizon = horizon

    dummy_scaler = DummyScaler()
    dummy_model = DummyModel()

    buffer_speed = [
        {"timestamp": "19:00", "value": 1.0},
        {"timestamp": "19:15", "value": 1.2},
        {"timestamp": "19:30", "value": 1.4},
        {"timestamp": "19:45", "value": 1.6}
    ]
    buffer_dir = [
        {"timestamp": "19:00", "value": 100},
        {"timestamp": "19:15", "value": 110},
        {"timestamp": "19:30", "value": 120},
        {"timestamp": "19:45", "value": 130}
    ]

    model.models[horizon] = {
        "model": dummy_model,
        "scaler_X": dummy_scaler,
        "scaler_y": dummy_scaler,
        "buffer_speed": buffer_speed,
        "buffer_dir": buffer_dir,
        "pred_history": []
    }

    print("[TEST DEBUG] Dummy model aktif:", model.models[horizon]["model"])

    # ✅ Override predict_from_data yang dipakai di sensor_connection.py
    import cuacane_app.utils.sensor_connection as sensor_conn

    def dummy_predict_from_data(models_dict, input_dict, horizon):
        print("[TEST DEBUG] dummy_predict_from_data() called")
        speed = 3.21
        direction = 88.0
        models_dict[horizon]["pred_history"].append(
            (datetime.now().strftime("%H:%M"), speed, direction)
        )
        models_dict[horizon]["chart"] = [
            {"timestamp": "19:00", "speed": 1.0, "dir": 100},
            {"timestamp": "19:15", "speed": 1.2, "dir": 110},
            {"timestamp": "19:30", "speed": 1.4, "dir": 120},
            {"timestamp": "19:45", "speed": 1.6, "dir": 130},
            {"timestamp": datetime.now().strftime("%H:%M"), "speed": speed, "dir": direction}
        ]
        return speed, direction

    sensor_conn.predict_from_data = dummy_predict_from_data

    return model


# === TEST CASES ===

def test_predict_success():
    model = setup_model(DummySensorManager())
    model.predictNow()
    assert round(model._latest_speed, 2) == 3.21
    assert round(model._latest_direction, 1) == 88.0
    assert "Valid Till" in model._prediction_expiry
    assert len(model.models["15m"]["pred_history"]) == 1
    assert len(model.models["15m"]["chart"]) == 5
    print("✅ Test 1: prediksi sukses")

def test_predict_lag_zero():
    model = setup_model(DummySensorManager(lag_ready=False))
    model.predictNow()
    assert model._prediction_expiry.startswith("❌")
    print("✅ Test 2: lag nol → prediksi dibatalkan")

def test_predict_buffer_kurang():
    model = setup_model(DummySensorManager(buffer_ready=False))
    model.predictNow()
    assert model._latest_speed == 0.0
    print("✅ Test 3: buffer kurang → prediksi dibatalkan")

def test_predict_missing_fields():
    model = setup_model(DummySensorManager(missing_field=True))
    model.predictNow()
    assert round(model._latest_speed, 2) == 3.21
    print("✅ Test 4: field hilang → prediksi tetap jalan")

# === RUN SEMUA TEST ===

if __name__ == "__main__":
    test_predict_success()
    test_predict_lag_zero()
    test_predict_buffer_kurang()
    test_predict_missing_fields()
    print("🎉 Semua test predictNow() selesai dengan sukses.")
