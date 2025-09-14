import torch
import joblib
import os
import sys
import torch.nn as nn
import numpy as np
import math
from pathlib import Path
from datetime import datetime, timedelta

# === Fungsi builder sesuai struktur masing-masing model ===
def make_model_15m(input_size, output_size):
    layers = []
    hidden_size = 256
    num_layers = 2
    dropout = 0.1686
    for i in range(num_layers):
        layers.append(nn.Linear(input_size if i == 0 else hidden_size, hidden_size))
        layers.append(nn.ReLU())
        layers.append(nn.Dropout(dropout))
    layers.append(nn.Linear(hidden_size, output_size))
    return nn.Sequential(*layers)

def make_model_bn(input_size, output_size, hidden_size, num_layers, dropout, activation_name='ReLU'):
    activation = {
        'ReLU': nn.ReLU(),
        'LeakyReLU': nn.LeakyReLU(),
        'Tanh': nn.Tanh(),
        'ELU': nn.ELU()
    }[activation_name]

    layers = []
    for i in range(num_layers):
        layers.append(nn.Linear(input_size if i == 0 else hidden_size, hidden_size))
        layers.append(nn.BatchNorm1d(hidden_size))
        layers.append(activation)
        layers.append(nn.Dropout(dropout))
    layers.append(nn.Linear(hidden_size, output_size))
    return nn.Sequential(*layers)

def make_model_no_bn(input_size, output_size, hidden_size, num_layers, dropout, activation_name='ReLU'):
    activation = {
        'ReLU': nn.ReLU(),
        'LeakyReLU': nn.LeakyReLU(),
        'Tanh': nn.Tanh(),
        'ELU': nn.ELU()
    }[activation_name]

    layers = []
    for i in range(num_layers):
        layers.append(nn.Linear(input_size if i == 0 else hidden_size, hidden_size))
        layers.append(activation)
        layers.append(nn.Dropout(dropout))
    layers.append(nn.Linear(hidden_size, output_size))
    return nn.Sequential(*layers)

# === Urutan fitur manual per horizon ===
FEATURE_ORDER = {
    "15m": [
        'air_temp', 'relative_humid', 'air_pressure',
        'rain_duration', 'rain_intensity',
        'hour', 'month', 'weekday',
        'prev_windspeed', 'prev_sin_dir', 'prev_cos_dir'
    ],
    "1h": [
        'air_temp', 'relative_humid', 'air_pressure',
        'rain_duration', 'rain_intensity',
        'hour', 'month', 'weekday',
        'prev_windspeed', 'prev_sin_dir', 'prev_cos_dir',
        'lag2_windspeed', 'lag3_windspeed',
        'lag2_sin_dir', 'lag3_cos_dir'
    ],
    "3h": [
        'air_temp', 'relative_humid', 'air_pressure',
        'rain_duration', 'rain_intensity',
        'sin_hour', 'cos_hour', 'sin_month', 'cos_month',
        'weekday',
        'prev_windspeed', 'prev_sin_dir', 'prev_cos_dir',
        'lag2_windspeed', 'lag3_windspeed',
        'lag2_sin_dir', 'lag3_cos_dir'
    ],
    "6h": [
        'air_temp', 'relative_humid', 'air_pressure',
        'rain_duration', 'rain_intensity',
        'sin_hour', 'cos_hour', 'sin_month', 'cos_month',
        'weekday',
        'prev_windspeed', 'prev_sin_dir', 'prev_cos_dir',
        'lag2_windspeed', 'lag3_windspeed',
        'lag2_sin_dir', 'lag3_cos_dir'
    ]
}

def resource_path(relative_path):
    """Dapatkan path absolut, mendukung PyInstaller"""
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def resource_path(relative_path):
    """Mengembalikan path absolut untuk file dalam bundle PyInstaller"""
    if getattr(sys, 'frozen', False):
        # Jalankan dari _MEIPASS (runtime folder PyInstaller)
        return Path(sys._MEIPASS) / relative_path
    else:
        return Path(relative_path).resolve()
    
def load_all_models():
    model_dict = {}

    configs = {
        "15m": {
            "path": "saved_models/model_15m",
            "input_size": 11,
            "builder": lambda inp, out: make_model_15m(inp, out)
        },
        "1h": {
            "path": "saved_models/model_1h",
            "input_size": 15,
            "builder": lambda inp, out: make_model_bn(inp, out, hidden_size=512, num_layers=3, dropout=0.3567, activation_name='ReLU')
        },
        "3h": {
            "path": "saved_models/model_3h",
            "input_size": 17,
            "builder": lambda inp, out: make_model_bn(inp, out, hidden_size=128, num_layers=3, dropout=0.3, activation_name='ReLU')
        },
        "6h": {
            "path": "saved_models/model_6h",
            "input_size": 17,
            "builder": lambda inp, out: make_model_no_bn(inp, out, hidden_size=64, num_layers=3, dropout=0.2, activation_name='LeakyReLU')
        }
    }

    for h, cfg in configs.items():
        path = cfg["path"]
        input_size = cfg["input_size"]
        builder = cfg["builder"]

        model = builder(input_size, 3)

        model_path = resource_path(f"saved_models/model_{h}/model_{h}.pth")
        scaler_X_path = resource_path(f"saved_models/model_{h}/scaler_X_{h}.pkl")
        scaler_y_path = resource_path(f"saved_models/model_{h}/scaler_y_{h}.pkl")

        model.load_state_dict(torch.load(str(model_path), map_location="cpu"))
        model.eval()

        scaler_X = joblib.load(str(scaler_X_path))
        scaler_y = joblib.load(str(scaler_y_path))

        model_dict[h] = {
            "model": model,
            "scaler_X": scaler_X,
            "scaler_y": scaler_y,
            "pred_history": [],
            "chart": [],
            "buffer_speed": [],
            "buffer_dir": []
        }

    return model_dict


# === Fungsi prediksi utama ===
def predict_from_data(models_dict, input_dict, horizon):
    m = models_dict[horizon]
    model = m["model"]
    scaler_X = m["scaler_X"]
    scaler_y = m["scaler_y"]

    feature_order = FEATURE_ORDER[horizon]
    input_row = [input_dict.get(k, 0.0) for k in feature_order]
    input_scaled = scaler_X.transform([input_row])
    input_tensor = torch.tensor(input_scaled, dtype=torch.float32)
    output = model(input_tensor).detach().numpy()
    output_true = scaler_y.inverse_transform(output)

    speed = output_true[0][0]
    sin_dir = output_true[0][1]
    cos_dir = output_true[0][2]
    direction = (np.degrees(np.arctan2(sin_dir, cos_dir))) % 360
    
    now = datetime.now()
    delta = {"15m": 15, "1h": 60, "3h": 180, "6h": 360}[horizon]
    pred_time = now + timedelta(minutes=delta)
    models_dict[horizon]["pred_history"].append((pred_time.strftime("%H:%M"), speed, direction))

    speed_buffer = models_dict[horizon]["buffer_speed"]
    dir_buffer = models_dict[horizon]["buffer_dir"]

    if len(speed_buffer) >= 4 and len(dir_buffer) >= 4:
        if math.isfinite(speed) and math.isfinite(direction):
            models_dict[horizon]["chart"] = [
                {"timestamp": speed_buffer[-4]["timestamp"], "speed": float(speed_buffer[-4]["value"]), "dir": float(dir_buffer[-4]["value"])},
                {"timestamp": speed_buffer[-3]["timestamp"], "speed": float(speed_buffer[-3]["value"]), "dir": float(dir_buffer[-3]["value"])},
                {"timestamp": speed_buffer[-2]["timestamp"], "speed": float(speed_buffer[-2]["value"]), "dir": float(dir_buffer[-2]["value"])},
                {"timestamp": speed_buffer[-1]["timestamp"], "speed": float(speed_buffer[-1]["value"]), "dir": float(dir_buffer[-1]["value"])},
                {"timestamp": pred_time.strftime("%H:%M"), "speed": float(speed), "dir": float(direction)}
            ]
        else:
            print(f"[❌] Invalid prediction value: speed={speed}, dir={direction}")

    return speed, direction

# === Getter agar pred_history bisa dibaca dari QML ===
def get_prediction_history(models_dict, horizon):
    return [
        {"timestamp": t, "speed": s, "dir": d}
        for (t, s, d) in models_dict[horizon]["pred_history"]
    ]

def get_full_series_for_chart(models_dict, horizon):
    try:
        chart_data = models_dict[horizon].get("chart", [])
        print(f"[📊 DEBUG CHART {horizon}] {chart_data}")
        return chart_data
    except Exception as e:
       # print(f"[⚠️] Gagal ambil data chart {horizon}: {e}")
        return []
