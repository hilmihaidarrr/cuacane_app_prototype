# 🌦️ Cuacane – Desktop Weather & Dispersion Simulation App

Cuacane is a **desktop application** built with **PyQt5 + QML** that integrates **Vaisala WXT520 sensor data**, performs **real-time weather monitoring**, **multi-horizon wind prediction (MLP models)**, and **atmospheric dispersion simulation (Gaussian Plume Model)**.  
This application was developed as part of a **Final Project (Capstone Design)** at **Telkom University** in collaboration with **BRIN (Badan Riset dan Inovasi Nasional, Indonesia)**.

---

## ✨ Features

- **📊 Real-time Weather Dashboard**  
  Displays temperature, humidity, pressure, wind speed & direction, and rainfall from Vaisala WXT520 sensors in a modern card-based UI with adaptive scaling (1366×768 → 1920×1080).

- **📈 Historical Graphs**  
  Dynamic line charts using `pyqtgraph` and `QtCharts` for daily temperature trends and short-term wind speed/direction history.

- **🧭 Wind Compass**  
  A custom `QWidget` compass that visualizes real-time wind direction and intensity.

- **🌍 Interactive Map (Google Maps + Leaflet)**  
  - Displays real-time sensor location and wind vector.  
  - Atmospheric dispersion simulation (Gaussian Plume Model) visualized as a heatmap with color legend.  
  - Supports multiple models (Plume, Puff, Lagrangian).

- **🤖 Wind Forecast (Machine Learning)**  
  - 4 **MLP models** for wind speed & direction prediction:  
    - +15 minutes, +1 hour, +3 hours, +6 hours ahead.  
  - Multi-output regression: `[windspeed, sin(direction), cos(direction)]`.  
  - Trained on **Vaisala WXT520 dataset (2021–2024)** with **PyTorch**.  
  - Performance evaluated using **MAE, RMSE, R²**, and **mean angular error**.

- **🗂 Data Converter**  
  - Converts raw WXT520 `.txt` sensor logs into **CSV** and **MH2 (PC-COSYMA compatible)** formats.  
  - Includes custom parser `txt_to_csv.py`.

- **⚙️ Settings**  
  - **Dark/Light mode toggle**  
  - **UI scale adjustment** (Small, Normal, Large)  
  - **Developer credits**

---

## 🏗️ Architecture

- **Frontend**: PyQt5 + QML (modern card UI, dashboard, charts, map integration via `QWebEngineView`)  
- **Backend**: Python services for  
  - Sensor connection & logging (`SensorConnectionManager`)  
  - Data parsing & storage (CSV, MH2)  
  - Gaussian Plume dispersion simulation (`simulate_atmos.py`)  
  - Wind prediction models (`predictor.py`, `MultiHorizonPredictionModel`)  
- **Machine Learning**:  
  - MLP models stored in `saved_models/` (`.pth`, `.pkl` scalers)  
  - Trained with PyTorch & scikit-learn

---

## 📂 Project Structure
- cuacane_app_prototype/
  - ├── main_window.py # Main PyQt5 window with QML integration
  - ├── views/ # QML UI files (DashboardPage.qml, MapsPage.qml, etc.)
  - ├── widgets/ # Custom widgets (TemperatureGraph, WindCompass)
  - ├── utils/ # Utility modules (parser, Gaussian Plume, Pasquill classifier)
  - ├── saved_models/ # Trained MLP models (15m, 1h, 3h, 6h)
  - ├── data/ # Example sensor data (CSV, MH2)
  - ├── realtime_log.csv # Auto-logged real-time data
  - └── requirements.txt # Python dependencies

## 📊 Machine Learning Models

The app includes 4 prediction models for wind speed & direction:
  - 15-minute ahead → saved_models/model_15m/
  - 1-hour ahead → saved_models/model_1h/
  - 3-hour ahead → saved_models/model_3h/
  - 6-hour ahead → saved_models/model_6h/
- **All models predict:**
[ avg_windspeed, sin(wind_direction), cos(wind_direction) ]
\nEvaluated using MAE, RMSE, R², and Mean Angular Error.
\nModels are trained using historical Vaisala WXT520 dataset (2021–2024).

## 🧑‍💻 Developers
- Muhamad Hilmi Haidar – Backend & ML Engineer, Documentation, Project Leader
- Nabila Putri Rihan – Frontend & UI/UX Developer
- Muhammad Thoriq Zam – Maps, Simulation, Cloud Integration
