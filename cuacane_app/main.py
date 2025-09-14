import sys
import PyQt5.QtCore
from PyQt5 import QtWebEngineWidgets  # ⬅ trigger import agar context dibuat
PyQt5.QtCore.QCoreApplication.setOrganizationName("Cuacane")
PyQt5.QtCore.QCoreApplication.setOrganizationDomain("cuacane.local")
PyQt5.QtCore.QCoreApplication.setApplicationName("Cuacane App")
from PyQt5.QtWidgets import QApplication
from cuacane_app.main_window import MainWindow

print("[DEBUG] Memulai main.py (sebelum QApplication dibuat)")

def main():
    app = QApplication(sys.argv)
    print("[DEBUG] QApplication dibuat")

    window = MainWindow(None)  # Weather model sudah tidak digunakan
    print("[DEBUG] MainWindow dibuat")
    window.showMaximized()
    print("[DEBUG] Window ditampilkan")

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
