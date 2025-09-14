from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QStackedLayout, QMessageBox, QGridLayout, QFrame, QSizePolicy, QLabel
)
from PyQt5.QtQuickWidgets import QQuickWidget
from PyQt5.QtCore import QUrl, QDir, Qt, QObject, pyqtSlot
from PyQt5.QtQml import qmlRegisterSingletonType
from PyQt5.QtGui import QIcon
import os

from cuacane_app.utils.convert_to_mh2 import batch_convert
from cuacane_app.views.settings_manager import SettingsManager
from cuacane_app.utils.sensor_connection import SensorConnectionManager
import sys
from pathlib import Path


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return str(Path(sys._MEIPASS) / relative_path)
    return str(Path(relative_path).resolve())


class ConvertSignalHandler(QObject):
    @pyqtSlot(str)
    def convertNow(self, output_path):
        try:
            input_file = "cuacane_app/data_logs/realtime_log.csv"
            output_file = os.path.join(output_path, "output.MH2")
            batch_convert(input_path=input_file, output_path=output_file)
            QMessageBox.information(None, "Sukses", f"File MH2 berhasil disimpan di:\n{output_file}")
        except Exception as e:
            QMessageBox.critical(None, "Gagal", f"Gagal membuat file MH2:\n{str(e)}")


# Helper to create placeholder pages for WIP sections
def create_placeholder_page(title: str, subtitle: str = "Work in progress") -> QWidget:
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setContentsMargins(24, 24, 24, 24)
    layout.setSpacing(8)

    label = QLabel(f"""
        <div style='text-align:center;'>
            <h2 style='margin-bottom:8px;'>🚧 {title}</h2>
            <p style='font-size:14px; color:#666;'>
                {subtitle} — This feature is currently under active development.
            </p>
        </div>
    """)
    label.setAlignment(Qt.AlignCenter)
    label.setWordWrap(True)
    layout.addStretch(1)
    layout.addWidget(label)
    layout.addStretch(1)
    return page


class MainWindow(QWidget):
    def __init__(self, weather_model=None):
        super().__init__()
        self.setWindowTitle("Cuacane - Weather and Dispersion Simulation")
        icon_path = os.path.join("cuacane_app", "assets", "icons", "cuacane_icon2.png")
        self.setWindowIcon(QIcon(icon_path))
        self.setMinimumSize(1100, 700)

        main_layout = QHBoxLayout(self)

        # === Sidebar
        sidebar = QVBoxLayout()
        sidebar.setSpacing(12)
        sidebar.setContentsMargins(12, 12, 12, 12)

        btn_dashboard = QPushButton("Dashboard")
        btn_prediksi = QPushButton("Prediction")

        # Renamed from "Radioactive Dispersion Maps"
        btn_gpm = QPushButton("Gaussian Plume Model Simulation")
        # New pages requested
        btn_puff = QPushButton("Puff Model Simulation")
        btn_lagrangian = QPushButton("Lagrangian Model Simulation")

        btn_convert = QPushButton("Input File Preparation")
        # New integration button under Input File Preparation
        btn_integration = QPushButton("Integration to PC-COSYMA")

        btn_settings = QPushButton("Settings")

        for btn in [
            btn_dashboard,
            btn_prediksi,
            btn_gpm,
            btn_puff,
            btn_lagrangian,
            btn_convert,
            btn_integration,
            btn_settings,
        ]:
            btn.setMinimumHeight(40)
            sidebar.addWidget(btn)
        sidebar.addStretch()

        # === Stack Layout
        self.stack = QStackedLayout()

        # === Manager
        self.settings_manager = SettingsManager()
        self.sensor_manager = SensorConnectionManager()
        self.sensor_manager.main_window = self

        # === Theme QML Singleton
        qmlRegisterSingletonType(QUrl.fromLocalFile(resource_path("views/Theme.qml")), "AppTheme", 1, 0, "Theme")

        # === Dashboard Page (FULL QML)
        dashboard_page = QWidget()
        dashboard_layout = QVBoxLayout(dashboard_page)

        dashboard_qml = QQuickWidget()
        dashboard_qml.rootContext().setContextProperty("settingsManager", self.settings_manager)
        dashboard_qml.rootContext().setContextProperty("sensorManager", self.sensor_manager)
        dashboard_qml.setResizeMode(QQuickWidget.SizeRootObjectToView)
        dashboard_qml.setSource(QUrl.fromLocalFile(resource_path("views/DashboardPage.qml")))
        dashboard_qml.setMinimumHeight(600)

        dashboard_layout.addWidget(dashboard_qml)

        # === Prediction Page (FULL QML)
        prediksi_page = QWidget()
        prediksi_layout = QVBoxLayout(prediksi_page)

        prediksi_qml = QQuickWidget()
        prediksi_qml.rootContext().setContextProperty("settingsManager", self.settings_manager)
        prediksi_qml.rootContext().setContextProperty("windPredictionModel", self.sensor_manager.windPredictionModel)
        prediksi_qml.setResizeMode(QQuickWidget.SizeRootObjectToView)
        prediksi_qml.setSource(QUrl.fromLocalFile(resource_path("views/PrediksiPage.qml")))
        prediksi_qml.setMinimumHeight(400)

        prediksi_layout.addWidget(prediksi_qml)

        # === GPM Maps Page ===
        gpm_page = QWidget()
        gpm_layout = QVBoxLayout(gpm_page)
        gpm_layout.setContentsMargins(0, 0, 0, 0)
        gpm_layout.setSpacing(0)

        self.maps_qml = QQuickWidget()
        self.maps_qml.setResizeMode(QQuickWidget.SizeRootObjectToView)
        self.maps_qml.setClearColor(Qt.transparent)

        qml_url = QUrl.fromLocalFile(resource_path("views/MapsPage.qml"))
        print(f"[DEBUG] Loading QML: {qml_url.toString()}")

        self.maps_qml.rootContext().setContextProperty("sensorManager", self.sensor_manager)
        self.maps_qml.setSource(qml_url)

        if self.maps_qml.status() != QQuickWidget.Ready:
            print("[ERROR] MapsPage.qml gagal dimuat:")
            for err in self.maps_qml.errors():
                print("  ->", err.toString())

        gpm_layout.addWidget(self.maps_qml)

        # === Puff Model (placeholder)
        puff_page = create_placeholder_page(
            title="Puff Model Simulation",
            subtitle="Coming soon"
        )

        # === Lagrangian Model (placeholder)
        lagrangian_page = create_placeholder_page(
            title="Lagrangian Model Simulation",
            subtitle="Coming soon"
        )

        # === Convert Page (FULL QML)
        convert_page = QWidget()
        convert_layout = QVBoxLayout(convert_page)

        convert_qml = QQuickWidget()
        self.convert_handler = ConvertSignalHandler()
        convert_qml.rootContext().setContextProperty("convertSignalHandler", self.convert_handler)
        convert_qml.rootContext().setContextProperty("settingsManager", self.settings_manager)
        convert_qml.setResizeMode(QQuickWidget.SizeRootObjectToView)
        convert_qml.setSource(QUrl.fromLocalFile(resource_path("views/ConvertDataPage.qml")))
        convert_qml.setMinimumHeight(300)

        convert_layout.addWidget(convert_qml)

        # === Integration to PC-COSYMA (placeholder)
        integration_page = create_placeholder_page(
            title="Integration to PC-COSYMA",
            subtitle="API & pipeline wiring"
        )

        # === Settings Page (FULL QML)
        settings_page = QWidget()
        settings_layout = QVBoxLayout(settings_page)

        settings_qml = QQuickWidget()
        settings_qml.rootContext().setContextProperty("settingsManager", self.settings_manager)
        settings_qml.rootContext().setContextProperty("sensorManager", self.sensor_manager)
        settings_qml.setResizeMode(QQuickWidget.SizeRootObjectToView)
        settings_qml.setSource(QUrl.fromLocalFile(resource_path("views/SettingsPage.qml")))
        settings_qml.setMinimumHeight(300)

        settings_layout.addWidget(settings_qml)

        # === Stack Pages (order matters for indices)
        self.stack.addWidget(dashboard_page)    # index 0
        self.stack.addWidget(prediksi_page)     # index 1
        self.stack.addWidget(gpm_page)          # index 2 (GPM / Maps)
        self.stack.addWidget(puff_page)         # index 3
        self.stack.addWidget(lagrangian_page)   # index 4
        self.stack.addWidget(convert_page)      # index 5
        self.stack.addWidget(integration_page)  # index 6
        self.stack.addWidget(settings_page)     # index 7

        # === Sidebar Navigation
        btn_dashboard.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        btn_prediksi.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        btn_gpm.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        btn_puff.clicked.connect(lambda: self.stack.setCurrentIndex(3))
        btn_lagrangian.clicked.connect(lambda: self.stack.setCurrentIndex(4))
        btn_convert.clicked.connect(lambda: self.stack.setCurrentIndex(5))
        btn_integration.clicked.connect(lambda: self.stack.setCurrentIndex(6))
        btn_settings.clicked.connect(lambda: self.stack.setCurrentIndex(7))

        # === Final Layout
        main_layout.addLayout(sidebar)
        main_layout.addLayout(self.stack)

    def show_maps_page(self):
        # Corrected to show GPM/Maps (index 2)
        self.stack.setCurrentIndex(2)
